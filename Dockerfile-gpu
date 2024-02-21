# syntax=docker/dockerfile:1

FROM nvcr.io/nvidia/cuda:11.0.3-base-ubuntu20.04

RUN apt-get -y update \
    && apt-get install -y software-properties-common  \
    && apt-get -y update \
    && add-apt-repository universe
RUN apt-get -y update
RUN apt-get install docker.io -y
RUN apt-get -y install python3
RUN apt-get -y install python3-pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
