FROM ubuntu:focal
MAINTAINER Samantha Finnigan
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies via apt
RUN apt-get update &&\
    apt-get install -y build-essential wget g++ libgfortran5 libboost-serialization1.71.0 &&\
    rm -rf /var/lib/apt/lists/*

# Install Conda. Taken from miniconda3 Dockerfile
ENV PATH=/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh &&\
    /bin/bash ~/miniconda.sh -b -p /opt/conda &&\
    rm ~/miniconda.sh &&\
    /opt/conda/bin/conda clean -tipsy &&\
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh &&\
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc &&\
    echo "conda activate base" >> ~/.bashrc &&\
    find /opt/conda/ -follow -type f -name '*.a' -delete &&\
    find /opt/conda/ -follow -type f -name '*.js.map' -delete &&\
    /opt/conda/bin/conda clean -afy

# https://pythonspeed.com/articles/activate-conda-dockerfile/
# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# COPY ./requirements.txt /app/requirements.txt
# RUN . /opt/conda/etc/profile.d/conda.sh &&\
#      conda install -c conda-forge --file requirements.txt

# Copy rest of app environment
COPY . /app

COPY ./model/FieldStats /FieldStats
COPY ./model/Weather /Weather
RUN mkdir /OutFiles

EXPOSE 5000

# Use entrypoint to run commands under conda environment
# conda run -n tgrains /bin/bash -c
ENTRYPOINT ["conda", "run", "-n", "tgrains"]

CMD gunicorn --worker-tmp-dir /dev/shm \
            --workers=2 --threads=4 --worker-class=gthread \
            --timeout 120 --log-file=- \
            --bind 0.0.0.0:5000 'server:app'

#CMD celery worker -A tasks.celery --loglevel=INFO --concurrency=8
