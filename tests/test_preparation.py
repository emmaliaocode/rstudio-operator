from pathlib import Path
from typing import Dict
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from src.rstudio import PrepareApiData


class TestPrepareApiData:
    """Test cases for the PrepareApiData class."""

    @pytest.fixture
    def prepare_api_data(self, resources_path: Path):
        """Fixture to provide a PrepareApiData instance for the tests"""

        inst: PrepareApiData = PrepareApiData(name="test")
        inst._tmpl_path = resources_path

        return inst

    def test_read_template(self, prepare_api_data: PrepareApiData):
        # When
        result: str = prepare_api_data.read_template(file_name="fake.yaml")

        # Then
        assert result == "fake: fake\nname: '{name}'"

    def test_generate_api_data(
        self, monkeypatch: MonkeyPatch, prepare_api_data: PrepareApiData
    ):
        # Given
        fake_tmpl: str = "fake: fake\nname: '{name}'"
        mock_read_template: Mock = Mock(return_value=fake_tmpl)
        monkeypatch.setattr(PrepareApiData, "read_template", mock_read_template)

        # When
        result: Dict = prepare_api_data.generate_api_data(tmpl_file_name="fake.yaml")

        # Then
        mock_read_template.assert_called_once()
        assert result == {"fake": "fake", "name": "test"}
