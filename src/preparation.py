import os
from pathlib import Path
from typing import Dict

import yaml


class PrepareApiData:
    """Prepare data for kubernetes api requests to create rstudio-related resources

    Args:
        name (str): the name of the rstudio custom resource
    """

    def __init__(self, name: str):

        self._tmpl_path: Path = Path(os.path.dirname(__file__)) / "resources"
        self.name: str = name

    def read_template(self, file_name: str) -> str:
        """Read the specific template yaml from self._tmpl_path

        Args:
            file_name (str): the file name of the template yaml

        Returns:
            str: the content of the template yaml
        """

        path: Path = self._tmpl_path / file_name
        tmpl: str = open(path, "rt").read()

        return tmpl

    def generate_api_data(self, tmpl_file_name: str, **kwargs) -> Dict:
        """Replace values in the template yaml with name and keyword arguments and
        generate data for kubernetes api requests

        Args:
            tmpl_file_name (str): the file name of the template yaml
            **image (str): the image parameter defined in the rstudio yaml
            **image_pull_policy (str): the pull policy parametes defined in the rstudio yaml

        Returns:
            dict: a dictionary contains api data
        """

        tmpl: str = self.read_template(tmpl_file_name)
        replaced: str = tmpl.format(name=self.name, **kwargs)
        data: Dict = yaml.safe_load(replaced)

        return data
