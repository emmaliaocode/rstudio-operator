# Contributing Guidelines
Thank you for considering contributing to this project! This document outlines the setup instructions and development workflow to help you get started.

## Table of Contents
- [Setup Kubernetes Environment](#setup-kubernetes-environment)
- [Setup Python Virtual Environment](#setup-python-virtual-environment)
- [Run RStudio Operator locally](#run-rstudio-operator-locally)
- [Contribution Process](#contribution-process)

## Setup Kubernetes Environment
To develop the operator and in an isolated Kubernetes cluter, [install minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download). And start the minikube cluster with the following command.

```bash
minikube start
```
Then deploy the Rstudio Custom Resource Definition (CRD).
```
kubectl get nodes
kubectl apply -f manifests/base/crd.yaml
```

## Setup Python Virtual Environment
Use any tool you’re comfortable with to manage Python virtual environments and make sure the dependencies are installed.
```bash
uv venv
uv sync
```

## Run RStudio Operator locally
To test your Operator locally using `Kopf`, run:
```bash
kopf run src/handler.py
```
Kopf will watch your Kubernetes cluster and handle custom resources as defined.

## Contribution Process
1. Fork the repository
2. Create a new branch: `git checkout -b feat/your-feature-name`
3. Make your changes
4. Test locally with `kopf run`
5. Commit and push: `git commit -m "commit message` then `git push origin feat/your-feature-name`
6. Submit a Pull Request
