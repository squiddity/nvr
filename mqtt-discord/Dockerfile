FROM bitnami/python:3.7

RUN pip install hbmqtt discord

ENV MQTT mqtt://127.0.0.1:1883/
ENV DISCORD some_token
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY bot.py /app
CMD ["python", "bot.py"]
