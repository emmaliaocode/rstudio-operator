import logging
import subprocess
import time
from typing import Dict
from unittest.mock import Mock

import kopf
import pytest
from kopf.testing import KopfRunner
from kubernetes.client.api.apps_v1_api import AppsV1Api
from kubernetes.client.api.core_v1_api import CoreV1Api
from pytest import MonkeyPatch

from src import handler


def test_create_fn(caplog, monkeypatch: MonkeyPatch):
    # Given
    mock_generate_api_data: Mock = Mock()
    monkeypatch.setattr(
        handler.BuildApiData, "generate_api_data", mock_generate_api_data
    )

    mock_adopt: Mock = Mock()
    monkeypatch.setattr(kopf, "adopt", mock_adopt)

    mock_create_deploy: Mock = Mock()
    monkeypatch.setattr(AppsV1Api, "create_namespaced_deployment", mock_create_deploy)

    mock_create_svc: Mock = Mock()
    monkeypatch.setattr(CoreV1Api, "create_namespaced_service", mock_create_svc)

    mock_create_secret: Mock = Mock()
    monkeypatch.setattr(CoreV1Api, "create_namespaced_secret", mock_create_secret)

    # When
    with caplog.at_level(logging.INFO):
        result: Dict = handler.create_fn(
            name="test", spec={"image": "test"}, namespace="test", logger=logging
        )

    # Then
    mock_generate_api_data.call_count == 3
    mock_adopt.call_count == 3
    mock_create_deploy.assert_called_once()
    mock_create_svc.assert_called_once()
    mock_create_secret.assert_called_once()
    expected: Dict = {"rstudio-image": "test"}
    result == expected


@pytest.mark.integtest
def test_integration_create_fn():
    """Test the kopf operator by creating rstudio object"""

    # When
    with KopfRunner(["run", "src/handler.py", "--verbose"]) as runner:

        subprocess.run(
            "kubectl apply -f tests/resources/rstudio.yaml", shell=True, check=True
        )
        time.sleep(1)

        subprocess.run(
            "kubectl delete -f tests/resources/rstudio.yaml", shell=True, check=True
        )
        time.sleep(1)

    # Then
    assert runner.exit_code == 0
    assert runner.exception is None
    print(runner.stdout)
    assert "`test` Deployment, Secret and Service childs are created." in runner.stdout
