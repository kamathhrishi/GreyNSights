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
    
RUN add-apt-repository ppa:ubuntu-toolchain-r/test
RUN apt -y update
RUN apt -y upgrade
RUN apt-get -y install gcc-9
RUN apt-get -y install libstdc++6
RUN apt-get -y upgrade libstdc++6

RUN python3.9 -m pip install --upgrade pip

COPY ./ GreyNSights

WORKDIR GreyNSights

RUN pip install -r requirements.txt
RUN python3 setup.py install

ENTRYPOINT [ "/bin/bash" ]
