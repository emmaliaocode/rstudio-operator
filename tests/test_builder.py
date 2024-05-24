from pathlib import Path
from typing import Dict
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from src.builder import BuildApiData


class TestParseApiData:
    """Test cases for the PrepareApiData class."""

    @pytest.fixture
    def build_api_data(self, resources_path: Path):
        """Fixture to provide a PrepareApiData instance for the tests"""

        inst: BuildApiData = BuildApiData(name="", spec={})
        inst._tmpl_path = resources_path

        return inst

    def test_get_parameters(
        self, monkeypatch: MonkeyPatch, build_api_data: BuildApiData
    ):
        # Given
        fake_params: tuple = (("key1", "val1"), ("key3", "val3"))
        mock_retrieve_params: Mock = Mock(return_value=fake_params)
        monkeypatch.setattr(BuildApiData, "retrieve_parameters", mock_retrieve_params)

        # When
        build_api_data.get_parameters()

        # Then
        mock_retrieve_params.assert_called_once()
        expected: Dict = {"key1": "val1", "key3": "val3"}
        assert build_api_data.parameters == expected

    @pytest.mark.parametrize(
        "input, expected",
        [
            ({"key1": "val1", "key2": "val2"}, {"key1": "val1", "key2": "val2"}),
            (
                {"key1": "val1", "key2": {"key3": "val3"}},
                {"key1": "val1", "key3": "val3"},
            ),
        ],
    )
    def test_retrieve_parameters(
        self, build_api_data: BuildApiData, input: Dict, expected: tuple
    ):
        # When
        result: tuple = build_api_data.retrieve_parameters(input)

        # Then
        assert dict(result) == expected

    def test_read_template(self, build_api_data: BuildApiData):
        # When
        result: str = build_api_data.read_template(file_name="fake.yaml")

        # Then
        expected: str = "fake: fake\nname: '{name}'\nimage: '{image}'\n"
        assert result == expected

    def test_replace_values(self, build_api_data: BuildApiData):
        # Given
        build_api_data.name = "test"
        build_api_data.parameters = {"image": "test"}
        fake_template: str = "name: '{name}'\nimage: '{image}'\n"

        # When
        result: str = build_api_data.replace_values(fake_template)

        # Then
        expected: str = "name: 'test'\nimage: 'test'\n"
        assert result == expected

    def test_generate_api_data(
        self, monkeypatch: MonkeyPatch, build_api_data: BuildApiData
    ):
        # Given
        mock_get_parameters: Mock = Mock()
        monkeypatch.setattr(BuildApiData, "get_parameters", mock_get_parameters)

        mock_read_template: Mock = Mock(return_value="")
        monkeypatch.setattr(BuildApiData, "read_template", mock_read_template)

        mock_replace_values: Mock = Mock(return_value="key1: val1\nkey2: val2")
        monkeypatch.setattr(BuildApiData, "replace_values", mock_replace_values)

        # When
        result: Dict = build_api_data.generate_api_data(tmpl_file="fake.yaml")

        # Then
        mock_get_parameters.assert_called_once()
        mock_read_template.assert_called_once()
        mock_replace_values.assert_called_once()
        expected: Dict = {"key1": "val1", "key2": "val2"}
        assert result == expected
