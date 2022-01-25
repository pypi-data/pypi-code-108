# parameter_types.py
from typing import Generic, KeysView, TypeVar

T = TypeVar('T')


class StringParameter:
    def __init__(self, value: str):
        self.value = value


class BooleanParameter:
    def __init__(self, value: bool):
        self.value = value


class ObjectParameter:
    def __init__(self, value: dict):
        self.value = value


class ListParameter(Generic[T]):
    def __init__(self, value: 'list[T]'):
        self.value = value


class KeyVaultSecretObject:
    def __init__(self, secret_name: str, secret_value: str):
        self.secretName = secret_name
        self.secretValue = secret_value


class KeyVaultSecretsObject:
    def __init__(self, secrets: 'list[KeyVaultSecretObject]'):
        self.secrets = secrets


class KeyVaultSecretsParameter:
    def __init__(self, value: dict):
        keyvault_secrets_list: 'list[KeyVaultSecretsObject]' = []
        for name, secret in value:
            keyvault_secret_object = KeyVaultSecretObject(name, secret)
            keyvault_secrets_list.append(keyvault_secret_object)

        self.value = KeyVaultSecretsObject(keyvault_secrets_list)
