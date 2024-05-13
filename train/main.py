from pathlib import Path
import sys 
path = Path().joinpath().joinpath('..')
sys.path.append(str(path))
import json 
import numpy as np
from joblib import dump
from src.estimator import BootcampEstimator
import argparse
import warnings
warnings.filterwarnings('ignore')

def main(env):

    #---------------------------------------------------------------
    # Instancia o estimator
    #---------------------------------------------------------------

    bootcamp_estimator = BootcampEstimator(env = env)

    #---------------------------------------------------------------
    # Carrega os dados de treino
    #---------------------------------------------------------------

    # Carrega as instâncias de treino
    path_str = "../data/train/"

    # Converte o nome da pasta em uma variável `Path`
    path = Path(path_str)

    # Passa por todos os arquivos da pasta e carrega os dados em `instances`
    instances = []
    for file in path.iterdir():

        # Acessa o arquivo
        with open(file) as f:

            # Lê os dados do arquivo
            data = json.load(f)

        # Adiciona os dados do arquivo à lista `instances`
        instances.append(data)

    #---------------------------------------------------------------
    # Prepara os dados de treino
    #---------------------------------------------------------------

    # Junta todos os pontos de entrega de todas as instâncias em uma única lista
    points = []
    for instance in instances:
        points.extend(bootcamp_estimator.get_delivery_coordinates(instance))

    # Adiciona a cor de cada ponto
    for p in points:
        p['color'] = 'blue'
        
    # Preparando os dados para o modelo de clustering
    input_points = [ (p['lat'], p['lng']) for p in points]
    input_points = np.array(input_points)

    #---------------------------------------------------------------
    # Treinando o modelo
    #---------------------------------------------------------------

    model, m, drift_params, sample_points = bootcamp_estimator.fit(points = points, input_points =  input_points)

    #---------------------------------------------------------------
    # Guarda os artefatos do modelo
    #---------------------------------------------------------------

    # Salva o modelo
    dump(model, 'model/clustering_model.joblib') 

    # Salva o mapa
    m.save('model/clustering_map.html')

    # Salva os parâmetros de model drift
    dump(drift_params, 'model/drift_params.joblib') 

    # Salva os data points de exemplo
    dump(sample_points, 'model/sample_points.joblib')



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Receive main parameters')
    parser.add_argument('--env', required=True, help='environment to run the application')
    args = parser.parse_args()
    main(args.env)