'''
[![NPM version](https://badge.fury.io/js/cdk-prowler.svg)](https://badge.fury.io/js/cdk-prowler)
[![PyPI version](https://badge.fury.io/py/cdk-prowler.svg)](https://badge.fury.io/py/cdk-prowler)
[![.NET version](https://img.shields.io/nuget/v/com.github.mmuller88.awsCdkBuildBadge.svg?style=flat-square)](https://www.nuget.org/packages/com.github.mmuller88.cdkProwler/)
![Release](https://github.com/mmuller88/cdk-prowler/workflows/Release/badge.svg)

Author = [https://martinmueller.dev](https://martinmueller.dev)

# cdk-prowler

An AWS CDK custom construct for deploying Prowler to you AWS Account. The following description about Prowler is taken from https://github.com/toniblyx/prowler:

Prowler is a security tool to perform AWS security best practices assessments, audits, incident response, continuous monitoring, hardening and forensics readiness. It contains all CIS controls listed here https://d0.awsstatic.com/whitepapers/compliance/AWS_CIS_Foundations_Benchmark.pdf and more than 100 additional checks that help on GDPR, HIPAA …

It generates security html results which are stored in an s3 bucket:

![html results](https://raw.githubusercontent.com/mmuller88/cdk-prowler/main/misc/html-out.png)

And in your Codebuild Report group:

![Report group](https://raw.githubusercontent.com/mmuller88/cdk-prowler/main/misc/report-group-out.png)

# AWS AMI

If you just want to make the Prowler security checks in your account try my [Prowler AWS Marketplace AMI](https://aws.amazon.com/marketplace/pp/prodview-jlwcdlc3weta6). With just $1 Prowler will do over 180 security checks across a huge amount of AWS services in all your regions. Don't forget the terminate the Ec2 instance when the Prowler stack got created for not paying more than that $1 :).

With buying the AMI you support my on my passion for creating open source products like this cdk-prowler construct. Furthermore you enable me to work on future features like mentioned in the **Planned Features** section. Thank you so much :) !

# Example

```python
import { ProwlerAudit } from 'cdk-prowler';
...
    const app = new App();

    const stack = new Stack(app, 'ProwlerAudit-stack');

    new ProwlerAudit(stack, 'ProwlerAudit');
```

# Architect diagram

![diagram](https://raw.githubusercontent.com/mmuller88/cdk-prowler/main/misc/cdk-prowler.png)

# cdk-prowler Properties

cdk-prowler supports some properties to tweak your stack. Like for running a Cloudwatch schedule to regualary run the Prowler scan with a defined cron expression.

# API Reference <a name="API Reference"></a>

## Constructs <a name="Constructs"></a>

### ProwlerAudit <a name="cdk-prowler.ProwlerAudit"></a>

Creates a CodeBuild project to audit an AWS account with Prowler and stores the html report in a S3 bucket.

This will run onece at the beginning and on a schedule afterwards. Partial contribution from https://github.com/stevecjones

#### Initializers <a name="cdk-prowler.ProwlerAudit.Initializer"></a>

```python
import { ProwlerAudit } from 'cdk-prowler'

new ProwlerAudit(parent: Stack, id: string, props?: ProwlerAuditProps)
```

##### `parent`<sup>Required</sup> <a name="cdk-prowler.ProwlerAudit.parameter.parent"></a>

* *Type:* [`@aws-cdk/core.Stack`](#@aws-cdk/core.Stack)

---


##### `id`<sup>Required</sup> <a name="cdk-prowler.ProwlerAudit.parameter.id"></a>

* *Type:* `string`

---


##### `props`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAudit.parameter.props"></a>

* *Type:* [`cdk-prowler.ProwlerAuditProps`](#cdk-prowler.ProwlerAuditProps)

---


#### Properties <a name="Properties"></a>

##### `codebuildProject`<sup>Required</sup> <a name="cdk-prowler.ProwlerAudit.property.codebuildProject"></a>

```python
public readonly codebuildProject: Project;
```

* *Type:* [`@aws-cdk/aws-codebuild.Project`](#@aws-cdk/aws-codebuild.Project)

---


##### `enableScheduler`<sup>Required</sup> <a name="cdk-prowler.ProwlerAudit.property.enableScheduler"></a>

```python
public readonly enableScheduler: boolean;
```

* *Type:* `boolean`

---


##### `logsRetentionInDays`<sup>Required</sup> <a name="cdk-prowler.ProwlerAudit.property.logsRetentionInDays"></a>

```python
public readonly logsRetentionInDays: RetentionDays;
```

* *Type:* [`@aws-cdk/aws-logs.RetentionDays`](#@aws-cdk/aws-logs.RetentionDays)

---


##### `prowlerOptions`<sup>Required</sup> <a name="cdk-prowler.ProwlerAudit.property.prowlerOptions"></a>

```python
public readonly prowlerOptions: string;
```

* *Type:* `string`

---


##### `prowlerScheduler`<sup>Required</sup> <a name="cdk-prowler.ProwlerAudit.property.prowlerScheduler"></a>

```python
public readonly prowlerScheduler: string;
```

* *Type:* `string`

---


##### `prowlerVersion`<sup>Required</sup> <a name="cdk-prowler.ProwlerAudit.property.prowlerVersion"></a>

```python
public readonly prowlerVersion: string;
```

* *Type:* `string`

---


##### `serviceName`<sup>Required</sup> <a name="cdk-prowler.ProwlerAudit.property.serviceName"></a>

```python
public readonly serviceName: string;
```

* *Type:* `string`

---


## Structs <a name="Structs"></a>

### ProwlerAuditProps <a name="cdk-prowler.ProwlerAuditProps"></a>

#### Initializer <a name="[object Object].Initializer"></a>

```python
import { ProwlerAuditProps } from 'cdk-prowler'

const prowlerAuditProps: ProwlerAuditProps = { ... }
```

##### `additionalS3CopyArgs`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAuditProps.property.additionalS3CopyArgs"></a>

```python
public readonly additionalS3CopyArgs: string;
```

* *Type:* `string`

An optional parameter to add to the S3 bucket copy command.

---


##### `allowlist`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAuditProps.property.allowlist"></a>

```python
public readonly allowlist: Asset;
```

* *Type:* [`@aws-cdk/aws-s3-assets.Asset`](#@aws-cdk/aws-s3-assets.Asset)
* *Default:* undefined

An Prowler-specific Allowlist file.

If a value is provided then this is passed to Prowler on runs using the '-w' flag.
If no value is provided, the -w parameter is not used. If you provide an asset that is zipped, it must contain
an 'allowlist.txt' file which will be passed to Prowler.

---


##### `enableScheduler`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAuditProps.property.enableScheduler"></a>

```python
public readonly enableScheduler: boolean;
```

* *Type:* `boolean`
* *Default:* false

enables the scheduler for running prowler periodically.

Together with prowlerScheduler.

---


##### `logsRetentionInDays`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAuditProps.property.logsRetentionInDays"></a>

```python
public readonly logsRetentionInDays: RetentionDays;
```

* *Type:* [`@aws-cdk/aws-logs.RetentionDays`](#@aws-cdk/aws-logs.RetentionDays)
* *Default:* : 3

Specifies the number of days you want to retain CodeBuild run log events in the specified log group.

Junit reports are kept for 30 days, HTML reports in S3 are not deleted

---


##### `prowlerOptions`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAuditProps.property.prowlerOptions"></a>

```python
public readonly prowlerOptions: string;
```

* *Type:* `string`
* *Default:* '-M text,junit-xml,html,csv,json'

Options to pass to Prowler command, make sure at least -M junit-xml is used for CodeBuild reports.

Use -r for the region to send API queries, -f to filter only one region, -M output formats, -c for comma separated checks, for all checks do not use -c or -g, for more options see -h. For a complete assessment use  "-M text,junit-xml,html,csv,json", for SecurityHub integration use "-r region -f region -M text,junit-xml,html,csv,json,json-asff -S -q"

---


##### `prowlerScheduler`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAuditProps.property.prowlerScheduler"></a>

```python
public readonly prowlerScheduler: string;
```

* *Type:* `string`
* *Default:* 'cron(0 22 * * ? *)'

The time when Prowler will run in cron format.

Default is daily at 22:00h or 10PM 'cron(0 22 * * ? *)', for every 5 hours also works 'rate(5 hours)'. More info here https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html.

---


##### `prowlerVersion`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAuditProps.property.prowlerVersion"></a>

```python
public readonly prowlerVersion: string;
```

* *Type:* `string`
* *Default:* 2.5.0

Specifies the concrete Prowler version.

---


##### `reportBucket`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAuditProps.property.reportBucket"></a>

```python
public readonly reportBucket: IBucket;
```

* *Type:* [`@aws-cdk/aws-s3.IBucket`](#@aws-cdk/aws-s3.IBucket)

An optional S3 bucket to store the Prowler reports.

---


##### `reportBucketPrefix`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAuditProps.property.reportBucketPrefix"></a>

```python
public readonly reportBucketPrefix: string;
```

* *Type:* `string`

An optional prefix for the report bucket objects.

---


##### `serviceName`<sup>Optional</sup> <a name="cdk-prowler.ProwlerAuditProps.property.serviceName"></a>

```python
public readonly serviceName: string;
```

* *Type:* `string`
* *Default:* : prowler

Specifies the service name used within component naming.

---


# Cross Account Buckets

By providing your own Bucket you can have the CodeBuild project drop the Prowler results in another account. Make sure that you have your Bucket policy setup to allow the account running the Prowler reports access to writing those record.
Additionally, you will probably want to provide an `additionalS3CopyArgs: '--acl bucket-owner-full-control'` to ensure that those object can be read by the account owner.

# Planned Features

* Supporting AWS SecurityHub https://github.com/toniblyx/prowler#security-hub-integration
* Triggering an event with SNS when prowler finishes the run
* AMI EC2 executable

# Architecture

![cfn](misc/cfn.jpg)

# Misc

```sh
yes | yarn destroy && yarn deploy --require-approval never
```

Rerun Prowler on deploy

```sh
yarn deploy --require-approval never -c reRunProwler=true
```

# Thanks To

* My friend and fellaw ex colleague Tony de la Fuente (https://github.com/toniblyx https://twitter.com/ToniBlyx) for developing such a cool security tool as [Prowler](https://github.com/toniblyx/prowler)
* As always to the amazing CDK / Projen Community. Join us on [Slack](https://cdk-dev.slack.com)!
* [Projen](https://github.com/projen/projen) project and the community around it
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
import aws_cdk.aws_codebuild
import aws_cdk.aws_logs
import aws_cdk.aws_s3
import aws_cdk.aws_s3_assets
import constructs


class ProwlerAudit(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-prowler.ProwlerAudit",
):
    '''Creates a CodeBuild project to audit an AWS account with Prowler and stores the html report in a S3 bucket.

    This will run onece at the beginning and on a schedule afterwards. Partial contribution from https://github.com/stevecjones
    '''

    def __init__(
        self,
        parent: aws_cdk.Stack,
        id: builtins.str,
        *,
        additional_s3_copy_args: typing.Optional[builtins.str] = None,
        allowlist: typing.Optional[aws_cdk.aws_s3_assets.Asset] = None,
        enable_scheduler: typing.Optional[builtins.bool] = None,
        logs_retention_in_days: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        prowler_options: typing.Optional[builtins.str] = None,
        prowler_scheduler: typing.Optional[builtins.str] = None,
        prowler_version: typing.Optional[builtins.str] = None,
        report_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        report_bucket_prefix: typing.Optional[builtins.str] = None,
        service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: -
        :param additional_s3_copy_args: An optional parameter to add to the S3 bucket copy command.
        :param allowlist: An Prowler-specific Allowlist file. If a value is provided then this is passed to Prowler on runs using the '-w' flag. If no value is provided, the -w parameter is not used. If you provide an asset that is zipped, it must contain an 'allowlist.txt' file which will be passed to Prowler. Default: undefined
        :param enable_scheduler: enables the scheduler for running prowler periodically. Together with prowlerScheduler. Default: false
        :param logs_retention_in_days: Specifies the number of days you want to retain CodeBuild run log events in the specified log group. Junit reports are kept for 30 days, HTML reports in S3 are not deleted Default: : 3
        :param prowler_options: Options to pass to Prowler command, make sure at least -M junit-xml is used for CodeBuild reports. Use -r for the region to send API queries, -f to filter only one region, -M output formats, -c for comma separated checks, for all checks do not use -c or -g, for more options see -h. For a complete assessment use "-M text,junit-xml,html,csv,json", for SecurityHub integration use "-r region -f region -M text,junit-xml,html,csv,json,json-asff -S -q" Default: '-M text,junit-xml,html,csv,json'
        :param prowler_scheduler: The time when Prowler will run in cron format. Default is daily at 22:00h or 10PM 'cron(0 22 * * ? *)', for every 5 hours also works 'rate(5 hours)'. More info here https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html. Default: 'cron(0 22 * * ? *)'
        :param prowler_version: Specifies the concrete Prowler version. Default: 2.6.0
        :param report_bucket: An optional S3 bucket to store the Prowler reports.
        :param report_bucket_prefix: An optional prefix for the report bucket objects.
        :param service_name: Specifies the service name used within component naming. Default: : prowler
        '''
        props = ProwlerAuditProps(
            additional_s3_copy_args=additional_s3_copy_args,
            allowlist=allowlist,
            enable_scheduler=enable_scheduler,
            logs_retention_in_days=logs_retention_in_days,
            prowler_options=prowler_options,
            prowler_scheduler=prowler_scheduler,
            prowler_version=prowler_version,
            report_bucket=report_bucket,
            report_bucket_prefix=report_bucket_prefix,
            service_name=service_name,
        )

        jsii.create(self.__class__, self, [parent, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="codebuildProject")
    def codebuild_project(self) -> aws_cdk.aws_codebuild.Project:
        return typing.cast(aws_cdk.aws_codebuild.Project, jsii.get(self, "codebuildProject"))

    @codebuild_project.setter
    def codebuild_project(self, value: aws_cdk.aws_codebuild.Project) -> None:
        jsii.set(self, "codebuildProject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableScheduler")
    def enable_scheduler(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "enableScheduler"))

    @enable_scheduler.setter
    def enable_scheduler(self, value: builtins.bool) -> None:
        jsii.set(self, "enableScheduler", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logsRetentionInDays")
    def logs_retention_in_days(self) -> aws_cdk.aws_logs.RetentionDays:
        return typing.cast(aws_cdk.aws_logs.RetentionDays, jsii.get(self, "logsRetentionInDays"))

    @logs_retention_in_days.setter
    def logs_retention_in_days(self, value: aws_cdk.aws_logs.RetentionDays) -> None:
        jsii.set(self, "logsRetentionInDays", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prowlerOptions")
    def prowler_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prowlerOptions"))

    @prowler_options.setter
    def prowler_options(self, value: builtins.str) -> None:
        jsii.set(self, "prowlerOptions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prowlerScheduler")
    def prowler_scheduler(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prowlerScheduler"))

    @prowler_scheduler.setter
    def prowler_scheduler(self, value: builtins.str) -> None:
        jsii.set(self, "prowlerScheduler", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prowlerVersion")
    def prowler_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prowlerVersion"))

    @prowler_version.setter
    def prowler_version(self, value: builtins.str) -> None:
        jsii.set(self, "prowlerVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @service_name.setter
    def service_name(self, value: builtins.str) -> None:
        jsii.set(self, "serviceName", value)


@jsii.data_type(
    jsii_type="cdk-prowler.ProwlerAuditProps",
    jsii_struct_bases=[],
    name_mapping={
        "additional_s3_copy_args": "additionalS3CopyArgs",
        "allowlist": "allowlist",
        "enable_scheduler": "enableScheduler",
        "logs_retention_in_days": "logsRetentionInDays",
        "prowler_options": "prowlerOptions",
        "prowler_scheduler": "prowlerScheduler",
        "prowler_version": "prowlerVersion",
        "report_bucket": "reportBucket",
        "report_bucket_prefix": "reportBucketPrefix",
        "service_name": "serviceName",
    },
)
class ProwlerAuditProps:
    def __init__(
        self,
        *,
        additional_s3_copy_args: typing.Optional[builtins.str] = None,
        allowlist: typing.Optional[aws_cdk.aws_s3_assets.Asset] = None,
        enable_scheduler: typing.Optional[builtins.bool] = None,
        logs_retention_in_days: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        prowler_options: typing.Optional[builtins.str] = None,
        prowler_scheduler: typing.Optional[builtins.str] = None,
        prowler_version: typing.Optional[builtins.str] = None,
        report_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        report_bucket_prefix: typing.Optional[builtins.str] = None,
        service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param additional_s3_copy_args: An optional parameter to add to the S3 bucket copy command.
        :param allowlist: An Prowler-specific Allowlist file. If a value is provided then this is passed to Prowler on runs using the '-w' flag. If no value is provided, the -w parameter is not used. If you provide an asset that is zipped, it must contain an 'allowlist.txt' file which will be passed to Prowler. Default: undefined
        :param enable_scheduler: enables the scheduler for running prowler periodically. Together with prowlerScheduler. Default: false
        :param logs_retention_in_days: Specifies the number of days you want to retain CodeBuild run log events in the specified log group. Junit reports are kept for 30 days, HTML reports in S3 are not deleted Default: : 3
        :param prowler_options: Options to pass to Prowler command, make sure at least -M junit-xml is used for CodeBuild reports. Use -r for the region to send API queries, -f to filter only one region, -M output formats, -c for comma separated checks, for all checks do not use -c or -g, for more options see -h. For a complete assessment use "-M text,junit-xml,html,csv,json", for SecurityHub integration use "-r region -f region -M text,junit-xml,html,csv,json,json-asff -S -q" Default: '-M text,junit-xml,html,csv,json'
        :param prowler_scheduler: The time when Prowler will run in cron format. Default is daily at 22:00h or 10PM 'cron(0 22 * * ? *)', for every 5 hours also works 'rate(5 hours)'. More info here https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html. Default: 'cron(0 22 * * ? *)'
        :param prowler_version: Specifies the concrete Prowler version. Default: 2.6.0
        :param report_bucket: An optional S3 bucket to store the Prowler reports.
        :param report_bucket_prefix: An optional prefix for the report bucket objects.
        :param service_name: Specifies the service name used within component naming. Default: : prowler
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if additional_s3_copy_args is not None:
            self._values["additional_s3_copy_args"] = additional_s3_copy_args
        if allowlist is not None:
            self._values["allowlist"] = allowlist
        if enable_scheduler is not None:
            self._values["enable_scheduler"] = enable_scheduler
        if logs_retention_in_days is not None:
            self._values["logs_retention_in_days"] = logs_retention_in_days
        if prowler_options is not None:
            self._values["prowler_options"] = prowler_options
        if prowler_scheduler is not None:
            self._values["prowler_scheduler"] = prowler_scheduler
        if prowler_version is not None:
            self._values["prowler_version"] = prowler_version
        if report_bucket is not None:
            self._values["report_bucket"] = report_bucket
        if report_bucket_prefix is not None:
            self._values["report_bucket_prefix"] = report_bucket_prefix
        if service_name is not None:
            self._values["service_name"] = service_name

    @builtins.property
    def additional_s3_copy_args(self) -> typing.Optional[builtins.str]:
        '''An optional parameter to add to the S3 bucket copy command.

        Example::

            --acl bucket-owner-full-control
        '''
        result = self._values.get("additional_s3_copy_args")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allowlist(self) -> typing.Optional[aws_cdk.aws_s3_assets.Asset]:
        '''An Prowler-specific Allowlist file.

        If a value is provided then this is passed to Prowler on runs using the '-w' flag.
        If no value is provided, the -w parameter is not used. If you provide an asset that is zipped, it must contain
        an 'allowlist.txt' file which will be passed to Prowler.

        :default: undefined

        Example::

            new Asset(this, 'AllowList', { path: path.join(__dirname, 'allowlist.txt') })
        '''
        result = self._values.get("allowlist")
        return typing.cast(typing.Optional[aws_cdk.aws_s3_assets.Asset], result)

    @builtins.property
    def enable_scheduler(self) -> typing.Optional[builtins.bool]:
        '''enables the scheduler for running prowler periodically.

        Together with prowlerScheduler.

        :default: false
        '''
        result = self._values.get("enable_scheduler")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def logs_retention_in_days(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''Specifies the number of days you want to retain CodeBuild run log events in the specified log group.

        Junit reports are kept for 30 days, HTML reports in S3 are not deleted

        :default: : 3
        '''
        result = self._values.get("logs_retention_in_days")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def prowler_options(self) -> typing.Optional[builtins.str]:
        '''Options to pass to Prowler command, make sure at least -M junit-xml is used for CodeBuild reports.

        Use -r for the region to send API queries, -f to filter only one region, -M output formats, -c for comma separated checks, for all checks do not use -c or -g, for more options see -h. For a complete assessment use  "-M text,junit-xml,html,csv,json", for SecurityHub integration use "-r region -f region -M text,junit-xml,html,csv,json,json-asff -S -q"

        :default: '-M text,junit-xml,html,csv,json'
        '''
        result = self._values.get("prowler_options")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prowler_scheduler(self) -> typing.Optional[builtins.str]:
        '''The time when Prowler will run in cron format.

        Default is daily at 22:00h or 10PM 'cron(0 22 * * ? *)', for every 5 hours also works 'rate(5 hours)'. More info here https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html.

        :default: 'cron(0 22 * * ? *)'
        '''
        result = self._values.get("prowler_scheduler")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prowler_version(self) -> typing.Optional[builtins.str]:
        '''Specifies the concrete Prowler version.

        :default: 2.6.0
        '''
        result = self._values.get("prowler_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def report_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''An optional S3 bucket to store the Prowler reports.'''
        result = self._values.get("report_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def report_bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''An optional prefix for the report bucket objects.'''
        result = self._values.get("report_bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        '''Specifies the service name used within component naming.

        :default: : prowler
        '''
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProwlerAuditProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProwlerAudit",
    "ProwlerAuditProps",
]

publication.publish()
