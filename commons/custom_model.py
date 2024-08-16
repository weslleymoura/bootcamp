import mlflow
from joblib import load
import configparser
import geopy.distance

class CustomModel(mlflow.pyfunc.PythonModel):

    def __init__(self, env = 'PROD'):
        
        self.env = env
        self.app_config = self.get_app_config('config/app_config.ini')

    def load_context(self, context):

        app_config_path = context.artifacts["app_config"]
        model_path = context.artifacts["model"]

        # Load app config
        self.app_config = self.get_app_config(app_config_path)
        
        # Load model
        self.model = load(model_path)

        # Load config variables
        self.covered_region_in_km = int(self.app_config[self.env]['covered_region_in_km'])
        self.run_id = self.app_config['ALL']['run_id']
        self.model_name = self.app_config['ALL']['model_name']
        
    # Carrega das configurações da aplicação
    def get_app_config (self, app_config_path):

        app_config = configparser.ConfigParser()
        app_config.read(app_config_path)
        return app_config
        
    def predict(self, context, model_input):

        if 'method' not in model_input:
            raise ValueError("Input must contain a 'method' key to specify the operation")

        method = model_input['method']
        data = model_input['data']

        if method == 'predict':
            return self.make_predictions(data, self.model, self.covered_region_in_km)
        
        elif method == 'get_cluster_centroids':
            return self.get_cluster_centroids()

        elif method == 'get_model_version':
            return self.get_model_version()
            
        else:
            raise ValueError(f"Unknown method: {method}")
        

    def get_model_version(self):
        
        # Initialize MLflow client
        client = mlflow.tracking.MlflowClient()
        
        # Search all registered models
        registered_models = client.search_registered_models()
        
        # Filter to find the models associated with the specified run ID
        models_associated_with_run = []
        for registered_model in registered_models:
            for version in registered_model.latest_versions:
                if version.run_id == self.run_id:
                    models_associated_with_run.append({
                        "model_name": registered_model.name,
                        "aliases": registered_model.aliases,
                        "version": version.version,
                        "run_id": version.run_id
                    })
        
        return models_associated_with_run
        
    def make_predictions(self, data, model, covered_region_in_km):
    
        # Prepara as coordenadas do CEP
        coords_cep = (data[0], data[1])
    
        # Lista centróides dos clusters
        centers = self.get_cluster_centroids()
    
        # Verifica a distância (em km) entre o CEP a cada cluster
        res = dict()
        for c in centers:
            coords_cluster = (c['lat'], c['lng'])
            res[c['cluster']] = geopy.distance.geodesic(coords_cep, coords_cluster).km
    
        # Cria uma lista com as chaves (keys) ordenadas pelos seus valores (values)
        res_sorted_keys = sorted(res, key=res.get, reverse=False)
    
        print ("teste")
        print (res_sorted_keys) 
        print(centers)
        
        # Prepara o resultado do endpoint
        results = {
            'is_region_covered': round(res[res_sorted_keys[0]], 2) <= covered_region_in_km,
            'closest_center': {
                'id': res_sorted_keys[0],
                'distance_in_km': round(res[res_sorted_keys[0]], 2),
                'lat': centers[res_sorted_keys[0]]['lat'],
                'lng': centers[res_sorted_keys[0]]['lng']
            }
        }

        return results
    
    # Retorna os centróides de cada cluster
    def get_cluster_centroids (self):

        centers = []
        for i, center in enumerate(self.model.cluster_centers_):
            c = dict()
            c['lat'] = center[0]
            c['lng'] = center[1]
            c['cluster'] = i + 1
            centers.append(c)
            
        return centers