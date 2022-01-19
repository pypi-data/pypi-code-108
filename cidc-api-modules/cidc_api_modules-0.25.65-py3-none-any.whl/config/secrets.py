from os import environ
from google.cloud import storage


def get_secrets_manager(is_testing=False):
    """Get a secrets manager based on whether the app is running in test mode"""
    if is_testing:
        from unittest.mock import MagicMock

        # If we're testing, we shouldn't need access to secrets in GCS
        return MagicMock()
    else:
        secrets_bucket = environ.get("GOOGLE_SECRETS_BUCKET")
        return CloudStorageSecretManager(secrets_bucket)


class SecretNotFoundError(Exception):
    pass


class CloudStorageSecretManager:
    """
        Get and set secrets (e.g., API keys, db passwords) in Google Cloud Storage
        to leverage GCS's default at-rest encryption.
    """

    def __init__(self, bucket_name):
        """
            Initialize a CloudStorageSecretManager with a connection to a Cloud Storage bucket.
        """
        assert bucket_name, "a bucket name is required to manage secrets"

        self.bucket_name = bucket_name
        self.bucket = storage.Client().get_bucket(bucket_name)

    def get(self, secret_name):
        """
            Try to find a secret in Google Cloud Storage.
            Raises a SecretNotFound exception if the secret doesn't exist.
        """
        # Look for the secret in Cloud Storage
        secret_blob = self.bucket.get_blob(secret_name)

        if not secret_blob:
            raise SecretNotFoundError(
                f'no secret "{secret_name}" in bucket "{self.bucket_name}'
            )

        # Download the secret_blob (as bytes) and decode to a string
        secret = secret_blob.download_as_string().decode("utf-8")

        return secret

    def set(self, secret_name, secret):
        """
            Store secret in a Google Cloud Storage bucket.
        """
        blob = self.bucket.blob(secret_name)
        blob.upload_from_string(secret)
