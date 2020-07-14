FROM continuumio/miniconda3:4.8.2
MAINTAINER Samantha Finnigan
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /app/requirements.txt
RUN . /opt/conda/etc/profile.d/conda.sh &&\
     conda install -c conda-forge --file requirements.txt

# Install dependencies via apt (debian testing branch required for libboost-serialization1.71.0)
RUN sed -i 's/buster\/updates/testing-security/; s/buster/testing/g' /etc/apt/sources.list &&\
    apt-get update &&\
    apt-get install -y build-essential g++ libgfortran5 libboost-serialization1.71.0 &&\
    rm -rf /var/lib/apt/lists/*

# Copy rest of app environment
COPY . /app

COPY ./model/FieldStats /FieldStats
COPY ./model/Weather /Weather
RUN mkdir /OutFiles

EXPOSE 5000

CMD gunicorn --worker-tmp-dir /dev/shm \
            --workers=2 --threads=4 --worker-class=gthread \
            --timeout 120 \
            --bind 0.0.0.0:5000 'server:app'
