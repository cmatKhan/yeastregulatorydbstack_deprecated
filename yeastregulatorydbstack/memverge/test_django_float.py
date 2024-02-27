from unittest.mock import mock_open, patch

import pytest

from .django_float import (  # Adjust the import according to your actual file structure
    env_args_str,
    load_env_vars_from_file,
)


def test_load_env_vars_from_file():
    mock_content = "API_KEY=secret\nDB_HOST=localhost"
    with patch("builtins.open", mock_open(read_data=mock_content)):
        env_vars = load_env_vars_from_file("dummy/path")
        assert env_vars == {"API_KEY": "secret", "DB_HOST": "localhost"}


@pytest.fixture
def mock_env_files(mocker):
    mock_content_django = "DEBUG=True\nSECRET_KEY=supersecret"
    mock_content_postgres = "DB_NAME=appdb\nDB_USER=admin"
    mocker.patch(
        "builtins.open",
        side_effect=[
            mock_open(read_data=mock_content_django).return_value,
            mock_open(read_data=mock_content_postgres).return_value,
        ],
    )


def test_env_args_str(mock_env_files):
    expected_result = "-e DEBUG=True \\\n-e SECRET_KEY=supersecret \\\n-e DB_NAME=appdb \\\n-e DB_USER=admin \\"
    assert env_args_str().strip() == expected_result
