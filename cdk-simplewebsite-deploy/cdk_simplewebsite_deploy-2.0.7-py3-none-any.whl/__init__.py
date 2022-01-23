'''
[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
![Build](https://github.com/SnapPetal/cdk-simplewebsite-deploy/workflows/build/badge.svg)
![Release](https://github.com/SnapPetal/cdk-simplewebsite-deploy/workflows/release/badge.svg?branch=main)

# cdk-simplewebsite-deploy

This is an AWS CDK Construct to simplify deploying a single-page website using either S3 buckets or CloudFront distributions.

## Installation and Usage

### [CreateBasicSite](https://github.com/snappetal/cdk-simplewebsite-deploy/blob/main/API.md#cdk-cloudfront-deploy-createbasicsite)

#### Creates a simple website using S3 buckets with a domain hosted in Route 53.

##### Typescript

```console
npm install cdk-simplewebsite-deploy
```

```python
import * as cdk from '@aws-cdk/core';
import { CreateBasicSite } from 'cdk-simplewebsite-deploy';

export class PipelineStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new CreateBasicSite(stack, 'test-website', {
      websiteFolder: './src/build',
      indexDoc: 'index.html',
      hostedZone: 'example.com',
    });
  }
}
```

##### C#

```console
dotnet add package ThonBecker.CDK.SimpleWebsiteDeploy
```

```cs
using Amazon.CDK;
using ThonBecker.CDK.SimpleWebsiteDeploy;

namespace SimpleWebsiteDeploy
{
    public class PipelineStack : Stack
    {
        internal PipelineStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
        {
            new CreateBasicSite(scope, "test-website", new BasicSiteConfiguration()
            {
                WebsiteFolder = "./src/build",
                IndexDoc = "index.html",
                HostedZone = "example.com",
            });
        }
    }
}
```

##### Java

```xml
<dependency>
	<groupId>com.thonbecker.simplewebsitedeploy</groupId>
	<artifactId>cdk-simplewebsite-deploy</artifactId>
	<version>0.4.2</version>
</dependency>
```

```java
package com.myorg;

import software.amazon.awscdk.core.Construct;
import software.amazon.awscdk.core.Stack;
import software.amazon.awscdk.core.StackProps;
import com.thonbecker.simplewebsitedeploy.CreateBasicSite;

public class MyProjectStack extends Stack {
    public MyProjectStack(final Construct scope, final String id) {
        this(scope, id, null);
    }

    public MyProjectStack(final Construct scope, final String id, final StackProps props) {
        super(scope, id, props);

        CreateBasicSite.Builder.create(this, "test-website")
        		.websiteFolder("./src/build")
        		.indexDoc("index.html")
        		.hostedZone("example.com");
    }
}
```

##### Python

```console
pip install cdk-simplewebsite-deploy
```

```python
from aws_cdk import Stack
from cdk_simplewebsite_deploy import CreateBasicSite
from constructs import Construct

class MyProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        CreateBasicSite(self, 'test-website', website_folder='./src/build',
                        index_doc='index.html',
                        hosted_zone='example.com')
```

### [CreateCloudfrontSite](https://github.com/snappetal/cdk-simplewebsite-deploy/blob/main/API.md#cdk-cloudfront-deploy-createcloudfrontsite)

#### Creates a simple website using a CloudFront distribution with a domain hosted in Route 53.

##### Typescript

```console
npm install cdk-simplewebsite-deploy
```

```python
import * as cdk from '@aws-cdk/core';
import { CreateCloudfrontSite } from 'cdk-simplewebsite-deploy';

export class PipelineStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new CreateCloudfrontSite(stack, 'test-website', {
      websiteFolder: './src/dist',
      indexDoc: 'index.html',
      hostedZone: 'example.com',
      subDomain: 'www.example.com',
    });
  }
}
```

##### C#

```console
dotnet add package ThonBecker.CDK.SimpleWebsiteDeploy
```

```cs
using Amazon.CDK;
using ThonBecker.CDK.SimpleWebsiteDeploy;

namespace SimpleWebsiteDeploy
{
    public class PipelineStack : Stack
    {
        internal PipelineStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
        {
            new CreateCloudfrontSite(scope, "test-website", new CloudfrontSiteConfiguration()
            {
                WebsiteFolder = "./src/build",
                IndexDoc = "index.html",
                HostedZone = "example.com",
                SubDomain = "www.example.com",
            });
        }
    }
}
```

##### Java

```xml
<dependency>
	<groupId>com.thonbecker.simplewebsitedeploy</groupId>
	<artifactId>cdk-simplewebsite-deploy</artifactId>
	<version>0.4.2</version>
</dependency>
```

```java
package com.myorg;

import software.amazon.awscdk.core.Construct;
import software.amazon.awscdk.core.Stack;
import software.amazon.awscdk.core.StackProps;
import com.thonbecker.simplewebsitedeploy.CreateCloudfrontSite;

public class MyProjectStack extends Stack {
    public MyProjectStack(final Construct scope, final String id) {
        this(scope, id, null);
    }

    public MyProjectStack(final Construct scope, final String id, final StackProps props) {
        super(scope, id, props);

        CreateCloudfrontSite.Builder.create(this, "test-website")
        		.websiteFolder("./src/build")
        		.indexDoc("index.html")
        		.hostedZone("example.com")
        		.subDomain("www.example.com");
    }
}
```

##### Python

```console
pip install cdk-simplewebsite-deploy
```

```python
from aws_cdk import core
from cdk_simplewebsite_deploy import CreateCloudfrontSite


class MyProjectStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        CreateCloudfrontSite(self, 'test-website', website_folder='./src/build',
                             index_doc='index.html',
                             hosted_zone='example.com',
                             sub_domain='www.example.com')
```

## License

Distributed under the [Apache-2.0](./LICENSE) license.
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

import constructs


@jsii.data_type(
    jsii_type="cdk-simplewebsite-deploy.BasicSiteConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone": "hostedZone",
        "index_doc": "indexDoc",
        "website_folder": "websiteFolder",
        "error_doc": "errorDoc",
    },
)
class BasicSiteConfiguration:
    def __init__(
        self,
        *,
        hosted_zone: builtins.str,
        index_doc: builtins.str,
        website_folder: builtins.str,
        error_doc: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hosted_zone: Hosted Zone used to create the DNS record for the website.
        :param index_doc: The index document of the website.
        :param website_folder: Local path to the website folder you want to deploy on S3.
        :param error_doc: The error document of the website. Default: - No error document.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hosted_zone": hosted_zone,
            "index_doc": index_doc,
            "website_folder": website_folder,
        }
        if error_doc is not None:
            self._values["error_doc"] = error_doc

    @builtins.property
    def hosted_zone(self) -> builtins.str:
        '''Hosted Zone used to create the DNS record for the website.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def index_doc(self) -> builtins.str:
        '''The index document of the website.'''
        result = self._values.get("index_doc")
        assert result is not None, "Required property 'index_doc' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def website_folder(self) -> builtins.str:
        '''Local path to the website folder you want to deploy on S3.'''
        result = self._values.get("website_folder")
        assert result is not None, "Required property 'website_folder' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def error_doc(self) -> typing.Optional[builtins.str]:
        '''The error document of the website.

        :default: - No error document.
        '''
        result = self._values.get("error_doc")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BasicSiteConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-simplewebsite-deploy.CloudfrontSiteConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone": "hostedZone",
        "index_doc": "indexDoc",
        "website_folder": "websiteFolder",
        "domain": "domain",
        "error_doc": "errorDoc",
        "price_class": "priceClass",
        "sub_domain": "subDomain",
    },
)
class CloudfrontSiteConfiguration:
    def __init__(
        self,
        *,
        hosted_zone: builtins.str,
        index_doc: builtins.str,
        website_folder: builtins.str,
        domain: typing.Optional[builtins.str] = None,
        error_doc: typing.Optional[builtins.str] = None,
        price_class: typing.Optional["PriceClass"] = None,
        sub_domain: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hosted_zone: Hosted Zone used to create the DNS record for the website.
        :param index_doc: The index document of the website.
        :param website_folder: Local path to the website folder you want to deploy on S3.
        :param domain: Used to deploy a Cloudfront site with a single domain. e.g. sample.example.com If you include a value for both domain and subDomain, an error will be thrown. Default: - no value
        :param error_doc: The error document of the website. Default: - No error document.
        :param price_class: The price class determines how many edge locations CloudFront will use for your distribution. Default: PriceClass.PRICE_CLASS_100.
        :param sub_domain: The sub-domain name you want to deploy. e.g. www.example.com If you include a value for both domain and subDomain, an error will be thrown. Default: - no value
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hosted_zone": hosted_zone,
            "index_doc": index_doc,
            "website_folder": website_folder,
        }
        if domain is not None:
            self._values["domain"] = domain
        if error_doc is not None:
            self._values["error_doc"] = error_doc
        if price_class is not None:
            self._values["price_class"] = price_class
        if sub_domain is not None:
            self._values["sub_domain"] = sub_domain

    @builtins.property
    def hosted_zone(self) -> builtins.str:
        '''Hosted Zone used to create the DNS record for the website.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def index_doc(self) -> builtins.str:
        '''The index document of the website.'''
        result = self._values.get("index_doc")
        assert result is not None, "Required property 'index_doc' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def website_folder(self) -> builtins.str:
        '''Local path to the website folder you want to deploy on S3.'''
        result = self._values.get("website_folder")
        assert result is not None, "Required property 'website_folder' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Used to deploy a Cloudfront site with a single domain.

        e.g. sample.example.com
        If you include a value for both domain and subDomain,
        an error will be thrown.

        :default: - no value
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def error_doc(self) -> typing.Optional[builtins.str]:
        '''The error document of the website.

        :default: - No error document.
        '''
        result = self._values.get("error_doc")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def price_class(self) -> typing.Optional["PriceClass"]:
        '''The price class determines how many edge locations CloudFront will use for your distribution.

        :default: PriceClass.PRICE_CLASS_100.

        :see: https://aws.amazon.com/cloudfront/pricing/.
        '''
        result = self._values.get("price_class")
        return typing.cast(typing.Optional["PriceClass"], result)

    @builtins.property
    def sub_domain(self) -> typing.Optional[builtins.str]:
        '''The sub-domain name you want to deploy.

        e.g. www.example.com
        If you include a value for both domain and subDomain,
        an error will be thrown.

        :default: - no value
        '''
        result = self._values.get("sub_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontSiteConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CreateBasicSite(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-simplewebsite-deploy.CreateBasicSite",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        hosted_zone: builtins.str,
        index_doc: builtins.str,
        website_folder: builtins.str,
        error_doc: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: Hosted Zone used to create the DNS record for the website.
        :param index_doc: The index document of the website.
        :param website_folder: Local path to the website folder you want to deploy on S3.
        :param error_doc: The error document of the website. Default: - No error document.
        '''
        props = BasicSiteConfiguration(
            hosted_zone=hosted_zone,
            index_doc=index_doc,
            website_folder=website_folder,
            error_doc=error_doc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class CreateCloudfrontSite(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-simplewebsite-deploy.CreateCloudfrontSite",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        hosted_zone: builtins.str,
        index_doc: builtins.str,
        website_folder: builtins.str,
        domain: typing.Optional[builtins.str] = None,
        error_doc: typing.Optional[builtins.str] = None,
        price_class: typing.Optional["PriceClass"] = None,
        sub_domain: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: Hosted Zone used to create the DNS record for the website.
        :param index_doc: The index document of the website.
        :param website_folder: Local path to the website folder you want to deploy on S3.
        :param domain: Used to deploy a Cloudfront site with a single domain. e.g. sample.example.com If you include a value for both domain and subDomain, an error will be thrown. Default: - no value
        :param error_doc: The error document of the website. Default: - No error document.
        :param price_class: The price class determines how many edge locations CloudFront will use for your distribution. Default: PriceClass.PRICE_CLASS_100.
        :param sub_domain: The sub-domain name you want to deploy. e.g. www.example.com If you include a value for both domain and subDomain, an error will be thrown. Default: - no value
        '''
        props = CloudfrontSiteConfiguration(
            hosted_zone=hosted_zone,
            index_doc=index_doc,
            website_folder=website_folder,
            domain=domain,
            error_doc=error_doc,
            price_class=price_class,
            sub_domain=sub_domain,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.enum(jsii_type="cdk-simplewebsite-deploy.PriceClass")
class PriceClass(enum.Enum):
    PRICE_CLASS_100 = "PRICE_CLASS_100"
    '''USA, Canada, Europe, & Israel.'''
    PRICE_CLASS_200 = "PRICE_CLASS_200"
    '''PRICE_CLASS_100 + South Africa, Kenya, Middle East, Japan, Singapore, South Korea, Taiwan, Hong Kong, & Philippines.'''
    PRICE_CLASS_ALL = "PRICE_CLASS_ALL"
    '''All locations.'''


__all__ = [
    "BasicSiteConfiguration",
    "CloudfrontSiteConfiguration",
    "CreateBasicSite",
    "CreateCloudfrontSite",
    "PriceClass",
]

publication.publish()
