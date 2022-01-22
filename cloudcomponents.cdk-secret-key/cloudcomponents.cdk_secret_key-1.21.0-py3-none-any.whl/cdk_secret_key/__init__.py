'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-secret-key

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-secret-key)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-secret-key/)

> Provide secret keys to lambdas

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-secret-key
```

Python:

```bash
pip install cloudcomponents.cdk-secret-key
```

## How to use

```python
import { SecretKey } from '@cloudcomponents/cdk-secret-key';

const secretKey = SecretKey.fromPlainText(process.env.SECRET_KEY as string);
const secretKeyString = secretKey.serialize(),
```

See [cloudcomponents/lambda-utils-nodejs](https://github.com/cloudcomponents/lambda-utils-nodejs) for the counterpart in lambda functions

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-secret-key/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-secret-key/LICENSE)
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_iam
import aws_cdk.aws_secretsmanager
import aws_cdk.aws_ssm


@jsii.enum(jsii_type="@cloudcomponents/cdk-secret-key.KeyType")
class KeyType(enum.Enum):
    SECRETS_MANAGER = "SECRETS_MANAGER"
    SSM_PARAMETER = "SSM_PARAMETER"
    PLAIN_TEXT = "PLAIN_TEXT"


class SecretKey(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cloudcomponents/cdk-secret-key.SecretKey",
):
    def __init__(self, secret_key_type: KeyType) -> None:
        '''
        :param secret_key_type: -
        '''
        jsii.create(self.__class__, self, [secret_key_type])

    @jsii.member(jsii_name="fromPlainText") # type: ignore[misc]
    @builtins.classmethod
    def from_plain_text(cls, value: builtins.str) -> "SecretKey":
        '''
        :param value: -
        '''
        return typing.cast("SecretKey", jsii.sinvoke(cls, "fromPlainText", [value]))

    @jsii.member(jsii_name="fromSecretsManager") # type: ignore[misc]
    @builtins.classmethod
    def from_secrets_manager(
        cls,
        secret_key_secret: aws_cdk.aws_secretsmanager.ISecret,
        field_name: typing.Optional[builtins.str] = None,
    ) -> "SecretKey":
        '''
        :param secret_key_secret: -
        :param field_name: -
        '''
        return typing.cast("SecretKey", jsii.sinvoke(cls, "fromSecretsManager", [secret_key_secret, field_name]))

    @jsii.member(jsii_name="fromSSMParameter") # type: ignore[misc]
    @builtins.classmethod
    def from_ssm_parameter(
        cls,
        secret_key_parameter: aws_cdk.aws_ssm.IParameter,
    ) -> "SecretKey":
        '''
        :param secret_key_parameter: -
        '''
        return typing.cast("SecretKey", jsii.sinvoke(cls, "fromSSMParameter", [secret_key_parameter]))

    @jsii.member(jsii_name="grantRead") # type: ignore[misc]
    @abc.abstractmethod
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        '''
        :param grantee: -
        '''
        ...

    @jsii.member(jsii_name="serialize") # type: ignore[misc]
    @abc.abstractmethod
    def serialize(self) -> builtins.str:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretKeyType")
    def secret_key_type(self) -> KeyType:
        return typing.cast(KeyType, jsii.get(self, "secretKeyType"))


class _SecretKeyProxy(SecretKey):
    @jsii.member(jsii_name="grantRead")
    def grant_read(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        '''
        :param grantee: -
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="serialize")
    def serialize(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "serialize", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, SecretKey).__jsii_proxy_class__ = lambda : _SecretKeyProxy


class SecretKeyStore(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cloudcomponents/cdk-secret-key.SecretKeyStore",
):
    def __init__(self, secret_key_type: KeyType) -> None:
        '''
        :param secret_key_type: -
        '''
        jsii.create(self.__class__, self, [secret_key_type])

    @jsii.member(jsii_name="fromSecretsManager") # type: ignore[misc]
    @builtins.classmethod
    def from_secrets_manager(
        cls,
        secret_key_secret: aws_cdk.aws_secretsmanager.ISecret,
    ) -> "SecretKeyStore":
        '''
        :param secret_key_secret: -
        '''
        return typing.cast("SecretKeyStore", jsii.sinvoke(cls, "fromSecretsManager", [secret_key_secret]))

    @jsii.member(jsii_name="fromSSMParameter") # type: ignore[misc]
    @builtins.classmethod
    def from_ssm_parameter(
        cls,
        secret_key_parameter: aws_cdk.aws_ssm.IParameter,
    ) -> "SecretKeyStore":
        '''
        :param secret_key_parameter: -
        '''
        return typing.cast("SecretKeyStore", jsii.sinvoke(cls, "fromSSMParameter", [secret_key_parameter]))

    @jsii.member(jsii_name="grantWrite") # type: ignore[misc]
    @abc.abstractmethod
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        '''
        :param grantee: -
        '''
        ...

    @jsii.member(jsii_name="serialize") # type: ignore[misc]
    @abc.abstractmethod
    def serialize(self) -> builtins.str:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretKeyType")
    def secret_key_type(self) -> KeyType:
        return typing.cast(KeyType, jsii.get(self, "secretKeyType"))


class _SecretKeyStoreProxy(SecretKeyStore):
    @jsii.member(jsii_name="grantWrite")
    def grant_write(self, grantee: aws_cdk.aws_iam.IGrantable) -> aws_cdk.aws_iam.Grant:
        '''
        :param grantee: -
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantWrite", [grantee]))

    @jsii.member(jsii_name="serialize")
    def serialize(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "serialize", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, SecretKeyStore).__jsii_proxy_class__ = lambda : _SecretKeyStoreProxy


__all__ = [
    "KeyType",
    "SecretKey",
    "SecretKeyStore",
]

publication.publish()
