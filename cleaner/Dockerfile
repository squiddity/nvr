FROM alpine:latest

COPY cleaner.sh /etc/periodic/hourly/cleaner.sh

RUN chmod +x /etc/periodic/hourly/cleaner.sh

VOLUME ["/data"]

CMD ["crond", "-l", "2", "-f"]
