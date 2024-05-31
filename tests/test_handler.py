import logging
import subprocess
import time
from typing import Dict
from unittest.mock import Mock

import kopf
import pytest
from kopf import PermanentError
from kopf.testing import KopfRunner
from kubernetes.client.api.apps_v1_api import AppsV1Api
from kubernetes.client.api.core_v1_api import CoreV1Api
from pytest import MonkeyPatch

from src import handler


def test_create_fn_expect_succeeded(caplog, monkeypatch: MonkeyPatch):
    # Given
    mock_generate_api_data: Mock = Mock()
    monkeypatch.setattr(
        handler.BuildApiData, "generate_api_data", mock_generate_api_data
    )

    mock_adopt: Mock = Mock()
    monkeypatch.setattr(kopf, "adopt", mock_adopt)

    mock_create_sts: Mock = Mock()
    monkeypatch.setattr(AppsV1Api, "create_namespaced_stateful_set", mock_create_sts)

    mock_create_svc: Mock = Mock()
    monkeypatch.setattr(CoreV1Api, "create_namespaced_service", mock_create_svc)

    # When
    with caplog.at_level(logging.INFO):
        result: Dict = handler.create_fn(
            name="test", spec={"image": "test"}, namespace="test", logger=logging
        )

    # Then
    mock_generate_api_data.call_count == 3
    mock_adopt.call_count == 3
    mock_create_sts.assert_called_once()
    mock_create_svc.assert_called_once()
    assert "`test` StatefulSet and Service childs are created." in caplog.text
    assert result == {"rstudio-image": "test"}


def test_create_fn_expect_failed_when_k8s_api_create_objects(
    caplog, monkeypatch: MonkeyPatch
):
    # Given
    mock_generate_api_data: Mock = Mock()
    monkeypatch.setattr(
        handler.BuildApiData, "generate_api_data", mock_generate_api_data
    )

    mock_adopt: Mock = Mock()
    monkeypatch.setattr(kopf, "adopt", mock_adopt)

    mock_create_objects: Mock = Mock(side_effect=PermanentError())
    monkeypatch.setattr(
        AppsV1Api, "create_namespaced_stateful_set", mock_create_objects
    )

    # When
    with caplog.at_level(logging.INFO):
        with pytest.raises(PermanentError):
            handler.create_fn(
                name="test", spec={"image": "test"}, namespace="test", logger=logging
            )

    # Then
    mock_generate_api_data.call_count == 3
    mock_adopt.call_count == 3
    mock_create_objects.assert_called_once()
    assert "`test` StatefulSet and Service childs are created." not in caplog.text


@pytest.mark.integtest
def test_integration_create_fn():
    """Test the kopf operator by actually creating an rstudio object

    Pre-deployed Rstudio Operator should be temporarily shut-down
    before running this test to avoid conflict
    """

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
    assert "`test` StatefulSet and Service childs are created." in runner.stdout
