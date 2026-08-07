"""Unit tests for S3StorageService using pytest and unittest.mock."""

from datetime import datetime
from io import BytesIO
from unittest.mock import ANY, MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from src.s3_service import S3StorageService
from src.settings import Settings


@pytest.fixture
def disabled_settings() -> Settings:
    """Settings fixture with S3 storage disabled."""
    return Settings(use_s3_storage=False)


@pytest.fixture
def valid_s3_settings() -> Settings:
    """Settings fixture with valid S3 credentials and configuration."""
    return Settings(
        use_s3_storage=True,
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        aws_region="eu-central-1",
        aws_s3_bucket_name="test-bucket",
    )


def test_s3_service_disabled(disabled_settings: Settings) -> None:
    """Test initializing S3 service when disabled in settings."""
    service = S3StorageService(disabled_settings)
    assert not service.enabled
    assert service.bucket_name is None


@patch("boto3.Session")
def test_s3_service_missing_credentials(mock_session: MagicMock) -> None:
    """Test error raised when S3 is enabled but credentials are missing."""
    mock_session.return_value.get_credentials.return_value = None
    invalid_settings = Settings(
        use_s3_storage=True,
        aws_access_key_id="",
        aws_secret_access_key="",
    )
    with pytest.raises(ValueError, match="S3 storage is enabled but AWS credentials are missing"):
        S3StorageService(invalid_settings)


@patch("boto3.client")
def test_s3_service_initialization(mock_boto_client: MagicMock, valid_s3_settings: Settings) -> None:
    """Test successful S3 service initialization with mocked boto3 and explicit credentials."""
    service = S3StorageService(valid_s3_settings)

    assert service.enabled
    assert service.bucket_name == "test-bucket"
    mock_boto_client.assert_called_once_with(
        "s3",
        aws_access_key_id="mock_access_key",
        aws_secret_access_key="mock_secret_key",
        config=ANY,
    )


@patch("boto3.client")
@patch("boto3.Session")
def test_s3_service_initialization_default_credentials(
    mock_session: MagicMock, mock_boto_client: MagicMock
) -> None:
    """Test S3 service initialization using boto3 default credential chain when secret key is None."""
    mock_session.return_value.get_credentials.return_value = MagicMock()
    s3_settings = Settings(
        use_s3_storage=True,
        aws_access_key_id="mock_access_key",
        aws_secret_access_key=None,
        aws_region="eu-central-1",
        aws_s3_bucket_name="test-bucket",
    )
    service = S3StorageService(s3_settings)

    assert service.enabled
    assert service.bucket_name == "test-bucket"
    mock_boto_client.assert_called_once_with("s3", config=ANY)


@patch("boto3.client")
def test_upload_file_success(mock_boto_client: MagicMock, valid_s3_settings: Settings) -> None:
    """Test uploading a file to S3."""
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    service = S3StorageService(valid_s3_settings)
    result = service.upload_file(b"content", "test.txt", "text/plain")

    assert result == "test.txt"
    mock_s3.put_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="test.txt",
        Body=b"content",
        ContentType="text/plain",
    )


@patch("boto3.client")
def test_list_files_success(mock_boto_client: MagicMock, valid_s3_settings: Settings) -> None:
    """Test listing files from S3 with metadata."""
    mock_s3 = MagicMock()
    mock_s3.list_objects_v2.return_value = {
        "Contents": [
            {
                "Key": "doc1.pdf",
                "Size": 1024,
                "LastModified": datetime(2026, 8, 4, 18, 0, 0),
            }
        ]
    }
    mock_boto_client.return_value = mock_s3

    service = S3StorageService(valid_s3_settings)
    files = service.list_files()

    assert len(files) == 1
    assert files[0]["filename"] == "doc1.pdf"
    assert files[0]["size"] == 1024
    assert files[0]["last_modified"] == "2026-08-04T18:00:00"


@patch("boto3.client")
def test_get_file_stream_success(mock_boto_client: MagicMock, valid_s3_settings: Settings) -> None:
    """Test retrieving a file stream from S3."""
    mock_s3 = MagicMock()
    mock_body = MagicMock()
    mock_body.read.return_value = b"sample pdf content"
    mock_s3.get_object.return_value = {"Body": mock_body}
    mock_boto_client.return_value = mock_s3

    service = S3StorageService(valid_s3_settings)
    stream = service.get_file_stream("sample.pdf")

    assert isinstance(stream, BytesIO)
    assert stream.getvalue() == b"sample pdf content"


@patch("boto3.client")
def test_get_file_stream_not_found(mock_boto_client: MagicMock, valid_s3_settings: Settings) -> None:
    """Test FileNotFoundError is raised when file does not exist in S3."""
    mock_s3 = MagicMock()
    error_response = {"Error": {"Code": "NoSuchKey", "Message": "The specified key does not exist."}}
    mock_s3.get_object.side_effect = ClientError(error_response, "GetObject")
    mock_boto_client.return_value = mock_s3

    service = S3StorageService(valid_s3_settings)
    with pytest.raises(FileNotFoundError, match="File 'missing.txt' not found in S3 bucket"):
        service.get_file_stream("missing.txt")


@patch("boto3.client")
def test_delete_file_success(mock_boto_client: MagicMock, valid_s3_settings: Settings) -> None:
    """Test deleting a file from S3."""
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    service = S3StorageService(valid_s3_settings)
    success = service.delete_file("test.txt")

    assert success is True
    mock_s3.delete_object.assert_called_once_with(Bucket="test-bucket", Key="test.txt")


@patch("boto3.client")
def test_check_bucket_access_success(mock_boto_client: MagicMock, valid_s3_settings: Settings) -> None:
    """Test bucket access check returning True when bucket exists."""
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    service = S3StorageService(valid_s3_settings)
    assert service.check_bucket_access() is True