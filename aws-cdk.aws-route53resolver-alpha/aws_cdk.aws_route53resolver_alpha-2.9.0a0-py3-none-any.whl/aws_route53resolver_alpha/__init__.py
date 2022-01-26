'''
# Amazon Route53 Resolver Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## DNS Firewall

With Route 53 Resolver DNS Firewall, you can filter and regulate outbound DNS traffic for your
virtual private connections (VPCs). To do this, you create reusable collections of filtering rules
in DNS Firewall rule groups and associate the rule groups to your VPC.

DNS Firewall provides protection for outbound DNS requests from your VPCs. These requests route
through Resolver for domain name resolution. A primary use of DNS Firewall protections is to help
prevent DNS exfiltration of your data. DNS exfiltration can happen when a bad actor compromises
an application instance in your VPC and then uses DNS lookup to send data out of the VPC to a domain
that they control. With DNS Firewall, you can monitor and control the domains that your applications
can query. You can deny access to the domains that you know to be bad and allow all other queries
to pass through. Alternately, you can deny access to all domains except for the ones that you
explicitly trust.

### Domain lists

Domain lists can be created using a list of strings, a text file stored in Amazon S3 or a local
text file:

```python
block_list = route53resolver.FirewallDomainList(self, "BlockList",
    domains=route53resolver.FirewallDomains.from_list(["bad-domain.com", "bot-domain.net"])
)

s3_list = route53resolver.FirewallDomainList(self, "S3List",
    domains=route53resolver.FirewallDomains.from_s3_url("s3://bucket/prefix/object")
)

asset_list = route53resolver.FirewallDomainList(self, "AssetList",
    domains=route53resolver.FirewallDomains.from_asset("/path/to/domains.txt")
)
```

The file must be a text file and must contain a single domain per line.

Use `FirewallDomainList.fromFirewallDomainListId()` to import an existing or [AWS managed domain list](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver-dns-firewall-managed-domain-lists.html):

```python
# AWSManagedDomainsMalwareDomainList in us-east-1
malware_list = route53resolver.FirewallDomainList.from_firewall_domain_list_id(self, "Malware", "rslvr-fdl-2c46f2ecbfec4dcc")
```

### Rule group

Create a rule group:

```python
# my_block_list: route53resolver.FirewallDomainList

route53resolver.FirewallRuleGroup(self, "RuleGroup",
    rules=[route53resolver.FirewallRule(
        priority=10,
        firewall_domain_list=my_block_list,
        # block and reply with NODATA
        action=route53resolver.FirewallRuleAction.block()
    )
    ]
)
```

Rules can be added at construction time or using `addRule()`:

```python
# my_block_list: route53resolver.FirewallDomainList
# rule_group: route53resolver.FirewallRuleGroup


rule_group.add_rule(
    priority=10,
    firewall_domain_list=my_block_list,
    # block and reply with NXDOMAIN
    action=route53resolver.FirewallRuleAction.block(route53resolver.DnsBlockResponse.nx_domain())
)

rule_group.add_rule(
    priority=20,
    firewall_domain_list=my_block_list,
    # block and override DNS response with a custom domain
    action=route53resolver.FirewallRuleAction.block(route53resolver.DnsBlockResponse.override("amazon.com"))
)
```

Use `associate()` to associate a rule group with a VPC:

```python
import aws_cdk.aws_ec2 as ec2

# rule_group: route53resolver.FirewallRuleGroup
# my_vpc: ec2.Vpc


rule_group.associate("Association",
    priority=101,
    vpc=my_vpc
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
import aws_cdk.aws_ec2
import aws_cdk.aws_s3
import constructs


class DnsBlockResponse(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-route53resolver-alpha.DnsBlockResponse",
):
    '''(experimental) The way that you want DNS Firewall to block the request.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # my_block_list: route53resolver.FirewallDomainList
        # rule_group: route53resolver.FirewallRuleGroup
        
        
        rule_group.add_rule(
            priority=10,
            firewall_domain_list=my_block_list,
            # block and reply with NXDOMAIN
            action=route53resolver.FirewallRuleAction.block(route53resolver.DnsBlockResponse.nx_domain())
        )
        
        rule_group.add_rule(
            priority=20,
            firewall_domain_list=my_block_list,
            # block and override DNS response with a custom domain
            action=route53resolver.FirewallRuleAction.block(route53resolver.DnsBlockResponse.override("amazon.com"))
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="noData") # type: ignore[misc]
    @builtins.classmethod
    def no_data(cls) -> "DnsBlockResponse":
        '''(experimental) Respond indicating that the query was successful, but no response is available for it.

        :stability: experimental
        '''
        return typing.cast("DnsBlockResponse", jsii.sinvoke(cls, "noData", []))

    @jsii.member(jsii_name="nxDomain") # type: ignore[misc]
    @builtins.classmethod
    def nx_domain(cls) -> "DnsBlockResponse":
        '''(experimental) Respond indicating that the domain name that's in the query doesn't exist.

        :stability: experimental
        '''
        return typing.cast("DnsBlockResponse", jsii.sinvoke(cls, "nxDomain", []))

    @jsii.member(jsii_name="override") # type: ignore[misc]
    @builtins.classmethod
    def override(
        cls,
        domain: builtins.str,
        ttl: typing.Optional[aws_cdk.Duration] = None,
    ) -> "DnsBlockResponse":
        '''(experimental) Provides a custom override response to the query.

        :param domain: The custom DNS record to send back in response to the query.
        :param ttl: The recommended amount of time for the DNS resolver or web browser to cache the provided override record.

        :stability: experimental
        '''
        return typing.cast("DnsBlockResponse", jsii.sinvoke(cls, "override", [domain, ttl]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockOverrideDnsType")
    @abc.abstractmethod
    def block_override_dns_type(self) -> typing.Optional[builtins.str]:
        '''(experimental) The DNS record's type.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockOverrideDomain")
    @abc.abstractmethod
    def block_override_domain(self) -> typing.Optional[builtins.str]:
        '''(experimental) The custom DNS record to send back in response to the query.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockOverrideTtl")
    @abc.abstractmethod
    def block_override_ttl(self) -> typing.Optional[aws_cdk.Duration]:
        '''(experimental) The recommended amount of time for the DNS resolver or web browser to cache the provided override record.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockResponse")
    @abc.abstractmethod
    def block_response(self) -> typing.Optional[builtins.str]:
        '''(experimental) The way that you want DNS Firewall to block the request.

        :stability: experimental
        '''
        ...


class _DnsBlockResponseProxy(DnsBlockResponse):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockOverrideDnsType")
    def block_override_dns_type(self) -> typing.Optional[builtins.str]:
        '''(experimental) The DNS record's type.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "blockOverrideDnsType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockOverrideDomain")
    def block_override_domain(self) -> typing.Optional[builtins.str]:
        '''(experimental) The custom DNS record to send back in response to the query.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "blockOverrideDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockOverrideTtl")
    def block_override_ttl(self) -> typing.Optional[aws_cdk.Duration]:
        '''(experimental) The recommended amount of time for the DNS resolver or web browser to cache the provided override record.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.Duration], jsii.get(self, "blockOverrideTtl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockResponse")
    def block_response(self) -> typing.Optional[builtins.str]:
        '''(experimental) The way that you want DNS Firewall to block the request.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "blockResponse"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, DnsBlockResponse).__jsii_proxy_class__ = lambda : _DnsBlockResponseProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver-alpha.DomainsConfig",
    jsii_struct_bases=[],
    name_mapping={"domain_file_url": "domainFileUrl", "domains": "domains"},
)
class DomainsConfig:
    def __init__(
        self,
        *,
        domain_file_url: typing.Optional[builtins.str] = None,
        domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Domains configuration.

        :param domain_file_url: (experimental) The fully qualified URL or URI of the file stored in Amazon S3 that contains the list of domains to import. The file must be a text file and must contain a single domain per line. The content type of the S3 object must be ``plain/text``. Default: - use ``domains``
        :param domains: (experimental) A list of domains. Default: - use ``domainFileUrl``

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_route53resolver_alpha as route53resolver_alpha
            
            domains_config = route53resolver_alpha.DomainsConfig(
                domain_file_url="domainFileUrl",
                domains=["domains"]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if domain_file_url is not None:
            self._values["domain_file_url"] = domain_file_url
        if domains is not None:
            self._values["domains"] = domains

    @builtins.property
    def domain_file_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The fully qualified URL or URI of the file stored in Amazon S3 that contains the list of domains to import.

        The file must be a text file and must contain
        a single domain per line. The content type of the S3 object must be ``plain/text``.

        :default: - use ``domains``

        :stability: experimental
        '''
        result = self._values.get("domain_file_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of domains.

        :default: - use ``domainFileUrl``

        :stability: experimental
        '''
        result = self._values.get("domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver-alpha.FirewallDomainListProps",
    jsii_struct_bases=[],
    name_mapping={"domains": "domains", "name": "name"},
)
class FirewallDomainListProps:
    def __init__(
        self,
        *,
        domains: "FirewallDomains",
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a Firewall Domain List.

        :param domains: (experimental) A list of domains.
        :param name: (experimental) A name for the domain list. Default: - a CloudFormation generated name

        :stability: experimental
        :exampleMetadata: infused

        Example::

            block_list = route53resolver.FirewallDomainList(self, "BlockList",
                domains=route53resolver.FirewallDomains.from_list(["bad-domain.com", "bot-domain.net"])
            )
            
            s3_list = route53resolver.FirewallDomainList(self, "S3List",
                domains=route53resolver.FirewallDomains.from_s3_url("s3://bucket/prefix/object")
            )
            
            asset_list = route53resolver.FirewallDomainList(self, "AssetList",
                domains=route53resolver.FirewallDomains.from_asset("/path/to/domains.txt")
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domains": domains,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def domains(self) -> "FirewallDomains":
        '''(experimental) A list of domains.

        :stability: experimental
        '''
        result = self._values.get("domains")
        assert result is not None, "Required property 'domains' is missing"
        return typing.cast("FirewallDomains", result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the domain list.

        :default: - a CloudFormation generated name

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirewallDomainListProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FirewallDomains(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-route53resolver-alpha.FirewallDomains",
):
    '''(experimental) A list of domains.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        block_list = route53resolver.FirewallDomainList(self, "BlockList",
            domains=route53resolver.FirewallDomains.from_list(["bad-domain.com", "bot-domain.net"])
        )
        
        s3_list = route53resolver.FirewallDomainList(self, "S3List",
            domains=route53resolver.FirewallDomains.from_s3_url("s3://bucket/prefix/object")
        )
        
        asset_list = route53resolver.FirewallDomainList(self, "AssetList",
            domains=route53resolver.FirewallDomains.from_asset("/path/to/domains.txt")
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromAsset") # type: ignore[misc]
    @builtins.classmethod
    def from_asset(cls, asset_path: builtins.str) -> "FirewallDomains":
        '''(experimental) Firewall domains created from a local disk path to a text file.

        The file must be a text file (``.txt`` extension) and must contain a single
        domain per line. It will be uploaded to S3.

        :param asset_path: path to the text file.

        :stability: experimental
        '''
        return typing.cast("FirewallDomains", jsii.sinvoke(cls, "fromAsset", [asset_path]))

    @jsii.member(jsii_name="fromList") # type: ignore[misc]
    @builtins.classmethod
    def from_list(cls, list: typing.Sequence[builtins.str]) -> "FirewallDomains":
        '''(experimental) Firewall domains created from a list of domains.

        :param list: the list of domains.

        :stability: experimental
        '''
        return typing.cast("FirewallDomains", jsii.sinvoke(cls, "fromList", [list]))

    @jsii.member(jsii_name="fromS3") # type: ignore[misc]
    @builtins.classmethod
    def from_s3(
        cls,
        bucket: aws_cdk.aws_s3.IBucket,
        key: builtins.str,
    ) -> "FirewallDomains":
        '''(experimental) Firewall domains created from a file stored in Amazon S3.

        The file must be a text file and must contain a single domain per line.
        The content type of the S3 object must be ``plain/text``.

        :param bucket: S3 bucket.
        :param key: S3 key.

        :stability: experimental
        '''
        return typing.cast("FirewallDomains", jsii.sinvoke(cls, "fromS3", [bucket, key]))

    @jsii.member(jsii_name="fromS3Url") # type: ignore[misc]
    @builtins.classmethod
    def from_s3_url(cls, url: builtins.str) -> "FirewallDomains":
        '''(experimental) Firewall domains created from the URL of a file stored in Amazon S3.

        The file must be a text file and must contain a single domain per line.
        The content type of the S3 object must be ``plain/text``.

        :param url: S3 bucket url (s3://bucket/prefix/objet).

        :stability: experimental
        '''
        return typing.cast("FirewallDomains", jsii.sinvoke(cls, "fromS3Url", [url]))

    @jsii.member(jsii_name="bind") # type: ignore[misc]
    @abc.abstractmethod
    def bind(self, scope: constructs.Construct) -> DomainsConfig:
        '''(experimental) Binds the domains to a domain list.

        :param scope: -

        :stability: experimental
        '''
        ...


class _FirewallDomainsProxy(FirewallDomains):
    @jsii.member(jsii_name="bind")
    def bind(self, scope: constructs.Construct) -> DomainsConfig:
        '''(experimental) Binds the domains to a domain list.

        :param scope: -

        :stability: experimental
        '''
        return typing.cast(DomainsConfig, jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, FirewallDomains).__jsii_proxy_class__ = lambda : _FirewallDomainsProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver-alpha.FirewallRule",
    jsii_struct_bases=[],
    name_mapping={
        "action": "action",
        "firewall_domain_list": "firewallDomainList",
        "priority": "priority",
    },
)
class FirewallRule:
    def __init__(
        self,
        *,
        action: "FirewallRuleAction",
        firewall_domain_list: "IFirewallDomainList",
        priority: jsii.Number,
    ) -> None:
        '''(experimental) A Firewall Rule.

        :param action: (experimental) The action for this rule.
        :param firewall_domain_list: (experimental) The domain list for this rule.
        :param priority: (experimental) The priority of the rule in the rule group. This value must be unique within the rule group.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # my_block_list: route53resolver.FirewallDomainList
            # rule_group: route53resolver.FirewallRuleGroup
            
            
            rule_group.add_rule(
                priority=10,
                firewall_domain_list=my_block_list,
                # block and reply with NXDOMAIN
                action=route53resolver.FirewallRuleAction.block(route53resolver.DnsBlockResponse.nx_domain())
            )
            
            rule_group.add_rule(
                priority=20,
                firewall_domain_list=my_block_list,
                # block and override DNS response with a custom domain
                action=route53resolver.FirewallRuleAction.block(route53resolver.DnsBlockResponse.override("amazon.com"))
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
            "firewall_domain_list": firewall_domain_list,
            "priority": priority,
        }

    @builtins.property
    def action(self) -> "FirewallRuleAction":
        '''(experimental) The action for this rule.

        :stability: experimental
        '''
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast("FirewallRuleAction", result)

    @builtins.property
    def firewall_domain_list(self) -> "IFirewallDomainList":
        '''(experimental) The domain list for this rule.

        :stability: experimental
        '''
        result = self._values.get("firewall_domain_list")
        assert result is not None, "Required property 'firewall_domain_list' is missing"
        return typing.cast("IFirewallDomainList", result)

    @builtins.property
    def priority(self) -> jsii.Number:
        '''(experimental) The priority of the rule in the rule group.

        This value must be unique within
        the rule group.

        :stability: experimental
        '''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirewallRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FirewallRuleAction(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-route53resolver-alpha.FirewallRuleAction",
):
    '''(experimental) A Firewall Rule.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # my_block_list: route53resolver.FirewallDomainList
        
        route53resolver.FirewallRuleGroup(self, "RuleGroup",
            rules=[route53resolver.FirewallRule(
                priority=10,
                firewall_domain_list=my_block_list,
                # block and reply with NODATA
                action=route53resolver.FirewallRuleAction.block()
            )
            ]
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="alert") # type: ignore[misc]
    @builtins.classmethod
    def alert(cls) -> "FirewallRuleAction":
        '''(experimental) Permit the request to go through but send an alert to the logs.

        :stability: experimental
        '''
        return typing.cast("FirewallRuleAction", jsii.sinvoke(cls, "alert", []))

    @jsii.member(jsii_name="allow") # type: ignore[misc]
    @builtins.classmethod
    def allow(cls) -> "FirewallRuleAction":
        '''(experimental) Permit the request to go through.

        :stability: experimental
        '''
        return typing.cast("FirewallRuleAction", jsii.sinvoke(cls, "allow", []))

    @jsii.member(jsii_name="block") # type: ignore[misc]
    @builtins.classmethod
    def block(
        cls,
        response: typing.Optional[DnsBlockResponse] = None,
    ) -> "FirewallRuleAction":
        '''(experimental) Disallow the request.

        :param response: The way that you want DNS Firewall to block the request.

        :stability: experimental
        '''
        return typing.cast("FirewallRuleAction", jsii.sinvoke(cls, "block", [response]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    @abc.abstractmethod
    def action(self) -> builtins.str:
        '''(experimental) The action that DNS Firewall should take on a DNS query when it matches one of the domains in the rule's domain list.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockResponse")
    @abc.abstractmethod
    def block_response(self) -> typing.Optional[DnsBlockResponse]:
        '''(experimental) The way that you want DNS Firewall to block the request.

        :stability: experimental
        '''
        ...


class _FirewallRuleActionProxy(FirewallRuleAction):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        '''(experimental) The action that DNS Firewall should take on a DNS query when it matches one of the domains in the rule's domain list.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blockResponse")
    def block_response(self) -> typing.Optional[DnsBlockResponse]:
        '''(experimental) The way that you want DNS Firewall to block the request.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[DnsBlockResponse], jsii.get(self, "blockResponse"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, FirewallRuleAction).__jsii_proxy_class__ = lambda : _FirewallRuleActionProxy


class FirewallRuleGroupAssociation(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver-alpha.FirewallRuleGroupAssociation",
):
    '''(experimental) A Firewall Rule Group Association.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_route53resolver_alpha as route53resolver_alpha
        from aws_cdk import aws_ec2 as ec2
        
        # firewall_rule_group: route53resolver_alpha.FirewallRuleGroup
        # vpc: ec2.Vpc
        
        firewall_rule_group_association = route53resolver_alpha.FirewallRuleGroupAssociation(self, "MyFirewallRuleGroupAssociation",
            firewall_rule_group=firewall_rule_group,
            priority=123,
            vpc=vpc,
        
            # the properties below are optional
            mutation_protection=False,
            name="name"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        firewall_rule_group: "IFirewallRuleGroup",
        priority: jsii.Number,
        vpc: aws_cdk.aws_ec2.IVpc,
        mutation_protection: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param firewall_rule_group: (experimental) The firewall rule group which must be associated.
        :param priority: (experimental) The setting that determines the processing order of the rule group among the rule groups that are associated with a single VPC. DNS Firewall filters VPC traffic starting from rule group with the lowest numeric priority setting. This value must be greater than 100 and less than 9,000
        :param vpc: (experimental) The VPC that to associate with the rule group.
        :param mutation_protection: (experimental) If enabled, this setting disallows modification or removal of the association, to help prevent against accidentally altering DNS firewall protections. Default: true
        :param name: (experimental) The name of the association. Default: - a CloudFormation generated name

        :stability: experimental
        '''
        props = FirewallRuleGroupAssociationProps(
            firewall_rule_group=firewall_rule_group,
            priority=priority,
            vpc=vpc,
            mutation_protection=mutation_protection,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupAssociationArn")
    def firewall_rule_group_association_arn(self) -> builtins.str:
        '''(experimental) The ARN (Amazon Resource Name) of the association.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupAssociationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupAssociationCreationTime")
    def firewall_rule_group_association_creation_time(self) -> builtins.str:
        '''(experimental) The date and time that the association was created.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupAssociationCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupAssociationCreatorRequestId")
    def firewall_rule_group_association_creator_request_id(self) -> builtins.str:
        '''(experimental) The creator request ID.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupAssociationCreatorRequestId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupAssociationId")
    def firewall_rule_group_association_id(self) -> builtins.str:
        '''(experimental) The ID of the association.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupAssociationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupAssociationManagedOwnerName")
    def firewall_rule_group_association_managed_owner_name(self) -> builtins.str:
        '''(experimental) The owner of the association, used only for lists that are not managed by you.

        If you use AWS Firewall Manager to manage your firewallls from DNS Firewall,
        then this reports Firewall Manager as the managed owner.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupAssociationManagedOwnerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupAssociationModificationTime")
    def firewall_rule_group_association_modification_time(self) -> builtins.str:
        '''(experimental) The date and time that the association was last modified.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupAssociationModificationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupAssociationStatus")
    def firewall_rule_group_association_status(self) -> builtins.str:
        '''(experimental) The status of the association.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupAssociationStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupAssociationStatusMessage")
    def firewall_rule_group_association_status_message(self) -> builtins.str:
        '''(experimental) Additional information about the status of the association.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupAssociationStatusMessage"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver-alpha.FirewallRuleGroupAssociationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "priority": "priority",
        "vpc": "vpc",
        "mutation_protection": "mutationProtection",
        "name": "name",
    },
)
class FirewallRuleGroupAssociationOptions:
    def __init__(
        self,
        *,
        priority: jsii.Number,
        vpc: aws_cdk.aws_ec2.IVpc,
        mutation_protection: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for a Firewall Rule Group Association.

        :param priority: (experimental) The setting that determines the processing order of the rule group among the rule groups that are associated with a single VPC. DNS Firewall filters VPC traffic starting from rule group with the lowest numeric priority setting. This value must be greater than 100 and less than 9,000
        :param vpc: (experimental) The VPC that to associate with the rule group.
        :param mutation_protection: (experimental) If enabled, this setting disallows modification or removal of the association, to help prevent against accidentally altering DNS firewall protections. Default: true
        :param name: (experimental) The name of the association. Default: - a CloudFormation generated name

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_ec2 as ec2
            
            # rule_group: route53resolver.FirewallRuleGroup
            # my_vpc: ec2.Vpc
            
            
            rule_group.associate("Association",
                priority=101,
                vpc=my_vpc
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "priority": priority,
            "vpc": vpc,
        }
        if mutation_protection is not None:
            self._values["mutation_protection"] = mutation_protection
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def priority(self) -> jsii.Number:
        '''(experimental) The setting that determines the processing order of the rule group among the rule groups that are associated with a single VPC.

        DNS Firewall filters VPC
        traffic starting from rule group with the lowest numeric priority setting.

        This value must be greater than 100 and less than 9,000

        :stability: experimental
        '''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The VPC that to associate with the rule group.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def mutation_protection(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If enabled, this setting disallows modification or removal of the association, to help prevent against accidentally altering DNS firewall protections.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mutation_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the association.

        :default: - a CloudFormation generated name

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirewallRuleGroupAssociationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver-alpha.FirewallRuleGroupAssociationProps",
    jsii_struct_bases=[FirewallRuleGroupAssociationOptions],
    name_mapping={
        "priority": "priority",
        "vpc": "vpc",
        "mutation_protection": "mutationProtection",
        "name": "name",
        "firewall_rule_group": "firewallRuleGroup",
    },
)
class FirewallRuleGroupAssociationProps(FirewallRuleGroupAssociationOptions):
    def __init__(
        self,
        *,
        priority: jsii.Number,
        vpc: aws_cdk.aws_ec2.IVpc,
        mutation_protection: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
        firewall_rule_group: "IFirewallRuleGroup",
    ) -> None:
        '''(experimental) Properties for a Firewall Rule Group Association.

        :param priority: (experimental) The setting that determines the processing order of the rule group among the rule groups that are associated with a single VPC. DNS Firewall filters VPC traffic starting from rule group with the lowest numeric priority setting. This value must be greater than 100 and less than 9,000
        :param vpc: (experimental) The VPC that to associate with the rule group.
        :param mutation_protection: (experimental) If enabled, this setting disallows modification or removal of the association, to help prevent against accidentally altering DNS firewall protections. Default: true
        :param name: (experimental) The name of the association. Default: - a CloudFormation generated name
        :param firewall_rule_group: (experimental) The firewall rule group which must be associated.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_route53resolver_alpha as route53resolver_alpha
            from aws_cdk import aws_ec2 as ec2
            
            # firewall_rule_group: route53resolver_alpha.FirewallRuleGroup
            # vpc: ec2.Vpc
            
            firewall_rule_group_association_props = route53resolver_alpha.FirewallRuleGroupAssociationProps(
                firewall_rule_group=firewall_rule_group,
                priority=123,
                vpc=vpc,
            
                # the properties below are optional
                mutation_protection=False,
                name="name"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "priority": priority,
            "vpc": vpc,
            "firewall_rule_group": firewall_rule_group,
        }
        if mutation_protection is not None:
            self._values["mutation_protection"] = mutation_protection
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def priority(self) -> jsii.Number:
        '''(experimental) The setting that determines the processing order of the rule group among the rule groups that are associated with a single VPC.

        DNS Firewall filters VPC
        traffic starting from rule group with the lowest numeric priority setting.

        This value must be greater than 100 and less than 9,000

        :stability: experimental
        '''
        result = self._values.get("priority")
        assert result is not None, "Required property 'priority' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) The VPC that to associate with the rule group.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def mutation_protection(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If enabled, this setting disallows modification or removal of the association, to help prevent against accidentally altering DNS firewall protections.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mutation_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the association.

        :default: - a CloudFormation generated name

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def firewall_rule_group(self) -> "IFirewallRuleGroup":
        '''(experimental) The firewall rule group which must be associated.

        :stability: experimental
        '''
        result = self._values.get("firewall_rule_group")
        assert result is not None, "Required property 'firewall_rule_group' is missing"
        return typing.cast("IFirewallRuleGroup", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirewallRuleGroupAssociationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-route53resolver-alpha.FirewallRuleGroupProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "rules": "rules"},
)
class FirewallRuleGroupProps:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Sequence[FirewallRule]] = None,
    ) -> None:
        '''(experimental) Properties for a Firewall Rule Group.

        :param name: (experimental) The name of the rule group. Default: - a CloudFormation generated name
        :param rules: (experimental) A list of rules for this group. Default: - no rules

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # my_block_list: route53resolver.FirewallDomainList
            
            route53resolver.FirewallRuleGroup(self, "RuleGroup",
                rules=[route53resolver.FirewallRule(
                    priority=10,
                    firewall_domain_list=my_block_list,
                    # block and reply with NODATA
                    action=route53resolver.FirewallRuleAction.block()
                )
                ]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if rules is not None:
            self._values["rules"] = rules

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the rule group.

        :default: - a CloudFormation generated name

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rules(self) -> typing.Optional[typing.List[FirewallRule]]:
        '''(experimental) A list of rules for this group.

        :default: - no rules

        :stability: experimental
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.List[FirewallRule]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FirewallRuleGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-route53resolver-alpha.IFirewallDomainList")
class IFirewallDomainList(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) A Firewall Domain List.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListId")
    def firewall_domain_list_id(self) -> builtins.str:
        '''(experimental) The ID of the domain list.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IFirewallDomainListProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) A Firewall Domain List.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-route53resolver-alpha.IFirewallDomainList"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListId")
    def firewall_domain_list_id(self) -> builtins.str:
        '''(experimental) The ID of the domain list.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallDomainListId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFirewallDomainList).__jsii_proxy_class__ = lambda : _IFirewallDomainListProxy


@jsii.interface(jsii_type="@aws-cdk/aws-route53resolver-alpha.IFirewallRuleGroup")
class IFirewallRuleGroup(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) A Firewall Rule Group.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupId")
    def firewall_rule_group_id(self) -> builtins.str:
        '''(experimental) The ID of the rule group.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IFirewallRuleGroupProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) A Firewall Rule Group.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-route53resolver-alpha.IFirewallRuleGroup"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupId")
    def firewall_rule_group_id(self) -> builtins.str:
        '''(experimental) The ID of the rule group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFirewallRuleGroup).__jsii_proxy_class__ = lambda : _IFirewallRuleGroupProxy


@jsii.implements(IFirewallDomainList)
class FirewallDomainList(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver-alpha.FirewallDomainList",
):
    '''(experimental) A Firewall Domain List.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        block_list = route53resolver.FirewallDomainList(self, "BlockList",
            domains=route53resolver.FirewallDomains.from_list(["bad-domain.com", "bot-domain.net"])
        )
        
        s3_list = route53resolver.FirewallDomainList(self, "S3List",
            domains=route53resolver.FirewallDomains.from_s3_url("s3://bucket/prefix/object")
        )
        
        asset_list = route53resolver.FirewallDomainList(self, "AssetList",
            domains=route53resolver.FirewallDomains.from_asset("/path/to/domains.txt")
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domains: FirewallDomains,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domains: (experimental) A list of domains.
        :param name: (experimental) A name for the domain list. Default: - a CloudFormation generated name

        :stability: experimental
        '''
        props = FirewallDomainListProps(domains=domains, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromFirewallDomainListId") # type: ignore[misc]
    @builtins.classmethod
    def from_firewall_domain_list_id(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        firewall_domain_list_id: builtins.str,
    ) -> IFirewallDomainList:
        '''(experimental) Import an existing Firewall Rule Group.

        :param scope: -
        :param id: -
        :param firewall_domain_list_id: -

        :stability: experimental
        '''
        return typing.cast(IFirewallDomainList, jsii.sinvoke(cls, "fromFirewallDomainListId", [scope, id, firewall_domain_list_id]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListArn")
    def firewall_domain_list_arn(self) -> builtins.str:
        '''(experimental) The ARN (Amazon Resource Name) of the domain list.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallDomainListArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListCreationTime")
    def firewall_domain_list_creation_time(self) -> builtins.str:
        '''(experimental) The date and time that the domain list was created.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallDomainListCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListCreatorRequestId")
    def firewall_domain_list_creator_request_id(self) -> builtins.str:
        '''(experimental) The creator request ID.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallDomainListCreatorRequestId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListDomainCount")
    def firewall_domain_list_domain_count(self) -> jsii.Number:
        '''(experimental) The number of domains in the list.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(jsii.Number, jsii.get(self, "firewallDomainListDomainCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListId")
    def firewall_domain_list_id(self) -> builtins.str:
        '''(experimental) The ID of the domain list.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallDomainListId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListManagedOwnerName")
    def firewall_domain_list_managed_owner_name(self) -> builtins.str:
        '''(experimental) The owner of the list, used only for lists that are not managed by you.

        For example, the managed domain list ``AWSManagedDomainsMalwareDomainList``
        has the managed owner name ``Route 53 Resolver DNS Firewall``.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallDomainListManagedOwnerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListModificationTime")
    def firewall_domain_list_modification_time(self) -> builtins.str:
        '''(experimental) The date and time that the domain list was last modified.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallDomainListModificationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListStatus")
    def firewall_domain_list_status(self) -> builtins.str:
        '''(experimental) The status of the domain list.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallDomainListStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallDomainListStatusMessage")
    def firewall_domain_list_status_message(self) -> builtins.str:
        '''(experimental) Additional information about the status of the rule group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallDomainListStatusMessage"))


@jsii.implements(IFirewallRuleGroup)
class FirewallRuleGroup(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-route53resolver-alpha.FirewallRuleGroup",
):
    '''(experimental) A Firewall Rule Group.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # my_block_list: route53resolver.FirewallDomainList
        
        route53resolver.FirewallRuleGroup(self, "RuleGroup",
            rules=[route53resolver.FirewallRule(
                priority=10,
                firewall_domain_list=my_block_list,
                # block and reply with NODATA
                action=route53resolver.FirewallRuleAction.block()
            )
            ]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Sequence[FirewallRule]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: (experimental) The name of the rule group. Default: - a CloudFormation generated name
        :param rules: (experimental) A list of rules for this group. Default: - no rules

        :stability: experimental
        '''
        props = FirewallRuleGroupProps(name=name, rules=rules)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromFirewallRuleGroupId") # type: ignore[misc]
    @builtins.classmethod
    def from_firewall_rule_group_id(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        firewall_rule_group_id: builtins.str,
    ) -> IFirewallRuleGroup:
        '''(experimental) Import an existing Firewall Rule Group.

        :param scope: -
        :param id: -
        :param firewall_rule_group_id: -

        :stability: experimental
        '''
        return typing.cast(IFirewallRuleGroup, jsii.sinvoke(cls, "fromFirewallRuleGroupId", [scope, id, firewall_rule_group_id]))

    @jsii.member(jsii_name="addRule")
    def add_rule(
        self,
        *,
        action: FirewallRuleAction,
        firewall_domain_list: IFirewallDomainList,
        priority: jsii.Number,
    ) -> "FirewallRuleGroup":
        '''(experimental) Adds a rule to this group.

        :param action: (experimental) The action for this rule.
        :param firewall_domain_list: (experimental) The domain list for this rule.
        :param priority: (experimental) The priority of the rule in the rule group. This value must be unique within the rule group.

        :stability: experimental
        '''
        rule = FirewallRule(
            action=action, firewall_domain_list=firewall_domain_list, priority=priority
        )

        return typing.cast("FirewallRuleGroup", jsii.invoke(self, "addRule", [rule]))

    @jsii.member(jsii_name="associate")
    def associate(
        self,
        id: builtins.str,
        *,
        priority: jsii.Number,
        vpc: aws_cdk.aws_ec2.IVpc,
        mutation_protection: typing.Optional[builtins.bool] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> FirewallRuleGroupAssociation:
        '''(experimental) Associates this Firewall Rule Group with a VPC.

        :param id: -
        :param priority: (experimental) The setting that determines the processing order of the rule group among the rule groups that are associated with a single VPC. DNS Firewall filters VPC traffic starting from rule group with the lowest numeric priority setting. This value must be greater than 100 and less than 9,000
        :param vpc: (experimental) The VPC that to associate with the rule group.
        :param mutation_protection: (experimental) If enabled, this setting disallows modification or removal of the association, to help prevent against accidentally altering DNS firewall protections. Default: true
        :param name: (experimental) The name of the association. Default: - a CloudFormation generated name

        :stability: experimental
        '''
        props = FirewallRuleGroupAssociationOptions(
            priority=priority,
            vpc=vpc,
            mutation_protection=mutation_protection,
            name=name,
        )

        return typing.cast(FirewallRuleGroupAssociation, jsii.invoke(self, "associate", [id, props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupArn")
    def firewall_rule_group_arn(self) -> builtins.str:
        '''(experimental) The ARN (Amazon Resource Name) of the rule group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupCreationTime")
    def firewall_rule_group_creation_time(self) -> builtins.str:
        '''(experimental) The date and time that the rule group was created.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupCreationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupCreatorRequestId")
    def firewall_rule_group_creator_request_id(self) -> builtins.str:
        '''(experimental) The creator request ID.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupCreatorRequestId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupId")
    def firewall_rule_group_id(self) -> builtins.str:
        '''(experimental) The ID of the rule group.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupModificationTime")
    def firewall_rule_group_modification_time(self) -> builtins.str:
        '''(experimental) The date and time that the rule group was last modified.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupModificationTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupOwnerId")
    def firewall_rule_group_owner_id(self) -> builtins.str:
        '''(experimental) The AWS account ID for the account that created the rule group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupOwnerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupRuleCount")
    def firewall_rule_group_rule_count(self) -> jsii.Number:
        '''(experimental) The number of rules in the rule group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(jsii.Number, jsii.get(self, "firewallRuleGroupRuleCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupShareStatus")
    def firewall_rule_group_share_status(self) -> builtins.str:
        '''(experimental) Whether the rule group is shared with other AWS accounts, or was shared with the current account by another AWS account.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupShareStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupStatus")
    def firewall_rule_group_status(self) -> builtins.str:
        '''(experimental) The status of the rule group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="firewallRuleGroupStatusMessage")
    def firewall_rule_group_status_message(self) -> builtins.str:
        '''(experimental) Additional information about the status of the rule group.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "firewallRuleGroupStatusMessage"))


__all__ = [
    "DnsBlockResponse",
    "DomainsConfig",
    "FirewallDomainList",
    "FirewallDomainListProps",
    "FirewallDomains",
    "FirewallRule",
    "FirewallRuleAction",
    "FirewallRuleGroup",
    "FirewallRuleGroupAssociation",
    "FirewallRuleGroupAssociationOptions",
    "FirewallRuleGroupAssociationProps",
    "FirewallRuleGroupProps",
    "IFirewallDomainList",
    "IFirewallRuleGroup",
]

publication.publish()
