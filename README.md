# RStudio Operator

## Overview
RStudio IDE is an integrated development environment for R widely used by data scientists. The RStudio Operator aims to make running an RStudio on Kubernetes easier by using Kubernetes custom resources.

## Installation
Clone the repository and install with [Kustomize](https://kustomize.io/).
```
cd rstudio-operator
kustomize build manifests/base | kubectl apply -f -
```

## Usage
Create a RStudio object.
```bash
kubectl apply -f - <<EOF
apiVersion: emmaliaocode.dev/v1
kind: Rstudio
metadata:
  name: example
  namespace: default
spec:
  image: rocker/rstudio:latest
  imagePullPolicy: IfNotPresent
  loginPassword: cGFzc3dvcmQxMjMK
  isRoot: true
EOF
```
```bash
rstudio.emmaliaocode.dev/example created
```
Get `example` Rstudio.
```bash
kubectl get rstudio example
```
```bash
NAME      AGE
example   44s
```
