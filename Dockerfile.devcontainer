FROM debian:bookworm

RUN apt update \
  && apt install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    git-lfs \
    iproute2 \
    python3 \
    unzip \
  && rm -rf /var/lib/apt/lists/*
