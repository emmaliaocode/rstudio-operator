import os
from pathlib import Path
from typing import Dict

import yaml


class BuildApiData:
    """Prepare data for kubernetes api requests to create rstudio-related resources

    Args:
        name (str): the name of the custom resource
        spec (dict): the specification part of the custom resource
    """

    def __init__(self, name: str, spec: Dict):

        self._tmpl_path: Path = Path(os.path.dirname(__file__)) / "resources"
        self.name: str = name
        self.spec: Dict = spec

        self.parameters: Dict = {}

    def get_parameters(self) -> Dict:
        """Get parameters by retrieve_parameters function"""

        params: tuple = self.retrieve_parameters(self.spec)

        self.parameters = dict(params)

    def retrieve_parameters(self, spec: Dict):
        """Recursively retrieves parameters from a nested dictionary

        Args:
            spec (dict): the specification part of the custom resource

        Yields:
            tuple: a tuple containing a key and its corresponding value
        """

        for key, val in spec.items():
            if isinstance(val, dict):
                yield from self.retrieve_parameters(val)
            else:
                yield (key, val)

    def read_template(self, file_name: str) -> str:
        """Read the specific template yaml from self._tmpl_path

        Args:
            file_name (str): the file name of the template yaml

        Returns:
            str: the content of the template yaml
        """

        path: Path = self._tmpl_path / file_name
        template: str = open(path, "rt").read()

        return template

    def replace_values(self, template: str) -> str:
        """Replace values in the template yaml with parametes

        Args:
            tmpl_text (str): the content of the template yaml

        Returns:
            str: the content of the yaml
        """

        return template.format(name=self.name, **self.parameters)

    def generate_api_data(self, tmpl_file: str) -> Dict:
        """Generate data for kubernetes api requests

        Args:
            tmpl_file_name (str): the file name of the template yaml

        Returns:
            dict: a dictionary contains api data
        """

        self.get_parameters()

        tmpl: str = self.read_template(file_name=tmpl_file)
        replaced: str = self.replace_values(template=tmpl)
        data: Dict = yaml.safe_load(replaced)

        return data
