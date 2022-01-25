'''
[![NPM version](https://badge.fury.io/js/cdk-certbot-dns-route53.svg)](https://badge.fury.io/js/cdk-certbot-dns-route53)
[![PyPI version](https://badge.fury.io/py/cdk-certbot-dns-route53.svg)](https://badge.fury.io/py/cdk-certbot-dns-route53)
[![Release](https://github.com/neilkuan/cdk-certbot-dns-route53/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/neilkuan/cdk-certbot-dns-route53/actions/workflows/release.yml)

# cdk-certbot-dns-route53

**cdk-certbot-dns-route53** is a CDK construct library that allows you to create [Certbot](https://github.com/certbot/certbot) Lambda Function on AWS with CDK, and setting schedule cron job to renew certificate to store on S3 Bucket.

## Install

```bash
Use the npm dist tag to opt in CDKv1 or CDKv2:

// for CDKv2
npm install cdk-certbot-dns-route53
or
npm install cdk-certbot-dns-route53@latest

// for CDKv1
npm install cdk-certbot-dns-route53@cdkv1
```

💡💡💡 please click [here](https://github.com/neilkuan/cdk-certbot-dns-route53/tree/cdkv1#readme), if you are using aws-cdk v1.x.x version.💡💡💡

```python
import * as r53 from 'aws-cdk-lib/aws-route53';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cdk from 'aws-cdk-lib';
import { CertbotDnsRoute53Job } from 'cdk-certbot-dns-route53';

const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new cdk.App();

const stack = new cdk.Stack(app, 'lambda-certbot-dev', { env: devEnv });

new CertbotDnsRoute53Job(stack, 'Demo', {
  certbotOptions: {
    domainName: '*.example.com',
    email: 'user@example.com',
  },
  zone: r53.HostedZone.fromHostedZoneAttributes(stack, 'myZone', {｀
    zoneName: 'example.com',
    hostedZoneId:  'mockId',
  }),
  destinationBucket: s3.Bucket.fromBucketName(stack, 'myBucket', 'mybucket'),
});
```

### Example: Invoke Lambda Function log.

![](./images/lambda-logs.png)

### Example: Renew certificate to store on S3 Bucket

![](./images/s3-bucket.png)
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

import aws_cdk
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_route53
import aws_cdk.aws_s3
import constructs


class BashExecFunction(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-certbot-dns-route53.BashExecFunction",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        script: builtins.str,
        dockerfile: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param script: The path of the shell script to be executed.
        :param dockerfile: The path of your custom dockerfile.
        :param environment: Lambda environment variables.
        :param role: Custom lambda execution role. Default: - auto generated role.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: - Duration.seconds(60)
        '''
        props = BashExecFunctionProps(
            script=script,
            dockerfile=dockerfile,
            environment=environment,
            role=role,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.DockerImageFunction:
        return typing.cast(aws_cdk.aws_lambda.DockerImageFunction, jsii.get(self, "handler"))


@jsii.data_type(
    jsii_type="cdk-certbot-dns-route53.BashExecFunctionProps",
    jsii_struct_bases=[],
    name_mapping={
        "script": "script",
        "dockerfile": "dockerfile",
        "environment": "environment",
        "role": "role",
        "timeout": "timeout",
    },
)
class BashExecFunctionProps:
    def __init__(
        self,
        *,
        script: builtins.str,
        dockerfile: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param script: The path of the shell script to be executed.
        :param dockerfile: The path of your custom dockerfile.
        :param environment: Lambda environment variables.
        :param role: Custom lambda execution role. Default: - auto generated role.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: - Duration.seconds(60)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "script": script,
        }
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if environment is not None:
            self._values["environment"] = environment
        if role is not None:
            self._values["role"] = role
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def script(self) -> builtins.str:
        '''The path of the shell script to be executed.'''
        result = self._values.get("script")
        assert result is not None, "Required property 'script' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''The path of your custom dockerfile.'''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Lambda environment variables.'''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Custom lambda execution role.

        :default: - auto generated role.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        '''The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value based on the function's expected execution time.

        :default: - Duration.seconds(60)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BashExecFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertbotDnsRoute53Job(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-certbot-dns-route53.CertbotDnsRoute53Job",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        certbot_options: "CertbotOptions",
        destination_bucket: aws_cdk.aws_s3.IBucket,
        zone: aws_cdk.aws_route53.IHostedZone,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param certbot_options: certbot cmd options.
        :param destination_bucket: The S3 bucket to store certificate.
        :param zone: The HostZone on route53 to dns-01 challenge.
        :param schedule: run the Job with defined schedule. Default: - no shedule
        '''
        props = CertbotDnsRoute53JobProps(
            certbot_options=certbot_options,
            destination_bucket=destination_bucket,
            zone=zone,
            schedule=schedule,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-certbot-dns-route53.CertbotDnsRoute53JobProps",
    jsii_struct_bases=[],
    name_mapping={
        "certbot_options": "certbotOptions",
        "destination_bucket": "destinationBucket",
        "zone": "zone",
        "schedule": "schedule",
    },
)
class CertbotDnsRoute53JobProps:
    def __init__(
        self,
        *,
        certbot_options: "CertbotOptions",
        destination_bucket: aws_cdk.aws_s3.IBucket,
        zone: aws_cdk.aws_route53.IHostedZone,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
    ) -> None:
        '''
        :param certbot_options: certbot cmd options.
        :param destination_bucket: The S3 bucket to store certificate.
        :param zone: The HostZone on route53 to dns-01 challenge.
        :param schedule: run the Job with defined schedule. Default: - no shedule
        '''
        if isinstance(certbot_options, dict):
            certbot_options = CertbotOptions(**certbot_options)
        self._values: typing.Dict[str, typing.Any] = {
            "certbot_options": certbot_options,
            "destination_bucket": destination_bucket,
            "zone": zone,
        }
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def certbot_options(self) -> "CertbotOptions":
        '''certbot cmd options.'''
        result = self._values.get("certbot_options")
        assert result is not None, "Required property 'certbot_options' is missing"
        return typing.cast("CertbotOptions", result)

    @builtins.property
    def destination_bucket(self) -> aws_cdk.aws_s3.IBucket:
        '''The S3 bucket to store certificate.'''
        result = self._values.get("destination_bucket")
        assert result is not None, "Required property 'destination_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def zone(self) -> aws_cdk.aws_route53.IHostedZone:
        '''The HostZone on route53 to dns-01 challenge.'''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    @builtins.property
    def schedule(self) -> typing.Optional[aws_cdk.aws_events.Schedule]:
        '''run the Job with defined schedule.

        :default: - no shedule
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[aws_cdk.aws_events.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertbotDnsRoute53JobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-certbot-dns-route53.CertbotOptions",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "email": "email",
        "custom_prefix_directory": "customPrefixDirectory",
    },
)
class CertbotOptions:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        email: builtins.str,
        custom_prefix_directory: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param domain_name: the domain must host on route53 like example.com.
        :param email: Email address for important account notifications.
        :param custom_prefix_directory: Custom prefix directory on s3 bucket object path. Default: - ``s3://YOUR_BUCKET_NAME/2021-01-01/your.domain.name/``
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
            "email": email,
        }
        if custom_prefix_directory is not None:
            self._values["custom_prefix_directory"] = custom_prefix_directory

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''the domain must host on route53 like example.com.

        Example::

            - `*.example.com` or `a.example.com` .
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email(self) -> builtins.str:
        '''Email address for important account notifications.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_prefix_directory(self) -> typing.Optional[builtins.str]:
        '''Custom prefix directory on s3 bucket object path.

        :default: - ``s3://YOUR_BUCKET_NAME/2021-01-01/your.domain.name/``

        Example::

            - customPrefixDirectory: 'abc' -> `s3://YOUR_BUCKET_NAME/abc/your.domain.name/`
        '''
        result = self._values.get("custom_prefix_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertbotOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BashExecFunction",
    "BashExecFunctionProps",
    "CertbotDnsRoute53Job",
    "CertbotDnsRoute53JobProps",
    "CertbotOptions",
]

publication.publish()
