import json
from typing import Dict, List

import kopf
from kopf import Logger, PermanentError
from kubernetes.client.exceptions import ApiException
from kubernetes.client.models.v1_deployment import V1Deployment
from kubernetes.client.models.v1_secret import V1Secret
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

    build_api_data: BuildApiData = BuildApiData(name=name, spec=spec)
    k8s_client = KubernetesClient()

    tmpls: List = ["deployment.yaml.j2", "service.yaml.j2", "secret.yaml.j2"]

    api_data: Dict = {}

    for tmpl in tmpls:
        key: str = str(tmpl).rsplit(".")[0]
        val: Dict = build_api_data.generate_api_data(tmpl)
        kopf.adopt(val)
        api_data.update({key: val})

    try:
        _: V1Deployment = k8s_client.app_v1_api.create_namespaced_deployment(
            namespace=namespace,
            body=api_data["deployment"],
        )
        _: V1Service = k8s_client.core_v1_api.create_namespaced_service(
            namespace=namespace,
            body=api_data["service"],
        )
        _: V1Secret = k8s_client.core_v1_api.create_namespaced_secret(
            namespace=namespace, body=api_data["secret"]
        )

        logger.info(f"`{name}` Deployment, Secret and Service childs are created.")

        return {"rstudio-image": rstudio_image}

    except ApiException as e:
        if e.reason == "Conflict":
            res: Dict = json.loads(e.body)
            raise PermanentError(res["message"])
        else:
            raise PermanentError(e)
