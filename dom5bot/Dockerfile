FROM bitnami/python:3.7

RUN pip install discord aiofiles
# packages required for headless dom5.sh
RUN install_packages libglu1 libsdl2-2.0-0
RUN install_packages lsb-release
RUN install_packages procps

ENV PORT 0
ENV DISCORD some_token
ENV CHANNEL general
ENV DOM5USERDIR /dom5user
ENV DOM5GAMEDIR /dom5game
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY dom5bot.py /app
CMD ["python", "dom5bot.py"]
