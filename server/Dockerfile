FROM continuumio/miniconda3:4.8.2-alpine
MAINTAINER Samantha Finnigan
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /app/requirements.txt
RUN . /opt/conda/etc/profile.d/conda.sh &&\
     conda install -c conda-forge --file requirements.txt

# Uhuh... https://github.com/ContinuumIO/docker-images/pull/141
# (seems to be only required for Alpine)
ENV PATH="/opt/conda/bin:${PATH}"

# Copy rest of app environment
COPY . /app

EXPOSE 5000

ENTRYPOINT gunicorn --worker-tmp-dir /dev/shm \
            --workers=2 --threads=4 --worker-class=gthread \
            --timeout 120 \
            --bind 0.0.0.0:5000 'server:app'
