FROM continuumio/miniconda3:v25.11.1-1 AS build
LABEL maintainer="Samantha Finnigan"
WORKDIR /app

# https://pythonspeed.com/articles/conda-docker-image-size/
# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Install conda-pack:
RUN conda install -c conda-forge conda-pack \
    && conda clean -afy

# Use conda-pack to create a standalone environment
# in /venv:
RUN conda-pack -n tgrains -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack


# Build multistage image for runtime
FROM ubuntu:noble AS runtime
WORKDIR /app

# set environment variables (don't buffer stdout, don't write bytecode)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies via apt
# libTGRAINS.so was compiled against Boost 1.71 (Ubuntu Focal). Noble only has 1.83,
# so we install the Focal .deb directly — its only deps are libc6/libgcc/libstdc++.
RUN apt-get update &&\
    apt-get install -y libgfortran5 curl &&\
    curl -fsSLo /tmp/libboost-serialization.deb \
      http://archive.ubuntu.com/ubuntu/pool/main/b/boost1.71/libboost-serialization1.71.0_1.71.0-6ubuntu6_amd64.deb &&\
    dpkg -i /tmp/libboost-serialization.deb &&\
    rm /tmp/libboost-serialization.deb &&\
    apt-get purge -y curl && apt-get autoremove -y &&\
    rm -rf /var/lib/apt/lists/*

# Copy /venv from the build stage
COPY --from=build /venv /venv

COPY ./model/FieldStats /FieldStats
COPY ./model/Weather /Weather
RUN mkdir /OutFiles

# Copy rest of app environment
COPY . /app

EXPOSE 5000

RUN touch /app/run.sh && chmod +x /app/run.sh && echo 'source /venv/bin/activate && $*' > /app/run.sh

# Use entrypoint to run commands under environment
SHELL ["/bin/bash", "-c"]
ENTRYPOINT ["/bin/bash", "/app/run.sh"]

CMD ["gunicorn", "--worker-tmp-dir=/dev/shm", "--workers=2", "--threads=4", "--worker-class=gthread", "--timeout=120", "--log-file=-", "--bind=0.0.0.0:5000", "server:app"]

# Command examples for running this image as webserver or task worker
#CMD gunicorn --worker-tmp-dir=/dev/shm --workers=2 --threads=4 --worker-class=gthread --timeout=120 --log-file=- --bind=0.0.0.0:5000 server:app
#CMD celery -A tasks.celery worker --loglevel=INFO --concurrency=8
