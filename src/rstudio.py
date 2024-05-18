import os

import kopf
import kubernetes
import yaml


@kopf.on.create("rstudios")
def create_fn(spec, name, namespace, logger, **kwargs):

    image: str = spec.get("image")

    # create a deployment

    path = os.path.join(os.path.dirname(__file__), "resources/deployment.yaml")
    tmpl = open(path, "rt").read()
    text = tmpl.format(name=name, image=image)
    data = yaml.safe_load(text)

    kopf.adopt(data)

    api = kubernetes.client.AppsV1Api()
    deploy_obj = api.create_namespaced_deployment(
        namespace=namespace,
        body=data,
    )
    logger.info(f"`{deploy_obj.metadata.name}` {deploy_obj.kind} child is created.")

    # create a service

    path = os.path.join(os.path.dirname(__file__), "resources/service.yaml")
    tmpl = open(path, "rt").read()
    text = tmpl.format(name=name)
    data = yaml.safe_load(text)

    kopf.adopt(data)

    api = kubernetes.client.CoreV1Api()
    svc_obj = api.create_namespaced_service(
        namespace=namespace,
        body=data,
    )
    logger.info(f"`{svc_obj.metadata.name}` {svc_obj.kind} child is created.")

    return {"deployment-image": image}
