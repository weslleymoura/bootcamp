from pathlib import Path
import sys 
path = Path().joinpath().joinpath('..')
sys.path.append(str(path))
import os
import shutil
import argparse
import configparser
import warnings
warnings.filterwarnings('ignore')

def main(version):
    
    # Diretório do deploy
    dir_source = '../api'
    dir_deploy = '../deploy/api'
    dir_deploy_new_version = dir_deploy + '/{}'.format(version)
    dir_train = '../train/model'

    # Lista as versões atuais (já salvas do diretório)
    past_versions = next(os.walk(dir_deploy))[1]

    # Se já existe uma versão anterior, cancela o deploy
    if version in past_versions:
        print("Já existe")
    
    # Caso contrário, continua o deploy
    else:

        # Copia o source code para a pasta da nova versão
        shutil.copytree(dir_source, dir_deploy_new_version)

        # Limpa a pasta de artefatos do modelo
        shutil.rmtree(dir_deploy_new_version + '/model')

        # Copia os novos artefatos do modelo
        shutil.copytree(dir_train, dir_deploy_new_version + '/model')

        # Atualiza a versão no arquivo de configuração
        app_config = configparser.ConfigParser()
        app_config.read(dir_deploy_new_version + '/config/app_config.ini')
        app_config.set('PROD', 'version', version)
        app_config.set('DEV', 'version', version)
        with open(dir_deploy_new_version + '/config/app_config.ini', 'w') as configfile:
            app_config.write(configfile)

        # Copia requirements.txt
        shutil.copyfile('../requirements.txt', dir_deploy_new_version + '/requirements.txt')
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Receive main parameters')
    parser.add_argument('--version', required=True, help='version')
    args = parser.parse_args()
    main(args.version)


    