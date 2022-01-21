import boto3
from base64 import b64decode


class Kms:
    def __init__(self, region: str):

        # Create and store a kms client.
        self.kms = boto3.client('kms', region_name=region)

    def decrypt(self, cypherText: str) -> str:
        return self.kms.decrypt(
            CiphertextBlob=b64decode(cypherText)
        )['Plaintext']

    def encrypt(self, keyID: str, plaintext: str) -> str:
        return self.kms.encrypt(
            KeyId=keyID,
            Plaintext=b64decode(plaintext)
        )['CiphertextBlob']
