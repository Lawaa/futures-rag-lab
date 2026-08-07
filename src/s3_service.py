"""AWS S3 storage service for document management.

This module provides a dedicated service for uploading, listing, retrieving,
and deleting documents from an AWS S3 bucket. It integrates with the existing
RAG pipeline by providing in-memory BytesIO streams that LangChain document
loaders can parse without writing to local disk.
"""

from __future__ import annotations

import logging
from datetime import datetime
from io import BytesIO
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from botocore.config import Config

from .logging_config import get_logger
from .settings import Settings

logger = get_logger(__name__)


class S3StorageService:
    """Service for managing documents in AWS S3.

    This service handles all S3 operations including file uploads, listing,
    retrieval as in-memory streams, and deletion. It includes comprehensive
    error handling for AWS-specific issues and provides clean integration
    with the RAG document loading pipeline.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the S3 service with AWS credentials and configuration.

        Args:
            settings: Application settings containing AWS credentials and bucket name.

        Raises:
            ValueError: If S3 storage is enabled but credentials are missing.
        """
        if not settings.use_s3_storage:
            logger.info("S3 storage is disabled in settings.")
            self._enabled = False
            self._s3_client = None
            self._bucket_name = None
            return

        self._enabled = True
        self._bucket_name = settings.aws_s3_bucket_name

        # Configure S3 client with retry settings and region
        config = Config(
            region_name=settings.aws_region,
            retries={"max_attempts": 3, "mode": "adaptive"},
        )

        client_kwargs: dict[str, Any] = {"config": config}
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        else:
            # Fall back to boto3's default credential provider chain (~/.aws/credentials, env, etc.)
            session = boto3.Session(region_name=settings.aws_region)
            if not session.get_credentials():
                raise ValueError(
                    "S3 storage is enabled but AWS credentials are missing. "
                    "Please set AWS credentials in ~/.aws/credentials or environment variables."
                )

        try:
            self._s3_client = boto3.client("s3", **client_kwargs)
            logger.info(
                "S3 service initialized for bucket '%s' in region '%s'.",
                self._bucket_name,
                settings.aws_region,
            )
        except Exception as e:
            logger.error("Failed to initialize S3 client: %s", e)
            raise

    @property
    def enabled(self) -> bool:
        """Whether S3 storage is currently enabled."""
        return self._enabled

    @property
    def bucket_name(self) -> str | None:
        """The S3 bucket name."""
        return self._bucket_name

    def upload_file(
        self, file_bytes: bytes, filename: str, content_type: str
    ) -> str:
        """Upload a file to S3 and return the object key.

        Args:
            file_bytes: The file content as bytes.
            filename: The name to give the file in S3 (object key).
            content_type: The MIME type of the file (e.g., "application/pdf").

        Returns:
            The S3 object key (filename) of the uploaded file.

        Raises:
            RuntimeError: If S3 storage is not enabled.
            ClientError: If the upload fails due to AWS issues.
            BotoCoreError: If there's a boto3-specific error.
        """
        if not self._enabled or not self._s3_client:
            raise RuntimeError("S3 storage is not enabled or not initialized.")

        try:
            self._s3_client.put_object(
                Bucket=self._bucket_name,
                Key=filename,
                Body=file_bytes,
                ContentType=content_type,
            )
            logger.info("Successfully uploaded file '%s' to S3 bucket '%s'.", filename, self._bucket_name)
            return filename
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                "Failed to upload file '%s' to S3. Error code: %s, Message: %s",
                filename,
                error_code,
                str(e),
            )
            raise
        except BotoCoreError as e:
            logger.error("Boto3 error during upload of '%s': %s", filename, e)
            raise
        except Exception as e:
            logger.error("Unexpected error during upload of '%s': %s", filename, e)
            raise

    def list_files(self) -> list[dict[str, Any]]:
        """List all objects in the S3 bucket with metadata.

        Returns:
            A list of dictionaries containing file metadata:
            - filename: The object key
            - size: File size in bytes
            - last_modified: ISO-formatted timestamp of last modification

        Raises:
            RuntimeError: If S3 storage is not enabled.
            ClientError: If listing fails due to AWS issues.
            NoCredentialsError: If AWS credentials are invalid.
        """
        if not self._enabled or not self._s3_client:
            raise RuntimeError("S3 storage is not enabled or not initialized.")

        try:
            response = self._s3_client.list_objects_v2(Bucket=self._bucket_name)
            files: list[dict[str, Any]] = []

            if "Contents" in response:
                for obj in response["Contents"]:
                    files.append(
                        {
                            "filename": obj["Key"],
                            "size": obj["Size"],
                            "last_modified": obj["LastModified"].isoformat(),
                        }
                    )

            logger.info("Listed %d files from S3 bucket '%s'.", len(files), self._bucket_name)
            return files

        except NoCredentialsError:
            logger.error("AWS credentials not found or invalid.")
            raise
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                "Failed to list files from S3. Error code: %s, Message: %s",
                error_code,
                str(e),
            )
            raise
        except Exception as e:
            logger.error("Unexpected error during file listing: %s", e)
            raise

    def get_file_stream(self, object_key: str) -> BytesIO:
        """Download a file from S3 into an in-memory BytesIO stream.

        This method is designed for integration with LangChain document loaders,
        allowing them to parse files without writing to local disk.

        Args:
            object_key: The S3 object key (filename) to retrieve.

        Returns:
            A BytesIO stream containing the file content.

        Raises:
            RuntimeError: If S3 storage is not enabled.
            ClientError: If the download fails due to AWS issues.
            FileNotFoundError: If the object does not exist in the bucket.
        """
        if not self._enabled or not self._s3_client:
            raise RuntimeError("S3 storage is not enabled or not initialized.")

        try:
            response = self._s3_client.get_object(Bucket=self._bucket_name, Key=object_key)
            file_bytes = response["Body"].read()
            stream = BytesIO(file_bytes)
            stream.seek(0)  # Reset stream position for reading
            logger.info("Successfully retrieved file '%s' from S3.", object_key)
            return stream

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchKey":
                logger.error("File '%s' not found in S3 bucket '%s'.", object_key, self._bucket_name)
                raise FileNotFoundError(f"File '{object_key}' not found in S3 bucket.") from e
            logger.error(
                "Failed to retrieve file '%s' from S3. Error code: %s, Message: %s",
                object_key,
                error_code,
                str(e),
            )
            raise
        except BotoCoreError as e:
            logger.error("Boto3 error during retrieval of '%s': %s", object_key, e)
            raise
        except Exception as e:
            logger.error("Unexpected error during retrieval of '%s': %s", object_key, e)
            raise

    def delete_file(self, object_key: str) -> bool:
        """Delete an object从 the S3 bucket.

        Args:
            object_key: The S3 object key (filename) to delete.

        Returns:
            True if deletion was successful.

        Raises:
            RuntimeError: If S3 storage is not enabled.
            ClientError: If deletion fails due to AWS issues.
        """
        if not self._enabled or not self._s3_client:
            raise RuntimeError("S3 storage is not enabled or not initialized.")

        try:
            self._s3_client.delete_object(Bucket=self._bucket_name, Key=object_key)
            logger.info("Successfully deleted file '%s' from S3 bucket '%s'.", object_key, self._bucket_name)
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                "Failed to delete file '%s' from S3. Error code: %s, Message: %s",
                object_key,
                error_code,
                str(e),
            )
            raise
        except BotoCoreError as e:
            logger.error("Boto3 error during deletion of '%s': %s", object_key, e)
            raise
        except Exception as e:
            logger.error("Unexpected error during deletion of '%s': %s", object_key, e)
            raise

    def check_bucket_access(self) -> bool:
        """Verify that the configured bucket exists and is accessible.

        Returns:
            True if the bucket is accessible, False otherwise.

        Raises:
            RuntimeError: If S3 storage is not enabled.
        """
        if not self._enabled or not self._s3_client:
            raise RuntimeError("S3 storage is not enabled or not initialized.")

        try:
            self._s3_client.head_bucket(Bucket=self._bucket_name)
            logger.info("Bucket '%s' is accessible.", self._bucket_name)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "404":
                logger.error("Bucket '%s' does not exist.", self._bucket_name)
            elif error_code == "403":
                logger.error("Access denied to bucket '%s'.", self._bucket_name)
            else:
                logger.error(
                    "Cannot access bucket '%s'. Error code: %s, Message: %s",
                    self._bucket_name,
                    error_code,
                    str(e),
                )
            return False
        except Exception as e:
            logger.error("Unexpected error checking bucket access: %s", e)
            return False
