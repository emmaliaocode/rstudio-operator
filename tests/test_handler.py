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
from kubernetes.client.models.v1_object_meta import V1ObjectMeta
from kubernetes.client.models.v1_persistent_volume_claim import V1PersistentVolumeClaim
from kubernetes.client.models.v1_persistent_volume_claim_list import V1PersistentVolumeClaimList
from pytest import MonkeyPatch

from src import handler


def test_generate_storage_status_expect_return_storage_name(monkeypatch: MonkeyPatch):
    # Given
    fake_name: str = "test"
    fake_spec: Dict = {"storages": "test"}
    fake_namespace: str = "test"

    fake_pvc_list: V1PersistentVolumeClaimList = V1PersistentVolumeClaimList(
        items=[V1PersistentVolumeClaim(metadata=V1ObjectMeta(name="test"))]
    )

    mock_list_pvc: Mock = Mock(return_value=fake_pvc_list)
    monkeypatch.setattr(CoreV1Api, "list_namespaced_persistent_volume_claim", mock_list_pvc)

    # When
    result: Dict = handler.generate_storage_status(name=fake_name, spec=fake_spec, namespace=fake_namespace)

    # Then
    mock_list_pvc.assert_called_once()
    assert result == {"storage-pvc": "test"}


def test_generate_storage_status_expect_return_storage_unspecified():
    # Given
    fake_name: str = "test"
    fake_spec: Dict = {}
    fake_namespace: str = "test"

    # When
    result: Dict = handler.generate_storage_status(name=fake_name, spec=fake_spec, namespace=fake_namespace)

    # Then
    assert result == {"storage-pvc": "storage unspecified"}


def test_create_fn_expect_succeeded(caplog, monkeypatch: MonkeyPatch):
    # Given
    fake_name: str = "test"
    fake_spec: Dict = {}
    fake_namespace: str = "test"

    mock_generate_api_data: Mock = Mock()
    monkeypatch.setattr(handler.BuildApiData, "generate_api_data", mock_generate_api_data)

    mock_adopt: Mock = Mock()
    monkeypatch.setattr(kopf, "adopt", mock_adopt)

    mock_create_sts: Mock = Mock()
    monkeypatch.setattr(AppsV1Api, "create_namespaced_stateful_set", mock_create_sts)

    mock_create_svc: Mock = Mock()
    monkeypatch.setattr(CoreV1Api, "create_namespaced_service", mock_create_svc)

    fake_status: Dict = {"test": "test"}
    mock_generate_storage_status: Mock = Mock(return_value=fake_status)
    monkeypatch.setattr(handler, "generate_storage_status", mock_generate_storage_status)

    # When
    with caplog.at_level(logging.INFO):
        result: Dict = handler.create_fn(name=fake_name, spec=fake_spec, namespace=fake_namespace, logger=logging)

    # Then
    mock_generate_api_data.call_count == 2
    mock_adopt.call_count == 2
    mock_create_sts.assert_called_once()
    mock_create_svc.assert_called_once()
    mock_generate_storage_status.assert_called_once()
    assert "`test` StatefulSet and Service childs are created." in caplog.text
    assert result == fake_status


def test_create_fn_expect_failed_when_k8s_api_create_sts(caplog, monkeypatch: MonkeyPatch):
    # Given
    fake_name: str = "test"
    fake_spec: Dict = {}
    fake_namespace: str = "test"

    mock_generate_api_data: Mock = Mock()
    monkeypatch.setattr(handler.BuildApiData, "generate_api_data", mock_generate_api_data)

    mock_adopt: Mock = Mock()
    monkeypatch.setattr(kopf, "adopt", mock_adopt)

    mock_create_sts: Mock = Mock(side_effect=PermanentError("error"))
    monkeypatch.setattr(AppsV1Api, "create_namespaced_stateful_set", mock_create_sts)

    mock_create_svc: Mock = Mock()
    monkeypatch.setattr(CoreV1Api, "create_namespaced_service", mock_create_svc)

    mock_generate_storage_status: Mock = Mock()
    monkeypatch.setattr(handler, "generate_storage_status", mock_generate_storage_status)

    # When
    with caplog.at_level(logging.INFO):
        with pytest.raises(PermanentError) as e:
            handler.create_fn(name=fake_name, spec=fake_spec, namespace=fake_namespace, logger=logging)

    # Then
    mock_generate_api_data.call_count == 2
    mock_adopt.call_count == 2
    mock_create_sts.assert_called_once()
    mock_create_svc.assert_not_called()
    mock_generate_storage_status.assert_not_called()
    assert str(e.value) == "error"
    assert "`test` StatefulSet and Service childs are created." not in caplog.text


def test_update_fn_expect_succeeded(caplog, monkeypatch: MonkeyPatch):
    # Given
    fake_name: str = "test"
    fake_spec: Dict = {}
    fake_namespace: str = "test"

    mock_generate_api_data: Mock = Mock()
    monkeypatch.setattr(handler.BuildApiData, "generate_api_data", mock_generate_api_data)

    mock_adopt: Mock = Mock()
    monkeypatch.setattr(kopf, "adopt", mock_adopt)

    mock_replace_sts: Mock = Mock()
    monkeypatch.setattr(AppsV1Api, "replace_namespaced_stateful_set", mock_replace_sts)

    # When
    with caplog.at_level(logging.INFO):
        handler.update_fn(name=fake_name, spec=fake_spec, namespace=fake_namespace, logger=logging)

    # Then
    mock_generate_api_data.assert_called_once()
    mock_adopt.assert_called_once()
    mock_replace_sts.assert_called_once()
    assert "`test` StatefulSet childs are updated." in caplog.text


def test_update_fn_expect_failed_when_k8s_api_replace_sts(caplog, monkeypatch: MonkeyPatch):
    # Given
    fake_name: str = "test"
    fake_spec: Dict = {}
    fake_namespace: str = "test"

    mock_generate_api_data: Mock = Mock()
    monkeypatch.setattr(handler.BuildApiData, "generate_api_data", mock_generate_api_data)

    mock_adopt: Mock = Mock()
    monkeypatch.setattr(kopf, "adopt", mock_adopt)

    mock_replace_sts: Mock = Mock(side_effect=PermanentError("error"))
    monkeypatch.setattr(AppsV1Api, "replace_namespaced_stateful_set", mock_replace_sts)

    mock_generate_storage_status: Mock = Mock()
    monkeypatch.setattr(handler, "generate_storage_status", mock_generate_storage_status)

    # When
    with caplog.at_level(logging.ERROR):
        with pytest.raises(PermanentError) as e:
            handler.update_fn(name=fake_name, spec=fake_spec, namespace=fake_namespace, logger=logging)

    # Then
    mock_generate_api_data.assert_called_once()
    mock_adopt.assert_called_once()
    mock_replace_sts.assert_called_once()
    mock_generate_storage_status.assert_not_called()
    assert str(e.value) == "error"
    assert "`test` StatefulSet childs are updated." not in caplog.text


@pytest.mark.integtest
def test_integration_create_fn():
    """Test the kopf operator by actually creating an rstudio object

    Pre-deployed Rstudio Operator should be temporarily shut-down
    before running this test to avoid conflict
    """

    # When
    with KopfRunner(["run", "src/handler.py", "--verbose"]) as runner:
        subprocess.run("kubectl apply -f tests/resources/rstudio.yaml", shell=True, check=True)
        time.sleep(1)

        subprocess.run("kubectl delete -f tests/resources/rstudio.yaml", shell=True, check=True)
        time.sleep(1)

    # Then
    assert runner.exit_code == 0
    assert runner.exception is None
    assert "`test` StatefulSet and Service childs are created." in runner.stdout
