'''
# Terraform CDK tls Provider ~> 3.1

This repo builds and publishes the Terraform tls Provider bindings for [cdktf](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-tls](https://www.npmjs.com/package/@cdktf/provider-tls).

`npm install @cdktf/provider-tls`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-tls](https://pypi.org/project/cdktf-cdktf-provider-tls).

`pipenv install cdktf-cdktf-provider-tls`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Tls](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Tls).

`dotnet add package HashiCorp.Cdktf.Providers.Tls`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-tls](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-tls).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-tls</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform tls Provider version 1:1. In fact, it always tracks `latest` of `~> 3.1` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform tls Provider](https://github.com/terraform-providers/terraform-provider-tls)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform tls Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

## Features / Issues / Bugs

Please report bugs and issues to the [terraform cdk](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### projen

This is mostly based on [projen](https://github.com/eladb/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on projen

There's a custom [project builder](https://github.com/hashicorp/cdktf-provider-project) which encapsulate the common settings for all `cdktf` providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [Repository Manager](https://github.com/hashicorp/cdktf-repository-manager/)
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

import cdktf
import constructs


class CertRequest(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.CertRequest",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/r/cert_request tls_cert_request}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        key_algorithm: builtins.str,
        private_key_pem: builtins.str,
        subject: typing.Sequence["CertRequestSubject"],
        dns_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        uris: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/r/cert_request tls_cert_request} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param key_algorithm: Name of the algorithm to use to generate the certificate's private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#key_algorithm CertRequest#key_algorithm}
        :param private_key_pem: PEM-encoded private key that the certificate will belong to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#private_key_pem CertRequest#private_key_pem}
        :param subject: subject block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#subject CertRequest#subject}
        :param dns_names: List of DNS names to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#dns_names CertRequest#dns_names}
        :param ip_addresses: List of IP addresses to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#ip_addresses CertRequest#ip_addresses}
        :param uris: List of URIs to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#uris CertRequest#uris}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CertRequestConfig(
            key_algorithm=key_algorithm,
            private_key_pem=private_key_pem,
            subject=subject,
            dns_names=dns_names,
            ip_addresses=ip_addresses,
            uris=uris,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDnsNames")
    def reset_dns_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsNames", []))

    @jsii.member(jsii_name="resetIpAddresses")
    def reset_ip_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpAddresses", []))

    @jsii.member(jsii_name="resetUris")
    def reset_uris(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUris", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certRequestPem")
    def cert_request_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certRequestPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsNamesInput")
    def dns_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddressesInput")
    def ip_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipAddressesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyAlgorithmInput")
    def key_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyAlgorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPemInput")
    def private_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subjectInput")
    def subject_input(self) -> typing.Optional[typing.List["CertRequestSubject"]]:
        return typing.cast(typing.Optional[typing.List["CertRequestSubject"]], jsii.get(self, "subjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urisInput")
    def uris_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "urisInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsNames")
    def dns_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsNames"))

    @dns_names.setter
    def dns_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dnsNames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))

    @ip_addresses.setter
    def ip_addresses(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "ipAddresses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyAlgorithm")
    def key_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyAlgorithm"))

    @key_algorithm.setter
    def key_algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "keyAlgorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPem")
    def private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPem"))

    @private_key_pem.setter
    def private_key_pem(self, value: builtins.str) -> None:
        jsii.set(self, "privateKeyPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subject")
    def subject(self) -> typing.List["CertRequestSubject"]:
        return typing.cast(typing.List["CertRequestSubject"], jsii.get(self, "subject"))

    @subject.setter
    def subject(self, value: typing.List["CertRequestSubject"]) -> None:
        jsii.set(self, "subject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uris")
    def uris(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "uris"))

    @uris.setter
    def uris(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "uris", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.CertRequestConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "key_algorithm": "keyAlgorithm",
        "private_key_pem": "privateKeyPem",
        "subject": "subject",
        "dns_names": "dnsNames",
        "ip_addresses": "ipAddresses",
        "uris": "uris",
    },
)
class CertRequestConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        key_algorithm: builtins.str,
        private_key_pem: builtins.str,
        subject: typing.Sequence["CertRequestSubject"],
        dns_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        uris: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param key_algorithm: Name of the algorithm to use to generate the certificate's private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#key_algorithm CertRequest#key_algorithm}
        :param private_key_pem: PEM-encoded private key that the certificate will belong to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#private_key_pem CertRequest#private_key_pem}
        :param subject: subject block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#subject CertRequest#subject}
        :param dns_names: List of DNS names to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#dns_names CertRequest#dns_names}
        :param ip_addresses: List of IP addresses to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#ip_addresses CertRequest#ip_addresses}
        :param uris: List of URIs to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#uris CertRequest#uris}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "key_algorithm": key_algorithm,
            "private_key_pem": private_key_pem,
            "subject": subject,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if dns_names is not None:
            self._values["dns_names"] = dns_names
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if uris is not None:
            self._values["uris"] = uris

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def key_algorithm(self) -> builtins.str:
        '''Name of the algorithm to use to generate the certificate's private key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#key_algorithm CertRequest#key_algorithm}
        '''
        result = self._values.get("key_algorithm")
        assert result is not None, "Required property 'key_algorithm' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key_pem(self) -> builtins.str:
        '''PEM-encoded private key that the certificate will belong to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#private_key_pem CertRequest#private_key_pem}
        '''
        result = self._values.get("private_key_pem")
        assert result is not None, "Required property 'private_key_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subject(self) -> typing.List["CertRequestSubject"]:
        '''subject block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#subject CertRequest#subject}
        '''
        result = self._values.get("subject")
        assert result is not None, "Required property 'subject' is missing"
        return typing.cast(typing.List["CertRequestSubject"], result)

    @builtins.property
    def dns_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of DNS names to use as subjects of the certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#dns_names CertRequest#dns_names}
        '''
        result = self._values.get("dns_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ip_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IP addresses to use as subjects of the certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#ip_addresses CertRequest#ip_addresses}
        '''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def uris(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of URIs to use as subjects of the certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#uris CertRequest#uris}
        '''
        result = self._values.get("uris")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertRequestConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.CertRequestSubject",
    jsii_struct_bases=[],
    name_mapping={
        "common_name": "commonName",
        "country": "country",
        "locality": "locality",
        "organization": "organization",
        "organizational_unit": "organizationalUnit",
        "postal_code": "postalCode",
        "province": "province",
        "serial_number": "serialNumber",
        "street_address": "streetAddress",
    },
)
class CertRequestSubject:
    def __init__(
        self,
        *,
        common_name: typing.Optional[builtins.str] = None,
        country: typing.Optional[builtins.str] = None,
        locality: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        organizational_unit: typing.Optional[builtins.str] = None,
        postal_code: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        serial_number: typing.Optional[builtins.str] = None,
        street_address: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param common_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#common_name CertRequest#common_name}.
        :param country: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#country CertRequest#country}.
        :param locality: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#locality CertRequest#locality}.
        :param organization: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#organization CertRequest#organization}.
        :param organizational_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#organizational_unit CertRequest#organizational_unit}.
        :param postal_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#postal_code CertRequest#postal_code}.
        :param province: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#province CertRequest#province}.
        :param serial_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#serial_number CertRequest#serial_number}.
        :param street_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#street_address CertRequest#street_address}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if common_name is not None:
            self._values["common_name"] = common_name
        if country is not None:
            self._values["country"] = country
        if locality is not None:
            self._values["locality"] = locality
        if organization is not None:
            self._values["organization"] = organization
        if organizational_unit is not None:
            self._values["organizational_unit"] = organizational_unit
        if postal_code is not None:
            self._values["postal_code"] = postal_code
        if province is not None:
            self._values["province"] = province
        if serial_number is not None:
            self._values["serial_number"] = serial_number
        if street_address is not None:
            self._values["street_address"] = street_address

    @builtins.property
    def common_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#common_name CertRequest#common_name}.'''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def country(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#country CertRequest#country}.'''
        result = self._values.get("country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locality(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#locality CertRequest#locality}.'''
        result = self._values.get("locality")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#organization CertRequest#organization}.'''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organizational_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#organizational_unit CertRequest#organizational_unit}.'''
        result = self._values.get("organizational_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postal_code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#postal_code CertRequest#postal_code}.'''
        result = self._values.get("postal_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def province(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#province CertRequest#province}.'''
        result = self._values.get("province")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def serial_number(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#serial_number CertRequest#serial_number}.'''
        result = self._values.get("serial_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def street_address(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#street_address CertRequest#street_address}.'''
        result = self._values.get("street_address")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertRequestSubject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataTlsCertificate(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.DataTlsCertificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/d/certificate tls_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        url: builtins.str,
        verify_chain: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/d/certificate tls_certificate} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#url DataTlsCertificate#url}.
        :param verify_chain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#verify_chain DataTlsCertificate#verify_chain}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataTlsCertificateConfig(
            url=url,
            verify_chain=verify_chain,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="certificates")
    def certificates(self, index: builtins.str) -> "DataTlsCertificateCertificates":
        '''
        :param index: -
        '''
        return typing.cast("DataTlsCertificateCertificates", jsii.invoke(self, "certificates", [index]))

    @jsii.member(jsii_name="resetVerifyChain")
    def reset_verify_chain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerifyChain", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifyChainInput")
    def verify_chain_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "verifyChainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        jsii.set(self, "url", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifyChain")
    def verify_chain(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "verifyChain"))

    @verify_chain.setter
    def verify_chain(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "verifyChain", value)


class DataTlsCertificateCertificates(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.DataTlsCertificateCertificates",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isCa")
    def is_ca(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "isCa"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="issuer")
    def issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notAfter")
    def not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notAfter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notBefore")
    def not_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notBefore"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyAlgorithm")
    def public_key_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyAlgorithm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serialNumber")
    def serial_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serialNumber"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sha1Fingerprint")
    def sha1_fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha1Fingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signatureAlgorithm")
    def signature_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signatureAlgorithm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subject")
    def subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.DataTlsCertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "url": "url",
        "verify_chain": "verifyChain",
    },
)
class DataTlsCertificateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        url: builtins.str,
        verify_chain: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#url DataTlsCertificate#url}.
        :param verify_chain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#verify_chain DataTlsCertificate#verify_chain}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "url": url,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if verify_chain is not None:
            self._values["verify_chain"] = verify_chain

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#url DataTlsCertificate#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def verify_chain(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#verify_chain DataTlsCertificate#verify_chain}.'''
        result = self._values.get("verify_chain")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataTlsCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataTlsPublicKey(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.DataTlsPublicKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/d/public_key tls_public_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        private_key_pem: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/d/public_key tls_public_key} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param private_key_pem: PEM formatted string to use as the private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/public_key#private_key_pem DataTlsPublicKey#private_key_pem}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataTlsPublicKeyConfig(
            private_key_pem=private_key_pem,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyFingerprintMd5")
    def public_key_fingerprint_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyFingerprintMd5"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyOpenssh")
    def public_key_openssh(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyOpenssh"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyPem")
    def public_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPemInput")
    def private_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPem")
    def private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPem"))

    @private_key_pem.setter
    def private_key_pem(self, value: builtins.str) -> None:
        jsii.set(self, "privateKeyPem", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.DataTlsPublicKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "private_key_pem": "privateKeyPem",
    },
)
class DataTlsPublicKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        private_key_pem: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param private_key_pem: PEM formatted string to use as the private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/public_key#private_key_pem DataTlsPublicKey#private_key_pem}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "private_key_pem": private_key_pem,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def private_key_pem(self) -> builtins.str:
        '''PEM formatted string to use as the private key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/public_key#private_key_pem DataTlsPublicKey#private_key_pem}
        '''
        result = self._values.get("private_key_pem")
        assert result is not None, "Required property 'private_key_pem' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataTlsPublicKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LocallySignedCert(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.LocallySignedCert",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert tls_locally_signed_cert}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        allowed_uses: typing.Sequence[builtins.str],
        ca_cert_pem: builtins.str,
        ca_key_algorithm: builtins.str,
        ca_private_key_pem: builtins.str,
        cert_request_pem: builtins.str,
        validity_period_hours: jsii.Number,
        early_renewal_hours: typing.Optional[jsii.Number] = None,
        is_ca_certificate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        set_subject_key_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert tls_locally_signed_cert} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param allowed_uses: Uses that are allowed for the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#allowed_uses LocallySignedCert#allowed_uses}
        :param ca_cert_pem: PEM-encoded CA certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_cert_pem LocallySignedCert#ca_cert_pem}
        :param ca_key_algorithm: Name of the algorithm used to generate the certificate's private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_key_algorithm LocallySignedCert#ca_key_algorithm}
        :param ca_private_key_pem: PEM-encoded CA private key used to sign the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_private_key_pem LocallySignedCert#ca_private_key_pem}
        :param cert_request_pem: PEM-encoded certificate request. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#cert_request_pem LocallySignedCert#cert_request_pem}
        :param validity_period_hours: Number of hours that the certificate will remain valid for. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#validity_period_hours LocallySignedCert#validity_period_hours}
        :param early_renewal_hours: Number of hours before the certificates expiry when a new certificate will be generated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#early_renewal_hours LocallySignedCert#early_renewal_hours}
        :param is_ca_certificate: Whether the generated certificate will be usable as a CA certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#is_ca_certificate LocallySignedCert#is_ca_certificate}
        :param set_subject_key_id: If true, the generated certificate will include a subject key identifier. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#set_subject_key_id LocallySignedCert#set_subject_key_id}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LocallySignedCertConfig(
            allowed_uses=allowed_uses,
            ca_cert_pem=ca_cert_pem,
            ca_key_algorithm=ca_key_algorithm,
            ca_private_key_pem=ca_private_key_pem,
            cert_request_pem=cert_request_pem,
            validity_period_hours=validity_period_hours,
            early_renewal_hours=early_renewal_hours,
            is_ca_certificate=is_ca_certificate,
            set_subject_key_id=set_subject_key_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEarlyRenewalHours")
    def reset_early_renewal_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEarlyRenewalHours", []))

    @jsii.member(jsii_name="resetIsCaCertificate")
    def reset_is_ca_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsCaCertificate", []))

    @jsii.member(jsii_name="resetSetSubjectKeyId")
    def reset_set_subject_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetSubjectKeyId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certPem")
    def cert_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readyForRenewal")
    def ready_for_renewal(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "readyForRenewal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityEndTime")
    def validity_end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validityEndTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityStartTime")
    def validity_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validityStartTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedUsesInput")
    def allowed_uses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedUsesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caCertPemInput")
    def ca_cert_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caKeyAlgorithmInput")
    def ca_key_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caKeyAlgorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caPrivateKeyPemInput")
    def ca_private_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPrivateKeyPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certRequestPemInput")
    def cert_request_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certRequestPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyRenewalHoursInput")
    def early_renewal_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "earlyRenewalHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isCaCertificateInput")
    def is_ca_certificate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "isCaCertificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setSubjectKeyIdInput")
    def set_subject_key_id_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "setSubjectKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityPeriodHoursInput")
    def validity_period_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "validityPeriodHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedUses")
    def allowed_uses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedUses"))

    @allowed_uses.setter
    def allowed_uses(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "allowedUses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caCertPem")
    def ca_cert_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caCertPem"))

    @ca_cert_pem.setter
    def ca_cert_pem(self, value: builtins.str) -> None:
        jsii.set(self, "caCertPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caKeyAlgorithm")
    def ca_key_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caKeyAlgorithm"))

    @ca_key_algorithm.setter
    def ca_key_algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "caKeyAlgorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caPrivateKeyPem")
    def ca_private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caPrivateKeyPem"))

    @ca_private_key_pem.setter
    def ca_private_key_pem(self, value: builtins.str) -> None:
        jsii.set(self, "caPrivateKeyPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certRequestPem")
    def cert_request_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certRequestPem"))

    @cert_request_pem.setter
    def cert_request_pem(self, value: builtins.str) -> None:
        jsii.set(self, "certRequestPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyRenewalHours")
    def early_renewal_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "earlyRenewalHours"))

    @early_renewal_hours.setter
    def early_renewal_hours(self, value: jsii.Number) -> None:
        jsii.set(self, "earlyRenewalHours", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isCaCertificate")
    def is_ca_certificate(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "isCaCertificate"))

    @is_ca_certificate.setter
    def is_ca_certificate(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "isCaCertificate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setSubjectKeyId")
    def set_subject_key_id(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "setSubjectKeyId"))

    @set_subject_key_id.setter
    def set_subject_key_id(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "setSubjectKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityPeriodHours")
    def validity_period_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "validityPeriodHours"))

    @validity_period_hours.setter
    def validity_period_hours(self, value: jsii.Number) -> None:
        jsii.set(self, "validityPeriodHours", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.LocallySignedCertConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "allowed_uses": "allowedUses",
        "ca_cert_pem": "caCertPem",
        "ca_key_algorithm": "caKeyAlgorithm",
        "ca_private_key_pem": "caPrivateKeyPem",
        "cert_request_pem": "certRequestPem",
        "validity_period_hours": "validityPeriodHours",
        "early_renewal_hours": "earlyRenewalHours",
        "is_ca_certificate": "isCaCertificate",
        "set_subject_key_id": "setSubjectKeyId",
    },
)
class LocallySignedCertConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        allowed_uses: typing.Sequence[builtins.str],
        ca_cert_pem: builtins.str,
        ca_key_algorithm: builtins.str,
        ca_private_key_pem: builtins.str,
        cert_request_pem: builtins.str,
        validity_period_hours: jsii.Number,
        early_renewal_hours: typing.Optional[jsii.Number] = None,
        is_ca_certificate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        set_subject_key_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param allowed_uses: Uses that are allowed for the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#allowed_uses LocallySignedCert#allowed_uses}
        :param ca_cert_pem: PEM-encoded CA certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_cert_pem LocallySignedCert#ca_cert_pem}
        :param ca_key_algorithm: Name of the algorithm used to generate the certificate's private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_key_algorithm LocallySignedCert#ca_key_algorithm}
        :param ca_private_key_pem: PEM-encoded CA private key used to sign the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_private_key_pem LocallySignedCert#ca_private_key_pem}
        :param cert_request_pem: PEM-encoded certificate request. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#cert_request_pem LocallySignedCert#cert_request_pem}
        :param validity_period_hours: Number of hours that the certificate will remain valid for. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#validity_period_hours LocallySignedCert#validity_period_hours}
        :param early_renewal_hours: Number of hours before the certificates expiry when a new certificate will be generated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#early_renewal_hours LocallySignedCert#early_renewal_hours}
        :param is_ca_certificate: Whether the generated certificate will be usable as a CA certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#is_ca_certificate LocallySignedCert#is_ca_certificate}
        :param set_subject_key_id: If true, the generated certificate will include a subject key identifier. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#set_subject_key_id LocallySignedCert#set_subject_key_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "allowed_uses": allowed_uses,
            "ca_cert_pem": ca_cert_pem,
            "ca_key_algorithm": ca_key_algorithm,
            "ca_private_key_pem": ca_private_key_pem,
            "cert_request_pem": cert_request_pem,
            "validity_period_hours": validity_period_hours,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if early_renewal_hours is not None:
            self._values["early_renewal_hours"] = early_renewal_hours
        if is_ca_certificate is not None:
            self._values["is_ca_certificate"] = is_ca_certificate
        if set_subject_key_id is not None:
            self._values["set_subject_key_id"] = set_subject_key_id

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def allowed_uses(self) -> typing.List[builtins.str]:
        '''Uses that are allowed for the certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#allowed_uses LocallySignedCert#allowed_uses}
        '''
        result = self._values.get("allowed_uses")
        assert result is not None, "Required property 'allowed_uses' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def ca_cert_pem(self) -> builtins.str:
        '''PEM-encoded CA certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_cert_pem LocallySignedCert#ca_cert_pem}
        '''
        result = self._values.get("ca_cert_pem")
        assert result is not None, "Required property 'ca_cert_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ca_key_algorithm(self) -> builtins.str:
        '''Name of the algorithm used to generate the certificate's private key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_key_algorithm LocallySignedCert#ca_key_algorithm}
        '''
        result = self._values.get("ca_key_algorithm")
        assert result is not None, "Required property 'ca_key_algorithm' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ca_private_key_pem(self) -> builtins.str:
        '''PEM-encoded CA private key used to sign the certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_private_key_pem LocallySignedCert#ca_private_key_pem}
        '''
        result = self._values.get("ca_private_key_pem")
        assert result is not None, "Required property 'ca_private_key_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cert_request_pem(self) -> builtins.str:
        '''PEM-encoded certificate request.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#cert_request_pem LocallySignedCert#cert_request_pem}
        '''
        result = self._values.get("cert_request_pem")
        assert result is not None, "Required property 'cert_request_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def validity_period_hours(self) -> jsii.Number:
        '''Number of hours that the certificate will remain valid for.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#validity_period_hours LocallySignedCert#validity_period_hours}
        '''
        result = self._values.get("validity_period_hours")
        assert result is not None, "Required property 'validity_period_hours' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def early_renewal_hours(self) -> typing.Optional[jsii.Number]:
        '''Number of hours before the certificates expiry when a new certificate will be generated.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#early_renewal_hours LocallySignedCert#early_renewal_hours}
        '''
        result = self._values.get("early_renewal_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def is_ca_certificate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether the generated certificate will be usable as a CA certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#is_ca_certificate LocallySignedCert#is_ca_certificate}
        '''
        result = self._values.get("is_ca_certificate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def set_subject_key_id(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If true, the generated certificate will include a subject key identifier.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#set_subject_key_id LocallySignedCert#set_subject_key_id}
        '''
        result = self._values.get("set_subject_key_id")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LocallySignedCertConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PrivateKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.PrivateKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/r/private_key tls_private_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        algorithm: builtins.str,
        ecdsa_curve: typing.Optional[builtins.str] = None,
        rsa_bits: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/r/private_key tls_private_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param algorithm: Name of the algorithm to use to generate the private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#algorithm PrivateKey#algorithm}
        :param ecdsa_curve: ECDSA curve to use when generating a key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#ecdsa_curve PrivateKey#ecdsa_curve}
        :param rsa_bits: Number of bits to use when generating an RSA key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#rsa_bits PrivateKey#rsa_bits}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = PrivateKeyConfig(
            algorithm=algorithm,
            ecdsa_curve=ecdsa_curve,
            rsa_bits=rsa_bits,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEcdsaCurve")
    def reset_ecdsa_curve(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEcdsaCurve", []))

    @jsii.member(jsii_name="resetRsaBits")
    def reset_rsa_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRsaBits", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPem")
    def private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyFingerprintMd5")
    def public_key_fingerprint_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyFingerprintMd5"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyOpenssh")
    def public_key_openssh(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyOpenssh"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyPem")
    def public_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="algorithmInput")
    def algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecdsaCurveInput")
    def ecdsa_curve_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ecdsaCurveInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rsaBitsInput")
    def rsa_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rsaBitsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "algorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecdsaCurve")
    def ecdsa_curve(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ecdsaCurve"))

    @ecdsa_curve.setter
    def ecdsa_curve(self, value: builtins.str) -> None:
        jsii.set(self, "ecdsaCurve", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rsaBits")
    def rsa_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rsaBits"))

    @rsa_bits.setter
    def rsa_bits(self, value: jsii.Number) -> None:
        jsii.set(self, "rsaBits", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.PrivateKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "algorithm": "algorithm",
        "ecdsa_curve": "ecdsaCurve",
        "rsa_bits": "rsaBits",
    },
)
class PrivateKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        algorithm: builtins.str,
        ecdsa_curve: typing.Optional[builtins.str] = None,
        rsa_bits: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param algorithm: Name of the algorithm to use to generate the private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#algorithm PrivateKey#algorithm}
        :param ecdsa_curve: ECDSA curve to use when generating a key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#ecdsa_curve PrivateKey#ecdsa_curve}
        :param rsa_bits: Number of bits to use when generating an RSA key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#rsa_bits PrivateKey#rsa_bits}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "algorithm": algorithm,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if ecdsa_curve is not None:
            self._values["ecdsa_curve"] = ecdsa_curve
        if rsa_bits is not None:
            self._values["rsa_bits"] = rsa_bits

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def algorithm(self) -> builtins.str:
        '''Name of the algorithm to use to generate the private key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#algorithm PrivateKey#algorithm}
        '''
        result = self._values.get("algorithm")
        assert result is not None, "Required property 'algorithm' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ecdsa_curve(self) -> typing.Optional[builtins.str]:
        '''ECDSA curve to use when generating a key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#ecdsa_curve PrivateKey#ecdsa_curve}
        '''
        result = self._values.get("ecdsa_curve")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rsa_bits(self) -> typing.Optional[jsii.Number]:
        '''Number of bits to use when generating an RSA key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#rsa_bits PrivateKey#rsa_bits}
        '''
        result = self._values.get("rsa_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrivateKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SelfSignedCert(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.SelfSignedCert",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert tls_self_signed_cert}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        allowed_uses: typing.Sequence[builtins.str],
        key_algorithm: builtins.str,
        private_key_pem: builtins.str,
        subject: typing.Sequence["SelfSignedCertSubject"],
        validity_period_hours: jsii.Number,
        dns_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        early_renewal_hours: typing.Optional[jsii.Number] = None,
        ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_ca_certificate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        set_subject_key_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        uris: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert tls_self_signed_cert} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param allowed_uses: Uses that are allowed for the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#allowed_uses SelfSignedCert#allowed_uses}
        :param key_algorithm: Name of the algorithm to use to generate the certificate's private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#key_algorithm SelfSignedCert#key_algorithm}
        :param private_key_pem: PEM-encoded private key that the certificate will belong to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#private_key_pem SelfSignedCert#private_key_pem}
        :param subject: subject block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#subject SelfSignedCert#subject}
        :param validity_period_hours: Number of hours that the certificate will remain valid for. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#validity_period_hours SelfSignedCert#validity_period_hours}
        :param dns_names: List of DNS names to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#dns_names SelfSignedCert#dns_names}
        :param early_renewal_hours: Number of hours before the certificates expiry when a new certificate will be generated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#early_renewal_hours SelfSignedCert#early_renewal_hours}
        :param ip_addresses: List of IP addresses to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#ip_addresses SelfSignedCert#ip_addresses}
        :param is_ca_certificate: Whether the generated certificate will be usable as a CA certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#is_ca_certificate SelfSignedCert#is_ca_certificate}
        :param set_subject_key_id: If true, the generated certificate will include a subject key identifier. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#set_subject_key_id SelfSignedCert#set_subject_key_id}
        :param uris: List of URIs to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#uris SelfSignedCert#uris}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SelfSignedCertConfig(
            allowed_uses=allowed_uses,
            key_algorithm=key_algorithm,
            private_key_pem=private_key_pem,
            subject=subject,
            validity_period_hours=validity_period_hours,
            dns_names=dns_names,
            early_renewal_hours=early_renewal_hours,
            ip_addresses=ip_addresses,
            is_ca_certificate=is_ca_certificate,
            set_subject_key_id=set_subject_key_id,
            uris=uris,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDnsNames")
    def reset_dns_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsNames", []))

    @jsii.member(jsii_name="resetEarlyRenewalHours")
    def reset_early_renewal_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEarlyRenewalHours", []))

    @jsii.member(jsii_name="resetIpAddresses")
    def reset_ip_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpAddresses", []))

    @jsii.member(jsii_name="resetIsCaCertificate")
    def reset_is_ca_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsCaCertificate", []))

    @jsii.member(jsii_name="resetSetSubjectKeyId")
    def reset_set_subject_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetSubjectKeyId", []))

    @jsii.member(jsii_name="resetUris")
    def reset_uris(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUris", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certPem")
    def cert_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readyForRenewal")
    def ready_for_renewal(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "readyForRenewal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityEndTime")
    def validity_end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validityEndTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityStartTime")
    def validity_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validityStartTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedUsesInput")
    def allowed_uses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedUsesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsNamesInput")
    def dns_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyRenewalHoursInput")
    def early_renewal_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "earlyRenewalHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddressesInput")
    def ip_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipAddressesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isCaCertificateInput")
    def is_ca_certificate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "isCaCertificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyAlgorithmInput")
    def key_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyAlgorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPemInput")
    def private_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setSubjectKeyIdInput")
    def set_subject_key_id_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "setSubjectKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subjectInput")
    def subject_input(self) -> typing.Optional[typing.List["SelfSignedCertSubject"]]:
        return typing.cast(typing.Optional[typing.List["SelfSignedCertSubject"]], jsii.get(self, "subjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urisInput")
    def uris_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "urisInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityPeriodHoursInput")
    def validity_period_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "validityPeriodHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedUses")
    def allowed_uses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedUses"))

    @allowed_uses.setter
    def allowed_uses(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "allowedUses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsNames")
    def dns_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsNames"))

    @dns_names.setter
    def dns_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dnsNames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyRenewalHours")
    def early_renewal_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "earlyRenewalHours"))

    @early_renewal_hours.setter
    def early_renewal_hours(self, value: jsii.Number) -> None:
        jsii.set(self, "earlyRenewalHours", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))

    @ip_addresses.setter
    def ip_addresses(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "ipAddresses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isCaCertificate")
    def is_ca_certificate(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "isCaCertificate"))

    @is_ca_certificate.setter
    def is_ca_certificate(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "isCaCertificate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyAlgorithm")
    def key_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyAlgorithm"))

    @key_algorithm.setter
    def key_algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "keyAlgorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPem")
    def private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPem"))

    @private_key_pem.setter
    def private_key_pem(self, value: builtins.str) -> None:
        jsii.set(self, "privateKeyPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setSubjectKeyId")
    def set_subject_key_id(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "setSubjectKeyId"))

    @set_subject_key_id.setter
    def set_subject_key_id(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "setSubjectKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subject")
    def subject(self) -> typing.List["SelfSignedCertSubject"]:
        return typing.cast(typing.List["SelfSignedCertSubject"], jsii.get(self, "subject"))

    @subject.setter
    def subject(self, value: typing.List["SelfSignedCertSubject"]) -> None:
        jsii.set(self, "subject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uris")
    def uris(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "uris"))

    @uris.setter
    def uris(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "uris", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityPeriodHours")
    def validity_period_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "validityPeriodHours"))

    @validity_period_hours.setter
    def validity_period_hours(self, value: jsii.Number) -> None:
        jsii.set(self, "validityPeriodHours", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.SelfSignedCertConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "allowed_uses": "allowedUses",
        "key_algorithm": "keyAlgorithm",
        "private_key_pem": "privateKeyPem",
        "subject": "subject",
        "validity_period_hours": "validityPeriodHours",
        "dns_names": "dnsNames",
        "early_renewal_hours": "earlyRenewalHours",
        "ip_addresses": "ipAddresses",
        "is_ca_certificate": "isCaCertificate",
        "set_subject_key_id": "setSubjectKeyId",
        "uris": "uris",
    },
)
class SelfSignedCertConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        allowed_uses: typing.Sequence[builtins.str],
        key_algorithm: builtins.str,
        private_key_pem: builtins.str,
        subject: typing.Sequence["SelfSignedCertSubject"],
        validity_period_hours: jsii.Number,
        dns_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        early_renewal_hours: typing.Optional[jsii.Number] = None,
        ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_ca_certificate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        set_subject_key_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        uris: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param allowed_uses: Uses that are allowed for the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#allowed_uses SelfSignedCert#allowed_uses}
        :param key_algorithm: Name of the algorithm to use to generate the certificate's private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#key_algorithm SelfSignedCert#key_algorithm}
        :param private_key_pem: PEM-encoded private key that the certificate will belong to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#private_key_pem SelfSignedCert#private_key_pem}
        :param subject: subject block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#subject SelfSignedCert#subject}
        :param validity_period_hours: Number of hours that the certificate will remain valid for. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#validity_period_hours SelfSignedCert#validity_period_hours}
        :param dns_names: List of DNS names to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#dns_names SelfSignedCert#dns_names}
        :param early_renewal_hours: Number of hours before the certificates expiry when a new certificate will be generated. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#early_renewal_hours SelfSignedCert#early_renewal_hours}
        :param ip_addresses: List of IP addresses to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#ip_addresses SelfSignedCert#ip_addresses}
        :param is_ca_certificate: Whether the generated certificate will be usable as a CA certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#is_ca_certificate SelfSignedCert#is_ca_certificate}
        :param set_subject_key_id: If true, the generated certificate will include a subject key identifier. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#set_subject_key_id SelfSignedCert#set_subject_key_id}
        :param uris: List of URIs to use as subjects of the certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#uris SelfSignedCert#uris}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "allowed_uses": allowed_uses,
            "key_algorithm": key_algorithm,
            "private_key_pem": private_key_pem,
            "subject": subject,
            "validity_period_hours": validity_period_hours,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if dns_names is not None:
            self._values["dns_names"] = dns_names
        if early_renewal_hours is not None:
            self._values["early_renewal_hours"] = early_renewal_hours
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if is_ca_certificate is not None:
            self._values["is_ca_certificate"] = is_ca_certificate
        if set_subject_key_id is not None:
            self._values["set_subject_key_id"] = set_subject_key_id
        if uris is not None:
            self._values["uris"] = uris

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def allowed_uses(self) -> typing.List[builtins.str]:
        '''Uses that are allowed for the certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#allowed_uses SelfSignedCert#allowed_uses}
        '''
        result = self._values.get("allowed_uses")
        assert result is not None, "Required property 'allowed_uses' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def key_algorithm(self) -> builtins.str:
        '''Name of the algorithm to use to generate the certificate's private key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#key_algorithm SelfSignedCert#key_algorithm}
        '''
        result = self._values.get("key_algorithm")
        assert result is not None, "Required property 'key_algorithm' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key_pem(self) -> builtins.str:
        '''PEM-encoded private key that the certificate will belong to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#private_key_pem SelfSignedCert#private_key_pem}
        '''
        result = self._values.get("private_key_pem")
        assert result is not None, "Required property 'private_key_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subject(self) -> typing.List["SelfSignedCertSubject"]:
        '''subject block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#subject SelfSignedCert#subject}
        '''
        result = self._values.get("subject")
        assert result is not None, "Required property 'subject' is missing"
        return typing.cast(typing.List["SelfSignedCertSubject"], result)

    @builtins.property
    def validity_period_hours(self) -> jsii.Number:
        '''Number of hours that the certificate will remain valid for.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#validity_period_hours SelfSignedCert#validity_period_hours}
        '''
        result = self._values.get("validity_period_hours")
        assert result is not None, "Required property 'validity_period_hours' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def dns_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of DNS names to use as subjects of the certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#dns_names SelfSignedCert#dns_names}
        '''
        result = self._values.get("dns_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def early_renewal_hours(self) -> typing.Optional[jsii.Number]:
        '''Number of hours before the certificates expiry when a new certificate will be generated.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#early_renewal_hours SelfSignedCert#early_renewal_hours}
        '''
        result = self._values.get("early_renewal_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ip_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IP addresses to use as subjects of the certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#ip_addresses SelfSignedCert#ip_addresses}
        '''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def is_ca_certificate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether the generated certificate will be usable as a CA certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#is_ca_certificate SelfSignedCert#is_ca_certificate}
        '''
        result = self._values.get("is_ca_certificate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def set_subject_key_id(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If true, the generated certificate will include a subject key identifier.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#set_subject_key_id SelfSignedCert#set_subject_key_id}
        '''
        result = self._values.get("set_subject_key_id")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def uris(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of URIs to use as subjects of the certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#uris SelfSignedCert#uris}
        '''
        result = self._values.get("uris")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SelfSignedCertConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.SelfSignedCertSubject",
    jsii_struct_bases=[],
    name_mapping={
        "common_name": "commonName",
        "country": "country",
        "locality": "locality",
        "organization": "organization",
        "organizational_unit": "organizationalUnit",
        "postal_code": "postalCode",
        "province": "province",
        "serial_number": "serialNumber",
        "street_address": "streetAddress",
    },
)
class SelfSignedCertSubject:
    def __init__(
        self,
        *,
        common_name: typing.Optional[builtins.str] = None,
        country: typing.Optional[builtins.str] = None,
        locality: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        organizational_unit: typing.Optional[builtins.str] = None,
        postal_code: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        serial_number: typing.Optional[builtins.str] = None,
        street_address: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param common_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#common_name SelfSignedCert#common_name}.
        :param country: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#country SelfSignedCert#country}.
        :param locality: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#locality SelfSignedCert#locality}.
        :param organization: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#organization SelfSignedCert#organization}.
        :param organizational_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#organizational_unit SelfSignedCert#organizational_unit}.
        :param postal_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#postal_code SelfSignedCert#postal_code}.
        :param province: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#province SelfSignedCert#province}.
        :param serial_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#serial_number SelfSignedCert#serial_number}.
        :param street_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#street_address SelfSignedCert#street_address}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if common_name is not None:
            self._values["common_name"] = common_name
        if country is not None:
            self._values["country"] = country
        if locality is not None:
            self._values["locality"] = locality
        if organization is not None:
            self._values["organization"] = organization
        if organizational_unit is not None:
            self._values["organizational_unit"] = organizational_unit
        if postal_code is not None:
            self._values["postal_code"] = postal_code
        if province is not None:
            self._values["province"] = province
        if serial_number is not None:
            self._values["serial_number"] = serial_number
        if street_address is not None:
            self._values["street_address"] = street_address

    @builtins.property
    def common_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#common_name SelfSignedCert#common_name}.'''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def country(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#country SelfSignedCert#country}.'''
        result = self._values.get("country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locality(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#locality SelfSignedCert#locality}.'''
        result = self._values.get("locality")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#organization SelfSignedCert#organization}.'''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organizational_unit(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#organizational_unit SelfSignedCert#organizational_unit}.'''
        result = self._values.get("organizational_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postal_code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#postal_code SelfSignedCert#postal_code}.'''
        result = self._values.get("postal_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def province(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#province SelfSignedCert#province}.'''
        result = self._values.get("province")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def serial_number(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#serial_number SelfSignedCert#serial_number}.'''
        result = self._values.get("serial_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def street_address(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#street_address SelfSignedCert#street_address}.'''
        result = self._values.get("street_address")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SelfSignedCertSubject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TlsProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.TlsProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls tls}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls tls} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls#alias TlsProvider#alias}
        '''
        config = TlsProviderConfig(alias=alias)

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "alias", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.TlsProviderConfig",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias"},
)
class TlsProviderConfig:
    def __init__(self, *, alias: typing.Optional[builtins.str] = None) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls#alias TlsProvider#alias}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls#alias TlsProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TlsProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CertRequest",
    "CertRequestConfig",
    "CertRequestSubject",
    "DataTlsCertificate",
    "DataTlsCertificateCertificates",
    "DataTlsCertificateConfig",
    "DataTlsPublicKey",
    "DataTlsPublicKeyConfig",
    "LocallySignedCert",
    "LocallySignedCertConfig",
    "PrivateKey",
    "PrivateKeyConfig",
    "SelfSignedCert",
    "SelfSignedCertConfig",
    "SelfSignedCertSubject",
    "TlsProvider",
    "TlsProviderConfig",
]

publication.publish()
