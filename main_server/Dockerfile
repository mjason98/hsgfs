FROM python:3.9

ARG APP_PORT=8020

WORKDIR /app_main

ENV CHUNKS_PORTS=app1:8080
ENV ENV_PORT=$APP_PORT

COPY services services
COPY requirements.txt .
COPY app.py .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD python -m gunicorn --bind 0.0.0.0:$ENV_PORT app:app
