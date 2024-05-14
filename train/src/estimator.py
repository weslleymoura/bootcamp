import configparser
import folium
import json 
import numpy as np
from sklearn.cluster import KMeans
from yellowbrick.cluster import KElbowVisualizer
import random
from joblib import dump
import geopy.distance
import logging 

logger = logging.getLogger(__name__)

class BootcampEstimator:

    # Construtor
    def __init__(self, env = 'PROD'):
        
        self.env = env
        self.app_config = self.get_app_config(env)
        self.version = self.app_config['version']

        logger.info('constructor executed')
    
    # Carrega das configurações da aplicação
    def get_app_config (self, env):

        app_config = configparser.ConfigParser()
        app_config.read('config/app_config.ini')
        return app_config[env]
    
    # Função para treinar o modelo
    def fit(self, points, input_points):

        #---------------------------------------------------------------
        # Treinando o modelo
        #---------------------------------------------------------------

        # Define o modelo base
        model = KMeans()

        # Cria um visualizer 
        visualizer = KElbowVisualizer(model, k=(1,50))

        # Treino vários modelos de clustering
        visualizer.fit(input_points)

        # Define o número de clusters
        n_clusters = visualizer.elbow_value_

        # Treina o modelo de clustering
        model = KMeans(n_clusters = n_clusters, random_state = 0).fit(input_points)

        #---------------------------------------------------------------
        # Guarda um mapa de exemplo do modelo
        #---------------------------------------------------------------

        # Cria uma função para gerar cores aleatórias
        get_colors = lambda n: ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(n)]

        # Seleciona algumas cores para o mapa
        colors = get_colors(n_clusters)

        # Agora vamos preparar um colormap, no qual vamos associar uma cor para cada cluster
        cm = dict()
        for cluster in np.unique(model.labels_):
            cm[cluster] = colors[cluster]

        # Preparando os pontos do mapa
        for p in points:
            cluster = model.predict([[ p['lat'], p['lng'] ]] )
            p['cluster'] = cluster[0]
            p['color'] = cm[cluster[0]]

        # Preparando os marcadores do mapa
        markers = []
        for i, center in enumerate(model.cluster_centers_):
            m = dict()
            m['lat'] = center[0]
            m['lng'] = center[1]
            m['cluster'] = i + 1
            m['color'] = 'black'
            m['type'] = ['cluster', 'pin']
            m['tooltip'] = 'Cluster {}'.format(i + 1)
            markers.append(m)

        # Exibe todos os dados de treino no mapa
        map = self.plot_points(points = points, markers = markers)

        #---------------------------------------------------------------
        # Model drift params
        #---------------------------------------------------------------

        # Primeiramente, vamos calcular as distâncias (em km) de cada ponto para o centróide de seu cluster
        distances = dict()

        for p in points:
            
            # Coordenadas do ponto p
            coords_p = (p['lat'], p['lng'])

            # Coordenadas do cluster associado ao ponto p
            lat_cliuster = markers[p['cluster'] - 1]['lat']
            lng_cliuster = markers[p['cluster'] - 1]['lng']
            coords_cluster = ( lat_cliuster, lng_cliuster )   

            # Calcula a distância entre o ponto p e seu cluster
            dist = geopy.distance.geodesic(coords_cluster, coords_p).km

            # Seleciona a identificação do cluster do ponto p
            cluster = p['cluster']
            
            # Adiciona o resultado à lista
            try:
                distances[cluster] += [dist]
            except:
                distances[cluster] = [dist]

        # Vamos salvar algumas estatísticas do nosso modelo e definir nosso regra para retreinar o modelo ao processar novos dados de treino no futuro.
        drift_params = dict()
        for k, v in distances.items():
            drift_params[k] = {
                'mean': round(np.mean(v), 2),
                'stdev': round(np.std(v), 2)
            }

        #---------------------------------------------------------------
        # Separa alguns data points de exemplo para nossa API
        #---------------------------------------------------------------

        sample_points = dict()
        sample_points['covered'] = []
        sample_points['not_covered'] = []

        for p in points:
            coords_p = (p['lat'], p['lng'])
            coords_p_dict = {
                'lat': p['lat'],
                'lng': p['lng']
            }

            # Verifica a distância (em km) entre o ponto a cada cluster
            res = dict()
            for m in markers:
                coords_cluster = (m['lat'], m['lng'])
                res[m['cluster']] = geopy.distance.geodesic(coords_cluster, coords_p).km

            # Cria uma lista com as chaves (keys) ordenadas pelos seus valores (values)
            res_sorted_keys = sorted(res, key=res.get, reverse=False)

            # Busca a distância mais curta
            dist = round(res[res_sorted_keys[0]], 2)

            if (dist <= 5 and len(sample_points['covered']) < 10):
                sample_points['covered'] += [coords_p_dict]
            elif (dist > 5 and len(sample_points['not_covered']) < 10):
                sample_points['not_covered'] += [coords_p_dict]

            if len(sample_points['covered']) + len(sample_points['not_covered']) == 20:
                break

        # Retorna artefato do modelo
        return model, map, drift_params, sample_points

    # Função que recebe uma instância de entrega e retorna uma lista de pontos (lat, lng)
    def get_delivery_coordinates(self, instance):
        
        points = []
        for delivery in instance['deliveries']:
            points.append(delivery['point'])

        return points

    # Vamos criar uma função para exibir uma instância de entrega no mapa
    def plot_points(self, points, markers):

        # Cria um mapa
        m = folium.Map(
            location=(points[0]['lat'], points[0]['lng']),
            zoom_start=12,
            tiles="OpenStreetMap",
        )

        # Adiciona um feature group para colocarmos os pins no mapa
        fg_points = folium.FeatureGroup(name='Points').add_to(m)

        # Adiciona pontos ao mapa
        for point in points:
            folium.CircleMarker(
                [point['lat'], point['lng']], color=point['color'], radius=1, weight=1
            ).add_to(m)

        # Adiciona marcadores ao mapa
        if markers != None:
            for marker in markers:

                # Adiciona os marcadores do tipo pin no mapa
                if 'pin' in (marker['type']):
                    folium_marker = folium.Marker(location=[marker['lat'], marker['lng']], radius=10, tooltip=marker['tooltip'], icon=folium.Icon(color=marker['color']))
                    folium_marker.add_to(fg_points)
                
                # Adiciona os marcadores do tipo cluster no mapa
                if 'cluster' in (marker['type']):
                    folium.Circle([marker['lat'], marker['lng']], color=marker['color'], radius=5000, weight=3).add_to(m)

        # Adiciona legenda ao mapa
        m.add_child(folium.LayerControl(position='topright', collapsed=False, autoZIndex=True))

        return m