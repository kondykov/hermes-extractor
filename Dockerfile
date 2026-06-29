FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install hermes-dec --break-system-packages

WORKDIR /app
RUN mkdir -p /input /output

COPY app/* /app/

RUN chmod +x /app/pipeline.sh

ENTRYPOINT ["/app/pipeline.sh"]
