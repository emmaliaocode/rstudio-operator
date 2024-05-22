import os
from pathlib import Path

import pytest


@pytest.fixture
def project_path() -> Path:
    """Fixture to provide the path to the project root"""

    return Path(os.path.dirname(__file__))


@pytest.fixture
def resources_path(project_path: Path) -> Path:
    """Fixture to provide the path to the folder of test resources"""

    return project_path / "resources"
