FROM alpine:latest

RUN apk add --no-cache tzdata
RUN apk add --no-cache ffmpeg
RUN apk add --no-cache dumb-init

ENV TZ America/Los_Angeles
ENV CAMERA_IP 127.0.0.1
ENV CAMERA_NAME unknown
ENV CAMERA_USER nobody
ENV CAMERA_PW nothing

COPY recorder.sh /

VOLUME ["/data"]

ENTRYPOINT ["/usr/bin/dumb-init", "--rewrite", "15:2", "--"]
CMD ["/recorder.sh"]
