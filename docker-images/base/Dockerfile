FROM ubuntu:18.04

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install git clang build-essential
RUN apt-get -y install software-properties-common
RUN apt-get -y install python3.7
RUN apt-get -y install python3-pip

RUN python3.7 -m pip install --upgrade pip
RUN apt-get -y upgrade libstdc++6

COPY ./ GreyNSights

WORKDIR GreyNSights

RUN pip3 install -r requirements.txt
RUN python3 setup.py install

ENTRYPOINT [ "/bin/bash" ]
