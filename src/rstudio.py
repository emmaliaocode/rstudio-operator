import os
from pathlib import Path
from typing import Dict

import kopf
import yaml

from client import KubernetesClient


class PrepareApiData:
    """Prepare data for kubernetes api requests to create rstudio-related resources

    Args:
        name (str): the name of the rstudio custom resource
    """

    def __init__(self, name: str):

        self._tmpl_path: Path = Path(os.path.dirname(__file__)) / "resources"
        self.name: str = name

    def read_template(self, file_name: str) -> str:
        """Read the specific template yaml from `self._tmpl_path`

        Args:
            file_name (str): the file name of the template yaml

        Returns:
            str: the content of the template yaml
        """

        path: Path = self._tmpl_path / file_name
        tmpl: str = open(path, "rt").read()

        return tmpl

    def generate_api_data(self, tmpl_file_name: str, **kwargs) -> str:
        """Replace values in the template yaml with name and keyword arguments and
        generate data for kubernetes api requests

        Args:
            tmpl_file_name (str): the file name of the template yaml
            **image (str): the image parameter defined in rstudio yaml

        Returns:
            str: the content of the template yaml with user-defined values replaced
        """

        tmpl: str = self.read_template(tmpl_file_name)
        replaced: str = tmpl.format(name=self.name, **kwargs)
        data: str = yaml.safe_load(replaced)

        return data


@kopf.on.create("rstudios")
def create_fn(spec, name, namespace, logger, **kwargs) -> Dict:
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

    api_data: PrepareApiData = PrepareApiData(name=name)
    k8s_client = KubernetesClient()

    deploy_api_data: str = api_data.generate_api_data(
        tmpl_file_name="deployment.yaml", image=image
    )
    kopf.adopt(deploy_api_data)
    _ = k8s_client.app_v1_api.create_namespaced_deployment(
        namespace=namespace,
        body=deploy_api_data,
    )

    svc_api_data: str = api_data.generate_api_data(tmpl_file_name="service.yaml")
    kopf.adopt(svc_api_data)
    _ = k8s_client.core_v1_api.create_namespaced_service(
        namespace=namespace,
        body=svc_api_data,
    )

    logger.info(f"`{name}` Deployment and Service childs are created.")

    return {"deployment-image": image}
