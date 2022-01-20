'''
# AWS::IoTFleetHub Construct Library

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

```python
import monocdk as iotfleethub
```

<!--BEGIN CFNONLY DISCLAIMER-->

There are no hand-written ([L2](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) constructs for this service yet.
However, you can still use the automatically generated [L1](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_l1_using) constructs, and use this service exactly as you would using CloudFormation directly.

For more information on the resources and properties available for this service, see the [CloudFormation documentation for AWS::IoTFleetHub](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/AWS_IoTFleetHub.html).

(Read the [CDK Contributing Guide](https://github.com/aws/aws-cdk/blob/master/CONTRIBUTING.md) if you are interested in contributing to this construct library.)

<!--END CFNONLY DISCLAIMER-->
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import (
    CfnResource as _CfnResource_e0a482dc,
    CfnTag as _CfnTag_95fbdc29,
    Construct as _Construct_e78e779f,
    IInspectable as _IInspectable_82c04a63,
    TagManager as _TagManager_0b7ab120,
    TreeInspector as _TreeInspector_1cd1894e,
)


@jsii.implements(_IInspectable_82c04a63)
class CfnApplication(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_iotfleethub.CfnApplication",
):
    '''A CloudFormation ``AWS::IoTFleetHub::Application``.

    Represents a Fleet Hub for AWS IoT Device Management web application.

    :cloudformationResource: AWS::IoTFleetHub::Application
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotfleethub-application.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_iotfleethub as iotfleethub
        
        cfn_application = iotfleethub.CfnApplication(self, "MyCfnApplication",
            application_name="applicationName",
            role_arn="roleArn",
        
            # the properties below are optional
            application_description="applicationDescription",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        application_name: builtins.str,
        role_arn: builtins.str,
        application_description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Create a new ``AWS::IoTFleetHub::Application``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param application_name: The name of the web application.
        :param role_arn: The ARN of the role that the web application assumes when it interacts with AWS IoT Core . .. epigraph:: The name of the role must be in the form ``FleetHub_random_string`` . Pattern: ``^arn:[!-~]+$``
        :param application_description: An optional description of the web application.
        :param tags: A set of key/value pairs that you can use to manage the web application resource.
        '''
        props = CfnApplicationProps(
            application_name=application_name,
            role_arn=role_arn,
            application_description=application_description,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_1cd1894e) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrApplicationArn")
    def attr_application_arn(self) -> builtins.str:
        '''The ARN of the web application.

        :cloudformationAttribute: ApplicationArn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrApplicationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrApplicationCreationDate")
    def attr_application_creation_date(self) -> jsii.Number:
        '''The date (in Unix epoch time) when the web application was created.

        :cloudformationAttribute: ApplicationCreationDate
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrApplicationCreationDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrApplicationId")
    def attr_application_id(self) -> builtins.str:
        '''The unique Id of the web application.

        :cloudformationAttribute: ApplicationId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrApplicationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrApplicationLastUpdateDate")
    def attr_application_last_update_date(self) -> jsii.Number:
        '''The date (in Unix epoch time) when the web application was last updated.

        :cloudformationAttribute: ApplicationLastUpdateDate
        '''
        return typing.cast(jsii.Number, jsii.get(self, "attrApplicationLastUpdateDate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrApplicationState")
    def attr_application_state(self) -> builtins.str:
        '''The current state of the web application.

        :cloudformationAttribute: ApplicationState
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrApplicationState"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrApplicationUrl")
    def attr_application_url(self) -> builtins.str:
        '''The URL of the web application.

        :cloudformationAttribute: ApplicationUrl
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrApplicationUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrErrorMessage")
    def attr_error_message(self) -> builtins.str:
        '''A message that explains any failures included in the applicationState response field.

        This message explains failures in the ``CreateApplication`` and ``DeleteApplication`` actions.

        :cloudformationAttribute: ErrorMessage
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrErrorMessage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrSsoClientId")
    def attr_sso_client_id(self) -> builtins.str:
        '''The Id of the single sign-on client that you use to authenticate and authorize users on the web application.

        :cloudformationAttribute: SsoClientId
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrSsoClientId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0b7ab120:
        '''A set of key/value pairs that you can use to manage the web application resource.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotfleethub-application.html#cfn-iotfleethub-application-tags
        '''
        return typing.cast(_TagManager_0b7ab120, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> builtins.str:
        '''The name of the web application.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotfleethub-application.html#cfn-iotfleethub-application-applicationname
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationName"))

    @application_name.setter
    def application_name(self, value: builtins.str) -> None:
        jsii.set(self, "applicationName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        '''The ARN of the role that the web application assumes when it interacts with AWS IoT Core .

        .. epigraph::

           The name of the role must be in the form ``FleetHub_random_string`` .

        Pattern: ``^arn:[!-~]+$``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotfleethub-application.html#cfn-iotfleethub-application-rolearn
        '''
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationDescription")
    def application_description(self) -> typing.Optional[builtins.str]:
        '''An optional description of the web application.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotfleethub-application.html#cfn-iotfleethub-application-applicationdescription
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "applicationDescription"))

    @application_description.setter
    def application_description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "applicationDescription", value)


@jsii.data_type(
    jsii_type="monocdk.aws_iotfleethub.CfnApplicationProps",
    jsii_struct_bases=[],
    name_mapping={
        "application_name": "applicationName",
        "role_arn": "roleArn",
        "application_description": "applicationDescription",
        "tags": "tags",
    },
)
class CfnApplicationProps:
    def __init__(
        self,
        *,
        application_name: builtins.str,
        role_arn: builtins.str,
        application_description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Properties for defining a ``CfnApplication``.

        :param application_name: The name of the web application.
        :param role_arn: The ARN of the role that the web application assumes when it interacts with AWS IoT Core . .. epigraph:: The name of the role must be in the form ``FleetHub_random_string`` . Pattern: ``^arn:[!-~]+$``
        :param application_description: An optional description of the web application.
        :param tags: A set of key/value pairs that you can use to manage the web application resource.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotfleethub-application.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_iotfleethub as iotfleethub
            
            cfn_application_props = iotfleethub.CfnApplicationProps(
                application_name="applicationName",
                role_arn="roleArn",
            
                # the properties below are optional
                application_description="applicationDescription",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "application_name": application_name,
            "role_arn": role_arn,
        }
        if application_description is not None:
            self._values["application_description"] = application_description
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def application_name(self) -> builtins.str:
        '''The name of the web application.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotfleethub-application.html#cfn-iotfleethub-application-applicationname
        '''
        result = self._values.get("application_name")
        assert result is not None, "Required property 'application_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''The ARN of the role that the web application assumes when it interacts with AWS IoT Core .

        .. epigraph::

           The name of the role must be in the form ``FleetHub_random_string`` .

        Pattern: ``^arn:[!-~]+$``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotfleethub-application.html#cfn-iotfleethub-application-rolearn
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_description(self) -> typing.Optional[builtins.str]:
        '''An optional description of the web application.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotfleethub-application.html#cfn-iotfleethub-application-applicationdescription
        '''
        result = self._values.get("application_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_95fbdc29]]:
        '''A set of key/value pairs that you can use to manage the web application resource.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iotfleethub-application.html#cfn-iotfleethub-application-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_95fbdc29]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnApplicationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CfnApplication",
    "CfnApplicationProps",
]

publication.publish()
