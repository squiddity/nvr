FROM bitnami/python:3.7

RUN pip install discord aiofiles

ENV PORT 0
ENV DISCORD some_token
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY dom5bot.py /app
CMD ["python", "dom5bot.py"]
