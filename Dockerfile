FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копируем локальный hermes-dec
WORKDIR /app
COPY bin/hermes-dec /usr/local/bin/hermes-dec
RUN chmod +x /usr/local/bin/hermes-dec

RUN mkdir -p /input /output

COPY app/* /app/
RUN chmod +x /app/pipeline.sh

ENTRYPOINT ["/app/pipeline.sh"]
