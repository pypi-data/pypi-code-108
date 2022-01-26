'''
# AWS ServiceCatalogAppRegistry Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

[AWS Service Catalog App Registry](https://docs.aws.amazon.com/servicecatalog/latest/adminguide/appregistry.html)
enables organizations to create and manage repositores of applications and associated resources.

## Table Of Contents

* [Application](#application)
* [Attribute-Group](#attribute-group)
* [Associations](#associations)

  * [Associating application with an attribute group](#attribute-group-association)
  * [Associating application with a stack](#resource-association)

The `@aws-cdk/aws-servicecatalogappregistry` package contains resources that enable users to automate governance and management of their AWS resources at scale.

```python
import aws_cdk.aws_servicecatalogappregistry_alpha as appreg
```

## Application

An AppRegistry application enables you to define your applications and associated resources.
The application name must be unique at the account level, but is mutable.

```python
application = appreg.Application(self, "MyFirstApplication",
    application_name="MyFirstApplicationName",
    description="description for my application"
)
```

An application that has been created outside of the stack can be imported into your CDK app.
Applications can be imported by their ARN via the `Application.fromApplicationArn()` API:

```python
imported_application = appreg.Application.from_application_arn(self, "MyImportedApplication", "arn:aws:servicecatalog:us-east-1:012345678910:/applications/0aqmvxvgmry0ecc4mjhwypun6i")
```

## Attribute Group

An AppRegistry attribute group acts as a container for user-defined attributes for an application.
Metadata is attached in a machine-readble format to integrate with automated workflows and tools.

```python
attribute_group = appreg.AttributeGroup(self, "MyFirstAttributeGroup",
    attribute_group_name="MyFirstAttributeGroupName",
    description="description for my attribute group",  # the description is optional,
    attributes={
        "project": "foo",
        "team": ["member1", "member2", "member3"],
        "public": False,
        "stages": {
            "alpha": "complete",
            "beta": "incomplete",
            "release": "not started"
        }
    }
)
```

An attribute group that has been created outside of the stack can be imported into your CDK app.
Attribute groups can be imported by their ARN via the `AttributeGroup.fromAttributeGroupArn()` API:

```python
imported_attribute_group = appreg.AttributeGroup.from_attribute_group_arn(self, "MyImportedAttrGroup", "arn:aws:servicecatalog:us-east-1:012345678910:/attribute-groups/0aqmvxvgmry0ecc4mjhwypun6i")
```

## Associations

You can associate your appregistry application with attribute groups and resources.
Resources are CloudFormation stacks that you can associate with an application to group relevant
stacks together to enable metadata rich insights into your applications and resources.
A Cloudformation stack can only be associated with one appregistry application.
If a stack is associated with multiple applications in your app or is already associated with one,
CDK will fail at deploy time.

### Associating application with an attribute group

You can associate an attribute group with an application with the `associateAttributeGroup()` API:

```python
# application: appreg.Application
# attribute_group: appreg.AttributeGroup

application.associate_attribute_group(attribute_group)
```

### Associating application with a Stack

You can associate a stack with an application with the `associateStack()` API:

```python
# application: appreg.Application
app = App()
my_stack = Stack(app, "MyStack")
application.associate_stack(my_stack)
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
import constructs


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.ApplicationProps",
    jsii_struct_bases=[],
    name_mapping={"application_name": "applicationName", "description": "description"},
)
class ApplicationProps:
    def __init__(
        self,
        *,
        application_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a Service Catalog AppRegistry Application.

        :param application_name: (experimental) Enforces a particular physical application name.
        :param description: (experimental) Description for application. Default: - No description provided

        :stability: experimental
        :exampleMetadata: infused

        Example::

            application = appreg.Application(self, "MyFirstApplication",
                application_name="MyFirstApplicationName",
                description="description for my application"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "application_name": application_name,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def application_name(self) -> builtins.str:
        '''(experimental) Enforces a particular physical application name.

        :stability: experimental
        '''
        result = self._values.get("application_name")
        assert result is not None, "Required property 'application_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description for application.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.AttributeGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_group_name": "attributeGroupName",
        "attributes": "attributes",
        "description": "description",
    },
)
class AttributeGroupProps:
    def __init__(
        self,
        *,
        attribute_group_name: builtins.str,
        attributes: typing.Mapping[builtins.str, typing.Any],
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a Service Catalog AppRegistry Attribute Group.

        :param attribute_group_name: (experimental) Enforces a particular physical attribute group name.
        :param attributes: (experimental) A JSON of nested key-value pairs that represent the attributes in the group. Attributes maybe an empty JSON '{}', but must be explicitly stated.
        :param description: (experimental) Description for attribute group. Default: - No description provided

        :stability: experimental
        :exampleMetadata: infused

        Example::

            attribute_group = appreg.AttributeGroup(self, "MyFirstAttributeGroup",
                attribute_group_name="MyFirstAttributeGroupName",
                description="description for my attribute group",  # the description is optional,
                attributes={
                    "project": "foo",
                    "team": ["member1", "member2", "member3"],
                    "public": False,
                    "stages": {
                        "alpha": "complete",
                        "beta": "incomplete",
                        "release": "not started"
                    }
                }
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "attribute_group_name": attribute_group_name,
            "attributes": attributes,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def attribute_group_name(self) -> builtins.str:
        '''(experimental) Enforces a particular physical attribute group name.

        :stability: experimental
        '''
        result = self._values.get("attribute_group_name")
        assert result is not None, "Required property 'attribute_group_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) A JSON of nested key-value pairs that represent the attributes in the group.

        Attributes maybe an empty JSON '{}', but must be explicitly stated.

        :stability: experimental
        '''
        result = self._values.get("attributes")
        assert result is not None, "Required property 'attributes' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description for attribute group.

        :default: - No description provided

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AttributeGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.IApplication")
class IApplication(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) A Service Catalog AppRegistry Application.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The ARN of the application.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="associateAttributeGroup")
    def associate_attribute_group(self, attribute_group: "IAttributeGroup") -> None:
        '''(experimental) Associate thisapplication with an attribute group.

        :param attribute_group: AppRegistry attribute group.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="associateStack")
    def associate_stack(self, stack: aws_cdk.Stack) -> None:
        '''(experimental) Associate this application with a CloudFormation stack.

        :param stack: a CFN stack.

        :stability: experimental
        '''
        ...


class _IApplicationProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) A Service Catalog AppRegistry Application.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-servicecatalogappregistry-alpha.IApplication"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The ARN of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))

    @jsii.member(jsii_name="associateAttributeGroup")
    def associate_attribute_group(self, attribute_group: "IAttributeGroup") -> None:
        '''(experimental) Associate thisapplication with an attribute group.

        :param attribute_group: AppRegistry attribute group.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "associateAttributeGroup", [attribute_group]))

    @jsii.member(jsii_name="associateStack")
    def associate_stack(self, stack: aws_cdk.Stack) -> None:
        '''(experimental) Associate this application with a CloudFormation stack.

        :param stack: a CFN stack.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "associateStack", [stack]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IApplication).__jsii_proxy_class__ = lambda : _IApplicationProxy


@jsii.interface(
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.IAttributeGroup"
)
class IAttributeGroup(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) A Service Catalog AppRegistry Attribute Group.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeGroupArn")
    def attribute_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the attribute group.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeGroupId")
    def attribute_group_id(self) -> builtins.str:
        '''(experimental) The ID of the attribute group.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IAttributeGroupProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) A Service Catalog AppRegistry Attribute Group.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-servicecatalogappregistry-alpha.IAttributeGroup"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeGroupArn")
    def attribute_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the attribute group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "attributeGroupArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeGroupId")
    def attribute_group_id(self) -> builtins.str:
        '''(experimental) The ID of the attribute group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "attributeGroupId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAttributeGroup).__jsii_proxy_class__ = lambda : _IAttributeGroupProxy


@jsii.implements(IApplication)
class Application(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.Application",
):
    '''(experimental) A Service Catalog AppRegistry Application.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        application = appreg.Application(self, "MyFirstApplication",
            application_name="MyFirstApplicationName",
            description="description for my application"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        application_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application_name: (experimental) Enforces a particular physical application name.
        :param description: (experimental) Description for application. Default: - No description provided

        :stability: experimental
        '''
        props = ApplicationProps(
            application_name=application_name, description=description
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromApplicationArn") # type: ignore[misc]
    @builtins.classmethod
    def from_application_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        application_arn: builtins.str,
    ) -> IApplication:
        '''(experimental) Imports an Application construct that represents an external application.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param application_arn: the Amazon Resource Name of the existing AppRegistry Application.

        :stability: experimental
        '''
        return typing.cast(IApplication, jsii.sinvoke(cls, "fromApplicationArn", [scope, id, application_arn]))

    @jsii.member(jsii_name="associateAttributeGroup")
    def associate_attribute_group(self, attribute_group: IAttributeGroup) -> None:
        '''(experimental) Associate an attribute group with application If the attribute group is already associated, it will ignore duplicate request.

        :param attribute_group: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "associateAttributeGroup", [attribute_group]))

    @jsii.member(jsii_name="associateStack")
    def associate_stack(self, stack: aws_cdk.Stack) -> None:
        '''(experimental) Associate a stack with the application If the resource is already associated, it will ignore duplicate request.

        A stack can only be associated with one application.

        :param stack: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "associateStack", [stack]))

    @jsii.member(jsii_name="generateUniqueHash")
    def _generate_unique_hash(self, resource_address: builtins.str) -> builtins.str:
        '''(experimental) Create a unique id.

        :param resource_address: -

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "generateUniqueHash", [resource_address]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The ARN of the application.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationId")
    def application_id(self) -> builtins.str:
        '''(experimental) The ID of the application.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationId"))


@jsii.implements(IAttributeGroup)
class AttributeGroup(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-servicecatalogappregistry-alpha.AttributeGroup",
):
    '''(experimental) A Service Catalog AppRegistry Attribute Group.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        attribute_group = appreg.AttributeGroup(self, "MyFirstAttributeGroup",
            attribute_group_name="MyFirstAttributeGroupName",
            description="description for my attribute group",  # the description is optional,
            attributes={
                "project": "foo",
                "team": ["member1", "member2", "member3"],
                "public": False,
                "stages": {
                    "alpha": "complete",
                    "beta": "incomplete",
                    "release": "not started"
                }
            }
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        attribute_group_name: builtins.str,
        attributes: typing.Mapping[builtins.str, typing.Any],
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param attribute_group_name: (experimental) Enforces a particular physical attribute group name.
        :param attributes: (experimental) A JSON of nested key-value pairs that represent the attributes in the group. Attributes maybe an empty JSON '{}', but must be explicitly stated.
        :param description: (experimental) Description for attribute group. Default: - No description provided

        :stability: experimental
        '''
        props = AttributeGroupProps(
            attribute_group_name=attribute_group_name,
            attributes=attributes,
            description=description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAttributeGroupArn") # type: ignore[misc]
    @builtins.classmethod
    def from_attribute_group_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        attribute_group_arn: builtins.str,
    ) -> IAttributeGroup:
        '''(experimental) Imports an attribute group construct that represents an external attribute group.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param attribute_group_arn: the Amazon Resource Name of the existing AppRegistry attribute group.

        :stability: experimental
        '''
        return typing.cast(IAttributeGroup, jsii.sinvoke(cls, "fromAttributeGroupArn", [scope, id, attribute_group_arn]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeGroupArn")
    def attribute_group_arn(self) -> builtins.str:
        '''(experimental) The ARN of the attribute group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "attributeGroupArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attributeGroupId")
    def attribute_group_id(self) -> builtins.str:
        '''(experimental) The ID of the attribute group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "attributeGroupId"))


__all__ = [
    "Application",
    "ApplicationProps",
    "AttributeGroup",
    "AttributeGroupProps",
    "IApplication",
    "IAttributeGroup",
]

publication.publish()
