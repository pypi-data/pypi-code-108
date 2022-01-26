'''
# AWS Service Catalog Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

[AWS Service Catalog](https://docs.aws.amazon.com/servicecatalog/latest/dg/what-is-service-catalog.html)
enables organizations to create and manage catalogs of products for their end users that are approved for use on AWS.

## Table Of Contents

* [Portfolio](#portfolio)

  * [Granting access to a portfolio](#granting-access-to-a-portfolio)
  * [Sharing a portfolio with another AWS account](#sharing-a-portfolio-with-another-aws-account)
* [Product](#product)

  * [Creating a product from a local asset](#creating-a-product-from-local-asset)
  * [Creating a product from a stack](#creating-a-product-from-a-stack)
  * [Adding a product to a portfolio](#adding-a-product-to-a-portfolio)
* [TagOptions](#tag-options)
* [Constraints](#constraints)

  * [Tag update constraint](#tag-update-constraint)
  * [Notify on stack events](#notify-on-stack-events)
  * [CloudFormation parameters constraint](#cloudformation-parameters-constraint)
  * [Set launch role](#set-launch-role)
  * [Deploy with StackSets](#deploy-with-stacksets)

The `@aws-cdk/aws-servicecatalog` package contains resources that enable users to automate governance and management of their AWS resources at scale.

```python
import aws_cdk.aws_servicecatalog_alpha as servicecatalog
```

## Portfolio

AWS Service Catalog portfolios allow admins to manage products that their end users have access to.
Using the CDK, a new portfolio can be created with the `Portfolio` construct:

```python
servicecatalog.Portfolio(self, "MyFirstPortfolio",
    display_name="MyFirstPortfolio",
    provider_name="MyTeam"
)
```

You can also specify properties such as `description` and `acceptLanguage`
to help better catalog and manage your portfolios.

```python
servicecatalog.Portfolio(self, "MyFirstPortfolio",
    display_name="MyFirstPortfolio",
    provider_name="MyTeam",
    description="Portfolio for a project",
    message_language=servicecatalog.MessageLanguage.EN
)
```

Read more at [Creating and Managing Portfolios](https://docs.aws.amazon.com/servicecatalog/latest/adminguide/catalogs_portfolios.html).

A portfolio that has been created outside the stack can be imported into your CDK app.
Portfolios can be imported by their ARN via the `Portfolio.fromPortfolioArn()` API:

```python
portfolio = servicecatalog.Portfolio.from_portfolio_arn(self, "MyImportedPortfolio", "arn:aws:catalog:region:account-id:portfolio/port-abcdefghi")
```

### Granting access to a portfolio

You can manage end user access to a portfolio by granting permissions to `IAM` entities like a user, group, or role.
Once resources are deployed end users will be able to access them via the console or service catalog CLI.

```python
# Example automatically generated from non-compiling source. May contain errors.
import aws_cdk.aws_iam as iam


user = iam.User(self, "MyUser")
portfolio.give_access_to_user(user)

role = iam.Role(self, "MyRole",
    assumed_by=iam.AccountRootPrincipal()
)
portfolio.give_access_to_role(role)

group = iam.Group(self, "MyGroup")
portfolio.give_access_to_group(group)
```

### Sharing a portfolio with another AWS account

A portfolio can be programatically shared with other accounts so that specified users can also access it:

```python
# Example automatically generated from non-compiling source. May contain errors.
portfolio.share_with_account("012345678901")
```

## Product

Products are the resources you are allowing end users to provision and utilize.
The CDK currently only supports adding products of type Cloudformation product.
Using the CDK, a new Product can be created with the `CloudFormationProduct` construct.
`CloudFormationTemplate.fromUrl` can be utilized to create a Product using a Cloudformation template directly from an URL:

```python
product = servicecatalog.CloudFormationProduct(self, "MyFirstProduct",
    product_name="My Product",
    owner="Product Owner",
    product_versions=[servicecatalog.CloudFormationProductVersion(
        product_version_name="v1",
        cloud_formation_template=servicecatalog.CloudFormationTemplate.from_url("https://raw.githubusercontent.com/awslabs/aws-cloudformation-templates/master/aws/services/ServiceCatalog/Product.yaml")
    )
    ]
)
```

### Creating a product from a local asset

A `CloudFormationProduct` can also be created using a Cloudformation template from an Asset.
Assets are files that are uploaded to an S3 Bucket before deployment.
`CloudFormationTemplate.fromAsset` can be utilized to create a Product by passing the path to a local template file on your disk:

```python
import path as path


product = servicecatalog.CloudFormationProduct(self, "MyFirstProduct",
    product_name="My Product",
    owner="Product Owner",
    product_versions=[servicecatalog.CloudFormationProductVersion(
        product_version_name="v1",
        cloud_formation_template=servicecatalog.CloudFormationTemplate.from_url("https://raw.githubusercontent.com/awslabs/aws-cloudformation-templates/master/aws/services/ServiceCatalog/Product.yaml")
    ), servicecatalog.CloudFormationProductVersion(
        product_version_name="v2",
        cloud_formation_template=servicecatalog.CloudFormationTemplate.from_asset(path.join(__dirname, "development-environment.template.json"))
    )
    ]
)
```

### Creating a product from a stack

You can define a service catalog `CloudFormationProduct` entirely within CDK using a service catalog `ProductStack`.
A separate child stack for your product is created and you can add resources like you would for any other CDK stack,
such as an S3 Bucket, IAM roles, and EC2 instances. This stack is passed in as a product version to your
product.  This will not create a separate stack during deployment.

```python
# Example automatically generated from non-compiling source. May contain errors.
import aws_cdk.aws_s3 as s3
import aws_cdk as cdk


class S3BucketProduct(servicecatalog.ProductStack):
    def __init__(self, scope, id):
        super().__init__(scope, id)

        s3.Bucket(self, "BucketProduct")

product = servicecatalog.CloudFormationProduct(self, "MyFirstProduct",
    product_name="My Product",
    owner="Product Owner",
    product_versions=[servicecatalog.CloudFormationProductVersion(
        product_version_name="v1",
        cloud_formation_template=servicecatalog.CloudFormationTemplate.from_product_stack(S3BucketProduct(self, "S3BucketProduct"))
    )
    ]
)
```

### Adding a product to a portfolio

You add products to a portfolio to manage your resources at scale.  After adding a product to a portfolio,
it creates a portfolio-product association, and will become visible from the portfolio side in both the console and service catalog CLI.
A product can be added to multiple portfolios depending on your resource and organizational needs.

```python
portfolio.add_product(product)
```

## Tag Options

TagOptions allow administrators to easily manage tags on provisioned products by creating a selection of tags for end users to choose from.
For example, an end user can choose an `ec2` for the instance type size.
TagOptions are created by specifying a key with a selection of values and can be associated with both portfolios and products.
When launching a product, both the TagOptions associated with the product and the containing portfolio are made available.

At the moment, TagOptions can only be disabled in the console.

```python
tag_options_for_portfolio = servicecatalog.TagOptions({
    "cost_center": ["Data Insights", "Marketing"]
})
portfolio.associate_tag_options(tag_options_for_portfolio)

tag_options_for_product = servicecatalog.TagOptions({
    "ec2_instance_type": ["A1", "M4"],
    "ec2_instance_size": ["medium", "large"]
})
product.associate_tag_options(tag_options_for_product)
```

## Constraints

Constraints define governance mechanisms that allow you to manage permissions, notifications, and options related to actions end users can perform on products,
Constraints are applied on a portfolio-product association.
Using the CDK, if you do not explicitly associate a product to a portfolio and add a constraint, it will automatically add an association for you.

There are rules around plurariliites of constraints for a portfolio and product.
For example, you can only have a single "tag update" constraint applied to a portfolio-product association.
If a misconfigured constraint is added, `synth` will fail with an error message.

Read more at [Service Catalog Constraints](https://docs.aws.amazon.com/servicecatalog/latest/adminguide/constraints.html).

### Tag update constraint

Tag update constraints allow or disallow end users to update tags on resources associated with an AWS Service Catalog product upon provisioning.
By default, tag updating is not permitted.
If tag updating is allowed, then new tags associated with the product or portfolio will be applied to provisioned resources during a provisioned product update.

```python
portfolio.add_product(product)

portfolio.constrain_tag_updates(product)
```

If you want to disable this feature later on, you can update it by setting the "allow" parameter to `false`:

```python
# to disable tag updates:
portfolio.constrain_tag_updates(product,
    allow=False
)
```

### Notify on stack events

Allows users to subscribe an AWS `SNS` topic to the stack events of the product.
When an end user provisions a product it creates a product stack that notifies the subscribed topic on creation, edit, and delete events.
An individual `SNS` topic may only be subscribed once to a portfolio-product association.

```python
import aws_cdk.aws_sns as sns


topic1 = sns.Topic(self, "MyTopic1")
portfolio.notify_on_stack_events(product, topic1)

topic2 = sns.Topic(self, "MyTopic2")
portfolio.notify_on_stack_events(product, topic2,
    description="description for this topic2"
)
```

### CloudFormation parameters constraint

CloudFormation parameters constraints allow you to configure the that are available to end users when they launch a product via defined rules.
A rule consists of one or more assertions that narrow the allowable values for parameters in a product.
You can configure multiple parameter constraints to govern the different parameters and parameter options in your products.
For example, a rule might define the various instance types that users can choose from when launching a stack that includes EC2 instances.
A parameter rule has an optional `condition` field that allows ability to configure when rules are applied.
If a `condition` is specified, all the assertions will be applied if the condition evalutates to true.
For information on rule-specific intrinsic functions to define rule conditions and assertions,
see [AWS Rule Functions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-rules.html).

```python
import aws_cdk as cdk


portfolio.constrain_cloud_formation_parameters(product,
    rule=servicecatalog.TemplateRule(
        rule_name="testInstanceType",
        condition=cdk.Fn.condition_equals(cdk.Fn.ref("Environment"), "test"),
        assertions=[servicecatalog.TemplateRuleAssertion(
            assert=cdk.Fn.condition_contains(["t2.micro", "t2.small"], cdk.Fn.ref("InstanceType")),
            description="For test environment, the instance type should be small"
        )]
    )
)
```

### Set launch role

Allows you to configure a specific AWS `IAM` role that a user must assume when launching a product.
By setting this launch role, you can control what policies and privileges end users can have.
The launch role must be assumed by the service catalog principal.
You can only have one launch role set for a portfolio-product association, and you cannot set a launch role if a StackSets deployment has been configured.

```python
import aws_cdk.aws_iam as iam


launch_role = iam.Role(self, "LaunchRole",
    assumed_by=iam.ServicePrincipal("servicecatalog.amazonaws.com")
)

portfolio.set_launch_role(product, launch_role)
```

You can also set the launch role using just the name of a role which is locally deployed in end user accounts.
This is useful for when roles and users are separately managed outside of the CDK.
The given role must exist in both the account that creates the launch role constraint,
as well as in any end user accounts that wish to provision a product with the launch role.

You can do this by passing in the role with an explicitly set name:

```python
import aws_cdk.aws_iam as iam


launch_role = iam.Role(self, "LaunchRole",
    role_name="MyRole",
    assumed_by=iam.ServicePrincipal("servicecatalog.amazonaws.com")
)

portfolio.set_local_launch_role(product, launch_role)
```

Or you can simply pass in a role name and CDK will create a role with that name that trusts service catalog in the account:

```python
import aws_cdk.aws_iam as iam


role_name = "MyRole"

launch_role = portfolio.set_local_launch_role_name(product, role_name)
```

See [Launch Constraint](https://docs.aws.amazon.com/servicecatalog/latest/adminguide/constraints-launch.html) documentation
to understand the permissions roles need.

### Deploy with StackSets

A StackSets deployment constraint allows you to configure product deployment options using
[AWS CloudFormation StackSets](https://docs.aws.amazon.com/servicecatalog/latest/adminguide/using-stacksets.html).
You can specify multiple accounts and regions for the product launch following StackSets conventions.
There is an additional field `allowStackSetInstanceOperations` that configures ability for end users to create, edit, or delete the stacks.
By default, this field is set to `false`.
End users can manage those accounts and determine where products deploy and the order of deployment.
You can only define one StackSets deployment configuration per portfolio-product association,
and you cannot both set a launch role and StackSets deployment configuration for an assocation.

```python
import aws_cdk.aws_iam as iam


admin_role = iam.Role(self, "AdminRole",
    assumed_by=iam.AccountRootPrincipal()
)

portfolio.deploy_with_stack_sets(product,
    accounts=["012345678901", "012345678902", "012345678903"],
    regions=["us-west-1", "us-east-1", "us-west-2", "us-east-1"],
    admin_role=admin_role,
    execution_role_name="SCStackSetExecutionRole",  # Name of role deployed in end users accounts.
    allow_stack_set_instance_operations=True
)
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

import aws_cdk
import aws_cdk.aws_iam
import aws_cdk.aws_s3_assets
import aws_cdk.aws_sns
import constructs


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.CloudFormationProductProps",
    jsii_struct_bases=[],
    name_mapping={
        "owner": "owner",
        "product_name": "productName",
        "product_versions": "productVersions",
        "description": "description",
        "distributor": "distributor",
        "message_language": "messageLanguage",
        "replace_product_version_ids": "replaceProductVersionIds",
        "support_description": "supportDescription",
        "support_email": "supportEmail",
        "support_url": "supportUrl",
        "tag_options": "tagOptions",
    },
)
class CloudFormationProductProps:
    def __init__(
        self,
        *,
        owner: builtins.str,
        product_name: builtins.str,
        product_versions: typing.Sequence["CloudFormationProductVersion"],
        description: typing.Optional[builtins.str] = None,
        distributor: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
        replace_product_version_ids: typing.Optional[builtins.bool] = None,
        support_description: typing.Optional[builtins.str] = None,
        support_email: typing.Optional[builtins.str] = None,
        support_url: typing.Optional[builtins.str] = None,
        tag_options: typing.Optional["TagOptions"] = None,
    ) -> None:
        '''(experimental) Properties for a Cloudformation Product.

        :param owner: (experimental) The owner of the product.
        :param product_name: (experimental) The name of the product.
        :param product_versions: (experimental) The configuration of the product version.
        :param description: (experimental) The description of the product. Default: - No description provided
        :param distributor: (experimental) The distributor of the product. Default: - No distributor provided
        :param message_language: (experimental) The language code. Controls language for logging and errors. Default: - English
        :param replace_product_version_ids: (experimental) Whether to give provisioning artifacts a new unique identifier when the product attributes or provisioning artifacts is updated. Default: false
        :param support_description: (experimental) The support information about the product. Default: - No support description provided
        :param support_email: (experimental) The contact email for product support. Default: - No support email provided
        :param support_url: (experimental) The contact URL for product support. Default: - No support URL provided
        :param tag_options: (experimental) TagOptions associated directly to a product. Default: - No tagOptions provided

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import path as path
            
            
            product = servicecatalog.CloudFormationProduct(self, "MyFirstProduct",
                product_name="My Product",
                owner="Product Owner",
                product_versions=[servicecatalog.CloudFormationProductVersion(
                    product_version_name="v1",
                    cloud_formation_template=servicecatalog.CloudFormationTemplate.from_url("https://raw.githubusercontent.com/awslabs/aws-cloudformation-templates/master/aws/services/ServiceCatalog/Product.yaml")
                ), servicecatalog.CloudFormationProductVersion(
                    product_version_name="v2",
                    cloud_formation_template=servicecatalog.CloudFormationTemplate.from_asset(path.join(__dirname, "development-environment.template.json"))
                )
                ]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "owner": owner,
            "product_name": product_name,
            "product_versions": product_versions,
        }
        if description is not None:
            self._values["description"] = description
        if distributor is not None:
            self._values["distributor"] = distributor
        if message_language is not None:
            self._values["message_language"] = message_language
        if replace_product_version_ids is not None:
            self._values["replace_product_version_ids"] = replace_product_version_ids
        if support_description is not None:
            self._values["support_description"] = support_description
        if support_email is not None:
            self._values["support_email"] = support_email
        if support_url is not None:
            self._values["support_url"] = support_url
        if tag_options is not None:
            self._values["tag_options"] = tag_options

    @builtins.property
    def owner(self) -> builtins.str:
        '''(experimental) The owner of the product.

        :stability: experimental
        '''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def product_name(self) -> builtins.str:
        '''(experimental) The name of the product.

        :stability: experimental
        '''
        result = self._values.get("product_name")
        assert result is not None, "Required property 'product_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def product_versions(self) -> typing.List["CloudFormationProductVersion"]:
        '''(experimental) The configuration of the product version.

        :stability: experimental
        '''
        result = self._values.get("product_versions")
        assert result is not None, "Required property 'product_versions' is missing"
        return typing.cast(typing.List["CloudFormationProductVersion"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the product.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def distributor(self) -> typing.Optional[builtins.str]:
        '''(experimental) The distributor of the product.

        :default: - No distributor provided

        :stability: experimental
        '''
        result = self._values.get("distributor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_language(self) -> typing.Optional["MessageLanguage"]:
        '''(experimental) The language code.

        Controls language for logging and errors.

        :default: - English

        :stability: experimental
        '''
        result = self._values.get("message_language")
        return typing.cast(typing.Optional["MessageLanguage"], result)

    @builtins.property
    def replace_product_version_ids(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to give provisioning artifacts a new unique identifier when the product attributes or provisioning artifacts is updated.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("replace_product_version_ids")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def support_description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The support information about the product.

        :default: - No support description provided

        :stability: experimental
        '''
        result = self._values.get("support_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def support_email(self) -> typing.Optional[builtins.str]:
        '''(experimental) The contact email for product support.

        :default: - No support email provided

        :stability: experimental
        '''
        result = self._values.get("support_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def support_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The contact URL for product support.

        :default: - No support URL provided

        :stability: experimental
        '''
        result = self._values.get("support_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_options(self) -> typing.Optional["TagOptions"]:
        '''(experimental) TagOptions associated directly to a product.

        :default: - No tagOptions provided

        :stability: experimental
        '''
        result = self._values.get("tag_options")
        return typing.cast(typing.Optional["TagOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFormationProductProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.CloudFormationProductVersion",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_formation_template": "cloudFormationTemplate",
        "description": "description",
        "product_version_name": "productVersionName",
        "validate_template": "validateTemplate",
    },
)
class CloudFormationProductVersion:
    def __init__(
        self,
        *,
        cloud_formation_template: "CloudFormationTemplate",
        description: typing.Optional[builtins.str] = None,
        product_version_name: typing.Optional[builtins.str] = None,
        validate_template: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties of product version (also known as a provisioning artifact).

        :param cloud_formation_template: (experimental) The S3 template that points to the provisioning version template.
        :param description: (experimental) The description of the product version. Default: - No description provided
        :param product_version_name: (experimental) The name of the product version. Default: - No product version name provided
        :param validate_template: (experimental) Whether the specified product template will be validated by CloudFormation. If turned off, an invalid template configuration can be stored. Default: true

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_servicecatalog_alpha as servicecatalog_alpha
            
            # cloud_formation_template: servicecatalog_alpha.CloudFormationTemplate
            
            cloud_formation_product_version = servicecatalog_alpha.CloudFormationProductVersion(
                cloud_formation_template=cloud_formation_template,
            
                # the properties below are optional
                description="description",
                product_version_name="productVersionName",
                validate_template=False
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cloud_formation_template": cloud_formation_template,
        }
        if description is not None:
            self._values["description"] = description
        if product_version_name is not None:
            self._values["product_version_name"] = product_version_name
        if validate_template is not None:
            self._values["validate_template"] = validate_template

    @builtins.property
    def cloud_formation_template(self) -> "CloudFormationTemplate":
        '''(experimental) The S3 template that points to the provisioning version template.

        :stability: experimental
        '''
        result = self._values.get("cloud_formation_template")
        assert result is not None, "Required property 'cloud_formation_template' is missing"
        return typing.cast("CloudFormationTemplate", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the product version.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def product_version_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the product version.

        :default: - No product version name provided

        :stability: experimental
        '''
        result = self._values.get("product_version_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def validate_template(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the specified product template will be validated by CloudFormation.

        If turned off, an invalid template configuration can be stored.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("validate_template")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFormationProductVersion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudFormationTemplate(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.CloudFormationTemplate",
):
    '''(experimental) Represents the Product Provisioning Artifact Template.

    :stability: experimental
    :exampleMetadata: fixture=portfolio-product infused

    Example::

        import aws_cdk.aws_iam as iam
        
        
        launch_role = iam.Role(self, "LaunchRole",
            role_name="MyRole",
            assumed_by=iam.ServicePrincipal("servicecatalog.amazonaws.com")
        )
        
        portfolio.set_local_launch_role(product, launch_role)
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromAsset") # type: ignore[misc]
    @builtins.classmethod
    def from_asset(
        cls,
        path: builtins.str,
        *,
        readers: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IGrantable]] = None,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[aws_cdk.AssetHashType] = None,
        bundling: typing.Optional[aws_cdk.BundlingOptions] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow_symlinks: typing.Optional[aws_cdk.SymlinkFollowMode] = None,
        ignore_mode: typing.Optional[aws_cdk.IgnoreMode] = None,
    ) -> "CloudFormationTemplate":
        '''(experimental) Loads the provisioning artifacts template from a local disk path.

        :param path: A file containing the provisioning artifacts.
        :param readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
        :param asset_hash: Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: Specifies the type of hash to calculate for this asset. If ``assetHash`` is configured, this option must be ``undefined`` or ``AssetHashType.CUSTOM``. Default: - the default is ``AssetHashType.SOURCE``, but if ``assetHash`` is explicitly specified this value defaults to ``AssetHashType.CUSTOM``.
        :param bundling: Bundle the asset by executing a command in a Docker container or a custom bundling provider. The asset path will be mounted at ``/asset-input``. The Docker container is responsible for putting content at ``/asset-output``. The content at ``/asset-output`` will be zipped and used as the final asset. Default: - uploaded as-is to S3 if the asset is a regular file or a .zip file, archived into a .zip file and uploaded to S3 otherwise
        :param exclude: Glob patterns to exclude from the copy. Default: - nothing is excluded
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param ignore_mode: The ignore behavior to use for exclude patterns. Default: IgnoreMode.GLOB

        :stability: experimental
        '''
        options = aws_cdk.aws_s3_assets.AssetOptions(
            readers=readers,
            asset_hash=asset_hash,
            asset_hash_type=asset_hash_type,
            bundling=bundling,
            exclude=exclude,
            follow_symlinks=follow_symlinks,
            ignore_mode=ignore_mode,
        )

        return typing.cast("CloudFormationTemplate", jsii.sinvoke(cls, "fromAsset", [path, options]))

    @jsii.member(jsii_name="fromProductStack") # type: ignore[misc]
    @builtins.classmethod
    def from_product_stack(
        cls,
        product_stack: "ProductStack",
    ) -> "CloudFormationTemplate":
        '''(experimental) Creates a product with the resources defined in the given product stack.

        :param product_stack: -

        :stability: experimental
        '''
        return typing.cast("CloudFormationTemplate", jsii.sinvoke(cls, "fromProductStack", [product_stack]))

    @jsii.member(jsii_name="fromUrl") # type: ignore[misc]
    @builtins.classmethod
    def from_url(cls, url: builtins.str) -> "CloudFormationTemplate":
        '''(experimental) Template from URL.

        :param url: The url that points to the provisioning artifacts template.

        :stability: experimental
        '''
        return typing.cast("CloudFormationTemplate", jsii.sinvoke(cls, "fromUrl", [url]))

    @jsii.member(jsii_name="bind") # type: ignore[misc]
    @abc.abstractmethod
    def bind(self, scope: constructs.Construct) -> "CloudFormationTemplateConfig":
        '''(experimental) Called when the product is initialized to allow this object to bind to the stack, add resources and have fun.

        :param scope: The binding scope. Don't be smart about trying to down-cast or assume it's initialized. You may just use it as a construct scope.

        :stability: experimental
        '''
        ...


class _CloudFormationTemplateProxy(CloudFormationTemplate):
    @jsii.member(jsii_name="bind")
    def bind(self, scope: constructs.Construct) -> "CloudFormationTemplateConfig":
        '''(experimental) Called when the product is initialized to allow this object to bind to the stack, add resources and have fun.

        :param scope: The binding scope. Don't be smart about trying to down-cast or assume it's initialized. You may just use it as a construct scope.

        :stability: experimental
        '''
        return typing.cast("CloudFormationTemplateConfig", jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, CloudFormationTemplate).__jsii_proxy_class__ = lambda : _CloudFormationTemplateProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.CloudFormationTemplateConfig",
    jsii_struct_bases=[],
    name_mapping={"http_url": "httpUrl"},
)
class CloudFormationTemplateConfig:
    def __init__(self, *, http_url: builtins.str) -> None:
        '''(experimental) Result of binding ``Template`` into a ``Product``.

        :param http_url: (experimental) The http url of the template in S3.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_servicecatalog_alpha as servicecatalog_alpha
            
            cloud_formation_template_config = servicecatalog_alpha.CloudFormationTemplateConfig(
                http_url="httpUrl"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "http_url": http_url,
        }

    @builtins.property
    def http_url(self) -> builtins.str:
        '''(experimental) The http url of the template in S3.

        :stability: experimental
        '''
        result = self._values.get("http_url")
        assert result is not None, "Required property 'http_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFormationTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.CommonConstraintOptions",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "message_language": "messageLanguage"},
)
class CommonConstraintOptions:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Properties for governance mechanisms and constraints.

        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        :exampleMetadata: fixture=portfolio-product infused

        Example::

            import aws_cdk.aws_sns as sns
            
            
            topic1 = sns.Topic(self, "MyTopic1")
            portfolio.notify_on_stack_events(product, topic1)
            
            topic2 = sns.Topic(self, "MyTopic2")
            portfolio.notify_on_stack_events(product, topic2,
                description="description for this topic2"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if message_language is not None:
            self._values["message_language"] = message_language

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the constraint.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_language(self) -> typing.Optional["MessageLanguage"]:
        '''(experimental) The language code.

        Configures the language for error messages from service catalog.

        :default: - English

        :stability: experimental
        '''
        result = self._values.get("message_language")
        return typing.cast(typing.Optional["MessageLanguage"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonConstraintOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-servicecatalog-alpha.IPortfolio")
class IPortfolio(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) A Service Catalog portfolio.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portfolioArn")
    def portfolio_arn(self) -> builtins.str:
        '''(experimental) The ARN of the portfolio.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> builtins.str:
        '''(experimental) The ID of the portfolio.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="addProduct")
    def add_product(self, product: "IProduct") -> None:
        '''(experimental) Associate portfolio with the given product.

        :param product: A service catalog produt.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="associateTagOptions")
    def associate_tag_options(self, tag_options: "TagOptions") -> None:
        '''(experimental) Associate Tag Options.

        A TagOption is a key-value pair managed in AWS Service Catalog.
        It is not an AWS tag, but serves as a template for creating an AWS tag based on the TagOption.

        :param tag_options: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="constrainCloudFormationParameters")
    def constrain_cloud_formation_parameters(
        self,
        product: "IProduct",
        *,
        rule: "TemplateRule",
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Set provisioning rules for the product.

        :param product: A service catalog product.
        :param rule: (experimental) The rule with condition and assertions to apply to template.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="constrainTagUpdates")
    def constrain_tag_updates(
        self,
        product: "IProduct",
        *,
        allow: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Add a Resource Update Constraint.

        :param product: -
        :param allow: (experimental) Toggle for if users should be allowed to change/update tags on provisioned products. Default: true
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="deployWithStackSets")
    def deploy_with_stack_sets(
        self,
        product: "IProduct",
        *,
        accounts: typing.Sequence[builtins.str],
        admin_role: aws_cdk.aws_iam.IRole,
        execution_role_name: builtins.str,
        regions: typing.Sequence[builtins.str],
        allow_stack_set_instance_operations: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Configure deployment options using AWS Cloudformation StackSets.

        :param product: A service catalog product.
        :param accounts: (experimental) List of accounts to deploy stacks to.
        :param admin_role: (experimental) IAM role used to administer the StackSets configuration.
        :param execution_role_name: (experimental) IAM role used to provision the products in the Stacks.
        :param regions: (experimental) List of regions to deploy stacks to.
        :param allow_stack_set_instance_operations: (experimental) Wether to allow end users to create, update, and delete stacks. Default: false
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="giveAccessToGroup")
    def give_access_to_group(self, group: aws_cdk.aws_iam.IGroup) -> None:
        '''(experimental) Associate portfolio with an IAM Group.

        :param group: an IAM Group.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="giveAccessToRole")
    def give_access_to_role(self, role: aws_cdk.aws_iam.IRole) -> None:
        '''(experimental) Associate portfolio with an IAM Role.

        :param role: an IAM role.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="giveAccessToUser")
    def give_access_to_user(self, user: aws_cdk.aws_iam.IUser) -> None:
        '''(experimental) Associate portfolio with an IAM User.

        :param user: an IAM user.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="notifyOnStackEvents")
    def notify_on_stack_events(
        self,
        product: "IProduct",
        topic: aws_cdk.aws_sns.ITopic,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Add notifications for supplied topics on the provisioned product.

        :param product: A service catalog product.
        :param topic: A SNS Topic to receive notifications on events related to the provisioned product.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="setLaunchRole")
    def set_launch_role(
        self,
        product: "IProduct",
        launch_role: aws_cdk.aws_iam.IRole,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Force users to assume a certain role when launching a product.

        This sets the launch role using the role arn which is tied to the account this role exists in.
        This is useful if you will be provisioning products from the account where this role exists.
        If you intend to share the portfolio across accounts, use a local launch role.

        :param product: A service catalog product.
        :param launch_role: The IAM role a user must assume when provisioning the product.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="setLocalLaunchRole")
    def set_local_launch_role(
        self,
        product: "IProduct",
        launch_role: aws_cdk.aws_iam.IRole,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Force users to assume a certain role when launching a product.

        The role name will be referenced by in the local account and must be set explicitly.
        This is useful when sharing the portfolio with multiple accounts.

        :param product: A service catalog product.
        :param launch_role: The IAM role a user must assume when provisioning the product. A role with this name must exist in the account where the portolio is created and the accounts it is shared with. The role name must be set explicitly.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="setLocalLaunchRoleName")
    def set_local_launch_role_name(
        self,
        product: "IProduct",
        launch_role_name: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> aws_cdk.aws_iam.IRole:
        '''(experimental) Force users to assume a certain role when launching a product.

        The role will be referenced by name in the local account instead of a static role arn.
        A role with this name will automatically be created and assumable by Service Catalog in this account.
        This is useful when sharing the portfolio with multiple accounts.

        :param product: A service catalog product.
        :param launch_role_name: The name of the IAM role a user must assume when provisioning the product. A role with this name must exist in the account where the portolio is created and the accounts it is shared with.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="shareWithAccount")
    def share_with_account(
        self,
        account_id: builtins.str,
        *,
        message_language: typing.Optional["MessageLanguage"] = None,
        share_tag_options: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Initiate a portfolio share with another account.

        :param account_id: AWS account to share portfolio with.
        :param message_language: (experimental) The message language of the share. Controls status and error message language for share. Default: - English
        :param share_tag_options: (experimental) Whether to share tagOptions as a part of the portfolio share. Default: - share not specified

        :stability: experimental
        '''
        ...


class _IPortfolioProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) A Service Catalog portfolio.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-servicecatalog-alpha.IPortfolio"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portfolioArn")
    def portfolio_arn(self) -> builtins.str:
        '''(experimental) The ARN of the portfolio.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "portfolioArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> builtins.str:
        '''(experimental) The ID of the portfolio.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "portfolioId"))

    @jsii.member(jsii_name="addProduct")
    def add_product(self, product: "IProduct") -> None:
        '''(experimental) Associate portfolio with the given product.

        :param product: A service catalog produt.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addProduct", [product]))

    @jsii.member(jsii_name="associateTagOptions")
    def associate_tag_options(self, tag_options: "TagOptions") -> None:
        '''(experimental) Associate Tag Options.

        A TagOption is a key-value pair managed in AWS Service Catalog.
        It is not an AWS tag, but serves as a template for creating an AWS tag based on the TagOption.

        :param tag_options: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "associateTagOptions", [tag_options]))

    @jsii.member(jsii_name="constrainCloudFormationParameters")
    def constrain_cloud_formation_parameters(
        self,
        product: "IProduct",
        *,
        rule: "TemplateRule",
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Set provisioning rules for the product.

        :param product: A service catalog product.
        :param rule: (experimental) The rule with condition and assertions to apply to template.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = CloudFormationRuleConstraintOptions(
            rule=rule, description=description, message_language=message_language
        )

        return typing.cast(None, jsii.invoke(self, "constrainCloudFormationParameters", [product, options]))

    @jsii.member(jsii_name="constrainTagUpdates")
    def constrain_tag_updates(
        self,
        product: "IProduct",
        *,
        allow: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Add a Resource Update Constraint.

        :param product: -
        :param allow: (experimental) Toggle for if users should be allowed to change/update tags on provisioned products. Default: true
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = TagUpdateConstraintOptions(
            allow=allow, description=description, message_language=message_language
        )

        return typing.cast(None, jsii.invoke(self, "constrainTagUpdates", [product, options]))

    @jsii.member(jsii_name="deployWithStackSets")
    def deploy_with_stack_sets(
        self,
        product: "IProduct",
        *,
        accounts: typing.Sequence[builtins.str],
        admin_role: aws_cdk.aws_iam.IRole,
        execution_role_name: builtins.str,
        regions: typing.Sequence[builtins.str],
        allow_stack_set_instance_operations: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Configure deployment options using AWS Cloudformation StackSets.

        :param product: A service catalog product.
        :param accounts: (experimental) List of accounts to deploy stacks to.
        :param admin_role: (experimental) IAM role used to administer the StackSets configuration.
        :param execution_role_name: (experimental) IAM role used to provision the products in the Stacks.
        :param regions: (experimental) List of regions to deploy stacks to.
        :param allow_stack_set_instance_operations: (experimental) Wether to allow end users to create, update, and delete stacks. Default: false
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = StackSetsConstraintOptions(
            accounts=accounts,
            admin_role=admin_role,
            execution_role_name=execution_role_name,
            regions=regions,
            allow_stack_set_instance_operations=allow_stack_set_instance_operations,
            description=description,
            message_language=message_language,
        )

        return typing.cast(None, jsii.invoke(self, "deployWithStackSets", [product, options]))

    @jsii.member(jsii_name="giveAccessToGroup")
    def give_access_to_group(self, group: aws_cdk.aws_iam.IGroup) -> None:
        '''(experimental) Associate portfolio with an IAM Group.

        :param group: an IAM Group.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "giveAccessToGroup", [group]))

    @jsii.member(jsii_name="giveAccessToRole")
    def give_access_to_role(self, role: aws_cdk.aws_iam.IRole) -> None:
        '''(experimental) Associate portfolio with an IAM Role.

        :param role: an IAM role.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "giveAccessToRole", [role]))

    @jsii.member(jsii_name="giveAccessToUser")
    def give_access_to_user(self, user: aws_cdk.aws_iam.IUser) -> None:
        '''(experimental) Associate portfolio with an IAM User.

        :param user: an IAM user.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "giveAccessToUser", [user]))

    @jsii.member(jsii_name="notifyOnStackEvents")
    def notify_on_stack_events(
        self,
        product: "IProduct",
        topic: aws_cdk.aws_sns.ITopic,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Add notifications for supplied topics on the provisioned product.

        :param product: A service catalog product.
        :param topic: A SNS Topic to receive notifications on events related to the provisioned product.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = CommonConstraintOptions(
            description=description, message_language=message_language
        )

        return typing.cast(None, jsii.invoke(self, "notifyOnStackEvents", [product, topic, options]))

    @jsii.member(jsii_name="setLaunchRole")
    def set_launch_role(
        self,
        product: "IProduct",
        launch_role: aws_cdk.aws_iam.IRole,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Force users to assume a certain role when launching a product.

        This sets the launch role using the role arn which is tied to the account this role exists in.
        This is useful if you will be provisioning products from the account where this role exists.
        If you intend to share the portfolio across accounts, use a local launch role.

        :param product: A service catalog product.
        :param launch_role: The IAM role a user must assume when provisioning the product.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = CommonConstraintOptions(
            description=description, message_language=message_language
        )

        return typing.cast(None, jsii.invoke(self, "setLaunchRole", [product, launch_role, options]))

    @jsii.member(jsii_name="setLocalLaunchRole")
    def set_local_launch_role(
        self,
        product: "IProduct",
        launch_role: aws_cdk.aws_iam.IRole,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> None:
        '''(experimental) Force users to assume a certain role when launching a product.

        The role name will be referenced by in the local account and must be set explicitly.
        This is useful when sharing the portfolio with multiple accounts.

        :param product: A service catalog product.
        :param launch_role: The IAM role a user must assume when provisioning the product. A role with this name must exist in the account where the portolio is created and the accounts it is shared with. The role name must be set explicitly.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = CommonConstraintOptions(
            description=description, message_language=message_language
        )

        return typing.cast(None, jsii.invoke(self, "setLocalLaunchRole", [product, launch_role, options]))

    @jsii.member(jsii_name="setLocalLaunchRoleName")
    def set_local_launch_role_name(
        self,
        product: "IProduct",
        launch_role_name: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional["MessageLanguage"] = None,
    ) -> aws_cdk.aws_iam.IRole:
        '''(experimental) Force users to assume a certain role when launching a product.

        The role will be referenced by name in the local account instead of a static role arn.
        A role with this name will automatically be created and assumable by Service Catalog in this account.
        This is useful when sharing the portfolio with multiple accounts.

        :param product: A service catalog product.
        :param launch_role_name: The name of the IAM role a user must assume when provisioning the product. A role with this name must exist in the account where the portolio is created and the accounts it is shared with.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = CommonConstraintOptions(
            description=description, message_language=message_language
        )

        return typing.cast(aws_cdk.aws_iam.IRole, jsii.invoke(self, "setLocalLaunchRoleName", [product, launch_role_name, options]))

    @jsii.member(jsii_name="shareWithAccount")
    def share_with_account(
        self,
        account_id: builtins.str,
        *,
        message_language: typing.Optional["MessageLanguage"] = None,
        share_tag_options: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Initiate a portfolio share with another account.

        :param account_id: AWS account to share portfolio with.
        :param message_language: (experimental) The message language of the share. Controls status and error message language for share. Default: - English
        :param share_tag_options: (experimental) Whether to share tagOptions as a part of the portfolio share. Default: - share not specified

        :stability: experimental
        '''
        options = PortfolioShareOptions(
            message_language=message_language, share_tag_options=share_tag_options
        )

        return typing.cast(None, jsii.invoke(self, "shareWithAccount", [account_id, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPortfolio).__jsii_proxy_class__ = lambda : _IPortfolioProxy


@jsii.interface(jsii_type="@aws-cdk/aws-servicecatalog-alpha.IProduct")
class IProduct(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) A Service Catalog product, currently only supports type CloudFormationProduct.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productArn")
    def product_arn(self) -> builtins.str:
        '''(experimental) The ARN of the product.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productId")
    def product_id(self) -> builtins.str:
        '''(experimental) The id of the product.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="associateTagOptions")
    def associate_tag_options(self, tag_options: "TagOptions") -> None:
        '''(experimental) Associate Tag Options.

        A TagOption is a key-value pair managed in AWS Service Catalog.
        It is not an AWS tag, but serves as a template for creating an AWS tag based on the TagOption.

        :param tag_options: -

        :stability: experimental
        '''
        ...


class _IProductProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) A Service Catalog product, currently only supports type CloudFormationProduct.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-servicecatalog-alpha.IProduct"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productArn")
    def product_arn(self) -> builtins.str:
        '''(experimental) The ARN of the product.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "productArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productId")
    def product_id(self) -> builtins.str:
        '''(experimental) The id of the product.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "productId"))

    @jsii.member(jsii_name="associateTagOptions")
    def associate_tag_options(self, tag_options: "TagOptions") -> None:
        '''(experimental) Associate Tag Options.

        A TagOption is a key-value pair managed in AWS Service Catalog.
        It is not an AWS tag, but serves as a template for creating an AWS tag based on the TagOption.

        :param tag_options: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "associateTagOptions", [tag_options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IProduct).__jsii_proxy_class__ = lambda : _IProductProxy


@jsii.enum(jsii_type="@aws-cdk/aws-servicecatalog-alpha.MessageLanguage")
class MessageLanguage(enum.Enum):
    '''(experimental) The language code.

    Used for error and logging messages for end users.
    The default behavior if not specified is English.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        servicecatalog.Portfolio(self, "MyFirstPortfolio",
            display_name="MyFirstPortfolio",
            provider_name="MyTeam",
            description="Portfolio for a project",
            message_language=servicecatalog.MessageLanguage.EN
        )
    '''

    EN = "EN"
    '''(experimental) English.

    :stability: experimental
    '''
    JP = "JP"
    '''(experimental) Japanese.

    :stability: experimental
    '''
    ZH = "ZH"
    '''(experimental) Chinese.

    :stability: experimental
    '''


@jsii.implements(IPortfolio)
class Portfolio(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.Portfolio",
):
    '''(experimental) A Service Catalog portfolio.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        servicecatalog.Portfolio(self, "MyFirstPortfolio",
            display_name="MyFirstPortfolio",
            provider_name="MyTeam"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        display_name: builtins.str,
        provider_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
        tag_options: typing.Optional["TagOptions"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param display_name: (experimental) The name of the portfolio.
        :param provider_name: (experimental) The provider name.
        :param description: (experimental) Description for portfolio. Default: - No description provided
        :param message_language: (experimental) The message language. Controls language for status logging and errors. Default: - English
        :param tag_options: (experimental) TagOptions associated directly to a portfolio. Default: - No tagOptions provided

        :stability: experimental
        '''
        props = PortfolioProps(
            display_name=display_name,
            provider_name=provider_name,
            description=description,
            message_language=message_language,
            tag_options=tag_options,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromPortfolioArn") # type: ignore[misc]
    @builtins.classmethod
    def from_portfolio_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        portfolio_arn: builtins.str,
    ) -> IPortfolio:
        '''(experimental) Creates a Portfolio construct that represents an external portfolio.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param portfolio_arn: the Amazon Resource Name of the existing portfolio.

        :stability: experimental
        '''
        return typing.cast(IPortfolio, jsii.sinvoke(cls, "fromPortfolioArn", [scope, id, portfolio_arn]))

    @jsii.member(jsii_name="addProduct")
    def add_product(self, product: IProduct) -> None:
        '''(experimental) Associate portfolio with the given product.

        :param product: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addProduct", [product]))

    @jsii.member(jsii_name="associateTagOptions")
    def associate_tag_options(self, tag_options: "TagOptions") -> None:
        '''(experimental) Associate Tag Options.

        A TagOption is a key-value pair managed in AWS Service Catalog.
        It is not an AWS tag, but serves as a template for creating an AWS tag based on the TagOption.

        :param tag_options: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "associateTagOptions", [tag_options]))

    @jsii.member(jsii_name="constrainCloudFormationParameters")
    def constrain_cloud_formation_parameters(
        self,
        product: IProduct,
        *,
        rule: "TemplateRule",
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
    ) -> None:
        '''(experimental) Set provisioning rules for the product.

        :param product: -
        :param rule: (experimental) The rule with condition and assertions to apply to template.
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = CloudFormationRuleConstraintOptions(
            rule=rule, description=description, message_language=message_language
        )

        return typing.cast(None, jsii.invoke(self, "constrainCloudFormationParameters", [product, options]))

    @jsii.member(jsii_name="constrainTagUpdates")
    def constrain_tag_updates(
        self,
        product: IProduct,
        *,
        allow: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
    ) -> None:
        '''(experimental) Add a Resource Update Constraint.

        :param product: -
        :param allow: (experimental) Toggle for if users should be allowed to change/update tags on provisioned products. Default: true
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = TagUpdateConstraintOptions(
            allow=allow, description=description, message_language=message_language
        )

        return typing.cast(None, jsii.invoke(self, "constrainTagUpdates", [product, options]))

    @jsii.member(jsii_name="deployWithStackSets")
    def deploy_with_stack_sets(
        self,
        product: IProduct,
        *,
        accounts: typing.Sequence[builtins.str],
        admin_role: aws_cdk.aws_iam.IRole,
        execution_role_name: builtins.str,
        regions: typing.Sequence[builtins.str],
        allow_stack_set_instance_operations: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
    ) -> None:
        '''(experimental) Configure deployment options using AWS Cloudformation StackSets.

        :param product: -
        :param accounts: (experimental) List of accounts to deploy stacks to.
        :param admin_role: (experimental) IAM role used to administer the StackSets configuration.
        :param execution_role_name: (experimental) IAM role used to provision the products in the Stacks.
        :param regions: (experimental) List of regions to deploy stacks to.
        :param allow_stack_set_instance_operations: (experimental) Wether to allow end users to create, update, and delete stacks. Default: false
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = StackSetsConstraintOptions(
            accounts=accounts,
            admin_role=admin_role,
            execution_role_name=execution_role_name,
            regions=regions,
            allow_stack_set_instance_operations=allow_stack_set_instance_operations,
            description=description,
            message_language=message_language,
        )

        return typing.cast(None, jsii.invoke(self, "deployWithStackSets", [product, options]))

    @jsii.member(jsii_name="generateUniqueHash")
    def _generate_unique_hash(self, value: builtins.str) -> builtins.str:
        '''(experimental) Create a unique id based off the L1 CfnPortfolio or the arn of an imported portfolio.

        :param value: -

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "generateUniqueHash", [value]))

    @jsii.member(jsii_name="giveAccessToGroup")
    def give_access_to_group(self, group: aws_cdk.aws_iam.IGroup) -> None:
        '''(experimental) Associate portfolio with an IAM Group.

        :param group: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "giveAccessToGroup", [group]))

    @jsii.member(jsii_name="giveAccessToRole")
    def give_access_to_role(self, role: aws_cdk.aws_iam.IRole) -> None:
        '''(experimental) Associate portfolio with an IAM Role.

        :param role: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "giveAccessToRole", [role]))

    @jsii.member(jsii_name="giveAccessToUser")
    def give_access_to_user(self, user: aws_cdk.aws_iam.IUser) -> None:
        '''(experimental) Associate portfolio with an IAM User.

        :param user: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "giveAccessToUser", [user]))

    @jsii.member(jsii_name="notifyOnStackEvents")
    def notify_on_stack_events(
        self,
        product: IProduct,
        topic: aws_cdk.aws_sns.ITopic,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
    ) -> None:
        '''(experimental) Add notifications for supplied topics on the provisioned product.

        :param product: -
        :param topic: -
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = CommonConstraintOptions(
            description=description, message_language=message_language
        )

        return typing.cast(None, jsii.invoke(self, "notifyOnStackEvents", [product, topic, options]))

    @jsii.member(jsii_name="setLaunchRole")
    def set_launch_role(
        self,
        product: IProduct,
        launch_role: aws_cdk.aws_iam.IRole,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
    ) -> None:
        '''(experimental) Force users to assume a certain role when launching a product.

        This sets the launch role using the role arn which is tied to the account this role exists in.
        This is useful if you will be provisioning products from the account where this role exists.
        If you intend to share the portfolio across accounts, use a local launch role.

        :param product: -
        :param launch_role: -
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = CommonConstraintOptions(
            description=description, message_language=message_language
        )

        return typing.cast(None, jsii.invoke(self, "setLaunchRole", [product, launch_role, options]))

    @jsii.member(jsii_name="setLocalLaunchRole")
    def set_local_launch_role(
        self,
        product: IProduct,
        launch_role: aws_cdk.aws_iam.IRole,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
    ) -> None:
        '''(experimental) Force users to assume a certain role when launching a product.

        The role name will be referenced by in the local account and must be set explicitly.
        This is useful when sharing the portfolio with multiple accounts.

        :param product: -
        :param launch_role: -
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = CommonConstraintOptions(
            description=description, message_language=message_language
        )

        return typing.cast(None, jsii.invoke(self, "setLocalLaunchRole", [product, launch_role, options]))

    @jsii.member(jsii_name="setLocalLaunchRoleName")
    def set_local_launch_role_name(
        self,
        product: IProduct,
        launch_role_name: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
    ) -> aws_cdk.aws_iam.IRole:
        '''(experimental) Force users to assume a certain role when launching a product.

        The role will be referenced by name in the local account instead of a static role arn.
        A role with this name will automatically be created and assumable by Service Catalog in this account.
        This is useful when sharing the portfolio with multiple accounts.

        :param product: -
        :param launch_role_name: -
        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English

        :stability: experimental
        '''
        options = CommonConstraintOptions(
            description=description, message_language=message_language
        )

        return typing.cast(aws_cdk.aws_iam.IRole, jsii.invoke(self, "setLocalLaunchRoleName", [product, launch_role_name, options]))

    @jsii.member(jsii_name="shareWithAccount")
    def share_with_account(
        self,
        account_id: builtins.str,
        *,
        message_language: typing.Optional[MessageLanguage] = None,
        share_tag_options: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Initiate a portfolio share with another account.

        :param account_id: -
        :param message_language: (experimental) The message language of the share. Controls status and error message language for share. Default: - English
        :param share_tag_options: (experimental) Whether to share tagOptions as a part of the portfolio share. Default: - share not specified

        :stability: experimental
        '''
        options = PortfolioShareOptions(
            message_language=message_language, share_tag_options=share_tag_options
        )

        return typing.cast(None, jsii.invoke(self, "shareWithAccount", [account_id, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portfolioArn")
    def portfolio_arn(self) -> builtins.str:
        '''(experimental) The ARN of the portfolio.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "portfolioArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portfolioId")
    def portfolio_id(self) -> builtins.str:
        '''(experimental) The ID of the portfolio.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "portfolioId"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.PortfolioProps",
    jsii_struct_bases=[],
    name_mapping={
        "display_name": "displayName",
        "provider_name": "providerName",
        "description": "description",
        "message_language": "messageLanguage",
        "tag_options": "tagOptions",
    },
)
class PortfolioProps:
    def __init__(
        self,
        *,
        display_name: builtins.str,
        provider_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
        tag_options: typing.Optional["TagOptions"] = None,
    ) -> None:
        '''(experimental) Properties for a Portfolio.

        :param display_name: (experimental) The name of the portfolio.
        :param provider_name: (experimental) The provider name.
        :param description: (experimental) Description for portfolio. Default: - No description provided
        :param message_language: (experimental) The message language. Controls language for status logging and errors. Default: - English
        :param tag_options: (experimental) TagOptions associated directly to a portfolio. Default: - No tagOptions provided

        :stability: experimental
        :exampleMetadata: infused

        Example::

            servicecatalog.Portfolio(self, "MyFirstPortfolio",
                display_name="MyFirstPortfolio",
                provider_name="MyTeam"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "display_name": display_name,
            "provider_name": provider_name,
        }
        if description is not None:
            self._values["description"] = description
        if message_language is not None:
            self._values["message_language"] = message_language
        if tag_options is not None:
            self._values["tag_options"] = tag_options

    @builtins.property
    def display_name(self) -> builtins.str:
        '''(experimental) The name of the portfolio.

        :stability: experimental
        '''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider_name(self) -> builtins.str:
        '''(experimental) The provider name.

        :stability: experimental
        '''
        result = self._values.get("provider_name")
        assert result is not None, "Required property 'provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description for portfolio.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_language(self) -> typing.Optional[MessageLanguage]:
        '''(experimental) The message language.

        Controls language for
        status logging and errors.

        :default: - English

        :stability: experimental
        '''
        result = self._values.get("message_language")
        return typing.cast(typing.Optional[MessageLanguage], result)

    @builtins.property
    def tag_options(self) -> typing.Optional["TagOptions"]:
        '''(experimental) TagOptions associated directly to a portfolio.

        :default: - No tagOptions provided

        :stability: experimental
        '''
        result = self._values.get("tag_options")
        return typing.cast(typing.Optional["TagOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PortfolioProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.PortfolioShareOptions",
    jsii_struct_bases=[],
    name_mapping={
        "message_language": "messageLanguage",
        "share_tag_options": "shareTagOptions",
    },
)
class PortfolioShareOptions:
    def __init__(
        self,
        *,
        message_language: typing.Optional[MessageLanguage] = None,
        share_tag_options: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for portfolio share.

        :param message_language: (experimental) The message language of the share. Controls status and error message language for share. Default: - English
        :param share_tag_options: (experimental) Whether to share tagOptions as a part of the portfolio share. Default: - share not specified

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_servicecatalog_alpha as servicecatalog_alpha
            
            portfolio_share_options = servicecatalog_alpha.PortfolioShareOptions(
                message_language=servicecatalog_alpha.MessageLanguage.EN,
                share_tag_options=False
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if message_language is not None:
            self._values["message_language"] = message_language
        if share_tag_options is not None:
            self._values["share_tag_options"] = share_tag_options

    @builtins.property
    def message_language(self) -> typing.Optional[MessageLanguage]:
        '''(experimental) The message language of the share.

        Controls status and error message language for share.

        :default: - English

        :stability: experimental
        '''
        result = self._values.get("message_language")
        return typing.cast(typing.Optional[MessageLanguage], result)

    @builtins.property
    def share_tag_options(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to share tagOptions as a part of the portfolio share.

        :default: - share not specified

        :stability: experimental
        '''
        result = self._values.get("share_tag_options")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PortfolioShareOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IProduct)
class Product(
    aws_cdk.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.Product",
):
    '''(experimental) Abstract class for Service Catalog Product.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_servicecatalog_alpha as servicecatalog_alpha
        
        product = servicecatalog_alpha.Product.from_product_arn(self, "MyProduct", "productArn")
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        props = aws_cdk.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromProductArn") # type: ignore[misc]
    @builtins.classmethod
    def from_product_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        product_arn: builtins.str,
    ) -> IProduct:
        '''(experimental) Creates a Product construct that represents an external product.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param product_arn: Product Arn.

        :stability: experimental
        '''
        return typing.cast(IProduct, jsii.sinvoke(cls, "fromProductArn", [scope, id, product_arn]))

    @jsii.member(jsii_name="associateTagOptions")
    def associate_tag_options(self, tag_options: "TagOptions") -> None:
        '''(experimental) Associate Tag Options.

        A TagOption is a key-value pair managed in AWS Service Catalog.
        It is not an AWS tag, but serves as a template for creating an AWS tag based on the TagOption.

        :param tag_options: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "associateTagOptions", [tag_options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productArn")
    @abc.abstractmethod
    def product_arn(self) -> builtins.str:
        '''(experimental) The ARN of the product.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productId")
    @abc.abstractmethod
    def product_id(self) -> builtins.str:
        '''(experimental) The id of the product.

        :stability: experimental
        '''
        ...


class _ProductProxy(
    Product, jsii.proxy_for(aws_cdk.Resource) # type: ignore[misc]
):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productArn")
    def product_arn(self) -> builtins.str:
        '''(experimental) The ARN of the product.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "productArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productId")
    def product_id(self) -> builtins.str:
        '''(experimental) The id of the product.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "productId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Product).__jsii_proxy_class__ = lambda : _ProductProxy


class ProductStack(
    aws_cdk.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.ProductStack",
):
    '''(experimental) A Service Catalog product stack, which is similar in form to a Cloudformation nested stack.

    You can add the resources to this stack that you want to define for your service catalog product.

    This stack will not be treated as an independent deployment
    artifact (won't be listed in "cdk list" or deployable through "cdk deploy"),
    but rather only synthesized as a template and uploaded as an asset to S3.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        import aws_cdk.aws_s3 as s3
        import aws_cdk as cdk
        
        
        class S3BucketProduct(servicecatalog.ProductStack):
            def __init__(self, scope, id):
                super().__init__(scope, id)
        
                s3.Bucket(self, "BucketProduct")
        
        product = servicecatalog.CloudFormationProduct(self, "MyFirstProduct",
            product_name="My Product",
            owner="Product Owner",
            product_versions=[servicecatalog.CloudFormationProductVersion(
                product_version_name="v1",
                cloud_formation_template=servicecatalog.CloudFormationTemplate.from_product_stack(S3BucketProduct(self, "S3BucketProduct"))
            )
            ]
        )
    '''

    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="templateFile")
    def template_file(self) -> builtins.str:
        '''(experimental) The name of the CloudFormation template file emitted to the output directory during synthesis.

        Example value: ``MyStack.template.json``

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "templateFile"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.StackSetsConstraintOptions",
    jsii_struct_bases=[CommonConstraintOptions],
    name_mapping={
        "description": "description",
        "message_language": "messageLanguage",
        "accounts": "accounts",
        "admin_role": "adminRole",
        "execution_role_name": "executionRoleName",
        "regions": "regions",
        "allow_stack_set_instance_operations": "allowStackSetInstanceOperations",
    },
)
class StackSetsConstraintOptions(CommonConstraintOptions):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
        accounts: typing.Sequence[builtins.str],
        admin_role: aws_cdk.aws_iam.IRole,
        execution_role_name: builtins.str,
        regions: typing.Sequence[builtins.str],
        allow_stack_set_instance_operations: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for deploying with Stackset, which creates a StackSet constraint.

        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English
        :param accounts: (experimental) List of accounts to deploy stacks to.
        :param admin_role: (experimental) IAM role used to administer the StackSets configuration.
        :param execution_role_name: (experimental) IAM role used to provision the products in the Stacks.
        :param regions: (experimental) List of regions to deploy stacks to.
        :param allow_stack_set_instance_operations: (experimental) Wether to allow end users to create, update, and delete stacks. Default: false

        :stability: experimental
        :exampleMetadata: fixture=portfolio-product infused

        Example::

            import aws_cdk.aws_iam as iam
            
            
            admin_role = iam.Role(self, "AdminRole",
                assumed_by=iam.AccountRootPrincipal()
            )
            
            portfolio.deploy_with_stack_sets(product,
                accounts=["012345678901", "012345678902", "012345678903"],
                regions=["us-west-1", "us-east-1", "us-west-2", "us-east-1"],
                admin_role=admin_role,
                execution_role_name="SCStackSetExecutionRole",  # Name of role deployed in end users accounts.
                allow_stack_set_instance_operations=True
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "accounts": accounts,
            "admin_role": admin_role,
            "execution_role_name": execution_role_name,
            "regions": regions,
        }
        if description is not None:
            self._values["description"] = description
        if message_language is not None:
            self._values["message_language"] = message_language
        if allow_stack_set_instance_operations is not None:
            self._values["allow_stack_set_instance_operations"] = allow_stack_set_instance_operations

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the constraint.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_language(self) -> typing.Optional[MessageLanguage]:
        '''(experimental) The language code.

        Configures the language for error messages from service catalog.

        :default: - English

        :stability: experimental
        '''
        result = self._values.get("message_language")
        return typing.cast(typing.Optional[MessageLanguage], result)

    @builtins.property
    def accounts(self) -> typing.List[builtins.str]:
        '''(experimental) List of accounts to deploy stacks to.

        :stability: experimental
        '''
        result = self._values.get("accounts")
        assert result is not None, "Required property 'accounts' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def admin_role(self) -> aws_cdk.aws_iam.IRole:
        '''(experimental) IAM role used to administer the StackSets configuration.

        :stability: experimental
        '''
        result = self._values.get("admin_role")
        assert result is not None, "Required property 'admin_role' is missing"
        return typing.cast(aws_cdk.aws_iam.IRole, result)

    @builtins.property
    def execution_role_name(self) -> builtins.str:
        '''(experimental) IAM role used to provision the products in the Stacks.

        :stability: experimental
        '''
        result = self._values.get("execution_role_name")
        assert result is not None, "Required property 'execution_role_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def regions(self) -> typing.List[builtins.str]:
        '''(experimental) List of regions to deploy stacks to.

        :stability: experimental
        '''
        result = self._values.get("regions")
        assert result is not None, "Required property 'regions' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def allow_stack_set_instance_operations(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Wether to allow end users to create, update, and delete stacks.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("allow_stack_set_instance_operations")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StackSetsConstraintOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TagOptions(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.TagOptions",
):
    '''(experimental) Defines a Tag Option, which are similar to tags but have multiple values per key.

    :stability: experimental
    :exampleMetadata: fixture=portfolio-product infused

    Example::

        tag_options_for_portfolio = servicecatalog.TagOptions({
            "cost_center": ["Data Insights", "Marketing"]
        })
        portfolio.associate_tag_options(tag_options_for_portfolio)
        
        tag_options_for_product = servicecatalog.TagOptions({
            "ec2_instance_type": ["A1", "M4"],
            "ec2_instance_size": ["medium", "large"]
        })
        product.associate_tag_options(tag_options_for_product)
    '''

    def __init__(
        self,
        tag_options_map: typing.Mapping[builtins.str, typing.Sequence[builtins.str]],
    ) -> None:
        '''
        :param tag_options_map: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [tag_options_map])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagOptionsMap")
    def tag_options_map(
        self,
    ) -> typing.Mapping[builtins.str, typing.List[builtins.str]]:
        '''(experimental) List of CfnTagOption.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.List[builtins.str]], jsii.get(self, "tagOptionsMap"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.TagUpdateConstraintOptions",
    jsii_struct_bases=[CommonConstraintOptions],
    name_mapping={
        "description": "description",
        "message_language": "messageLanguage",
        "allow": "allow",
    },
)
class TagUpdateConstraintOptions(CommonConstraintOptions):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
        allow: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for ResourceUpdateConstraint.

        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English
        :param allow: (experimental) Toggle for if users should be allowed to change/update tags on provisioned products. Default: true

        :stability: experimental
        :exampleMetadata: fixture=portfolio-product infused

        Example::

            # to disable tag updates:
            portfolio.constrain_tag_updates(product,
                allow=False
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if message_language is not None:
            self._values["message_language"] = message_language
        if allow is not None:
            self._values["allow"] = allow

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the constraint.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_language(self) -> typing.Optional[MessageLanguage]:
        '''(experimental) The language code.

        Configures the language for error messages from service catalog.

        :default: - English

        :stability: experimental
        '''
        result = self._values.get("message_language")
        return typing.cast(typing.Optional[MessageLanguage], result)

    @builtins.property
    def allow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Toggle for if users should be allowed to change/update tags on provisioned products.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("allow")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TagUpdateConstraintOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.TemplateRule",
    jsii_struct_bases=[],
    name_mapping={
        "assertions": "assertions",
        "rule_name": "ruleName",
        "condition": "condition",
    },
)
class TemplateRule:
    def __init__(
        self,
        *,
        assertions: typing.Sequence["TemplateRuleAssertion"],
        rule_name: builtins.str,
        condition: typing.Optional[aws_cdk.ICfnRuleConditionExpression] = None,
    ) -> None:
        '''(experimental) Defines the provisioning template constraints.

        :param assertions: (experimental) A list of assertions that make up the rule.
        :param rule_name: (experimental) Name of the rule.
        :param condition: (experimental) Specify when to apply rule with a rule-specific intrinsic function. Default: - no rule condition provided

        :stability: experimental
        :exampleMetadata: fixture=portfolio-product infused

        Example::

            import aws_cdk as cdk
            
            
            portfolio.constrain_cloud_formation_parameters(product,
                rule=servicecatalog.TemplateRule(
                    rule_name="testInstanceType",
                    condition=cdk.Fn.condition_equals(cdk.Fn.ref("Environment"), "test"),
                    assertions=[servicecatalog.TemplateRuleAssertion(
                        assert=cdk.Fn.condition_contains(["t2.micro", "t2.small"], cdk.Fn.ref("InstanceType")),
                        description="For test environment, the instance type should be small"
                    )]
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "assertions": assertions,
            "rule_name": rule_name,
        }
        if condition is not None:
            self._values["condition"] = condition

    @builtins.property
    def assertions(self) -> typing.List["TemplateRuleAssertion"]:
        '''(experimental) A list of assertions that make up the rule.

        :stability: experimental
        '''
        result = self._values.get("assertions")
        assert result is not None, "Required property 'assertions' is missing"
        return typing.cast(typing.List["TemplateRuleAssertion"], result)

    @builtins.property
    def rule_name(self) -> builtins.str:
        '''(experimental) Name of the rule.

        :stability: experimental
        '''
        result = self._values.get("rule_name")
        assert result is not None, "Required property 'rule_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def condition(self) -> typing.Optional[aws_cdk.ICfnRuleConditionExpression]:
        '''(experimental) Specify when to apply rule with a rule-specific intrinsic function.

        :default: - no rule condition provided

        :stability: experimental
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[aws_cdk.ICfnRuleConditionExpression], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TemplateRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.TemplateRuleAssertion",
    jsii_struct_bases=[],
    name_mapping={"assert_": "assert", "description": "description"},
)
class TemplateRuleAssertion:
    def __init__(
        self,
        *,
        assert_: aws_cdk.ICfnRuleConditionExpression,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) An assertion within a template rule, defined by intrinsic functions.

        :param assert_: (experimental) The assertion condition.
        :param description: (experimental) The description for the asssertion. Default: - no description provided for the assertion.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_servicecatalog_alpha as servicecatalog_alpha
            import aws_cdk as cdk
            
            # cfn_rule_condition_expression: cdk.ICfnRuleConditionExpression
            
            template_rule_assertion = servicecatalog_alpha.TemplateRuleAssertion(
                assert=cfn_rule_condition_expression,
            
                # the properties below are optional
                description="description"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "assert_": assert_,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def assert_(self) -> aws_cdk.ICfnRuleConditionExpression:
        '''(experimental) The assertion condition.

        :stability: experimental
        '''
        result = self._values.get("assert_")
        assert result is not None, "Required property 'assert_' is missing"
        return typing.cast(aws_cdk.ICfnRuleConditionExpression, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description for the asssertion.

        :default: - no description provided for the assertion.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TemplateRuleAssertion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudFormationProduct(
    Product,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.CloudFormationProduct",
):
    '''(experimental) A Service Catalog Cloudformation Product.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import path as path
        
        
        product = servicecatalog.CloudFormationProduct(self, "MyFirstProduct",
            product_name="My Product",
            owner="Product Owner",
            product_versions=[servicecatalog.CloudFormationProductVersion(
                product_version_name="v1",
                cloud_formation_template=servicecatalog.CloudFormationTemplate.from_url("https://raw.githubusercontent.com/awslabs/aws-cloudformation-templates/master/aws/services/ServiceCatalog/Product.yaml")
            ), servicecatalog.CloudFormationProductVersion(
                product_version_name="v2",
                cloud_formation_template=servicecatalog.CloudFormationTemplate.from_asset(path.join(__dirname, "development-environment.template.json"))
            )
            ]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        owner: builtins.str,
        product_name: builtins.str,
        product_versions: typing.Sequence[CloudFormationProductVersion],
        description: typing.Optional[builtins.str] = None,
        distributor: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
        replace_product_version_ids: typing.Optional[builtins.bool] = None,
        support_description: typing.Optional[builtins.str] = None,
        support_email: typing.Optional[builtins.str] = None,
        support_url: typing.Optional[builtins.str] = None,
        tag_options: typing.Optional[TagOptions] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param owner: (experimental) The owner of the product.
        :param product_name: (experimental) The name of the product.
        :param product_versions: (experimental) The configuration of the product version.
        :param description: (experimental) The description of the product. Default: - No description provided
        :param distributor: (experimental) The distributor of the product. Default: - No distributor provided
        :param message_language: (experimental) The language code. Controls language for logging and errors. Default: - English
        :param replace_product_version_ids: (experimental) Whether to give provisioning artifacts a new unique identifier when the product attributes or provisioning artifacts is updated. Default: false
        :param support_description: (experimental) The support information about the product. Default: - No support description provided
        :param support_email: (experimental) The contact email for product support. Default: - No support email provided
        :param support_url: (experimental) The contact URL for product support. Default: - No support URL provided
        :param tag_options: (experimental) TagOptions associated directly to a product. Default: - No tagOptions provided

        :stability: experimental
        '''
        props = CloudFormationProductProps(
            owner=owner,
            product_name=product_name,
            product_versions=product_versions,
            description=description,
            distributor=distributor,
            message_language=message_language,
            replace_product_version_ids=replace_product_version_ids,
            support_description=support_description,
            support_email=support_email,
            support_url=support_url,
            tag_options=tag_options,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productArn")
    def product_arn(self) -> builtins.str:
        '''(experimental) The ARN of the product.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "productArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="productId")
    def product_id(self) -> builtins.str:
        '''(experimental) The id of the product.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "productId"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalog-alpha.CloudFormationRuleConstraintOptions",
    jsii_struct_bases=[CommonConstraintOptions],
    name_mapping={
        "description": "description",
        "message_language": "messageLanguage",
        "rule": "rule",
    },
)
class CloudFormationRuleConstraintOptions(CommonConstraintOptions):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        message_language: typing.Optional[MessageLanguage] = None,
        rule: TemplateRule,
    ) -> None:
        '''(experimental) Properties for provisoning rule constraint.

        :param description: (experimental) The description of the constraint. Default: - No description provided
        :param message_language: (experimental) The language code. Configures the language for error messages from service catalog. Default: - English
        :param rule: (experimental) The rule with condition and assertions to apply to template.

        :stability: experimental
        :exampleMetadata: fixture=portfolio-product infused

        Example::

            import aws_cdk as cdk
            
            
            portfolio.constrain_cloud_formation_parameters(product,
                rule=servicecatalog.TemplateRule(
                    rule_name="testInstanceType",
                    condition=cdk.Fn.condition_equals(cdk.Fn.ref("Environment"), "test"),
                    assertions=[servicecatalog.TemplateRuleAssertion(
                        assert=cdk.Fn.condition_contains(["t2.micro", "t2.small"], cdk.Fn.ref("InstanceType")),
                        description="For test environment, the instance type should be small"
                    )]
                )
            )
        '''
        if isinstance(rule, dict):
            rule = TemplateRule(**rule)
        self._values: typing.Dict[str, typing.Any] = {
            "rule": rule,
        }
        if description is not None:
            self._values["description"] = description
        if message_language is not None:
            self._values["message_language"] = message_language

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the constraint.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_language(self) -> typing.Optional[MessageLanguage]:
        '''(experimental) The language code.

        Configures the language for error messages from service catalog.

        :default: - English

        :stability: experimental
        '''
        result = self._values.get("message_language")
        return typing.cast(typing.Optional[MessageLanguage], result)

    @builtins.property
    def rule(self) -> TemplateRule:
        '''(experimental) The rule with condition and assertions to apply to template.

        :stability: experimental
        '''
        result = self._values.get("rule")
        assert result is not None, "Required property 'rule' is missing"
        return typing.cast(TemplateRule, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFormationRuleConstraintOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CloudFormationProduct",
    "CloudFormationProductProps",
    "CloudFormationProductVersion",
    "CloudFormationRuleConstraintOptions",
    "CloudFormationTemplate",
    "CloudFormationTemplateConfig",
    "CommonConstraintOptions",
    "IPortfolio",
    "IProduct",
    "MessageLanguage",
    "Portfolio",
    "PortfolioProps",
    "PortfolioShareOptions",
    "Product",
    "ProductStack",
    "StackSetsConstraintOptions",
    "TagOptions",
    "TagUpdateConstraintOptions",
    "TemplateRule",
    "TemplateRuleAssertion",
]

publication.publish()
