# This image is used to prepare test samples for test cases
FROM debian:bullseye-slim

USER root
RUN echo "deb http://deb.debian.org/debian bookworm-backports main" >> /etc/apt/sources.list

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    upx gcc-mingw-w64-i686-win32 build-essential
