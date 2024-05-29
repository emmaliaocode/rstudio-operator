from pathlib import Path
from typing import Dict
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from src.builder import BuildApiData


class TestBuildApiData:
    """Test cases for the PrepareApiData class."""

    @pytest.fixture
    def build_api_data(self, resources_path: Path):
        """Fixture to provide a PrepareApiData instance for the tests"""

        inst: BuildApiData = BuildApiData(name="", spec={})
        inst._tmpl_dir = resources_path

        return inst

    def test_render_template(self, build_api_data: BuildApiData):
        # Given
        build_api_data.name = "test"
        build_api_data.spec = {"image": "test", "isRoot": True}

        # When
        result: str = build_api_data.render_template("fake.yaml.j2")

        # Then
        expected: str = "name: test\nimage: test\nisRoot: true"
        assert result == expected

    def test_generate_api_data(
        self, monkeypatch: MonkeyPatch, build_api_data: BuildApiData
    ):
        # Given
        mock_render_template: Mock = Mock(return_value="key1: val1\nkey2: val2")
        monkeypatch.setattr(BuildApiData, "render_template", mock_render_template)

        # When
        result: Dict = build_api_data.generate_api_data(tmpl="fake.yaml.j2")

        # Then
        mock_render_template.assert_called_once()
        expected: Dict = {"key1": "val1", "key2": "val2"}
        assert result == expected
