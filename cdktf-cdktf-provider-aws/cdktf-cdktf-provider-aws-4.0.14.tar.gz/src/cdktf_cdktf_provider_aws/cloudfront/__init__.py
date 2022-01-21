import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import cdktf
import constructs


class CloudfrontCachePolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy aws_cloudfront_cache_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        parameters_in_cache_key_and_forwarded_to_origin: "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin",
        comment: typing.Optional[builtins.str] = None,
        default_ttl: typing.Optional[jsii.Number] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        min_ttl: typing.Optional[jsii.Number] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy aws_cloudfront_cache_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#name CloudfrontCachePolicy#name}.
        :param parameters_in_cache_key_and_forwarded_to_origin: parameters_in_cache_key_and_forwarded_to_origin block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#parameters_in_cache_key_and_forwarded_to_origin CloudfrontCachePolicy#parameters_in_cache_key_and_forwarded_to_origin}
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#comment CloudfrontCachePolicy#comment}.
        :param default_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#default_ttl CloudfrontCachePolicy#default_ttl}.
        :param max_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#max_ttl CloudfrontCachePolicy#max_ttl}.
        :param min_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#min_ttl CloudfrontCachePolicy#min_ttl}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontCachePolicyConfig(
            name=name,
            parameters_in_cache_key_and_forwarded_to_origin=parameters_in_cache_key_and_forwarded_to_origin,
            comment=comment,
            default_ttl=default_ttl,
            max_ttl=max_ttl,
            min_ttl=min_ttl,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putParametersInCacheKeyAndForwardedToOrigin")
    def put_parameters_in_cache_key_and_forwarded_to_origin(
        self,
        *,
        cookies_config: "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig",
        headers_config: "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig",
        query_strings_config: "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig",
        enable_accept_encoding_brotli: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_accept_encoding_gzip: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param cookies_config: cookies_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#cookies_config CloudfrontCachePolicy#cookies_config}
        :param headers_config: headers_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#headers_config CloudfrontCachePolicy#headers_config}
        :param query_strings_config: query_strings_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#query_strings_config CloudfrontCachePolicy#query_strings_config}
        :param enable_accept_encoding_brotli: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#enable_accept_encoding_brotli CloudfrontCachePolicy#enable_accept_encoding_brotli}.
        :param enable_accept_encoding_gzip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#enable_accept_encoding_gzip CloudfrontCachePolicy#enable_accept_encoding_gzip}.
        '''
        value = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin(
            cookies_config=cookies_config,
            headers_config=headers_config,
            query_strings_config=query_strings_config,
            enable_accept_encoding_brotli=enable_accept_encoding_brotli,
            enable_accept_encoding_gzip=enable_accept_encoding_gzip,
        )

        return typing.cast(None, jsii.invoke(self, "putParametersInCacheKeyAndForwardedToOrigin", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetDefaultTtl")
    def reset_default_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTtl", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetMinTtl")
    def reset_min_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinTtl", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parametersInCacheKeyAndForwardedToOrigin")
    def parameters_in_cache_key_and_forwarded_to_origin(
        self,
    ) -> "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginOutputReference":
        return typing.cast("CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginOutputReference", jsii.get(self, "parametersInCacheKeyAndForwardedToOrigin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTtlInput")
    def default_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultTtlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxTtlInput")
    def max_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTtlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minTtlInput")
    def min_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minTtlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parametersInCacheKeyAndForwardedToOriginInput")
    def parameters_in_cache_key_and_forwarded_to_origin_input(
        self,
    ) -> typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin"]:
        return typing.cast(typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin"], jsii.get(self, "parametersInCacheKeyAndForwardedToOriginInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        jsii.set(self, "comment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTtl")
    def default_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultTtl"))

    @default_ttl.setter
    def default_ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "defaultTtl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "maxTtl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minTtl")
    def min_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minTtl"))

    @min_ttl.setter
    def min_ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "minTtl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "parameters_in_cache_key_and_forwarded_to_origin": "parametersInCacheKeyAndForwardedToOrigin",
        "comment": "comment",
        "default_ttl": "defaultTtl",
        "max_ttl": "maxTtl",
        "min_ttl": "minTtl",
    },
)
class CloudfrontCachePolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        parameters_in_cache_key_and_forwarded_to_origin: "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin",
        comment: typing.Optional[builtins.str] = None,
        default_ttl: typing.Optional[jsii.Number] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        min_ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#name CloudfrontCachePolicy#name}.
        :param parameters_in_cache_key_and_forwarded_to_origin: parameters_in_cache_key_and_forwarded_to_origin block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#parameters_in_cache_key_and_forwarded_to_origin CloudfrontCachePolicy#parameters_in_cache_key_and_forwarded_to_origin}
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#comment CloudfrontCachePolicy#comment}.
        :param default_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#default_ttl CloudfrontCachePolicy#default_ttl}.
        :param max_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#max_ttl CloudfrontCachePolicy#max_ttl}.
        :param min_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#min_ttl CloudfrontCachePolicy#min_ttl}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(parameters_in_cache_key_and_forwarded_to_origin, dict):
            parameters_in_cache_key_and_forwarded_to_origin = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin(**parameters_in_cache_key_and_forwarded_to_origin)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "parameters_in_cache_key_and_forwarded_to_origin": parameters_in_cache_key_and_forwarded_to_origin,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if comment is not None:
            self._values["comment"] = comment
        if default_ttl is not None:
            self._values["default_ttl"] = default_ttl
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if min_ttl is not None:
            self._values["min_ttl"] = min_ttl

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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#name CloudfrontCachePolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameters_in_cache_key_and_forwarded_to_origin(
        self,
    ) -> "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin":
        '''parameters_in_cache_key_and_forwarded_to_origin block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#parameters_in_cache_key_and_forwarded_to_origin CloudfrontCachePolicy#parameters_in_cache_key_and_forwarded_to_origin}
        '''
        result = self._values.get("parameters_in_cache_key_and_forwarded_to_origin")
        assert result is not None, "Required property 'parameters_in_cache_key_and_forwarded_to_origin' is missing"
        return typing.cast("CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin", result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#comment CloudfrontCachePolicy#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#default_ttl CloudfrontCachePolicy#default_ttl}.'''
        result = self._values.get("default_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#max_ttl CloudfrontCachePolicy#max_ttl}.'''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#min_ttl CloudfrontCachePolicy#min_ttl}.'''
        result = self._values.get("min_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontCachePolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin",
    jsii_struct_bases=[],
    name_mapping={
        "cookies_config": "cookiesConfig",
        "headers_config": "headersConfig",
        "query_strings_config": "queryStringsConfig",
        "enable_accept_encoding_brotli": "enableAcceptEncodingBrotli",
        "enable_accept_encoding_gzip": "enableAcceptEncodingGzip",
    },
)
class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin:
    def __init__(
        self,
        *,
        cookies_config: "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig",
        headers_config: "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig",
        query_strings_config: "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig",
        enable_accept_encoding_brotli: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_accept_encoding_gzip: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param cookies_config: cookies_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#cookies_config CloudfrontCachePolicy#cookies_config}
        :param headers_config: headers_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#headers_config CloudfrontCachePolicy#headers_config}
        :param query_strings_config: query_strings_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#query_strings_config CloudfrontCachePolicy#query_strings_config}
        :param enable_accept_encoding_brotli: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#enable_accept_encoding_brotli CloudfrontCachePolicy#enable_accept_encoding_brotli}.
        :param enable_accept_encoding_gzip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#enable_accept_encoding_gzip CloudfrontCachePolicy#enable_accept_encoding_gzip}.
        '''
        if isinstance(cookies_config, dict):
            cookies_config = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig(**cookies_config)
        if isinstance(headers_config, dict):
            headers_config = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig(**headers_config)
        if isinstance(query_strings_config, dict):
            query_strings_config = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig(**query_strings_config)
        self._values: typing.Dict[str, typing.Any] = {
            "cookies_config": cookies_config,
            "headers_config": headers_config,
            "query_strings_config": query_strings_config,
        }
        if enable_accept_encoding_brotli is not None:
            self._values["enable_accept_encoding_brotli"] = enable_accept_encoding_brotli
        if enable_accept_encoding_gzip is not None:
            self._values["enable_accept_encoding_gzip"] = enable_accept_encoding_gzip

    @builtins.property
    def cookies_config(
        self,
    ) -> "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig":
        '''cookies_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#cookies_config CloudfrontCachePolicy#cookies_config}
        '''
        result = self._values.get("cookies_config")
        assert result is not None, "Required property 'cookies_config' is missing"
        return typing.cast("CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig", result)

    @builtins.property
    def headers_config(
        self,
    ) -> "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig":
        '''headers_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#headers_config CloudfrontCachePolicy#headers_config}
        '''
        result = self._values.get("headers_config")
        assert result is not None, "Required property 'headers_config' is missing"
        return typing.cast("CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig", result)

    @builtins.property
    def query_strings_config(
        self,
    ) -> "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig":
        '''query_strings_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#query_strings_config CloudfrontCachePolicy#query_strings_config}
        '''
        result = self._values.get("query_strings_config")
        assert result is not None, "Required property 'query_strings_config' is missing"
        return typing.cast("CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig", result)

    @builtins.property
    def enable_accept_encoding_brotli(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#enable_accept_encoding_brotli CloudfrontCachePolicy#enable_accept_encoding_brotli}.'''
        result = self._values.get("enable_accept_encoding_brotli")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_accept_encoding_gzip(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#enable_accept_encoding_gzip CloudfrontCachePolicy#enable_accept_encoding_gzip}.'''
        result = self._values.get("enable_accept_encoding_gzip")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig",
    jsii_struct_bases=[],
    name_mapping={"cookie_behavior": "cookieBehavior", "cookies": "cookies"},
)
class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig:
    def __init__(
        self,
        *,
        cookie_behavior: builtins.str,
        cookies: typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies"] = None,
    ) -> None:
        '''
        :param cookie_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#cookie_behavior CloudfrontCachePolicy#cookie_behavior}.
        :param cookies: cookies block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#cookies CloudfrontCachePolicy#cookies}
        '''
        if isinstance(cookies, dict):
            cookies = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies(**cookies)
        self._values: typing.Dict[str, typing.Any] = {
            "cookie_behavior": cookie_behavior,
        }
        if cookies is not None:
            self._values["cookies"] = cookies

    @builtins.property
    def cookie_behavior(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#cookie_behavior CloudfrontCachePolicy#cookie_behavior}.'''
        result = self._values.get("cookie_behavior")
        assert result is not None, "Required property 'cookie_behavior' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cookies(
        self,
    ) -> typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies"]:
        '''cookies block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#cookies CloudfrontCachePolicy#cookies}
        '''
        result = self._values.get("cookies")
        return typing.cast(typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#items CloudfrontCachePolicy#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#items CloudfrontCachePolicy#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putCookies")
    def put_cookies(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#items CloudfrontCachePolicy#items}.
        '''
        value = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies(
            items=items
        )

        return typing.cast(None, jsii.invoke(self, "putCookies", [value]))

    @jsii.member(jsii_name="resetCookies")
    def reset_cookies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCookies", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookies")
    def cookies(
        self,
    ) -> CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookiesOutputReference:
        return typing.cast(CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookiesOutputReference, jsii.get(self, "cookies"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookieBehaviorInput")
    def cookie_behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cookieBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookiesInput")
    def cookies_input(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies], jsii.get(self, "cookiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookieBehavior")
    def cookie_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cookieBehavior"))

    @cookie_behavior.setter
    def cookie_behavior(self, value: builtins.str) -> None:
        jsii.set(self, "cookieBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig",
    jsii_struct_bases=[],
    name_mapping={"header_behavior": "headerBehavior", "headers": "headers"},
)
class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig:
    def __init__(
        self,
        *,
        header_behavior: typing.Optional[builtins.str] = None,
        headers: typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders"] = None,
    ) -> None:
        '''
        :param header_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#header_behavior CloudfrontCachePolicy#header_behavior}.
        :param headers: headers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#headers CloudfrontCachePolicy#headers}
        '''
        if isinstance(headers, dict):
            headers = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders(**headers)
        self._values: typing.Dict[str, typing.Any] = {}
        if header_behavior is not None:
            self._values["header_behavior"] = header_behavior
        if headers is not None:
            self._values["headers"] = headers

    @builtins.property
    def header_behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#header_behavior CloudfrontCachePolicy#header_behavior}.'''
        result = self._values.get("header_behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def headers(
        self,
    ) -> typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders"]:
        '''headers block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#headers CloudfrontCachePolicy#headers}
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#items CloudfrontCachePolicy#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#items CloudfrontCachePolicy#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeadersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeadersOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putHeaders")
    def put_headers(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#items CloudfrontCachePolicy#items}.
        '''
        value = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders(
            items=items
        )

        return typing.cast(None, jsii.invoke(self, "putHeaders", [value]))

    @jsii.member(jsii_name="resetHeaderBehavior")
    def reset_header_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaderBehavior", []))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headers")
    def headers(
        self,
    ) -> CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeadersOutputReference:
        return typing.cast(CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeadersOutputReference, jsii.get(self, "headers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headerBehaviorInput")
    def header_behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersInput")
    def headers_input(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders], jsii.get(self, "headersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headerBehavior")
    def header_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerBehavior"))

    @header_behavior.setter
    def header_behavior(self, value: builtins.str) -> None:
        jsii.set(self, "headerBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putCookiesConfig")
    def put_cookies_config(
        self,
        *,
        cookie_behavior: builtins.str,
        cookies: typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies] = None,
    ) -> None:
        '''
        :param cookie_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#cookie_behavior CloudfrontCachePolicy#cookie_behavior}.
        :param cookies: cookies block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#cookies CloudfrontCachePolicy#cookies}
        '''
        value = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig(
            cookie_behavior=cookie_behavior, cookies=cookies
        )

        return typing.cast(None, jsii.invoke(self, "putCookiesConfig", [value]))

    @jsii.member(jsii_name="putHeadersConfig")
    def put_headers_config(
        self,
        *,
        header_behavior: typing.Optional[builtins.str] = None,
        headers: typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders] = None,
    ) -> None:
        '''
        :param header_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#header_behavior CloudfrontCachePolicy#header_behavior}.
        :param headers: headers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#headers CloudfrontCachePolicy#headers}
        '''
        value = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig(
            header_behavior=header_behavior, headers=headers
        )

        return typing.cast(None, jsii.invoke(self, "putHeadersConfig", [value]))

    @jsii.member(jsii_name="putQueryStringsConfig")
    def put_query_strings_config(
        self,
        *,
        query_string_behavior: builtins.str,
        query_strings: typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings"] = None,
    ) -> None:
        '''
        :param query_string_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#query_string_behavior CloudfrontCachePolicy#query_string_behavior}.
        :param query_strings: query_strings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#query_strings CloudfrontCachePolicy#query_strings}
        '''
        value = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig(
            query_string_behavior=query_string_behavior, query_strings=query_strings
        )

        return typing.cast(None, jsii.invoke(self, "putQueryStringsConfig", [value]))

    @jsii.member(jsii_name="resetEnableAcceptEncodingBrotli")
    def reset_enable_accept_encoding_brotli(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableAcceptEncodingBrotli", []))

    @jsii.member(jsii_name="resetEnableAcceptEncodingGzip")
    def reset_enable_accept_encoding_gzip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableAcceptEncodingGzip", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookiesConfig")
    def cookies_config(
        self,
    ) -> CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigOutputReference:
        return typing.cast(CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigOutputReference, jsii.get(self, "cookiesConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersConfig")
    def headers_config(
        self,
    ) -> CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigOutputReference:
        return typing.cast(CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigOutputReference, jsii.get(self, "headersConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringsConfig")
    def query_strings_config(
        self,
    ) -> "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigOutputReference":
        return typing.cast("CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigOutputReference", jsii.get(self, "queryStringsConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookiesConfigInput")
    def cookies_config_input(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig], jsii.get(self, "cookiesConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAcceptEncodingBrotliInput")
    def enable_accept_encoding_brotli_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableAcceptEncodingBrotliInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAcceptEncodingGzipInput")
    def enable_accept_encoding_gzip_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableAcceptEncodingGzipInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersConfigInput")
    def headers_config_input(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig], jsii.get(self, "headersConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringsConfigInput")
    def query_strings_config_input(
        self,
    ) -> typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig"]:
        return typing.cast(typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig"], jsii.get(self, "queryStringsConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAcceptEncodingBrotli")
    def enable_accept_encoding_brotli(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableAcceptEncodingBrotli"))

    @enable_accept_encoding_brotli.setter
    def enable_accept_encoding_brotli(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableAcceptEncodingBrotli", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAcceptEncodingGzip")
    def enable_accept_encoding_gzip(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableAcceptEncodingGzip"))

    @enable_accept_encoding_gzip.setter
    def enable_accept_encoding_gzip(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "enableAcceptEncodingGzip", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "query_string_behavior": "queryStringBehavior",
        "query_strings": "queryStrings",
    },
)
class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig:
    def __init__(
        self,
        *,
        query_string_behavior: builtins.str,
        query_strings: typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings"] = None,
    ) -> None:
        '''
        :param query_string_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#query_string_behavior CloudfrontCachePolicy#query_string_behavior}.
        :param query_strings: query_strings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#query_strings CloudfrontCachePolicy#query_strings}
        '''
        if isinstance(query_strings, dict):
            query_strings = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings(**query_strings)
        self._values: typing.Dict[str, typing.Any] = {
            "query_string_behavior": query_string_behavior,
        }
        if query_strings is not None:
            self._values["query_strings"] = query_strings

    @builtins.property
    def query_string_behavior(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#query_string_behavior CloudfrontCachePolicy#query_string_behavior}.'''
        result = self._values.get("query_string_behavior")
        assert result is not None, "Required property 'query_string_behavior' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query_strings(
        self,
    ) -> typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings"]:
        '''query_strings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#query_strings CloudfrontCachePolicy#query_strings}
        '''
        result = self._values.get("query_strings")
        return typing.cast(typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putQueryStrings")
    def put_query_strings(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#items CloudfrontCachePolicy#items}.
        '''
        value = CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings(
            items=items
        )

        return typing.cast(None, jsii.invoke(self, "putQueryStrings", [value]))

    @jsii.member(jsii_name="resetQueryStrings")
    def reset_query_strings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryStrings", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStrings")
    def query_strings(
        self,
    ) -> "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStringsOutputReference":
        return typing.cast("CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStringsOutputReference", jsii.get(self, "queryStrings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringBehaviorInput")
    def query_string_behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryStringBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringsInput")
    def query_strings_input(
        self,
    ) -> typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings"]:
        return typing.cast(typing.Optional["CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings"], jsii.get(self, "queryStringsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringBehavior")
    def query_string_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryStringBehavior"))

    @query_string_behavior.setter
    def query_string_behavior(self, value: builtins.str) -> None:
        jsii.set(self, "queryStringBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#items CloudfrontCachePolicy#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_cache_policy#items CloudfrontCachePolicy#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStringsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStringsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings]:
        return typing.cast(typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontDistribution(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistribution",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution aws_cloudfront_distribution}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        default_cache_behavior: "CloudfrontDistributionDefaultCacheBehavior",
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        origin: typing.Sequence["CloudfrontDistributionOrigin"],
        restrictions: "CloudfrontDistributionRestrictions",
        viewer_certificate: "CloudfrontDistributionViewerCertificate",
        aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
        comment: typing.Optional[builtins.str] = None,
        custom_error_response: typing.Optional[typing.Sequence["CloudfrontDistributionCustomErrorResponse"]] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        http_version: typing.Optional[builtins.str] = None,
        is_ipv6_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        logging_config: typing.Optional["CloudfrontDistributionLoggingConfig"] = None,
        ordered_cache_behavior: typing.Optional[typing.Sequence["CloudfrontDistributionOrderedCacheBehavior"]] = None,
        origin_group: typing.Optional[typing.Sequence["CloudfrontDistributionOriginGroup"]] = None,
        price_class: typing.Optional[builtins.str] = None,
        retain_on_delete: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        wait_for_deployment: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution aws_cloudfront_distribution} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param default_cache_behavior: default_cache_behavior block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_cache_behavior CloudfrontDistribution#default_cache_behavior}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#enabled CloudfrontDistribution#enabled}.
        :param origin: origin block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin CloudfrontDistribution#origin}
        :param restrictions: restrictions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#restrictions CloudfrontDistribution#restrictions}
        :param viewer_certificate: viewer_certificate block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#viewer_certificate CloudfrontDistribution#viewer_certificate}
        :param aliases: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#aliases CloudfrontDistribution#aliases}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#comment CloudfrontDistribution#comment}.
        :param custom_error_response: custom_error_response block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#custom_error_response CloudfrontDistribution#custom_error_response}
        :param default_root_object: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_root_object CloudfrontDistribution#default_root_object}.
        :param http_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#http_version CloudfrontDistribution#http_version}.
        :param is_ipv6_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#is_ipv6_enabled CloudfrontDistribution#is_ipv6_enabled}.
        :param logging_config: logging_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#logging_config CloudfrontDistribution#logging_config}
        :param ordered_cache_behavior: ordered_cache_behavior block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#ordered_cache_behavior CloudfrontDistribution#ordered_cache_behavior}
        :param origin_group: origin_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_group CloudfrontDistribution#origin_group}
        :param price_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#price_class CloudfrontDistribution#price_class}.
        :param retain_on_delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#retain_on_delete CloudfrontDistribution#retain_on_delete}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#tags CloudfrontDistribution#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#tags_all CloudfrontDistribution#tags_all}.
        :param wait_for_deployment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#wait_for_deployment CloudfrontDistribution#wait_for_deployment}.
        :param web_acl_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#web_acl_id CloudfrontDistribution#web_acl_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontDistributionConfig(
            default_cache_behavior=default_cache_behavior,
            enabled=enabled,
            origin=origin,
            restrictions=restrictions,
            viewer_certificate=viewer_certificate,
            aliases=aliases,
            comment=comment,
            custom_error_response=custom_error_response,
            default_root_object=default_root_object,
            http_version=http_version,
            is_ipv6_enabled=is_ipv6_enabled,
            logging_config=logging_config,
            ordered_cache_behavior=ordered_cache_behavior,
            origin_group=origin_group,
            price_class=price_class,
            retain_on_delete=retain_on_delete,
            tags=tags,
            tags_all=tags_all,
            wait_for_deployment=wait_for_deployment,
            web_acl_id=web_acl_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDefaultCacheBehavior")
    def put_default_cache_behavior(
        self,
        *,
        allowed_methods: typing.Sequence[builtins.str],
        cached_methods: typing.Sequence[builtins.str],
        target_origin_id: builtins.str,
        viewer_protocol_policy: builtins.str,
        cache_policy_id: typing.Optional[builtins.str] = None,
        compress: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        default_ttl: typing.Optional[jsii.Number] = None,
        field_level_encryption_id: typing.Optional[builtins.str] = None,
        forwarded_values: typing.Optional["CloudfrontDistributionDefaultCacheBehaviorForwardedValues"] = None,
        function_association: typing.Optional[typing.Sequence["CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation"]] = None,
        lambda_function_association: typing.Optional[typing.Sequence["CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation"]] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        min_ttl: typing.Optional[jsii.Number] = None,
        origin_request_policy_id: typing.Optional[builtins.str] = None,
        realtime_log_config_arn: typing.Optional[builtins.str] = None,
        response_headers_policy_id: typing.Optional[builtins.str] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        trusted_signers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allowed_methods: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#allowed_methods CloudfrontDistribution#allowed_methods}.
        :param cached_methods: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cached_methods CloudfrontDistribution#cached_methods}.
        :param target_origin_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#target_origin_id CloudfrontDistribution#target_origin_id}.
        :param viewer_protocol_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#viewer_protocol_policy CloudfrontDistribution#viewer_protocol_policy}.
        :param cache_policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cache_policy_id CloudfrontDistribution#cache_policy_id}.
        :param compress: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#compress CloudfrontDistribution#compress}.
        :param default_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_ttl CloudfrontDistribution#default_ttl}.
        :param field_level_encryption_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#field_level_encryption_id CloudfrontDistribution#field_level_encryption_id}.
        :param forwarded_values: forwarded_values block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forwarded_values CloudfrontDistribution#forwarded_values}
        :param function_association: function_association block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#function_association CloudfrontDistribution#function_association}
        :param lambda_function_association: lambda_function_association block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#lambda_function_association CloudfrontDistribution#lambda_function_association}
        :param max_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#max_ttl CloudfrontDistribution#max_ttl}.
        :param min_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#min_ttl CloudfrontDistribution#min_ttl}.
        :param origin_request_policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_request_policy_id CloudfrontDistribution#origin_request_policy_id}.
        :param realtime_log_config_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#realtime_log_config_arn CloudfrontDistribution#realtime_log_config_arn}.
        :param response_headers_policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#response_headers_policy_id CloudfrontDistribution#response_headers_policy_id}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#smooth_streaming CloudfrontDistribution#smooth_streaming}.
        :param trusted_key_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#trusted_key_groups CloudfrontDistribution#trusted_key_groups}.
        :param trusted_signers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#trusted_signers CloudfrontDistribution#trusted_signers}.
        '''
        value = CloudfrontDistributionDefaultCacheBehavior(
            allowed_methods=allowed_methods,
            cached_methods=cached_methods,
            target_origin_id=target_origin_id,
            viewer_protocol_policy=viewer_protocol_policy,
            cache_policy_id=cache_policy_id,
            compress=compress,
            default_ttl=default_ttl,
            field_level_encryption_id=field_level_encryption_id,
            forwarded_values=forwarded_values,
            function_association=function_association,
            lambda_function_association=lambda_function_association,
            max_ttl=max_ttl,
            min_ttl=min_ttl,
            origin_request_policy_id=origin_request_policy_id,
            realtime_log_config_arn=realtime_log_config_arn,
            response_headers_policy_id=response_headers_policy_id,
            smooth_streaming=smooth_streaming,
            trusted_key_groups=trusted_key_groups,
            trusted_signers=trusted_signers,
        )

        return typing.cast(None, jsii.invoke(self, "putDefaultCacheBehavior", [value]))

    @jsii.member(jsii_name="putLoggingConfig")
    def put_logging_config(
        self,
        *,
        bucket: builtins.str,
        include_cookies: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#bucket CloudfrontDistribution#bucket}.
        :param include_cookies: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#include_cookies CloudfrontDistribution#include_cookies}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#prefix CloudfrontDistribution#prefix}.
        '''
        value = CloudfrontDistributionLoggingConfig(
            bucket=bucket, include_cookies=include_cookies, prefix=prefix
        )

        return typing.cast(None, jsii.invoke(self, "putLoggingConfig", [value]))

    @jsii.member(jsii_name="putRestrictions")
    def put_restrictions(
        self,
        *,
        geo_restriction: "CloudfrontDistributionRestrictionsGeoRestriction",
    ) -> None:
        '''
        :param geo_restriction: geo_restriction block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#geo_restriction CloudfrontDistribution#geo_restriction}
        '''
        value = CloudfrontDistributionRestrictions(geo_restriction=geo_restriction)

        return typing.cast(None, jsii.invoke(self, "putRestrictions", [value]))

    @jsii.member(jsii_name="putViewerCertificate")
    def put_viewer_certificate(
        self,
        *,
        acm_certificate_arn: typing.Optional[builtins.str] = None,
        cloudfront_default_certificate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iam_certificate_id: typing.Optional[builtins.str] = None,
        minimum_protocol_version: typing.Optional[builtins.str] = None,
        ssl_support_method: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param acm_certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#acm_certificate_arn CloudfrontDistribution#acm_certificate_arn}.
        :param cloudfront_default_certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cloudfront_default_certificate CloudfrontDistribution#cloudfront_default_certificate}.
        :param iam_certificate_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#iam_certificate_id CloudfrontDistribution#iam_certificate_id}.
        :param minimum_protocol_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#minimum_protocol_version CloudfrontDistribution#minimum_protocol_version}.
        :param ssl_support_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#ssl_support_method CloudfrontDistribution#ssl_support_method}.
        '''
        value = CloudfrontDistributionViewerCertificate(
            acm_certificate_arn=acm_certificate_arn,
            cloudfront_default_certificate=cloudfront_default_certificate,
            iam_certificate_id=iam_certificate_id,
            minimum_protocol_version=minimum_protocol_version,
            ssl_support_method=ssl_support_method,
        )

        return typing.cast(None, jsii.invoke(self, "putViewerCertificate", [value]))

    @jsii.member(jsii_name="resetAliases")
    def reset_aliases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAliases", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetCustomErrorResponse")
    def reset_custom_error_response(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomErrorResponse", []))

    @jsii.member(jsii_name="resetDefaultRootObject")
    def reset_default_root_object(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultRootObject", []))

    @jsii.member(jsii_name="resetHttpVersion")
    def reset_http_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpVersion", []))

    @jsii.member(jsii_name="resetIsIpv6Enabled")
    def reset_is_ipv6_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsIpv6Enabled", []))

    @jsii.member(jsii_name="resetLoggingConfig")
    def reset_logging_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLoggingConfig", []))

    @jsii.member(jsii_name="resetOrderedCacheBehavior")
    def reset_ordered_cache_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrderedCacheBehavior", []))

    @jsii.member(jsii_name="resetOriginGroup")
    def reset_origin_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginGroup", []))

    @jsii.member(jsii_name="resetPriceClass")
    def reset_price_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPriceClass", []))

    @jsii.member(jsii_name="resetRetainOnDelete")
    def reset_retain_on_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetainOnDelete", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetWaitForDeployment")
    def reset_wait_for_deployment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitForDeployment", []))

    @jsii.member(jsii_name="resetWebAclId")
    def reset_web_acl_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebAclId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="trustedKeyGroups")
    def trusted_key_groups(
        self,
        index: builtins.str,
    ) -> "CloudfrontDistributionTrustedKeyGroups":
        '''
        :param index: -
        '''
        return typing.cast("CloudfrontDistributionTrustedKeyGroups", jsii.invoke(self, "trustedKeyGroups", [index]))

    @jsii.member(jsii_name="trustedSigners")
    def trusted_signers(
        self,
        index: builtins.str,
    ) -> "CloudfrontDistributionTrustedSigners":
        '''
        :param index: -
        '''
        return typing.cast("CloudfrontDistributionTrustedSigners", jsii.invoke(self, "trustedSigners", [index]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callerReference")
    def caller_reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "callerReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultCacheBehavior")
    def default_cache_behavior(
        self,
    ) -> "CloudfrontDistributionDefaultCacheBehaviorOutputReference":
        return typing.cast("CloudfrontDistributionDefaultCacheBehaviorOutputReference", jsii.get(self, "defaultCacheBehavior"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inProgressValidationBatches")
    def in_progress_validation_batches(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "inProgressValidationBatches"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedTime")
    def last_modified_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingConfig")
    def logging_config(self) -> "CloudfrontDistributionLoggingConfigOutputReference":
        return typing.cast("CloudfrontDistributionLoggingConfigOutputReference", jsii.get(self, "loggingConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictions")
    def restrictions(self) -> "CloudfrontDistributionRestrictionsOutputReference":
        return typing.cast("CloudfrontDistributionRestrictionsOutputReference", jsii.get(self, "restrictions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="viewerCertificate")
    def viewer_certificate(
        self,
    ) -> "CloudfrontDistributionViewerCertificateOutputReference":
        return typing.cast("CloudfrontDistributionViewerCertificateOutputReference", jsii.get(self, "viewerCertificate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasesInput")
    def aliases_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "aliasesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customErrorResponseInput")
    def custom_error_response_input(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionCustomErrorResponse"]]:
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionCustomErrorResponse"]], jsii.get(self, "customErrorResponseInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultCacheBehaviorInput")
    def default_cache_behavior_input(
        self,
    ) -> typing.Optional["CloudfrontDistributionDefaultCacheBehavior"]:
        return typing.cast(typing.Optional["CloudfrontDistributionDefaultCacheBehavior"], jsii.get(self, "defaultCacheBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRootObjectInput")
    def default_root_object_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultRootObjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpVersionInput")
    def http_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isIpv6EnabledInput")
    def is_ipv6_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "isIpv6EnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loggingConfigInput")
    def logging_config_input(
        self,
    ) -> typing.Optional["CloudfrontDistributionLoggingConfig"]:
        return typing.cast(typing.Optional["CloudfrontDistributionLoggingConfig"], jsii.get(self, "loggingConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="orderedCacheBehaviorInput")
    def ordered_cache_behavior_input(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionOrderedCacheBehavior"]]:
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionOrderedCacheBehavior"]], jsii.get(self, "orderedCacheBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originGroupInput")
    def origin_group_input(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionOriginGroup"]]:
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionOriginGroup"]], jsii.get(self, "originGroupInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originInput")
    def origin_input(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionOrigin"]]:
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionOrigin"]], jsii.get(self, "originInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priceClassInput")
    def price_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "priceClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictionsInput")
    def restrictions_input(
        self,
    ) -> typing.Optional["CloudfrontDistributionRestrictions"]:
        return typing.cast(typing.Optional["CloudfrontDistributionRestrictions"], jsii.get(self, "restrictionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainOnDeleteInput")
    def retain_on_delete_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "retainOnDeleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="viewerCertificateInput")
    def viewer_certificate_input(
        self,
    ) -> typing.Optional["CloudfrontDistributionViewerCertificate"]:
        return typing.cast(typing.Optional["CloudfrontDistributionViewerCertificate"], jsii.get(self, "viewerCertificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitForDeploymentInput")
    def wait_for_deployment_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "waitForDeploymentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="webAclIdInput")
    def web_acl_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webAclIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliases")
    def aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "aliases"))

    @aliases.setter
    def aliases(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "aliases", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        jsii.set(self, "comment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customErrorResponse")
    def custom_error_response(
        self,
    ) -> typing.List["CloudfrontDistributionCustomErrorResponse"]:
        return typing.cast(typing.List["CloudfrontDistributionCustomErrorResponse"], jsii.get(self, "customErrorResponse"))

    @custom_error_response.setter
    def custom_error_response(
        self,
        value: typing.List["CloudfrontDistributionCustomErrorResponse"],
    ) -> None:
        jsii.set(self, "customErrorResponse", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRootObject")
    def default_root_object(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultRootObject"))

    @default_root_object.setter
    def default_root_object(self, value: builtins.str) -> None:
        jsii.set(self, "defaultRootObject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpVersion")
    def http_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpVersion"))

    @http_version.setter
    def http_version(self, value: builtins.str) -> None:
        jsii.set(self, "httpVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isIpv6Enabled")
    def is_ipv6_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "isIpv6Enabled"))

    @is_ipv6_enabled.setter
    def is_ipv6_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "isIpv6Enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="orderedCacheBehavior")
    def ordered_cache_behavior(
        self,
    ) -> typing.List["CloudfrontDistributionOrderedCacheBehavior"]:
        return typing.cast(typing.List["CloudfrontDistributionOrderedCacheBehavior"], jsii.get(self, "orderedCacheBehavior"))

    @ordered_cache_behavior.setter
    def ordered_cache_behavior(
        self,
        value: typing.List["CloudfrontDistributionOrderedCacheBehavior"],
    ) -> None:
        jsii.set(self, "orderedCacheBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="origin")
    def origin(self) -> typing.List["CloudfrontDistributionOrigin"]:
        return typing.cast(typing.List["CloudfrontDistributionOrigin"], jsii.get(self, "origin"))

    @origin.setter
    def origin(self, value: typing.List["CloudfrontDistributionOrigin"]) -> None:
        jsii.set(self, "origin", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originGroup")
    def origin_group(self) -> typing.List["CloudfrontDistributionOriginGroup"]:
        return typing.cast(typing.List["CloudfrontDistributionOriginGroup"], jsii.get(self, "originGroup"))

    @origin_group.setter
    def origin_group(
        self,
        value: typing.List["CloudfrontDistributionOriginGroup"],
    ) -> None:
        jsii.set(self, "originGroup", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="priceClass")
    def price_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "priceClass"))

    @price_class.setter
    def price_class(self, value: builtins.str) -> None:
        jsii.set(self, "priceClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retainOnDelete")
    def retain_on_delete(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "retainOnDelete"))

    @retain_on_delete.setter
    def retain_on_delete(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "retainOnDelete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="waitForDeployment")
    def wait_for_deployment(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "waitForDeployment"))

    @wait_for_deployment.setter
    def wait_for_deployment(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "waitForDeployment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="webAclId")
    def web_acl_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webAclId"))

    @web_acl_id.setter
    def web_acl_id(self, value: builtins.str) -> None:
        jsii.set(self, "webAclId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "default_cache_behavior": "defaultCacheBehavior",
        "enabled": "enabled",
        "origin": "origin",
        "restrictions": "restrictions",
        "viewer_certificate": "viewerCertificate",
        "aliases": "aliases",
        "comment": "comment",
        "custom_error_response": "customErrorResponse",
        "default_root_object": "defaultRootObject",
        "http_version": "httpVersion",
        "is_ipv6_enabled": "isIpv6Enabled",
        "logging_config": "loggingConfig",
        "ordered_cache_behavior": "orderedCacheBehavior",
        "origin_group": "originGroup",
        "price_class": "priceClass",
        "retain_on_delete": "retainOnDelete",
        "tags": "tags",
        "tags_all": "tagsAll",
        "wait_for_deployment": "waitForDeployment",
        "web_acl_id": "webAclId",
    },
)
class CloudfrontDistributionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        default_cache_behavior: "CloudfrontDistributionDefaultCacheBehavior",
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        origin: typing.Sequence["CloudfrontDistributionOrigin"],
        restrictions: "CloudfrontDistributionRestrictions",
        viewer_certificate: "CloudfrontDistributionViewerCertificate",
        aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
        comment: typing.Optional[builtins.str] = None,
        custom_error_response: typing.Optional[typing.Sequence["CloudfrontDistributionCustomErrorResponse"]] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        http_version: typing.Optional[builtins.str] = None,
        is_ipv6_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        logging_config: typing.Optional["CloudfrontDistributionLoggingConfig"] = None,
        ordered_cache_behavior: typing.Optional[typing.Sequence["CloudfrontDistributionOrderedCacheBehavior"]] = None,
        origin_group: typing.Optional[typing.Sequence["CloudfrontDistributionOriginGroup"]] = None,
        price_class: typing.Optional[builtins.str] = None,
        retain_on_delete: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        wait_for_deployment: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param default_cache_behavior: default_cache_behavior block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_cache_behavior CloudfrontDistribution#default_cache_behavior}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#enabled CloudfrontDistribution#enabled}.
        :param origin: origin block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin CloudfrontDistribution#origin}
        :param restrictions: restrictions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#restrictions CloudfrontDistribution#restrictions}
        :param viewer_certificate: viewer_certificate block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#viewer_certificate CloudfrontDistribution#viewer_certificate}
        :param aliases: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#aliases CloudfrontDistribution#aliases}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#comment CloudfrontDistribution#comment}.
        :param custom_error_response: custom_error_response block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#custom_error_response CloudfrontDistribution#custom_error_response}
        :param default_root_object: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_root_object CloudfrontDistribution#default_root_object}.
        :param http_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#http_version CloudfrontDistribution#http_version}.
        :param is_ipv6_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#is_ipv6_enabled CloudfrontDistribution#is_ipv6_enabled}.
        :param logging_config: logging_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#logging_config CloudfrontDistribution#logging_config}
        :param ordered_cache_behavior: ordered_cache_behavior block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#ordered_cache_behavior CloudfrontDistribution#ordered_cache_behavior}
        :param origin_group: origin_group block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_group CloudfrontDistribution#origin_group}
        :param price_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#price_class CloudfrontDistribution#price_class}.
        :param retain_on_delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#retain_on_delete CloudfrontDistribution#retain_on_delete}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#tags CloudfrontDistribution#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#tags_all CloudfrontDistribution#tags_all}.
        :param wait_for_deployment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#wait_for_deployment CloudfrontDistribution#wait_for_deployment}.
        :param web_acl_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#web_acl_id CloudfrontDistribution#web_acl_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(default_cache_behavior, dict):
            default_cache_behavior = CloudfrontDistributionDefaultCacheBehavior(**default_cache_behavior)
        if isinstance(restrictions, dict):
            restrictions = CloudfrontDistributionRestrictions(**restrictions)
        if isinstance(viewer_certificate, dict):
            viewer_certificate = CloudfrontDistributionViewerCertificate(**viewer_certificate)
        if isinstance(logging_config, dict):
            logging_config = CloudfrontDistributionLoggingConfig(**logging_config)
        self._values: typing.Dict[str, typing.Any] = {
            "default_cache_behavior": default_cache_behavior,
            "enabled": enabled,
            "origin": origin,
            "restrictions": restrictions,
            "viewer_certificate": viewer_certificate,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if aliases is not None:
            self._values["aliases"] = aliases
        if comment is not None:
            self._values["comment"] = comment
        if custom_error_response is not None:
            self._values["custom_error_response"] = custom_error_response
        if default_root_object is not None:
            self._values["default_root_object"] = default_root_object
        if http_version is not None:
            self._values["http_version"] = http_version
        if is_ipv6_enabled is not None:
            self._values["is_ipv6_enabled"] = is_ipv6_enabled
        if logging_config is not None:
            self._values["logging_config"] = logging_config
        if ordered_cache_behavior is not None:
            self._values["ordered_cache_behavior"] = ordered_cache_behavior
        if origin_group is not None:
            self._values["origin_group"] = origin_group
        if price_class is not None:
            self._values["price_class"] = price_class
        if retain_on_delete is not None:
            self._values["retain_on_delete"] = retain_on_delete
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if wait_for_deployment is not None:
            self._values["wait_for_deployment"] = wait_for_deployment
        if web_acl_id is not None:
            self._values["web_acl_id"] = web_acl_id

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
    def default_cache_behavior(self) -> "CloudfrontDistributionDefaultCacheBehavior":
        '''default_cache_behavior block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_cache_behavior CloudfrontDistribution#default_cache_behavior}
        '''
        result = self._values.get("default_cache_behavior")
        assert result is not None, "Required property 'default_cache_behavior' is missing"
        return typing.cast("CloudfrontDistributionDefaultCacheBehavior", result)

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#enabled CloudfrontDistribution#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def origin(self) -> typing.List["CloudfrontDistributionOrigin"]:
        '''origin block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin CloudfrontDistribution#origin}
        '''
        result = self._values.get("origin")
        assert result is not None, "Required property 'origin' is missing"
        return typing.cast(typing.List["CloudfrontDistributionOrigin"], result)

    @builtins.property
    def restrictions(self) -> "CloudfrontDistributionRestrictions":
        '''restrictions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#restrictions CloudfrontDistribution#restrictions}
        '''
        result = self._values.get("restrictions")
        assert result is not None, "Required property 'restrictions' is missing"
        return typing.cast("CloudfrontDistributionRestrictions", result)

    @builtins.property
    def viewer_certificate(self) -> "CloudfrontDistributionViewerCertificate":
        '''viewer_certificate block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#viewer_certificate CloudfrontDistribution#viewer_certificate}
        '''
        result = self._values.get("viewer_certificate")
        assert result is not None, "Required property 'viewer_certificate' is missing"
        return typing.cast("CloudfrontDistributionViewerCertificate", result)

    @builtins.property
    def aliases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#aliases CloudfrontDistribution#aliases}.'''
        result = self._values.get("aliases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#comment CloudfrontDistribution#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_error_response(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionCustomErrorResponse"]]:
        '''custom_error_response block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#custom_error_response CloudfrontDistribution#custom_error_response}
        '''
        result = self._values.get("custom_error_response")
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionCustomErrorResponse"]], result)

    @builtins.property
    def default_root_object(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_root_object CloudfrontDistribution#default_root_object}.'''
        result = self._values.get("default_root_object")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#http_version CloudfrontDistribution#http_version}.'''
        result = self._values.get("http_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_ipv6_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#is_ipv6_enabled CloudfrontDistribution#is_ipv6_enabled}.'''
        result = self._values.get("is_ipv6_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def logging_config(self) -> typing.Optional["CloudfrontDistributionLoggingConfig"]:
        '''logging_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#logging_config CloudfrontDistribution#logging_config}
        '''
        result = self._values.get("logging_config")
        return typing.cast(typing.Optional["CloudfrontDistributionLoggingConfig"], result)

    @builtins.property
    def ordered_cache_behavior(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionOrderedCacheBehavior"]]:
        '''ordered_cache_behavior block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#ordered_cache_behavior CloudfrontDistribution#ordered_cache_behavior}
        '''
        result = self._values.get("ordered_cache_behavior")
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionOrderedCacheBehavior"]], result)

    @builtins.property
    def origin_group(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionOriginGroup"]]:
        '''origin_group block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_group CloudfrontDistribution#origin_group}
        '''
        result = self._values.get("origin_group")
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionOriginGroup"]], result)

    @builtins.property
    def price_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#price_class CloudfrontDistribution#price_class}.'''
        result = self._values.get("price_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retain_on_delete(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#retain_on_delete CloudfrontDistribution#retain_on_delete}.'''
        result = self._values.get("retain_on_delete")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#tags CloudfrontDistribution#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#tags_all CloudfrontDistribution#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def wait_for_deployment(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#wait_for_deployment CloudfrontDistribution#wait_for_deployment}.'''
        result = self._values.get("wait_for_deployment")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def web_acl_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#web_acl_id CloudfrontDistribution#web_acl_id}.'''
        result = self._values.get("web_acl_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionCustomErrorResponse",
    jsii_struct_bases=[],
    name_mapping={
        "error_code": "errorCode",
        "error_caching_min_ttl": "errorCachingMinTtl",
        "response_code": "responseCode",
        "response_page_path": "responsePagePath",
    },
)
class CloudfrontDistributionCustomErrorResponse:
    def __init__(
        self,
        *,
        error_code: jsii.Number,
        error_caching_min_ttl: typing.Optional[jsii.Number] = None,
        response_code: typing.Optional[jsii.Number] = None,
        response_page_path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param error_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#error_code CloudfrontDistribution#error_code}.
        :param error_caching_min_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#error_caching_min_ttl CloudfrontDistribution#error_caching_min_ttl}.
        :param response_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#response_code CloudfrontDistribution#response_code}.
        :param response_page_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#response_page_path CloudfrontDistribution#response_page_path}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "error_code": error_code,
        }
        if error_caching_min_ttl is not None:
            self._values["error_caching_min_ttl"] = error_caching_min_ttl
        if response_code is not None:
            self._values["response_code"] = response_code
        if response_page_path is not None:
            self._values["response_page_path"] = response_page_path

    @builtins.property
    def error_code(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#error_code CloudfrontDistribution#error_code}.'''
        result = self._values.get("error_code")
        assert result is not None, "Required property 'error_code' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def error_caching_min_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#error_caching_min_ttl CloudfrontDistribution#error_caching_min_ttl}.'''
        result = self._values.get("error_caching_min_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def response_code(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#response_code CloudfrontDistribution#response_code}.'''
        result = self._values.get("response_code")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def response_page_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#response_page_path CloudfrontDistribution#response_page_path}.'''
        result = self._values.get("response_page_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionCustomErrorResponse(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionDefaultCacheBehavior",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_methods": "allowedMethods",
        "cached_methods": "cachedMethods",
        "target_origin_id": "targetOriginId",
        "viewer_protocol_policy": "viewerProtocolPolicy",
        "cache_policy_id": "cachePolicyId",
        "compress": "compress",
        "default_ttl": "defaultTtl",
        "field_level_encryption_id": "fieldLevelEncryptionId",
        "forwarded_values": "forwardedValues",
        "function_association": "functionAssociation",
        "lambda_function_association": "lambdaFunctionAssociation",
        "max_ttl": "maxTtl",
        "min_ttl": "minTtl",
        "origin_request_policy_id": "originRequestPolicyId",
        "realtime_log_config_arn": "realtimeLogConfigArn",
        "response_headers_policy_id": "responseHeadersPolicyId",
        "smooth_streaming": "smoothStreaming",
        "trusted_key_groups": "trustedKeyGroups",
        "trusted_signers": "trustedSigners",
    },
)
class CloudfrontDistributionDefaultCacheBehavior:
    def __init__(
        self,
        *,
        allowed_methods: typing.Sequence[builtins.str],
        cached_methods: typing.Sequence[builtins.str],
        target_origin_id: builtins.str,
        viewer_protocol_policy: builtins.str,
        cache_policy_id: typing.Optional[builtins.str] = None,
        compress: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        default_ttl: typing.Optional[jsii.Number] = None,
        field_level_encryption_id: typing.Optional[builtins.str] = None,
        forwarded_values: typing.Optional["CloudfrontDistributionDefaultCacheBehaviorForwardedValues"] = None,
        function_association: typing.Optional[typing.Sequence["CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation"]] = None,
        lambda_function_association: typing.Optional[typing.Sequence["CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation"]] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        min_ttl: typing.Optional[jsii.Number] = None,
        origin_request_policy_id: typing.Optional[builtins.str] = None,
        realtime_log_config_arn: typing.Optional[builtins.str] = None,
        response_headers_policy_id: typing.Optional[builtins.str] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        trusted_signers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allowed_methods: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#allowed_methods CloudfrontDistribution#allowed_methods}.
        :param cached_methods: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cached_methods CloudfrontDistribution#cached_methods}.
        :param target_origin_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#target_origin_id CloudfrontDistribution#target_origin_id}.
        :param viewer_protocol_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#viewer_protocol_policy CloudfrontDistribution#viewer_protocol_policy}.
        :param cache_policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cache_policy_id CloudfrontDistribution#cache_policy_id}.
        :param compress: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#compress CloudfrontDistribution#compress}.
        :param default_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_ttl CloudfrontDistribution#default_ttl}.
        :param field_level_encryption_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#field_level_encryption_id CloudfrontDistribution#field_level_encryption_id}.
        :param forwarded_values: forwarded_values block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forwarded_values CloudfrontDistribution#forwarded_values}
        :param function_association: function_association block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#function_association CloudfrontDistribution#function_association}
        :param lambda_function_association: lambda_function_association block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#lambda_function_association CloudfrontDistribution#lambda_function_association}
        :param max_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#max_ttl CloudfrontDistribution#max_ttl}.
        :param min_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#min_ttl CloudfrontDistribution#min_ttl}.
        :param origin_request_policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_request_policy_id CloudfrontDistribution#origin_request_policy_id}.
        :param realtime_log_config_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#realtime_log_config_arn CloudfrontDistribution#realtime_log_config_arn}.
        :param response_headers_policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#response_headers_policy_id CloudfrontDistribution#response_headers_policy_id}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#smooth_streaming CloudfrontDistribution#smooth_streaming}.
        :param trusted_key_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#trusted_key_groups CloudfrontDistribution#trusted_key_groups}.
        :param trusted_signers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#trusted_signers CloudfrontDistribution#trusted_signers}.
        '''
        if isinstance(forwarded_values, dict):
            forwarded_values = CloudfrontDistributionDefaultCacheBehaviorForwardedValues(**forwarded_values)
        self._values: typing.Dict[str, typing.Any] = {
            "allowed_methods": allowed_methods,
            "cached_methods": cached_methods,
            "target_origin_id": target_origin_id,
            "viewer_protocol_policy": viewer_protocol_policy,
        }
        if cache_policy_id is not None:
            self._values["cache_policy_id"] = cache_policy_id
        if compress is not None:
            self._values["compress"] = compress
        if default_ttl is not None:
            self._values["default_ttl"] = default_ttl
        if field_level_encryption_id is not None:
            self._values["field_level_encryption_id"] = field_level_encryption_id
        if forwarded_values is not None:
            self._values["forwarded_values"] = forwarded_values
        if function_association is not None:
            self._values["function_association"] = function_association
        if lambda_function_association is not None:
            self._values["lambda_function_association"] = lambda_function_association
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if min_ttl is not None:
            self._values["min_ttl"] = min_ttl
        if origin_request_policy_id is not None:
            self._values["origin_request_policy_id"] = origin_request_policy_id
        if realtime_log_config_arn is not None:
            self._values["realtime_log_config_arn"] = realtime_log_config_arn
        if response_headers_policy_id is not None:
            self._values["response_headers_policy_id"] = response_headers_policy_id
        if smooth_streaming is not None:
            self._values["smooth_streaming"] = smooth_streaming
        if trusted_key_groups is not None:
            self._values["trusted_key_groups"] = trusted_key_groups
        if trusted_signers is not None:
            self._values["trusted_signers"] = trusted_signers

    @builtins.property
    def allowed_methods(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#allowed_methods CloudfrontDistribution#allowed_methods}.'''
        result = self._values.get("allowed_methods")
        assert result is not None, "Required property 'allowed_methods' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def cached_methods(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cached_methods CloudfrontDistribution#cached_methods}.'''
        result = self._values.get("cached_methods")
        assert result is not None, "Required property 'cached_methods' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def target_origin_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#target_origin_id CloudfrontDistribution#target_origin_id}.'''
        result = self._values.get("target_origin_id")
        assert result is not None, "Required property 'target_origin_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def viewer_protocol_policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#viewer_protocol_policy CloudfrontDistribution#viewer_protocol_policy}.'''
        result = self._values.get("viewer_protocol_policy")
        assert result is not None, "Required property 'viewer_protocol_policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cache_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cache_policy_id CloudfrontDistribution#cache_policy_id}.'''
        result = self._values.get("cache_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compress(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#compress CloudfrontDistribution#compress}.'''
        result = self._values.get("compress")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def default_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_ttl CloudfrontDistribution#default_ttl}.'''
        result = self._values.get("default_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def field_level_encryption_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#field_level_encryption_id CloudfrontDistribution#field_level_encryption_id}.'''
        result = self._values.get("field_level_encryption_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def forwarded_values(
        self,
    ) -> typing.Optional["CloudfrontDistributionDefaultCacheBehaviorForwardedValues"]:
        '''forwarded_values block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forwarded_values CloudfrontDistribution#forwarded_values}
        '''
        result = self._values.get("forwarded_values")
        return typing.cast(typing.Optional["CloudfrontDistributionDefaultCacheBehaviorForwardedValues"], result)

    @builtins.property
    def function_association(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation"]]:
        '''function_association block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#function_association CloudfrontDistribution#function_association}
        '''
        result = self._values.get("function_association")
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation"]], result)

    @builtins.property
    def lambda_function_association(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation"]]:
        '''lambda_function_association block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#lambda_function_association CloudfrontDistribution#lambda_function_association}
        '''
        result = self._values.get("lambda_function_association")
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation"]], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#max_ttl CloudfrontDistribution#max_ttl}.'''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#min_ttl CloudfrontDistribution#min_ttl}.'''
        result = self._values.get("min_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def origin_request_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_request_policy_id CloudfrontDistribution#origin_request_policy_id}.'''
        result = self._values.get("origin_request_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def realtime_log_config_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#realtime_log_config_arn CloudfrontDistribution#realtime_log_config_arn}.'''
        result = self._values.get("realtime_log_config_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def response_headers_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#response_headers_policy_id CloudfrontDistribution#response_headers_policy_id}.'''
        result = self._values.get("response_headers_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def smooth_streaming(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#smooth_streaming CloudfrontDistribution#smooth_streaming}.'''
        result = self._values.get("smooth_streaming")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def trusted_key_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#trusted_key_groups CloudfrontDistribution#trusted_key_groups}.'''
        result = self._values.get("trusted_key_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def trusted_signers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#trusted_signers CloudfrontDistribution#trusted_signers}.'''
        result = self._values.get("trusted_signers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionDefaultCacheBehavior(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionDefaultCacheBehaviorForwardedValues",
    jsii_struct_bases=[],
    name_mapping={
        "cookies": "cookies",
        "query_string": "queryString",
        "headers": "headers",
        "query_string_cache_keys": "queryStringCacheKeys",
    },
)
class CloudfrontDistributionDefaultCacheBehaviorForwardedValues:
    def __init__(
        self,
        *,
        cookies: "CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies",
        query_string: typing.Union[builtins.bool, cdktf.IResolvable],
        headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_string_cache_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param cookies: cookies block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cookies CloudfrontDistribution#cookies}
        :param query_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#query_string CloudfrontDistribution#query_string}.
        :param headers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#headers CloudfrontDistribution#headers}.
        :param query_string_cache_keys: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#query_string_cache_keys CloudfrontDistribution#query_string_cache_keys}.
        '''
        if isinstance(cookies, dict):
            cookies = CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies(**cookies)
        self._values: typing.Dict[str, typing.Any] = {
            "cookies": cookies,
            "query_string": query_string,
        }
        if headers is not None:
            self._values["headers"] = headers
        if query_string_cache_keys is not None:
            self._values["query_string_cache_keys"] = query_string_cache_keys

    @builtins.property
    def cookies(
        self,
    ) -> "CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies":
        '''cookies block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cookies CloudfrontDistribution#cookies}
        '''
        result = self._values.get("cookies")
        assert result is not None, "Required property 'cookies' is missing"
        return typing.cast("CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies", result)

    @builtins.property
    def query_string(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#query_string CloudfrontDistribution#query_string}.'''
        result = self._values.get("query_string")
        assert result is not None, "Required property 'query_string' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#headers CloudfrontDistribution#headers}.'''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def query_string_cache_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#query_string_cache_keys CloudfrontDistribution#query_string_cache_keys}.'''
        result = self._values.get("query_string_cache_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionDefaultCacheBehaviorForwardedValues(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies",
    jsii_struct_bases=[],
    name_mapping={"forward": "forward", "whitelisted_names": "whitelistedNames"},
)
class CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies:
    def __init__(
        self,
        *,
        forward: builtins.str,
        whitelisted_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param forward: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forward CloudfrontDistribution#forward}.
        :param whitelisted_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#whitelisted_names CloudfrontDistribution#whitelisted_names}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "forward": forward,
        }
        if whitelisted_names is not None:
            self._values["whitelisted_names"] = whitelisted_names

    @builtins.property
    def forward(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forward CloudfrontDistribution#forward}.'''
        result = self._values.get("forward")
        assert result is not None, "Required property 'forward' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def whitelisted_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#whitelisted_names CloudfrontDistribution#whitelisted_names}.'''
        result = self._values.get("whitelisted_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetWhitelistedNames")
    def reset_whitelisted_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhitelistedNames", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forwardInput")
    def forward_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "forwardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="whitelistedNamesInput")
    def whitelisted_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "whitelistedNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forward")
    def forward(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "forward"))

    @forward.setter
    def forward(self, value: builtins.str) -> None:
        jsii.set(self, "forward", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="whitelistedNames")
    def whitelisted_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "whitelistedNames"))

    @whitelisted_names.setter
    def whitelisted_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "whitelistedNames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies]:
        return typing.cast(typing.Optional[CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontDistributionDefaultCacheBehaviorForwardedValuesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionDefaultCacheBehaviorForwardedValuesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putCookies")
    def put_cookies(
        self,
        *,
        forward: builtins.str,
        whitelisted_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param forward: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forward CloudfrontDistribution#forward}.
        :param whitelisted_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#whitelisted_names CloudfrontDistribution#whitelisted_names}.
        '''
        value = CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies(
            forward=forward, whitelisted_names=whitelisted_names
        )

        return typing.cast(None, jsii.invoke(self, "putCookies", [value]))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @jsii.member(jsii_name="resetQueryStringCacheKeys")
    def reset_query_string_cache_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryStringCacheKeys", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookies")
    def cookies(
        self,
    ) -> CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookiesOutputReference:
        return typing.cast(CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookiesOutputReference, jsii.get(self, "cookies"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookiesInput")
    def cookies_input(
        self,
    ) -> typing.Optional[CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies]:
        return typing.cast(typing.Optional[CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies], jsii.get(self, "cookiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersInput")
    def headers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "headersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringCacheKeysInput")
    def query_string_cache_keys_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "queryStringCacheKeysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringInput")
    def query_string_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "queryStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "headers"))

    @headers.setter
    def headers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "headers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryString")
    def query_string(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "queryString"))

    @query_string.setter
    def query_string(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "queryString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringCacheKeys")
    def query_string_cache_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "queryStringCacheKeys"))

    @query_string_cache_keys.setter
    def query_string_cache_keys(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "queryStringCacheKeys", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionDefaultCacheBehaviorForwardedValues]:
        return typing.cast(typing.Optional[CloudfrontDistributionDefaultCacheBehaviorForwardedValues], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionDefaultCacheBehaviorForwardedValues],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation",
    jsii_struct_bases=[],
    name_mapping={"event_type": "eventType", "function_arn": "functionArn"},
)
class CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation:
    def __init__(self, *, event_type: builtins.str, function_arn: builtins.str) -> None:
        '''
        :param event_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#event_type CloudfrontDistribution#event_type}.
        :param function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#function_arn CloudfrontDistribution#function_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "event_type": event_type,
            "function_arn": function_arn,
        }

    @builtins.property
    def event_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#event_type CloudfrontDistribution#event_type}.'''
        result = self._values.get("event_type")
        assert result is not None, "Required property 'event_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#function_arn CloudfrontDistribution#function_arn}.'''
        result = self._values.get("function_arn")
        assert result is not None, "Required property 'function_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation",
    jsii_struct_bases=[],
    name_mapping={
        "event_type": "eventType",
        "lambda_arn": "lambdaArn",
        "include_body": "includeBody",
    },
)
class CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation:
    def __init__(
        self,
        *,
        event_type: builtins.str,
        lambda_arn: builtins.str,
        include_body: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param event_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#event_type CloudfrontDistribution#event_type}.
        :param lambda_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#lambda_arn CloudfrontDistribution#lambda_arn}.
        :param include_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#include_body CloudfrontDistribution#include_body}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "event_type": event_type,
            "lambda_arn": lambda_arn,
        }
        if include_body is not None:
            self._values["include_body"] = include_body

    @builtins.property
    def event_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#event_type CloudfrontDistribution#event_type}.'''
        result = self._values.get("event_type")
        assert result is not None, "Required property 'event_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#lambda_arn CloudfrontDistribution#lambda_arn}.'''
        result = self._values.get("lambda_arn")
        assert result is not None, "Required property 'lambda_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def include_body(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#include_body CloudfrontDistribution#include_body}.'''
        result = self._values.get("include_body")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontDistributionDefaultCacheBehaviorOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionDefaultCacheBehaviorOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putForwardedValues")
    def put_forwarded_values(
        self,
        *,
        cookies: CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies,
        query_string: typing.Union[builtins.bool, cdktf.IResolvable],
        headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_string_cache_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param cookies: cookies block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cookies CloudfrontDistribution#cookies}
        :param query_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#query_string CloudfrontDistribution#query_string}.
        :param headers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#headers CloudfrontDistribution#headers}.
        :param query_string_cache_keys: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#query_string_cache_keys CloudfrontDistribution#query_string_cache_keys}.
        '''
        value = CloudfrontDistributionDefaultCacheBehaviorForwardedValues(
            cookies=cookies,
            query_string=query_string,
            headers=headers,
            query_string_cache_keys=query_string_cache_keys,
        )

        return typing.cast(None, jsii.invoke(self, "putForwardedValues", [value]))

    @jsii.member(jsii_name="resetCachePolicyId")
    def reset_cache_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCachePolicyId", []))

    @jsii.member(jsii_name="resetCompress")
    def reset_compress(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompress", []))

    @jsii.member(jsii_name="resetDefaultTtl")
    def reset_default_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTtl", []))

    @jsii.member(jsii_name="resetFieldLevelEncryptionId")
    def reset_field_level_encryption_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFieldLevelEncryptionId", []))

    @jsii.member(jsii_name="resetForwardedValues")
    def reset_forwarded_values(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForwardedValues", []))

    @jsii.member(jsii_name="resetFunctionAssociation")
    def reset_function_association(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunctionAssociation", []))

    @jsii.member(jsii_name="resetLambdaFunctionAssociation")
    def reset_lambda_function_association(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambdaFunctionAssociation", []))

    @jsii.member(jsii_name="resetMaxTtl")
    def reset_max_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTtl", []))

    @jsii.member(jsii_name="resetMinTtl")
    def reset_min_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinTtl", []))

    @jsii.member(jsii_name="resetOriginRequestPolicyId")
    def reset_origin_request_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginRequestPolicyId", []))

    @jsii.member(jsii_name="resetRealtimeLogConfigArn")
    def reset_realtime_log_config_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRealtimeLogConfigArn", []))

    @jsii.member(jsii_name="resetResponseHeadersPolicyId")
    def reset_response_headers_policy_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseHeadersPolicyId", []))

    @jsii.member(jsii_name="resetSmoothStreaming")
    def reset_smooth_streaming(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmoothStreaming", []))

    @jsii.member(jsii_name="resetTrustedKeyGroups")
    def reset_trusted_key_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrustedKeyGroups", []))

    @jsii.member(jsii_name="resetTrustedSigners")
    def reset_trusted_signers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrustedSigners", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forwardedValues")
    def forwarded_values(
        self,
    ) -> CloudfrontDistributionDefaultCacheBehaviorForwardedValuesOutputReference:
        return typing.cast(CloudfrontDistributionDefaultCacheBehaviorForwardedValuesOutputReference, jsii.get(self, "forwardedValues"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedMethodsInput")
    def allowed_methods_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedMethodsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cachedMethodsInput")
    def cached_methods_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cachedMethodsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cachePolicyIdInput")
    def cache_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cachePolicyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compressInput")
    def compress_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "compressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTtlInput")
    def default_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultTtlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldLevelEncryptionIdInput")
    def field_level_encryption_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldLevelEncryptionIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forwardedValuesInput")
    def forwarded_values_input(
        self,
    ) -> typing.Optional[CloudfrontDistributionDefaultCacheBehaviorForwardedValues]:
        return typing.cast(typing.Optional[CloudfrontDistributionDefaultCacheBehaviorForwardedValues], jsii.get(self, "forwardedValuesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionAssociationInput")
    def function_association_input(
        self,
    ) -> typing.Optional[typing.List[CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation]]:
        return typing.cast(typing.Optional[typing.List[CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation]], jsii.get(self, "functionAssociationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunctionAssociationInput")
    def lambda_function_association_input(
        self,
    ) -> typing.Optional[typing.List[CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation]]:
        return typing.cast(typing.Optional[typing.List[CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation]], jsii.get(self, "lambdaFunctionAssociationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxTtlInput")
    def max_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTtlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minTtlInput")
    def min_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minTtlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originRequestPolicyIdInput")
    def origin_request_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "originRequestPolicyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="realtimeLogConfigArnInput")
    def realtime_log_config_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "realtimeLogConfigArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseHeadersPolicyIdInput")
    def response_headers_policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseHeadersPolicyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smoothStreamingInput")
    def smooth_streaming_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "smoothStreamingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetOriginIdInput")
    def target_origin_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetOriginIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trustedKeyGroupsInput")
    def trusted_key_groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "trustedKeyGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trustedSignersInput")
    def trusted_signers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "trustedSignersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="viewerProtocolPolicyInput")
    def viewer_protocol_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "viewerProtocolPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedMethods")
    def allowed_methods(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedMethods"))

    @allowed_methods.setter
    def allowed_methods(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "allowedMethods", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cachedMethods")
    def cached_methods(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cachedMethods"))

    @cached_methods.setter
    def cached_methods(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "cachedMethods", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cachePolicyId")
    def cache_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cachePolicyId"))

    @cache_policy_id.setter
    def cache_policy_id(self, value: builtins.str) -> None:
        jsii.set(self, "cachePolicyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="compress")
    def compress(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "compress"))

    @compress.setter
    def compress(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "compress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTtl")
    def default_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultTtl"))

    @default_ttl.setter
    def default_ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "defaultTtl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldLevelEncryptionId")
    def field_level_encryption_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fieldLevelEncryptionId"))

    @field_level_encryption_id.setter
    def field_level_encryption_id(self, value: builtins.str) -> None:
        jsii.set(self, "fieldLevelEncryptionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionAssociation")
    def function_association(
        self,
    ) -> typing.List[CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation]:
        return typing.cast(typing.List[CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation], jsii.get(self, "functionAssociation"))

    @function_association.setter
    def function_association(
        self,
        value: typing.List[CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation],
    ) -> None:
        jsii.set(self, "functionAssociation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunctionAssociation")
    def lambda_function_association(
        self,
    ) -> typing.List[CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation]:
        return typing.cast(typing.List[CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation], jsii.get(self, "lambdaFunctionAssociation"))

    @lambda_function_association.setter
    def lambda_function_association(
        self,
        value: typing.List[CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation],
    ) -> None:
        jsii.set(self, "lambdaFunctionAssociation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTtl"))

    @max_ttl.setter
    def max_ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "maxTtl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minTtl")
    def min_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minTtl"))

    @min_ttl.setter
    def min_ttl(self, value: jsii.Number) -> None:
        jsii.set(self, "minTtl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originRequestPolicyId")
    def origin_request_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "originRequestPolicyId"))

    @origin_request_policy_id.setter
    def origin_request_policy_id(self, value: builtins.str) -> None:
        jsii.set(self, "originRequestPolicyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="realtimeLogConfigArn")
    def realtime_log_config_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "realtimeLogConfigArn"))

    @realtime_log_config_arn.setter
    def realtime_log_config_arn(self, value: builtins.str) -> None:
        jsii.set(self, "realtimeLogConfigArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="responseHeadersPolicyId")
    def response_headers_policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseHeadersPolicyId"))

    @response_headers_policy_id.setter
    def response_headers_policy_id(self, value: builtins.str) -> None:
        jsii.set(self, "responseHeadersPolicyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="smoothStreaming")
    def smooth_streaming(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "smoothStreaming"))

    @smooth_streaming.setter
    def smooth_streaming(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "smoothStreaming", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetOriginId")
    def target_origin_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetOriginId"))

    @target_origin_id.setter
    def target_origin_id(self, value: builtins.str) -> None:
        jsii.set(self, "targetOriginId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trustedKeyGroups")
    def trusted_key_groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "trustedKeyGroups"))

    @trusted_key_groups.setter
    def trusted_key_groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "trustedKeyGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trustedSigners")
    def trusted_signers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "trustedSigners"))

    @trusted_signers.setter
    def trusted_signers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "trustedSigners", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="viewerProtocolPolicy")
    def viewer_protocol_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "viewerProtocolPolicy"))

    @viewer_protocol_policy.setter
    def viewer_protocol_policy(self, value: builtins.str) -> None:
        jsii.set(self, "viewerProtocolPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionDefaultCacheBehavior]:
        return typing.cast(typing.Optional[CloudfrontDistributionDefaultCacheBehavior], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionDefaultCacheBehavior],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionLoggingConfig",
    jsii_struct_bases=[],
    name_mapping={
        "bucket": "bucket",
        "include_cookies": "includeCookies",
        "prefix": "prefix",
    },
)
class CloudfrontDistributionLoggingConfig:
    def __init__(
        self,
        *,
        bucket: builtins.str,
        include_cookies: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#bucket CloudfrontDistribution#bucket}.
        :param include_cookies: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#include_cookies CloudfrontDistribution#include_cookies}.
        :param prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#prefix CloudfrontDistribution#prefix}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
        }
        if include_cookies is not None:
            self._values["include_cookies"] = include_cookies
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#bucket CloudfrontDistribution#bucket}.'''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def include_cookies(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#include_cookies CloudfrontDistribution#include_cookies}.'''
        result = self._values.get("include_cookies")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#prefix CloudfrontDistribution#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionLoggingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontDistributionLoggingConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionLoggingConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetIncludeCookies")
    def reset_include_cookies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeCookies", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeCookiesInput")
    def include_cookies_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeCookiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        jsii.set(self, "bucket", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeCookies")
    def include_cookies(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeCookies"))

    @include_cookies.setter
    def include_cookies(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeCookies", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudfrontDistributionLoggingConfig]:
        return typing.cast(typing.Optional[CloudfrontDistributionLoggingConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionLoggingConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOrderedCacheBehavior",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_methods": "allowedMethods",
        "cached_methods": "cachedMethods",
        "path_pattern": "pathPattern",
        "target_origin_id": "targetOriginId",
        "viewer_protocol_policy": "viewerProtocolPolicy",
        "cache_policy_id": "cachePolicyId",
        "compress": "compress",
        "default_ttl": "defaultTtl",
        "field_level_encryption_id": "fieldLevelEncryptionId",
        "forwarded_values": "forwardedValues",
        "function_association": "functionAssociation",
        "lambda_function_association": "lambdaFunctionAssociation",
        "max_ttl": "maxTtl",
        "min_ttl": "minTtl",
        "origin_request_policy_id": "originRequestPolicyId",
        "realtime_log_config_arn": "realtimeLogConfigArn",
        "response_headers_policy_id": "responseHeadersPolicyId",
        "smooth_streaming": "smoothStreaming",
        "trusted_key_groups": "trustedKeyGroups",
        "trusted_signers": "trustedSigners",
    },
)
class CloudfrontDistributionOrderedCacheBehavior:
    def __init__(
        self,
        *,
        allowed_methods: typing.Sequence[builtins.str],
        cached_methods: typing.Sequence[builtins.str],
        path_pattern: builtins.str,
        target_origin_id: builtins.str,
        viewer_protocol_policy: builtins.str,
        cache_policy_id: typing.Optional[builtins.str] = None,
        compress: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        default_ttl: typing.Optional[jsii.Number] = None,
        field_level_encryption_id: typing.Optional[builtins.str] = None,
        forwarded_values: typing.Optional["CloudfrontDistributionOrderedCacheBehaviorForwardedValues"] = None,
        function_association: typing.Optional[typing.Sequence["CloudfrontDistributionOrderedCacheBehaviorFunctionAssociation"]] = None,
        lambda_function_association: typing.Optional[typing.Sequence["CloudfrontDistributionOrderedCacheBehaviorLambdaFunctionAssociation"]] = None,
        max_ttl: typing.Optional[jsii.Number] = None,
        min_ttl: typing.Optional[jsii.Number] = None,
        origin_request_policy_id: typing.Optional[builtins.str] = None,
        realtime_log_config_arn: typing.Optional[builtins.str] = None,
        response_headers_policy_id: typing.Optional[builtins.str] = None,
        smooth_streaming: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        trusted_signers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allowed_methods: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#allowed_methods CloudfrontDistribution#allowed_methods}.
        :param cached_methods: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cached_methods CloudfrontDistribution#cached_methods}.
        :param path_pattern: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#path_pattern CloudfrontDistribution#path_pattern}.
        :param target_origin_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#target_origin_id CloudfrontDistribution#target_origin_id}.
        :param viewer_protocol_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#viewer_protocol_policy CloudfrontDistribution#viewer_protocol_policy}.
        :param cache_policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cache_policy_id CloudfrontDistribution#cache_policy_id}.
        :param compress: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#compress CloudfrontDistribution#compress}.
        :param default_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_ttl CloudfrontDistribution#default_ttl}.
        :param field_level_encryption_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#field_level_encryption_id CloudfrontDistribution#field_level_encryption_id}.
        :param forwarded_values: forwarded_values block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forwarded_values CloudfrontDistribution#forwarded_values}
        :param function_association: function_association block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#function_association CloudfrontDistribution#function_association}
        :param lambda_function_association: lambda_function_association block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#lambda_function_association CloudfrontDistribution#lambda_function_association}
        :param max_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#max_ttl CloudfrontDistribution#max_ttl}.
        :param min_ttl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#min_ttl CloudfrontDistribution#min_ttl}.
        :param origin_request_policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_request_policy_id CloudfrontDistribution#origin_request_policy_id}.
        :param realtime_log_config_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#realtime_log_config_arn CloudfrontDistribution#realtime_log_config_arn}.
        :param response_headers_policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#response_headers_policy_id CloudfrontDistribution#response_headers_policy_id}.
        :param smooth_streaming: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#smooth_streaming CloudfrontDistribution#smooth_streaming}.
        :param trusted_key_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#trusted_key_groups CloudfrontDistribution#trusted_key_groups}.
        :param trusted_signers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#trusted_signers CloudfrontDistribution#trusted_signers}.
        '''
        if isinstance(forwarded_values, dict):
            forwarded_values = CloudfrontDistributionOrderedCacheBehaviorForwardedValues(**forwarded_values)
        self._values: typing.Dict[str, typing.Any] = {
            "allowed_methods": allowed_methods,
            "cached_methods": cached_methods,
            "path_pattern": path_pattern,
            "target_origin_id": target_origin_id,
            "viewer_protocol_policy": viewer_protocol_policy,
        }
        if cache_policy_id is not None:
            self._values["cache_policy_id"] = cache_policy_id
        if compress is not None:
            self._values["compress"] = compress
        if default_ttl is not None:
            self._values["default_ttl"] = default_ttl
        if field_level_encryption_id is not None:
            self._values["field_level_encryption_id"] = field_level_encryption_id
        if forwarded_values is not None:
            self._values["forwarded_values"] = forwarded_values
        if function_association is not None:
            self._values["function_association"] = function_association
        if lambda_function_association is not None:
            self._values["lambda_function_association"] = lambda_function_association
        if max_ttl is not None:
            self._values["max_ttl"] = max_ttl
        if min_ttl is not None:
            self._values["min_ttl"] = min_ttl
        if origin_request_policy_id is not None:
            self._values["origin_request_policy_id"] = origin_request_policy_id
        if realtime_log_config_arn is not None:
            self._values["realtime_log_config_arn"] = realtime_log_config_arn
        if response_headers_policy_id is not None:
            self._values["response_headers_policy_id"] = response_headers_policy_id
        if smooth_streaming is not None:
            self._values["smooth_streaming"] = smooth_streaming
        if trusted_key_groups is not None:
            self._values["trusted_key_groups"] = trusted_key_groups
        if trusted_signers is not None:
            self._values["trusted_signers"] = trusted_signers

    @builtins.property
    def allowed_methods(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#allowed_methods CloudfrontDistribution#allowed_methods}.'''
        result = self._values.get("allowed_methods")
        assert result is not None, "Required property 'allowed_methods' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def cached_methods(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cached_methods CloudfrontDistribution#cached_methods}.'''
        result = self._values.get("cached_methods")
        assert result is not None, "Required property 'cached_methods' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def path_pattern(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#path_pattern CloudfrontDistribution#path_pattern}.'''
        result = self._values.get("path_pattern")
        assert result is not None, "Required property 'path_pattern' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_origin_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#target_origin_id CloudfrontDistribution#target_origin_id}.'''
        result = self._values.get("target_origin_id")
        assert result is not None, "Required property 'target_origin_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def viewer_protocol_policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#viewer_protocol_policy CloudfrontDistribution#viewer_protocol_policy}.'''
        result = self._values.get("viewer_protocol_policy")
        assert result is not None, "Required property 'viewer_protocol_policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cache_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cache_policy_id CloudfrontDistribution#cache_policy_id}.'''
        result = self._values.get("cache_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compress(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#compress CloudfrontDistribution#compress}.'''
        result = self._values.get("compress")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def default_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#default_ttl CloudfrontDistribution#default_ttl}.'''
        result = self._values.get("default_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def field_level_encryption_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#field_level_encryption_id CloudfrontDistribution#field_level_encryption_id}.'''
        result = self._values.get("field_level_encryption_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def forwarded_values(
        self,
    ) -> typing.Optional["CloudfrontDistributionOrderedCacheBehaviorForwardedValues"]:
        '''forwarded_values block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forwarded_values CloudfrontDistribution#forwarded_values}
        '''
        result = self._values.get("forwarded_values")
        return typing.cast(typing.Optional["CloudfrontDistributionOrderedCacheBehaviorForwardedValues"], result)

    @builtins.property
    def function_association(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionOrderedCacheBehaviorFunctionAssociation"]]:
        '''function_association block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#function_association CloudfrontDistribution#function_association}
        '''
        result = self._values.get("function_association")
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionOrderedCacheBehaviorFunctionAssociation"]], result)

    @builtins.property
    def lambda_function_association(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionOrderedCacheBehaviorLambdaFunctionAssociation"]]:
        '''lambda_function_association block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#lambda_function_association CloudfrontDistribution#lambda_function_association}
        '''
        result = self._values.get("lambda_function_association")
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionOrderedCacheBehaviorLambdaFunctionAssociation"]], result)

    @builtins.property
    def max_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#max_ttl CloudfrontDistribution#max_ttl}.'''
        result = self._values.get("max_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_ttl(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#min_ttl CloudfrontDistribution#min_ttl}.'''
        result = self._values.get("min_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def origin_request_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_request_policy_id CloudfrontDistribution#origin_request_policy_id}.'''
        result = self._values.get("origin_request_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def realtime_log_config_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#realtime_log_config_arn CloudfrontDistribution#realtime_log_config_arn}.'''
        result = self._values.get("realtime_log_config_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def response_headers_policy_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#response_headers_policy_id CloudfrontDistribution#response_headers_policy_id}.'''
        result = self._values.get("response_headers_policy_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def smooth_streaming(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#smooth_streaming CloudfrontDistribution#smooth_streaming}.'''
        result = self._values.get("smooth_streaming")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def trusted_key_groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#trusted_key_groups CloudfrontDistribution#trusted_key_groups}.'''
        result = self._values.get("trusted_key_groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def trusted_signers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#trusted_signers CloudfrontDistribution#trusted_signers}.'''
        result = self._values.get("trusted_signers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOrderedCacheBehavior(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOrderedCacheBehaviorForwardedValues",
    jsii_struct_bases=[],
    name_mapping={
        "cookies": "cookies",
        "query_string": "queryString",
        "headers": "headers",
        "query_string_cache_keys": "queryStringCacheKeys",
    },
)
class CloudfrontDistributionOrderedCacheBehaviorForwardedValues:
    def __init__(
        self,
        *,
        cookies: "CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies",
        query_string: typing.Union[builtins.bool, cdktf.IResolvable],
        headers: typing.Optional[typing.Sequence[builtins.str]] = None,
        query_string_cache_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param cookies: cookies block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cookies CloudfrontDistribution#cookies}
        :param query_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#query_string CloudfrontDistribution#query_string}.
        :param headers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#headers CloudfrontDistribution#headers}.
        :param query_string_cache_keys: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#query_string_cache_keys CloudfrontDistribution#query_string_cache_keys}.
        '''
        if isinstance(cookies, dict):
            cookies = CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies(**cookies)
        self._values: typing.Dict[str, typing.Any] = {
            "cookies": cookies,
            "query_string": query_string,
        }
        if headers is not None:
            self._values["headers"] = headers
        if query_string_cache_keys is not None:
            self._values["query_string_cache_keys"] = query_string_cache_keys

    @builtins.property
    def cookies(
        self,
    ) -> "CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies":
        '''cookies block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cookies CloudfrontDistribution#cookies}
        '''
        result = self._values.get("cookies")
        assert result is not None, "Required property 'cookies' is missing"
        return typing.cast("CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies", result)

    @builtins.property
    def query_string(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#query_string CloudfrontDistribution#query_string}.'''
        result = self._values.get("query_string")
        assert result is not None, "Required property 'query_string' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def headers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#headers CloudfrontDistribution#headers}.'''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def query_string_cache_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#query_string_cache_keys CloudfrontDistribution#query_string_cache_keys}.'''
        result = self._values.get("query_string_cache_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOrderedCacheBehaviorForwardedValues(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies",
    jsii_struct_bases=[],
    name_mapping={"forward": "forward", "whitelisted_names": "whitelistedNames"},
)
class CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies:
    def __init__(
        self,
        *,
        forward: builtins.str,
        whitelisted_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param forward: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forward CloudfrontDistribution#forward}.
        :param whitelisted_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#whitelisted_names CloudfrontDistribution#whitelisted_names}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "forward": forward,
        }
        if whitelisted_names is not None:
            self._values["whitelisted_names"] = whitelisted_names

    @builtins.property
    def forward(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forward CloudfrontDistribution#forward}.'''
        result = self._values.get("forward")
        assert result is not None, "Required property 'forward' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def whitelisted_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#whitelisted_names CloudfrontDistribution#whitelisted_names}.'''
        result = self._values.get("whitelisted_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetWhitelistedNames")
    def reset_whitelisted_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWhitelistedNames", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forwardInput")
    def forward_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "forwardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="whitelistedNamesInput")
    def whitelisted_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "whitelistedNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forward")
    def forward(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "forward"))

    @forward.setter
    def forward(self, value: builtins.str) -> None:
        jsii.set(self, "forward", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="whitelistedNames")
    def whitelisted_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "whitelistedNames"))

    @whitelisted_names.setter
    def whitelisted_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "whitelistedNames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies]:
        return typing.cast(typing.Optional[CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontDistributionOrderedCacheBehaviorForwardedValuesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOrderedCacheBehaviorForwardedValuesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putCookies")
    def put_cookies(
        self,
        *,
        forward: builtins.str,
        whitelisted_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param forward: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#forward CloudfrontDistribution#forward}.
        :param whitelisted_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#whitelisted_names CloudfrontDistribution#whitelisted_names}.
        '''
        value = CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies(
            forward=forward, whitelisted_names=whitelisted_names
        )

        return typing.cast(None, jsii.invoke(self, "putCookies", [value]))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @jsii.member(jsii_name="resetQueryStringCacheKeys")
    def reset_query_string_cache_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryStringCacheKeys", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookies")
    def cookies(
        self,
    ) -> CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookiesOutputReference:
        return typing.cast(CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookiesOutputReference, jsii.get(self, "cookies"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookiesInput")
    def cookies_input(
        self,
    ) -> typing.Optional[CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies]:
        return typing.cast(typing.Optional[CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies], jsii.get(self, "cookiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersInput")
    def headers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "headersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringCacheKeysInput")
    def query_string_cache_keys_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "queryStringCacheKeysInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringInput")
    def query_string_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "queryStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "headers"))

    @headers.setter
    def headers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "headers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryString")
    def query_string(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "queryString"))

    @query_string.setter
    def query_string(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "queryString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringCacheKeys")
    def query_string_cache_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "queryStringCacheKeys"))

    @query_string_cache_keys.setter
    def query_string_cache_keys(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "queryStringCacheKeys", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionOrderedCacheBehaviorForwardedValues]:
        return typing.cast(typing.Optional[CloudfrontDistributionOrderedCacheBehaviorForwardedValues], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionOrderedCacheBehaviorForwardedValues],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOrderedCacheBehaviorFunctionAssociation",
    jsii_struct_bases=[],
    name_mapping={"event_type": "eventType", "function_arn": "functionArn"},
)
class CloudfrontDistributionOrderedCacheBehaviorFunctionAssociation:
    def __init__(self, *, event_type: builtins.str, function_arn: builtins.str) -> None:
        '''
        :param event_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#event_type CloudfrontDistribution#event_type}.
        :param function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#function_arn CloudfrontDistribution#function_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "event_type": event_type,
            "function_arn": function_arn,
        }

    @builtins.property
    def event_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#event_type CloudfrontDistribution#event_type}.'''
        result = self._values.get("event_type")
        assert result is not None, "Required property 'event_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#function_arn CloudfrontDistribution#function_arn}.'''
        result = self._values.get("function_arn")
        assert result is not None, "Required property 'function_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOrderedCacheBehaviorFunctionAssociation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOrderedCacheBehaviorLambdaFunctionAssociation",
    jsii_struct_bases=[],
    name_mapping={
        "event_type": "eventType",
        "lambda_arn": "lambdaArn",
        "include_body": "includeBody",
    },
)
class CloudfrontDistributionOrderedCacheBehaviorLambdaFunctionAssociation:
    def __init__(
        self,
        *,
        event_type: builtins.str,
        lambda_arn: builtins.str,
        include_body: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param event_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#event_type CloudfrontDistribution#event_type}.
        :param lambda_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#lambda_arn CloudfrontDistribution#lambda_arn}.
        :param include_body: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#include_body CloudfrontDistribution#include_body}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "event_type": event_type,
            "lambda_arn": lambda_arn,
        }
        if include_body is not None:
            self._values["include_body"] = include_body

    @builtins.property
    def event_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#event_type CloudfrontDistribution#event_type}.'''
        result = self._values.get("event_type")
        assert result is not None, "Required property 'event_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lambda_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#lambda_arn CloudfrontDistribution#lambda_arn}.'''
        result = self._values.get("lambda_arn")
        assert result is not None, "Required property 'lambda_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def include_body(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#include_body CloudfrontDistribution#include_body}.'''
        result = self._values.get("include_body")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOrderedCacheBehaviorLambdaFunctionAssociation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOrigin",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "origin_id": "originId",
        "connection_attempts": "connectionAttempts",
        "connection_timeout": "connectionTimeout",
        "custom_header": "customHeader",
        "custom_origin_config": "customOriginConfig",
        "origin_path": "originPath",
        "origin_shield": "originShield",
        "s3_origin_config": "s3OriginConfig",
    },
)
class CloudfrontDistributionOrigin:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        origin_id: builtins.str,
        connection_attempts: typing.Optional[jsii.Number] = None,
        connection_timeout: typing.Optional[jsii.Number] = None,
        custom_header: typing.Optional[typing.Sequence["CloudfrontDistributionOriginCustomHeader"]] = None,
        custom_origin_config: typing.Optional["CloudfrontDistributionOriginCustomOriginConfig"] = None,
        origin_path: typing.Optional[builtins.str] = None,
        origin_shield: typing.Optional["CloudfrontDistributionOriginOriginShield"] = None,
        s3_origin_config: typing.Optional["CloudfrontDistributionOriginS3OriginConfig"] = None,
    ) -> None:
        '''
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#domain_name CloudfrontDistribution#domain_name}.
        :param origin_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_id CloudfrontDistribution#origin_id}.
        :param connection_attempts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#connection_attempts CloudfrontDistribution#connection_attempts}.
        :param connection_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#connection_timeout CloudfrontDistribution#connection_timeout}.
        :param custom_header: custom_header block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#custom_header CloudfrontDistribution#custom_header}
        :param custom_origin_config: custom_origin_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#custom_origin_config CloudfrontDistribution#custom_origin_config}
        :param origin_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_path CloudfrontDistribution#origin_path}.
        :param origin_shield: origin_shield block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_shield CloudfrontDistribution#origin_shield}
        :param s3_origin_config: s3_origin_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#s3_origin_config CloudfrontDistribution#s3_origin_config}
        '''
        if isinstance(custom_origin_config, dict):
            custom_origin_config = CloudfrontDistributionOriginCustomOriginConfig(**custom_origin_config)
        if isinstance(origin_shield, dict):
            origin_shield = CloudfrontDistributionOriginOriginShield(**origin_shield)
        if isinstance(s3_origin_config, dict):
            s3_origin_config = CloudfrontDistributionOriginS3OriginConfig(**s3_origin_config)
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
            "origin_id": origin_id,
        }
        if connection_attempts is not None:
            self._values["connection_attempts"] = connection_attempts
        if connection_timeout is not None:
            self._values["connection_timeout"] = connection_timeout
        if custom_header is not None:
            self._values["custom_header"] = custom_header
        if custom_origin_config is not None:
            self._values["custom_origin_config"] = custom_origin_config
        if origin_path is not None:
            self._values["origin_path"] = origin_path
        if origin_shield is not None:
            self._values["origin_shield"] = origin_shield
        if s3_origin_config is not None:
            self._values["s3_origin_config"] = s3_origin_config

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#domain_name CloudfrontDistribution#domain_name}.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def origin_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_id CloudfrontDistribution#origin_id}.'''
        result = self._values.get("origin_id")
        assert result is not None, "Required property 'origin_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connection_attempts(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#connection_attempts CloudfrontDistribution#connection_attempts}.'''
        result = self._values.get("connection_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def connection_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#connection_timeout CloudfrontDistribution#connection_timeout}.'''
        result = self._values.get("connection_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def custom_header(
        self,
    ) -> typing.Optional[typing.List["CloudfrontDistributionOriginCustomHeader"]]:
        '''custom_header block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#custom_header CloudfrontDistribution#custom_header}
        '''
        result = self._values.get("custom_header")
        return typing.cast(typing.Optional[typing.List["CloudfrontDistributionOriginCustomHeader"]], result)

    @builtins.property
    def custom_origin_config(
        self,
    ) -> typing.Optional["CloudfrontDistributionOriginCustomOriginConfig"]:
        '''custom_origin_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#custom_origin_config CloudfrontDistribution#custom_origin_config}
        '''
        result = self._values.get("custom_origin_config")
        return typing.cast(typing.Optional["CloudfrontDistributionOriginCustomOriginConfig"], result)

    @builtins.property
    def origin_path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_path CloudfrontDistribution#origin_path}.'''
        result = self._values.get("origin_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origin_shield(
        self,
    ) -> typing.Optional["CloudfrontDistributionOriginOriginShield"]:
        '''origin_shield block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_shield CloudfrontDistribution#origin_shield}
        '''
        result = self._values.get("origin_shield")
        return typing.cast(typing.Optional["CloudfrontDistributionOriginOriginShield"], result)

    @builtins.property
    def s3_origin_config(
        self,
    ) -> typing.Optional["CloudfrontDistributionOriginS3OriginConfig"]:
        '''s3_origin_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#s3_origin_config CloudfrontDistribution#s3_origin_config}
        '''
        result = self._values.get("s3_origin_config")
        return typing.cast(typing.Optional["CloudfrontDistributionOriginS3OriginConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOrigin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginCustomHeader",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class CloudfrontDistributionOriginCustomHeader:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#name CloudfrontDistribution#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#value CloudfrontDistribution#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#name CloudfrontDistribution#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#value CloudfrontDistribution#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOriginCustomHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginCustomOriginConfig",
    jsii_struct_bases=[],
    name_mapping={
        "http_port": "httpPort",
        "https_port": "httpsPort",
        "origin_protocol_policy": "originProtocolPolicy",
        "origin_ssl_protocols": "originSslProtocols",
        "origin_keepalive_timeout": "originKeepaliveTimeout",
        "origin_read_timeout": "originReadTimeout",
    },
)
class CloudfrontDistributionOriginCustomOriginConfig:
    def __init__(
        self,
        *,
        http_port: jsii.Number,
        https_port: jsii.Number,
        origin_protocol_policy: builtins.str,
        origin_ssl_protocols: typing.Sequence[builtins.str],
        origin_keepalive_timeout: typing.Optional[jsii.Number] = None,
        origin_read_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param http_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#http_port CloudfrontDistribution#http_port}.
        :param https_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#https_port CloudfrontDistribution#https_port}.
        :param origin_protocol_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_protocol_policy CloudfrontDistribution#origin_protocol_policy}.
        :param origin_ssl_protocols: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_ssl_protocols CloudfrontDistribution#origin_ssl_protocols}.
        :param origin_keepalive_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_keepalive_timeout CloudfrontDistribution#origin_keepalive_timeout}.
        :param origin_read_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_read_timeout CloudfrontDistribution#origin_read_timeout}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "http_port": http_port,
            "https_port": https_port,
            "origin_protocol_policy": origin_protocol_policy,
            "origin_ssl_protocols": origin_ssl_protocols,
        }
        if origin_keepalive_timeout is not None:
            self._values["origin_keepalive_timeout"] = origin_keepalive_timeout
        if origin_read_timeout is not None:
            self._values["origin_read_timeout"] = origin_read_timeout

    @builtins.property
    def http_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#http_port CloudfrontDistribution#http_port}.'''
        result = self._values.get("http_port")
        assert result is not None, "Required property 'http_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def https_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#https_port CloudfrontDistribution#https_port}.'''
        result = self._values.get("https_port")
        assert result is not None, "Required property 'https_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def origin_protocol_policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_protocol_policy CloudfrontDistribution#origin_protocol_policy}.'''
        result = self._values.get("origin_protocol_policy")
        assert result is not None, "Required property 'origin_protocol_policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def origin_ssl_protocols(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_ssl_protocols CloudfrontDistribution#origin_ssl_protocols}.'''
        result = self._values.get("origin_ssl_protocols")
        assert result is not None, "Required property 'origin_ssl_protocols' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def origin_keepalive_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_keepalive_timeout CloudfrontDistribution#origin_keepalive_timeout}.'''
        result = self._values.get("origin_keepalive_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def origin_read_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_read_timeout CloudfrontDistribution#origin_read_timeout}.'''
        result = self._values.get("origin_read_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOriginCustomOriginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontDistributionOriginCustomOriginConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginCustomOriginConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetOriginKeepaliveTimeout")
    def reset_origin_keepalive_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginKeepaliveTimeout", []))

    @jsii.member(jsii_name="resetOriginReadTimeout")
    def reset_origin_read_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginReadTimeout", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpPortInput")
    def http_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpsPortInput")
    def https_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpsPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originKeepaliveTimeoutInput")
    def origin_keepalive_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "originKeepaliveTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originProtocolPolicyInput")
    def origin_protocol_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "originProtocolPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originReadTimeoutInput")
    def origin_read_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "originReadTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originSslProtocolsInput")
    def origin_ssl_protocols_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "originSslProtocolsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpPort")
    def http_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpPort"))

    @http_port.setter
    def http_port(self, value: jsii.Number) -> None:
        jsii.set(self, "httpPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpsPort")
    def https_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpsPort"))

    @https_port.setter
    def https_port(self, value: jsii.Number) -> None:
        jsii.set(self, "httpsPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originKeepaliveTimeout")
    def origin_keepalive_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "originKeepaliveTimeout"))

    @origin_keepalive_timeout.setter
    def origin_keepalive_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "originKeepaliveTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originProtocolPolicy")
    def origin_protocol_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "originProtocolPolicy"))

    @origin_protocol_policy.setter
    def origin_protocol_policy(self, value: builtins.str) -> None:
        jsii.set(self, "originProtocolPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originReadTimeout")
    def origin_read_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "originReadTimeout"))

    @origin_read_timeout.setter
    def origin_read_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "originReadTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originSslProtocols")
    def origin_ssl_protocols(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "originSslProtocols"))

    @origin_ssl_protocols.setter
    def origin_ssl_protocols(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "originSslProtocols", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionOriginCustomOriginConfig]:
        return typing.cast(typing.Optional[CloudfrontDistributionOriginCustomOriginConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionOriginCustomOriginConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginGroup",
    jsii_struct_bases=[],
    name_mapping={
        "failover_criteria": "failoverCriteria",
        "member": "member",
        "origin_id": "originId",
    },
)
class CloudfrontDistributionOriginGroup:
    def __init__(
        self,
        *,
        failover_criteria: "CloudfrontDistributionOriginGroupFailoverCriteria",
        member: typing.Sequence["CloudfrontDistributionOriginGroupMember"],
        origin_id: builtins.str,
    ) -> None:
        '''
        :param failover_criteria: failover_criteria block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#failover_criteria CloudfrontDistribution#failover_criteria}
        :param member: member block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#member CloudfrontDistribution#member}
        :param origin_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_id CloudfrontDistribution#origin_id}.
        '''
        if isinstance(failover_criteria, dict):
            failover_criteria = CloudfrontDistributionOriginGroupFailoverCriteria(**failover_criteria)
        self._values: typing.Dict[str, typing.Any] = {
            "failover_criteria": failover_criteria,
            "member": member,
            "origin_id": origin_id,
        }

    @builtins.property
    def failover_criteria(self) -> "CloudfrontDistributionOriginGroupFailoverCriteria":
        '''failover_criteria block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#failover_criteria CloudfrontDistribution#failover_criteria}
        '''
        result = self._values.get("failover_criteria")
        assert result is not None, "Required property 'failover_criteria' is missing"
        return typing.cast("CloudfrontDistributionOriginGroupFailoverCriteria", result)

    @builtins.property
    def member(self) -> typing.List["CloudfrontDistributionOriginGroupMember"]:
        '''member block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#member CloudfrontDistribution#member}
        '''
        result = self._values.get("member")
        assert result is not None, "Required property 'member' is missing"
        return typing.cast(typing.List["CloudfrontDistributionOriginGroupMember"], result)

    @builtins.property
    def origin_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_id CloudfrontDistribution#origin_id}.'''
        result = self._values.get("origin_id")
        assert result is not None, "Required property 'origin_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOriginGroup(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginGroupFailoverCriteria",
    jsii_struct_bases=[],
    name_mapping={"status_codes": "statusCodes"},
)
class CloudfrontDistributionOriginGroupFailoverCriteria:
    def __init__(self, *, status_codes: typing.Sequence[jsii.Number]) -> None:
        '''
        :param status_codes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#status_codes CloudfrontDistribution#status_codes}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "status_codes": status_codes,
        }

    @builtins.property
    def status_codes(self) -> typing.List[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#status_codes CloudfrontDistribution#status_codes}.'''
        result = self._values.get("status_codes")
        assert result is not None, "Required property 'status_codes' is missing"
        return typing.cast(typing.List[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOriginGroupFailoverCriteria(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontDistributionOriginGroupFailoverCriteriaOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginGroupFailoverCriteriaOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusCodesInput")
    def status_codes_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "statusCodesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusCodes")
    def status_codes(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "statusCodes"))

    @status_codes.setter
    def status_codes(self, value: typing.List[jsii.Number]) -> None:
        jsii.set(self, "statusCodes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionOriginGroupFailoverCriteria]:
        return typing.cast(typing.Optional[CloudfrontDistributionOriginGroupFailoverCriteria], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionOriginGroupFailoverCriteria],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginGroupMember",
    jsii_struct_bases=[],
    name_mapping={"origin_id": "originId"},
)
class CloudfrontDistributionOriginGroupMember:
    def __init__(self, *, origin_id: builtins.str) -> None:
        '''
        :param origin_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_id CloudfrontDistribution#origin_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "origin_id": origin_id,
        }

    @builtins.property
    def origin_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_id CloudfrontDistribution#origin_id}.'''
        result = self._values.get("origin_id")
        assert result is not None, "Required property 'origin_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOriginGroupMember(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginOriginShield",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "origin_shield_region": "originShieldRegion"},
)
class CloudfrontDistributionOriginOriginShield:
    def __init__(
        self,
        *,
        enabled: typing.Union[builtins.bool, cdktf.IResolvable],
        origin_shield_region: builtins.str,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#enabled CloudfrontDistribution#enabled}.
        :param origin_shield_region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_shield_region CloudfrontDistribution#origin_shield_region}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enabled": enabled,
            "origin_shield_region": origin_shield_region,
        }

    @builtins.property
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#enabled CloudfrontDistribution#enabled}.'''
        result = self._values.get("enabled")
        assert result is not None, "Required property 'enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def origin_shield_region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_shield_region CloudfrontDistribution#origin_shield_region}.'''
        result = self._values.get("origin_shield_region")
        assert result is not None, "Required property 'origin_shield_region' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOriginOriginShield(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontDistributionOriginOriginShieldOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginOriginShieldOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originShieldRegionInput")
    def origin_shield_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "originShieldRegionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originShieldRegion")
    def origin_shield_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "originShieldRegion"))

    @origin_shield_region.setter
    def origin_shield_region(self, value: builtins.str) -> None:
        jsii.set(self, "originShieldRegion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionOriginOriginShield]:
        return typing.cast(typing.Optional[CloudfrontDistributionOriginOriginShield], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionOriginOriginShield],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginS3OriginConfig",
    jsii_struct_bases=[],
    name_mapping={"origin_access_identity": "originAccessIdentity"},
)
class CloudfrontDistributionOriginS3OriginConfig:
    def __init__(self, *, origin_access_identity: builtins.str) -> None:
        '''
        :param origin_access_identity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_access_identity CloudfrontDistribution#origin_access_identity}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "origin_access_identity": origin_access_identity,
        }

    @builtins.property
    def origin_access_identity(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#origin_access_identity CloudfrontDistribution#origin_access_identity}.'''
        result = self._values.get("origin_access_identity")
        assert result is not None, "Required property 'origin_access_identity' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionOriginS3OriginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontDistributionOriginS3OriginConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionOriginS3OriginConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originAccessIdentityInput")
    def origin_access_identity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "originAccessIdentityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originAccessIdentity")
    def origin_access_identity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "originAccessIdentity"))

    @origin_access_identity.setter
    def origin_access_identity(self, value: builtins.str) -> None:
        jsii.set(self, "originAccessIdentity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionOriginS3OriginConfig]:
        return typing.cast(typing.Optional[CloudfrontDistributionOriginS3OriginConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionOriginS3OriginConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionRestrictions",
    jsii_struct_bases=[],
    name_mapping={"geo_restriction": "geoRestriction"},
)
class CloudfrontDistributionRestrictions:
    def __init__(
        self,
        *,
        geo_restriction: "CloudfrontDistributionRestrictionsGeoRestriction",
    ) -> None:
        '''
        :param geo_restriction: geo_restriction block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#geo_restriction CloudfrontDistribution#geo_restriction}
        '''
        if isinstance(geo_restriction, dict):
            geo_restriction = CloudfrontDistributionRestrictionsGeoRestriction(**geo_restriction)
        self._values: typing.Dict[str, typing.Any] = {
            "geo_restriction": geo_restriction,
        }

    @builtins.property
    def geo_restriction(self) -> "CloudfrontDistributionRestrictionsGeoRestriction":
        '''geo_restriction block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#geo_restriction CloudfrontDistribution#geo_restriction}
        '''
        result = self._values.get("geo_restriction")
        assert result is not None, "Required property 'geo_restriction' is missing"
        return typing.cast("CloudfrontDistributionRestrictionsGeoRestriction", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionRestrictions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionRestrictionsGeoRestriction",
    jsii_struct_bases=[],
    name_mapping={"restriction_type": "restrictionType", "locations": "locations"},
)
class CloudfrontDistributionRestrictionsGeoRestriction:
    def __init__(
        self,
        *,
        restriction_type: builtins.str,
        locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param restriction_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#restriction_type CloudfrontDistribution#restriction_type}.
        :param locations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#locations CloudfrontDistribution#locations}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "restriction_type": restriction_type,
        }
        if locations is not None:
            self._values["locations"] = locations

    @builtins.property
    def restriction_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#restriction_type CloudfrontDistribution#restriction_type}.'''
        result = self._values.get("restriction_type")
        assert result is not None, "Required property 'restriction_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def locations(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#locations CloudfrontDistribution#locations}.'''
        result = self._values.get("locations")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionRestrictionsGeoRestriction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontDistributionRestrictionsGeoRestrictionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionRestrictionsGeoRestrictionOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetLocations")
    def reset_locations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocations", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locationsInput")
    def locations_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "locationsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictionTypeInput")
    def restriction_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restrictionTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locations")
    def locations(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "locations"))

    @locations.setter
    def locations(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "locations", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restrictionType")
    def restriction_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restrictionType"))

    @restriction_type.setter
    def restriction_type(self, value: builtins.str) -> None:
        jsii.set(self, "restrictionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionRestrictionsGeoRestriction]:
        return typing.cast(typing.Optional[CloudfrontDistributionRestrictionsGeoRestriction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionRestrictionsGeoRestriction],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontDistributionRestrictionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionRestrictionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putGeoRestriction")
    def put_geo_restriction(
        self,
        *,
        restriction_type: builtins.str,
        locations: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param restriction_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#restriction_type CloudfrontDistribution#restriction_type}.
        :param locations: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#locations CloudfrontDistribution#locations}.
        '''
        value = CloudfrontDistributionRestrictionsGeoRestriction(
            restriction_type=restriction_type, locations=locations
        )

        return typing.cast(None, jsii.invoke(self, "putGeoRestriction", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="geoRestriction")
    def geo_restriction(
        self,
    ) -> CloudfrontDistributionRestrictionsGeoRestrictionOutputReference:
        return typing.cast(CloudfrontDistributionRestrictionsGeoRestrictionOutputReference, jsii.get(self, "geoRestriction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="geoRestrictionInput")
    def geo_restriction_input(
        self,
    ) -> typing.Optional[CloudfrontDistributionRestrictionsGeoRestriction]:
        return typing.cast(typing.Optional[CloudfrontDistributionRestrictionsGeoRestriction], jsii.get(self, "geoRestrictionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudfrontDistributionRestrictions]:
        return typing.cast(typing.Optional[CloudfrontDistributionRestrictions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionRestrictions],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontDistributionTrustedKeyGroups(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionTrustedKeyGroups",
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
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "items"))


class CloudfrontDistributionTrustedKeyGroupsItems(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionTrustedKeyGroupsItems",
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
    @jsii.member(jsii_name="keyGroupId")
    def key_group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyGroupId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPairIds")
    def key_pair_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "keyPairIds"))


class CloudfrontDistributionTrustedSigners(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionTrustedSigners",
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
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "items"))


class CloudfrontDistributionTrustedSignersItems(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionTrustedSignersItems",
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
    @jsii.member(jsii_name="awsAccountNumber")
    def aws_account_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccountNumber"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPairIds")
    def key_pair_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "keyPairIds"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionViewerCertificate",
    jsii_struct_bases=[],
    name_mapping={
        "acm_certificate_arn": "acmCertificateArn",
        "cloudfront_default_certificate": "cloudfrontDefaultCertificate",
        "iam_certificate_id": "iamCertificateId",
        "minimum_protocol_version": "minimumProtocolVersion",
        "ssl_support_method": "sslSupportMethod",
    },
)
class CloudfrontDistributionViewerCertificate:
    def __init__(
        self,
        *,
        acm_certificate_arn: typing.Optional[builtins.str] = None,
        cloudfront_default_certificate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iam_certificate_id: typing.Optional[builtins.str] = None,
        minimum_protocol_version: typing.Optional[builtins.str] = None,
        ssl_support_method: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param acm_certificate_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#acm_certificate_arn CloudfrontDistribution#acm_certificate_arn}.
        :param cloudfront_default_certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cloudfront_default_certificate CloudfrontDistribution#cloudfront_default_certificate}.
        :param iam_certificate_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#iam_certificate_id CloudfrontDistribution#iam_certificate_id}.
        :param minimum_protocol_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#minimum_protocol_version CloudfrontDistribution#minimum_protocol_version}.
        :param ssl_support_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#ssl_support_method CloudfrontDistribution#ssl_support_method}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if acm_certificate_arn is not None:
            self._values["acm_certificate_arn"] = acm_certificate_arn
        if cloudfront_default_certificate is not None:
            self._values["cloudfront_default_certificate"] = cloudfront_default_certificate
        if iam_certificate_id is not None:
            self._values["iam_certificate_id"] = iam_certificate_id
        if minimum_protocol_version is not None:
            self._values["minimum_protocol_version"] = minimum_protocol_version
        if ssl_support_method is not None:
            self._values["ssl_support_method"] = ssl_support_method

    @builtins.property
    def acm_certificate_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#acm_certificate_arn CloudfrontDistribution#acm_certificate_arn}.'''
        result = self._values.get("acm_certificate_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudfront_default_certificate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#cloudfront_default_certificate CloudfrontDistribution#cloudfront_default_certificate}.'''
        result = self._values.get("cloudfront_default_certificate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iam_certificate_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#iam_certificate_id CloudfrontDistribution#iam_certificate_id}.'''
        result = self._values.get("iam_certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum_protocol_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#minimum_protocol_version CloudfrontDistribution#minimum_protocol_version}.'''
        result = self._values.get("minimum_protocol_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_support_method(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution#ssl_support_method CloudfrontDistribution#ssl_support_method}.'''
        result = self._values.get("ssl_support_method")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontDistributionViewerCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontDistributionViewerCertificateOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontDistributionViewerCertificateOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetAcmCertificateArn")
    def reset_acm_certificate_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAcmCertificateArn", []))

    @jsii.member(jsii_name="resetCloudfrontDefaultCertificate")
    def reset_cloudfront_default_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudfrontDefaultCertificate", []))

    @jsii.member(jsii_name="resetIamCertificateId")
    def reset_iam_certificate_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamCertificateId", []))

    @jsii.member(jsii_name="resetMinimumProtocolVersion")
    def reset_minimum_protocol_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumProtocolVersion", []))

    @jsii.member(jsii_name="resetSslSupportMethod")
    def reset_ssl_support_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslSupportMethod", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="acmCertificateArnInput")
    def acm_certificate_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "acmCertificateArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudfrontDefaultCertificateInput")
    def cloudfront_default_certificate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "cloudfrontDefaultCertificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamCertificateIdInput")
    def iam_certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamCertificateIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumProtocolVersionInput")
    def minimum_protocol_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumProtocolVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslSupportMethodInput")
    def ssl_support_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sslSupportMethodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="acmCertificateArn")
    def acm_certificate_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acmCertificateArn"))

    @acm_certificate_arn.setter
    def acm_certificate_arn(self, value: builtins.str) -> None:
        jsii.set(self, "acmCertificateArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudfrontDefaultCertificate")
    def cloudfront_default_certificate(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "cloudfrontDefaultCertificate"))

    @cloudfront_default_certificate.setter
    def cloudfront_default_certificate(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "cloudfrontDefaultCertificate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamCertificateId")
    def iam_certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamCertificateId"))

    @iam_certificate_id.setter
    def iam_certificate_id(self, value: builtins.str) -> None:
        jsii.set(self, "iamCertificateId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumProtocolVersion")
    def minimum_protocol_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimumProtocolVersion"))

    @minimum_protocol_version.setter
    def minimum_protocol_version(self, value: builtins.str) -> None:
        jsii.set(self, "minimumProtocolVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslSupportMethod")
    def ssl_support_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sslSupportMethod"))

    @ssl_support_method.setter
    def ssl_support_method(self, value: builtins.str) -> None:
        jsii.set(self, "sslSupportMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontDistributionViewerCertificate]:
        return typing.cast(typing.Optional[CloudfrontDistributionViewerCertificate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontDistributionViewerCertificate],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontFieldLevelEncryptionConfig(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfig",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config aws_cloudfront_field_level_encryption_config}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        content_type_profile_config: "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig",
        query_arg_profile_config: "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig",
        comment: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config aws_cloudfront_field_level_encryption_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param content_type_profile_config: content_type_profile_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#content_type_profile_config CloudfrontFieldLevelEncryptionConfig#content_type_profile_config}
        :param query_arg_profile_config: query_arg_profile_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#query_arg_profile_config CloudfrontFieldLevelEncryptionConfig#query_arg_profile_config}
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#comment CloudfrontFieldLevelEncryptionConfig#comment}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontFieldLevelEncryptionConfigConfig(
            content_type_profile_config=content_type_profile_config,
            query_arg_profile_config=query_arg_profile_config,
            comment=comment,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putContentTypeProfileConfig")
    def put_content_type_profile_config(
        self,
        *,
        content_type_profiles: "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles",
        forward_when_content_type_is_unknown: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param content_type_profiles: content_type_profiles block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#content_type_profiles CloudfrontFieldLevelEncryptionConfig#content_type_profiles}
        :param forward_when_content_type_is_unknown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#forward_when_content_type_is_unknown CloudfrontFieldLevelEncryptionConfig#forward_when_content_type_is_unknown}.
        '''
        value = CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig(
            content_type_profiles=content_type_profiles,
            forward_when_content_type_is_unknown=forward_when_content_type_is_unknown,
        )

        return typing.cast(None, jsii.invoke(self, "putContentTypeProfileConfig", [value]))

    @jsii.member(jsii_name="putQueryArgProfileConfig")
    def put_query_arg_profile_config(
        self,
        *,
        forward_when_query_arg_profile_is_unknown: typing.Union[builtins.bool, cdktf.IResolvable],
        query_arg_profiles: typing.Optional["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles"] = None,
    ) -> None:
        '''
        :param forward_when_query_arg_profile_is_unknown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#forward_when_query_arg_profile_is_unknown CloudfrontFieldLevelEncryptionConfig#forward_when_query_arg_profile_is_unknown}.
        :param query_arg_profiles: query_arg_profiles block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#query_arg_profiles CloudfrontFieldLevelEncryptionConfig#query_arg_profiles}
        '''
        value = CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig(
            forward_when_query_arg_profile_is_unknown=forward_when_query_arg_profile_is_unknown,
            query_arg_profiles=query_arg_profiles,
        )

        return typing.cast(None, jsii.invoke(self, "putQueryArgProfileConfig", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callerReference")
    def caller_reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "callerReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeProfileConfig")
    def content_type_profile_config(
        self,
    ) -> "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigOutputReference":
        return typing.cast("CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigOutputReference", jsii.get(self, "contentTypeProfileConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryArgProfileConfig")
    def query_arg_profile_config(
        self,
    ) -> "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigOutputReference":
        return typing.cast("CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigOutputReference", jsii.get(self, "queryArgProfileConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeProfileConfigInput")
    def content_type_profile_config_input(
        self,
    ) -> typing.Optional["CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig"]:
        return typing.cast(typing.Optional["CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig"], jsii.get(self, "contentTypeProfileConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryArgProfileConfigInput")
    def query_arg_profile_config_input(
        self,
    ) -> typing.Optional["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig"]:
        return typing.cast(typing.Optional["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig"], jsii.get(self, "queryArgProfileConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        jsii.set(self, "comment", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "content_type_profile_config": "contentTypeProfileConfig",
        "query_arg_profile_config": "queryArgProfileConfig",
        "comment": "comment",
    },
)
class CloudfrontFieldLevelEncryptionConfigConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        content_type_profile_config: "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig",
        query_arg_profile_config: "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig",
        comment: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param content_type_profile_config: content_type_profile_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#content_type_profile_config CloudfrontFieldLevelEncryptionConfig#content_type_profile_config}
        :param query_arg_profile_config: query_arg_profile_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#query_arg_profile_config CloudfrontFieldLevelEncryptionConfig#query_arg_profile_config}
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#comment CloudfrontFieldLevelEncryptionConfig#comment}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(content_type_profile_config, dict):
            content_type_profile_config = CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig(**content_type_profile_config)
        if isinstance(query_arg_profile_config, dict):
            query_arg_profile_config = CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig(**query_arg_profile_config)
        self._values: typing.Dict[str, typing.Any] = {
            "content_type_profile_config": content_type_profile_config,
            "query_arg_profile_config": query_arg_profile_config,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if comment is not None:
            self._values["comment"] = comment

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
    def content_type_profile_config(
        self,
    ) -> "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig":
        '''content_type_profile_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#content_type_profile_config CloudfrontFieldLevelEncryptionConfig#content_type_profile_config}
        '''
        result = self._values.get("content_type_profile_config")
        assert result is not None, "Required property 'content_type_profile_config' is missing"
        return typing.cast("CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig", result)

    @builtins.property
    def query_arg_profile_config(
        self,
    ) -> "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig":
        '''query_arg_profile_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#query_arg_profile_config CloudfrontFieldLevelEncryptionConfig#query_arg_profile_config}
        '''
        result = self._values.get("query_arg_profile_config")
        assert result is not None, "Required property 'query_arg_profile_config' is missing"
        return typing.cast("CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig", result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#comment CloudfrontFieldLevelEncryptionConfig#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig",
    jsii_struct_bases=[],
    name_mapping={
        "content_type_profiles": "contentTypeProfiles",
        "forward_when_content_type_is_unknown": "forwardWhenContentTypeIsUnknown",
    },
)
class CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig:
    def __init__(
        self,
        *,
        content_type_profiles: "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles",
        forward_when_content_type_is_unknown: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param content_type_profiles: content_type_profiles block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#content_type_profiles CloudfrontFieldLevelEncryptionConfig#content_type_profiles}
        :param forward_when_content_type_is_unknown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#forward_when_content_type_is_unknown CloudfrontFieldLevelEncryptionConfig#forward_when_content_type_is_unknown}.
        '''
        if isinstance(content_type_profiles, dict):
            content_type_profiles = CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles(**content_type_profiles)
        self._values: typing.Dict[str, typing.Any] = {
            "content_type_profiles": content_type_profiles,
            "forward_when_content_type_is_unknown": forward_when_content_type_is_unknown,
        }

    @builtins.property
    def content_type_profiles(
        self,
    ) -> "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles":
        '''content_type_profiles block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#content_type_profiles CloudfrontFieldLevelEncryptionConfig#content_type_profiles}
        '''
        result = self._values.get("content_type_profiles")
        assert result is not None, "Required property 'content_type_profiles' is missing"
        return typing.cast("CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles", result)

    @builtins.property
    def forward_when_content_type_is_unknown(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#forward_when_content_type_is_unknown CloudfrontFieldLevelEncryptionConfig#forward_when_content_type_is_unknown}.'''
        result = self._values.get("forward_when_content_type_is_unknown")
        assert result is not None, "Required property 'forward_when_content_type_is_unknown' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles:
    def __init__(
        self,
        *,
        items: typing.Sequence["CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems"],
    ) -> None:
        '''
        :param items: items block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#items CloudfrontFieldLevelEncryptionConfig#items}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "items": items,
        }

    @builtins.property
    def items(
        self,
    ) -> typing.List["CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems"]:
        '''items block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#items CloudfrontFieldLevelEncryptionConfig#items}
        '''
        result = self._values.get("items")
        assert result is not None, "Required property 'items' is missing"
        return typing.cast(typing.List["CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems",
    jsii_struct_bases=[],
    name_mapping={
        "content_type": "contentType",
        "format": "format",
        "profile_id": "profileId",
    },
)
class CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems:
    def __init__(
        self,
        *,
        content_type: builtins.str,
        format: builtins.str,
        profile_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param content_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#content_type CloudfrontFieldLevelEncryptionConfig#content_type}.
        :param format: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#format CloudfrontFieldLevelEncryptionConfig#format}.
        :param profile_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#profile_id CloudfrontFieldLevelEncryptionConfig#profile_id}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content_type": content_type,
            "format": format,
        }
        if profile_id is not None:
            self._values["profile_id"] = profile_id

    @builtins.property
    def content_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#content_type CloudfrontFieldLevelEncryptionConfig#content_type}.'''
        result = self._values.get("content_type")
        assert result is not None, "Required property 'content_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def format(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#format CloudfrontFieldLevelEncryptionConfig#format}.'''
        result = self._values.get("format")
        assert result is not None, "Required property 'format' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#profile_id CloudfrontFieldLevelEncryptionConfig#profile_id}.'''
        result = self._values.get("profile_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(
        self,
    ) -> typing.Optional[typing.List[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems]]:
        return typing.cast(typing.Optional[typing.List[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(
        self,
    ) -> typing.List[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems]:
        return typing.cast(typing.List[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems], jsii.get(self, "items"))

    @items.setter
    def items(
        self,
        value: typing.List[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems],
    ) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles]:
        return typing.cast(typing.Optional[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putContentTypeProfiles")
    def put_content_type_profiles(
        self,
        *,
        items: typing.Sequence[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems],
    ) -> None:
        '''
        :param items: items block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#items CloudfrontFieldLevelEncryptionConfig#items}
        '''
        value = CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles(
            items=items
        )

        return typing.cast(None, jsii.invoke(self, "putContentTypeProfiles", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeProfiles")
    def content_type_profiles(
        self,
    ) -> CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesOutputReference:
        return typing.cast(CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesOutputReference, jsii.get(self, "contentTypeProfiles"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeProfilesInput")
    def content_type_profiles_input(
        self,
    ) -> typing.Optional[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles]:
        return typing.cast(typing.Optional[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles], jsii.get(self, "contentTypeProfilesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forwardWhenContentTypeIsUnknownInput")
    def forward_when_content_type_is_unknown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forwardWhenContentTypeIsUnknownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forwardWhenContentTypeIsUnknown")
    def forward_when_content_type_is_unknown(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forwardWhenContentTypeIsUnknown"))

    @forward_when_content_type_is_unknown.setter
    def forward_when_content_type_is_unknown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forwardWhenContentTypeIsUnknown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig]:
        return typing.cast(typing.Optional[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig",
    jsii_struct_bases=[],
    name_mapping={
        "forward_when_query_arg_profile_is_unknown": "forwardWhenQueryArgProfileIsUnknown",
        "query_arg_profiles": "queryArgProfiles",
    },
)
class CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig:
    def __init__(
        self,
        *,
        forward_when_query_arg_profile_is_unknown: typing.Union[builtins.bool, cdktf.IResolvable],
        query_arg_profiles: typing.Optional["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles"] = None,
    ) -> None:
        '''
        :param forward_when_query_arg_profile_is_unknown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#forward_when_query_arg_profile_is_unknown CloudfrontFieldLevelEncryptionConfig#forward_when_query_arg_profile_is_unknown}.
        :param query_arg_profiles: query_arg_profiles block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#query_arg_profiles CloudfrontFieldLevelEncryptionConfig#query_arg_profiles}
        '''
        if isinstance(query_arg_profiles, dict):
            query_arg_profiles = CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles(**query_arg_profiles)
        self._values: typing.Dict[str, typing.Any] = {
            "forward_when_query_arg_profile_is_unknown": forward_when_query_arg_profile_is_unknown,
        }
        if query_arg_profiles is not None:
            self._values["query_arg_profiles"] = query_arg_profiles

    @builtins.property
    def forward_when_query_arg_profile_is_unknown(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#forward_when_query_arg_profile_is_unknown CloudfrontFieldLevelEncryptionConfig#forward_when_query_arg_profile_is_unknown}.'''
        result = self._values.get("forward_when_query_arg_profile_is_unknown")
        assert result is not None, "Required property 'forward_when_query_arg_profile_is_unknown' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def query_arg_profiles(
        self,
    ) -> typing.Optional["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles"]:
        '''query_arg_profiles block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#query_arg_profiles CloudfrontFieldLevelEncryptionConfig#query_arg_profiles}
        '''
        result = self._values.get("query_arg_profiles")
        return typing.cast(typing.Optional["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putQueryArgProfiles")
    def put_query_arg_profiles(
        self,
        *,
        items: typing.Optional[typing.Sequence["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems"]] = None,
    ) -> None:
        '''
        :param items: items block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#items CloudfrontFieldLevelEncryptionConfig#items}
        '''
        value = CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles(
            items=items
        )

        return typing.cast(None, jsii.invoke(self, "putQueryArgProfiles", [value]))

    @jsii.member(jsii_name="resetQueryArgProfiles")
    def reset_query_arg_profiles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryArgProfiles", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryArgProfiles")
    def query_arg_profiles(
        self,
    ) -> "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesOutputReference":
        return typing.cast("CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesOutputReference", jsii.get(self, "queryArgProfiles"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forwardWhenQueryArgProfileIsUnknownInput")
    def forward_when_query_arg_profile_is_unknown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forwardWhenQueryArgProfileIsUnknownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryArgProfilesInput")
    def query_arg_profiles_input(
        self,
    ) -> typing.Optional["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles"]:
        return typing.cast(typing.Optional["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles"], jsii.get(self, "queryArgProfilesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forwardWhenQueryArgProfileIsUnknown")
    def forward_when_query_arg_profile_is_unknown(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forwardWhenQueryArgProfileIsUnknown"))

    @forward_when_query_arg_profile_is_unknown.setter
    def forward_when_query_arg_profile_is_unknown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forwardWhenQueryArgProfileIsUnknown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig]:
        return typing.cast(typing.Optional[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems"]] = None,
    ) -> None:
        '''
        :param items: items block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#items CloudfrontFieldLevelEncryptionConfig#items}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(
        self,
    ) -> typing.Optional[typing.List["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems"]]:
        '''items block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#items CloudfrontFieldLevelEncryptionConfig#items}
        '''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List["CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems",
    jsii_struct_bases=[],
    name_mapping={"profile_id": "profileId", "query_arg": "queryArg"},
)
class CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems:
    def __init__(self, *, profile_id: builtins.str, query_arg: builtins.str) -> None:
        '''
        :param profile_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#profile_id CloudfrontFieldLevelEncryptionConfig#profile_id}.
        :param query_arg: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#query_arg CloudfrontFieldLevelEncryptionConfig#query_arg}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "profile_id": profile_id,
            "query_arg": query_arg,
        }

    @builtins.property
    def profile_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#profile_id CloudfrontFieldLevelEncryptionConfig#profile_id}.'''
        result = self._values.get("profile_id")
        assert result is not None, "Required property 'profile_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query_arg(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_config#query_arg CloudfrontFieldLevelEncryptionConfig#query_arg}.'''
        result = self._values.get("query_arg")
        assert result is not None, "Required property 'query_arg' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(
        self,
    ) -> typing.Optional[typing.List[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems]]:
        return typing.cast(typing.Optional[typing.List[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(
        self,
    ) -> typing.List[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems]:
        return typing.cast(typing.List[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems], jsii.get(self, "items"))

    @items.setter
    def items(
        self,
        value: typing.List[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems],
    ) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles]:
        return typing.cast(typing.Optional[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontFieldLevelEncryptionProfile(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionProfile",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile aws_cloudfront_field_level_encryption_profile}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        encryption_entities: "CloudfrontFieldLevelEncryptionProfileEncryptionEntities",
        name: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile aws_cloudfront_field_level_encryption_profile} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param encryption_entities: encryption_entities block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#encryption_entities CloudfrontFieldLevelEncryptionProfile#encryption_entities}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#name CloudfrontFieldLevelEncryptionProfile#name}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#comment CloudfrontFieldLevelEncryptionProfile#comment}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontFieldLevelEncryptionProfileConfig(
            encryption_entities=encryption_entities,
            name=name,
            comment=comment,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putEncryptionEntities")
    def put_encryption_entities(
        self,
        *,
        items: typing.Optional[typing.Sequence["CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems"]] = None,
    ) -> None:
        '''
        :param items: items block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#items CloudfrontFieldLevelEncryptionProfile#items}
        '''
        value = CloudfrontFieldLevelEncryptionProfileEncryptionEntities(items=items)

        return typing.cast(None, jsii.invoke(self, "putEncryptionEntities", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callerReference")
    def caller_reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "callerReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionEntities")
    def encryption_entities(
        self,
    ) -> "CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesOutputReference":
        return typing.cast("CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesOutputReference", jsii.get(self, "encryptionEntities"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionEntitiesInput")
    def encryption_entities_input(
        self,
    ) -> typing.Optional["CloudfrontFieldLevelEncryptionProfileEncryptionEntities"]:
        return typing.cast(typing.Optional["CloudfrontFieldLevelEncryptionProfileEncryptionEntities"], jsii.get(self, "encryptionEntitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        jsii.set(self, "comment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionProfileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "encryption_entities": "encryptionEntities",
        "name": "name",
        "comment": "comment",
    },
)
class CloudfrontFieldLevelEncryptionProfileConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        encryption_entities: "CloudfrontFieldLevelEncryptionProfileEncryptionEntities",
        name: builtins.str,
        comment: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param encryption_entities: encryption_entities block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#encryption_entities CloudfrontFieldLevelEncryptionProfile#encryption_entities}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#name CloudfrontFieldLevelEncryptionProfile#name}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#comment CloudfrontFieldLevelEncryptionProfile#comment}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(encryption_entities, dict):
            encryption_entities = CloudfrontFieldLevelEncryptionProfileEncryptionEntities(**encryption_entities)
        self._values: typing.Dict[str, typing.Any] = {
            "encryption_entities": encryption_entities,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if comment is not None:
            self._values["comment"] = comment

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
    def encryption_entities(
        self,
    ) -> "CloudfrontFieldLevelEncryptionProfileEncryptionEntities":
        '''encryption_entities block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#encryption_entities CloudfrontFieldLevelEncryptionProfile#encryption_entities}
        '''
        result = self._values.get("encryption_entities")
        assert result is not None, "Required property 'encryption_entities' is missing"
        return typing.cast("CloudfrontFieldLevelEncryptionProfileEncryptionEntities", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#name CloudfrontFieldLevelEncryptionProfile#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#comment CloudfrontFieldLevelEncryptionProfile#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionProfileEncryptionEntities",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontFieldLevelEncryptionProfileEncryptionEntities:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence["CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems"]] = None,
    ) -> None:
        '''
        :param items: items block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#items CloudfrontFieldLevelEncryptionProfile#items}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(
        self,
    ) -> typing.Optional[typing.List["CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems"]]:
        '''items block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#items CloudfrontFieldLevelEncryptionProfile#items}
        '''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List["CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionProfileEncryptionEntities(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems",
    jsii_struct_bases=[],
    name_mapping={
        "field_patterns": "fieldPatterns",
        "provider_id": "providerId",
        "public_key_id": "publicKeyId",
    },
)
class CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems:
    def __init__(
        self,
        *,
        field_patterns: "CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns",
        provider_id: builtins.str,
        public_key_id: builtins.str,
    ) -> None:
        '''
        :param field_patterns: field_patterns block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#field_patterns CloudfrontFieldLevelEncryptionProfile#field_patterns}
        :param provider_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#provider_id CloudfrontFieldLevelEncryptionProfile#provider_id}.
        :param public_key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#public_key_id CloudfrontFieldLevelEncryptionProfile#public_key_id}.
        '''
        if isinstance(field_patterns, dict):
            field_patterns = CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns(**field_patterns)
        self._values: typing.Dict[str, typing.Any] = {
            "field_patterns": field_patterns,
            "provider_id": provider_id,
            "public_key_id": public_key_id,
        }

    @builtins.property
    def field_patterns(
        self,
    ) -> "CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns":
        '''field_patterns block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#field_patterns CloudfrontFieldLevelEncryptionProfile#field_patterns}
        '''
        result = self._values.get("field_patterns")
        assert result is not None, "Required property 'field_patterns' is missing"
        return typing.cast("CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns", result)

    @builtins.property
    def provider_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#provider_id CloudfrontFieldLevelEncryptionProfile#provider_id}.'''
        result = self._values.get("provider_id")
        assert result is not None, "Required property 'provider_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def public_key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#public_key_id CloudfrontFieldLevelEncryptionProfile#public_key_id}.'''
        result = self._values.get("public_key_id")
        assert result is not None, "Required property 'public_key_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#items CloudfrontFieldLevelEncryptionProfile#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_field_level_encryption_profile#items CloudfrontFieldLevelEncryptionProfile#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatternsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatternsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns]:
        return typing.cast(typing.Optional[CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(
        self,
    ) -> typing.Optional[typing.List[CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems]]:
        return typing.cast(typing.Optional[typing.List[CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(
        self,
    ) -> typing.List[CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems]:
        return typing.cast(typing.List[CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems], jsii.get(self, "items"))

    @items.setter
    def items(
        self,
        value: typing.List[CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems],
    ) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontFieldLevelEncryptionProfileEncryptionEntities]:
        return typing.cast(typing.Optional[CloudfrontFieldLevelEncryptionProfileEncryptionEntities], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontFieldLevelEncryptionProfileEncryptionEntities],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontFunction(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFunction",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function aws_cloudfront_function}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        code: builtins.str,
        name: builtins.str,
        runtime: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        publish: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function aws_cloudfront_function} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#code CloudfrontFunction#code}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#name CloudfrontFunction#name}.
        :param runtime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#runtime CloudfrontFunction#runtime}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#comment CloudfrontFunction#comment}.
        :param publish: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#publish CloudfrontFunction#publish}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontFunctionConfig(
            code=code,
            name=name,
            runtime=runtime,
            comment=comment,
            publish=publish,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetPublish")
    def reset_publish(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublish", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="liveStageEtag")
    def live_stage_etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "liveStageEtag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="codeInput")
    def code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "codeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishInput")
    def publish_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publishInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtimeInput")
    def runtime_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runtimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="code")
    def code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "code"))

    @code.setter
    def code(self, value: builtins.str) -> None:
        jsii.set(self, "code", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        jsii.set(self, "comment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publish")
    def publish(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "publish"))

    @publish.setter
    def publish(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "publish", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runtime"))

    @runtime.setter
    def runtime(self, value: builtins.str) -> None:
        jsii.set(self, "runtime", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontFunctionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "code": "code",
        "name": "name",
        "runtime": "runtime",
        "comment": "comment",
        "publish": "publish",
    },
)
class CloudfrontFunctionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        code: builtins.str,
        name: builtins.str,
        runtime: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        publish: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#code CloudfrontFunction#code}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#name CloudfrontFunction#name}.
        :param runtime: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#runtime CloudfrontFunction#runtime}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#comment CloudfrontFunction#comment}.
        :param publish: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#publish CloudfrontFunction#publish}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "code": code,
            "name": name,
            "runtime": runtime,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if comment is not None:
            self._values["comment"] = comment
        if publish is not None:
            self._values["publish"] = publish

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
    def code(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#code CloudfrontFunction#code}.'''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#name CloudfrontFunction#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runtime(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#runtime CloudfrontFunction#runtime}.'''
        result = self._values.get("runtime")
        assert result is not None, "Required property 'runtime' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#comment CloudfrontFunction#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_function#publish CloudfrontFunction#publish}.'''
        result = self._values.get("publish")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontFunctionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontKeyGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontKeyGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group aws_cloudfront_key_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        items: typing.Sequence[builtins.str],
        name: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group aws_cloudfront_key_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group#items CloudfrontKeyGroup#items}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group#name CloudfrontKeyGroup#name}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group#comment CloudfrontKeyGroup#comment}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontKeyGroupConfig(
            items=items,
            name=name,
            comment=comment,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        jsii.set(self, "comment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontKeyGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "items": "items",
        "name": "name",
        "comment": "comment",
    },
)
class CloudfrontKeyGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        items: typing.Sequence[builtins.str],
        name: builtins.str,
        comment: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group#items CloudfrontKeyGroup#items}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group#name CloudfrontKeyGroup#name}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group#comment CloudfrontKeyGroup#comment}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "items": items,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if comment is not None:
            self._values["comment"] = comment

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
    def items(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group#items CloudfrontKeyGroup#items}.'''
        result = self._values.get("items")
        assert result is not None, "Required property 'items' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group#name CloudfrontKeyGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_key_group#comment CloudfrontKeyGroup#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontKeyGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontMonitoringSubscription(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontMonitoringSubscription",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription aws_cloudfront_monitoring_subscription}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        distribution_id: builtins.str,
        monitoring_subscription: "CloudfrontMonitoringSubscriptionMonitoringSubscription",
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription aws_cloudfront_monitoring_subscription} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param distribution_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#distribution_id CloudfrontMonitoringSubscription#distribution_id}.
        :param monitoring_subscription: monitoring_subscription block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#monitoring_subscription CloudfrontMonitoringSubscription#monitoring_subscription}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontMonitoringSubscriptionConfig(
            distribution_id=distribution_id,
            monitoring_subscription=monitoring_subscription,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putMonitoringSubscription")
    def put_monitoring_subscription(
        self,
        *,
        realtime_metrics_subscription_config: "CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig",
    ) -> None:
        '''
        :param realtime_metrics_subscription_config: realtime_metrics_subscription_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#realtime_metrics_subscription_config CloudfrontMonitoringSubscription#realtime_metrics_subscription_config}
        '''
        value = CloudfrontMonitoringSubscriptionMonitoringSubscription(
            realtime_metrics_subscription_config=realtime_metrics_subscription_config
        )

        return typing.cast(None, jsii.invoke(self, "putMonitoringSubscription", [value]))

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
    @jsii.member(jsii_name="monitoringSubscription")
    def monitoring_subscription(
        self,
    ) -> "CloudfrontMonitoringSubscriptionMonitoringSubscriptionOutputReference":
        return typing.cast("CloudfrontMonitoringSubscriptionMonitoringSubscriptionOutputReference", jsii.get(self, "monitoringSubscription"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionIdInput")
    def distribution_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "distributionIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitoringSubscriptionInput")
    def monitoring_subscription_input(
        self,
    ) -> typing.Optional["CloudfrontMonitoringSubscriptionMonitoringSubscription"]:
        return typing.cast(typing.Optional["CloudfrontMonitoringSubscriptionMonitoringSubscription"], jsii.get(self, "monitoringSubscriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionId")
    def distribution_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "distributionId"))

    @distribution_id.setter
    def distribution_id(self, value: builtins.str) -> None:
        jsii.set(self, "distributionId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontMonitoringSubscriptionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "distribution_id": "distributionId",
        "monitoring_subscription": "monitoringSubscription",
    },
)
class CloudfrontMonitoringSubscriptionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        distribution_id: builtins.str,
        monitoring_subscription: "CloudfrontMonitoringSubscriptionMonitoringSubscription",
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param distribution_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#distribution_id CloudfrontMonitoringSubscription#distribution_id}.
        :param monitoring_subscription: monitoring_subscription block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#monitoring_subscription CloudfrontMonitoringSubscription#monitoring_subscription}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(monitoring_subscription, dict):
            monitoring_subscription = CloudfrontMonitoringSubscriptionMonitoringSubscription(**monitoring_subscription)
        self._values: typing.Dict[str, typing.Any] = {
            "distribution_id": distribution_id,
            "monitoring_subscription": monitoring_subscription,
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
    def distribution_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#distribution_id CloudfrontMonitoringSubscription#distribution_id}.'''
        result = self._values.get("distribution_id")
        assert result is not None, "Required property 'distribution_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def monitoring_subscription(
        self,
    ) -> "CloudfrontMonitoringSubscriptionMonitoringSubscription":
        '''monitoring_subscription block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#monitoring_subscription CloudfrontMonitoringSubscription#monitoring_subscription}
        '''
        result = self._values.get("monitoring_subscription")
        assert result is not None, "Required property 'monitoring_subscription' is missing"
        return typing.cast("CloudfrontMonitoringSubscriptionMonitoringSubscription", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontMonitoringSubscriptionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontMonitoringSubscriptionMonitoringSubscription",
    jsii_struct_bases=[],
    name_mapping={
        "realtime_metrics_subscription_config": "realtimeMetricsSubscriptionConfig",
    },
)
class CloudfrontMonitoringSubscriptionMonitoringSubscription:
    def __init__(
        self,
        *,
        realtime_metrics_subscription_config: "CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig",
    ) -> None:
        '''
        :param realtime_metrics_subscription_config: realtime_metrics_subscription_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#realtime_metrics_subscription_config CloudfrontMonitoringSubscription#realtime_metrics_subscription_config}
        '''
        if isinstance(realtime_metrics_subscription_config, dict):
            realtime_metrics_subscription_config = CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig(**realtime_metrics_subscription_config)
        self._values: typing.Dict[str, typing.Any] = {
            "realtime_metrics_subscription_config": realtime_metrics_subscription_config,
        }

    @builtins.property
    def realtime_metrics_subscription_config(
        self,
    ) -> "CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig":
        '''realtime_metrics_subscription_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#realtime_metrics_subscription_config CloudfrontMonitoringSubscription#realtime_metrics_subscription_config}
        '''
        result = self._values.get("realtime_metrics_subscription_config")
        assert result is not None, "Required property 'realtime_metrics_subscription_config' is missing"
        return typing.cast("CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontMonitoringSubscriptionMonitoringSubscription(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontMonitoringSubscriptionMonitoringSubscriptionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontMonitoringSubscriptionMonitoringSubscriptionOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putRealtimeMetricsSubscriptionConfig")
    def put_realtime_metrics_subscription_config(
        self,
        *,
        realtime_metrics_subscription_status: builtins.str,
    ) -> None:
        '''
        :param realtime_metrics_subscription_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#realtime_metrics_subscription_status CloudfrontMonitoringSubscription#realtime_metrics_subscription_status}.
        '''
        value = CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig(
            realtime_metrics_subscription_status=realtime_metrics_subscription_status
        )

        return typing.cast(None, jsii.invoke(self, "putRealtimeMetricsSubscriptionConfig", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="realtimeMetricsSubscriptionConfig")
    def realtime_metrics_subscription_config(
        self,
    ) -> "CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfigOutputReference":
        return typing.cast("CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfigOutputReference", jsii.get(self, "realtimeMetricsSubscriptionConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="realtimeMetricsSubscriptionConfigInput")
    def realtime_metrics_subscription_config_input(
        self,
    ) -> typing.Optional["CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig"]:
        return typing.cast(typing.Optional["CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig"], jsii.get(self, "realtimeMetricsSubscriptionConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontMonitoringSubscriptionMonitoringSubscription]:
        return typing.cast(typing.Optional[CloudfrontMonitoringSubscriptionMonitoringSubscription], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontMonitoringSubscriptionMonitoringSubscription],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig",
    jsii_struct_bases=[],
    name_mapping={
        "realtime_metrics_subscription_status": "realtimeMetricsSubscriptionStatus",
    },
)
class CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig:
    def __init__(self, *, realtime_metrics_subscription_status: builtins.str) -> None:
        '''
        :param realtime_metrics_subscription_status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#realtime_metrics_subscription_status CloudfrontMonitoringSubscription#realtime_metrics_subscription_status}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "realtime_metrics_subscription_status": realtime_metrics_subscription_status,
        }

    @builtins.property
    def realtime_metrics_subscription_status(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_monitoring_subscription#realtime_metrics_subscription_status CloudfrontMonitoringSubscription#realtime_metrics_subscription_status}.'''
        result = self._values.get("realtime_metrics_subscription_status")
        assert result is not None, "Required property 'realtime_metrics_subscription_status' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="realtimeMetricsSubscriptionStatusInput")
    def realtime_metrics_subscription_status_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "realtimeMetricsSubscriptionStatusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="realtimeMetricsSubscriptionStatus")
    def realtime_metrics_subscription_status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "realtimeMetricsSubscriptionStatus"))

    @realtime_metrics_subscription_status.setter
    def realtime_metrics_subscription_status(self, value: builtins.str) -> None:
        jsii.set(self, "realtimeMetricsSubscriptionStatus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig]:
        return typing.cast(typing.Optional[CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontOriginAccessIdentity(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginAccessIdentity",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_access_identity aws_cloudfront_origin_access_identity}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        comment: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_access_identity aws_cloudfront_origin_access_identity} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_access_identity#comment CloudfrontOriginAccessIdentity#comment}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontOriginAccessIdentityConfig(
            comment=comment,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callerReference")
    def caller_reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "callerReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudfrontAccessIdentityPath")
    def cloudfront_access_identity_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudfrontAccessIdentityPath"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamArn")
    def iam_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3CanonicalUserId")
    def s3_canonical_user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "s3CanonicalUserId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        jsii.set(self, "comment", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginAccessIdentityConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "comment": "comment",
    },
)
class CloudfrontOriginAccessIdentityConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        comment: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_access_identity#comment CloudfrontOriginAccessIdentity#comment}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if comment is not None:
            self._values["comment"] = comment

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
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_access_identity#comment CloudfrontOriginAccessIdentity#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontOriginAccessIdentityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontOriginRequestPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy aws_cloudfront_origin_request_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cookies_config: "CloudfrontOriginRequestPolicyCookiesConfig",
        headers_config: "CloudfrontOriginRequestPolicyHeadersConfig",
        name: builtins.str,
        query_strings_config: "CloudfrontOriginRequestPolicyQueryStringsConfig",
        comment: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy aws_cloudfront_origin_request_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cookies_config: cookies_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#cookies_config CloudfrontOriginRequestPolicy#cookies_config}
        :param headers_config: headers_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#headers_config CloudfrontOriginRequestPolicy#headers_config}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#name CloudfrontOriginRequestPolicy#name}.
        :param query_strings_config: query_strings_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#query_strings_config CloudfrontOriginRequestPolicy#query_strings_config}
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#comment CloudfrontOriginRequestPolicy#comment}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontOriginRequestPolicyConfig(
            cookies_config=cookies_config,
            headers_config=headers_config,
            name=name,
            query_strings_config=query_strings_config,
            comment=comment,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCookiesConfig")
    def put_cookies_config(
        self,
        *,
        cookie_behavior: builtins.str,
        cookies: typing.Optional["CloudfrontOriginRequestPolicyCookiesConfigCookies"] = None,
    ) -> None:
        '''
        :param cookie_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#cookie_behavior CloudfrontOriginRequestPolicy#cookie_behavior}.
        :param cookies: cookies block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#cookies CloudfrontOriginRequestPolicy#cookies}
        '''
        value = CloudfrontOriginRequestPolicyCookiesConfig(
            cookie_behavior=cookie_behavior, cookies=cookies
        )

        return typing.cast(None, jsii.invoke(self, "putCookiesConfig", [value]))

    @jsii.member(jsii_name="putHeadersConfig")
    def put_headers_config(
        self,
        *,
        header_behavior: typing.Optional[builtins.str] = None,
        headers: typing.Optional["CloudfrontOriginRequestPolicyHeadersConfigHeaders"] = None,
    ) -> None:
        '''
        :param header_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#header_behavior CloudfrontOriginRequestPolicy#header_behavior}.
        :param headers: headers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#headers CloudfrontOriginRequestPolicy#headers}
        '''
        value = CloudfrontOriginRequestPolicyHeadersConfig(
            header_behavior=header_behavior, headers=headers
        )

        return typing.cast(None, jsii.invoke(self, "putHeadersConfig", [value]))

    @jsii.member(jsii_name="putQueryStringsConfig")
    def put_query_strings_config(
        self,
        *,
        query_string_behavior: builtins.str,
        query_strings: typing.Optional["CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings"] = None,
    ) -> None:
        '''
        :param query_string_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#query_string_behavior CloudfrontOriginRequestPolicy#query_string_behavior}.
        :param query_strings: query_strings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#query_strings CloudfrontOriginRequestPolicy#query_strings}
        '''
        value = CloudfrontOriginRequestPolicyQueryStringsConfig(
            query_string_behavior=query_string_behavior, query_strings=query_strings
        )

        return typing.cast(None, jsii.invoke(self, "putQueryStringsConfig", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookiesConfig")
    def cookies_config(
        self,
    ) -> "CloudfrontOriginRequestPolicyCookiesConfigOutputReference":
        return typing.cast("CloudfrontOriginRequestPolicyCookiesConfigOutputReference", jsii.get(self, "cookiesConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersConfig")
    def headers_config(
        self,
    ) -> "CloudfrontOriginRequestPolicyHeadersConfigOutputReference":
        return typing.cast("CloudfrontOriginRequestPolicyHeadersConfigOutputReference", jsii.get(self, "headersConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringsConfig")
    def query_strings_config(
        self,
    ) -> "CloudfrontOriginRequestPolicyQueryStringsConfigOutputReference":
        return typing.cast("CloudfrontOriginRequestPolicyQueryStringsConfigOutputReference", jsii.get(self, "queryStringsConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookiesConfigInput")
    def cookies_config_input(
        self,
    ) -> typing.Optional["CloudfrontOriginRequestPolicyCookiesConfig"]:
        return typing.cast(typing.Optional["CloudfrontOriginRequestPolicyCookiesConfig"], jsii.get(self, "cookiesConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersConfigInput")
    def headers_config_input(
        self,
    ) -> typing.Optional["CloudfrontOriginRequestPolicyHeadersConfig"]:
        return typing.cast(typing.Optional["CloudfrontOriginRequestPolicyHeadersConfig"], jsii.get(self, "headersConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringsConfigInput")
    def query_strings_config_input(
        self,
    ) -> typing.Optional["CloudfrontOriginRequestPolicyQueryStringsConfig"]:
        return typing.cast(typing.Optional["CloudfrontOriginRequestPolicyQueryStringsConfig"], jsii.get(self, "queryStringsConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        jsii.set(self, "comment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cookies_config": "cookiesConfig",
        "headers_config": "headersConfig",
        "name": "name",
        "query_strings_config": "queryStringsConfig",
        "comment": "comment",
    },
)
class CloudfrontOriginRequestPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cookies_config: "CloudfrontOriginRequestPolicyCookiesConfig",
        headers_config: "CloudfrontOriginRequestPolicyHeadersConfig",
        name: builtins.str,
        query_strings_config: "CloudfrontOriginRequestPolicyQueryStringsConfig",
        comment: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cookies_config: cookies_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#cookies_config CloudfrontOriginRequestPolicy#cookies_config}
        :param headers_config: headers_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#headers_config CloudfrontOriginRequestPolicy#headers_config}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#name CloudfrontOriginRequestPolicy#name}.
        :param query_strings_config: query_strings_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#query_strings_config CloudfrontOriginRequestPolicy#query_strings_config}
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#comment CloudfrontOriginRequestPolicy#comment}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cookies_config, dict):
            cookies_config = CloudfrontOriginRequestPolicyCookiesConfig(**cookies_config)
        if isinstance(headers_config, dict):
            headers_config = CloudfrontOriginRequestPolicyHeadersConfig(**headers_config)
        if isinstance(query_strings_config, dict):
            query_strings_config = CloudfrontOriginRequestPolicyQueryStringsConfig(**query_strings_config)
        self._values: typing.Dict[str, typing.Any] = {
            "cookies_config": cookies_config,
            "headers_config": headers_config,
            "name": name,
            "query_strings_config": query_strings_config,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if comment is not None:
            self._values["comment"] = comment

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
    def cookies_config(self) -> "CloudfrontOriginRequestPolicyCookiesConfig":
        '''cookies_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#cookies_config CloudfrontOriginRequestPolicy#cookies_config}
        '''
        result = self._values.get("cookies_config")
        assert result is not None, "Required property 'cookies_config' is missing"
        return typing.cast("CloudfrontOriginRequestPolicyCookiesConfig", result)

    @builtins.property
    def headers_config(self) -> "CloudfrontOriginRequestPolicyHeadersConfig":
        '''headers_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#headers_config CloudfrontOriginRequestPolicy#headers_config}
        '''
        result = self._values.get("headers_config")
        assert result is not None, "Required property 'headers_config' is missing"
        return typing.cast("CloudfrontOriginRequestPolicyHeadersConfig", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#name CloudfrontOriginRequestPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query_strings_config(self) -> "CloudfrontOriginRequestPolicyQueryStringsConfig":
        '''query_strings_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#query_strings_config CloudfrontOriginRequestPolicy#query_strings_config}
        '''
        result = self._values.get("query_strings_config")
        assert result is not None, "Required property 'query_strings_config' is missing"
        return typing.cast("CloudfrontOriginRequestPolicyQueryStringsConfig", result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#comment CloudfrontOriginRequestPolicy#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontOriginRequestPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyCookiesConfig",
    jsii_struct_bases=[],
    name_mapping={"cookie_behavior": "cookieBehavior", "cookies": "cookies"},
)
class CloudfrontOriginRequestPolicyCookiesConfig:
    def __init__(
        self,
        *,
        cookie_behavior: builtins.str,
        cookies: typing.Optional["CloudfrontOriginRequestPolicyCookiesConfigCookies"] = None,
    ) -> None:
        '''
        :param cookie_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#cookie_behavior CloudfrontOriginRequestPolicy#cookie_behavior}.
        :param cookies: cookies block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#cookies CloudfrontOriginRequestPolicy#cookies}
        '''
        if isinstance(cookies, dict):
            cookies = CloudfrontOriginRequestPolicyCookiesConfigCookies(**cookies)
        self._values: typing.Dict[str, typing.Any] = {
            "cookie_behavior": cookie_behavior,
        }
        if cookies is not None:
            self._values["cookies"] = cookies

    @builtins.property
    def cookie_behavior(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#cookie_behavior CloudfrontOriginRequestPolicy#cookie_behavior}.'''
        result = self._values.get("cookie_behavior")
        assert result is not None, "Required property 'cookie_behavior' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cookies(
        self,
    ) -> typing.Optional["CloudfrontOriginRequestPolicyCookiesConfigCookies"]:
        '''cookies block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#cookies CloudfrontOriginRequestPolicy#cookies}
        '''
        result = self._values.get("cookies")
        return typing.cast(typing.Optional["CloudfrontOriginRequestPolicyCookiesConfigCookies"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontOriginRequestPolicyCookiesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyCookiesConfigCookies",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontOriginRequestPolicyCookiesConfigCookies:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#items CloudfrontOriginRequestPolicy#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#items CloudfrontOriginRequestPolicy#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontOriginRequestPolicyCookiesConfigCookies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontOriginRequestPolicyCookiesConfigCookiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyCookiesConfigCookiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontOriginRequestPolicyCookiesConfigCookies]:
        return typing.cast(typing.Optional[CloudfrontOriginRequestPolicyCookiesConfigCookies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontOriginRequestPolicyCookiesConfigCookies],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontOriginRequestPolicyCookiesConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyCookiesConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putCookies")
    def put_cookies(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#items CloudfrontOriginRequestPolicy#items}.
        '''
        value = CloudfrontOriginRequestPolicyCookiesConfigCookies(items=items)

        return typing.cast(None, jsii.invoke(self, "putCookies", [value]))

    @jsii.member(jsii_name="resetCookies")
    def reset_cookies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCookies", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookies")
    def cookies(
        self,
    ) -> CloudfrontOriginRequestPolicyCookiesConfigCookiesOutputReference:
        return typing.cast(CloudfrontOriginRequestPolicyCookiesConfigCookiesOutputReference, jsii.get(self, "cookies"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookieBehaviorInput")
    def cookie_behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cookieBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookiesInput")
    def cookies_input(
        self,
    ) -> typing.Optional[CloudfrontOriginRequestPolicyCookiesConfigCookies]:
        return typing.cast(typing.Optional[CloudfrontOriginRequestPolicyCookiesConfigCookies], jsii.get(self, "cookiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookieBehavior")
    def cookie_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cookieBehavior"))

    @cookie_behavior.setter
    def cookie_behavior(self, value: builtins.str) -> None:
        jsii.set(self, "cookieBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontOriginRequestPolicyCookiesConfig]:
        return typing.cast(typing.Optional[CloudfrontOriginRequestPolicyCookiesConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontOriginRequestPolicyCookiesConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyHeadersConfig",
    jsii_struct_bases=[],
    name_mapping={"header_behavior": "headerBehavior", "headers": "headers"},
)
class CloudfrontOriginRequestPolicyHeadersConfig:
    def __init__(
        self,
        *,
        header_behavior: typing.Optional[builtins.str] = None,
        headers: typing.Optional["CloudfrontOriginRequestPolicyHeadersConfigHeaders"] = None,
    ) -> None:
        '''
        :param header_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#header_behavior CloudfrontOriginRequestPolicy#header_behavior}.
        :param headers: headers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#headers CloudfrontOriginRequestPolicy#headers}
        '''
        if isinstance(headers, dict):
            headers = CloudfrontOriginRequestPolicyHeadersConfigHeaders(**headers)
        self._values: typing.Dict[str, typing.Any] = {}
        if header_behavior is not None:
            self._values["header_behavior"] = header_behavior
        if headers is not None:
            self._values["headers"] = headers

    @builtins.property
    def header_behavior(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#header_behavior CloudfrontOriginRequestPolicy#header_behavior}.'''
        result = self._values.get("header_behavior")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def headers(
        self,
    ) -> typing.Optional["CloudfrontOriginRequestPolicyHeadersConfigHeaders"]:
        '''headers block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#headers CloudfrontOriginRequestPolicy#headers}
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional["CloudfrontOriginRequestPolicyHeadersConfigHeaders"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontOriginRequestPolicyHeadersConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyHeadersConfigHeaders",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontOriginRequestPolicyHeadersConfigHeaders:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#items CloudfrontOriginRequestPolicy#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#items CloudfrontOriginRequestPolicy#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontOriginRequestPolicyHeadersConfigHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontOriginRequestPolicyHeadersConfigHeadersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyHeadersConfigHeadersOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontOriginRequestPolicyHeadersConfigHeaders]:
        return typing.cast(typing.Optional[CloudfrontOriginRequestPolicyHeadersConfigHeaders], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontOriginRequestPolicyHeadersConfigHeaders],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontOriginRequestPolicyHeadersConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyHeadersConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putHeaders")
    def put_headers(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#items CloudfrontOriginRequestPolicy#items}.
        '''
        value = CloudfrontOriginRequestPolicyHeadersConfigHeaders(items=items)

        return typing.cast(None, jsii.invoke(self, "putHeaders", [value]))

    @jsii.member(jsii_name="resetHeaderBehavior")
    def reset_header_behavior(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaderBehavior", []))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headers")
    def headers(
        self,
    ) -> CloudfrontOriginRequestPolicyHeadersConfigHeadersOutputReference:
        return typing.cast(CloudfrontOriginRequestPolicyHeadersConfigHeadersOutputReference, jsii.get(self, "headers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headerBehaviorInput")
    def header_behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "headerBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersInput")
    def headers_input(
        self,
    ) -> typing.Optional[CloudfrontOriginRequestPolicyHeadersConfigHeaders]:
        return typing.cast(typing.Optional[CloudfrontOriginRequestPolicyHeadersConfigHeaders], jsii.get(self, "headersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headerBehavior")
    def header_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerBehavior"))

    @header_behavior.setter
    def header_behavior(self, value: builtins.str) -> None:
        jsii.set(self, "headerBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontOriginRequestPolicyHeadersConfig]:
        return typing.cast(typing.Optional[CloudfrontOriginRequestPolicyHeadersConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontOriginRequestPolicyHeadersConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyQueryStringsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "query_string_behavior": "queryStringBehavior",
        "query_strings": "queryStrings",
    },
)
class CloudfrontOriginRequestPolicyQueryStringsConfig:
    def __init__(
        self,
        *,
        query_string_behavior: builtins.str,
        query_strings: typing.Optional["CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings"] = None,
    ) -> None:
        '''
        :param query_string_behavior: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#query_string_behavior CloudfrontOriginRequestPolicy#query_string_behavior}.
        :param query_strings: query_strings block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#query_strings CloudfrontOriginRequestPolicy#query_strings}
        '''
        if isinstance(query_strings, dict):
            query_strings = CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings(**query_strings)
        self._values: typing.Dict[str, typing.Any] = {
            "query_string_behavior": query_string_behavior,
        }
        if query_strings is not None:
            self._values["query_strings"] = query_strings

    @builtins.property
    def query_string_behavior(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#query_string_behavior CloudfrontOriginRequestPolicy#query_string_behavior}.'''
        result = self._values.get("query_string_behavior")
        assert result is not None, "Required property 'query_string_behavior' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def query_strings(
        self,
    ) -> typing.Optional["CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings"]:
        '''query_strings block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#query_strings CloudfrontOriginRequestPolicy#query_strings}
        '''
        result = self._values.get("query_strings")
        return typing.cast(typing.Optional["CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontOriginRequestPolicyQueryStringsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontOriginRequestPolicyQueryStringsConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyQueryStringsConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putQueryStrings")
    def put_query_strings(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#items CloudfrontOriginRequestPolicy#items}.
        '''
        value = CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings(
            items=items
        )

        return typing.cast(None, jsii.invoke(self, "putQueryStrings", [value]))

    @jsii.member(jsii_name="resetQueryStrings")
    def reset_query_strings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQueryStrings", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStrings")
    def query_strings(
        self,
    ) -> "CloudfrontOriginRequestPolicyQueryStringsConfigQueryStringsOutputReference":
        return typing.cast("CloudfrontOriginRequestPolicyQueryStringsConfigQueryStringsOutputReference", jsii.get(self, "queryStrings"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringBehaviorInput")
    def query_string_behavior_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryStringBehaviorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringsInput")
    def query_strings_input(
        self,
    ) -> typing.Optional["CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings"]:
        return typing.cast(typing.Optional["CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings"], jsii.get(self, "queryStringsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringBehavior")
    def query_string_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryStringBehavior"))

    @query_string_behavior.setter
    def query_string_behavior(self, value: builtins.str) -> None:
        jsii.set(self, "queryStringBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontOriginRequestPolicyQueryStringsConfig]:
        return typing.cast(typing.Optional[CloudfrontOriginRequestPolicyQueryStringsConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontOriginRequestPolicyQueryStringsConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#items CloudfrontOriginRequestPolicy#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_origin_request_policy#items CloudfrontOriginRequestPolicy#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontOriginRequestPolicyQueryStringsConfigQueryStringsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontOriginRequestPolicyQueryStringsConfigQueryStringsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings]:
        return typing.cast(typing.Optional[CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontPublicKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontPublicKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key aws_cloudfront_public_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        encoded_key: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key aws_cloudfront_public_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param encoded_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#encoded_key CloudfrontPublicKey#encoded_key}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#comment CloudfrontPublicKey#comment}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#name CloudfrontPublicKey#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#name_prefix CloudfrontPublicKey#name_prefix}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontPublicKeyConfig(
            encoded_key=encoded_key,
            comment=comment,
            name=name,
            name_prefix=name_prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="callerReference")
    def caller_reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "callerReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encodedKeyInput")
    def encoded_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encodedKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        jsii.set(self, "comment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encodedKey")
    def encoded_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encodedKey"))

    @encoded_key.setter
    def encoded_key(self, value: builtins.str) -> None:
        jsii.set(self, "encodedKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontPublicKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "encoded_key": "encodedKey",
        "comment": "comment",
        "name": "name",
        "name_prefix": "namePrefix",
    },
)
class CloudfrontPublicKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        encoded_key: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param encoded_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#encoded_key CloudfrontPublicKey#encoded_key}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#comment CloudfrontPublicKey#comment}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#name CloudfrontPublicKey#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#name_prefix CloudfrontPublicKey#name_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "encoded_key": encoded_key,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if comment is not None:
            self._values["comment"] = comment
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix

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
    def encoded_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#encoded_key CloudfrontPublicKey#encoded_key}.'''
        result = self._values.get("encoded_key")
        assert result is not None, "Required property 'encoded_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#comment CloudfrontPublicKey#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#name CloudfrontPublicKey#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_public_key#name_prefix CloudfrontPublicKey#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontPublicKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontRealtimeLogConfig(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontRealtimeLogConfig",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config aws_cloudfront_realtime_log_config}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        endpoint: "CloudfrontRealtimeLogConfigEndpoint",
        fields: typing.Sequence[builtins.str],
        name: builtins.str,
        sampling_rate: jsii.Number,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config aws_cloudfront_realtime_log_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param endpoint: endpoint block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#endpoint CloudfrontRealtimeLogConfig#endpoint}
        :param fields: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#fields CloudfrontRealtimeLogConfig#fields}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#name CloudfrontRealtimeLogConfig#name}.
        :param sampling_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#sampling_rate CloudfrontRealtimeLogConfig#sampling_rate}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontRealtimeLogConfigConfig(
            endpoint=endpoint,
            fields=fields,
            name=name,
            sampling_rate=sampling_rate,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putEndpoint")
    def put_endpoint(
        self,
        *,
        kinesis_stream_config: "CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig",
        stream_type: builtins.str,
    ) -> None:
        '''
        :param kinesis_stream_config: kinesis_stream_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#kinesis_stream_config CloudfrontRealtimeLogConfig#kinesis_stream_config}
        :param stream_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#stream_type CloudfrontRealtimeLogConfig#stream_type}.
        '''
        value = CloudfrontRealtimeLogConfigEndpoint(
            kinesis_stream_config=kinesis_stream_config, stream_type=stream_type
        )

        return typing.cast(None, jsii.invoke(self, "putEndpoint", [value]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> "CloudfrontRealtimeLogConfigEndpointOutputReference":
        return typing.cast("CloudfrontRealtimeLogConfigEndpointOutputReference", jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional["CloudfrontRealtimeLogConfigEndpoint"]:
        return typing.cast(typing.Optional["CloudfrontRealtimeLogConfigEndpoint"], jsii.get(self, "endpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldsInput")
    def fields_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "fieldsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samplingRateInput")
    def sampling_rate_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "samplingRateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fields")
    def fields(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "fields"))

    @fields.setter
    def fields(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "fields", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samplingRate")
    def sampling_rate(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "samplingRate"))

    @sampling_rate.setter
    def sampling_rate(self, value: jsii.Number) -> None:
        jsii.set(self, "samplingRate", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontRealtimeLogConfigConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "endpoint": "endpoint",
        "fields": "fields",
        "name": "name",
        "sampling_rate": "samplingRate",
    },
)
class CloudfrontRealtimeLogConfigConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        endpoint: "CloudfrontRealtimeLogConfigEndpoint",
        fields: typing.Sequence[builtins.str],
        name: builtins.str,
        sampling_rate: jsii.Number,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param endpoint: endpoint block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#endpoint CloudfrontRealtimeLogConfig#endpoint}
        :param fields: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#fields CloudfrontRealtimeLogConfig#fields}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#name CloudfrontRealtimeLogConfig#name}.
        :param sampling_rate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#sampling_rate CloudfrontRealtimeLogConfig#sampling_rate}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(endpoint, dict):
            endpoint = CloudfrontRealtimeLogConfigEndpoint(**endpoint)
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint": endpoint,
            "fields": fields,
            "name": name,
            "sampling_rate": sampling_rate,
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
    def endpoint(self) -> "CloudfrontRealtimeLogConfigEndpoint":
        '''endpoint block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#endpoint CloudfrontRealtimeLogConfig#endpoint}
        '''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast("CloudfrontRealtimeLogConfigEndpoint", result)

    @builtins.property
    def fields(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#fields CloudfrontRealtimeLogConfig#fields}.'''
        result = self._values.get("fields")
        assert result is not None, "Required property 'fields' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#name CloudfrontRealtimeLogConfig#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sampling_rate(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#sampling_rate CloudfrontRealtimeLogConfig#sampling_rate}.'''
        result = self._values.get("sampling_rate")
        assert result is not None, "Required property 'sampling_rate' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontRealtimeLogConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontRealtimeLogConfigEndpoint",
    jsii_struct_bases=[],
    name_mapping={
        "kinesis_stream_config": "kinesisStreamConfig",
        "stream_type": "streamType",
    },
)
class CloudfrontRealtimeLogConfigEndpoint:
    def __init__(
        self,
        *,
        kinesis_stream_config: "CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig",
        stream_type: builtins.str,
    ) -> None:
        '''
        :param kinesis_stream_config: kinesis_stream_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#kinesis_stream_config CloudfrontRealtimeLogConfig#kinesis_stream_config}
        :param stream_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#stream_type CloudfrontRealtimeLogConfig#stream_type}.
        '''
        if isinstance(kinesis_stream_config, dict):
            kinesis_stream_config = CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig(**kinesis_stream_config)
        self._values: typing.Dict[str, typing.Any] = {
            "kinesis_stream_config": kinesis_stream_config,
            "stream_type": stream_type,
        }

    @builtins.property
    def kinesis_stream_config(
        self,
    ) -> "CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig":
        '''kinesis_stream_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#kinesis_stream_config CloudfrontRealtimeLogConfig#kinesis_stream_config}
        '''
        result = self._values.get("kinesis_stream_config")
        assert result is not None, "Required property 'kinesis_stream_config' is missing"
        return typing.cast("CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig", result)

    @builtins.property
    def stream_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#stream_type CloudfrontRealtimeLogConfig#stream_type}.'''
        result = self._values.get("stream_type")
        assert result is not None, "Required property 'stream_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontRealtimeLogConfigEndpoint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig",
    jsii_struct_bases=[],
    name_mapping={"role_arn": "roleArn", "stream_arn": "streamArn"},
)
class CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig:
    def __init__(self, *, role_arn: builtins.str, stream_arn: builtins.str) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#role_arn CloudfrontRealtimeLogConfig#role_arn}.
        :param stream_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#stream_arn CloudfrontRealtimeLogConfig#stream_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "stream_arn": stream_arn,
        }

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#role_arn CloudfrontRealtimeLogConfig#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stream_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#stream_arn CloudfrontRealtimeLogConfig#stream_arn}.'''
        result = self._values.get("stream_arn")
        assert result is not None, "Required property 'stream_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontRealtimeLogConfigEndpointKinesisStreamConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontRealtimeLogConfigEndpointKinesisStreamConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamArnInput")
    def stream_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streamArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamArn")
    def stream_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamArn"))

    @stream_arn.setter
    def stream_arn(self, value: builtins.str) -> None:
        jsii.set(self, "streamArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig]:
        return typing.cast(typing.Optional[CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontRealtimeLogConfigEndpointOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontRealtimeLogConfigEndpointOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putKinesisStreamConfig")
    def put_kinesis_stream_config(
        self,
        *,
        role_arn: builtins.str,
        stream_arn: builtins.str,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#role_arn CloudfrontRealtimeLogConfig#role_arn}.
        :param stream_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_realtime_log_config#stream_arn CloudfrontRealtimeLogConfig#stream_arn}.
        '''
        value = CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig(
            role_arn=role_arn, stream_arn=stream_arn
        )

        return typing.cast(None, jsii.invoke(self, "putKinesisStreamConfig", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisStreamConfig")
    def kinesis_stream_config(
        self,
    ) -> CloudfrontRealtimeLogConfigEndpointKinesisStreamConfigOutputReference:
        return typing.cast(CloudfrontRealtimeLogConfigEndpointKinesisStreamConfigOutputReference, jsii.get(self, "kinesisStreamConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisStreamConfigInput")
    def kinesis_stream_config_input(
        self,
    ) -> typing.Optional[CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig]:
        return typing.cast(typing.Optional[CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig], jsii.get(self, "kinesisStreamConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamTypeInput")
    def stream_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streamTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamType")
    def stream_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamType"))

    @stream_type.setter
    def stream_type(self, value: builtins.str) -> None:
        jsii.set(self, "streamType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudfrontRealtimeLogConfigEndpoint]:
        return typing.cast(typing.Optional[CloudfrontRealtimeLogConfigEndpoint], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontRealtimeLogConfigEndpoint],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontResponseHeadersPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy aws_cloudfront_response_headers_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        cors_config: typing.Optional["CloudfrontResponseHeadersPolicyCorsConfig"] = None,
        custom_headers_config: typing.Optional["CloudfrontResponseHeadersPolicyCustomHeadersConfig"] = None,
        etag: typing.Optional[builtins.str] = None,
        security_headers_config: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfig"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy aws_cloudfront_response_headers_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#name CloudfrontResponseHeadersPolicy#name}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#comment CloudfrontResponseHeadersPolicy#comment}.
        :param cors_config: cors_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#cors_config CloudfrontResponseHeadersPolicy#cors_config}
        :param custom_headers_config: custom_headers_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#custom_headers_config CloudfrontResponseHeadersPolicy#custom_headers_config}
        :param etag: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#etag CloudfrontResponseHeadersPolicy#etag}.
        :param security_headers_config: security_headers_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#security_headers_config CloudfrontResponseHeadersPolicy#security_headers_config}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudfrontResponseHeadersPolicyConfig(
            name=name,
            comment=comment,
            cors_config=cors_config,
            custom_headers_config=custom_headers_config,
            etag=etag,
            security_headers_config=security_headers_config,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCorsConfig")
    def put_cors_config(
        self,
        *,
        access_control_allow_credentials: typing.Union[builtins.bool, cdktf.IResolvable],
        access_control_allow_headers: "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders",
        access_control_allow_methods: "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods",
        access_control_allow_origins: "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins",
        origin_override: typing.Union[builtins.bool, cdktf.IResolvable],
        access_control_expose_headers: typing.Optional["CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders"] = None,
        access_control_max_age_sec: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param access_control_allow_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_credentials CloudfrontResponseHeadersPolicy#access_control_allow_credentials}.
        :param access_control_allow_headers: access_control_allow_headers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_headers CloudfrontResponseHeadersPolicy#access_control_allow_headers}
        :param access_control_allow_methods: access_control_allow_methods block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_methods CloudfrontResponseHeadersPolicy#access_control_allow_methods}
        :param access_control_allow_origins: access_control_allow_origins block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_origins CloudfrontResponseHeadersPolicy#access_control_allow_origins}
        :param origin_override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#origin_override CloudfrontResponseHeadersPolicy#origin_override}.
        :param access_control_expose_headers: access_control_expose_headers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_expose_headers CloudfrontResponseHeadersPolicy#access_control_expose_headers}
        :param access_control_max_age_sec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_max_age_sec CloudfrontResponseHeadersPolicy#access_control_max_age_sec}.
        '''
        value = CloudfrontResponseHeadersPolicyCorsConfig(
            access_control_allow_credentials=access_control_allow_credentials,
            access_control_allow_headers=access_control_allow_headers,
            access_control_allow_methods=access_control_allow_methods,
            access_control_allow_origins=access_control_allow_origins,
            origin_override=origin_override,
            access_control_expose_headers=access_control_expose_headers,
            access_control_max_age_sec=access_control_max_age_sec,
        )

        return typing.cast(None, jsii.invoke(self, "putCorsConfig", [value]))

    @jsii.member(jsii_name="putCustomHeadersConfig")
    def put_custom_headers_config(
        self,
        *,
        items: typing.Optional[typing.Sequence["CloudfrontResponseHeadersPolicyCustomHeadersConfigItems"]] = None,
    ) -> None:
        '''
        :param items: items block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}
        '''
        value = CloudfrontResponseHeadersPolicyCustomHeadersConfig(items=items)

        return typing.cast(None, jsii.invoke(self, "putCustomHeadersConfig", [value]))

    @jsii.member(jsii_name="putSecurityHeadersConfig")
    def put_security_headers_config(
        self,
        *,
        content_security_policy: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy"] = None,
        content_type_options: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions"] = None,
        frame_options: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions"] = None,
        referrer_policy: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy"] = None,
        strict_transport_security: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity"] = None,
        xss_protection: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection"] = None,
    ) -> None:
        '''
        :param content_security_policy: content_security_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#content_security_policy CloudfrontResponseHeadersPolicy#content_security_policy}
        :param content_type_options: content_type_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#content_type_options CloudfrontResponseHeadersPolicy#content_type_options}
        :param frame_options: frame_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#frame_options CloudfrontResponseHeadersPolicy#frame_options}
        :param referrer_policy: referrer_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#referrer_policy CloudfrontResponseHeadersPolicy#referrer_policy}
        :param strict_transport_security: strict_transport_security block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#strict_transport_security CloudfrontResponseHeadersPolicy#strict_transport_security}
        :param xss_protection: xss_protection block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#xss_protection CloudfrontResponseHeadersPolicy#xss_protection}
        '''
        value = CloudfrontResponseHeadersPolicySecurityHeadersConfig(
            content_security_policy=content_security_policy,
            content_type_options=content_type_options,
            frame_options=frame_options,
            referrer_policy=referrer_policy,
            strict_transport_security=strict_transport_security,
            xss_protection=xss_protection,
        )

        return typing.cast(None, jsii.invoke(self, "putSecurityHeadersConfig", [value]))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetCorsConfig")
    def reset_cors_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCorsConfig", []))

    @jsii.member(jsii_name="resetCustomHeadersConfig")
    def reset_custom_headers_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomHeadersConfig", []))

    @jsii.member(jsii_name="resetEtag")
    def reset_etag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEtag", []))

    @jsii.member(jsii_name="resetSecurityHeadersConfig")
    def reset_security_headers_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityHeadersConfig", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="corsConfig")
    def cors_config(self) -> "CloudfrontResponseHeadersPolicyCorsConfigOutputReference":
        return typing.cast("CloudfrontResponseHeadersPolicyCorsConfigOutputReference", jsii.get(self, "corsConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customHeadersConfig")
    def custom_headers_config(
        self,
    ) -> "CloudfrontResponseHeadersPolicyCustomHeadersConfigOutputReference":
        return typing.cast("CloudfrontResponseHeadersPolicyCustomHeadersConfigOutputReference", jsii.get(self, "customHeadersConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityHeadersConfig")
    def security_headers_config(
        self,
    ) -> "CloudfrontResponseHeadersPolicySecurityHeadersConfigOutputReference":
        return typing.cast("CloudfrontResponseHeadersPolicySecurityHeadersConfigOutputReference", jsii.get(self, "securityHeadersConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="corsConfigInput")
    def cors_config_input(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicyCorsConfig"]:
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicyCorsConfig"], jsii.get(self, "corsConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customHeadersConfigInput")
    def custom_headers_config_input(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicyCustomHeadersConfig"]:
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicyCustomHeadersConfig"], jsii.get(self, "customHeadersConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etagInput")
    def etag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "etagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityHeadersConfigInput")
    def security_headers_config_input(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfig"]:
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfig"], jsii.get(self, "securityHeadersConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        jsii.set(self, "comment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @etag.setter
    def etag(self, value: builtins.str) -> None:
        jsii.set(self, "etag", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "comment": "comment",
        "cors_config": "corsConfig",
        "custom_headers_config": "customHeadersConfig",
        "etag": "etag",
        "security_headers_config": "securityHeadersConfig",
    },
)
class CloudfrontResponseHeadersPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        comment: typing.Optional[builtins.str] = None,
        cors_config: typing.Optional["CloudfrontResponseHeadersPolicyCorsConfig"] = None,
        custom_headers_config: typing.Optional["CloudfrontResponseHeadersPolicyCustomHeadersConfig"] = None,
        etag: typing.Optional[builtins.str] = None,
        security_headers_config: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfig"] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#name CloudfrontResponseHeadersPolicy#name}.
        :param comment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#comment CloudfrontResponseHeadersPolicy#comment}.
        :param cors_config: cors_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#cors_config CloudfrontResponseHeadersPolicy#cors_config}
        :param custom_headers_config: custom_headers_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#custom_headers_config CloudfrontResponseHeadersPolicy#custom_headers_config}
        :param etag: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#etag CloudfrontResponseHeadersPolicy#etag}.
        :param security_headers_config: security_headers_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#security_headers_config CloudfrontResponseHeadersPolicy#security_headers_config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cors_config, dict):
            cors_config = CloudfrontResponseHeadersPolicyCorsConfig(**cors_config)
        if isinstance(custom_headers_config, dict):
            custom_headers_config = CloudfrontResponseHeadersPolicyCustomHeadersConfig(**custom_headers_config)
        if isinstance(security_headers_config, dict):
            security_headers_config = CloudfrontResponseHeadersPolicySecurityHeadersConfig(**security_headers_config)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if comment is not None:
            self._values["comment"] = comment
        if cors_config is not None:
            self._values["cors_config"] = cors_config
        if custom_headers_config is not None:
            self._values["custom_headers_config"] = custom_headers_config
        if etag is not None:
            self._values["etag"] = etag
        if security_headers_config is not None:
            self._values["security_headers_config"] = security_headers_config

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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#name CloudfrontResponseHeadersPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#comment CloudfrontResponseHeadersPolicy#comment}.'''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cors_config(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicyCorsConfig"]:
        '''cors_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#cors_config CloudfrontResponseHeadersPolicy#cors_config}
        '''
        result = self._values.get("cors_config")
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicyCorsConfig"], result)

    @builtins.property
    def custom_headers_config(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicyCustomHeadersConfig"]:
        '''custom_headers_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#custom_headers_config CloudfrontResponseHeadersPolicy#custom_headers_config}
        '''
        result = self._values.get("custom_headers_config")
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicyCustomHeadersConfig"], result)

    @builtins.property
    def etag(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#etag CloudfrontResponseHeadersPolicy#etag}.'''
        result = self._values.get("etag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_headers_config(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfig"]:
        '''security_headers_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#security_headers_config CloudfrontResponseHeadersPolicy#security_headers_config}
        '''
        result = self._values.get("security_headers_config")
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCorsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "access_control_allow_credentials": "accessControlAllowCredentials",
        "access_control_allow_headers": "accessControlAllowHeaders",
        "access_control_allow_methods": "accessControlAllowMethods",
        "access_control_allow_origins": "accessControlAllowOrigins",
        "origin_override": "originOverride",
        "access_control_expose_headers": "accessControlExposeHeaders",
        "access_control_max_age_sec": "accessControlMaxAgeSec",
    },
)
class CloudfrontResponseHeadersPolicyCorsConfig:
    def __init__(
        self,
        *,
        access_control_allow_credentials: typing.Union[builtins.bool, cdktf.IResolvable],
        access_control_allow_headers: "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders",
        access_control_allow_methods: "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods",
        access_control_allow_origins: "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins",
        origin_override: typing.Union[builtins.bool, cdktf.IResolvable],
        access_control_expose_headers: typing.Optional["CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders"] = None,
        access_control_max_age_sec: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param access_control_allow_credentials: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_credentials CloudfrontResponseHeadersPolicy#access_control_allow_credentials}.
        :param access_control_allow_headers: access_control_allow_headers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_headers CloudfrontResponseHeadersPolicy#access_control_allow_headers}
        :param access_control_allow_methods: access_control_allow_methods block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_methods CloudfrontResponseHeadersPolicy#access_control_allow_methods}
        :param access_control_allow_origins: access_control_allow_origins block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_origins CloudfrontResponseHeadersPolicy#access_control_allow_origins}
        :param origin_override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#origin_override CloudfrontResponseHeadersPolicy#origin_override}.
        :param access_control_expose_headers: access_control_expose_headers block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_expose_headers CloudfrontResponseHeadersPolicy#access_control_expose_headers}
        :param access_control_max_age_sec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_max_age_sec CloudfrontResponseHeadersPolicy#access_control_max_age_sec}.
        '''
        if isinstance(access_control_allow_headers, dict):
            access_control_allow_headers = CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders(**access_control_allow_headers)
        if isinstance(access_control_allow_methods, dict):
            access_control_allow_methods = CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods(**access_control_allow_methods)
        if isinstance(access_control_allow_origins, dict):
            access_control_allow_origins = CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins(**access_control_allow_origins)
        if isinstance(access_control_expose_headers, dict):
            access_control_expose_headers = CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders(**access_control_expose_headers)
        self._values: typing.Dict[str, typing.Any] = {
            "access_control_allow_credentials": access_control_allow_credentials,
            "access_control_allow_headers": access_control_allow_headers,
            "access_control_allow_methods": access_control_allow_methods,
            "access_control_allow_origins": access_control_allow_origins,
            "origin_override": origin_override,
        }
        if access_control_expose_headers is not None:
            self._values["access_control_expose_headers"] = access_control_expose_headers
        if access_control_max_age_sec is not None:
            self._values["access_control_max_age_sec"] = access_control_max_age_sec

    @builtins.property
    def access_control_allow_credentials(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_credentials CloudfrontResponseHeadersPolicy#access_control_allow_credentials}.'''
        result = self._values.get("access_control_allow_credentials")
        assert result is not None, "Required property 'access_control_allow_credentials' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def access_control_allow_headers(
        self,
    ) -> "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders":
        '''access_control_allow_headers block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_headers CloudfrontResponseHeadersPolicy#access_control_allow_headers}
        '''
        result = self._values.get("access_control_allow_headers")
        assert result is not None, "Required property 'access_control_allow_headers' is missing"
        return typing.cast("CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders", result)

    @builtins.property
    def access_control_allow_methods(
        self,
    ) -> "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods":
        '''access_control_allow_methods block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_methods CloudfrontResponseHeadersPolicy#access_control_allow_methods}
        '''
        result = self._values.get("access_control_allow_methods")
        assert result is not None, "Required property 'access_control_allow_methods' is missing"
        return typing.cast("CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods", result)

    @builtins.property
    def access_control_allow_origins(
        self,
    ) -> "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins":
        '''access_control_allow_origins block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_allow_origins CloudfrontResponseHeadersPolicy#access_control_allow_origins}
        '''
        result = self._values.get("access_control_allow_origins")
        assert result is not None, "Required property 'access_control_allow_origins' is missing"
        return typing.cast("CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins", result)

    @builtins.property
    def origin_override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#origin_override CloudfrontResponseHeadersPolicy#origin_override}.'''
        result = self._values.get("origin_override")
        assert result is not None, "Required property 'origin_override' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def access_control_expose_headers(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders"]:
        '''access_control_expose_headers block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_expose_headers CloudfrontResponseHeadersPolicy#access_control_expose_headers}
        '''
        result = self._values.get("access_control_expose_headers")
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders"], result)

    @builtins.property
    def access_control_max_age_sec(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_max_age_sec CloudfrontResponseHeadersPolicy#access_control_max_age_sec}.'''
        result = self._values.get("access_control_max_age_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicyCorsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeadersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeadersOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethodsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethodsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOriginsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOriginsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.'''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeadersOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeadersOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))

    @items.setter
    def items(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontResponseHeadersPolicyCorsConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCorsConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putAccessControlAllowHeaders")
    def put_access_control_allow_headers(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.
        '''
        value = CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders(
            items=items
        )

        return typing.cast(None, jsii.invoke(self, "putAccessControlAllowHeaders", [value]))

    @jsii.member(jsii_name="putAccessControlAllowMethods")
    def put_access_control_allow_methods(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.
        '''
        value = CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods(
            items=items
        )

        return typing.cast(None, jsii.invoke(self, "putAccessControlAllowMethods", [value]))

    @jsii.member(jsii_name="putAccessControlAllowOrigins")
    def put_access_control_allow_origins(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.
        '''
        value = CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins(
            items=items
        )

        return typing.cast(None, jsii.invoke(self, "putAccessControlAllowOrigins", [value]))

    @jsii.member(jsii_name="putAccessControlExposeHeaders")
    def put_access_control_expose_headers(
        self,
        *,
        items: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param items: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}.
        '''
        value = CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders(
            items=items
        )

        return typing.cast(None, jsii.invoke(self, "putAccessControlExposeHeaders", [value]))

    @jsii.member(jsii_name="resetAccessControlExposeHeaders")
    def reset_access_control_expose_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessControlExposeHeaders", []))

    @jsii.member(jsii_name="resetAccessControlMaxAgeSec")
    def reset_access_control_max_age_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessControlMaxAgeSec", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowHeaders")
    def access_control_allow_headers(
        self,
    ) -> CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeadersOutputReference:
        return typing.cast(CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeadersOutputReference, jsii.get(self, "accessControlAllowHeaders"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowMethods")
    def access_control_allow_methods(
        self,
    ) -> CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethodsOutputReference:
        return typing.cast(CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethodsOutputReference, jsii.get(self, "accessControlAllowMethods"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowOrigins")
    def access_control_allow_origins(
        self,
    ) -> CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOriginsOutputReference:
        return typing.cast(CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOriginsOutputReference, jsii.get(self, "accessControlAllowOrigins"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlExposeHeaders")
    def access_control_expose_headers(
        self,
    ) -> CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeadersOutputReference:
        return typing.cast(CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeadersOutputReference, jsii.get(self, "accessControlExposeHeaders"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowCredentialsInput")
    def access_control_allow_credentials_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "accessControlAllowCredentialsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowHeadersInput")
    def access_control_allow_headers_input(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders], jsii.get(self, "accessControlAllowHeadersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowMethodsInput")
    def access_control_allow_methods_input(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods], jsii.get(self, "accessControlAllowMethodsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowOriginsInput")
    def access_control_allow_origins_input(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins], jsii.get(self, "accessControlAllowOriginsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlExposeHeadersInput")
    def access_control_expose_headers_input(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders], jsii.get(self, "accessControlExposeHeadersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlMaxAgeSecInput")
    def access_control_max_age_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accessControlMaxAgeSecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originOverrideInput")
    def origin_override_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "originOverrideInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowCredentials")
    def access_control_allow_credentials(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "accessControlAllowCredentials"))

    @access_control_allow_credentials.setter
    def access_control_allow_credentials(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "accessControlAllowCredentials", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlMaxAgeSec")
    def access_control_max_age_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessControlMaxAgeSec"))

    @access_control_max_age_sec.setter
    def access_control_max_age_sec(self, value: jsii.Number) -> None:
        jsii.set(self, "accessControlMaxAgeSec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originOverride")
    def origin_override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "originOverride"))

    @origin_override.setter
    def origin_override(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "originOverride", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicyCorsConfig]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicyCorsConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicyCorsConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCustomHeadersConfig",
    jsii_struct_bases=[],
    name_mapping={"items": "items"},
)
class CloudfrontResponseHeadersPolicyCustomHeadersConfig:
    def __init__(
        self,
        *,
        items: typing.Optional[typing.Sequence["CloudfrontResponseHeadersPolicyCustomHeadersConfigItems"]] = None,
    ) -> None:
        '''
        :param items: items block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if items is not None:
            self._values["items"] = items

    @builtins.property
    def items(
        self,
    ) -> typing.Optional[typing.List["CloudfrontResponseHeadersPolicyCustomHeadersConfigItems"]]:
        '''items block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#items CloudfrontResponseHeadersPolicy#items}
        '''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.List["CloudfrontResponseHeadersPolicyCustomHeadersConfigItems"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicyCustomHeadersConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCustomHeadersConfigItems",
    jsii_struct_bases=[],
    name_mapping={"header": "header", "override": "override", "value": "value"},
)
class CloudfrontResponseHeadersPolicyCustomHeadersConfigItems:
    def __init__(
        self,
        *,
        header: builtins.str,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
        value: builtins.str,
    ) -> None:
        '''
        :param header: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#header CloudfrontResponseHeadersPolicy#header}.
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#value CloudfrontResponseHeadersPolicy#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "header": header,
            "override": override,
            "value": value,
        }

    @builtins.property
    def header(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#header CloudfrontResponseHeadersPolicy#header}.'''
        result = self._values.get("header")
        assert result is not None, "Required property 'header' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.'''
        result = self._values.get("override")
        assert result is not None, "Required property 'override' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#value CloudfrontResponseHeadersPolicy#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicyCustomHeadersConfigItems(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicyCustomHeadersConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicyCustomHeadersConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="itemsInput")
    def items_input(
        self,
    ) -> typing.Optional[typing.List[CloudfrontResponseHeadersPolicyCustomHeadersConfigItems]]:
        return typing.cast(typing.Optional[typing.List[CloudfrontResponseHeadersPolicyCustomHeadersConfigItems]], jsii.get(self, "itemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="items")
    def items(
        self,
    ) -> typing.List[CloudfrontResponseHeadersPolicyCustomHeadersConfigItems]:
        return typing.cast(typing.List[CloudfrontResponseHeadersPolicyCustomHeadersConfigItems], jsii.get(self, "items"))

    @items.setter
    def items(
        self,
        value: typing.List[CloudfrontResponseHeadersPolicyCustomHeadersConfigItems],
    ) -> None:
        jsii.set(self, "items", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicyCustomHeadersConfig]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicyCustomHeadersConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicyCustomHeadersConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfig",
    jsii_struct_bases=[],
    name_mapping={
        "content_security_policy": "contentSecurityPolicy",
        "content_type_options": "contentTypeOptions",
        "frame_options": "frameOptions",
        "referrer_policy": "referrerPolicy",
        "strict_transport_security": "strictTransportSecurity",
        "xss_protection": "xssProtection",
    },
)
class CloudfrontResponseHeadersPolicySecurityHeadersConfig:
    def __init__(
        self,
        *,
        content_security_policy: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy"] = None,
        content_type_options: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions"] = None,
        frame_options: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions"] = None,
        referrer_policy: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy"] = None,
        strict_transport_security: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity"] = None,
        xss_protection: typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection"] = None,
    ) -> None:
        '''
        :param content_security_policy: content_security_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#content_security_policy CloudfrontResponseHeadersPolicy#content_security_policy}
        :param content_type_options: content_type_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#content_type_options CloudfrontResponseHeadersPolicy#content_type_options}
        :param frame_options: frame_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#frame_options CloudfrontResponseHeadersPolicy#frame_options}
        :param referrer_policy: referrer_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#referrer_policy CloudfrontResponseHeadersPolicy#referrer_policy}
        :param strict_transport_security: strict_transport_security block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#strict_transport_security CloudfrontResponseHeadersPolicy#strict_transport_security}
        :param xss_protection: xss_protection block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#xss_protection CloudfrontResponseHeadersPolicy#xss_protection}
        '''
        if isinstance(content_security_policy, dict):
            content_security_policy = CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy(**content_security_policy)
        if isinstance(content_type_options, dict):
            content_type_options = CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions(**content_type_options)
        if isinstance(frame_options, dict):
            frame_options = CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions(**frame_options)
        if isinstance(referrer_policy, dict):
            referrer_policy = CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy(**referrer_policy)
        if isinstance(strict_transport_security, dict):
            strict_transport_security = CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity(**strict_transport_security)
        if isinstance(xss_protection, dict):
            xss_protection = CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection(**xss_protection)
        self._values: typing.Dict[str, typing.Any] = {}
        if content_security_policy is not None:
            self._values["content_security_policy"] = content_security_policy
        if content_type_options is not None:
            self._values["content_type_options"] = content_type_options
        if frame_options is not None:
            self._values["frame_options"] = frame_options
        if referrer_policy is not None:
            self._values["referrer_policy"] = referrer_policy
        if strict_transport_security is not None:
            self._values["strict_transport_security"] = strict_transport_security
        if xss_protection is not None:
            self._values["xss_protection"] = xss_protection

    @builtins.property
    def content_security_policy(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy"]:
        '''content_security_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#content_security_policy CloudfrontResponseHeadersPolicy#content_security_policy}
        '''
        result = self._values.get("content_security_policy")
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy"], result)

    @builtins.property
    def content_type_options(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions"]:
        '''content_type_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#content_type_options CloudfrontResponseHeadersPolicy#content_type_options}
        '''
        result = self._values.get("content_type_options")
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions"], result)

    @builtins.property
    def frame_options(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions"]:
        '''frame_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#frame_options CloudfrontResponseHeadersPolicy#frame_options}
        '''
        result = self._values.get("frame_options")
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions"], result)

    @builtins.property
    def referrer_policy(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy"]:
        '''referrer_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#referrer_policy CloudfrontResponseHeadersPolicy#referrer_policy}
        '''
        result = self._values.get("referrer_policy")
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy"], result)

    @builtins.property
    def strict_transport_security(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity"]:
        '''strict_transport_security block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#strict_transport_security CloudfrontResponseHeadersPolicy#strict_transport_security}
        '''
        result = self._values.get("strict_transport_security")
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity"], result)

    @builtins.property
    def xss_protection(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection"]:
        '''xss_protection block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#xss_protection CloudfrontResponseHeadersPolicy#xss_protection}
        '''
        result = self._values.get("xss_protection")
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicySecurityHeadersConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "content_security_policy": "contentSecurityPolicy",
        "override": "override",
    },
)
class CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy:
    def __init__(
        self,
        *,
        content_security_policy: builtins.str,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param content_security_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#content_security_policy CloudfrontResponseHeadersPolicy#content_security_policy}.
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content_security_policy": content_security_policy,
            "override": override,
        }

    @builtins.property
    def content_security_policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#content_security_policy CloudfrontResponseHeadersPolicy#content_security_policy}.'''
        result = self._values.get("content_security_policy")
        assert result is not None, "Required property 'content_security_policy' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.'''
        result = self._values.get("override")
        assert result is not None, "Required property 'override' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicyOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentSecurityPolicyInput")
    def content_security_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentSecurityPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideInput")
    def override_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "overrideInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentSecurityPolicy")
    def content_security_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentSecurityPolicy"))

    @content_security_policy.setter
    def content_security_policy(self, value: builtins.str) -> None:
        jsii.set(self, "contentSecurityPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "override"))

    @override.setter
    def override(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "override", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions",
    jsii_struct_bases=[],
    name_mapping={"override": "override"},
)
class CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions:
    def __init__(
        self,
        *,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "override": override,
        }

    @builtins.property
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.'''
        result = self._values.get("override")
        assert result is not None, "Required property 'override' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideInput")
    def override_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "overrideInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "override"))

    @override.setter
    def override(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "override", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions",
    jsii_struct_bases=[],
    name_mapping={"frame_option": "frameOption", "override": "override"},
)
class CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions:
    def __init__(
        self,
        *,
        frame_option: builtins.str,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param frame_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#frame_option CloudfrontResponseHeadersPolicy#frame_option}.
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "frame_option": frame_option,
            "override": override,
        }

    @builtins.property
    def frame_option(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#frame_option CloudfrontResponseHeadersPolicy#frame_option}.'''
        result = self._values.get("frame_option")
        assert result is not None, "Required property 'frame_option' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.'''
        result = self._values.get("override")
        assert result is not None, "Required property 'override' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frameOptionInput")
    def frame_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frameOptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideInput")
    def override_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "overrideInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frameOption")
    def frame_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frameOption"))

    @frame_option.setter
    def frame_option(self, value: builtins.str) -> None:
        jsii.set(self, "frameOption", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "override"))

    @override.setter
    def override(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "override", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


class CloudfrontResponseHeadersPolicySecurityHeadersConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putContentSecurityPolicy")
    def put_content_security_policy(
        self,
        *,
        content_security_policy: builtins.str,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param content_security_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#content_security_policy CloudfrontResponseHeadersPolicy#content_security_policy}.
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        '''
        value = CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy(
            content_security_policy=content_security_policy, override=override
        )

        return typing.cast(None, jsii.invoke(self, "putContentSecurityPolicy", [value]))

    @jsii.member(jsii_name="putContentTypeOptions")
    def put_content_type_options(
        self,
        *,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        '''
        value = CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions(
            override=override
        )

        return typing.cast(None, jsii.invoke(self, "putContentTypeOptions", [value]))

    @jsii.member(jsii_name="putFrameOptions")
    def put_frame_options(
        self,
        *,
        frame_option: builtins.str,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        '''
        :param frame_option: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#frame_option CloudfrontResponseHeadersPolicy#frame_option}.
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        '''
        value = CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions(
            frame_option=frame_option, override=override
        )

        return typing.cast(None, jsii.invoke(self, "putFrameOptions", [value]))

    @jsii.member(jsii_name="putReferrerPolicy")
    def put_referrer_policy(
        self,
        *,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
        referrer_policy: builtins.str,
    ) -> None:
        '''
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        :param referrer_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#referrer_policy CloudfrontResponseHeadersPolicy#referrer_policy}.
        '''
        value = CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy(
            override=override, referrer_policy=referrer_policy
        )

        return typing.cast(None, jsii.invoke(self, "putReferrerPolicy", [value]))

    @jsii.member(jsii_name="putStrictTransportSecurity")
    def put_strict_transport_security(
        self,
        *,
        access_control_max_age_sec: jsii.Number,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
        include_subdomains: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        preload: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param access_control_max_age_sec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_max_age_sec CloudfrontResponseHeadersPolicy#access_control_max_age_sec}.
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        :param include_subdomains: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#include_subdomains CloudfrontResponseHeadersPolicy#include_subdomains}.
        :param preload: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#preload CloudfrontResponseHeadersPolicy#preload}.
        '''
        value = CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity(
            access_control_max_age_sec=access_control_max_age_sec,
            override=override,
            include_subdomains=include_subdomains,
            preload=preload,
        )

        return typing.cast(None, jsii.invoke(self, "putStrictTransportSecurity", [value]))

    @jsii.member(jsii_name="putXssProtection")
    def put_xss_protection(
        self,
        *,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
        protection: typing.Union[builtins.bool, cdktf.IResolvable],
        mode_block: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        report_uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        :param protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#protection CloudfrontResponseHeadersPolicy#protection}.
        :param mode_block: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#mode_block CloudfrontResponseHeadersPolicy#mode_block}.
        :param report_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#report_uri CloudfrontResponseHeadersPolicy#report_uri}.
        '''
        value = CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection(
            override=override,
            protection=protection,
            mode_block=mode_block,
            report_uri=report_uri,
        )

        return typing.cast(None, jsii.invoke(self, "putXssProtection", [value]))

    @jsii.member(jsii_name="resetContentSecurityPolicy")
    def reset_content_security_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentSecurityPolicy", []))

    @jsii.member(jsii_name="resetContentTypeOptions")
    def reset_content_type_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContentTypeOptions", []))

    @jsii.member(jsii_name="resetFrameOptions")
    def reset_frame_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrameOptions", []))

    @jsii.member(jsii_name="resetReferrerPolicy")
    def reset_referrer_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReferrerPolicy", []))

    @jsii.member(jsii_name="resetStrictTransportSecurity")
    def reset_strict_transport_security(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStrictTransportSecurity", []))

    @jsii.member(jsii_name="resetXssProtection")
    def reset_xss_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetXssProtection", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentSecurityPolicy")
    def content_security_policy(
        self,
    ) -> CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicyOutputReference:
        return typing.cast(CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicyOutputReference, jsii.get(self, "contentSecurityPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeOptions")
    def content_type_options(
        self,
    ) -> CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptionsOutputReference:
        return typing.cast(CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptionsOutputReference, jsii.get(self, "contentTypeOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frameOptions")
    def frame_options(
        self,
    ) -> CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptionsOutputReference:
        return typing.cast(CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptionsOutputReference, jsii.get(self, "frameOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="referrerPolicy")
    def referrer_policy(
        self,
    ) -> "CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicyOutputReference":
        return typing.cast("CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicyOutputReference", jsii.get(self, "referrerPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="strictTransportSecurity")
    def strict_transport_security(
        self,
    ) -> "CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurityOutputReference":
        return typing.cast("CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurityOutputReference", jsii.get(self, "strictTransportSecurity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="xssProtection")
    def xss_protection(
        self,
    ) -> "CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtectionOutputReference":
        return typing.cast("CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtectionOutputReference", jsii.get(self, "xssProtection"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentSecurityPolicyInput")
    def content_security_policy_input(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy], jsii.get(self, "contentSecurityPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeOptionsInput")
    def content_type_options_input(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions], jsii.get(self, "contentTypeOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frameOptionsInput")
    def frame_options_input(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions], jsii.get(self, "frameOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="referrerPolicyInput")
    def referrer_policy_input(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy"]:
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy"], jsii.get(self, "referrerPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="strictTransportSecurityInput")
    def strict_transport_security_input(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity"]:
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity"], jsii.get(self, "strictTransportSecurityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="xssProtectionInput")
    def xss_protection_input(
        self,
    ) -> typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection"]:
        return typing.cast(typing.Optional["CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection"], jsii.get(self, "xssProtectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfig]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy",
    jsii_struct_bases=[],
    name_mapping={"override": "override", "referrer_policy": "referrerPolicy"},
)
class CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy:
    def __init__(
        self,
        *,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
        referrer_policy: builtins.str,
    ) -> None:
        '''
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        :param referrer_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#referrer_policy CloudfrontResponseHeadersPolicy#referrer_policy}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "override": override,
            "referrer_policy": referrer_policy,
        }

    @builtins.property
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.'''
        result = self._values.get("override")
        assert result is not None, "Required property 'override' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def referrer_policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#referrer_policy CloudfrontResponseHeadersPolicy#referrer_policy}.'''
        result = self._values.get("referrer_policy")
        assert result is not None, "Required property 'referrer_policy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicyOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideInput")
    def override_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "overrideInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="referrerPolicyInput")
    def referrer_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "referrerPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "override"))

    @override.setter
    def override(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "override", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="referrerPolicy")
    def referrer_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "referrerPolicy"))

    @referrer_policy.setter
    def referrer_policy(self, value: builtins.str) -> None:
        jsii.set(self, "referrerPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity",
    jsii_struct_bases=[],
    name_mapping={
        "access_control_max_age_sec": "accessControlMaxAgeSec",
        "override": "override",
        "include_subdomains": "includeSubdomains",
        "preload": "preload",
    },
)
class CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity:
    def __init__(
        self,
        *,
        access_control_max_age_sec: jsii.Number,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
        include_subdomains: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        preload: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param access_control_max_age_sec: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_max_age_sec CloudfrontResponseHeadersPolicy#access_control_max_age_sec}.
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        :param include_subdomains: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#include_subdomains CloudfrontResponseHeadersPolicy#include_subdomains}.
        :param preload: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#preload CloudfrontResponseHeadersPolicy#preload}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "access_control_max_age_sec": access_control_max_age_sec,
            "override": override,
        }
        if include_subdomains is not None:
            self._values["include_subdomains"] = include_subdomains
        if preload is not None:
            self._values["preload"] = preload

    @builtins.property
    def access_control_max_age_sec(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#access_control_max_age_sec CloudfrontResponseHeadersPolicy#access_control_max_age_sec}.'''
        result = self._values.get("access_control_max_age_sec")
        assert result is not None, "Required property 'access_control_max_age_sec' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.'''
        result = self._values.get("override")
        assert result is not None, "Required property 'override' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def include_subdomains(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#include_subdomains CloudfrontResponseHeadersPolicy#include_subdomains}.'''
        result = self._values.get("include_subdomains")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def preload(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#preload CloudfrontResponseHeadersPolicy#preload}.'''
        result = self._values.get("preload")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurityOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurityOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetIncludeSubdomains")
    def reset_include_subdomains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeSubdomains", []))

    @jsii.member(jsii_name="resetPreload")
    def reset_preload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreload", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlMaxAgeSecInput")
    def access_control_max_age_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accessControlMaxAgeSecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeSubdomainsInput")
    def include_subdomains_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeSubdomainsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideInput")
    def override_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "overrideInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preloadInput")
    def preload_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "preloadInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlMaxAgeSec")
    def access_control_max_age_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessControlMaxAgeSec"))

    @access_control_max_age_sec.setter
    def access_control_max_age_sec(self, value: jsii.Number) -> None:
        jsii.set(self, "accessControlMaxAgeSec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeSubdomains")
    def include_subdomains(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeSubdomains"))

    @include_subdomains.setter
    def include_subdomains(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeSubdomains", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "override"))

    @override.setter
    def override(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "override", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preload")
    def preload(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "preload"))

    @preload.setter
    def preload(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "preload", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection",
    jsii_struct_bases=[],
    name_mapping={
        "override": "override",
        "protection": "protection",
        "mode_block": "modeBlock",
        "report_uri": "reportUri",
    },
)
class CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection:
    def __init__(
        self,
        *,
        override: typing.Union[builtins.bool, cdktf.IResolvable],
        protection: typing.Union[builtins.bool, cdktf.IResolvable],
        mode_block: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        report_uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param override: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.
        :param protection: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#protection CloudfrontResponseHeadersPolicy#protection}.
        :param mode_block: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#mode_block CloudfrontResponseHeadersPolicy#mode_block}.
        :param report_uri: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#report_uri CloudfrontResponseHeadersPolicy#report_uri}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "override": override,
            "protection": protection,
        }
        if mode_block is not None:
            self._values["mode_block"] = mode_block
        if report_uri is not None:
            self._values["report_uri"] = report_uri

    @builtins.property
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#override CloudfrontResponseHeadersPolicy#override}.'''
        result = self._values.get("override")
        assert result is not None, "Required property 'override' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def protection(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#protection CloudfrontResponseHeadersPolicy#protection}.'''
        result = self._values.get("protection")
        assert result is not None, "Required property 'protection' is missing"
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], result)

    @builtins.property
    def mode_block(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#mode_block CloudfrontResponseHeadersPolicy#mode_block}.'''
        result = self._values.get("mode_block")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def report_uri(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudfront_response_headers_policy#report_uri CloudfrontResponseHeadersPolicy#report_uri}.'''
        result = self._values.get("report_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtectionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtectionOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetModeBlock")
    def reset_mode_block(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModeBlock", []))

    @jsii.member(jsii_name="resetReportUri")
    def reset_report_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReportUri", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeBlockInput")
    def mode_block_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "modeBlockInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideInput")
    def override_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "overrideInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protectionInput")
    def protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "protectionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportUriInput")
    def report_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportUriInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeBlock")
    def mode_block(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "modeBlock"))

    @mode_block.setter
    def mode_block(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "modeBlock", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "override"))

    @override.setter
    def override(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "override", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protection")
    def protection(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "protection"))

    @protection.setter
    def protection(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "protection", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportUri")
    def report_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportUri"))

    @report_uri.setter
    def report_uri(self, value: builtins.str) -> None:
        jsii.set(self, "reportUri", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection]:
        return typing.cast(typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsCloudfrontCachePolicy(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontCachePolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_cache_policy aws_cloudfront_cache_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_cache_policy aws_cloudfront_cache_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_cache_policy#id DataAwsCloudfrontCachePolicy#id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_cache_policy#name DataAwsCloudfrontCachePolicy#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudfrontCachePolicyConfig(
            id=id,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="parametersInCacheKeyAndForwardedToOrigin")
    def parameters_in_cache_key_and_forwarded_to_origin(
        self,
        index: builtins.str,
    ) -> "DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin", jsii.invoke(self, "parametersInCacheKeyAndForwardedToOrigin", [index]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTtl")
    def default_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultTtl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxTtl")
    def max_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTtl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minTtl")
    def min_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minTtl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontCachePolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "id": "id",
        "name": "name",
    },
)
class DataAwsCloudfrontCachePolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_cache_policy#id DataAwsCloudfrontCachePolicy#id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_cache_policy#name DataAwsCloudfrontCachePolicy#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if name is not None:
            self._values["name"] = name

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
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_cache_policy#id DataAwsCloudfrontCachePolicy#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_cache_policy#name DataAwsCloudfrontCachePolicy#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudfrontCachePolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin",
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
    @jsii.member(jsii_name="cookiesConfig")
    def cookies_config(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "cookiesConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAcceptEncodingBrotli")
    def enable_accept_encoding_brotli(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enableAcceptEncodingBrotli"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableAcceptEncodingGzip")
    def enable_accept_encoding_gzip(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enableAcceptEncodingGzip"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headersConfig")
    def headers_config(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "headersConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStringsConfig")
    def query_strings_config(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "queryStringsConfig"))


class DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig",
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
    @jsii.member(jsii_name="cookieBehavior")
    def cookie_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cookieBehavior"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookies")
    def cookies(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "cookies"))


class DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))


class DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig",
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
    @jsii.member(jsii_name="headerBehavior")
    def header_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerBehavior"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "headers"))


class DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))


class DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig",
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
    @jsii.member(jsii_name="queryStringBehavior")
    def query_string_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryStringBehavior"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStrings")
    def query_strings(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "queryStrings"))


class DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))


class DataAwsCloudfrontDistribution(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontDistribution",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_distribution aws_cloudfront_distribution}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_distribution aws_cloudfront_distribution} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_distribution#id DataAwsCloudfrontDistribution#id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_distribution#tags DataAwsCloudfrontDistribution#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudfrontDistributionConfig(
            id=id,
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliases")
    def aliases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "aliases"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostedZoneId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inProgressValidationBatches")
    def in_progress_validation_batches(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "inProgressValidationBatches"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedTime")
    def last_modified_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontDistributionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "id": "id",
        "tags": "tags",
    },
)
class DataAwsCloudfrontDistributionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        id: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_distribution#id DataAwsCloudfrontDistribution#id}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_distribution#tags DataAwsCloudfrontDistribution#tags}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if tags is not None:
            self._values["tags"] = tags

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
    def id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_distribution#id DataAwsCloudfrontDistribution#id}.'''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_distribution#tags DataAwsCloudfrontDistribution#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudfrontDistributionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudfrontFunction(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontFunction",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_function aws_cloudfront_function}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        stage: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_function aws_cloudfront_function} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_function#name DataAwsCloudfrontFunction#name}.
        :param stage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_function#stage DataAwsCloudfrontFunction#stage}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudfrontFunctionConfig(
            name=name,
            stage=stage,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="code")
    def code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "code"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastModifiedTime")
    def last_modified_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastModifiedTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runtime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stageInput")
    def stage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stage")
    def stage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stage"))

    @stage.setter
    def stage(self, value: builtins.str) -> None:
        jsii.set(self, "stage", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontFunctionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "stage": "stage",
    },
)
class DataAwsCloudfrontFunctionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        stage: builtins.str,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_function#name DataAwsCloudfrontFunction#name}.
        :param stage: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_function#stage DataAwsCloudfrontFunction#stage}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "stage": stage,
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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_function#name DataAwsCloudfrontFunction#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stage(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_function#stage DataAwsCloudfrontFunction#stage}.'''
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudfrontFunctionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudfrontLogDeliveryCanonicalUserId(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontLogDeliveryCanonicalUserId",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_log_delivery_canonical_user_id aws_cloudfront_log_delivery_canonical_user_id}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        region: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_log_delivery_canonical_user_id aws_cloudfront_log_delivery_canonical_user_id} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_log_delivery_canonical_user_id#region DataAwsCloudfrontLogDeliveryCanonicalUserId#region}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudfrontLogDeliveryCanonicalUserIdConfig(
            region=region,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

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
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        jsii.set(self, "region", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontLogDeliveryCanonicalUserIdConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "region": "region",
    },
)
class DataAwsCloudfrontLogDeliveryCanonicalUserIdConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_log_delivery_canonical_user_id#region DataAwsCloudfrontLogDeliveryCanonicalUserId#region}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if region is not None:
            self._values["region"] = region

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
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_log_delivery_canonical_user_id#region DataAwsCloudfrontLogDeliveryCanonicalUserId#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudfrontLogDeliveryCanonicalUserIdConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudfrontOriginRequestPolicy(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontOriginRequestPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_origin_request_policy aws_cloudfront_origin_request_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_origin_request_policy aws_cloudfront_origin_request_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_origin_request_policy#id DataAwsCloudfrontOriginRequestPolicy#id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_origin_request_policy#name DataAwsCloudfrontOriginRequestPolicy#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudfrontOriginRequestPolicyConfig(
            id=id,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="cookiesConfig")
    def cookies_config(
        self,
        index: builtins.str,
    ) -> "DataAwsCloudfrontOriginRequestPolicyCookiesConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsCloudfrontOriginRequestPolicyCookiesConfig", jsii.invoke(self, "cookiesConfig", [index]))

    @jsii.member(jsii_name="headersConfig")
    def headers_config(
        self,
        index: builtins.str,
    ) -> "DataAwsCloudfrontOriginRequestPolicyHeadersConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsCloudfrontOriginRequestPolicyHeadersConfig", jsii.invoke(self, "headersConfig", [index]))

    @jsii.member(jsii_name="queryStringsConfig")
    def query_strings_config(
        self,
        index: builtins.str,
    ) -> "DataAwsCloudfrontOriginRequestPolicyQueryStringsConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsCloudfrontOriginRequestPolicyQueryStringsConfig", jsii.invoke(self, "queryStringsConfig", [index]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontOriginRequestPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "id": "id",
        "name": "name",
    },
)
class DataAwsCloudfrontOriginRequestPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_origin_request_policy#id DataAwsCloudfrontOriginRequestPolicy#id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_origin_request_policy#name DataAwsCloudfrontOriginRequestPolicy#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if name is not None:
            self._values["name"] = name

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
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_origin_request_policy#id DataAwsCloudfrontOriginRequestPolicy#id}.'''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_origin_request_policy#name DataAwsCloudfrontOriginRequestPolicy#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudfrontOriginRequestPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudfrontOriginRequestPolicyCookiesConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontOriginRequestPolicyCookiesConfig",
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
    @jsii.member(jsii_name="cookieBehavior")
    def cookie_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cookieBehavior"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookies")
    def cookies(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "cookies"))


class DataAwsCloudfrontOriginRequestPolicyCookiesConfigCookies(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontOriginRequestPolicyCookiesConfigCookies",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))


class DataAwsCloudfrontOriginRequestPolicyHeadersConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontOriginRequestPolicyHeadersConfig",
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
    @jsii.member(jsii_name="headerBehavior")
    def header_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "headerBehavior"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "headers"))


class DataAwsCloudfrontOriginRequestPolicyHeadersConfigHeaders(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontOriginRequestPolicyHeadersConfigHeaders",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))


class DataAwsCloudfrontOriginRequestPolicyQueryStringsConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontOriginRequestPolicyQueryStringsConfig",
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
    @jsii.member(jsii_name="queryStringBehavior")
    def query_string_behavior(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryStringBehavior"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryStrings")
    def query_strings(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "queryStrings"))


class DataAwsCloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))


class DataAwsCloudfrontResponseHeadersPolicy(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_response_headers_policy aws_cloudfront_response_headers_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_response_headers_policy aws_cloudfront_response_headers_policy} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_response_headers_policy#name DataAwsCloudfrontResponseHeadersPolicy#name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudfrontResponseHeadersPolicyConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="corsConfig")
    def cors_config(
        self,
        index: builtins.str,
    ) -> "DataAwsCloudfrontResponseHeadersPolicyCorsConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsCloudfrontResponseHeadersPolicyCorsConfig", jsii.invoke(self, "corsConfig", [index]))

    @jsii.member(jsii_name="customHeadersConfig")
    def custom_headers_config(
        self,
        index: builtins.str,
    ) -> "DataAwsCloudfrontResponseHeadersPolicyCustomHeadersConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsCloudfrontResponseHeadersPolicyCustomHeadersConfig", jsii.invoke(self, "customHeadersConfig", [index]))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="securityHeadersConfig")
    def security_headers_config(
        self,
        index: builtins.str,
    ) -> "DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfig", jsii.invoke(self, "securityHeadersConfig", [index]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="etag")
    def etag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "etag"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataAwsCloudfrontResponseHeadersPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS CloudFront.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_response_headers_policy#name DataAwsCloudfrontResponseHeadersPolicy#name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if name is not None:
            self._values["name"] = name

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
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudfront_response_headers_policy#name DataAwsCloudfrontResponseHeadersPolicy#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudfrontResponseHeadersPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsCloudfrontResponseHeadersPolicyCorsConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicyCorsConfig",
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
    @jsii.member(jsii_name="accessControlAllowCredentials")
    def access_control_allow_credentials(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "accessControlAllowCredentials"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowHeaders")
    def access_control_allow_headers(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "accessControlAllowHeaders"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowMethods")
    def access_control_allow_methods(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "accessControlAllowMethods"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlAllowOrigins")
    def access_control_allow_origins(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "accessControlAllowOrigins"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlExposeHeaders")
    def access_control_expose_headers(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "accessControlExposeHeaders"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessControlMaxAgeSec")
    def access_control_max_age_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessControlMaxAgeSec"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="originOverride")
    def origin_override(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "originOverride"))


class DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))


class DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))


class DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))


class DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "items"))


class DataAwsCloudfrontResponseHeadersPolicyCustomHeadersConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicyCustomHeadersConfig",
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
    @jsii.member(jsii_name="items")
    def items(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "items"))


class DataAwsCloudfrontResponseHeadersPolicyCustomHeadersConfigItems(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicyCustomHeadersConfigItems",
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
    @jsii.member(jsii_name="header")
    def header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "header"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "override"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))


class DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfig",
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
    @jsii.member(jsii_name="contentSecurityPolicy")
    def content_security_policy(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "contentSecurityPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentTypeOptions")
    def content_type_options(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "contentTypeOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frameOptions")
    def frame_options(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "frameOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="referrerPolicy")
    def referrer_policy(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "referrerPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="strictTransportSecurity")
    def strict_transport_security(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "strictTransportSecurity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="xssProtection")
    def xss_protection(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "xssProtection"))


class DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy",
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
    @jsii.member(jsii_name="contentSecurityPolicy")
    def content_security_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "contentSecurityPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "override"))


class DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions",
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
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "override"))


class DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions",
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
    @jsii.member(jsii_name="frameOption")
    def frame_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frameOption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "override"))


class DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy",
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
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "override"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="referrerPolicy")
    def referrer_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "referrerPolicy"))


class DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity",
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
    @jsii.member(jsii_name="accessControlMaxAgeSec")
    def access_control_max_age_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessControlMaxAgeSec"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeSubdomains")
    def include_subdomains(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "includeSubdomains"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "override"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="preload")
    def preload(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "preload"))


class DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.cloudfront.DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection",
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
    @jsii.member(jsii_name="modeBlock")
    def mode_block(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "modeBlock"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="override")
    def override(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "override"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protection")
    def protection(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "protection"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportUri")
    def report_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportUri"))


__all__ = [
    "CloudfrontCachePolicy",
    "CloudfrontCachePolicyConfig",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookiesOutputReference",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigOutputReference",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeadersOutputReference",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigOutputReference",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginOutputReference",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigOutputReference",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings",
    "CloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStringsOutputReference",
    "CloudfrontDistribution",
    "CloudfrontDistributionConfig",
    "CloudfrontDistributionCustomErrorResponse",
    "CloudfrontDistributionDefaultCacheBehavior",
    "CloudfrontDistributionDefaultCacheBehaviorForwardedValues",
    "CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookies",
    "CloudfrontDistributionDefaultCacheBehaviorForwardedValuesCookiesOutputReference",
    "CloudfrontDistributionDefaultCacheBehaviorForwardedValuesOutputReference",
    "CloudfrontDistributionDefaultCacheBehaviorFunctionAssociation",
    "CloudfrontDistributionDefaultCacheBehaviorLambdaFunctionAssociation",
    "CloudfrontDistributionDefaultCacheBehaviorOutputReference",
    "CloudfrontDistributionLoggingConfig",
    "CloudfrontDistributionLoggingConfigOutputReference",
    "CloudfrontDistributionOrderedCacheBehavior",
    "CloudfrontDistributionOrderedCacheBehaviorForwardedValues",
    "CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookies",
    "CloudfrontDistributionOrderedCacheBehaviorForwardedValuesCookiesOutputReference",
    "CloudfrontDistributionOrderedCacheBehaviorForwardedValuesOutputReference",
    "CloudfrontDistributionOrderedCacheBehaviorFunctionAssociation",
    "CloudfrontDistributionOrderedCacheBehaviorLambdaFunctionAssociation",
    "CloudfrontDistributionOrigin",
    "CloudfrontDistributionOriginCustomHeader",
    "CloudfrontDistributionOriginCustomOriginConfig",
    "CloudfrontDistributionOriginCustomOriginConfigOutputReference",
    "CloudfrontDistributionOriginGroup",
    "CloudfrontDistributionOriginGroupFailoverCriteria",
    "CloudfrontDistributionOriginGroupFailoverCriteriaOutputReference",
    "CloudfrontDistributionOriginGroupMember",
    "CloudfrontDistributionOriginOriginShield",
    "CloudfrontDistributionOriginOriginShieldOutputReference",
    "CloudfrontDistributionOriginS3OriginConfig",
    "CloudfrontDistributionOriginS3OriginConfigOutputReference",
    "CloudfrontDistributionRestrictions",
    "CloudfrontDistributionRestrictionsGeoRestriction",
    "CloudfrontDistributionRestrictionsGeoRestrictionOutputReference",
    "CloudfrontDistributionRestrictionsOutputReference",
    "CloudfrontDistributionTrustedKeyGroups",
    "CloudfrontDistributionTrustedKeyGroupsItems",
    "CloudfrontDistributionTrustedSigners",
    "CloudfrontDistributionTrustedSignersItems",
    "CloudfrontDistributionViewerCertificate",
    "CloudfrontDistributionViewerCertificateOutputReference",
    "CloudfrontFieldLevelEncryptionConfig",
    "CloudfrontFieldLevelEncryptionConfigConfig",
    "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfig",
    "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfiles",
    "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesItems",
    "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigContentTypeProfilesOutputReference",
    "CloudfrontFieldLevelEncryptionConfigContentTypeProfileConfigOutputReference",
    "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfig",
    "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigOutputReference",
    "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfiles",
    "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesItems",
    "CloudfrontFieldLevelEncryptionConfigQueryArgProfileConfigQueryArgProfilesOutputReference",
    "CloudfrontFieldLevelEncryptionProfile",
    "CloudfrontFieldLevelEncryptionProfileConfig",
    "CloudfrontFieldLevelEncryptionProfileEncryptionEntities",
    "CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItems",
    "CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatterns",
    "CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesItemsFieldPatternsOutputReference",
    "CloudfrontFieldLevelEncryptionProfileEncryptionEntitiesOutputReference",
    "CloudfrontFunction",
    "CloudfrontFunctionConfig",
    "CloudfrontKeyGroup",
    "CloudfrontKeyGroupConfig",
    "CloudfrontMonitoringSubscription",
    "CloudfrontMonitoringSubscriptionConfig",
    "CloudfrontMonitoringSubscriptionMonitoringSubscription",
    "CloudfrontMonitoringSubscriptionMonitoringSubscriptionOutputReference",
    "CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfig",
    "CloudfrontMonitoringSubscriptionMonitoringSubscriptionRealtimeMetricsSubscriptionConfigOutputReference",
    "CloudfrontOriginAccessIdentity",
    "CloudfrontOriginAccessIdentityConfig",
    "CloudfrontOriginRequestPolicy",
    "CloudfrontOriginRequestPolicyConfig",
    "CloudfrontOriginRequestPolicyCookiesConfig",
    "CloudfrontOriginRequestPolicyCookiesConfigCookies",
    "CloudfrontOriginRequestPolicyCookiesConfigCookiesOutputReference",
    "CloudfrontOriginRequestPolicyCookiesConfigOutputReference",
    "CloudfrontOriginRequestPolicyHeadersConfig",
    "CloudfrontOriginRequestPolicyHeadersConfigHeaders",
    "CloudfrontOriginRequestPolicyHeadersConfigHeadersOutputReference",
    "CloudfrontOriginRequestPolicyHeadersConfigOutputReference",
    "CloudfrontOriginRequestPolicyQueryStringsConfig",
    "CloudfrontOriginRequestPolicyQueryStringsConfigOutputReference",
    "CloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings",
    "CloudfrontOriginRequestPolicyQueryStringsConfigQueryStringsOutputReference",
    "CloudfrontPublicKey",
    "CloudfrontPublicKeyConfig",
    "CloudfrontRealtimeLogConfig",
    "CloudfrontRealtimeLogConfigConfig",
    "CloudfrontRealtimeLogConfigEndpoint",
    "CloudfrontRealtimeLogConfigEndpointKinesisStreamConfig",
    "CloudfrontRealtimeLogConfigEndpointKinesisStreamConfigOutputReference",
    "CloudfrontRealtimeLogConfigEndpointOutputReference",
    "CloudfrontResponseHeadersPolicy",
    "CloudfrontResponseHeadersPolicyConfig",
    "CloudfrontResponseHeadersPolicyCorsConfig",
    "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders",
    "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeadersOutputReference",
    "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods",
    "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethodsOutputReference",
    "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins",
    "CloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOriginsOutputReference",
    "CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders",
    "CloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeadersOutputReference",
    "CloudfrontResponseHeadersPolicyCorsConfigOutputReference",
    "CloudfrontResponseHeadersPolicyCustomHeadersConfig",
    "CloudfrontResponseHeadersPolicyCustomHeadersConfigItems",
    "CloudfrontResponseHeadersPolicyCustomHeadersConfigOutputReference",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfig",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicyOutputReference",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptionsOutputReference",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptionsOutputReference",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigOutputReference",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicyOutputReference",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurityOutputReference",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection",
    "CloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtectionOutputReference",
    "DataAwsCloudfrontCachePolicy",
    "DataAwsCloudfrontCachePolicyConfig",
    "DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOrigin",
    "DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfig",
    "DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginCookiesConfigCookies",
    "DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfig",
    "DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginHeadersConfigHeaders",
    "DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfig",
    "DataAwsCloudfrontCachePolicyParametersInCacheKeyAndForwardedToOriginQueryStringsConfigQueryStrings",
    "DataAwsCloudfrontDistribution",
    "DataAwsCloudfrontDistributionConfig",
    "DataAwsCloudfrontFunction",
    "DataAwsCloudfrontFunctionConfig",
    "DataAwsCloudfrontLogDeliveryCanonicalUserId",
    "DataAwsCloudfrontLogDeliveryCanonicalUserIdConfig",
    "DataAwsCloudfrontOriginRequestPolicy",
    "DataAwsCloudfrontOriginRequestPolicyConfig",
    "DataAwsCloudfrontOriginRequestPolicyCookiesConfig",
    "DataAwsCloudfrontOriginRequestPolicyCookiesConfigCookies",
    "DataAwsCloudfrontOriginRequestPolicyHeadersConfig",
    "DataAwsCloudfrontOriginRequestPolicyHeadersConfigHeaders",
    "DataAwsCloudfrontOriginRequestPolicyQueryStringsConfig",
    "DataAwsCloudfrontOriginRequestPolicyQueryStringsConfigQueryStrings",
    "DataAwsCloudfrontResponseHeadersPolicy",
    "DataAwsCloudfrontResponseHeadersPolicyConfig",
    "DataAwsCloudfrontResponseHeadersPolicyCorsConfig",
    "DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowHeaders",
    "DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowMethods",
    "DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlAllowOrigins",
    "DataAwsCloudfrontResponseHeadersPolicyCorsConfigAccessControlExposeHeaders",
    "DataAwsCloudfrontResponseHeadersPolicyCustomHeadersConfig",
    "DataAwsCloudfrontResponseHeadersPolicyCustomHeadersConfigItems",
    "DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfig",
    "DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigContentSecurityPolicy",
    "DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigContentTypeOptions",
    "DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigFrameOptions",
    "DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigReferrerPolicy",
    "DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigStrictTransportSecurity",
    "DataAwsCloudfrontResponseHeadersPolicySecurityHeadersConfigXssProtection",
]

publication.publish()
