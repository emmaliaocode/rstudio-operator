from typing import Dict

import kopf
from kopf import Logger
from kubernetes.client.models.v1_deployment import V1Deployment
from kubernetes.client.models.v1_service import V1Service

from builder import BuildApiData
from client import KubernetesClient


@kopf.on.create("rstudios")
def create_fn(name: str, spec: Dict, namespace: str, logger: Logger, **_) -> Dict:
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

    rstudio_image: str = spec.get("image")

    api_data: BuildApiData = BuildApiData(name=name, spec=spec)
    k8s_client = KubernetesClient()

    deploy_api_data: Dict = api_data.generate_api_data(tmpl_file="deployment.yaml")
    svc_api_data: Dict = api_data.generate_api_data(tmpl_file="service.yaml")

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

    return {"rstudio-image": rstudio_image}
