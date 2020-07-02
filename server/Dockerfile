FROM continuumio/miniconda3:4.8.2
MAINTAINER Samantha Finnigan
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /app/requirements.txt
RUN . /opt/conda/etc/profile.d/conda.sh &&\
     conda install -c conda-forge --file requirements.txt

# Sorry... We need libboost-serialization for the model :(
RUN apt-get update &&\
    apt-get install -y build-essential g++ libgfortran5 &&\
    rm -rf /var/lib/apt/lists/*

RUN export VERSION=1_72_0                                &&\
    export V_DOTS=$( echo ${VERSION} | tr '_' '.' )      &&\
    \
    echo "Installing libboost${V_DOTS} from source..."   &&\
                                                           \
    echo "Downloading boost from sourceforge... (quiet)" &&\
    wget -nv -O boost_${VERSION}.tar.gz                    \
        https://sourceforge.net/projects/boost/files/boost/${V_DOTS}/boost_${VERSION}.tar.gz/download &&\
                                                           \
    echo "Extracting boost..."                           &&\
    tar xzf boost_${VERSION}.tar.gz                      &&\
    cd boost_${VERSION}/                                 &&\
                                                           \
    ./bootstrap.sh --prefix=/usr/                        &&\
    ./b2 --with-serialization install                    &&\
                                                           \
    cd ../                                               &&\
    rm -rf boost_${VERSION}                              &&\
    rm boost_${VERSION}.tar.gz                           &&\
    echo "Installed libboost-serialization${V_DOTS}"

# Uhuh... https://github.com/ContinuumIO/docker-images/pull/141
# (seems to be only required for Alpine)
ENV PATH="/opt/conda/bin:${PATH}"

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
