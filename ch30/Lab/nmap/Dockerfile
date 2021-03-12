FROM debian:bullseye-slim
RUN apt update -y && \
    apt-get install nmap -y

ENTRYPOINT ["/usr/bin/nmap"]