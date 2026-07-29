FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cloud-image-utils \
        qemu-system-x86 \
        qemu-utils \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /usr/local/bin/buildbench-qemu-worker

ENTRYPOINT ["/usr/local/bin/buildbench-qemu-worker"]
