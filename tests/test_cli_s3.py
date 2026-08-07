"""Unit tests for AWS S3 credential configuration and persistence in CLI."""

import configparser
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.cli import (
    _persist_aws_credentials_to_file,
    _persist_s3_credentials_to_env,
    _resolve_s3_credentials,
)
from src.settings import Settings


def test_persist_aws_credentials_to_file(tmp_path: Path) -> None:
    """Test saving AWS secret credentials to ~/.aws/credentials formatted file."""
    cred_file = tmp_path / ".aws" / "credentials"
    _persist_aws_credentials_to_file("AKIA_TEST_KEY", "SECRET_TEST_KEY", credentials_path=cred_file)

    assert cred_file.exists()
    config = configparser.ConfigParser()
    config.read(cred_file, encoding="utf-8")

    assert "default" in config.sections()
    assert config.get("default", "aws_access_key_id") == "AKIA_TEST_KEY"
    assert config.get("default", "aws_secret_access_key") == "SECRET_TEST_KEY"


def test_persist_aws_credentials_to_file_update_existing(tmp_path: Path) -> None:
    """Test updating an existing ~/.aws/credentials file preserving existing sections."""
    cred_file = tmp_path / ".aws" / "credentials"
    cred_file.parent.mkdir(parents=True, exist_ok=True)
    cred_file.write_text("[other]\nfoo = bar\n", encoding="utf-8")

    _persist_aws_credentials_to_file("AKIA_NEW", "SECRET_NEW", credentials_path=cred_file)

    config = configparser.ConfigParser()
    config.read(cred_file, encoding="utf-8")

    assert "default" in config.sections()
    assert config.get("default", "aws_access_key_id") == "AKIA_NEW"
    assert config.get("default", "aws_secret_access_key") == "SECRET_NEW"
    assert "other" in config.sections()
    assert config.get("other", "foo") == "bar"


def test_persist_s3_credentials_to_env_never_stores_secret(tmp_path: Path) -> None:
    """Test that _persist_s3_credentials_to_env never writes RAG_AWS_SECRET_ACCESS_KEY to .env."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "RAG_LANGUAGE=en\nRAG_AWS_SECRET_ACCESS_KEY=old_secret\n", encoding="utf-8"
    )

    settings = Settings(
        use_s3_storage=True,
        aws_access_key_id="AKIA_ENV_KEY",
        aws_secret_access_key="SECRET_IN_MEMORY",
        aws_region="us-west-2",
        aws_s3_bucket_name="my-bucket",
    )

    _persist_s3_credentials_to_env(settings, env_path=env_file)

    content = env_file.read_text(encoding="utf-8")
    assert "RAG_USE_S3_STORAGE=true" in content
    assert "RAG_AWS_ACCESS_KEY_ID=AKIA_ENV_KEY" in content
    assert "RAG_AWS_REGION=us-west-2" in content
    assert "RAG_AWS_S3_BUCKET_NAME=my-bucket" in content
    assert "RAG_AWS_SECRET_ACCESS_KEY" not in content


@patch("src.cli._persist_aws_credentials_to_file")
@patch("src.cli._persist_s3_credentials_to_env")
@patch("src.cli.S3StorageService")
@patch("builtins.input")
def test_resolve_s3_credentials_success(
    mock_input: MagicMock,
    mock_s3_class: MagicMock,
    mock_persist_env: MagicMock,
    mock_persist_file: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test interactive S3 resolution flow when user enables S3 and enters credentials."""
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)

    # Prompts: 1. enable ("y"), 2. access key, 3. secret key, 4. region, 5. bucket name
    mock_input.side_effect = ["y", "AKIA_INPUT", "SECRET_INPUT", "eu-central-1", "test-bucket"]
    mock_s3_instance = MagicMock()
    mock_s3_instance.check_bucket_access.return_value = True
    mock_s3_class.return_value = mock_s3_instance

    initial_settings = Settings(
        use_s3_storage=False, aws_access_key_id=None, aws_secret_access_key=None
    )
    result = _resolve_s3_credentials(initial_settings)

    assert result.use_s3_storage is True
    assert result.aws_access_key_id == "AKIA_INPUT"
    assert result.aws_secret_access_key == "SECRET_INPUT"

    mock_persist_file.assert_called_once_with("AKIA_INPUT", "SECRET_INPUT")
    mock_persist_env.assert_called_once()
