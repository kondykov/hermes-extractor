FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    unzip \
    git \
    cmake \
    build-essential \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Установка hbctool
RUN pip3 install --break-system-packages \
    git+https://github.com/bongtrop/hbctool.git

# Установка Hermes CLI
RUN git clone https://github.com/facebook/hermes.git /hermes
WORKDIR /hermes
RUN ./gradlew :hermes-cli:installDist

# Добавляем hermesc в PATH
ENV PATH="/hermes/hermes-cli/build/install/hermes/bin:${PATH}"

# Директории пайплайна
WORKDIR /app
RUN mkdir -p /input /output

COPY app/* /app/
RUN chmod +x /app/pipeline.sh

ENTRYPOINT ["/app/pipeline.sh"]
