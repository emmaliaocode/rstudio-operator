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
Create a password secret to login to RStudio IDE.
```bash
kubectl create secret generic rstudio-secret --from-literal=password=[password]
```
Create a RStudio custom resource.
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
  loginSecret: rstudio-secret
  isRoot: true
  resources:
    requests:
      cpu: "250m"
      memory: "64Mi"
    limits:
      cpu: "500m"
      memory: "128Mi"
  storages:
  - name: rstudio-pvc
    storageClassName: standard
    storageSize: "1Gi"
    accessModes:
    - "ReadWriteMany"
  volumeMounts:
  - name: rstudio-pvc
    mountPath: /data
EOF
```
```bash
rstudio.emmaliaocode.dev/example created
```
Get `example` Rstudio.
```bash
kubectl get all -l rstudio=example
```
```bash
NAME                    READY   STATUS    RESTARTS   AGE
pod/example-rstudio-0   1/1     Running   0          4m13s

NAME                      TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
service/example-rstudio   NodePort   10.109.56.60   <none>        8787:32378/TCP   4m13s

NAME                               READY   AGE
statefulset.apps/example-rstudio   1/1     4m13s
```
