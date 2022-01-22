'''
# cdk-aspects-library-security-group

[![build](https://github.com/RenovoSolutions/cdk-aspects-library-security-group/actions/workflows/build.yml/badge.svg)](https://github.com/RenovoSolutions/cdk-aspects-library-security-group/actions/workflows/build.yml)

A CDK library containing EC2 security group related [CDK Aspects](https://docs.aws.amazon.com/cdk/latest/guide/aspects.html) and the ability to define custom aspects.

## Features

* Utilize built in aspects for common cases:

  * Disallow public access to any port
  * Disallow public access to AWS Restricted Common ports ([per the AWS Config rule](https://docs.aws.amazon.com/config/latest/developerguide/restricted-common-ports.html))
  * Disallow public access to SSH or RDP per CIS Benchmark guidelines and general good practice
  * Disallow public or ALL access to common management ports like SSH, RDP, WinRM, WinRM over HTTPS
  * Disallow public or ALL access common relational DB ports like MSSQL, MySQL, PostgreSQL, and Oracle
  * Disallow public or ALL common web ports like HTTP (80, 8080) and HTTPS (443, 8443)
* Create any other aspect using the base security group aspect class.
* By default aspects generate errors in the CDK metadata which the deployment or synth process will find, but this can be changed with the `annotationType` property
* All default provided aspects restrict based on the public access CIDRs (`0.0.0.0/0` and `::/0`) but you can also defined aspects with any set of restricted CIDRs or security group IDs you like

## API Doc

See [API](API.md)

## Examples

### Typescript

```
// Add an existing aspect to your stack
Aspects.of(stack).add(new NoPublicIngressAspect());

// Add a custom aspect to your stack
Aspects.of(stack).add(new SecurityGroupAspectBase({
  annotationText: 'This is a custom message warning you how you should not do what you are doing.',
  annotationType: AnnotationType.WARNING,
  ports: [5985],
  restrictedCidrs: ['10.1.0.0/16'],
}));

// Change an existing aspects message and type
Aspects.of(stack).add(new NoPublicIngressAspect(
  annotationText: 'This is custom text.',
  annotationType: AnnotationType.WARNING
));
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


@jsii.enum(
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.AnnotationType"
)
class AnnotationType(enum.Enum):
    '''The supported annotation types.

    Only error will stop deployment of restricted resources.
    '''

    WARNING = "WARNING"
    ERROR = "ERROR"
    INFO = "INFO"


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.AspectPropsBase",
    jsii_struct_bases=[],
    name_mapping={
        "annotation_text": "annotationText",
        "annotation_type": "annotationType",
    },
)
class AspectPropsBase:
    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''The base aspect properties available to any aspect.

        JSII doesn't support an Omit when extending interfaces, so we create a base class to extend from.
        This base class meets the needed properties for all non-base aspects.

        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if annotation_text is not None:
            self._values["annotation_text"] = annotation_text
        if annotation_type is not None:
            self._values["annotation_type"] = annotation_type

    @builtins.property
    def annotation_text(self) -> typing.Optional[builtins.str]:
        '''The annotation text to use for the annotation.'''
        result = self._values.get("annotation_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def annotation_type(self) -> typing.Optional[AnnotationType]:
        '''The annotation type to use for the annotation.'''
        result = self._values.get("annotation_type")
        return typing.cast(typing.Optional[AnnotationType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AspectPropsBase(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.AspectPropsExtended",
    jsii_struct_bases=[AspectPropsBase],
    name_mapping={
        "annotation_text": "annotationText",
        "annotation_type": "annotationType",
        "any_source": "anySource",
        "ports": "ports",
        "restricted_cidrs": "restrictedCidrs",
        "restricted_s_gs": "restrictedSGs",
    },
)
class AspectPropsExtended(AspectPropsBase):
    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
        any_source: typing.Optional[builtins.bool] = None,
        ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
        restricted_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        restricted_s_gs: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''The extended aspect properties available only to the base security aspects.

        These additional properties shouldn't be changed in aspects that already have clearly defined goals.
        So, this extended properties interface is applied selectively to the base aspects.

        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        :param any_source: Whether any source is valid. This will ignore all other restrictions and only check the port. Default: false
        :param ports: The restricted port. Defaults to restricting all ports and only checking sources. Default: undefined
        :param restricted_cidrs: The restricted CIDRs for the given port. Default: ['0.0.0.0/0', '::/0']
        :param restricted_s_gs: The restricted source security groups for the given port. Default: undefined
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if annotation_text is not None:
            self._values["annotation_text"] = annotation_text
        if annotation_type is not None:
            self._values["annotation_type"] = annotation_type
        if any_source is not None:
            self._values["any_source"] = any_source
        if ports is not None:
            self._values["ports"] = ports
        if restricted_cidrs is not None:
            self._values["restricted_cidrs"] = restricted_cidrs
        if restricted_s_gs is not None:
            self._values["restricted_s_gs"] = restricted_s_gs

    @builtins.property
    def annotation_text(self) -> typing.Optional[builtins.str]:
        '''The annotation text to use for the annotation.'''
        result = self._values.get("annotation_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def annotation_type(self) -> typing.Optional[AnnotationType]:
        '''The annotation type to use for the annotation.'''
        result = self._values.get("annotation_type")
        return typing.cast(typing.Optional[AnnotationType], result)

    @builtins.property
    def any_source(self) -> typing.Optional[builtins.bool]:
        '''Whether any source is valid.

        This will ignore all other restrictions and only check the port.

        :default: false
        '''
        result = self._values.get("any_source")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''The restricted port.

        Defaults to restricting all ports and only checking sources.

        :default: undefined
        '''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def restricted_cidrs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The restricted CIDRs for the given port.

        :default: ['0.0.0.0/0', '::/0']
        '''
        result = self._values.get("restricted_cidrs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def restricted_s_gs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The restricted source security groups for the given port.

        :default: undefined
        '''
        result = self._values.get("restricted_s_gs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AspectPropsExtended(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.RuleCheckArgs",
    jsii_struct_bases=[AspectPropsExtended],
    name_mapping={
        "annotation_text": "annotationText",
        "annotation_type": "annotationType",
        "any_source": "anySource",
        "ports": "ports",
        "restricted_cidrs": "restrictedCidrs",
        "restricted_s_gs": "restrictedSGs",
        "node": "node",
    },
)
class RuleCheckArgs(AspectPropsExtended):
    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
        any_source: typing.Optional[builtins.bool] = None,
        ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
        restricted_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        restricted_s_gs: typing.Optional[typing.Sequence[builtins.str]] = None,
        node: constructs.IConstruct,
    ) -> None:
        '''The arguments for the checkRules function.

        Extends the IAspectPropsBase interface which includes additional properties that can be used as args.

        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        :param any_source: Whether any source is valid. This will ignore all other restrictions and only check the port. Default: false
        :param ports: The restricted port. Defaults to restricting all ports and only checking sources. Default: undefined
        :param restricted_cidrs: The restricted CIDRs for the given port. Default: ['0.0.0.0/0', '::/0']
        :param restricted_s_gs: The restricted source security groups for the given port. Default: undefined
        :param node: The node to check.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "node": node,
        }
        if annotation_text is not None:
            self._values["annotation_text"] = annotation_text
        if annotation_type is not None:
            self._values["annotation_type"] = annotation_type
        if any_source is not None:
            self._values["any_source"] = any_source
        if ports is not None:
            self._values["ports"] = ports
        if restricted_cidrs is not None:
            self._values["restricted_cidrs"] = restricted_cidrs
        if restricted_s_gs is not None:
            self._values["restricted_s_gs"] = restricted_s_gs

    @builtins.property
    def annotation_text(self) -> typing.Optional[builtins.str]:
        '''The annotation text to use for the annotation.'''
        result = self._values.get("annotation_text")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def annotation_type(self) -> typing.Optional[AnnotationType]:
        '''The annotation type to use for the annotation.'''
        result = self._values.get("annotation_type")
        return typing.cast(typing.Optional[AnnotationType], result)

    @builtins.property
    def any_source(self) -> typing.Optional[builtins.bool]:
        '''Whether any source is valid.

        This will ignore all other restrictions and only check the port.

        :default: false
        '''
        result = self._values.get("any_source")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''The restricted port.

        Defaults to restricting all ports and only checking sources.

        :default: undefined
        '''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def restricted_cidrs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The restricted CIDRs for the given port.

        :default: ['0.0.0.0/0', '::/0']
        '''
        result = self._values.get("restricted_cidrs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def restricted_s_gs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The restricted source security groups for the given port.

        :default: undefined
        '''
        result = self._values.get("restricted_s_gs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def node(self) -> constructs.IConstruct:
        '''The node to check.'''
        result = self._values.get("node")
        assert result is not None, "Required property 'node' is missing"
        return typing.cast(constructs.IConstruct, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuleCheckArgs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.IAspect)
class SecurityGroupAspectBase(
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.SecurityGroupAspectBase",
):
    '''The base class for all security group aspects in the library.

    By default this will not restrict anything.
    '''

    def __init__(
        self,
        *,
        any_source: typing.Optional[builtins.bool] = None,
        ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
        restricted_cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
        restricted_s_gs: typing.Optional[typing.Sequence[builtins.str]] = None,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param any_source: Whether any source is valid. This will ignore all other restrictions and only check the port. Default: false
        :param ports: The restricted port. Defaults to restricting all ports and only checking sources. Default: undefined
        :param restricted_cidrs: The restricted CIDRs for the given port. Default: ['0.0.0.0/0', '::/0']
        :param restricted_s_gs: The restricted source security groups for the given port. Default: undefined
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsExtended(
            any_source=any_source,
            ports=ports,
            restricted_cidrs=restricted_cidrs,
            restricted_s_gs=restricted_s_gs,
            annotation_text=annotation_text,
            annotation_type=annotation_type,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, node: constructs.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="annotationText")
    def annotation_text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "annotationText"))

    @annotation_text.setter
    def annotation_text(self, value: builtins.str) -> None:
        jsii.set(self, "annotationText", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="annotationType")
    def annotation_type(self) -> AnnotationType:
        return typing.cast(AnnotationType, jsii.get(self, "annotationType"))

    @annotation_type.setter
    def annotation_type(self, value: AnnotationType) -> None:
        jsii.set(self, "annotationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="anySource")
    def any_source(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "anySource"))

    @any_source.setter
    def any_source(self, value: builtins.bool) -> None:
        jsii.set(self, "anySource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ports")
    def ports(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "ports"))

    @ports.setter
    def ports(self, value: typing.Optional[typing.List[jsii.Number]]) -> None:
        jsii.set(self, "ports", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictedCidrs")
    def restricted_cidrs(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "restrictedCidrs"))

    @restricted_cidrs.setter
    def restricted_cidrs(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "restrictedCidrs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictedSGs")
    def restricted_s_gs(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "restrictedSGs"))

    @restricted_s_gs.setter
    def restricted_s_gs(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "restrictedSGs", value)


class NoIngressCommonManagementPortsAspect(
    SecurityGroupAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.NoIngressCommonManagementPortsAspect",
):
    '''Aspect to restrict any access to common management ports.

    22 - SSH
    3389 - RDP
    5985 - WinRM
    5986 - WinRM HTTPS
    '''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


class NoIngressCommonRelationalDBPortsAspect(
    SecurityGroupAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.NoIngressCommonRelationalDBPortsAspect",
):
    '''Aspect to restrict any access to common relational DB ports.

    3306 - MySQL
    5432 - PostgreSQL
    1521 - Oracle
    1433 - SQL Server
    '''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


class NoIngressCommonWebPortsAspect(
    SecurityGroupAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.NoIngressCommonWebPortsAspect",
):
    '''Aspect to restrict any access to common web ports.

    80 - HTTP
    443 - HTTPS
    8080 - HTTP
    8443 - HTTPS
    '''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


@jsii.implements(aws_cdk.IAspect)
class NoPublicIngressAspectBase(
    SecurityGroupAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.NoPublicIngressAspectBase",
):
    '''The base aspect to determine if a security group allows inbound traffic from the public internet to any port.

    This inherits everything from the base SecurityGroupAspectBase class and sets a default set of CIDRS that match allowing all IPs on AWS.
    '''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


class NoPublicIngressCommonManagementPortsAspect(
    NoPublicIngressAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.NoPublicIngressCommonManagementPortsAspect",
):
    '''Aspect to restrict public access to common management ports.

    22 - SSH
    3389 - RDP
    5985 - WinRM
    5986 - WinRM HTTPS
    '''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


class NoPublicIngressCommonRelationalDBPortsAspect(
    NoPublicIngressAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.NoPublicIngressCommonRelationalDBPortsAspect",
):
    '''Aspect to restrict public access to common relational DB ports.

    3306 - MySQL
    5432 - PostgreSQL
    1521 - Oracle
    1433 - SQL Server
    '''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


class NoPublicIngressCommonWebPortsAspect(
    NoPublicIngressAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.NoPublicIngressCommonWebPortsAspect",
):
    '''Aspect to restrict public access to common web ports.

    80 - HTTP
    443 - HTTPS
    8080 - HTTP
    8443 - HTTPS
    '''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


class NoPublicIngressRDPAspect(
    NoPublicIngressAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.NoPublicIngressRDPAspect",
):
    '''Aspect to determine if a security group allows inbound traffic from the public internet to the RDP port.'''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


class NoPublicIngressSSHAspect(
    NoPublicIngressAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.NoPublicIngressSSHAspect",
):
    '''Aspect to determine if a security group allows inbound traffic from the public internet to the SSH port.'''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


class AWSRestrictedCommonPortsAspect(
    NoPublicIngressAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.AWSRestrictedCommonPortsAspect",
):
    '''Restricted common ports based on AWS Config rule https://docs.aws.amazon.com/config/latest/developerguide/restricted-common-ports.html.'''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


class CISAwsFoundationBenchmark4Dot1Aspect(
    NoPublicIngressSSHAspect,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.CISAwsFoundationBenchmark4Dot1Aspect",
):
    '''CIS AWS Foundations Benchmark 4.1.

    CIS recommends that no security group allow unrestricted ingress access to port 22. Removing unfettered connectivity to remote console services, such as SSH, reduces a server's exposure to risk.

    This aspect uses the NoPublicIngressSSHAspect with an alternate annotation text.
    '''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


class CISAwsFoundationBenchmark4Dot2Aspect(
    NoPublicIngressRDPAspect,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.CISAwsFoundationBenchmark4Dot2Aspect",
):
    '''CIS AWS Foundations Benchmark 4.2.

    CIS recommends that no security group allow unrestricted ingress access to port 3389. Removing unfettered connectivity to remote console services, such as RDP, reduces a server's exposure to risk.

    This aspect uses the NoPublicIngressRDPAspect with an alternate annotation text.
    '''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


@jsii.implements(aws_cdk.IAspect)
class NoPublicIngressAspect(
    NoPublicIngressAspectBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-aspects-library-security-group.NoPublicIngressAspect",
):
    '''The same as the base NoPublicIngressAspectBase but with a more descriptive annotation.

    Blocks the ANY port from the public internet.
    '''

    def __init__(
        self,
        *,
        annotation_text: typing.Optional[builtins.str] = None,
        annotation_type: typing.Optional[AnnotationType] = None,
    ) -> None:
        '''
        :param annotation_text: The annotation text to use for the annotation.
        :param annotation_type: The annotation type to use for the annotation.
        '''
        props = AspectPropsBase(
            annotation_text=annotation_text, annotation_type=annotation_type
        )

        jsii.create(self.__class__, self, [props])


__all__ = [
    "AWSRestrictedCommonPortsAspect",
    "AnnotationType",
    "AspectPropsBase",
    "AspectPropsExtended",
    "CISAwsFoundationBenchmark4Dot1Aspect",
    "CISAwsFoundationBenchmark4Dot2Aspect",
    "NoIngressCommonManagementPortsAspect",
    "NoIngressCommonRelationalDBPortsAspect",
    "NoIngressCommonWebPortsAspect",
    "NoPublicIngressAspect",
    "NoPublicIngressAspectBase",
    "NoPublicIngressCommonManagementPortsAspect",
    "NoPublicIngressCommonRelationalDBPortsAspect",
    "NoPublicIngressCommonWebPortsAspect",
    "NoPublicIngressRDPAspect",
    "NoPublicIngressSSHAspect",
    "RuleCheckArgs",
    "SecurityGroupAspectBase",
]

publication.publish()
