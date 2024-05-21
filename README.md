# RStudio Operator

## Overview
RStudio IDE is an integrated development environment for R widely used by data scientists. The RStudio Operator aims to make running an RStudio on Kubernetes easier by using Kubernetes custom resources.

The RStudio Operator supports the following features:
- Support various R versions: choose the desired version from [DockerHub](https://hub.docker.com/r/rocker/rstudio/tags)
- TBD

## Installation
Clone the repository and install with [Kustomize](https://kustomize.io/).
```
cd rstudio-operator
kustomize build manifests | kubectl apply -f -
```
