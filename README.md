# TGRAINS Crop model

## For full documentation, view the page at [https://tgrains.bitbucket.io/](https://tgrains.bitbucket.io/)

This repository contains the backend code for the [TGRAINS crop modelling tool](https://model.tgrains.com/).

The backend is written in C++ and is included as a .so shared object (a Linux DLL) leveraging the Landscape Model provided by our project partners at [Rothamsted Research](https://www.rothamsted.ac.uk/rothamsted-landscape-model). This is made accessible to the frontend as a REST API via a Python Flask server and Celery task runner.

For full documentation on the system architecture and further development guidance, see [https://tgrains.bitbucket.io](https://tgrains.bitbucket.io).

## Automatic builds

This repository is set up to automatically run a build with [Bitbucket Pipelines](https://support.atlassian.com/bitbucket-cloud/docs/get-started-with-bitbucket-pipelines/). This builds the code to a docker container and pushes it to DockerHub. The URL for the container repository is:

https://hub.docker.com/repository/docker/samfinnigan/tgrains-cropmodel-frontend

Bitbucket limits build minutes to 50 a month. This project needs double the space to build, so will be billed for double time. You therefore probably only want to push to the master branch when building for production. For source-controlling development code, use a git branch: `git checkout -b development`.

To build the code on your local machine, use instead docker build. See the bitbucket-pipelines.yml file for a detailed build script.
