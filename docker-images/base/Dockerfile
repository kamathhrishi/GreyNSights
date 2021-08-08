FROM ubuntu:18.04

ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-slim-buster

# Install apt-get packages
RUN apt-get update && \
    apt-get -y install \
    sudo \
    wget \
    zip \
    git \
    software-properties-common \
    gcc \
    g++ \
    clang-format \
    build-essential \
    python3-distutils \
    pkg-config \
    zlib1g-dev
    

RUN python3.9 -m pip install --upgrade pip
RUN apt-get -y upgrade libstdc++6

COPY ./ GreyNSights

WORKDIR GreyNSights

RUN pip3 install -r requirements.txt
RUN python3 setup.py install

ENTRYPOINT [ "/bin/bash" ]
