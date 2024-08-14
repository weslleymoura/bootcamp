FROM python:3.10

WORKDIR /app

COPY ./requirements.txt .
COPY ./api ./api

#ENV PYTHONPATH=/app/api
ENV PYTHONPATH="$PYTHONPATH:/app/api"

RUN pip install -r requirements.txt