import os
from pathlib import Path
from typing import Dict

import yaml
from jinja2 import Environment, FileSystemLoader, Template


class BuildApiData:
    """Prepare data for kubernetes api data to create rstudio-related resources

    Args:
        name (str): the name of the custom resource
        spec (dict): the specification part of the custom resource
    """

    def __init__(self, name: str, spec: Dict):

        self._tmpl_dir: Path = Path(os.path.dirname(__file__)) / "resources"
        self.name: str = name
        self.spec: Dict = spec

    def render_template(self, tmpl: str) -> str:
        """Read the specific template yaml from self._tmpl_path

        Args:
            tmpl (str): the file name of the template yaml

        Returns:
            str: the rendered yaml
        """

        env: Environment = Environment(loader=FileSystemLoader(self._tmpl_dir))
        template: Template = env.get_template(tmpl)

        return template.render(name=self.name, spec=self.spec)

    def generate_api_data(self, tmpl: str) -> Dict:
        """Generate data for kubernetes api requests

        Args:
            tmpl (str): the file name of the template yaml

        Returns:
            dict: a dictionary of api data
        """

        rendered_tmpl: str = self.render_template(tmpl=tmpl)
        data: Dict = yaml.safe_load(rendered_tmpl)

        return data
