Esta é a documentação técnica do nosso projeto! A seguir, você encontrará algumas explicações importantes sobre o código do projeto.

## Pipeline de treino
O pipeline de treino utiliza os dados de treino do projeto para criar o modelo de clustering. 
Este pipeline é controlado pelo método `main` do arquivo `main.py`

::: train.main.main
    options:
        heading_level: 3

Dentro do método `main`, o método `fit` é chamado. É neste momento em que o modelo de clustering é treinado.

::: train.src.estimator.BootcampEstimator.fit
    options:
        heading_level: 3

