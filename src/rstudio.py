import os
from pathlib import Path

import kopf
import yaml

from client import KubernetesClient


class PrepareApiData:

    def __init__(self, name: str):

        self._tmpl_path: Path = Path(os.path.dirname(__file__)) / "resources"
        self.name: str = name

    def read_template(self, file_name: str):

        path: Path = self._tmpl_path / file_name
        tmpl: str = open(path, "rt").read()

        return tmpl

    def replace_template_values(self, tmpl: str, **kwargs):

        replaced: str = tmpl.format(name=self.name, **kwargs)
        text: str = yaml.safe_load(replaced)

        return text

    def generate_api_data(self, tmpl_file_name: str, **kwargs):

        tmpl: str = self.read_template(tmpl_file_name)
        data: str = self.replace_template_values(tmpl, **kwargs)

        return data


@kopf.on.create("rstudios")
def create_fn(spec, name, namespace, logger, **kwargs):

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
