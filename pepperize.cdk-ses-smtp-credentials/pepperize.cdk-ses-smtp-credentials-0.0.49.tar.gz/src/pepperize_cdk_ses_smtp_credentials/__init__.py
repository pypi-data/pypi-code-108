'''
[![GitHub](https://img.shields.io/github/license/pepperize/cdk-ses-smtp-credentials?style=flat-square)](https://github.com/pepperize/cdk-ses-smtp-credentials/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@pepperize/cdk-ses-smtp-credentials?style=flat-square)](https://www.npmjs.com/package/@pepperize/cdk-ses-smtp-credentials)
[![PyPI](https://img.shields.io/pypi/v/pepperize.cdk-ses-smtp-credentials?style=flat-square)](https://pypi.org/project/pepperize.cdk-ses-smtp-credentials/)
[![Nuget](https://img.shields.io/nuget/v/Pepperize.CDK.SesSmtpCredentials?style=flat-square)](https://www.nuget.org/packages/Pepperize.CDK.SesSmtpCredentials/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pepperize/cdk-ses-smtp-credentials/release/main?label=release&style=flat-square)](https://github.com/pepperize/cdk-ses-smtp-credentials/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/pepperize/cdk-ses-smtp-credentials?sort=semver&style=flat-square)](https://github.com/pepperize/cdk-ses-smtp-credentials/releases)

# AWS CDK Ses Smtp Credentials

This projects provides a CDK construct to create ses smtp credentials for a given user. It takes a username, creates an AccessKey and generates the smtp password.

## Install

### TypeScript

```shell
npm install @pepperize/cdk-ses-smtp-credentials
```

or

```shell
yarn add @pepperize/cdk-ses-smtp-credentials
```

### Python

```shell
pip install pepperize.cdk-ses-smtp-credentials
```

### C# / .Net

```
dotnet add package Pepperize.CDK.SesSmtpCredentials
```

## Example

```shell
npm install @pepperize/cdk-ses-smtp-credentials
```

See [API.md](https://github.com/pepperize/cdk-ses-smtp-credentials/blob/main/API.md).

```python
import { User } from "@aws-cdk/aws-iam";
import { SesSmtpCredentials } from "@pepperize/cdk-ses-smtp-credentials";

const username = "ses-user";
const user = new User(stack, "SesUser", {
  userName: username,
});
const smtpCredentials = new SesSmtpCredentials(this, "SmtpCredentials", {
  user: user,
});

// smtpCredentials.secret contains json value {username: "<the generated access key id>", password: "<the calculated ses smtp password>"}
```
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
import aws_cdk.core


@jsii.enum(jsii_type="@pepperize/cdk-ses-smtp-credentials.Credentials")
class Credentials(enum.Enum):
    USERNAME = "USERNAME"
    '''The key of the username stored in the secretsmanager key/value json text.'''
    PASSWORD = "PASSWORD"
    '''The key of the password stored in the secretsmanager key/value json.'''


class SesSmtpCredentials(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-ses-smtp-credentials.SesSmtpCredentials",
):
    '''This construct creates an access key for the given user and stores the generated SMTP credentials inside a secret.

    Example::

        const user = User.fromUserName("ses-user-example");
        const credentials = new SesSmtpCredentials(this, 'SmtpCredentials', {
            user: user,
        });
        // credentials.secret
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        user: aws_cdk.aws_iam.IUser,
        secret: typing.Optional[aws_cdk.aws_secretsmanager.ISecret] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param user: The user for which to create an AWS Access Key and to generate the smtp password.
        :param secret: Optional, an SecretsManager secret to write the AWS SES Smtp credentials to.
        '''
        props = SesSmtpCredentialsProps(user=user, secret=secret)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, jsii.get(self, "secret"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-ses-smtp-credentials.SesSmtpCredentialsProps",
    jsii_struct_bases=[],
    name_mapping={"user": "user", "secret": "secret"},
)
class SesSmtpCredentialsProps:
    def __init__(
        self,
        *,
        user: aws_cdk.aws_iam.IUser,
        secret: typing.Optional[aws_cdk.aws_secretsmanager.ISecret] = None,
    ) -> None:
        '''
        :param user: The user for which to create an AWS Access Key and to generate the smtp password.
        :param secret: Optional, an SecretsManager secret to write the AWS SES Smtp credentials to.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "user": user,
        }
        if secret is not None:
            self._values["secret"] = secret

    @builtins.property
    def user(self) -> aws_cdk.aws_iam.IUser:
        '''The user for which to create an AWS Access Key and to generate the smtp password.'''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(aws_cdk.aws_iam.IUser, result)

    @builtins.property
    def secret(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        '''Optional, an SecretsManager secret to write the AWS SES Smtp credentials to.'''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.ISecret], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesSmtpCredentialsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Credentials",
    "SesSmtpCredentials",
    "SesSmtpCredentialsProps",
]

publication.publish()
