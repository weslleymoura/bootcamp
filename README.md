## Bootcamp data science / ML Ops

Nesta página você encontrará todas as informações necessárias para acompanhar este bootcamp.

### Pré-requisitos

Antes de começar, você terá que instalar os seguintes softwares na sua máquina:
* [Anaconda](https://www.anaconda.com/download) 
* [Python 3.10](https://www.python.org/downloads/)

Como o passo a passo para instalação depende de cada sistema operacional, esta parte fica por conta de vocês. 

### Criando um ambiente python com conda

Nosso primeiro passo será a criação do nosso ambiente python. Isso é importante, pois é aqui que garantimos que todos os pacotes utilizados no projeto estão instalados.

```conda create -n bootcamputilenv python=3.10```

Uma vez que o ambiente foi criado, devemos ativá-lo.

```conda activate bootcamputilenv```

### Clonando o repositório do projeto

Abra o terminal da sua máquina e navegue até o diretório em que deseja salvar o projeto. Em seguida, faça o clone do projeto.

```git clone ...```

### Instalando as dependências do projeto no seu ambiente python

Agora acesse a pasta do projeto que acabou se ser clonado na sua máquina

```cd bootcamp ```

Em seguida, instale os pacotes python no seu ambiente. Note que **você deve manter seu ambiente python ativado**.

```pip install -r requirements.txt```

### Iniciando os projetos na sua máquina

Para inicar a análise exploratória do projeto (notebook) na sua máquina, faça:

```jupyter lab```

Para inicar o pipeline de inferência (API) na sua máquina, faça:

```cd api```
```python -m uvicorn main:app --reload```

Para executar o pipeline de treino (API) na sua máquina, faça:

```cd train```
```python main.py --env PROD```

### Fazendo deploy do pipeline de inferência (API)

Para deploy da API deste projeto, vamos utilizar o [Render](https://dashboard.render.com/).
Neste caso iremos fazer deploy do código que está em ```api/v1.0.0```.

Nosso primeiro passo será criar um novo repositório no GitHub. Para isso, acesse sua conta no GitHub e faça a criação deste novo repositório manualmente. 

Após criar o repositório, volte para o seu diretório de trabalho (mesmo nível do diretório ```bootcamp```, **não** dentro do mesmo) na sua máquina e clone o projeto que você acabou de criar:
```git clone <<seu-novo-repositório>>```

Agora basta mover todos os arquivos que estão no diretório ```api/v1.0.0``` para o novo diretório clonado na sua máquina.
Em seguida, executar os seguintes comandos para fazer o push para a main branch do seu repositório:
```git add .```
```git commit -m "meu primeiro deploy"```
```git push origin main```

Até aqui, você já tem um repositório GitHub com o código da API na branch ````main``. Agora vamos criar um app no Render.
A forma mais simples para fazer o deploy da API no Render é por meio da utilização [deste template](https://docs.render.com/deploy-fastapi).
Seguindo o template, basta escolher o repositório GitHub da sua API e definir o seguinte código para iniciar sua aplicação:

```puvicorn main:app --host 0.0.0.0 --port $PORT```

### Referências

Segue abaixo algumas referências usadas neste projeto.

* https://plotly.com/python/builtin-colorscales/
* https://dev.to/alexdjulin/my-runing-map-using-python-and-folium-2h2m
* https://github.com/alexdjulin/running-events-map?tab=readme-ov-file
* https://run.alexdjulin.ovh/p/events.html
* https://python-visualization.github.io/folium/latest/user_guide/raster_layers/tiles.html
* https://ayselaydin.medium.com/an-introduction-to-python-fastapi-swagger-ui-fb68d8861fad
* https://github.com/AyselAydin/fastAPI?source=post_page-----fb68d8861fad--------------------------------
* https://stackoverflow.com/questions/31575399/dynamically-add-subplots-in-matplotlib-with-more-than-one-column
* https://stackoverflow.com/questions/12444716/how-do-i-set-the-figure-title-and-axes-labels-font-size
* https://stackoverflow.com/questions/18393498/gitignore-all-the-ds-store-files-in-every-folder-and-subfolder
* https://medium.com/@elton-martins/to-reset-a-git-branch-to-match-the-master-main-branch-6692c28a36fc