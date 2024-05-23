import logging
import subprocess
import time
from typing import Dict
from unittest.mock import Mock

import kopf
import pytest
from kopf.testing import KopfRunner
from kubernetes.client import AppsV1Api, CoreV1Api
from pytest import LogCaptureFixture, MonkeyPatch

from src import handler
from src.preparation import PrepareApiData


def test_create_fn(monkeypatch: MonkeyPatch, caplog: LogCaptureFixture):
    # Given
    mock_generate_api_data: Mock = Mock()
    monkeypatch.setattr(PrepareApiData, "generate_api_data", mock_generate_api_data)

    mock_adopt: Mock = Mock()
    monkeypatch.setattr(kopf, "adopt", mock_adopt)

    mock_create_deploy: Mock = Mock()
    monkeypatch.setattr(AppsV1Api, "create_namespaced_deployment", mock_create_deploy)

    mock_create_svc: Mock = Mock()
    monkeypatch.setattr(CoreV1Api, "create_namespaced_service", mock_create_svc)

    # When
    with caplog.at_level(logging.INFO):
        result: Dict = handler.create_fn(
            spec={"image": "test", "image_pull_policy": "test"},
            name="test",
            namespace="test",
            logger=logging,
        )

    # Then
    assert mock_generate_api_data.call_count == 2
    assert mock_adopt.call_count == 2
    mock_create_deploy.assert_called_once()
    mock_create_svc.assert_called_once()
    assert result == {"rstudio-image": "test"}
    assert "`test` Deployment and Service childs are created." in caplog.records[0].msg


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
    assert "`test` Deployment and Service childs are created." in runner.stdout
