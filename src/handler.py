from typing import Dict

import kopf
from kopf import Logger
from kubernetes.client.models.v1_deployment import V1Deployment
from kubernetes.client.models.v1_service import V1Service

from client import KubernetesClient
from preparation import PrepareApiData


@kopf.on.create("rstudios")
def create_fn(spec: Dict, name: str, namespace: str, logger: Logger, **_) -> Dict:
    """Handler function that is called when a new rstudio custom resource is created

    Args:
        spec (dict): the specification part of the custom resource
        name (str): the name of the custom resource
        namespace (str): the namespace in which the custom resource is created
        logger (kopf.Logger): the logger instance for logging within the handler
        **kwargs: arbitrary keyword arguments

    Returns:
        dict: a dictionary representing the result of the creation process
    """

    image: str = spec.get("image")
    image_pull_policy: str = spec.get("imagePullPolicy")

    api_data: PrepareApiData = PrepareApiData(name=name)
    k8s_client = KubernetesClient()

    deploy_api_data: Dict = api_data.generate_api_data(
        tmpl_file_name="deployment.yaml",
        image=image,
        image_pull_policy=image_pull_policy,
    )
    svc_api_data: Dict = api_data.generate_api_data(tmpl_file_name="service.yaml")

    kopf.adopt(deploy_api_data)
    kopf.adopt(svc_api_data)

    _: V1Deployment = k8s_client.app_v1_api.create_namespaced_deployment(
        namespace=namespace,
        body=deploy_api_data,
    )
    _: V1Service = k8s_client.core_v1_api.create_namespaced_service(
        namespace=namespace,
        body=svc_api_data,
    )

    logger.info(f"`{name}` Deployment and Service childs are created.")

    return {"rstudio-image": image}
