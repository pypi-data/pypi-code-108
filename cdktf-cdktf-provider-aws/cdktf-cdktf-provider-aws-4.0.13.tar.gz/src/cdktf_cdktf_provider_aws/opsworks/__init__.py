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


class OpsworksApplication(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksApplication",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application aws_opsworks_application}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        stack_id: builtins.str,
        type: builtins.str,
        app_source: typing.Optional[typing.Sequence["OpsworksApplicationAppSource"]] = None,
        auto_bundle_on_deploy: typing.Optional[builtins.str] = None,
        aws_flow_ruby_settings: typing.Optional[builtins.str] = None,
        data_source_arn: typing.Optional[builtins.str] = None,
        data_source_database_name: typing.Optional[builtins.str] = None,
        data_source_type: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        document_root: typing.Optional[builtins.str] = None,
        domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        enable_ssl: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        environment: typing.Optional[typing.Sequence["OpsworksApplicationEnvironment"]] = None,
        rails_env: typing.Optional[builtins.str] = None,
        short_name: typing.Optional[builtins.str] = None,
        ssl_configuration: typing.Optional[typing.Sequence["OpsworksApplicationSslConfiguration"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application aws_opsworks_application} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#name OpsworksApplication#name}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#stack_id OpsworksApplication#stack_id}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#type OpsworksApplication#type}.
        :param app_source: app_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#app_source OpsworksApplication#app_source}
        :param auto_bundle_on_deploy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#auto_bundle_on_deploy OpsworksApplication#auto_bundle_on_deploy}.
        :param aws_flow_ruby_settings: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#aws_flow_ruby_settings OpsworksApplication#aws_flow_ruby_settings}.
        :param data_source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#data_source_arn OpsworksApplication#data_source_arn}.
        :param data_source_database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#data_source_database_name OpsworksApplication#data_source_database_name}.
        :param data_source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#data_source_type OpsworksApplication#data_source_type}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#description OpsworksApplication#description}.
        :param document_root: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#document_root OpsworksApplication#document_root}.
        :param domains: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#domains OpsworksApplication#domains}.
        :param enable_ssl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#enable_ssl OpsworksApplication#enable_ssl}.
        :param environment: environment block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#environment OpsworksApplication#environment}
        :param rails_env: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#rails_env OpsworksApplication#rails_env}.
        :param short_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#short_name OpsworksApplication#short_name}.
        :param ssl_configuration: ssl_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#ssl_configuration OpsworksApplication#ssl_configuration}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksApplicationConfig(
            name=name,
            stack_id=stack_id,
            type=type,
            app_source=app_source,
            auto_bundle_on_deploy=auto_bundle_on_deploy,
            aws_flow_ruby_settings=aws_flow_ruby_settings,
            data_source_arn=data_source_arn,
            data_source_database_name=data_source_database_name,
            data_source_type=data_source_type,
            description=description,
            document_root=document_root,
            domains=domains,
            enable_ssl=enable_ssl,
            environment=environment,
            rails_env=rails_env,
            short_name=short_name,
            ssl_configuration=ssl_configuration,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAppSource")
    def reset_app_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppSource", []))

    @jsii.member(jsii_name="resetAutoBundleOnDeploy")
    def reset_auto_bundle_on_deploy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoBundleOnDeploy", []))

    @jsii.member(jsii_name="resetAwsFlowRubySettings")
    def reset_aws_flow_ruby_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsFlowRubySettings", []))

    @jsii.member(jsii_name="resetDataSourceArn")
    def reset_data_source_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSourceArn", []))

    @jsii.member(jsii_name="resetDataSourceDatabaseName")
    def reset_data_source_database_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSourceDatabaseName", []))

    @jsii.member(jsii_name="resetDataSourceType")
    def reset_data_source_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSourceType", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDocumentRoot")
    def reset_document_root(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDocumentRoot", []))

    @jsii.member(jsii_name="resetDomains")
    def reset_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomains", []))

    @jsii.member(jsii_name="resetEnableSsl")
    def reset_enable_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableSsl", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetRailsEnv")
    def reset_rails_env(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRailsEnv", []))

    @jsii.member(jsii_name="resetShortName")
    def reset_short_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShortName", []))

    @jsii.member(jsii_name="resetSslConfiguration")
    def reset_ssl_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSslConfiguration", []))

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
    @jsii.member(jsii_name="appSourceInput")
    def app_source_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksApplicationAppSource"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksApplicationAppSource"]], jsii.get(self, "appSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoBundleOnDeployInput")
    def auto_bundle_on_deploy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoBundleOnDeployInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsFlowRubySettingsInput")
    def aws_flow_ruby_settings_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsFlowRubySettingsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSourceArnInput")
    def data_source_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSourceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSourceDatabaseNameInput")
    def data_source_database_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSourceDatabaseNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSourceTypeInput")
    def data_source_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataSourceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="documentRootInput")
    def document_root_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "documentRootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainsInput")
    def domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "domainsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableSslInput")
    def enable_ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enableSslInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentInput")
    def environment_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksApplicationEnvironment"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksApplicationEnvironment"]], jsii.get(self, "environmentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="railsEnvInput")
    def rails_env_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "railsEnvInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shortNameInput")
    def short_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "shortNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslConfigurationInput")
    def ssl_configuration_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksApplicationSslConfiguration"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksApplicationSslConfiguration"]], jsii.get(self, "sslConfigurationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appSource")
    def app_source(self) -> typing.List["OpsworksApplicationAppSource"]:
        return typing.cast(typing.List["OpsworksApplicationAppSource"], jsii.get(self, "appSource"))

    @app_source.setter
    def app_source(self, value: typing.List["OpsworksApplicationAppSource"]) -> None:
        jsii.set(self, "appSource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoBundleOnDeploy")
    def auto_bundle_on_deploy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoBundleOnDeploy"))

    @auto_bundle_on_deploy.setter
    def auto_bundle_on_deploy(self, value: builtins.str) -> None:
        jsii.set(self, "autoBundleOnDeploy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsFlowRubySettings")
    def aws_flow_ruby_settings(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsFlowRubySettings"))

    @aws_flow_ruby_settings.setter
    def aws_flow_ruby_settings(self, value: builtins.str) -> None:
        jsii.set(self, "awsFlowRubySettings", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSourceArn")
    def data_source_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSourceArn"))

    @data_source_arn.setter
    def data_source_arn(self, value: builtins.str) -> None:
        jsii.set(self, "dataSourceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSourceDatabaseName")
    def data_source_database_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSourceDatabaseName"))

    @data_source_database_name.setter
    def data_source_database_name(self, value: builtins.str) -> None:
        jsii.set(self, "dataSourceDatabaseName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSourceType")
    def data_source_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataSourceType"))

    @data_source_type.setter
    def data_source_type(self, value: builtins.str) -> None:
        jsii.set(self, "dataSourceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="documentRoot")
    def document_root(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "documentRoot"))

    @document_root.setter
    def document_root(self, value: builtins.str) -> None:
        jsii.set(self, "documentRoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domains")
    def domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domains"))

    @domains.setter
    def domains(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "domains", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableSsl")
    def enable_ssl(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enableSsl"))

    @enable_ssl.setter
    def enable_ssl(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enableSsl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environment")
    def environment(self) -> typing.List["OpsworksApplicationEnvironment"]:
        return typing.cast(typing.List["OpsworksApplicationEnvironment"], jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: typing.List["OpsworksApplicationEnvironment"]) -> None:
        jsii.set(self, "environment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="railsEnv")
    def rails_env(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "railsEnv"))

    @rails_env.setter
    def rails_env(self, value: builtins.str) -> None:
        jsii.set(self, "railsEnv", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shortName")
    def short_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shortName"))

    @short_name.setter
    def short_name(self, value: builtins.str) -> None:
        jsii.set(self, "shortName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sslConfiguration")
    def ssl_configuration(self) -> typing.List["OpsworksApplicationSslConfiguration"]:
        return typing.cast(typing.List["OpsworksApplicationSslConfiguration"], jsii.get(self, "sslConfiguration"))

    @ssl_configuration.setter
    def ssl_configuration(
        self,
        value: typing.List["OpsworksApplicationSslConfiguration"],
    ) -> None:
        jsii.set(self, "sslConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksApplicationAppSource",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "password": "password",
        "revision": "revision",
        "ssh_key": "sshKey",
        "url": "url",
        "username": "username",
    },
)
class OpsworksApplicationAppSource:
    def __init__(
        self,
        *,
        type: builtins.str,
        password: typing.Optional[builtins.str] = None,
        revision: typing.Optional[builtins.str] = None,
        ssh_key: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#type OpsworksApplication#type}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#password OpsworksApplication#password}.
        :param revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#revision OpsworksApplication#revision}.
        :param ssh_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#ssh_key OpsworksApplication#ssh_key}.
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#url OpsworksApplication#url}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#username OpsworksApplication#username}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if password is not None:
            self._values["password"] = password
        if revision is not None:
            self._values["revision"] = revision
        if ssh_key is not None:
            self._values["ssh_key"] = ssh_key
        if url is not None:
            self._values["url"] = url
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#type OpsworksApplication#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#password OpsworksApplication#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def revision(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#revision OpsworksApplication#revision}.'''
        result = self._values.get("revision")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#ssh_key OpsworksApplication#ssh_key}.'''
        result = self._values.get("ssh_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#url OpsworksApplication#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#username OpsworksApplication#username}.'''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksApplicationAppSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksApplicationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "stack_id": "stackId",
        "type": "type",
        "app_source": "appSource",
        "auto_bundle_on_deploy": "autoBundleOnDeploy",
        "aws_flow_ruby_settings": "awsFlowRubySettings",
        "data_source_arn": "dataSourceArn",
        "data_source_database_name": "dataSourceDatabaseName",
        "data_source_type": "dataSourceType",
        "description": "description",
        "document_root": "documentRoot",
        "domains": "domains",
        "enable_ssl": "enableSsl",
        "environment": "environment",
        "rails_env": "railsEnv",
        "short_name": "shortName",
        "ssl_configuration": "sslConfiguration",
    },
)
class OpsworksApplicationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        stack_id: builtins.str,
        type: builtins.str,
        app_source: typing.Optional[typing.Sequence[OpsworksApplicationAppSource]] = None,
        auto_bundle_on_deploy: typing.Optional[builtins.str] = None,
        aws_flow_ruby_settings: typing.Optional[builtins.str] = None,
        data_source_arn: typing.Optional[builtins.str] = None,
        data_source_database_name: typing.Optional[builtins.str] = None,
        data_source_type: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        document_root: typing.Optional[builtins.str] = None,
        domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        enable_ssl: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        environment: typing.Optional[typing.Sequence["OpsworksApplicationEnvironment"]] = None,
        rails_env: typing.Optional[builtins.str] = None,
        short_name: typing.Optional[builtins.str] = None,
        ssl_configuration: typing.Optional[typing.Sequence["OpsworksApplicationSslConfiguration"]] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#name OpsworksApplication#name}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#stack_id OpsworksApplication#stack_id}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#type OpsworksApplication#type}.
        :param app_source: app_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#app_source OpsworksApplication#app_source}
        :param auto_bundle_on_deploy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#auto_bundle_on_deploy OpsworksApplication#auto_bundle_on_deploy}.
        :param aws_flow_ruby_settings: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#aws_flow_ruby_settings OpsworksApplication#aws_flow_ruby_settings}.
        :param data_source_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#data_source_arn OpsworksApplication#data_source_arn}.
        :param data_source_database_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#data_source_database_name OpsworksApplication#data_source_database_name}.
        :param data_source_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#data_source_type OpsworksApplication#data_source_type}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#description OpsworksApplication#description}.
        :param document_root: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#document_root OpsworksApplication#document_root}.
        :param domains: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#domains OpsworksApplication#domains}.
        :param enable_ssl: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#enable_ssl OpsworksApplication#enable_ssl}.
        :param environment: environment block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#environment OpsworksApplication#environment}
        :param rails_env: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#rails_env OpsworksApplication#rails_env}.
        :param short_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#short_name OpsworksApplication#short_name}.
        :param ssl_configuration: ssl_configuration block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#ssl_configuration OpsworksApplication#ssl_configuration}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "stack_id": stack_id,
            "type": type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if app_source is not None:
            self._values["app_source"] = app_source
        if auto_bundle_on_deploy is not None:
            self._values["auto_bundle_on_deploy"] = auto_bundle_on_deploy
        if aws_flow_ruby_settings is not None:
            self._values["aws_flow_ruby_settings"] = aws_flow_ruby_settings
        if data_source_arn is not None:
            self._values["data_source_arn"] = data_source_arn
        if data_source_database_name is not None:
            self._values["data_source_database_name"] = data_source_database_name
        if data_source_type is not None:
            self._values["data_source_type"] = data_source_type
        if description is not None:
            self._values["description"] = description
        if document_root is not None:
            self._values["document_root"] = document_root
        if domains is not None:
            self._values["domains"] = domains
        if enable_ssl is not None:
            self._values["enable_ssl"] = enable_ssl
        if environment is not None:
            self._values["environment"] = environment
        if rails_env is not None:
            self._values["rails_env"] = rails_env
        if short_name is not None:
            self._values["short_name"] = short_name
        if ssl_configuration is not None:
            self._values["ssl_configuration"] = ssl_configuration

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#name OpsworksApplication#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#stack_id OpsworksApplication#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#type OpsworksApplication#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_source(self) -> typing.Optional[typing.List[OpsworksApplicationAppSource]]:
        '''app_source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#app_source OpsworksApplication#app_source}
        '''
        result = self._values.get("app_source")
        return typing.cast(typing.Optional[typing.List[OpsworksApplicationAppSource]], result)

    @builtins.property
    def auto_bundle_on_deploy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#auto_bundle_on_deploy OpsworksApplication#auto_bundle_on_deploy}.'''
        result = self._values.get("auto_bundle_on_deploy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_flow_ruby_settings(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#aws_flow_ruby_settings OpsworksApplication#aws_flow_ruby_settings}.'''
        result = self._values.get("aws_flow_ruby_settings")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_source_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#data_source_arn OpsworksApplication#data_source_arn}.'''
        result = self._values.get("data_source_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_source_database_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#data_source_database_name OpsworksApplication#data_source_database_name}.'''
        result = self._values.get("data_source_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_source_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#data_source_type OpsworksApplication#data_source_type}.'''
        result = self._values.get("data_source_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#description OpsworksApplication#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def document_root(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#document_root OpsworksApplication#document_root}.'''
        result = self._values.get("document_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#domains OpsworksApplication#domains}.'''
        result = self._values.get("domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enable_ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#enable_ssl OpsworksApplication#enable_ssl}.'''
        result = self._values.get("enable_ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.List["OpsworksApplicationEnvironment"]]:
        '''environment block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#environment OpsworksApplication#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.List["OpsworksApplicationEnvironment"]], result)

    @builtins.property
    def rails_env(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#rails_env OpsworksApplication#rails_env}.'''
        result = self._values.get("rails_env")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def short_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#short_name OpsworksApplication#short_name}.'''
        result = self._values.get("short_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssl_configuration(
        self,
    ) -> typing.Optional[typing.List["OpsworksApplicationSslConfiguration"]]:
        '''ssl_configuration block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#ssl_configuration OpsworksApplication#ssl_configuration}
        '''
        result = self._values.get("ssl_configuration")
        return typing.cast(typing.Optional[typing.List["OpsworksApplicationSslConfiguration"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksApplicationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksApplicationEnvironment",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value", "secure": "secure"},
)
class OpsworksApplicationEnvironment:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: builtins.str,
        secure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#key OpsworksApplication#key}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#value OpsworksApplication#value}.
        :param secure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#secure OpsworksApplication#secure}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }
        if secure is not None:
            self._values["secure"] = secure

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#key OpsworksApplication#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#value OpsworksApplication#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secure(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#secure OpsworksApplication#secure}.'''
        result = self._values.get("secure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksApplicationEnvironment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksApplicationSslConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "certificate": "certificate",
        "private_key": "privateKey",
        "chain": "chain",
    },
)
class OpsworksApplicationSslConfiguration:
    def __init__(
        self,
        *,
        certificate: builtins.str,
        private_key: builtins.str,
        chain: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param certificate: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#certificate OpsworksApplication#certificate}.
        :param private_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#private_key OpsworksApplication#private_key}.
        :param chain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#chain OpsworksApplication#chain}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "certificate": certificate,
            "private_key": private_key,
        }
        if chain is not None:
            self._values["chain"] = chain

    @builtins.property
    def certificate(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#certificate OpsworksApplication#certificate}.'''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#private_key OpsworksApplication#private_key}.'''
        result = self._values.get("private_key")
        assert result is not None, "Required property 'private_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def chain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_application#chain OpsworksApplication#chain}.'''
        result = self._values.get("chain")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksApplicationSslConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksCustomLayer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksCustomLayer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer aws_opsworks_custom_layer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        short_name: builtins.str,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksCustomLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer aws_opsworks_custom_layer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#name OpsworksCustomLayer#name}.
        :param short_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#short_name OpsworksCustomLayer#short_name}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#stack_id OpsworksCustomLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#auto_assign_elastic_ips OpsworksCustomLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#auto_assign_public_ips OpsworksCustomLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#auto_healing OpsworksCustomLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_configure_recipes OpsworksCustomLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_deploy_recipes OpsworksCustomLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_instance_profile_arn OpsworksCustomLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_json OpsworksCustomLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_security_group_ids OpsworksCustomLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_setup_recipes OpsworksCustomLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_shutdown_recipes OpsworksCustomLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_undeploy_recipes OpsworksCustomLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#drain_elb_on_shutdown OpsworksCustomLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#ebs_volume OpsworksCustomLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#elastic_load_balancer OpsworksCustomLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#install_updates_on_boot OpsworksCustomLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#instance_shutdown_timeout OpsworksCustomLayer#instance_shutdown_timeout}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#system_packages OpsworksCustomLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#tags OpsworksCustomLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#tags_all OpsworksCustomLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#use_ebs_optimized_instances OpsworksCustomLayer#use_ebs_optimized_instances}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksCustomLayerConfig(
            name=name,
            short_name=short_name,
            stack_id=stack_id,
            auto_assign_elastic_ips=auto_assign_elastic_ips,
            auto_assign_public_ips=auto_assign_public_ips,
            auto_healing=auto_healing,
            custom_configure_recipes=custom_configure_recipes,
            custom_deploy_recipes=custom_deploy_recipes,
            custom_instance_profile_arn=custom_instance_profile_arn,
            custom_json=custom_json,
            custom_security_group_ids=custom_security_group_ids,
            custom_setup_recipes=custom_setup_recipes,
            custom_shutdown_recipes=custom_shutdown_recipes,
            custom_undeploy_recipes=custom_undeploy_recipes,
            drain_elb_on_shutdown=drain_elb_on_shutdown,
            ebs_volume=ebs_volume,
            elastic_load_balancer=elastic_load_balancer,
            install_updates_on_boot=install_updates_on_boot,
            instance_shutdown_timeout=instance_shutdown_timeout,
            system_packages=system_packages,
            tags=tags,
            tags_all=tags_all,
            use_ebs_optimized_instances=use_ebs_optimized_instances,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAutoAssignElasticIps")
    def reset_auto_assign_elastic_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignElasticIps", []))

    @jsii.member(jsii_name="resetAutoAssignPublicIps")
    def reset_auto_assign_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignPublicIps", []))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetCustomConfigureRecipes")
    def reset_custom_configure_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomConfigureRecipes", []))

    @jsii.member(jsii_name="resetCustomDeployRecipes")
    def reset_custom_deploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDeployRecipes", []))

    @jsii.member(jsii_name="resetCustomInstanceProfileArn")
    def reset_custom_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomInstanceProfileArn", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetCustomSecurityGroupIds")
    def reset_custom_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupIds", []))

    @jsii.member(jsii_name="resetCustomSetupRecipes")
    def reset_custom_setup_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSetupRecipes", []))

    @jsii.member(jsii_name="resetCustomShutdownRecipes")
    def reset_custom_shutdown_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomShutdownRecipes", []))

    @jsii.member(jsii_name="resetCustomUndeployRecipes")
    def reset_custom_undeploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUndeployRecipes", []))

    @jsii.member(jsii_name="resetDrainElbOnShutdown")
    def reset_drain_elb_on_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainElbOnShutdown", []))

    @jsii.member(jsii_name="resetEbsVolume")
    def reset_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolume", []))

    @jsii.member(jsii_name="resetElasticLoadBalancer")
    def reset_elastic_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticLoadBalancer", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceShutdownTimeout")
    def reset_instance_shutdown_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceShutdownTimeout", []))

    @jsii.member(jsii_name="resetSystemPackages")
    def reset_system_packages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemPackages", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUseEbsOptimizedInstances")
    def reset_use_ebs_optimized_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseEbsOptimizedInstances", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIpsInput")
    def auto_assign_elastic_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignElasticIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIpsInput")
    def auto_assign_public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignPublicIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipesInput")
    def custom_configure_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customConfigureRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipesInput")
    def custom_deploy_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customDeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArnInput")
    def custom_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdsInput")
    def custom_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipesInput")
    def custom_setup_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSetupRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipesInput")
    def custom_shutdown_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customShutdownRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipesInput")
    def custom_undeploy_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customUndeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdownInput")
    def drain_elb_on_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "drainElbOnShutdownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeInput")
    def ebs_volume_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksCustomLayerEbsVolume"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksCustomLayerEbsVolume"]], jsii.get(self, "ebsVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancerInput")
    def elastic_load_balancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticLoadBalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeoutInput")
    def instance_shutdown_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceShutdownTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shortNameInput")
    def short_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "shortNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackagesInput")
    def system_packages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "systemPackagesInput"))

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
    @jsii.member(jsii_name="useEbsOptimizedInstancesInput")
    def use_ebs_optimized_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useEbsOptimizedInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIps")
    def auto_assign_elastic_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignElasticIps"))

    @auto_assign_elastic_ips.setter
    def auto_assign_elastic_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignElasticIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIps")
    def auto_assign_public_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignPublicIps"))

    @auto_assign_public_ips.setter
    def auto_assign_public_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignPublicIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoHealing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipes")
    def custom_configure_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customConfigureRecipes"))

    @custom_configure_recipes.setter
    def custom_configure_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customConfigureRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipes")
    def custom_deploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDeployRecipes"))

    @custom_deploy_recipes.setter
    def custom_deploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customDeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArn")
    def custom_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customInstanceProfileArn"))

    @custom_instance_profile_arn.setter
    def custom_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "customInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIds")
    def custom_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSecurityGroupIds"))

    @custom_security_group_ids.setter
    def custom_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipes")
    def custom_setup_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSetupRecipes"))

    @custom_setup_recipes.setter
    def custom_setup_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSetupRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipes")
    def custom_shutdown_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customShutdownRecipes"))

    @custom_shutdown_recipes.setter
    def custom_shutdown_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customShutdownRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipes")
    def custom_undeploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customUndeployRecipes"))

    @custom_undeploy_recipes.setter
    def custom_undeploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customUndeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdown")
    def drain_elb_on_shutdown(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "drainElbOnShutdown"))

    @drain_elb_on_shutdown.setter
    def drain_elb_on_shutdown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "drainElbOnShutdown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolume")
    def ebs_volume(self) -> typing.List["OpsworksCustomLayerEbsVolume"]:
        return typing.cast(typing.List["OpsworksCustomLayerEbsVolume"], jsii.get(self, "ebsVolume"))

    @ebs_volume.setter
    def ebs_volume(self, value: typing.List["OpsworksCustomLayerEbsVolume"]) -> None:
        jsii.set(self, "ebsVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancer")
    def elastic_load_balancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticLoadBalancer"))

    @elastic_load_balancer.setter
    def elastic_load_balancer(self, value: builtins.str) -> None:
        jsii.set(self, "elasticLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeout")
    def instance_shutdown_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceShutdownTimeout"))

    @instance_shutdown_timeout.setter
    def instance_shutdown_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceShutdownTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shortName")
    def short_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "shortName"))

    @short_name.setter
    def short_name(self, value: builtins.str) -> None:
        jsii.set(self, "shortName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackages")
    def system_packages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "systemPackages"))

    @system_packages.setter
    def system_packages(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "systemPackages", value)

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
    @jsii.member(jsii_name="useEbsOptimizedInstances")
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useEbsOptimizedInstances"))

    @use_ebs_optimized_instances.setter
    def use_ebs_optimized_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useEbsOptimizedInstances", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksCustomLayerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "short_name": "shortName",
        "stack_id": "stackId",
        "auto_assign_elastic_ips": "autoAssignElasticIps",
        "auto_assign_public_ips": "autoAssignPublicIps",
        "auto_healing": "autoHealing",
        "custom_configure_recipes": "customConfigureRecipes",
        "custom_deploy_recipes": "customDeployRecipes",
        "custom_instance_profile_arn": "customInstanceProfileArn",
        "custom_json": "customJson",
        "custom_security_group_ids": "customSecurityGroupIds",
        "custom_setup_recipes": "customSetupRecipes",
        "custom_shutdown_recipes": "customShutdownRecipes",
        "custom_undeploy_recipes": "customUndeployRecipes",
        "drain_elb_on_shutdown": "drainElbOnShutdown",
        "ebs_volume": "ebsVolume",
        "elastic_load_balancer": "elasticLoadBalancer",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_shutdown_timeout": "instanceShutdownTimeout",
        "system_packages": "systemPackages",
        "tags": "tags",
        "tags_all": "tagsAll",
        "use_ebs_optimized_instances": "useEbsOptimizedInstances",
    },
)
class OpsworksCustomLayerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        short_name: builtins.str,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksCustomLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#name OpsworksCustomLayer#name}.
        :param short_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#short_name OpsworksCustomLayer#short_name}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#stack_id OpsworksCustomLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#auto_assign_elastic_ips OpsworksCustomLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#auto_assign_public_ips OpsworksCustomLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#auto_healing OpsworksCustomLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_configure_recipes OpsworksCustomLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_deploy_recipes OpsworksCustomLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_instance_profile_arn OpsworksCustomLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_json OpsworksCustomLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_security_group_ids OpsworksCustomLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_setup_recipes OpsworksCustomLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_shutdown_recipes OpsworksCustomLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_undeploy_recipes OpsworksCustomLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#drain_elb_on_shutdown OpsworksCustomLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#ebs_volume OpsworksCustomLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#elastic_load_balancer OpsworksCustomLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#install_updates_on_boot OpsworksCustomLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#instance_shutdown_timeout OpsworksCustomLayer#instance_shutdown_timeout}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#system_packages OpsworksCustomLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#tags OpsworksCustomLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#tags_all OpsworksCustomLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#use_ebs_optimized_instances OpsworksCustomLayer#use_ebs_optimized_instances}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "short_name": short_name,
            "stack_id": stack_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auto_assign_elastic_ips is not None:
            self._values["auto_assign_elastic_ips"] = auto_assign_elastic_ips
        if auto_assign_public_ips is not None:
            self._values["auto_assign_public_ips"] = auto_assign_public_ips
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if custom_configure_recipes is not None:
            self._values["custom_configure_recipes"] = custom_configure_recipes
        if custom_deploy_recipes is not None:
            self._values["custom_deploy_recipes"] = custom_deploy_recipes
        if custom_instance_profile_arn is not None:
            self._values["custom_instance_profile_arn"] = custom_instance_profile_arn
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if custom_security_group_ids is not None:
            self._values["custom_security_group_ids"] = custom_security_group_ids
        if custom_setup_recipes is not None:
            self._values["custom_setup_recipes"] = custom_setup_recipes
        if custom_shutdown_recipes is not None:
            self._values["custom_shutdown_recipes"] = custom_shutdown_recipes
        if custom_undeploy_recipes is not None:
            self._values["custom_undeploy_recipes"] = custom_undeploy_recipes
        if drain_elb_on_shutdown is not None:
            self._values["drain_elb_on_shutdown"] = drain_elb_on_shutdown
        if ebs_volume is not None:
            self._values["ebs_volume"] = ebs_volume
        if elastic_load_balancer is not None:
            self._values["elastic_load_balancer"] = elastic_load_balancer
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_shutdown_timeout is not None:
            self._values["instance_shutdown_timeout"] = instance_shutdown_timeout
        if system_packages is not None:
            self._values["system_packages"] = system_packages
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if use_ebs_optimized_instances is not None:
            self._values["use_ebs_optimized_instances"] = use_ebs_optimized_instances

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#name OpsworksCustomLayer#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def short_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#short_name OpsworksCustomLayer#short_name}.'''
        result = self._values.get("short_name")
        assert result is not None, "Required property 'short_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#stack_id OpsworksCustomLayer#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_assign_elastic_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#auto_assign_elastic_ips OpsworksCustomLayer#auto_assign_elastic_ips}.'''
        result = self._values.get("auto_assign_elastic_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_assign_public_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#auto_assign_public_ips OpsworksCustomLayer#auto_assign_public_ips}.'''
        result = self._values.get("auto_assign_public_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#auto_healing OpsworksCustomLayer#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def custom_configure_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_configure_recipes OpsworksCustomLayer#custom_configure_recipes}.'''
        result = self._values.get("custom_configure_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_deploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_deploy_recipes OpsworksCustomLayer#custom_deploy_recipes}.'''
        result = self._values.get("custom_deploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_instance_profile_arn OpsworksCustomLayer#custom_instance_profile_arn}.'''
        result = self._values.get("custom_instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_json OpsworksCustomLayer#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_security_group_ids OpsworksCustomLayer#custom_security_group_ids}.'''
        result = self._values.get("custom_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_setup_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_setup_recipes OpsworksCustomLayer#custom_setup_recipes}.'''
        result = self._values.get("custom_setup_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_shutdown_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_shutdown_recipes OpsworksCustomLayer#custom_shutdown_recipes}.'''
        result = self._values.get("custom_shutdown_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_undeploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#custom_undeploy_recipes OpsworksCustomLayer#custom_undeploy_recipes}.'''
        result = self._values.get("custom_undeploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drain_elb_on_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#drain_elb_on_shutdown OpsworksCustomLayer#drain_elb_on_shutdown}.'''
        result = self._values.get("drain_elb_on_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_volume(
        self,
    ) -> typing.Optional[typing.List["OpsworksCustomLayerEbsVolume"]]:
        '''ebs_volume block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#ebs_volume OpsworksCustomLayer#ebs_volume}
        '''
        result = self._values.get("ebs_volume")
        return typing.cast(typing.Optional[typing.List["OpsworksCustomLayerEbsVolume"]], result)

    @builtins.property
    def elastic_load_balancer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#elastic_load_balancer OpsworksCustomLayer#elastic_load_balancer}.'''
        result = self._values.get("elastic_load_balancer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#install_updates_on_boot OpsworksCustomLayer#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_shutdown_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#instance_shutdown_timeout OpsworksCustomLayer#instance_shutdown_timeout}.'''
        result = self._values.get("instance_shutdown_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def system_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#system_packages OpsworksCustomLayer#system_packages}.'''
        result = self._values.get("system_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#tags OpsworksCustomLayer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#tags_all OpsworksCustomLayer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#use_ebs_optimized_instances OpsworksCustomLayer#use_ebs_optimized_instances}.'''
        result = self._values.get("use_ebs_optimized_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksCustomLayerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksCustomLayerEbsVolume",
    jsii_struct_bases=[],
    name_mapping={
        "mount_point": "mountPoint",
        "number_of_disks": "numberOfDisks",
        "size": "size",
        "encrypted": "encrypted",
        "iops": "iops",
        "raid_level": "raidLevel",
        "type": "type",
    },
)
class OpsworksCustomLayerEbsVolume:
    def __init__(
        self,
        *,
        mount_point: builtins.str,
        number_of_disks: jsii.Number,
        size: jsii.Number,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        raid_level: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mount_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#mount_point OpsworksCustomLayer#mount_point}.
        :param number_of_disks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#number_of_disks OpsworksCustomLayer#number_of_disks}.
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#size OpsworksCustomLayer#size}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#encrypted OpsworksCustomLayer#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#iops OpsworksCustomLayer#iops}.
        :param raid_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#raid_level OpsworksCustomLayer#raid_level}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#type OpsworksCustomLayer#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mount_point": mount_point,
            "number_of_disks": number_of_disks,
            "size": size,
        }
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if raid_level is not None:
            self._values["raid_level"] = raid_level
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#mount_point OpsworksCustomLayer#mount_point}.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_disks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#number_of_disks OpsworksCustomLayer#number_of_disks}.'''
        result = self._values.get("number_of_disks")
        assert result is not None, "Required property 'number_of_disks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#size OpsworksCustomLayer#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#encrypted OpsworksCustomLayer#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#iops OpsworksCustomLayer#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raid_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#raid_level OpsworksCustomLayer#raid_level}.'''
        result = self._values.get("raid_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_custom_layer#type OpsworksCustomLayer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksCustomLayerEbsVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksGangliaLayer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksGangliaLayer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer aws_opsworks_ganglia_layer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        password: builtins.str,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksGangliaLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        url: typing.Optional[builtins.str] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer aws_opsworks_ganglia_layer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#password OpsworksGangliaLayer#password}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#stack_id OpsworksGangliaLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#auto_assign_elastic_ips OpsworksGangliaLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#auto_assign_public_ips OpsworksGangliaLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#auto_healing OpsworksGangliaLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_configure_recipes OpsworksGangliaLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_deploy_recipes OpsworksGangliaLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_instance_profile_arn OpsworksGangliaLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_json OpsworksGangliaLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_security_group_ids OpsworksGangliaLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_setup_recipes OpsworksGangliaLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_shutdown_recipes OpsworksGangliaLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_undeploy_recipes OpsworksGangliaLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#drain_elb_on_shutdown OpsworksGangliaLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#ebs_volume OpsworksGangliaLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#elastic_load_balancer OpsworksGangliaLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#install_updates_on_boot OpsworksGangliaLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#instance_shutdown_timeout OpsworksGangliaLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#name OpsworksGangliaLayer#name}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#system_packages OpsworksGangliaLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#tags OpsworksGangliaLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#tags_all OpsworksGangliaLayer#tags_all}.
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#url OpsworksGangliaLayer#url}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#use_ebs_optimized_instances OpsworksGangliaLayer#use_ebs_optimized_instances}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#username OpsworksGangliaLayer#username}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksGangliaLayerConfig(
            password=password,
            stack_id=stack_id,
            auto_assign_elastic_ips=auto_assign_elastic_ips,
            auto_assign_public_ips=auto_assign_public_ips,
            auto_healing=auto_healing,
            custom_configure_recipes=custom_configure_recipes,
            custom_deploy_recipes=custom_deploy_recipes,
            custom_instance_profile_arn=custom_instance_profile_arn,
            custom_json=custom_json,
            custom_security_group_ids=custom_security_group_ids,
            custom_setup_recipes=custom_setup_recipes,
            custom_shutdown_recipes=custom_shutdown_recipes,
            custom_undeploy_recipes=custom_undeploy_recipes,
            drain_elb_on_shutdown=drain_elb_on_shutdown,
            ebs_volume=ebs_volume,
            elastic_load_balancer=elastic_load_balancer,
            install_updates_on_boot=install_updates_on_boot,
            instance_shutdown_timeout=instance_shutdown_timeout,
            name=name,
            system_packages=system_packages,
            tags=tags,
            tags_all=tags_all,
            url=url,
            use_ebs_optimized_instances=use_ebs_optimized_instances,
            username=username,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAutoAssignElasticIps")
    def reset_auto_assign_elastic_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignElasticIps", []))

    @jsii.member(jsii_name="resetAutoAssignPublicIps")
    def reset_auto_assign_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignPublicIps", []))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetCustomConfigureRecipes")
    def reset_custom_configure_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomConfigureRecipes", []))

    @jsii.member(jsii_name="resetCustomDeployRecipes")
    def reset_custom_deploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDeployRecipes", []))

    @jsii.member(jsii_name="resetCustomInstanceProfileArn")
    def reset_custom_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomInstanceProfileArn", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetCustomSecurityGroupIds")
    def reset_custom_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupIds", []))

    @jsii.member(jsii_name="resetCustomSetupRecipes")
    def reset_custom_setup_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSetupRecipes", []))

    @jsii.member(jsii_name="resetCustomShutdownRecipes")
    def reset_custom_shutdown_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomShutdownRecipes", []))

    @jsii.member(jsii_name="resetCustomUndeployRecipes")
    def reset_custom_undeploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUndeployRecipes", []))

    @jsii.member(jsii_name="resetDrainElbOnShutdown")
    def reset_drain_elb_on_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainElbOnShutdown", []))

    @jsii.member(jsii_name="resetEbsVolume")
    def reset_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolume", []))

    @jsii.member(jsii_name="resetElasticLoadBalancer")
    def reset_elastic_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticLoadBalancer", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceShutdownTimeout")
    def reset_instance_shutdown_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceShutdownTimeout", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSystemPackages")
    def reset_system_packages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemPackages", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUseEbsOptimizedInstances")
    def reset_use_ebs_optimized_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseEbsOptimizedInstances", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIpsInput")
    def auto_assign_elastic_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignElasticIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIpsInput")
    def auto_assign_public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignPublicIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipesInput")
    def custom_configure_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customConfigureRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipesInput")
    def custom_deploy_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customDeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArnInput")
    def custom_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdsInput")
    def custom_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipesInput")
    def custom_setup_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSetupRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipesInput")
    def custom_shutdown_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customShutdownRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipesInput")
    def custom_undeploy_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customUndeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdownInput")
    def drain_elb_on_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "drainElbOnShutdownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeInput")
    def ebs_volume_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksGangliaLayerEbsVolume"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksGangliaLayerEbsVolume"]], jsii.get(self, "ebsVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancerInput")
    def elastic_load_balancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticLoadBalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeoutInput")
    def instance_shutdown_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceShutdownTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackagesInput")
    def system_packages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "systemPackagesInput"))

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
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useEbsOptimizedInstancesInput")
    def use_ebs_optimized_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useEbsOptimizedInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIps")
    def auto_assign_elastic_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignElasticIps"))

    @auto_assign_elastic_ips.setter
    def auto_assign_elastic_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignElasticIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIps")
    def auto_assign_public_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignPublicIps"))

    @auto_assign_public_ips.setter
    def auto_assign_public_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignPublicIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoHealing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipes")
    def custom_configure_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customConfigureRecipes"))

    @custom_configure_recipes.setter
    def custom_configure_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customConfigureRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipes")
    def custom_deploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDeployRecipes"))

    @custom_deploy_recipes.setter
    def custom_deploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customDeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArn")
    def custom_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customInstanceProfileArn"))

    @custom_instance_profile_arn.setter
    def custom_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "customInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIds")
    def custom_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSecurityGroupIds"))

    @custom_security_group_ids.setter
    def custom_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipes")
    def custom_setup_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSetupRecipes"))

    @custom_setup_recipes.setter
    def custom_setup_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSetupRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipes")
    def custom_shutdown_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customShutdownRecipes"))

    @custom_shutdown_recipes.setter
    def custom_shutdown_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customShutdownRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipes")
    def custom_undeploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customUndeployRecipes"))

    @custom_undeploy_recipes.setter
    def custom_undeploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customUndeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdown")
    def drain_elb_on_shutdown(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "drainElbOnShutdown"))

    @drain_elb_on_shutdown.setter
    def drain_elb_on_shutdown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "drainElbOnShutdown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolume")
    def ebs_volume(self) -> typing.List["OpsworksGangliaLayerEbsVolume"]:
        return typing.cast(typing.List["OpsworksGangliaLayerEbsVolume"], jsii.get(self, "ebsVolume"))

    @ebs_volume.setter
    def ebs_volume(self, value: typing.List["OpsworksGangliaLayerEbsVolume"]) -> None:
        jsii.set(self, "ebsVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancer")
    def elastic_load_balancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticLoadBalancer"))

    @elastic_load_balancer.setter
    def elastic_load_balancer(self, value: builtins.str) -> None:
        jsii.set(self, "elasticLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeout")
    def instance_shutdown_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceShutdownTimeout"))

    @instance_shutdown_timeout.setter
    def instance_shutdown_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceShutdownTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackages")
    def system_packages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "systemPackages"))

    @system_packages.setter
    def system_packages(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "systemPackages", value)

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
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        jsii.set(self, "url", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useEbsOptimizedInstances")
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useEbsOptimizedInstances"))

    @use_ebs_optimized_instances.setter
    def use_ebs_optimized_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useEbsOptimizedInstances", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksGangliaLayerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "password": "password",
        "stack_id": "stackId",
        "auto_assign_elastic_ips": "autoAssignElasticIps",
        "auto_assign_public_ips": "autoAssignPublicIps",
        "auto_healing": "autoHealing",
        "custom_configure_recipes": "customConfigureRecipes",
        "custom_deploy_recipes": "customDeployRecipes",
        "custom_instance_profile_arn": "customInstanceProfileArn",
        "custom_json": "customJson",
        "custom_security_group_ids": "customSecurityGroupIds",
        "custom_setup_recipes": "customSetupRecipes",
        "custom_shutdown_recipes": "customShutdownRecipes",
        "custom_undeploy_recipes": "customUndeployRecipes",
        "drain_elb_on_shutdown": "drainElbOnShutdown",
        "ebs_volume": "ebsVolume",
        "elastic_load_balancer": "elasticLoadBalancer",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_shutdown_timeout": "instanceShutdownTimeout",
        "name": "name",
        "system_packages": "systemPackages",
        "tags": "tags",
        "tags_all": "tagsAll",
        "url": "url",
        "use_ebs_optimized_instances": "useEbsOptimizedInstances",
        "username": "username",
    },
)
class OpsworksGangliaLayerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        password: builtins.str,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksGangliaLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        url: typing.Optional[builtins.str] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#password OpsworksGangliaLayer#password}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#stack_id OpsworksGangliaLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#auto_assign_elastic_ips OpsworksGangliaLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#auto_assign_public_ips OpsworksGangliaLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#auto_healing OpsworksGangliaLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_configure_recipes OpsworksGangliaLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_deploy_recipes OpsworksGangliaLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_instance_profile_arn OpsworksGangliaLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_json OpsworksGangliaLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_security_group_ids OpsworksGangliaLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_setup_recipes OpsworksGangliaLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_shutdown_recipes OpsworksGangliaLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_undeploy_recipes OpsworksGangliaLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#drain_elb_on_shutdown OpsworksGangliaLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#ebs_volume OpsworksGangliaLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#elastic_load_balancer OpsworksGangliaLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#install_updates_on_boot OpsworksGangliaLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#instance_shutdown_timeout OpsworksGangliaLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#name OpsworksGangliaLayer#name}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#system_packages OpsworksGangliaLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#tags OpsworksGangliaLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#tags_all OpsworksGangliaLayer#tags_all}.
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#url OpsworksGangliaLayer#url}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#use_ebs_optimized_instances OpsworksGangliaLayer#use_ebs_optimized_instances}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#username OpsworksGangliaLayer#username}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "password": password,
            "stack_id": stack_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auto_assign_elastic_ips is not None:
            self._values["auto_assign_elastic_ips"] = auto_assign_elastic_ips
        if auto_assign_public_ips is not None:
            self._values["auto_assign_public_ips"] = auto_assign_public_ips
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if custom_configure_recipes is not None:
            self._values["custom_configure_recipes"] = custom_configure_recipes
        if custom_deploy_recipes is not None:
            self._values["custom_deploy_recipes"] = custom_deploy_recipes
        if custom_instance_profile_arn is not None:
            self._values["custom_instance_profile_arn"] = custom_instance_profile_arn
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if custom_security_group_ids is not None:
            self._values["custom_security_group_ids"] = custom_security_group_ids
        if custom_setup_recipes is not None:
            self._values["custom_setup_recipes"] = custom_setup_recipes
        if custom_shutdown_recipes is not None:
            self._values["custom_shutdown_recipes"] = custom_shutdown_recipes
        if custom_undeploy_recipes is not None:
            self._values["custom_undeploy_recipes"] = custom_undeploy_recipes
        if drain_elb_on_shutdown is not None:
            self._values["drain_elb_on_shutdown"] = drain_elb_on_shutdown
        if ebs_volume is not None:
            self._values["ebs_volume"] = ebs_volume
        if elastic_load_balancer is not None:
            self._values["elastic_load_balancer"] = elastic_load_balancer
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_shutdown_timeout is not None:
            self._values["instance_shutdown_timeout"] = instance_shutdown_timeout
        if name is not None:
            self._values["name"] = name
        if system_packages is not None:
            self._values["system_packages"] = system_packages
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if url is not None:
            self._values["url"] = url
        if use_ebs_optimized_instances is not None:
            self._values["use_ebs_optimized_instances"] = use_ebs_optimized_instances
        if username is not None:
            self._values["username"] = username

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
    def password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#password OpsworksGangliaLayer#password}.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#stack_id OpsworksGangliaLayer#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_assign_elastic_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#auto_assign_elastic_ips OpsworksGangliaLayer#auto_assign_elastic_ips}.'''
        result = self._values.get("auto_assign_elastic_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_assign_public_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#auto_assign_public_ips OpsworksGangliaLayer#auto_assign_public_ips}.'''
        result = self._values.get("auto_assign_public_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#auto_healing OpsworksGangliaLayer#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def custom_configure_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_configure_recipes OpsworksGangliaLayer#custom_configure_recipes}.'''
        result = self._values.get("custom_configure_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_deploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_deploy_recipes OpsworksGangliaLayer#custom_deploy_recipes}.'''
        result = self._values.get("custom_deploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_instance_profile_arn OpsworksGangliaLayer#custom_instance_profile_arn}.'''
        result = self._values.get("custom_instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_json OpsworksGangliaLayer#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_security_group_ids OpsworksGangliaLayer#custom_security_group_ids}.'''
        result = self._values.get("custom_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_setup_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_setup_recipes OpsworksGangliaLayer#custom_setup_recipes}.'''
        result = self._values.get("custom_setup_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_shutdown_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_shutdown_recipes OpsworksGangliaLayer#custom_shutdown_recipes}.'''
        result = self._values.get("custom_shutdown_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_undeploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#custom_undeploy_recipes OpsworksGangliaLayer#custom_undeploy_recipes}.'''
        result = self._values.get("custom_undeploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drain_elb_on_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#drain_elb_on_shutdown OpsworksGangliaLayer#drain_elb_on_shutdown}.'''
        result = self._values.get("drain_elb_on_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_volume(
        self,
    ) -> typing.Optional[typing.List["OpsworksGangliaLayerEbsVolume"]]:
        '''ebs_volume block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#ebs_volume OpsworksGangliaLayer#ebs_volume}
        '''
        result = self._values.get("ebs_volume")
        return typing.cast(typing.Optional[typing.List["OpsworksGangliaLayerEbsVolume"]], result)

    @builtins.property
    def elastic_load_balancer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#elastic_load_balancer OpsworksGangliaLayer#elastic_load_balancer}.'''
        result = self._values.get("elastic_load_balancer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#install_updates_on_boot OpsworksGangliaLayer#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_shutdown_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#instance_shutdown_timeout OpsworksGangliaLayer#instance_shutdown_timeout}.'''
        result = self._values.get("instance_shutdown_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#name OpsworksGangliaLayer#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def system_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#system_packages OpsworksGangliaLayer#system_packages}.'''
        result = self._values.get("system_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#tags OpsworksGangliaLayer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#tags_all OpsworksGangliaLayer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#url OpsworksGangliaLayer#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#use_ebs_optimized_instances OpsworksGangliaLayer#use_ebs_optimized_instances}.'''
        result = self._values.get("use_ebs_optimized_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#username OpsworksGangliaLayer#username}.'''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksGangliaLayerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksGangliaLayerEbsVolume",
    jsii_struct_bases=[],
    name_mapping={
        "mount_point": "mountPoint",
        "number_of_disks": "numberOfDisks",
        "size": "size",
        "encrypted": "encrypted",
        "iops": "iops",
        "raid_level": "raidLevel",
        "type": "type",
    },
)
class OpsworksGangliaLayerEbsVolume:
    def __init__(
        self,
        *,
        mount_point: builtins.str,
        number_of_disks: jsii.Number,
        size: jsii.Number,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        raid_level: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mount_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#mount_point OpsworksGangliaLayer#mount_point}.
        :param number_of_disks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#number_of_disks OpsworksGangliaLayer#number_of_disks}.
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#size OpsworksGangliaLayer#size}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#encrypted OpsworksGangliaLayer#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#iops OpsworksGangliaLayer#iops}.
        :param raid_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#raid_level OpsworksGangliaLayer#raid_level}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#type OpsworksGangliaLayer#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mount_point": mount_point,
            "number_of_disks": number_of_disks,
            "size": size,
        }
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if raid_level is not None:
            self._values["raid_level"] = raid_level
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#mount_point OpsworksGangliaLayer#mount_point}.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_disks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#number_of_disks OpsworksGangliaLayer#number_of_disks}.'''
        result = self._values.get("number_of_disks")
        assert result is not None, "Required property 'number_of_disks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#size OpsworksGangliaLayer#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#encrypted OpsworksGangliaLayer#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#iops OpsworksGangliaLayer#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raid_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#raid_level OpsworksGangliaLayer#raid_level}.'''
        result = self._values.get("raid_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_ganglia_layer#type OpsworksGangliaLayer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksGangliaLayerEbsVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksHaproxyLayer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksHaproxyLayer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer aws_opsworks_haproxy_layer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        stack_id: builtins.str,
        stats_password: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksHaproxyLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        healthcheck_method: typing.Optional[builtins.str] = None,
        healthcheck_url: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        stats_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        stats_url: typing.Optional[builtins.str] = None,
        stats_user: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer aws_opsworks_haproxy_layer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stack_id OpsworksHaproxyLayer#stack_id}.
        :param stats_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_password OpsworksHaproxyLayer#stats_password}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#auto_assign_elastic_ips OpsworksHaproxyLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#auto_assign_public_ips OpsworksHaproxyLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#auto_healing OpsworksHaproxyLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_configure_recipes OpsworksHaproxyLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_deploy_recipes OpsworksHaproxyLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_instance_profile_arn OpsworksHaproxyLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_json OpsworksHaproxyLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_security_group_ids OpsworksHaproxyLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_setup_recipes OpsworksHaproxyLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_shutdown_recipes OpsworksHaproxyLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_undeploy_recipes OpsworksHaproxyLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#drain_elb_on_shutdown OpsworksHaproxyLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#ebs_volume OpsworksHaproxyLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#elastic_load_balancer OpsworksHaproxyLayer#elastic_load_balancer}.
        :param healthcheck_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#healthcheck_method OpsworksHaproxyLayer#healthcheck_method}.
        :param healthcheck_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#healthcheck_url OpsworksHaproxyLayer#healthcheck_url}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#install_updates_on_boot OpsworksHaproxyLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#instance_shutdown_timeout OpsworksHaproxyLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#name OpsworksHaproxyLayer#name}.
        :param stats_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_enabled OpsworksHaproxyLayer#stats_enabled}.
        :param stats_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_url OpsworksHaproxyLayer#stats_url}.
        :param stats_user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_user OpsworksHaproxyLayer#stats_user}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#system_packages OpsworksHaproxyLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#tags OpsworksHaproxyLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#tags_all OpsworksHaproxyLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#use_ebs_optimized_instances OpsworksHaproxyLayer#use_ebs_optimized_instances}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksHaproxyLayerConfig(
            stack_id=stack_id,
            stats_password=stats_password,
            auto_assign_elastic_ips=auto_assign_elastic_ips,
            auto_assign_public_ips=auto_assign_public_ips,
            auto_healing=auto_healing,
            custom_configure_recipes=custom_configure_recipes,
            custom_deploy_recipes=custom_deploy_recipes,
            custom_instance_profile_arn=custom_instance_profile_arn,
            custom_json=custom_json,
            custom_security_group_ids=custom_security_group_ids,
            custom_setup_recipes=custom_setup_recipes,
            custom_shutdown_recipes=custom_shutdown_recipes,
            custom_undeploy_recipes=custom_undeploy_recipes,
            drain_elb_on_shutdown=drain_elb_on_shutdown,
            ebs_volume=ebs_volume,
            elastic_load_balancer=elastic_load_balancer,
            healthcheck_method=healthcheck_method,
            healthcheck_url=healthcheck_url,
            install_updates_on_boot=install_updates_on_boot,
            instance_shutdown_timeout=instance_shutdown_timeout,
            name=name,
            stats_enabled=stats_enabled,
            stats_url=stats_url,
            stats_user=stats_user,
            system_packages=system_packages,
            tags=tags,
            tags_all=tags_all,
            use_ebs_optimized_instances=use_ebs_optimized_instances,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAutoAssignElasticIps")
    def reset_auto_assign_elastic_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignElasticIps", []))

    @jsii.member(jsii_name="resetAutoAssignPublicIps")
    def reset_auto_assign_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignPublicIps", []))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetCustomConfigureRecipes")
    def reset_custom_configure_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomConfigureRecipes", []))

    @jsii.member(jsii_name="resetCustomDeployRecipes")
    def reset_custom_deploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDeployRecipes", []))

    @jsii.member(jsii_name="resetCustomInstanceProfileArn")
    def reset_custom_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomInstanceProfileArn", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetCustomSecurityGroupIds")
    def reset_custom_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupIds", []))

    @jsii.member(jsii_name="resetCustomSetupRecipes")
    def reset_custom_setup_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSetupRecipes", []))

    @jsii.member(jsii_name="resetCustomShutdownRecipes")
    def reset_custom_shutdown_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomShutdownRecipes", []))

    @jsii.member(jsii_name="resetCustomUndeployRecipes")
    def reset_custom_undeploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUndeployRecipes", []))

    @jsii.member(jsii_name="resetDrainElbOnShutdown")
    def reset_drain_elb_on_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainElbOnShutdown", []))

    @jsii.member(jsii_name="resetEbsVolume")
    def reset_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolume", []))

    @jsii.member(jsii_name="resetElasticLoadBalancer")
    def reset_elastic_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticLoadBalancer", []))

    @jsii.member(jsii_name="resetHealthcheckMethod")
    def reset_healthcheck_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthcheckMethod", []))

    @jsii.member(jsii_name="resetHealthcheckUrl")
    def reset_healthcheck_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthcheckUrl", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceShutdownTimeout")
    def reset_instance_shutdown_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceShutdownTimeout", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetStatsEnabled")
    def reset_stats_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatsEnabled", []))

    @jsii.member(jsii_name="resetStatsUrl")
    def reset_stats_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatsUrl", []))

    @jsii.member(jsii_name="resetStatsUser")
    def reset_stats_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatsUser", []))

    @jsii.member(jsii_name="resetSystemPackages")
    def reset_system_packages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemPackages", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUseEbsOptimizedInstances")
    def reset_use_ebs_optimized_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseEbsOptimizedInstances", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIpsInput")
    def auto_assign_elastic_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignElasticIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIpsInput")
    def auto_assign_public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignPublicIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipesInput")
    def custom_configure_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customConfigureRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipesInput")
    def custom_deploy_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customDeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArnInput")
    def custom_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdsInput")
    def custom_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipesInput")
    def custom_setup_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSetupRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipesInput")
    def custom_shutdown_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customShutdownRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipesInput")
    def custom_undeploy_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customUndeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdownInput")
    def drain_elb_on_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "drainElbOnShutdownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeInput")
    def ebs_volume_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksHaproxyLayerEbsVolume"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksHaproxyLayerEbsVolume"]], jsii.get(self, "ebsVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancerInput")
    def elastic_load_balancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticLoadBalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthcheckMethodInput")
    def healthcheck_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "healthcheckMethodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthcheckUrlInput")
    def healthcheck_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "healthcheckUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeoutInput")
    def instance_shutdown_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceShutdownTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statsEnabledInput")
    def stats_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "statsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statsPasswordInput")
    def stats_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statsPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statsUrlInput")
    def stats_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statsUrlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statsUserInput")
    def stats_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statsUserInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackagesInput")
    def system_packages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "systemPackagesInput"))

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
    @jsii.member(jsii_name="useEbsOptimizedInstancesInput")
    def use_ebs_optimized_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useEbsOptimizedInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIps")
    def auto_assign_elastic_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignElasticIps"))

    @auto_assign_elastic_ips.setter
    def auto_assign_elastic_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignElasticIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIps")
    def auto_assign_public_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignPublicIps"))

    @auto_assign_public_ips.setter
    def auto_assign_public_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignPublicIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoHealing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipes")
    def custom_configure_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customConfigureRecipes"))

    @custom_configure_recipes.setter
    def custom_configure_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customConfigureRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipes")
    def custom_deploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDeployRecipes"))

    @custom_deploy_recipes.setter
    def custom_deploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customDeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArn")
    def custom_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customInstanceProfileArn"))

    @custom_instance_profile_arn.setter
    def custom_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "customInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIds")
    def custom_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSecurityGroupIds"))

    @custom_security_group_ids.setter
    def custom_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipes")
    def custom_setup_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSetupRecipes"))

    @custom_setup_recipes.setter
    def custom_setup_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSetupRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipes")
    def custom_shutdown_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customShutdownRecipes"))

    @custom_shutdown_recipes.setter
    def custom_shutdown_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customShutdownRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipes")
    def custom_undeploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customUndeployRecipes"))

    @custom_undeploy_recipes.setter
    def custom_undeploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customUndeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdown")
    def drain_elb_on_shutdown(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "drainElbOnShutdown"))

    @drain_elb_on_shutdown.setter
    def drain_elb_on_shutdown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "drainElbOnShutdown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolume")
    def ebs_volume(self) -> typing.List["OpsworksHaproxyLayerEbsVolume"]:
        return typing.cast(typing.List["OpsworksHaproxyLayerEbsVolume"], jsii.get(self, "ebsVolume"))

    @ebs_volume.setter
    def ebs_volume(self, value: typing.List["OpsworksHaproxyLayerEbsVolume"]) -> None:
        jsii.set(self, "ebsVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancer")
    def elastic_load_balancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticLoadBalancer"))

    @elastic_load_balancer.setter
    def elastic_load_balancer(self, value: builtins.str) -> None:
        jsii.set(self, "elasticLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthcheckMethod")
    def healthcheck_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "healthcheckMethod"))

    @healthcheck_method.setter
    def healthcheck_method(self, value: builtins.str) -> None:
        jsii.set(self, "healthcheckMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthcheckUrl")
    def healthcheck_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "healthcheckUrl"))

    @healthcheck_url.setter
    def healthcheck_url(self, value: builtins.str) -> None:
        jsii.set(self, "healthcheckUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeout")
    def instance_shutdown_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceShutdownTimeout"))

    @instance_shutdown_timeout.setter
    def instance_shutdown_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceShutdownTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statsEnabled")
    def stats_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "statsEnabled"))

    @stats_enabled.setter
    def stats_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "statsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statsPassword")
    def stats_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statsPassword"))

    @stats_password.setter
    def stats_password(self, value: builtins.str) -> None:
        jsii.set(self, "statsPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statsUrl")
    def stats_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statsUrl"))

    @stats_url.setter
    def stats_url(self, value: builtins.str) -> None:
        jsii.set(self, "statsUrl", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statsUser")
    def stats_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statsUser"))

    @stats_user.setter
    def stats_user(self, value: builtins.str) -> None:
        jsii.set(self, "statsUser", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackages")
    def system_packages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "systemPackages"))

    @system_packages.setter
    def system_packages(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "systemPackages", value)

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
    @jsii.member(jsii_name="useEbsOptimizedInstances")
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useEbsOptimizedInstances"))

    @use_ebs_optimized_instances.setter
    def use_ebs_optimized_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useEbsOptimizedInstances", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksHaproxyLayerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "stack_id": "stackId",
        "stats_password": "statsPassword",
        "auto_assign_elastic_ips": "autoAssignElasticIps",
        "auto_assign_public_ips": "autoAssignPublicIps",
        "auto_healing": "autoHealing",
        "custom_configure_recipes": "customConfigureRecipes",
        "custom_deploy_recipes": "customDeployRecipes",
        "custom_instance_profile_arn": "customInstanceProfileArn",
        "custom_json": "customJson",
        "custom_security_group_ids": "customSecurityGroupIds",
        "custom_setup_recipes": "customSetupRecipes",
        "custom_shutdown_recipes": "customShutdownRecipes",
        "custom_undeploy_recipes": "customUndeployRecipes",
        "drain_elb_on_shutdown": "drainElbOnShutdown",
        "ebs_volume": "ebsVolume",
        "elastic_load_balancer": "elasticLoadBalancer",
        "healthcheck_method": "healthcheckMethod",
        "healthcheck_url": "healthcheckUrl",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_shutdown_timeout": "instanceShutdownTimeout",
        "name": "name",
        "stats_enabled": "statsEnabled",
        "stats_url": "statsUrl",
        "stats_user": "statsUser",
        "system_packages": "systemPackages",
        "tags": "tags",
        "tags_all": "tagsAll",
        "use_ebs_optimized_instances": "useEbsOptimizedInstances",
    },
)
class OpsworksHaproxyLayerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        stack_id: builtins.str,
        stats_password: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksHaproxyLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        healthcheck_method: typing.Optional[builtins.str] = None,
        healthcheck_url: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        stats_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        stats_url: typing.Optional[builtins.str] = None,
        stats_user: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stack_id OpsworksHaproxyLayer#stack_id}.
        :param stats_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_password OpsworksHaproxyLayer#stats_password}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#auto_assign_elastic_ips OpsworksHaproxyLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#auto_assign_public_ips OpsworksHaproxyLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#auto_healing OpsworksHaproxyLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_configure_recipes OpsworksHaproxyLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_deploy_recipes OpsworksHaproxyLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_instance_profile_arn OpsworksHaproxyLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_json OpsworksHaproxyLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_security_group_ids OpsworksHaproxyLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_setup_recipes OpsworksHaproxyLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_shutdown_recipes OpsworksHaproxyLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_undeploy_recipes OpsworksHaproxyLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#drain_elb_on_shutdown OpsworksHaproxyLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#ebs_volume OpsworksHaproxyLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#elastic_load_balancer OpsworksHaproxyLayer#elastic_load_balancer}.
        :param healthcheck_method: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#healthcheck_method OpsworksHaproxyLayer#healthcheck_method}.
        :param healthcheck_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#healthcheck_url OpsworksHaproxyLayer#healthcheck_url}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#install_updates_on_boot OpsworksHaproxyLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#instance_shutdown_timeout OpsworksHaproxyLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#name OpsworksHaproxyLayer#name}.
        :param stats_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_enabled OpsworksHaproxyLayer#stats_enabled}.
        :param stats_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_url OpsworksHaproxyLayer#stats_url}.
        :param stats_user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_user OpsworksHaproxyLayer#stats_user}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#system_packages OpsworksHaproxyLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#tags OpsworksHaproxyLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#tags_all OpsworksHaproxyLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#use_ebs_optimized_instances OpsworksHaproxyLayer#use_ebs_optimized_instances}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "stack_id": stack_id,
            "stats_password": stats_password,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auto_assign_elastic_ips is not None:
            self._values["auto_assign_elastic_ips"] = auto_assign_elastic_ips
        if auto_assign_public_ips is not None:
            self._values["auto_assign_public_ips"] = auto_assign_public_ips
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if custom_configure_recipes is not None:
            self._values["custom_configure_recipes"] = custom_configure_recipes
        if custom_deploy_recipes is not None:
            self._values["custom_deploy_recipes"] = custom_deploy_recipes
        if custom_instance_profile_arn is not None:
            self._values["custom_instance_profile_arn"] = custom_instance_profile_arn
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if custom_security_group_ids is not None:
            self._values["custom_security_group_ids"] = custom_security_group_ids
        if custom_setup_recipes is not None:
            self._values["custom_setup_recipes"] = custom_setup_recipes
        if custom_shutdown_recipes is not None:
            self._values["custom_shutdown_recipes"] = custom_shutdown_recipes
        if custom_undeploy_recipes is not None:
            self._values["custom_undeploy_recipes"] = custom_undeploy_recipes
        if drain_elb_on_shutdown is not None:
            self._values["drain_elb_on_shutdown"] = drain_elb_on_shutdown
        if ebs_volume is not None:
            self._values["ebs_volume"] = ebs_volume
        if elastic_load_balancer is not None:
            self._values["elastic_load_balancer"] = elastic_load_balancer
        if healthcheck_method is not None:
            self._values["healthcheck_method"] = healthcheck_method
        if healthcheck_url is not None:
            self._values["healthcheck_url"] = healthcheck_url
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_shutdown_timeout is not None:
            self._values["instance_shutdown_timeout"] = instance_shutdown_timeout
        if name is not None:
            self._values["name"] = name
        if stats_enabled is not None:
            self._values["stats_enabled"] = stats_enabled
        if stats_url is not None:
            self._values["stats_url"] = stats_url
        if stats_user is not None:
            self._values["stats_user"] = stats_user
        if system_packages is not None:
            self._values["system_packages"] = system_packages
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if use_ebs_optimized_instances is not None:
            self._values["use_ebs_optimized_instances"] = use_ebs_optimized_instances

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
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stack_id OpsworksHaproxyLayer#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stats_password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_password OpsworksHaproxyLayer#stats_password}.'''
        result = self._values.get("stats_password")
        assert result is not None, "Required property 'stats_password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_assign_elastic_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#auto_assign_elastic_ips OpsworksHaproxyLayer#auto_assign_elastic_ips}.'''
        result = self._values.get("auto_assign_elastic_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_assign_public_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#auto_assign_public_ips OpsworksHaproxyLayer#auto_assign_public_ips}.'''
        result = self._values.get("auto_assign_public_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#auto_healing OpsworksHaproxyLayer#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def custom_configure_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_configure_recipes OpsworksHaproxyLayer#custom_configure_recipes}.'''
        result = self._values.get("custom_configure_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_deploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_deploy_recipes OpsworksHaproxyLayer#custom_deploy_recipes}.'''
        result = self._values.get("custom_deploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_instance_profile_arn OpsworksHaproxyLayer#custom_instance_profile_arn}.'''
        result = self._values.get("custom_instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_json OpsworksHaproxyLayer#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_security_group_ids OpsworksHaproxyLayer#custom_security_group_ids}.'''
        result = self._values.get("custom_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_setup_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_setup_recipes OpsworksHaproxyLayer#custom_setup_recipes}.'''
        result = self._values.get("custom_setup_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_shutdown_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_shutdown_recipes OpsworksHaproxyLayer#custom_shutdown_recipes}.'''
        result = self._values.get("custom_shutdown_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_undeploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#custom_undeploy_recipes OpsworksHaproxyLayer#custom_undeploy_recipes}.'''
        result = self._values.get("custom_undeploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drain_elb_on_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#drain_elb_on_shutdown OpsworksHaproxyLayer#drain_elb_on_shutdown}.'''
        result = self._values.get("drain_elb_on_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_volume(
        self,
    ) -> typing.Optional[typing.List["OpsworksHaproxyLayerEbsVolume"]]:
        '''ebs_volume block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#ebs_volume OpsworksHaproxyLayer#ebs_volume}
        '''
        result = self._values.get("ebs_volume")
        return typing.cast(typing.Optional[typing.List["OpsworksHaproxyLayerEbsVolume"]], result)

    @builtins.property
    def elastic_load_balancer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#elastic_load_balancer OpsworksHaproxyLayer#elastic_load_balancer}.'''
        result = self._values.get("elastic_load_balancer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def healthcheck_method(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#healthcheck_method OpsworksHaproxyLayer#healthcheck_method}.'''
        result = self._values.get("healthcheck_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def healthcheck_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#healthcheck_url OpsworksHaproxyLayer#healthcheck_url}.'''
        result = self._values.get("healthcheck_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#install_updates_on_boot OpsworksHaproxyLayer#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_shutdown_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#instance_shutdown_timeout OpsworksHaproxyLayer#instance_shutdown_timeout}.'''
        result = self._values.get("instance_shutdown_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#name OpsworksHaproxyLayer#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stats_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_enabled OpsworksHaproxyLayer#stats_enabled}.'''
        result = self._values.get("stats_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def stats_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_url OpsworksHaproxyLayer#stats_url}.'''
        result = self._values.get("stats_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stats_user(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#stats_user OpsworksHaproxyLayer#stats_user}.'''
        result = self._values.get("stats_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def system_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#system_packages OpsworksHaproxyLayer#system_packages}.'''
        result = self._values.get("system_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#tags OpsworksHaproxyLayer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#tags_all OpsworksHaproxyLayer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#use_ebs_optimized_instances OpsworksHaproxyLayer#use_ebs_optimized_instances}.'''
        result = self._values.get("use_ebs_optimized_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksHaproxyLayerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksHaproxyLayerEbsVolume",
    jsii_struct_bases=[],
    name_mapping={
        "mount_point": "mountPoint",
        "number_of_disks": "numberOfDisks",
        "size": "size",
        "encrypted": "encrypted",
        "iops": "iops",
        "raid_level": "raidLevel",
        "type": "type",
    },
)
class OpsworksHaproxyLayerEbsVolume:
    def __init__(
        self,
        *,
        mount_point: builtins.str,
        number_of_disks: jsii.Number,
        size: jsii.Number,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        raid_level: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mount_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#mount_point OpsworksHaproxyLayer#mount_point}.
        :param number_of_disks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#number_of_disks OpsworksHaproxyLayer#number_of_disks}.
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#size OpsworksHaproxyLayer#size}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#encrypted OpsworksHaproxyLayer#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#iops OpsworksHaproxyLayer#iops}.
        :param raid_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#raid_level OpsworksHaproxyLayer#raid_level}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#type OpsworksHaproxyLayer#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mount_point": mount_point,
            "number_of_disks": number_of_disks,
            "size": size,
        }
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if raid_level is not None:
            self._values["raid_level"] = raid_level
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#mount_point OpsworksHaproxyLayer#mount_point}.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_disks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#number_of_disks OpsworksHaproxyLayer#number_of_disks}.'''
        result = self._values.get("number_of_disks")
        assert result is not None, "Required property 'number_of_disks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#size OpsworksHaproxyLayer#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#encrypted OpsworksHaproxyLayer#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#iops OpsworksHaproxyLayer#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raid_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#raid_level OpsworksHaproxyLayer#raid_level}.'''
        result = self._values.get("raid_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_haproxy_layer#type OpsworksHaproxyLayer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksHaproxyLayerEbsVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksInstance(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance aws_opsworks_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        layer_ids: typing.Sequence[builtins.str],
        stack_id: builtins.str,
        agent_version: typing.Optional[builtins.str] = None,
        ami_id: typing.Optional[builtins.str] = None,
        architecture: typing.Optional[builtins.str] = None,
        auto_scaling_type: typing.Optional[builtins.str] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[builtins.str] = None,
        delete_ebs: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        delete_eip: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_block_device: typing.Optional[typing.Sequence["OpsworksInstanceEbsBlockDevice"]] = None,
        ebs_optimized: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ecs_cluster_arn: typing.Optional[builtins.str] = None,
        elastic_ip: typing.Optional[builtins.str] = None,
        ephemeral_block_device: typing.Optional[typing.Sequence["OpsworksInstanceEphemeralBlockDevice"]] = None,
        hostname: typing.Optional[builtins.str] = None,
        infrastructure_class: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[builtins.str] = None,
        last_service_error_id: typing.Optional[builtins.str] = None,
        os: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
        private_dns: typing.Optional[builtins.str] = None,
        private_ip: typing.Optional[builtins.str] = None,
        public_dns: typing.Optional[builtins.str] = None,
        public_ip: typing.Optional[builtins.str] = None,
        registered_by: typing.Optional[builtins.str] = None,
        reported_agent_version: typing.Optional[builtins.str] = None,
        reported_os_family: typing.Optional[builtins.str] = None,
        reported_os_name: typing.Optional[builtins.str] = None,
        reported_os_version: typing.Optional[builtins.str] = None,
        root_block_device: typing.Optional[typing.Sequence["OpsworksInstanceRootBlockDevice"]] = None,
        root_device_type: typing.Optional[builtins.str] = None,
        root_device_volume_id: typing.Optional[builtins.str] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        ssh_host_dsa_key_fingerprint: typing.Optional[builtins.str] = None,
        ssh_host_rsa_key_fingerprint: typing.Optional[builtins.str] = None,
        ssh_key_name: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        tenancy: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["OpsworksInstanceTimeouts"] = None,
        virtualization_type: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance aws_opsworks_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param layer_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#layer_ids OpsworksInstance#layer_ids}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#stack_id OpsworksInstance#stack_id}.
        :param agent_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#agent_version OpsworksInstance#agent_version}.
        :param ami_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ami_id OpsworksInstance#ami_id}.
        :param architecture: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#architecture OpsworksInstance#architecture}.
        :param auto_scaling_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#auto_scaling_type OpsworksInstance#auto_scaling_type}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#availability_zone OpsworksInstance#availability_zone}.
        :param created_at: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#created_at OpsworksInstance#created_at}.
        :param delete_ebs: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete_ebs OpsworksInstance#delete_ebs}.
        :param delete_eip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete_eip OpsworksInstance#delete_eip}.
        :param ebs_block_device: ebs_block_device block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ebs_block_device OpsworksInstance#ebs_block_device}
        :param ebs_optimized: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ebs_optimized OpsworksInstance#ebs_optimized}.
        :param ecs_cluster_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ecs_cluster_arn OpsworksInstance#ecs_cluster_arn}.
        :param elastic_ip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#elastic_ip OpsworksInstance#elastic_ip}.
        :param ephemeral_block_device: ephemeral_block_device block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ephemeral_block_device OpsworksInstance#ephemeral_block_device}
        :param hostname: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#hostname OpsworksInstance#hostname}.
        :param infrastructure_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#infrastructure_class OpsworksInstance#infrastructure_class}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#install_updates_on_boot OpsworksInstance#install_updates_on_boot}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#instance_profile_arn OpsworksInstance#instance_profile_arn}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#instance_type OpsworksInstance#instance_type}.
        :param last_service_error_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#last_service_error_id OpsworksInstance#last_service_error_id}.
        :param os: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#os OpsworksInstance#os}.
        :param platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#platform OpsworksInstance#platform}.
        :param private_dns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#private_dns OpsworksInstance#private_dns}.
        :param private_ip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#private_ip OpsworksInstance#private_ip}.
        :param public_dns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#public_dns OpsworksInstance#public_dns}.
        :param public_ip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#public_ip OpsworksInstance#public_ip}.
        :param registered_by: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#registered_by OpsworksInstance#registered_by}.
        :param reported_agent_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_agent_version OpsworksInstance#reported_agent_version}.
        :param reported_os_family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_os_family OpsworksInstance#reported_os_family}.
        :param reported_os_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_os_name OpsworksInstance#reported_os_name}.
        :param reported_os_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_os_version OpsworksInstance#reported_os_version}.
        :param root_block_device: root_block_device block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#root_block_device OpsworksInstance#root_block_device}
        :param root_device_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#root_device_type OpsworksInstance#root_device_type}.
        :param root_device_volume_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#root_device_volume_id OpsworksInstance#root_device_volume_id}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#security_group_ids OpsworksInstance#security_group_ids}.
        :param ssh_host_dsa_key_fingerprint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ssh_host_dsa_key_fingerprint OpsworksInstance#ssh_host_dsa_key_fingerprint}.
        :param ssh_host_rsa_key_fingerprint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ssh_host_rsa_key_fingerprint OpsworksInstance#ssh_host_rsa_key_fingerprint}.
        :param ssh_key_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ssh_key_name OpsworksInstance#ssh_key_name}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#state OpsworksInstance#state}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#status OpsworksInstance#status}.
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#subnet_id OpsworksInstance#subnet_id}.
        :param tenancy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#tenancy OpsworksInstance#tenancy}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#timeouts OpsworksInstance#timeouts}
        :param virtualization_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#virtualization_type OpsworksInstance#virtualization_type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksInstanceConfig(
            layer_ids=layer_ids,
            stack_id=stack_id,
            agent_version=agent_version,
            ami_id=ami_id,
            architecture=architecture,
            auto_scaling_type=auto_scaling_type,
            availability_zone=availability_zone,
            created_at=created_at,
            delete_ebs=delete_ebs,
            delete_eip=delete_eip,
            ebs_block_device=ebs_block_device,
            ebs_optimized=ebs_optimized,
            ecs_cluster_arn=ecs_cluster_arn,
            elastic_ip=elastic_ip,
            ephemeral_block_device=ephemeral_block_device,
            hostname=hostname,
            infrastructure_class=infrastructure_class,
            install_updates_on_boot=install_updates_on_boot,
            instance_profile_arn=instance_profile_arn,
            instance_type=instance_type,
            last_service_error_id=last_service_error_id,
            os=os,
            platform=platform,
            private_dns=private_dns,
            private_ip=private_ip,
            public_dns=public_dns,
            public_ip=public_ip,
            registered_by=registered_by,
            reported_agent_version=reported_agent_version,
            reported_os_family=reported_os_family,
            reported_os_name=reported_os_name,
            reported_os_version=reported_os_version,
            root_block_device=root_block_device,
            root_device_type=root_device_type,
            root_device_volume_id=root_device_volume_id,
            security_group_ids=security_group_ids,
            ssh_host_dsa_key_fingerprint=ssh_host_dsa_key_fingerprint,
            ssh_host_rsa_key_fingerprint=ssh_host_rsa_key_fingerprint,
            ssh_key_name=ssh_key_name,
            state=state,
            status=status,
            subnet_id=subnet_id,
            tenancy=tenancy,
            timeouts=timeouts,
            virtualization_type=virtualization_type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#create OpsworksInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete OpsworksInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#update OpsworksInstance#update}.
        '''
        value = OpsworksInstanceTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAgentVersion")
    def reset_agent_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAgentVersion", []))

    @jsii.member(jsii_name="resetAmiId")
    def reset_ami_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAmiId", []))

    @jsii.member(jsii_name="resetArchitecture")
    def reset_architecture(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArchitecture", []))

    @jsii.member(jsii_name="resetAutoScalingType")
    def reset_auto_scaling_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoScalingType", []))

    @jsii.member(jsii_name="resetAvailabilityZone")
    def reset_availability_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAvailabilityZone", []))

    @jsii.member(jsii_name="resetCreatedAt")
    def reset_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAt", []))

    @jsii.member(jsii_name="resetDeleteEbs")
    def reset_delete_ebs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteEbs", []))

    @jsii.member(jsii_name="resetDeleteEip")
    def reset_delete_eip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteEip", []))

    @jsii.member(jsii_name="resetEbsBlockDevice")
    def reset_ebs_block_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsBlockDevice", []))

    @jsii.member(jsii_name="resetEbsOptimized")
    def reset_ebs_optimized(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsOptimized", []))

    @jsii.member(jsii_name="resetEcsClusterArn")
    def reset_ecs_cluster_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEcsClusterArn", []))

    @jsii.member(jsii_name="resetElasticIp")
    def reset_elastic_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticIp", []))

    @jsii.member(jsii_name="resetEphemeralBlockDevice")
    def reset_ephemeral_block_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEphemeralBlockDevice", []))

    @jsii.member(jsii_name="resetHostname")
    def reset_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostname", []))

    @jsii.member(jsii_name="resetInfrastructureClass")
    def reset_infrastructure_class(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInfrastructureClass", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceProfileArn")
    def reset_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceProfileArn", []))

    @jsii.member(jsii_name="resetInstanceType")
    def reset_instance_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceType", []))

    @jsii.member(jsii_name="resetLastServiceErrorId")
    def reset_last_service_error_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastServiceErrorId", []))

    @jsii.member(jsii_name="resetOs")
    def reset_os(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOs", []))

    @jsii.member(jsii_name="resetPlatform")
    def reset_platform(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlatform", []))

    @jsii.member(jsii_name="resetPrivateDns")
    def reset_private_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateDns", []))

    @jsii.member(jsii_name="resetPrivateIp")
    def reset_private_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateIp", []))

    @jsii.member(jsii_name="resetPublicDns")
    def reset_public_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicDns", []))

    @jsii.member(jsii_name="resetPublicIp")
    def reset_public_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicIp", []))

    @jsii.member(jsii_name="resetRegisteredBy")
    def reset_registered_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegisteredBy", []))

    @jsii.member(jsii_name="resetReportedAgentVersion")
    def reset_reported_agent_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReportedAgentVersion", []))

    @jsii.member(jsii_name="resetReportedOsFamily")
    def reset_reported_os_family(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReportedOsFamily", []))

    @jsii.member(jsii_name="resetReportedOsName")
    def reset_reported_os_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReportedOsName", []))

    @jsii.member(jsii_name="resetReportedOsVersion")
    def reset_reported_os_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReportedOsVersion", []))

    @jsii.member(jsii_name="resetRootBlockDevice")
    def reset_root_block_device(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootBlockDevice", []))

    @jsii.member(jsii_name="resetRootDeviceType")
    def reset_root_device_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootDeviceType", []))

    @jsii.member(jsii_name="resetRootDeviceVolumeId")
    def reset_root_device_volume_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootDeviceVolumeId", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetSshHostDsaKeyFingerprint")
    def reset_ssh_host_dsa_key_fingerprint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshHostDsaKeyFingerprint", []))

    @jsii.member(jsii_name="resetSshHostRsaKeyFingerprint")
    def reset_ssh_host_rsa_key_fingerprint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshHostRsaKeyFingerprint", []))

    @jsii.member(jsii_name="resetSshKeyName")
    def reset_ssh_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshKeyName", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="resetSubnetId")
    def reset_subnet_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetId", []))

    @jsii.member(jsii_name="resetTenancy")
    def reset_tenancy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTenancy", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetVirtualizationType")
    def reset_virtualization_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVirtualizationType", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2InstanceId")
    def ec2_instance_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ec2InstanceId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "OpsworksInstanceTimeoutsOutputReference":
        return typing.cast("OpsworksInstanceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentVersionInput")
    def agent_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiIdInput")
    def ami_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "amiIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="architectureInput")
    def architecture_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "architectureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoScalingTypeInput")
    def auto_scaling_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoScalingTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneInput")
    def availability_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAtInput")
    def created_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAtInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteEbsInput")
    def delete_ebs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deleteEbsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteEipInput")
    def delete_eip_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "deleteEipInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsBlockDeviceInput")
    def ebs_block_device_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksInstanceEbsBlockDevice"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksInstanceEbsBlockDevice"]], jsii.get(self, "ebsBlockDeviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsOptimizedInput")
    def ebs_optimized_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ebsOptimizedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecsClusterArnInput")
    def ecs_cluster_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ecsClusterArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticIpInput")
    def elastic_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticIpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ephemeralBlockDeviceInput")
    def ephemeral_block_device_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksInstanceEphemeralBlockDevice"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksInstanceEphemeralBlockDevice"]], jsii.get(self, "ephemeralBlockDeviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infrastructureClassInput")
    def infrastructure_class_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "infrastructureClassInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfileArnInput")
    def instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceTypeInput")
    def instance_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastServiceErrorIdInput")
    def last_service_error_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastServiceErrorIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerIdsInput")
    def layer_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "layerIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="osInput")
    def os_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformInput")
    def platform_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "platformInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateDnsInput")
    def private_dns_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateDnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateIpInput")
    def private_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateIpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicDnsInput")
    def public_dns_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicDnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicIpInput")
    def public_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicIpInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registeredByInput")
    def registered_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "registeredByInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportedAgentVersionInput")
    def reported_agent_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportedAgentVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportedOsFamilyInput")
    def reported_os_family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportedOsFamilyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportedOsNameInput")
    def reported_os_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportedOsNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportedOsVersionInput")
    def reported_os_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "reportedOsVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootBlockDeviceInput")
    def root_block_device_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksInstanceRootBlockDevice"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksInstanceRootBlockDevice"]], jsii.get(self, "rootBlockDeviceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootDeviceTypeInput")
    def root_device_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rootDeviceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootDeviceVolumeIdInput")
    def root_device_volume_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rootDeviceVolumeIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshHostDsaKeyFingerprintInput")
    def ssh_host_dsa_key_fingerprint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sshHostDsaKeyFingerprintInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshHostRsaKeyFingerprintInput")
    def ssh_host_rsa_key_fingerprint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sshHostRsaKeyFingerprintInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshKeyNameInput")
    def ssh_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sshKeyNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdInput")
    def subnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tenancyInput")
    def tenancy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tenancyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["OpsworksInstanceTimeouts"]:
        return typing.cast(typing.Optional["OpsworksInstanceTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="virtualizationTypeInput")
    def virtualization_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "virtualizationTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentVersion")
    def agent_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "agentVersion"))

    @agent_version.setter
    def agent_version(self, value: builtins.str) -> None:
        jsii.set(self, "agentVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiId")
    def ami_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "amiId"))

    @ami_id.setter
    def ami_id(self, value: builtins.str) -> None:
        jsii.set(self, "amiId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="architecture")
    def architecture(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "architecture"))

    @architecture.setter
    def architecture(self, value: builtins.str) -> None:
        jsii.set(self, "architecture", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoScalingType")
    def auto_scaling_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoScalingType"))

    @auto_scaling_type.setter
    def auto_scaling_type(self, value: builtins.str) -> None:
        jsii.set(self, "autoScalingType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: builtins.str) -> None:
        jsii.set(self, "availabilityZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: builtins.str) -> None:
        jsii.set(self, "createdAt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteEbs")
    def delete_ebs(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deleteEbs"))

    @delete_ebs.setter
    def delete_ebs(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "deleteEbs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteEip")
    def delete_eip(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "deleteEip"))

    @delete_eip.setter
    def delete_eip(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "deleteEip", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsBlockDevice")
    def ebs_block_device(self) -> typing.List["OpsworksInstanceEbsBlockDevice"]:
        return typing.cast(typing.List["OpsworksInstanceEbsBlockDevice"], jsii.get(self, "ebsBlockDevice"))

    @ebs_block_device.setter
    def ebs_block_device(
        self,
        value: typing.List["OpsworksInstanceEbsBlockDevice"],
    ) -> None:
        jsii.set(self, "ebsBlockDevice", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsOptimized")
    def ebs_optimized(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ebsOptimized"))

    @ebs_optimized.setter
    def ebs_optimized(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "ebsOptimized", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecsClusterArn")
    def ecs_cluster_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ecsClusterArn"))

    @ecs_cluster_arn.setter
    def ecs_cluster_arn(self, value: builtins.str) -> None:
        jsii.set(self, "ecsClusterArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticIp")
    def elastic_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticIp"))

    @elastic_ip.setter
    def elastic_ip(self, value: builtins.str) -> None:
        jsii.set(self, "elasticIp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ephemeralBlockDevice")
    def ephemeral_block_device(
        self,
    ) -> typing.List["OpsworksInstanceEphemeralBlockDevice"]:
        return typing.cast(typing.List["OpsworksInstanceEphemeralBlockDevice"], jsii.get(self, "ephemeralBlockDevice"))

    @ephemeral_block_device.setter
    def ephemeral_block_device(
        self,
        value: typing.List["OpsworksInstanceEphemeralBlockDevice"],
    ) -> None:
        jsii.set(self, "ephemeralBlockDevice", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        jsii.set(self, "hostname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infrastructureClass")
    def infrastructure_class(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "infrastructureClass"))

    @infrastructure_class.setter
    def infrastructure_class(self, value: builtins.str) -> None:
        jsii.set(self, "infrastructureClass", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceProfileArn")
    def instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceProfileArn"))

    @instance_profile_arn.setter
    def instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "instanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastServiceErrorId")
    def last_service_error_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastServiceErrorId"))

    @last_service_error_id.setter
    def last_service_error_id(self, value: builtins.str) -> None:
        jsii.set(self, "lastServiceErrorId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="layerIds")
    def layer_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "layerIds"))

    @layer_ids.setter
    def layer_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "layerIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="os")
    def os(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "os"))

    @os.setter
    def os(self, value: builtins.str) -> None:
        jsii.set(self, "os", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @platform.setter
    def platform(self, value: builtins.str) -> None:
        jsii.set(self, "platform", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateDns")
    def private_dns(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateDns"))

    @private_dns.setter
    def private_dns(self, value: builtins.str) -> None:
        jsii.set(self, "privateDns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateIp")
    def private_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateIp"))

    @private_ip.setter
    def private_ip(self, value: builtins.str) -> None:
        jsii.set(self, "privateIp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicDns")
    def public_dns(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicDns"))

    @public_dns.setter
    def public_dns(self, value: builtins.str) -> None:
        jsii.set(self, "publicDns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicIp")
    def public_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicIp"))

    @public_ip.setter
    def public_ip(self, value: builtins.str) -> None:
        jsii.set(self, "publicIp", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registeredBy")
    def registered_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "registeredBy"))

    @registered_by.setter
    def registered_by(self, value: builtins.str) -> None:
        jsii.set(self, "registeredBy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportedAgentVersion")
    def reported_agent_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportedAgentVersion"))

    @reported_agent_version.setter
    def reported_agent_version(self, value: builtins.str) -> None:
        jsii.set(self, "reportedAgentVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportedOsFamily")
    def reported_os_family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportedOsFamily"))

    @reported_os_family.setter
    def reported_os_family(self, value: builtins.str) -> None:
        jsii.set(self, "reportedOsFamily", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportedOsName")
    def reported_os_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportedOsName"))

    @reported_os_name.setter
    def reported_os_name(self, value: builtins.str) -> None:
        jsii.set(self, "reportedOsName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reportedOsVersion")
    def reported_os_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "reportedOsVersion"))

    @reported_os_version.setter
    def reported_os_version(self, value: builtins.str) -> None:
        jsii.set(self, "reportedOsVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootBlockDevice")
    def root_block_device(self) -> typing.List["OpsworksInstanceRootBlockDevice"]:
        return typing.cast(typing.List["OpsworksInstanceRootBlockDevice"], jsii.get(self, "rootBlockDevice"))

    @root_block_device.setter
    def root_block_device(
        self,
        value: typing.List["OpsworksInstanceRootBlockDevice"],
    ) -> None:
        jsii.set(self, "rootBlockDevice", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootDeviceType")
    def root_device_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootDeviceType"))

    @root_device_type.setter
    def root_device_type(self, value: builtins.str) -> None:
        jsii.set(self, "rootDeviceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootDeviceVolumeId")
    def root_device_volume_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootDeviceVolumeId"))

    @root_device_volume_id.setter
    def root_device_volume_id(self, value: builtins.str) -> None:
        jsii.set(self, "rootDeviceVolumeId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshHostDsaKeyFingerprint")
    def ssh_host_dsa_key_fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshHostDsaKeyFingerprint"))

    @ssh_host_dsa_key_fingerprint.setter
    def ssh_host_dsa_key_fingerprint(self, value: builtins.str) -> None:
        jsii.set(self, "sshHostDsaKeyFingerprint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshHostRsaKeyFingerprint")
    def ssh_host_rsa_key_fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshHostRsaKeyFingerprint"))

    @ssh_host_rsa_key_fingerprint.setter
    def ssh_host_rsa_key_fingerprint(self, value: builtins.str) -> None:
        jsii.set(self, "sshHostRsaKeyFingerprint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshKeyName")
    def ssh_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshKeyName"))

    @ssh_key_name.setter
    def ssh_key_name(self, value: builtins.str) -> None:
        jsii.set(self, "sshKeyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        jsii.set(self, "state", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        jsii.set(self, "status", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetId"))

    @subnet_id.setter
    def subnet_id(self, value: builtins.str) -> None:
        jsii.set(self, "subnetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tenancy")
    def tenancy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tenancy"))

    @tenancy.setter
    def tenancy(self, value: builtins.str) -> None:
        jsii.set(self, "tenancy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="virtualizationType")
    def virtualization_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "virtualizationType"))

    @virtualization_type.setter
    def virtualization_type(self, value: builtins.str) -> None:
        jsii.set(self, "virtualizationType", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "layer_ids": "layerIds",
        "stack_id": "stackId",
        "agent_version": "agentVersion",
        "ami_id": "amiId",
        "architecture": "architecture",
        "auto_scaling_type": "autoScalingType",
        "availability_zone": "availabilityZone",
        "created_at": "createdAt",
        "delete_ebs": "deleteEbs",
        "delete_eip": "deleteEip",
        "ebs_block_device": "ebsBlockDevice",
        "ebs_optimized": "ebsOptimized",
        "ecs_cluster_arn": "ecsClusterArn",
        "elastic_ip": "elasticIp",
        "ephemeral_block_device": "ephemeralBlockDevice",
        "hostname": "hostname",
        "infrastructure_class": "infrastructureClass",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_profile_arn": "instanceProfileArn",
        "instance_type": "instanceType",
        "last_service_error_id": "lastServiceErrorId",
        "os": "os",
        "platform": "platform",
        "private_dns": "privateDns",
        "private_ip": "privateIp",
        "public_dns": "publicDns",
        "public_ip": "publicIp",
        "registered_by": "registeredBy",
        "reported_agent_version": "reportedAgentVersion",
        "reported_os_family": "reportedOsFamily",
        "reported_os_name": "reportedOsName",
        "reported_os_version": "reportedOsVersion",
        "root_block_device": "rootBlockDevice",
        "root_device_type": "rootDeviceType",
        "root_device_volume_id": "rootDeviceVolumeId",
        "security_group_ids": "securityGroupIds",
        "ssh_host_dsa_key_fingerprint": "sshHostDsaKeyFingerprint",
        "ssh_host_rsa_key_fingerprint": "sshHostRsaKeyFingerprint",
        "ssh_key_name": "sshKeyName",
        "state": "state",
        "status": "status",
        "subnet_id": "subnetId",
        "tenancy": "tenancy",
        "timeouts": "timeouts",
        "virtualization_type": "virtualizationType",
    },
)
class OpsworksInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        layer_ids: typing.Sequence[builtins.str],
        stack_id: builtins.str,
        agent_version: typing.Optional[builtins.str] = None,
        ami_id: typing.Optional[builtins.str] = None,
        architecture: typing.Optional[builtins.str] = None,
        auto_scaling_type: typing.Optional[builtins.str] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[builtins.str] = None,
        delete_ebs: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        delete_eip: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_block_device: typing.Optional[typing.Sequence["OpsworksInstanceEbsBlockDevice"]] = None,
        ebs_optimized: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ecs_cluster_arn: typing.Optional[builtins.str] = None,
        elastic_ip: typing.Optional[builtins.str] = None,
        ephemeral_block_device: typing.Optional[typing.Sequence["OpsworksInstanceEphemeralBlockDevice"]] = None,
        hostname: typing.Optional[builtins.str] = None,
        infrastructure_class: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_profile_arn: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[builtins.str] = None,
        last_service_error_id: typing.Optional[builtins.str] = None,
        os: typing.Optional[builtins.str] = None,
        platform: typing.Optional[builtins.str] = None,
        private_dns: typing.Optional[builtins.str] = None,
        private_ip: typing.Optional[builtins.str] = None,
        public_dns: typing.Optional[builtins.str] = None,
        public_ip: typing.Optional[builtins.str] = None,
        registered_by: typing.Optional[builtins.str] = None,
        reported_agent_version: typing.Optional[builtins.str] = None,
        reported_os_family: typing.Optional[builtins.str] = None,
        reported_os_name: typing.Optional[builtins.str] = None,
        reported_os_version: typing.Optional[builtins.str] = None,
        root_block_device: typing.Optional[typing.Sequence["OpsworksInstanceRootBlockDevice"]] = None,
        root_device_type: typing.Optional[builtins.str] = None,
        root_device_volume_id: typing.Optional[builtins.str] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        ssh_host_dsa_key_fingerprint: typing.Optional[builtins.str] = None,
        ssh_host_rsa_key_fingerprint: typing.Optional[builtins.str] = None,
        ssh_key_name: typing.Optional[builtins.str] = None,
        state: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        tenancy: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["OpsworksInstanceTimeouts"] = None,
        virtualization_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param layer_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#layer_ids OpsworksInstance#layer_ids}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#stack_id OpsworksInstance#stack_id}.
        :param agent_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#agent_version OpsworksInstance#agent_version}.
        :param ami_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ami_id OpsworksInstance#ami_id}.
        :param architecture: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#architecture OpsworksInstance#architecture}.
        :param auto_scaling_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#auto_scaling_type OpsworksInstance#auto_scaling_type}.
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#availability_zone OpsworksInstance#availability_zone}.
        :param created_at: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#created_at OpsworksInstance#created_at}.
        :param delete_ebs: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete_ebs OpsworksInstance#delete_ebs}.
        :param delete_eip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete_eip OpsworksInstance#delete_eip}.
        :param ebs_block_device: ebs_block_device block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ebs_block_device OpsworksInstance#ebs_block_device}
        :param ebs_optimized: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ebs_optimized OpsworksInstance#ebs_optimized}.
        :param ecs_cluster_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ecs_cluster_arn OpsworksInstance#ecs_cluster_arn}.
        :param elastic_ip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#elastic_ip OpsworksInstance#elastic_ip}.
        :param ephemeral_block_device: ephemeral_block_device block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ephemeral_block_device OpsworksInstance#ephemeral_block_device}
        :param hostname: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#hostname OpsworksInstance#hostname}.
        :param infrastructure_class: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#infrastructure_class OpsworksInstance#infrastructure_class}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#install_updates_on_boot OpsworksInstance#install_updates_on_boot}.
        :param instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#instance_profile_arn OpsworksInstance#instance_profile_arn}.
        :param instance_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#instance_type OpsworksInstance#instance_type}.
        :param last_service_error_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#last_service_error_id OpsworksInstance#last_service_error_id}.
        :param os: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#os OpsworksInstance#os}.
        :param platform: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#platform OpsworksInstance#platform}.
        :param private_dns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#private_dns OpsworksInstance#private_dns}.
        :param private_ip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#private_ip OpsworksInstance#private_ip}.
        :param public_dns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#public_dns OpsworksInstance#public_dns}.
        :param public_ip: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#public_ip OpsworksInstance#public_ip}.
        :param registered_by: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#registered_by OpsworksInstance#registered_by}.
        :param reported_agent_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_agent_version OpsworksInstance#reported_agent_version}.
        :param reported_os_family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_os_family OpsworksInstance#reported_os_family}.
        :param reported_os_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_os_name OpsworksInstance#reported_os_name}.
        :param reported_os_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_os_version OpsworksInstance#reported_os_version}.
        :param root_block_device: root_block_device block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#root_block_device OpsworksInstance#root_block_device}
        :param root_device_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#root_device_type OpsworksInstance#root_device_type}.
        :param root_device_volume_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#root_device_volume_id OpsworksInstance#root_device_volume_id}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#security_group_ids OpsworksInstance#security_group_ids}.
        :param ssh_host_dsa_key_fingerprint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ssh_host_dsa_key_fingerprint OpsworksInstance#ssh_host_dsa_key_fingerprint}.
        :param ssh_host_rsa_key_fingerprint: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ssh_host_rsa_key_fingerprint OpsworksInstance#ssh_host_rsa_key_fingerprint}.
        :param ssh_key_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ssh_key_name OpsworksInstance#ssh_key_name}.
        :param state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#state OpsworksInstance#state}.
        :param status: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#status OpsworksInstance#status}.
        :param subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#subnet_id OpsworksInstance#subnet_id}.
        :param tenancy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#tenancy OpsworksInstance#tenancy}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#timeouts OpsworksInstance#timeouts}
        :param virtualization_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#virtualization_type OpsworksInstance#virtualization_type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = OpsworksInstanceTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "layer_ids": layer_ids,
            "stack_id": stack_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if agent_version is not None:
            self._values["agent_version"] = agent_version
        if ami_id is not None:
            self._values["ami_id"] = ami_id
        if architecture is not None:
            self._values["architecture"] = architecture
        if auto_scaling_type is not None:
            self._values["auto_scaling_type"] = auto_scaling_type
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if created_at is not None:
            self._values["created_at"] = created_at
        if delete_ebs is not None:
            self._values["delete_ebs"] = delete_ebs
        if delete_eip is not None:
            self._values["delete_eip"] = delete_eip
        if ebs_block_device is not None:
            self._values["ebs_block_device"] = ebs_block_device
        if ebs_optimized is not None:
            self._values["ebs_optimized"] = ebs_optimized
        if ecs_cluster_arn is not None:
            self._values["ecs_cluster_arn"] = ecs_cluster_arn
        if elastic_ip is not None:
            self._values["elastic_ip"] = elastic_ip
        if ephemeral_block_device is not None:
            self._values["ephemeral_block_device"] = ephemeral_block_device
        if hostname is not None:
            self._values["hostname"] = hostname
        if infrastructure_class is not None:
            self._values["infrastructure_class"] = infrastructure_class
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_profile_arn is not None:
            self._values["instance_profile_arn"] = instance_profile_arn
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if last_service_error_id is not None:
            self._values["last_service_error_id"] = last_service_error_id
        if os is not None:
            self._values["os"] = os
        if platform is not None:
            self._values["platform"] = platform
        if private_dns is not None:
            self._values["private_dns"] = private_dns
        if private_ip is not None:
            self._values["private_ip"] = private_ip
        if public_dns is not None:
            self._values["public_dns"] = public_dns
        if public_ip is not None:
            self._values["public_ip"] = public_ip
        if registered_by is not None:
            self._values["registered_by"] = registered_by
        if reported_agent_version is not None:
            self._values["reported_agent_version"] = reported_agent_version
        if reported_os_family is not None:
            self._values["reported_os_family"] = reported_os_family
        if reported_os_name is not None:
            self._values["reported_os_name"] = reported_os_name
        if reported_os_version is not None:
            self._values["reported_os_version"] = reported_os_version
        if root_block_device is not None:
            self._values["root_block_device"] = root_block_device
        if root_device_type is not None:
            self._values["root_device_type"] = root_device_type
        if root_device_volume_id is not None:
            self._values["root_device_volume_id"] = root_device_volume_id
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if ssh_host_dsa_key_fingerprint is not None:
            self._values["ssh_host_dsa_key_fingerprint"] = ssh_host_dsa_key_fingerprint
        if ssh_host_rsa_key_fingerprint is not None:
            self._values["ssh_host_rsa_key_fingerprint"] = ssh_host_rsa_key_fingerprint
        if ssh_key_name is not None:
            self._values["ssh_key_name"] = ssh_key_name
        if state is not None:
            self._values["state"] = state
        if status is not None:
            self._values["status"] = status
        if subnet_id is not None:
            self._values["subnet_id"] = subnet_id
        if tenancy is not None:
            self._values["tenancy"] = tenancy
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if virtualization_type is not None:
            self._values["virtualization_type"] = virtualization_type

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
    def layer_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#layer_ids OpsworksInstance#layer_ids}.'''
        result = self._values.get("layer_ids")
        assert result is not None, "Required property 'layer_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#stack_id OpsworksInstance#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#agent_version OpsworksInstance#agent_version}.'''
        result = self._values.get("agent_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ami_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ami_id OpsworksInstance#ami_id}.'''
        result = self._values.get("ami_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def architecture(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#architecture OpsworksInstance#architecture}.'''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_scaling_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#auto_scaling_type OpsworksInstance#auto_scaling_type}.'''
        result = self._values.get("auto_scaling_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#availability_zone OpsworksInstance#availability_zone}.'''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_at(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#created_at OpsworksInstance#created_at}.'''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_ebs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete_ebs OpsworksInstance#delete_ebs}.'''
        result = self._values.get("delete_ebs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def delete_eip(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete_eip OpsworksInstance#delete_eip}.'''
        result = self._values.get("delete_eip")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_block_device(
        self,
    ) -> typing.Optional[typing.List["OpsworksInstanceEbsBlockDevice"]]:
        '''ebs_block_device block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ebs_block_device OpsworksInstance#ebs_block_device}
        '''
        result = self._values.get("ebs_block_device")
        return typing.cast(typing.Optional[typing.List["OpsworksInstanceEbsBlockDevice"]], result)

    @builtins.property
    def ebs_optimized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ebs_optimized OpsworksInstance#ebs_optimized}.'''
        result = self._values.get("ebs_optimized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ecs_cluster_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ecs_cluster_arn OpsworksInstance#ecs_cluster_arn}.'''
        result = self._values.get("ecs_cluster_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elastic_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#elastic_ip OpsworksInstance#elastic_ip}.'''
        result = self._values.get("elastic_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ephemeral_block_device(
        self,
    ) -> typing.Optional[typing.List["OpsworksInstanceEphemeralBlockDevice"]]:
        '''ephemeral_block_device block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ephemeral_block_device OpsworksInstance#ephemeral_block_device}
        '''
        result = self._values.get("ephemeral_block_device")
        return typing.cast(typing.Optional[typing.List["OpsworksInstanceEphemeralBlockDevice"]], result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#hostname OpsworksInstance#hostname}.'''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def infrastructure_class(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#infrastructure_class OpsworksInstance#infrastructure_class}.'''
        result = self._values.get("infrastructure_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#install_updates_on_boot OpsworksInstance#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#instance_profile_arn OpsworksInstance#instance_profile_arn}.'''
        result = self._values.get("instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#instance_type OpsworksInstance#instance_type}.'''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_service_error_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#last_service_error_id OpsworksInstance#last_service_error_id}.'''
        result = self._values.get("last_service_error_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def os(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#os OpsworksInstance#os}.'''
        result = self._values.get("os")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def platform(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#platform OpsworksInstance#platform}.'''
        result = self._values.get("platform")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_dns(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#private_dns OpsworksInstance#private_dns}.'''
        result = self._values.get("private_dns")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#private_ip OpsworksInstance#private_ip}.'''
        result = self._values.get("private_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_dns(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#public_dns OpsworksInstance#public_dns}.'''
        result = self._values.get("public_dns")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#public_ip OpsworksInstance#public_ip}.'''
        result = self._values.get("public_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registered_by(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#registered_by OpsworksInstance#registered_by}.'''
        result = self._values.get("registered_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def reported_agent_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_agent_version OpsworksInstance#reported_agent_version}.'''
        result = self._values.get("reported_agent_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def reported_os_family(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_os_family OpsworksInstance#reported_os_family}.'''
        result = self._values.get("reported_os_family")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def reported_os_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_os_name OpsworksInstance#reported_os_name}.'''
        result = self._values.get("reported_os_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def reported_os_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#reported_os_version OpsworksInstance#reported_os_version}.'''
        result = self._values.get("reported_os_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def root_block_device(
        self,
    ) -> typing.Optional[typing.List["OpsworksInstanceRootBlockDevice"]]:
        '''root_block_device block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#root_block_device OpsworksInstance#root_block_device}
        '''
        result = self._values.get("root_block_device")
        return typing.cast(typing.Optional[typing.List["OpsworksInstanceRootBlockDevice"]], result)

    @builtins.property
    def root_device_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#root_device_type OpsworksInstance#root_device_type}.'''
        result = self._values.get("root_device_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def root_device_volume_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#root_device_volume_id OpsworksInstance#root_device_volume_id}.'''
        result = self._values.get("root_device_volume_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#security_group_ids OpsworksInstance#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ssh_host_dsa_key_fingerprint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ssh_host_dsa_key_fingerprint OpsworksInstance#ssh_host_dsa_key_fingerprint}.'''
        result = self._values.get("ssh_host_dsa_key_fingerprint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_host_rsa_key_fingerprint(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ssh_host_rsa_key_fingerprint OpsworksInstance#ssh_host_rsa_key_fingerprint}.'''
        result = self._values.get("ssh_host_rsa_key_fingerprint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_key_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#ssh_key_name OpsworksInstance#ssh_key_name}.'''
        result = self._values.get("ssh_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#state OpsworksInstance#state}.'''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#status OpsworksInstance#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#subnet_id OpsworksInstance#subnet_id}.'''
        result = self._values.get("subnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tenancy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#tenancy OpsworksInstance#tenancy}.'''
        result = self._values.get("tenancy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["OpsworksInstanceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#timeouts OpsworksInstance#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["OpsworksInstanceTimeouts"], result)

    @builtins.property
    def virtualization_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#virtualization_type OpsworksInstance#virtualization_type}.'''
        result = self._values.get("virtualization_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksInstanceEbsBlockDevice",
    jsii_struct_bases=[],
    name_mapping={
        "device_name": "deviceName",
        "delete_on_termination": "deleteOnTermination",
        "iops": "iops",
        "snapshot_id": "snapshotId",
        "volume_size": "volumeSize",
        "volume_type": "volumeType",
    },
)
class OpsworksInstanceEbsBlockDevice:
    def __init__(
        self,
        *,
        device_name: builtins.str,
        delete_on_termination: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param device_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#device_name OpsworksInstance#device_name}.
        :param delete_on_termination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete_on_termination OpsworksInstance#delete_on_termination}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#iops OpsworksInstance#iops}.
        :param snapshot_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#snapshot_id OpsworksInstance#snapshot_id}.
        :param volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#volume_size OpsworksInstance#volume_size}.
        :param volume_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#volume_type OpsworksInstance#volume_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "device_name": device_name,
        }
        if delete_on_termination is not None:
            self._values["delete_on_termination"] = delete_on_termination
        if iops is not None:
            self._values["iops"] = iops
        if snapshot_id is not None:
            self._values["snapshot_id"] = snapshot_id
        if volume_size is not None:
            self._values["volume_size"] = volume_size
        if volume_type is not None:
            self._values["volume_type"] = volume_type

    @builtins.property
    def device_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#device_name OpsworksInstance#device_name}.'''
        result = self._values.get("device_name")
        assert result is not None, "Required property 'device_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_on_termination(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete_on_termination OpsworksInstance#delete_on_termination}.'''
        result = self._values.get("delete_on_termination")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#iops OpsworksInstance#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def snapshot_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#snapshot_id OpsworksInstance#snapshot_id}.'''
        result = self._values.get("snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#volume_size OpsworksInstance#volume_size}.'''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#volume_type OpsworksInstance#volume_type}.'''
        result = self._values.get("volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksInstanceEbsBlockDevice(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksInstanceEphemeralBlockDevice",
    jsii_struct_bases=[],
    name_mapping={"device_name": "deviceName", "virtual_name": "virtualName"},
)
class OpsworksInstanceEphemeralBlockDevice:
    def __init__(
        self,
        *,
        device_name: builtins.str,
        virtual_name: builtins.str,
    ) -> None:
        '''
        :param device_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#device_name OpsworksInstance#device_name}.
        :param virtual_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#virtual_name OpsworksInstance#virtual_name}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "device_name": device_name,
            "virtual_name": virtual_name,
        }

    @builtins.property
    def device_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#device_name OpsworksInstance#device_name}.'''
        result = self._values.get("device_name")
        assert result is not None, "Required property 'device_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def virtual_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#virtual_name OpsworksInstance#virtual_name}.'''
        result = self._values.get("virtual_name")
        assert result is not None, "Required property 'virtual_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksInstanceEphemeralBlockDevice(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksInstanceRootBlockDevice",
    jsii_struct_bases=[],
    name_mapping={
        "delete_on_termination": "deleteOnTermination",
        "iops": "iops",
        "volume_size": "volumeSize",
        "volume_type": "volumeType",
    },
)
class OpsworksInstanceRootBlockDevice:
    def __init__(
        self,
        *,
        delete_on_termination: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        volume_size: typing.Optional[jsii.Number] = None,
        volume_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delete_on_termination: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete_on_termination OpsworksInstance#delete_on_termination}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#iops OpsworksInstance#iops}.
        :param volume_size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#volume_size OpsworksInstance#volume_size}.
        :param volume_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#volume_type OpsworksInstance#volume_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delete_on_termination is not None:
            self._values["delete_on_termination"] = delete_on_termination
        if iops is not None:
            self._values["iops"] = iops
        if volume_size is not None:
            self._values["volume_size"] = volume_size
        if volume_type is not None:
            self._values["volume_type"] = volume_type

    @builtins.property
    def delete_on_termination(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete_on_termination OpsworksInstance#delete_on_termination}.'''
        result = self._values.get("delete_on_termination")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#iops OpsworksInstance#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#volume_size OpsworksInstance#volume_size}.'''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#volume_type OpsworksInstance#volume_type}.'''
        result = self._values.get("volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksInstanceRootBlockDevice(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksInstanceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class OpsworksInstanceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#create OpsworksInstance#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete OpsworksInstance#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#update OpsworksInstance#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#create OpsworksInstance#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#delete OpsworksInstance#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_instance#update OpsworksInstance#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksInstanceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksInstanceTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksInstanceTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OpsworksInstanceTimeouts]:
        return typing.cast(typing.Optional[OpsworksInstanceTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OpsworksInstanceTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class OpsworksJavaAppLayer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksJavaAppLayer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer aws_opsworks_java_app_layer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        stack_id: builtins.str,
        app_server: typing.Optional[builtins.str] = None,
        app_server_version: typing.Optional[builtins.str] = None,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksJavaAppLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        jvm_options: typing.Optional[builtins.str] = None,
        jvm_type: typing.Optional[builtins.str] = None,
        jvm_version: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer aws_opsworks_java_app_layer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#stack_id OpsworksJavaAppLayer#stack_id}.
        :param app_server: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#app_server OpsworksJavaAppLayer#app_server}.
        :param app_server_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#app_server_version OpsworksJavaAppLayer#app_server_version}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#auto_assign_elastic_ips OpsworksJavaAppLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#auto_assign_public_ips OpsworksJavaAppLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#auto_healing OpsworksJavaAppLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_configure_recipes OpsworksJavaAppLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_deploy_recipes OpsworksJavaAppLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_instance_profile_arn OpsworksJavaAppLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_json OpsworksJavaAppLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_security_group_ids OpsworksJavaAppLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_setup_recipes OpsworksJavaAppLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_shutdown_recipes OpsworksJavaAppLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_undeploy_recipes OpsworksJavaAppLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#drain_elb_on_shutdown OpsworksJavaAppLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#ebs_volume OpsworksJavaAppLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#elastic_load_balancer OpsworksJavaAppLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#install_updates_on_boot OpsworksJavaAppLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#instance_shutdown_timeout OpsworksJavaAppLayer#instance_shutdown_timeout}.
        :param jvm_options: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#jvm_options OpsworksJavaAppLayer#jvm_options}.
        :param jvm_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#jvm_type OpsworksJavaAppLayer#jvm_type}.
        :param jvm_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#jvm_version OpsworksJavaAppLayer#jvm_version}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#name OpsworksJavaAppLayer#name}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#system_packages OpsworksJavaAppLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#tags OpsworksJavaAppLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#tags_all OpsworksJavaAppLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#use_ebs_optimized_instances OpsworksJavaAppLayer#use_ebs_optimized_instances}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksJavaAppLayerConfig(
            stack_id=stack_id,
            app_server=app_server,
            app_server_version=app_server_version,
            auto_assign_elastic_ips=auto_assign_elastic_ips,
            auto_assign_public_ips=auto_assign_public_ips,
            auto_healing=auto_healing,
            custom_configure_recipes=custom_configure_recipes,
            custom_deploy_recipes=custom_deploy_recipes,
            custom_instance_profile_arn=custom_instance_profile_arn,
            custom_json=custom_json,
            custom_security_group_ids=custom_security_group_ids,
            custom_setup_recipes=custom_setup_recipes,
            custom_shutdown_recipes=custom_shutdown_recipes,
            custom_undeploy_recipes=custom_undeploy_recipes,
            drain_elb_on_shutdown=drain_elb_on_shutdown,
            ebs_volume=ebs_volume,
            elastic_load_balancer=elastic_load_balancer,
            install_updates_on_boot=install_updates_on_boot,
            instance_shutdown_timeout=instance_shutdown_timeout,
            jvm_options=jvm_options,
            jvm_type=jvm_type,
            jvm_version=jvm_version,
            name=name,
            system_packages=system_packages,
            tags=tags,
            tags_all=tags_all,
            use_ebs_optimized_instances=use_ebs_optimized_instances,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAppServer")
    def reset_app_server(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppServer", []))

    @jsii.member(jsii_name="resetAppServerVersion")
    def reset_app_server_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppServerVersion", []))

    @jsii.member(jsii_name="resetAutoAssignElasticIps")
    def reset_auto_assign_elastic_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignElasticIps", []))

    @jsii.member(jsii_name="resetAutoAssignPublicIps")
    def reset_auto_assign_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignPublicIps", []))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetCustomConfigureRecipes")
    def reset_custom_configure_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomConfigureRecipes", []))

    @jsii.member(jsii_name="resetCustomDeployRecipes")
    def reset_custom_deploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDeployRecipes", []))

    @jsii.member(jsii_name="resetCustomInstanceProfileArn")
    def reset_custom_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomInstanceProfileArn", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetCustomSecurityGroupIds")
    def reset_custom_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupIds", []))

    @jsii.member(jsii_name="resetCustomSetupRecipes")
    def reset_custom_setup_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSetupRecipes", []))

    @jsii.member(jsii_name="resetCustomShutdownRecipes")
    def reset_custom_shutdown_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomShutdownRecipes", []))

    @jsii.member(jsii_name="resetCustomUndeployRecipes")
    def reset_custom_undeploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUndeployRecipes", []))

    @jsii.member(jsii_name="resetDrainElbOnShutdown")
    def reset_drain_elb_on_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainElbOnShutdown", []))

    @jsii.member(jsii_name="resetEbsVolume")
    def reset_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolume", []))

    @jsii.member(jsii_name="resetElasticLoadBalancer")
    def reset_elastic_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticLoadBalancer", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceShutdownTimeout")
    def reset_instance_shutdown_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceShutdownTimeout", []))

    @jsii.member(jsii_name="resetJvmOptions")
    def reset_jvm_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJvmOptions", []))

    @jsii.member(jsii_name="resetJvmType")
    def reset_jvm_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJvmType", []))

    @jsii.member(jsii_name="resetJvmVersion")
    def reset_jvm_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJvmVersion", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSystemPackages")
    def reset_system_packages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemPackages", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUseEbsOptimizedInstances")
    def reset_use_ebs_optimized_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseEbsOptimizedInstances", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appServerInput")
    def app_server_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appServerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appServerVersionInput")
    def app_server_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appServerVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIpsInput")
    def auto_assign_elastic_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignElasticIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIpsInput")
    def auto_assign_public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignPublicIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipesInput")
    def custom_configure_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customConfigureRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipesInput")
    def custom_deploy_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customDeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArnInput")
    def custom_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdsInput")
    def custom_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipesInput")
    def custom_setup_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSetupRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipesInput")
    def custom_shutdown_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customShutdownRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipesInput")
    def custom_undeploy_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customUndeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdownInput")
    def drain_elb_on_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "drainElbOnShutdownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeInput")
    def ebs_volume_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksJavaAppLayerEbsVolume"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksJavaAppLayerEbsVolume"]], jsii.get(self, "ebsVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancerInput")
    def elastic_load_balancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticLoadBalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeoutInput")
    def instance_shutdown_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceShutdownTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmOptionsInput")
    def jvm_options_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jvmOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmTypeInput")
    def jvm_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jvmTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmVersionInput")
    def jvm_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jvmVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackagesInput")
    def system_packages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "systemPackagesInput"))

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
    @jsii.member(jsii_name="useEbsOptimizedInstancesInput")
    def use_ebs_optimized_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useEbsOptimizedInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appServer")
    def app_server(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appServer"))

    @app_server.setter
    def app_server(self, value: builtins.str) -> None:
        jsii.set(self, "appServer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appServerVersion")
    def app_server_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appServerVersion"))

    @app_server_version.setter
    def app_server_version(self, value: builtins.str) -> None:
        jsii.set(self, "appServerVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIps")
    def auto_assign_elastic_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignElasticIps"))

    @auto_assign_elastic_ips.setter
    def auto_assign_elastic_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignElasticIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIps")
    def auto_assign_public_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignPublicIps"))

    @auto_assign_public_ips.setter
    def auto_assign_public_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignPublicIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoHealing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipes")
    def custom_configure_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customConfigureRecipes"))

    @custom_configure_recipes.setter
    def custom_configure_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customConfigureRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipes")
    def custom_deploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDeployRecipes"))

    @custom_deploy_recipes.setter
    def custom_deploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customDeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArn")
    def custom_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customInstanceProfileArn"))

    @custom_instance_profile_arn.setter
    def custom_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "customInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIds")
    def custom_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSecurityGroupIds"))

    @custom_security_group_ids.setter
    def custom_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipes")
    def custom_setup_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSetupRecipes"))

    @custom_setup_recipes.setter
    def custom_setup_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSetupRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipes")
    def custom_shutdown_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customShutdownRecipes"))

    @custom_shutdown_recipes.setter
    def custom_shutdown_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customShutdownRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipes")
    def custom_undeploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customUndeployRecipes"))

    @custom_undeploy_recipes.setter
    def custom_undeploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customUndeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdown")
    def drain_elb_on_shutdown(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "drainElbOnShutdown"))

    @drain_elb_on_shutdown.setter
    def drain_elb_on_shutdown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "drainElbOnShutdown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolume")
    def ebs_volume(self) -> typing.List["OpsworksJavaAppLayerEbsVolume"]:
        return typing.cast(typing.List["OpsworksJavaAppLayerEbsVolume"], jsii.get(self, "ebsVolume"))

    @ebs_volume.setter
    def ebs_volume(self, value: typing.List["OpsworksJavaAppLayerEbsVolume"]) -> None:
        jsii.set(self, "ebsVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancer")
    def elastic_load_balancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticLoadBalancer"))

    @elastic_load_balancer.setter
    def elastic_load_balancer(self, value: builtins.str) -> None:
        jsii.set(self, "elasticLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeout")
    def instance_shutdown_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceShutdownTimeout"))

    @instance_shutdown_timeout.setter
    def instance_shutdown_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceShutdownTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmOptions")
    def jvm_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jvmOptions"))

    @jvm_options.setter
    def jvm_options(self, value: builtins.str) -> None:
        jsii.set(self, "jvmOptions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmType")
    def jvm_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jvmType"))

    @jvm_type.setter
    def jvm_type(self, value: builtins.str) -> None:
        jsii.set(self, "jvmType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jvmVersion")
    def jvm_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jvmVersion"))

    @jvm_version.setter
    def jvm_version(self, value: builtins.str) -> None:
        jsii.set(self, "jvmVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackages")
    def system_packages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "systemPackages"))

    @system_packages.setter
    def system_packages(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "systemPackages", value)

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
    @jsii.member(jsii_name="useEbsOptimizedInstances")
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useEbsOptimizedInstances"))

    @use_ebs_optimized_instances.setter
    def use_ebs_optimized_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useEbsOptimizedInstances", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksJavaAppLayerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "stack_id": "stackId",
        "app_server": "appServer",
        "app_server_version": "appServerVersion",
        "auto_assign_elastic_ips": "autoAssignElasticIps",
        "auto_assign_public_ips": "autoAssignPublicIps",
        "auto_healing": "autoHealing",
        "custom_configure_recipes": "customConfigureRecipes",
        "custom_deploy_recipes": "customDeployRecipes",
        "custom_instance_profile_arn": "customInstanceProfileArn",
        "custom_json": "customJson",
        "custom_security_group_ids": "customSecurityGroupIds",
        "custom_setup_recipes": "customSetupRecipes",
        "custom_shutdown_recipes": "customShutdownRecipes",
        "custom_undeploy_recipes": "customUndeployRecipes",
        "drain_elb_on_shutdown": "drainElbOnShutdown",
        "ebs_volume": "ebsVolume",
        "elastic_load_balancer": "elasticLoadBalancer",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_shutdown_timeout": "instanceShutdownTimeout",
        "jvm_options": "jvmOptions",
        "jvm_type": "jvmType",
        "jvm_version": "jvmVersion",
        "name": "name",
        "system_packages": "systemPackages",
        "tags": "tags",
        "tags_all": "tagsAll",
        "use_ebs_optimized_instances": "useEbsOptimizedInstances",
    },
)
class OpsworksJavaAppLayerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        stack_id: builtins.str,
        app_server: typing.Optional[builtins.str] = None,
        app_server_version: typing.Optional[builtins.str] = None,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksJavaAppLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        jvm_options: typing.Optional[builtins.str] = None,
        jvm_type: typing.Optional[builtins.str] = None,
        jvm_version: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#stack_id OpsworksJavaAppLayer#stack_id}.
        :param app_server: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#app_server OpsworksJavaAppLayer#app_server}.
        :param app_server_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#app_server_version OpsworksJavaAppLayer#app_server_version}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#auto_assign_elastic_ips OpsworksJavaAppLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#auto_assign_public_ips OpsworksJavaAppLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#auto_healing OpsworksJavaAppLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_configure_recipes OpsworksJavaAppLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_deploy_recipes OpsworksJavaAppLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_instance_profile_arn OpsworksJavaAppLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_json OpsworksJavaAppLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_security_group_ids OpsworksJavaAppLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_setup_recipes OpsworksJavaAppLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_shutdown_recipes OpsworksJavaAppLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_undeploy_recipes OpsworksJavaAppLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#drain_elb_on_shutdown OpsworksJavaAppLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#ebs_volume OpsworksJavaAppLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#elastic_load_balancer OpsworksJavaAppLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#install_updates_on_boot OpsworksJavaAppLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#instance_shutdown_timeout OpsworksJavaAppLayer#instance_shutdown_timeout}.
        :param jvm_options: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#jvm_options OpsworksJavaAppLayer#jvm_options}.
        :param jvm_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#jvm_type OpsworksJavaAppLayer#jvm_type}.
        :param jvm_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#jvm_version OpsworksJavaAppLayer#jvm_version}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#name OpsworksJavaAppLayer#name}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#system_packages OpsworksJavaAppLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#tags OpsworksJavaAppLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#tags_all OpsworksJavaAppLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#use_ebs_optimized_instances OpsworksJavaAppLayer#use_ebs_optimized_instances}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "stack_id": stack_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if app_server is not None:
            self._values["app_server"] = app_server
        if app_server_version is not None:
            self._values["app_server_version"] = app_server_version
        if auto_assign_elastic_ips is not None:
            self._values["auto_assign_elastic_ips"] = auto_assign_elastic_ips
        if auto_assign_public_ips is not None:
            self._values["auto_assign_public_ips"] = auto_assign_public_ips
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if custom_configure_recipes is not None:
            self._values["custom_configure_recipes"] = custom_configure_recipes
        if custom_deploy_recipes is not None:
            self._values["custom_deploy_recipes"] = custom_deploy_recipes
        if custom_instance_profile_arn is not None:
            self._values["custom_instance_profile_arn"] = custom_instance_profile_arn
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if custom_security_group_ids is not None:
            self._values["custom_security_group_ids"] = custom_security_group_ids
        if custom_setup_recipes is not None:
            self._values["custom_setup_recipes"] = custom_setup_recipes
        if custom_shutdown_recipes is not None:
            self._values["custom_shutdown_recipes"] = custom_shutdown_recipes
        if custom_undeploy_recipes is not None:
            self._values["custom_undeploy_recipes"] = custom_undeploy_recipes
        if drain_elb_on_shutdown is not None:
            self._values["drain_elb_on_shutdown"] = drain_elb_on_shutdown
        if ebs_volume is not None:
            self._values["ebs_volume"] = ebs_volume
        if elastic_load_balancer is not None:
            self._values["elastic_load_balancer"] = elastic_load_balancer
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_shutdown_timeout is not None:
            self._values["instance_shutdown_timeout"] = instance_shutdown_timeout
        if jvm_options is not None:
            self._values["jvm_options"] = jvm_options
        if jvm_type is not None:
            self._values["jvm_type"] = jvm_type
        if jvm_version is not None:
            self._values["jvm_version"] = jvm_version
        if name is not None:
            self._values["name"] = name
        if system_packages is not None:
            self._values["system_packages"] = system_packages
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if use_ebs_optimized_instances is not None:
            self._values["use_ebs_optimized_instances"] = use_ebs_optimized_instances

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
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#stack_id OpsworksJavaAppLayer#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_server(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#app_server OpsworksJavaAppLayer#app_server}.'''
        result = self._values.get("app_server")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app_server_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#app_server_version OpsworksJavaAppLayer#app_server_version}.'''
        result = self._values.get("app_server_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_assign_elastic_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#auto_assign_elastic_ips OpsworksJavaAppLayer#auto_assign_elastic_ips}.'''
        result = self._values.get("auto_assign_elastic_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_assign_public_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#auto_assign_public_ips OpsworksJavaAppLayer#auto_assign_public_ips}.'''
        result = self._values.get("auto_assign_public_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#auto_healing OpsworksJavaAppLayer#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def custom_configure_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_configure_recipes OpsworksJavaAppLayer#custom_configure_recipes}.'''
        result = self._values.get("custom_configure_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_deploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_deploy_recipes OpsworksJavaAppLayer#custom_deploy_recipes}.'''
        result = self._values.get("custom_deploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_instance_profile_arn OpsworksJavaAppLayer#custom_instance_profile_arn}.'''
        result = self._values.get("custom_instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_json OpsworksJavaAppLayer#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_security_group_ids OpsworksJavaAppLayer#custom_security_group_ids}.'''
        result = self._values.get("custom_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_setup_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_setup_recipes OpsworksJavaAppLayer#custom_setup_recipes}.'''
        result = self._values.get("custom_setup_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_shutdown_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_shutdown_recipes OpsworksJavaAppLayer#custom_shutdown_recipes}.'''
        result = self._values.get("custom_shutdown_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_undeploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#custom_undeploy_recipes OpsworksJavaAppLayer#custom_undeploy_recipes}.'''
        result = self._values.get("custom_undeploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drain_elb_on_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#drain_elb_on_shutdown OpsworksJavaAppLayer#drain_elb_on_shutdown}.'''
        result = self._values.get("drain_elb_on_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_volume(
        self,
    ) -> typing.Optional[typing.List["OpsworksJavaAppLayerEbsVolume"]]:
        '''ebs_volume block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#ebs_volume OpsworksJavaAppLayer#ebs_volume}
        '''
        result = self._values.get("ebs_volume")
        return typing.cast(typing.Optional[typing.List["OpsworksJavaAppLayerEbsVolume"]], result)

    @builtins.property
    def elastic_load_balancer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#elastic_load_balancer OpsworksJavaAppLayer#elastic_load_balancer}.'''
        result = self._values.get("elastic_load_balancer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#install_updates_on_boot OpsworksJavaAppLayer#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_shutdown_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#instance_shutdown_timeout OpsworksJavaAppLayer#instance_shutdown_timeout}.'''
        result = self._values.get("instance_shutdown_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def jvm_options(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#jvm_options OpsworksJavaAppLayer#jvm_options}.'''
        result = self._values.get("jvm_options")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jvm_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#jvm_type OpsworksJavaAppLayer#jvm_type}.'''
        result = self._values.get("jvm_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jvm_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#jvm_version OpsworksJavaAppLayer#jvm_version}.'''
        result = self._values.get("jvm_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#name OpsworksJavaAppLayer#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def system_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#system_packages OpsworksJavaAppLayer#system_packages}.'''
        result = self._values.get("system_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#tags OpsworksJavaAppLayer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#tags_all OpsworksJavaAppLayer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#use_ebs_optimized_instances OpsworksJavaAppLayer#use_ebs_optimized_instances}.'''
        result = self._values.get("use_ebs_optimized_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksJavaAppLayerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksJavaAppLayerEbsVolume",
    jsii_struct_bases=[],
    name_mapping={
        "mount_point": "mountPoint",
        "number_of_disks": "numberOfDisks",
        "size": "size",
        "encrypted": "encrypted",
        "iops": "iops",
        "raid_level": "raidLevel",
        "type": "type",
    },
)
class OpsworksJavaAppLayerEbsVolume:
    def __init__(
        self,
        *,
        mount_point: builtins.str,
        number_of_disks: jsii.Number,
        size: jsii.Number,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        raid_level: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mount_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#mount_point OpsworksJavaAppLayer#mount_point}.
        :param number_of_disks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#number_of_disks OpsworksJavaAppLayer#number_of_disks}.
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#size OpsworksJavaAppLayer#size}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#encrypted OpsworksJavaAppLayer#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#iops OpsworksJavaAppLayer#iops}.
        :param raid_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#raid_level OpsworksJavaAppLayer#raid_level}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#type OpsworksJavaAppLayer#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mount_point": mount_point,
            "number_of_disks": number_of_disks,
            "size": size,
        }
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if raid_level is not None:
            self._values["raid_level"] = raid_level
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#mount_point OpsworksJavaAppLayer#mount_point}.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_disks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#number_of_disks OpsworksJavaAppLayer#number_of_disks}.'''
        result = self._values.get("number_of_disks")
        assert result is not None, "Required property 'number_of_disks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#size OpsworksJavaAppLayer#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#encrypted OpsworksJavaAppLayer#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#iops OpsworksJavaAppLayer#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raid_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#raid_level OpsworksJavaAppLayer#raid_level}.'''
        result = self._values.get("raid_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_java_app_layer#type OpsworksJavaAppLayer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksJavaAppLayerEbsVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksMemcachedLayer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksMemcachedLayer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer aws_opsworks_memcached_layer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        stack_id: builtins.str,
        allocated_memory: typing.Optional[jsii.Number] = None,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksMemcachedLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer aws_opsworks_memcached_layer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#stack_id OpsworksMemcachedLayer#stack_id}.
        :param allocated_memory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#allocated_memory OpsworksMemcachedLayer#allocated_memory}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#auto_assign_elastic_ips OpsworksMemcachedLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#auto_assign_public_ips OpsworksMemcachedLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#auto_healing OpsworksMemcachedLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_configure_recipes OpsworksMemcachedLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_deploy_recipes OpsworksMemcachedLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_instance_profile_arn OpsworksMemcachedLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_json OpsworksMemcachedLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_security_group_ids OpsworksMemcachedLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_setup_recipes OpsworksMemcachedLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_shutdown_recipes OpsworksMemcachedLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_undeploy_recipes OpsworksMemcachedLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#drain_elb_on_shutdown OpsworksMemcachedLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#ebs_volume OpsworksMemcachedLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#elastic_load_balancer OpsworksMemcachedLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#install_updates_on_boot OpsworksMemcachedLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#instance_shutdown_timeout OpsworksMemcachedLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#name OpsworksMemcachedLayer#name}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#system_packages OpsworksMemcachedLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#tags OpsworksMemcachedLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#tags_all OpsworksMemcachedLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#use_ebs_optimized_instances OpsworksMemcachedLayer#use_ebs_optimized_instances}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksMemcachedLayerConfig(
            stack_id=stack_id,
            allocated_memory=allocated_memory,
            auto_assign_elastic_ips=auto_assign_elastic_ips,
            auto_assign_public_ips=auto_assign_public_ips,
            auto_healing=auto_healing,
            custom_configure_recipes=custom_configure_recipes,
            custom_deploy_recipes=custom_deploy_recipes,
            custom_instance_profile_arn=custom_instance_profile_arn,
            custom_json=custom_json,
            custom_security_group_ids=custom_security_group_ids,
            custom_setup_recipes=custom_setup_recipes,
            custom_shutdown_recipes=custom_shutdown_recipes,
            custom_undeploy_recipes=custom_undeploy_recipes,
            drain_elb_on_shutdown=drain_elb_on_shutdown,
            ebs_volume=ebs_volume,
            elastic_load_balancer=elastic_load_balancer,
            install_updates_on_boot=install_updates_on_boot,
            instance_shutdown_timeout=instance_shutdown_timeout,
            name=name,
            system_packages=system_packages,
            tags=tags,
            tags_all=tags_all,
            use_ebs_optimized_instances=use_ebs_optimized_instances,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAllocatedMemory")
    def reset_allocated_memory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllocatedMemory", []))

    @jsii.member(jsii_name="resetAutoAssignElasticIps")
    def reset_auto_assign_elastic_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignElasticIps", []))

    @jsii.member(jsii_name="resetAutoAssignPublicIps")
    def reset_auto_assign_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignPublicIps", []))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetCustomConfigureRecipes")
    def reset_custom_configure_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomConfigureRecipes", []))

    @jsii.member(jsii_name="resetCustomDeployRecipes")
    def reset_custom_deploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDeployRecipes", []))

    @jsii.member(jsii_name="resetCustomInstanceProfileArn")
    def reset_custom_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomInstanceProfileArn", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetCustomSecurityGroupIds")
    def reset_custom_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupIds", []))

    @jsii.member(jsii_name="resetCustomSetupRecipes")
    def reset_custom_setup_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSetupRecipes", []))

    @jsii.member(jsii_name="resetCustomShutdownRecipes")
    def reset_custom_shutdown_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomShutdownRecipes", []))

    @jsii.member(jsii_name="resetCustomUndeployRecipes")
    def reset_custom_undeploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUndeployRecipes", []))

    @jsii.member(jsii_name="resetDrainElbOnShutdown")
    def reset_drain_elb_on_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainElbOnShutdown", []))

    @jsii.member(jsii_name="resetEbsVolume")
    def reset_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolume", []))

    @jsii.member(jsii_name="resetElasticLoadBalancer")
    def reset_elastic_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticLoadBalancer", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceShutdownTimeout")
    def reset_instance_shutdown_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceShutdownTimeout", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSystemPackages")
    def reset_system_packages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemPackages", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUseEbsOptimizedInstances")
    def reset_use_ebs_optimized_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseEbsOptimizedInstances", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocatedMemoryInput")
    def allocated_memory_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "allocatedMemoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIpsInput")
    def auto_assign_elastic_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignElasticIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIpsInput")
    def auto_assign_public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignPublicIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipesInput")
    def custom_configure_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customConfigureRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipesInput")
    def custom_deploy_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customDeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArnInput")
    def custom_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdsInput")
    def custom_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipesInput")
    def custom_setup_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSetupRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipesInput")
    def custom_shutdown_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customShutdownRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipesInput")
    def custom_undeploy_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customUndeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdownInput")
    def drain_elb_on_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "drainElbOnShutdownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeInput")
    def ebs_volume_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksMemcachedLayerEbsVolume"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksMemcachedLayerEbsVolume"]], jsii.get(self, "ebsVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancerInput")
    def elastic_load_balancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticLoadBalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeoutInput")
    def instance_shutdown_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceShutdownTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackagesInput")
    def system_packages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "systemPackagesInput"))

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
    @jsii.member(jsii_name="useEbsOptimizedInstancesInput")
    def use_ebs_optimized_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useEbsOptimizedInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allocatedMemory")
    def allocated_memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "allocatedMemory"))

    @allocated_memory.setter
    def allocated_memory(self, value: jsii.Number) -> None:
        jsii.set(self, "allocatedMemory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIps")
    def auto_assign_elastic_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignElasticIps"))

    @auto_assign_elastic_ips.setter
    def auto_assign_elastic_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignElasticIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIps")
    def auto_assign_public_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignPublicIps"))

    @auto_assign_public_ips.setter
    def auto_assign_public_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignPublicIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoHealing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipes")
    def custom_configure_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customConfigureRecipes"))

    @custom_configure_recipes.setter
    def custom_configure_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customConfigureRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipes")
    def custom_deploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDeployRecipes"))

    @custom_deploy_recipes.setter
    def custom_deploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customDeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArn")
    def custom_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customInstanceProfileArn"))

    @custom_instance_profile_arn.setter
    def custom_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "customInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIds")
    def custom_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSecurityGroupIds"))

    @custom_security_group_ids.setter
    def custom_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipes")
    def custom_setup_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSetupRecipes"))

    @custom_setup_recipes.setter
    def custom_setup_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSetupRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipes")
    def custom_shutdown_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customShutdownRecipes"))

    @custom_shutdown_recipes.setter
    def custom_shutdown_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customShutdownRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipes")
    def custom_undeploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customUndeployRecipes"))

    @custom_undeploy_recipes.setter
    def custom_undeploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customUndeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdown")
    def drain_elb_on_shutdown(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "drainElbOnShutdown"))

    @drain_elb_on_shutdown.setter
    def drain_elb_on_shutdown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "drainElbOnShutdown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolume")
    def ebs_volume(self) -> typing.List["OpsworksMemcachedLayerEbsVolume"]:
        return typing.cast(typing.List["OpsworksMemcachedLayerEbsVolume"], jsii.get(self, "ebsVolume"))

    @ebs_volume.setter
    def ebs_volume(self, value: typing.List["OpsworksMemcachedLayerEbsVolume"]) -> None:
        jsii.set(self, "ebsVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancer")
    def elastic_load_balancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticLoadBalancer"))

    @elastic_load_balancer.setter
    def elastic_load_balancer(self, value: builtins.str) -> None:
        jsii.set(self, "elasticLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeout")
    def instance_shutdown_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceShutdownTimeout"))

    @instance_shutdown_timeout.setter
    def instance_shutdown_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceShutdownTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackages")
    def system_packages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "systemPackages"))

    @system_packages.setter
    def system_packages(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "systemPackages", value)

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
    @jsii.member(jsii_name="useEbsOptimizedInstances")
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useEbsOptimizedInstances"))

    @use_ebs_optimized_instances.setter
    def use_ebs_optimized_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useEbsOptimizedInstances", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksMemcachedLayerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "stack_id": "stackId",
        "allocated_memory": "allocatedMemory",
        "auto_assign_elastic_ips": "autoAssignElasticIps",
        "auto_assign_public_ips": "autoAssignPublicIps",
        "auto_healing": "autoHealing",
        "custom_configure_recipes": "customConfigureRecipes",
        "custom_deploy_recipes": "customDeployRecipes",
        "custom_instance_profile_arn": "customInstanceProfileArn",
        "custom_json": "customJson",
        "custom_security_group_ids": "customSecurityGroupIds",
        "custom_setup_recipes": "customSetupRecipes",
        "custom_shutdown_recipes": "customShutdownRecipes",
        "custom_undeploy_recipes": "customUndeployRecipes",
        "drain_elb_on_shutdown": "drainElbOnShutdown",
        "ebs_volume": "ebsVolume",
        "elastic_load_balancer": "elasticLoadBalancer",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_shutdown_timeout": "instanceShutdownTimeout",
        "name": "name",
        "system_packages": "systemPackages",
        "tags": "tags",
        "tags_all": "tagsAll",
        "use_ebs_optimized_instances": "useEbsOptimizedInstances",
    },
)
class OpsworksMemcachedLayerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        stack_id: builtins.str,
        allocated_memory: typing.Optional[jsii.Number] = None,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksMemcachedLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#stack_id OpsworksMemcachedLayer#stack_id}.
        :param allocated_memory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#allocated_memory OpsworksMemcachedLayer#allocated_memory}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#auto_assign_elastic_ips OpsworksMemcachedLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#auto_assign_public_ips OpsworksMemcachedLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#auto_healing OpsworksMemcachedLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_configure_recipes OpsworksMemcachedLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_deploy_recipes OpsworksMemcachedLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_instance_profile_arn OpsworksMemcachedLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_json OpsworksMemcachedLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_security_group_ids OpsworksMemcachedLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_setup_recipes OpsworksMemcachedLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_shutdown_recipes OpsworksMemcachedLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_undeploy_recipes OpsworksMemcachedLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#drain_elb_on_shutdown OpsworksMemcachedLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#ebs_volume OpsworksMemcachedLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#elastic_load_balancer OpsworksMemcachedLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#install_updates_on_boot OpsworksMemcachedLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#instance_shutdown_timeout OpsworksMemcachedLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#name OpsworksMemcachedLayer#name}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#system_packages OpsworksMemcachedLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#tags OpsworksMemcachedLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#tags_all OpsworksMemcachedLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#use_ebs_optimized_instances OpsworksMemcachedLayer#use_ebs_optimized_instances}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "stack_id": stack_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if allocated_memory is not None:
            self._values["allocated_memory"] = allocated_memory
        if auto_assign_elastic_ips is not None:
            self._values["auto_assign_elastic_ips"] = auto_assign_elastic_ips
        if auto_assign_public_ips is not None:
            self._values["auto_assign_public_ips"] = auto_assign_public_ips
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if custom_configure_recipes is not None:
            self._values["custom_configure_recipes"] = custom_configure_recipes
        if custom_deploy_recipes is not None:
            self._values["custom_deploy_recipes"] = custom_deploy_recipes
        if custom_instance_profile_arn is not None:
            self._values["custom_instance_profile_arn"] = custom_instance_profile_arn
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if custom_security_group_ids is not None:
            self._values["custom_security_group_ids"] = custom_security_group_ids
        if custom_setup_recipes is not None:
            self._values["custom_setup_recipes"] = custom_setup_recipes
        if custom_shutdown_recipes is not None:
            self._values["custom_shutdown_recipes"] = custom_shutdown_recipes
        if custom_undeploy_recipes is not None:
            self._values["custom_undeploy_recipes"] = custom_undeploy_recipes
        if drain_elb_on_shutdown is not None:
            self._values["drain_elb_on_shutdown"] = drain_elb_on_shutdown
        if ebs_volume is not None:
            self._values["ebs_volume"] = ebs_volume
        if elastic_load_balancer is not None:
            self._values["elastic_load_balancer"] = elastic_load_balancer
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_shutdown_timeout is not None:
            self._values["instance_shutdown_timeout"] = instance_shutdown_timeout
        if name is not None:
            self._values["name"] = name
        if system_packages is not None:
            self._values["system_packages"] = system_packages
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if use_ebs_optimized_instances is not None:
            self._values["use_ebs_optimized_instances"] = use_ebs_optimized_instances

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
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#stack_id OpsworksMemcachedLayer#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allocated_memory(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#allocated_memory OpsworksMemcachedLayer#allocated_memory}.'''
        result = self._values.get("allocated_memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def auto_assign_elastic_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#auto_assign_elastic_ips OpsworksMemcachedLayer#auto_assign_elastic_ips}.'''
        result = self._values.get("auto_assign_elastic_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_assign_public_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#auto_assign_public_ips OpsworksMemcachedLayer#auto_assign_public_ips}.'''
        result = self._values.get("auto_assign_public_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#auto_healing OpsworksMemcachedLayer#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def custom_configure_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_configure_recipes OpsworksMemcachedLayer#custom_configure_recipes}.'''
        result = self._values.get("custom_configure_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_deploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_deploy_recipes OpsworksMemcachedLayer#custom_deploy_recipes}.'''
        result = self._values.get("custom_deploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_instance_profile_arn OpsworksMemcachedLayer#custom_instance_profile_arn}.'''
        result = self._values.get("custom_instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_json OpsworksMemcachedLayer#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_security_group_ids OpsworksMemcachedLayer#custom_security_group_ids}.'''
        result = self._values.get("custom_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_setup_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_setup_recipes OpsworksMemcachedLayer#custom_setup_recipes}.'''
        result = self._values.get("custom_setup_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_shutdown_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_shutdown_recipes OpsworksMemcachedLayer#custom_shutdown_recipes}.'''
        result = self._values.get("custom_shutdown_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_undeploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#custom_undeploy_recipes OpsworksMemcachedLayer#custom_undeploy_recipes}.'''
        result = self._values.get("custom_undeploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drain_elb_on_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#drain_elb_on_shutdown OpsworksMemcachedLayer#drain_elb_on_shutdown}.'''
        result = self._values.get("drain_elb_on_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_volume(
        self,
    ) -> typing.Optional[typing.List["OpsworksMemcachedLayerEbsVolume"]]:
        '''ebs_volume block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#ebs_volume OpsworksMemcachedLayer#ebs_volume}
        '''
        result = self._values.get("ebs_volume")
        return typing.cast(typing.Optional[typing.List["OpsworksMemcachedLayerEbsVolume"]], result)

    @builtins.property
    def elastic_load_balancer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#elastic_load_balancer OpsworksMemcachedLayer#elastic_load_balancer}.'''
        result = self._values.get("elastic_load_balancer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#install_updates_on_boot OpsworksMemcachedLayer#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_shutdown_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#instance_shutdown_timeout OpsworksMemcachedLayer#instance_shutdown_timeout}.'''
        result = self._values.get("instance_shutdown_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#name OpsworksMemcachedLayer#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def system_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#system_packages OpsworksMemcachedLayer#system_packages}.'''
        result = self._values.get("system_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#tags OpsworksMemcachedLayer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#tags_all OpsworksMemcachedLayer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#use_ebs_optimized_instances OpsworksMemcachedLayer#use_ebs_optimized_instances}.'''
        result = self._values.get("use_ebs_optimized_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksMemcachedLayerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksMemcachedLayerEbsVolume",
    jsii_struct_bases=[],
    name_mapping={
        "mount_point": "mountPoint",
        "number_of_disks": "numberOfDisks",
        "size": "size",
        "encrypted": "encrypted",
        "iops": "iops",
        "raid_level": "raidLevel",
        "type": "type",
    },
)
class OpsworksMemcachedLayerEbsVolume:
    def __init__(
        self,
        *,
        mount_point: builtins.str,
        number_of_disks: jsii.Number,
        size: jsii.Number,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        raid_level: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mount_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#mount_point OpsworksMemcachedLayer#mount_point}.
        :param number_of_disks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#number_of_disks OpsworksMemcachedLayer#number_of_disks}.
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#size OpsworksMemcachedLayer#size}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#encrypted OpsworksMemcachedLayer#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#iops OpsworksMemcachedLayer#iops}.
        :param raid_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#raid_level OpsworksMemcachedLayer#raid_level}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#type OpsworksMemcachedLayer#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mount_point": mount_point,
            "number_of_disks": number_of_disks,
            "size": size,
        }
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if raid_level is not None:
            self._values["raid_level"] = raid_level
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#mount_point OpsworksMemcachedLayer#mount_point}.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_disks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#number_of_disks OpsworksMemcachedLayer#number_of_disks}.'''
        result = self._values.get("number_of_disks")
        assert result is not None, "Required property 'number_of_disks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#size OpsworksMemcachedLayer#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#encrypted OpsworksMemcachedLayer#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#iops OpsworksMemcachedLayer#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raid_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#raid_level OpsworksMemcachedLayer#raid_level}.'''
        result = self._values.get("raid_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_memcached_layer#type OpsworksMemcachedLayer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksMemcachedLayerEbsVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksMysqlLayer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksMysqlLayer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer aws_opsworks_mysql_layer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksMysqlLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        root_password: typing.Optional[builtins.str] = None,
        root_password_on_all_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer aws_opsworks_mysql_layer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#stack_id OpsworksMysqlLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#auto_assign_elastic_ips OpsworksMysqlLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#auto_assign_public_ips OpsworksMysqlLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#auto_healing OpsworksMysqlLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_configure_recipes OpsworksMysqlLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_deploy_recipes OpsworksMysqlLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_instance_profile_arn OpsworksMysqlLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_json OpsworksMysqlLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_security_group_ids OpsworksMysqlLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_setup_recipes OpsworksMysqlLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_shutdown_recipes OpsworksMysqlLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_undeploy_recipes OpsworksMysqlLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#drain_elb_on_shutdown OpsworksMysqlLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#ebs_volume OpsworksMysqlLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#elastic_load_balancer OpsworksMysqlLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#install_updates_on_boot OpsworksMysqlLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#instance_shutdown_timeout OpsworksMysqlLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#name OpsworksMysqlLayer#name}.
        :param root_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#root_password OpsworksMysqlLayer#root_password}.
        :param root_password_on_all_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#root_password_on_all_instances OpsworksMysqlLayer#root_password_on_all_instances}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#system_packages OpsworksMysqlLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#tags OpsworksMysqlLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#tags_all OpsworksMysqlLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#use_ebs_optimized_instances OpsworksMysqlLayer#use_ebs_optimized_instances}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksMysqlLayerConfig(
            stack_id=stack_id,
            auto_assign_elastic_ips=auto_assign_elastic_ips,
            auto_assign_public_ips=auto_assign_public_ips,
            auto_healing=auto_healing,
            custom_configure_recipes=custom_configure_recipes,
            custom_deploy_recipes=custom_deploy_recipes,
            custom_instance_profile_arn=custom_instance_profile_arn,
            custom_json=custom_json,
            custom_security_group_ids=custom_security_group_ids,
            custom_setup_recipes=custom_setup_recipes,
            custom_shutdown_recipes=custom_shutdown_recipes,
            custom_undeploy_recipes=custom_undeploy_recipes,
            drain_elb_on_shutdown=drain_elb_on_shutdown,
            ebs_volume=ebs_volume,
            elastic_load_balancer=elastic_load_balancer,
            install_updates_on_boot=install_updates_on_boot,
            instance_shutdown_timeout=instance_shutdown_timeout,
            name=name,
            root_password=root_password,
            root_password_on_all_instances=root_password_on_all_instances,
            system_packages=system_packages,
            tags=tags,
            tags_all=tags_all,
            use_ebs_optimized_instances=use_ebs_optimized_instances,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAutoAssignElasticIps")
    def reset_auto_assign_elastic_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignElasticIps", []))

    @jsii.member(jsii_name="resetAutoAssignPublicIps")
    def reset_auto_assign_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignPublicIps", []))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetCustomConfigureRecipes")
    def reset_custom_configure_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomConfigureRecipes", []))

    @jsii.member(jsii_name="resetCustomDeployRecipes")
    def reset_custom_deploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDeployRecipes", []))

    @jsii.member(jsii_name="resetCustomInstanceProfileArn")
    def reset_custom_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomInstanceProfileArn", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetCustomSecurityGroupIds")
    def reset_custom_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupIds", []))

    @jsii.member(jsii_name="resetCustomSetupRecipes")
    def reset_custom_setup_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSetupRecipes", []))

    @jsii.member(jsii_name="resetCustomShutdownRecipes")
    def reset_custom_shutdown_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomShutdownRecipes", []))

    @jsii.member(jsii_name="resetCustomUndeployRecipes")
    def reset_custom_undeploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUndeployRecipes", []))

    @jsii.member(jsii_name="resetDrainElbOnShutdown")
    def reset_drain_elb_on_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainElbOnShutdown", []))

    @jsii.member(jsii_name="resetEbsVolume")
    def reset_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolume", []))

    @jsii.member(jsii_name="resetElasticLoadBalancer")
    def reset_elastic_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticLoadBalancer", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceShutdownTimeout")
    def reset_instance_shutdown_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceShutdownTimeout", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetRootPassword")
    def reset_root_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootPassword", []))

    @jsii.member(jsii_name="resetRootPasswordOnAllInstances")
    def reset_root_password_on_all_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRootPasswordOnAllInstances", []))

    @jsii.member(jsii_name="resetSystemPackages")
    def reset_system_packages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemPackages", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUseEbsOptimizedInstances")
    def reset_use_ebs_optimized_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseEbsOptimizedInstances", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIpsInput")
    def auto_assign_elastic_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignElasticIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIpsInput")
    def auto_assign_public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignPublicIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipesInput")
    def custom_configure_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customConfigureRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipesInput")
    def custom_deploy_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customDeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArnInput")
    def custom_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdsInput")
    def custom_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipesInput")
    def custom_setup_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSetupRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipesInput")
    def custom_shutdown_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customShutdownRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipesInput")
    def custom_undeploy_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customUndeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdownInput")
    def drain_elb_on_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "drainElbOnShutdownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeInput")
    def ebs_volume_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksMysqlLayerEbsVolume"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksMysqlLayerEbsVolume"]], jsii.get(self, "ebsVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancerInput")
    def elastic_load_balancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticLoadBalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeoutInput")
    def instance_shutdown_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceShutdownTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootPasswordInput")
    def root_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rootPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootPasswordOnAllInstancesInput")
    def root_password_on_all_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "rootPasswordOnAllInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackagesInput")
    def system_packages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "systemPackagesInput"))

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
    @jsii.member(jsii_name="useEbsOptimizedInstancesInput")
    def use_ebs_optimized_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useEbsOptimizedInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIps")
    def auto_assign_elastic_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignElasticIps"))

    @auto_assign_elastic_ips.setter
    def auto_assign_elastic_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignElasticIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIps")
    def auto_assign_public_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignPublicIps"))

    @auto_assign_public_ips.setter
    def auto_assign_public_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignPublicIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoHealing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipes")
    def custom_configure_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customConfigureRecipes"))

    @custom_configure_recipes.setter
    def custom_configure_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customConfigureRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipes")
    def custom_deploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDeployRecipes"))

    @custom_deploy_recipes.setter
    def custom_deploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customDeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArn")
    def custom_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customInstanceProfileArn"))

    @custom_instance_profile_arn.setter
    def custom_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "customInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIds")
    def custom_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSecurityGroupIds"))

    @custom_security_group_ids.setter
    def custom_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipes")
    def custom_setup_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSetupRecipes"))

    @custom_setup_recipes.setter
    def custom_setup_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSetupRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipes")
    def custom_shutdown_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customShutdownRecipes"))

    @custom_shutdown_recipes.setter
    def custom_shutdown_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customShutdownRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipes")
    def custom_undeploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customUndeployRecipes"))

    @custom_undeploy_recipes.setter
    def custom_undeploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customUndeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdown")
    def drain_elb_on_shutdown(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "drainElbOnShutdown"))

    @drain_elb_on_shutdown.setter
    def drain_elb_on_shutdown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "drainElbOnShutdown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolume")
    def ebs_volume(self) -> typing.List["OpsworksMysqlLayerEbsVolume"]:
        return typing.cast(typing.List["OpsworksMysqlLayerEbsVolume"], jsii.get(self, "ebsVolume"))

    @ebs_volume.setter
    def ebs_volume(self, value: typing.List["OpsworksMysqlLayerEbsVolume"]) -> None:
        jsii.set(self, "ebsVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancer")
    def elastic_load_balancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticLoadBalancer"))

    @elastic_load_balancer.setter
    def elastic_load_balancer(self, value: builtins.str) -> None:
        jsii.set(self, "elasticLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeout")
    def instance_shutdown_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceShutdownTimeout"))

    @instance_shutdown_timeout.setter
    def instance_shutdown_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceShutdownTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootPassword")
    def root_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rootPassword"))

    @root_password.setter
    def root_password(self, value: builtins.str) -> None:
        jsii.set(self, "rootPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootPasswordOnAllInstances")
    def root_password_on_all_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "rootPasswordOnAllInstances"))

    @root_password_on_all_instances.setter
    def root_password_on_all_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "rootPasswordOnAllInstances", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackages")
    def system_packages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "systemPackages"))

    @system_packages.setter
    def system_packages(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "systemPackages", value)

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
    @jsii.member(jsii_name="useEbsOptimizedInstances")
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useEbsOptimizedInstances"))

    @use_ebs_optimized_instances.setter
    def use_ebs_optimized_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useEbsOptimizedInstances", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksMysqlLayerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "stack_id": "stackId",
        "auto_assign_elastic_ips": "autoAssignElasticIps",
        "auto_assign_public_ips": "autoAssignPublicIps",
        "auto_healing": "autoHealing",
        "custom_configure_recipes": "customConfigureRecipes",
        "custom_deploy_recipes": "customDeployRecipes",
        "custom_instance_profile_arn": "customInstanceProfileArn",
        "custom_json": "customJson",
        "custom_security_group_ids": "customSecurityGroupIds",
        "custom_setup_recipes": "customSetupRecipes",
        "custom_shutdown_recipes": "customShutdownRecipes",
        "custom_undeploy_recipes": "customUndeployRecipes",
        "drain_elb_on_shutdown": "drainElbOnShutdown",
        "ebs_volume": "ebsVolume",
        "elastic_load_balancer": "elasticLoadBalancer",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_shutdown_timeout": "instanceShutdownTimeout",
        "name": "name",
        "root_password": "rootPassword",
        "root_password_on_all_instances": "rootPasswordOnAllInstances",
        "system_packages": "systemPackages",
        "tags": "tags",
        "tags_all": "tagsAll",
        "use_ebs_optimized_instances": "useEbsOptimizedInstances",
    },
)
class OpsworksMysqlLayerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksMysqlLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        root_password: typing.Optional[builtins.str] = None,
        root_password_on_all_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#stack_id OpsworksMysqlLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#auto_assign_elastic_ips OpsworksMysqlLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#auto_assign_public_ips OpsworksMysqlLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#auto_healing OpsworksMysqlLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_configure_recipes OpsworksMysqlLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_deploy_recipes OpsworksMysqlLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_instance_profile_arn OpsworksMysqlLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_json OpsworksMysqlLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_security_group_ids OpsworksMysqlLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_setup_recipes OpsworksMysqlLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_shutdown_recipes OpsworksMysqlLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_undeploy_recipes OpsworksMysqlLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#drain_elb_on_shutdown OpsworksMysqlLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#ebs_volume OpsworksMysqlLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#elastic_load_balancer OpsworksMysqlLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#install_updates_on_boot OpsworksMysqlLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#instance_shutdown_timeout OpsworksMysqlLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#name OpsworksMysqlLayer#name}.
        :param root_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#root_password OpsworksMysqlLayer#root_password}.
        :param root_password_on_all_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#root_password_on_all_instances OpsworksMysqlLayer#root_password_on_all_instances}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#system_packages OpsworksMysqlLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#tags OpsworksMysqlLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#tags_all OpsworksMysqlLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#use_ebs_optimized_instances OpsworksMysqlLayer#use_ebs_optimized_instances}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "stack_id": stack_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auto_assign_elastic_ips is not None:
            self._values["auto_assign_elastic_ips"] = auto_assign_elastic_ips
        if auto_assign_public_ips is not None:
            self._values["auto_assign_public_ips"] = auto_assign_public_ips
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if custom_configure_recipes is not None:
            self._values["custom_configure_recipes"] = custom_configure_recipes
        if custom_deploy_recipes is not None:
            self._values["custom_deploy_recipes"] = custom_deploy_recipes
        if custom_instance_profile_arn is not None:
            self._values["custom_instance_profile_arn"] = custom_instance_profile_arn
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if custom_security_group_ids is not None:
            self._values["custom_security_group_ids"] = custom_security_group_ids
        if custom_setup_recipes is not None:
            self._values["custom_setup_recipes"] = custom_setup_recipes
        if custom_shutdown_recipes is not None:
            self._values["custom_shutdown_recipes"] = custom_shutdown_recipes
        if custom_undeploy_recipes is not None:
            self._values["custom_undeploy_recipes"] = custom_undeploy_recipes
        if drain_elb_on_shutdown is not None:
            self._values["drain_elb_on_shutdown"] = drain_elb_on_shutdown
        if ebs_volume is not None:
            self._values["ebs_volume"] = ebs_volume
        if elastic_load_balancer is not None:
            self._values["elastic_load_balancer"] = elastic_load_balancer
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_shutdown_timeout is not None:
            self._values["instance_shutdown_timeout"] = instance_shutdown_timeout
        if name is not None:
            self._values["name"] = name
        if root_password is not None:
            self._values["root_password"] = root_password
        if root_password_on_all_instances is not None:
            self._values["root_password_on_all_instances"] = root_password_on_all_instances
        if system_packages is not None:
            self._values["system_packages"] = system_packages
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if use_ebs_optimized_instances is not None:
            self._values["use_ebs_optimized_instances"] = use_ebs_optimized_instances

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
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#stack_id OpsworksMysqlLayer#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_assign_elastic_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#auto_assign_elastic_ips OpsworksMysqlLayer#auto_assign_elastic_ips}.'''
        result = self._values.get("auto_assign_elastic_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_assign_public_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#auto_assign_public_ips OpsworksMysqlLayer#auto_assign_public_ips}.'''
        result = self._values.get("auto_assign_public_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#auto_healing OpsworksMysqlLayer#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def custom_configure_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_configure_recipes OpsworksMysqlLayer#custom_configure_recipes}.'''
        result = self._values.get("custom_configure_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_deploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_deploy_recipes OpsworksMysqlLayer#custom_deploy_recipes}.'''
        result = self._values.get("custom_deploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_instance_profile_arn OpsworksMysqlLayer#custom_instance_profile_arn}.'''
        result = self._values.get("custom_instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_json OpsworksMysqlLayer#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_security_group_ids OpsworksMysqlLayer#custom_security_group_ids}.'''
        result = self._values.get("custom_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_setup_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_setup_recipes OpsworksMysqlLayer#custom_setup_recipes}.'''
        result = self._values.get("custom_setup_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_shutdown_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_shutdown_recipes OpsworksMysqlLayer#custom_shutdown_recipes}.'''
        result = self._values.get("custom_shutdown_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_undeploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#custom_undeploy_recipes OpsworksMysqlLayer#custom_undeploy_recipes}.'''
        result = self._values.get("custom_undeploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drain_elb_on_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#drain_elb_on_shutdown OpsworksMysqlLayer#drain_elb_on_shutdown}.'''
        result = self._values.get("drain_elb_on_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_volume(self) -> typing.Optional[typing.List["OpsworksMysqlLayerEbsVolume"]]:
        '''ebs_volume block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#ebs_volume OpsworksMysqlLayer#ebs_volume}
        '''
        result = self._values.get("ebs_volume")
        return typing.cast(typing.Optional[typing.List["OpsworksMysqlLayerEbsVolume"]], result)

    @builtins.property
    def elastic_load_balancer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#elastic_load_balancer OpsworksMysqlLayer#elastic_load_balancer}.'''
        result = self._values.get("elastic_load_balancer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#install_updates_on_boot OpsworksMysqlLayer#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_shutdown_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#instance_shutdown_timeout OpsworksMysqlLayer#instance_shutdown_timeout}.'''
        result = self._values.get("instance_shutdown_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#name OpsworksMysqlLayer#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def root_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#root_password OpsworksMysqlLayer#root_password}.'''
        result = self._values.get("root_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def root_password_on_all_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#root_password_on_all_instances OpsworksMysqlLayer#root_password_on_all_instances}.'''
        result = self._values.get("root_password_on_all_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def system_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#system_packages OpsworksMysqlLayer#system_packages}.'''
        result = self._values.get("system_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#tags OpsworksMysqlLayer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#tags_all OpsworksMysqlLayer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#use_ebs_optimized_instances OpsworksMysqlLayer#use_ebs_optimized_instances}.'''
        result = self._values.get("use_ebs_optimized_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksMysqlLayerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksMysqlLayerEbsVolume",
    jsii_struct_bases=[],
    name_mapping={
        "mount_point": "mountPoint",
        "number_of_disks": "numberOfDisks",
        "size": "size",
        "encrypted": "encrypted",
        "iops": "iops",
        "raid_level": "raidLevel",
        "type": "type",
    },
)
class OpsworksMysqlLayerEbsVolume:
    def __init__(
        self,
        *,
        mount_point: builtins.str,
        number_of_disks: jsii.Number,
        size: jsii.Number,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        raid_level: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mount_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#mount_point OpsworksMysqlLayer#mount_point}.
        :param number_of_disks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#number_of_disks OpsworksMysqlLayer#number_of_disks}.
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#size OpsworksMysqlLayer#size}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#encrypted OpsworksMysqlLayer#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#iops OpsworksMysqlLayer#iops}.
        :param raid_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#raid_level OpsworksMysqlLayer#raid_level}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#type OpsworksMysqlLayer#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mount_point": mount_point,
            "number_of_disks": number_of_disks,
            "size": size,
        }
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if raid_level is not None:
            self._values["raid_level"] = raid_level
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#mount_point OpsworksMysqlLayer#mount_point}.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_disks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#number_of_disks OpsworksMysqlLayer#number_of_disks}.'''
        result = self._values.get("number_of_disks")
        assert result is not None, "Required property 'number_of_disks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#size OpsworksMysqlLayer#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#encrypted OpsworksMysqlLayer#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#iops OpsworksMysqlLayer#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raid_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#raid_level OpsworksMysqlLayer#raid_level}.'''
        result = self._values.get("raid_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_mysql_layer#type OpsworksMysqlLayer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksMysqlLayerEbsVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksNodejsAppLayer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksNodejsAppLayer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer aws_opsworks_nodejs_app_layer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksNodejsAppLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        nodejs_version: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer aws_opsworks_nodejs_app_layer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#stack_id OpsworksNodejsAppLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#auto_assign_elastic_ips OpsworksNodejsAppLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#auto_assign_public_ips OpsworksNodejsAppLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#auto_healing OpsworksNodejsAppLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_configure_recipes OpsworksNodejsAppLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_deploy_recipes OpsworksNodejsAppLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_instance_profile_arn OpsworksNodejsAppLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_json OpsworksNodejsAppLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_security_group_ids OpsworksNodejsAppLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_setup_recipes OpsworksNodejsAppLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_shutdown_recipes OpsworksNodejsAppLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_undeploy_recipes OpsworksNodejsAppLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#drain_elb_on_shutdown OpsworksNodejsAppLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#ebs_volume OpsworksNodejsAppLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#elastic_load_balancer OpsworksNodejsAppLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#install_updates_on_boot OpsworksNodejsAppLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#instance_shutdown_timeout OpsworksNodejsAppLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#name OpsworksNodejsAppLayer#name}.
        :param nodejs_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#nodejs_version OpsworksNodejsAppLayer#nodejs_version}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#system_packages OpsworksNodejsAppLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#tags OpsworksNodejsAppLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#tags_all OpsworksNodejsAppLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#use_ebs_optimized_instances OpsworksNodejsAppLayer#use_ebs_optimized_instances}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksNodejsAppLayerConfig(
            stack_id=stack_id,
            auto_assign_elastic_ips=auto_assign_elastic_ips,
            auto_assign_public_ips=auto_assign_public_ips,
            auto_healing=auto_healing,
            custom_configure_recipes=custom_configure_recipes,
            custom_deploy_recipes=custom_deploy_recipes,
            custom_instance_profile_arn=custom_instance_profile_arn,
            custom_json=custom_json,
            custom_security_group_ids=custom_security_group_ids,
            custom_setup_recipes=custom_setup_recipes,
            custom_shutdown_recipes=custom_shutdown_recipes,
            custom_undeploy_recipes=custom_undeploy_recipes,
            drain_elb_on_shutdown=drain_elb_on_shutdown,
            ebs_volume=ebs_volume,
            elastic_load_balancer=elastic_load_balancer,
            install_updates_on_boot=install_updates_on_boot,
            instance_shutdown_timeout=instance_shutdown_timeout,
            name=name,
            nodejs_version=nodejs_version,
            system_packages=system_packages,
            tags=tags,
            tags_all=tags_all,
            use_ebs_optimized_instances=use_ebs_optimized_instances,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAutoAssignElasticIps")
    def reset_auto_assign_elastic_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignElasticIps", []))

    @jsii.member(jsii_name="resetAutoAssignPublicIps")
    def reset_auto_assign_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignPublicIps", []))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetCustomConfigureRecipes")
    def reset_custom_configure_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomConfigureRecipes", []))

    @jsii.member(jsii_name="resetCustomDeployRecipes")
    def reset_custom_deploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDeployRecipes", []))

    @jsii.member(jsii_name="resetCustomInstanceProfileArn")
    def reset_custom_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomInstanceProfileArn", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetCustomSecurityGroupIds")
    def reset_custom_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupIds", []))

    @jsii.member(jsii_name="resetCustomSetupRecipes")
    def reset_custom_setup_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSetupRecipes", []))

    @jsii.member(jsii_name="resetCustomShutdownRecipes")
    def reset_custom_shutdown_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomShutdownRecipes", []))

    @jsii.member(jsii_name="resetCustomUndeployRecipes")
    def reset_custom_undeploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUndeployRecipes", []))

    @jsii.member(jsii_name="resetDrainElbOnShutdown")
    def reset_drain_elb_on_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainElbOnShutdown", []))

    @jsii.member(jsii_name="resetEbsVolume")
    def reset_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolume", []))

    @jsii.member(jsii_name="resetElasticLoadBalancer")
    def reset_elastic_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticLoadBalancer", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceShutdownTimeout")
    def reset_instance_shutdown_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceShutdownTimeout", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNodejsVersion")
    def reset_nodejs_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodejsVersion", []))

    @jsii.member(jsii_name="resetSystemPackages")
    def reset_system_packages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemPackages", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUseEbsOptimizedInstances")
    def reset_use_ebs_optimized_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseEbsOptimizedInstances", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIpsInput")
    def auto_assign_elastic_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignElasticIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIpsInput")
    def auto_assign_public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignPublicIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipesInput")
    def custom_configure_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customConfigureRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipesInput")
    def custom_deploy_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customDeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArnInput")
    def custom_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdsInput")
    def custom_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipesInput")
    def custom_setup_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSetupRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipesInput")
    def custom_shutdown_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customShutdownRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipesInput")
    def custom_undeploy_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customUndeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdownInput")
    def drain_elb_on_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "drainElbOnShutdownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeInput")
    def ebs_volume_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksNodejsAppLayerEbsVolume"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksNodejsAppLayerEbsVolume"]], jsii.get(self, "ebsVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancerInput")
    def elastic_load_balancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticLoadBalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeoutInput")
    def instance_shutdown_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceShutdownTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodejsVersionInput")
    def nodejs_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodejsVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackagesInput")
    def system_packages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "systemPackagesInput"))

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
    @jsii.member(jsii_name="useEbsOptimizedInstancesInput")
    def use_ebs_optimized_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useEbsOptimizedInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIps")
    def auto_assign_elastic_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignElasticIps"))

    @auto_assign_elastic_ips.setter
    def auto_assign_elastic_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignElasticIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIps")
    def auto_assign_public_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignPublicIps"))

    @auto_assign_public_ips.setter
    def auto_assign_public_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignPublicIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoHealing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipes")
    def custom_configure_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customConfigureRecipes"))

    @custom_configure_recipes.setter
    def custom_configure_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customConfigureRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipes")
    def custom_deploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDeployRecipes"))

    @custom_deploy_recipes.setter
    def custom_deploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customDeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArn")
    def custom_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customInstanceProfileArn"))

    @custom_instance_profile_arn.setter
    def custom_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "customInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIds")
    def custom_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSecurityGroupIds"))

    @custom_security_group_ids.setter
    def custom_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipes")
    def custom_setup_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSetupRecipes"))

    @custom_setup_recipes.setter
    def custom_setup_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSetupRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipes")
    def custom_shutdown_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customShutdownRecipes"))

    @custom_shutdown_recipes.setter
    def custom_shutdown_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customShutdownRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipes")
    def custom_undeploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customUndeployRecipes"))

    @custom_undeploy_recipes.setter
    def custom_undeploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customUndeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdown")
    def drain_elb_on_shutdown(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "drainElbOnShutdown"))

    @drain_elb_on_shutdown.setter
    def drain_elb_on_shutdown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "drainElbOnShutdown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolume")
    def ebs_volume(self) -> typing.List["OpsworksNodejsAppLayerEbsVolume"]:
        return typing.cast(typing.List["OpsworksNodejsAppLayerEbsVolume"], jsii.get(self, "ebsVolume"))

    @ebs_volume.setter
    def ebs_volume(self, value: typing.List["OpsworksNodejsAppLayerEbsVolume"]) -> None:
        jsii.set(self, "ebsVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancer")
    def elastic_load_balancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticLoadBalancer"))

    @elastic_load_balancer.setter
    def elastic_load_balancer(self, value: builtins.str) -> None:
        jsii.set(self, "elasticLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeout")
    def instance_shutdown_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceShutdownTimeout"))

    @instance_shutdown_timeout.setter
    def instance_shutdown_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceShutdownTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodejsVersion")
    def nodejs_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodejsVersion"))

    @nodejs_version.setter
    def nodejs_version(self, value: builtins.str) -> None:
        jsii.set(self, "nodejsVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackages")
    def system_packages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "systemPackages"))

    @system_packages.setter
    def system_packages(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "systemPackages", value)

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
    @jsii.member(jsii_name="useEbsOptimizedInstances")
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useEbsOptimizedInstances"))

    @use_ebs_optimized_instances.setter
    def use_ebs_optimized_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useEbsOptimizedInstances", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksNodejsAppLayerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "stack_id": "stackId",
        "auto_assign_elastic_ips": "autoAssignElasticIps",
        "auto_assign_public_ips": "autoAssignPublicIps",
        "auto_healing": "autoHealing",
        "custom_configure_recipes": "customConfigureRecipes",
        "custom_deploy_recipes": "customDeployRecipes",
        "custom_instance_profile_arn": "customInstanceProfileArn",
        "custom_json": "customJson",
        "custom_security_group_ids": "customSecurityGroupIds",
        "custom_setup_recipes": "customSetupRecipes",
        "custom_shutdown_recipes": "customShutdownRecipes",
        "custom_undeploy_recipes": "customUndeployRecipes",
        "drain_elb_on_shutdown": "drainElbOnShutdown",
        "ebs_volume": "ebsVolume",
        "elastic_load_balancer": "elasticLoadBalancer",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_shutdown_timeout": "instanceShutdownTimeout",
        "name": "name",
        "nodejs_version": "nodejsVersion",
        "system_packages": "systemPackages",
        "tags": "tags",
        "tags_all": "tagsAll",
        "use_ebs_optimized_instances": "useEbsOptimizedInstances",
    },
)
class OpsworksNodejsAppLayerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksNodejsAppLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        nodejs_version: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#stack_id OpsworksNodejsAppLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#auto_assign_elastic_ips OpsworksNodejsAppLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#auto_assign_public_ips OpsworksNodejsAppLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#auto_healing OpsworksNodejsAppLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_configure_recipes OpsworksNodejsAppLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_deploy_recipes OpsworksNodejsAppLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_instance_profile_arn OpsworksNodejsAppLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_json OpsworksNodejsAppLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_security_group_ids OpsworksNodejsAppLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_setup_recipes OpsworksNodejsAppLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_shutdown_recipes OpsworksNodejsAppLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_undeploy_recipes OpsworksNodejsAppLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#drain_elb_on_shutdown OpsworksNodejsAppLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#ebs_volume OpsworksNodejsAppLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#elastic_load_balancer OpsworksNodejsAppLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#install_updates_on_boot OpsworksNodejsAppLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#instance_shutdown_timeout OpsworksNodejsAppLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#name OpsworksNodejsAppLayer#name}.
        :param nodejs_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#nodejs_version OpsworksNodejsAppLayer#nodejs_version}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#system_packages OpsworksNodejsAppLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#tags OpsworksNodejsAppLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#tags_all OpsworksNodejsAppLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#use_ebs_optimized_instances OpsworksNodejsAppLayer#use_ebs_optimized_instances}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "stack_id": stack_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auto_assign_elastic_ips is not None:
            self._values["auto_assign_elastic_ips"] = auto_assign_elastic_ips
        if auto_assign_public_ips is not None:
            self._values["auto_assign_public_ips"] = auto_assign_public_ips
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if custom_configure_recipes is not None:
            self._values["custom_configure_recipes"] = custom_configure_recipes
        if custom_deploy_recipes is not None:
            self._values["custom_deploy_recipes"] = custom_deploy_recipes
        if custom_instance_profile_arn is not None:
            self._values["custom_instance_profile_arn"] = custom_instance_profile_arn
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if custom_security_group_ids is not None:
            self._values["custom_security_group_ids"] = custom_security_group_ids
        if custom_setup_recipes is not None:
            self._values["custom_setup_recipes"] = custom_setup_recipes
        if custom_shutdown_recipes is not None:
            self._values["custom_shutdown_recipes"] = custom_shutdown_recipes
        if custom_undeploy_recipes is not None:
            self._values["custom_undeploy_recipes"] = custom_undeploy_recipes
        if drain_elb_on_shutdown is not None:
            self._values["drain_elb_on_shutdown"] = drain_elb_on_shutdown
        if ebs_volume is not None:
            self._values["ebs_volume"] = ebs_volume
        if elastic_load_balancer is not None:
            self._values["elastic_load_balancer"] = elastic_load_balancer
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_shutdown_timeout is not None:
            self._values["instance_shutdown_timeout"] = instance_shutdown_timeout
        if name is not None:
            self._values["name"] = name
        if nodejs_version is not None:
            self._values["nodejs_version"] = nodejs_version
        if system_packages is not None:
            self._values["system_packages"] = system_packages
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if use_ebs_optimized_instances is not None:
            self._values["use_ebs_optimized_instances"] = use_ebs_optimized_instances

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
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#stack_id OpsworksNodejsAppLayer#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_assign_elastic_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#auto_assign_elastic_ips OpsworksNodejsAppLayer#auto_assign_elastic_ips}.'''
        result = self._values.get("auto_assign_elastic_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_assign_public_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#auto_assign_public_ips OpsworksNodejsAppLayer#auto_assign_public_ips}.'''
        result = self._values.get("auto_assign_public_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#auto_healing OpsworksNodejsAppLayer#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def custom_configure_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_configure_recipes OpsworksNodejsAppLayer#custom_configure_recipes}.'''
        result = self._values.get("custom_configure_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_deploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_deploy_recipes OpsworksNodejsAppLayer#custom_deploy_recipes}.'''
        result = self._values.get("custom_deploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_instance_profile_arn OpsworksNodejsAppLayer#custom_instance_profile_arn}.'''
        result = self._values.get("custom_instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_json OpsworksNodejsAppLayer#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_security_group_ids OpsworksNodejsAppLayer#custom_security_group_ids}.'''
        result = self._values.get("custom_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_setup_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_setup_recipes OpsworksNodejsAppLayer#custom_setup_recipes}.'''
        result = self._values.get("custom_setup_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_shutdown_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_shutdown_recipes OpsworksNodejsAppLayer#custom_shutdown_recipes}.'''
        result = self._values.get("custom_shutdown_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_undeploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#custom_undeploy_recipes OpsworksNodejsAppLayer#custom_undeploy_recipes}.'''
        result = self._values.get("custom_undeploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drain_elb_on_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#drain_elb_on_shutdown OpsworksNodejsAppLayer#drain_elb_on_shutdown}.'''
        result = self._values.get("drain_elb_on_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_volume(
        self,
    ) -> typing.Optional[typing.List["OpsworksNodejsAppLayerEbsVolume"]]:
        '''ebs_volume block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#ebs_volume OpsworksNodejsAppLayer#ebs_volume}
        '''
        result = self._values.get("ebs_volume")
        return typing.cast(typing.Optional[typing.List["OpsworksNodejsAppLayerEbsVolume"]], result)

    @builtins.property
    def elastic_load_balancer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#elastic_load_balancer OpsworksNodejsAppLayer#elastic_load_balancer}.'''
        result = self._values.get("elastic_load_balancer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#install_updates_on_boot OpsworksNodejsAppLayer#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_shutdown_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#instance_shutdown_timeout OpsworksNodejsAppLayer#instance_shutdown_timeout}.'''
        result = self._values.get("instance_shutdown_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#name OpsworksNodejsAppLayer#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nodejs_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#nodejs_version OpsworksNodejsAppLayer#nodejs_version}.'''
        result = self._values.get("nodejs_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def system_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#system_packages OpsworksNodejsAppLayer#system_packages}.'''
        result = self._values.get("system_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#tags OpsworksNodejsAppLayer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#tags_all OpsworksNodejsAppLayer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#use_ebs_optimized_instances OpsworksNodejsAppLayer#use_ebs_optimized_instances}.'''
        result = self._values.get("use_ebs_optimized_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksNodejsAppLayerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksNodejsAppLayerEbsVolume",
    jsii_struct_bases=[],
    name_mapping={
        "mount_point": "mountPoint",
        "number_of_disks": "numberOfDisks",
        "size": "size",
        "encrypted": "encrypted",
        "iops": "iops",
        "raid_level": "raidLevel",
        "type": "type",
    },
)
class OpsworksNodejsAppLayerEbsVolume:
    def __init__(
        self,
        *,
        mount_point: builtins.str,
        number_of_disks: jsii.Number,
        size: jsii.Number,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        raid_level: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mount_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#mount_point OpsworksNodejsAppLayer#mount_point}.
        :param number_of_disks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#number_of_disks OpsworksNodejsAppLayer#number_of_disks}.
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#size OpsworksNodejsAppLayer#size}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#encrypted OpsworksNodejsAppLayer#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#iops OpsworksNodejsAppLayer#iops}.
        :param raid_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#raid_level OpsworksNodejsAppLayer#raid_level}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#type OpsworksNodejsAppLayer#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mount_point": mount_point,
            "number_of_disks": number_of_disks,
            "size": size,
        }
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if raid_level is not None:
            self._values["raid_level"] = raid_level
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#mount_point OpsworksNodejsAppLayer#mount_point}.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_disks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#number_of_disks OpsworksNodejsAppLayer#number_of_disks}.'''
        result = self._values.get("number_of_disks")
        assert result is not None, "Required property 'number_of_disks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#size OpsworksNodejsAppLayer#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#encrypted OpsworksNodejsAppLayer#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#iops OpsworksNodejsAppLayer#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raid_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#raid_level OpsworksNodejsAppLayer#raid_level}.'''
        result = self._values.get("raid_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_nodejs_app_layer#type OpsworksNodejsAppLayer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksNodejsAppLayerEbsVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksPermission(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksPermission",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission aws_opsworks_permission}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        user_arn: builtins.str,
        allow_ssh: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        allow_sudo: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        level: typing.Optional[builtins.str] = None,
        stack_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission aws_opsworks_permission} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param user_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#user_arn OpsworksPermission#user_arn}.
        :param allow_ssh: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#allow_ssh OpsworksPermission#allow_ssh}.
        :param allow_sudo: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#allow_sudo OpsworksPermission#allow_sudo}.
        :param level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#level OpsworksPermission#level}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#stack_id OpsworksPermission#stack_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksPermissionConfig(
            user_arn=user_arn,
            allow_ssh=allow_ssh,
            allow_sudo=allow_sudo,
            level=level,
            stack_id=stack_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAllowSsh")
    def reset_allow_ssh(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowSsh", []))

    @jsii.member(jsii_name="resetAllowSudo")
    def reset_allow_sudo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowSudo", []))

    @jsii.member(jsii_name="resetLevel")
    def reset_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLevel", []))

    @jsii.member(jsii_name="resetStackId")
    def reset_stack_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStackId", []))

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
    @jsii.member(jsii_name="allowSshInput")
    def allow_ssh_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowSshInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowSudoInput")
    def allow_sudo_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowSudoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="levelInput")
    def level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "levelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userArnInput")
    def user_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowSsh")
    def allow_ssh(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowSsh"))

    @allow_ssh.setter
    def allow_ssh(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "allowSsh", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowSudo")
    def allow_sudo(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowSudo"))

    @allow_sudo.setter
    def allow_sudo(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "allowSudo", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="level")
    def level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "level"))

    @level.setter
    def level(self, value: builtins.str) -> None:
        jsii.set(self, "level", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userArn"))

    @user_arn.setter
    def user_arn(self, value: builtins.str) -> None:
        jsii.set(self, "userArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksPermissionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "user_arn": "userArn",
        "allow_ssh": "allowSsh",
        "allow_sudo": "allowSudo",
        "level": "level",
        "stack_id": "stackId",
    },
)
class OpsworksPermissionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        user_arn: builtins.str,
        allow_ssh: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        allow_sudo: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        level: typing.Optional[builtins.str] = None,
        stack_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param user_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#user_arn OpsworksPermission#user_arn}.
        :param allow_ssh: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#allow_ssh OpsworksPermission#allow_ssh}.
        :param allow_sudo: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#allow_sudo OpsworksPermission#allow_sudo}.
        :param level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#level OpsworksPermission#level}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#stack_id OpsworksPermission#stack_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "user_arn": user_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if allow_ssh is not None:
            self._values["allow_ssh"] = allow_ssh
        if allow_sudo is not None:
            self._values["allow_sudo"] = allow_sudo
        if level is not None:
            self._values["level"] = level
        if stack_id is not None:
            self._values["stack_id"] = stack_id

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
    def user_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#user_arn OpsworksPermission#user_arn}.'''
        result = self._values.get("user_arn")
        assert result is not None, "Required property 'user_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_ssh(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#allow_ssh OpsworksPermission#allow_ssh}.'''
        result = self._values.get("allow_ssh")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def allow_sudo(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#allow_sudo OpsworksPermission#allow_sudo}.'''
        result = self._values.get("allow_sudo")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#level OpsworksPermission#level}.'''
        result = self._values.get("level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stack_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_permission#stack_id OpsworksPermission#stack_id}.'''
        result = self._values.get("stack_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksPermissionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksPhpAppLayer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksPhpAppLayer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer aws_opsworks_php_app_layer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksPhpAppLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer aws_opsworks_php_app_layer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#stack_id OpsworksPhpAppLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#auto_assign_elastic_ips OpsworksPhpAppLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#auto_assign_public_ips OpsworksPhpAppLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#auto_healing OpsworksPhpAppLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_configure_recipes OpsworksPhpAppLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_deploy_recipes OpsworksPhpAppLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_instance_profile_arn OpsworksPhpAppLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_json OpsworksPhpAppLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_security_group_ids OpsworksPhpAppLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_setup_recipes OpsworksPhpAppLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_shutdown_recipes OpsworksPhpAppLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_undeploy_recipes OpsworksPhpAppLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#drain_elb_on_shutdown OpsworksPhpAppLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#ebs_volume OpsworksPhpAppLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#elastic_load_balancer OpsworksPhpAppLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#install_updates_on_boot OpsworksPhpAppLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#instance_shutdown_timeout OpsworksPhpAppLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#name OpsworksPhpAppLayer#name}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#system_packages OpsworksPhpAppLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#tags OpsworksPhpAppLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#tags_all OpsworksPhpAppLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#use_ebs_optimized_instances OpsworksPhpAppLayer#use_ebs_optimized_instances}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksPhpAppLayerConfig(
            stack_id=stack_id,
            auto_assign_elastic_ips=auto_assign_elastic_ips,
            auto_assign_public_ips=auto_assign_public_ips,
            auto_healing=auto_healing,
            custom_configure_recipes=custom_configure_recipes,
            custom_deploy_recipes=custom_deploy_recipes,
            custom_instance_profile_arn=custom_instance_profile_arn,
            custom_json=custom_json,
            custom_security_group_ids=custom_security_group_ids,
            custom_setup_recipes=custom_setup_recipes,
            custom_shutdown_recipes=custom_shutdown_recipes,
            custom_undeploy_recipes=custom_undeploy_recipes,
            drain_elb_on_shutdown=drain_elb_on_shutdown,
            ebs_volume=ebs_volume,
            elastic_load_balancer=elastic_load_balancer,
            install_updates_on_boot=install_updates_on_boot,
            instance_shutdown_timeout=instance_shutdown_timeout,
            name=name,
            system_packages=system_packages,
            tags=tags,
            tags_all=tags_all,
            use_ebs_optimized_instances=use_ebs_optimized_instances,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAutoAssignElasticIps")
    def reset_auto_assign_elastic_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignElasticIps", []))

    @jsii.member(jsii_name="resetAutoAssignPublicIps")
    def reset_auto_assign_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignPublicIps", []))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetCustomConfigureRecipes")
    def reset_custom_configure_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomConfigureRecipes", []))

    @jsii.member(jsii_name="resetCustomDeployRecipes")
    def reset_custom_deploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDeployRecipes", []))

    @jsii.member(jsii_name="resetCustomInstanceProfileArn")
    def reset_custom_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomInstanceProfileArn", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetCustomSecurityGroupIds")
    def reset_custom_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupIds", []))

    @jsii.member(jsii_name="resetCustomSetupRecipes")
    def reset_custom_setup_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSetupRecipes", []))

    @jsii.member(jsii_name="resetCustomShutdownRecipes")
    def reset_custom_shutdown_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomShutdownRecipes", []))

    @jsii.member(jsii_name="resetCustomUndeployRecipes")
    def reset_custom_undeploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUndeployRecipes", []))

    @jsii.member(jsii_name="resetDrainElbOnShutdown")
    def reset_drain_elb_on_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainElbOnShutdown", []))

    @jsii.member(jsii_name="resetEbsVolume")
    def reset_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolume", []))

    @jsii.member(jsii_name="resetElasticLoadBalancer")
    def reset_elastic_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticLoadBalancer", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceShutdownTimeout")
    def reset_instance_shutdown_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceShutdownTimeout", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSystemPackages")
    def reset_system_packages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemPackages", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUseEbsOptimizedInstances")
    def reset_use_ebs_optimized_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseEbsOptimizedInstances", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIpsInput")
    def auto_assign_elastic_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignElasticIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIpsInput")
    def auto_assign_public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignPublicIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipesInput")
    def custom_configure_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customConfigureRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipesInput")
    def custom_deploy_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customDeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArnInput")
    def custom_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdsInput")
    def custom_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipesInput")
    def custom_setup_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSetupRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipesInput")
    def custom_shutdown_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customShutdownRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipesInput")
    def custom_undeploy_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customUndeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdownInput")
    def drain_elb_on_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "drainElbOnShutdownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeInput")
    def ebs_volume_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksPhpAppLayerEbsVolume"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksPhpAppLayerEbsVolume"]], jsii.get(self, "ebsVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancerInput")
    def elastic_load_balancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticLoadBalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeoutInput")
    def instance_shutdown_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceShutdownTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackagesInput")
    def system_packages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "systemPackagesInput"))

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
    @jsii.member(jsii_name="useEbsOptimizedInstancesInput")
    def use_ebs_optimized_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useEbsOptimizedInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIps")
    def auto_assign_elastic_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignElasticIps"))

    @auto_assign_elastic_ips.setter
    def auto_assign_elastic_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignElasticIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIps")
    def auto_assign_public_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignPublicIps"))

    @auto_assign_public_ips.setter
    def auto_assign_public_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignPublicIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoHealing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipes")
    def custom_configure_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customConfigureRecipes"))

    @custom_configure_recipes.setter
    def custom_configure_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customConfigureRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipes")
    def custom_deploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDeployRecipes"))

    @custom_deploy_recipes.setter
    def custom_deploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customDeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArn")
    def custom_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customInstanceProfileArn"))

    @custom_instance_profile_arn.setter
    def custom_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "customInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIds")
    def custom_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSecurityGroupIds"))

    @custom_security_group_ids.setter
    def custom_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipes")
    def custom_setup_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSetupRecipes"))

    @custom_setup_recipes.setter
    def custom_setup_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSetupRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipes")
    def custom_shutdown_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customShutdownRecipes"))

    @custom_shutdown_recipes.setter
    def custom_shutdown_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customShutdownRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipes")
    def custom_undeploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customUndeployRecipes"))

    @custom_undeploy_recipes.setter
    def custom_undeploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customUndeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdown")
    def drain_elb_on_shutdown(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "drainElbOnShutdown"))

    @drain_elb_on_shutdown.setter
    def drain_elb_on_shutdown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "drainElbOnShutdown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolume")
    def ebs_volume(self) -> typing.List["OpsworksPhpAppLayerEbsVolume"]:
        return typing.cast(typing.List["OpsworksPhpAppLayerEbsVolume"], jsii.get(self, "ebsVolume"))

    @ebs_volume.setter
    def ebs_volume(self, value: typing.List["OpsworksPhpAppLayerEbsVolume"]) -> None:
        jsii.set(self, "ebsVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancer")
    def elastic_load_balancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticLoadBalancer"))

    @elastic_load_balancer.setter
    def elastic_load_balancer(self, value: builtins.str) -> None:
        jsii.set(self, "elasticLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeout")
    def instance_shutdown_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceShutdownTimeout"))

    @instance_shutdown_timeout.setter
    def instance_shutdown_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceShutdownTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackages")
    def system_packages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "systemPackages"))

    @system_packages.setter
    def system_packages(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "systemPackages", value)

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
    @jsii.member(jsii_name="useEbsOptimizedInstances")
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useEbsOptimizedInstances"))

    @use_ebs_optimized_instances.setter
    def use_ebs_optimized_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useEbsOptimizedInstances", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksPhpAppLayerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "stack_id": "stackId",
        "auto_assign_elastic_ips": "autoAssignElasticIps",
        "auto_assign_public_ips": "autoAssignPublicIps",
        "auto_healing": "autoHealing",
        "custom_configure_recipes": "customConfigureRecipes",
        "custom_deploy_recipes": "customDeployRecipes",
        "custom_instance_profile_arn": "customInstanceProfileArn",
        "custom_json": "customJson",
        "custom_security_group_ids": "customSecurityGroupIds",
        "custom_setup_recipes": "customSetupRecipes",
        "custom_shutdown_recipes": "customShutdownRecipes",
        "custom_undeploy_recipes": "customUndeployRecipes",
        "drain_elb_on_shutdown": "drainElbOnShutdown",
        "ebs_volume": "ebsVolume",
        "elastic_load_balancer": "elasticLoadBalancer",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_shutdown_timeout": "instanceShutdownTimeout",
        "name": "name",
        "system_packages": "systemPackages",
        "tags": "tags",
        "tags_all": "tagsAll",
        "use_ebs_optimized_instances": "useEbsOptimizedInstances",
    },
)
class OpsworksPhpAppLayerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksPhpAppLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#stack_id OpsworksPhpAppLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#auto_assign_elastic_ips OpsworksPhpAppLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#auto_assign_public_ips OpsworksPhpAppLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#auto_healing OpsworksPhpAppLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_configure_recipes OpsworksPhpAppLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_deploy_recipes OpsworksPhpAppLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_instance_profile_arn OpsworksPhpAppLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_json OpsworksPhpAppLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_security_group_ids OpsworksPhpAppLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_setup_recipes OpsworksPhpAppLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_shutdown_recipes OpsworksPhpAppLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_undeploy_recipes OpsworksPhpAppLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#drain_elb_on_shutdown OpsworksPhpAppLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#ebs_volume OpsworksPhpAppLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#elastic_load_balancer OpsworksPhpAppLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#install_updates_on_boot OpsworksPhpAppLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#instance_shutdown_timeout OpsworksPhpAppLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#name OpsworksPhpAppLayer#name}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#system_packages OpsworksPhpAppLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#tags OpsworksPhpAppLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#tags_all OpsworksPhpAppLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#use_ebs_optimized_instances OpsworksPhpAppLayer#use_ebs_optimized_instances}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "stack_id": stack_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auto_assign_elastic_ips is not None:
            self._values["auto_assign_elastic_ips"] = auto_assign_elastic_ips
        if auto_assign_public_ips is not None:
            self._values["auto_assign_public_ips"] = auto_assign_public_ips
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if custom_configure_recipes is not None:
            self._values["custom_configure_recipes"] = custom_configure_recipes
        if custom_deploy_recipes is not None:
            self._values["custom_deploy_recipes"] = custom_deploy_recipes
        if custom_instance_profile_arn is not None:
            self._values["custom_instance_profile_arn"] = custom_instance_profile_arn
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if custom_security_group_ids is not None:
            self._values["custom_security_group_ids"] = custom_security_group_ids
        if custom_setup_recipes is not None:
            self._values["custom_setup_recipes"] = custom_setup_recipes
        if custom_shutdown_recipes is not None:
            self._values["custom_shutdown_recipes"] = custom_shutdown_recipes
        if custom_undeploy_recipes is not None:
            self._values["custom_undeploy_recipes"] = custom_undeploy_recipes
        if drain_elb_on_shutdown is not None:
            self._values["drain_elb_on_shutdown"] = drain_elb_on_shutdown
        if ebs_volume is not None:
            self._values["ebs_volume"] = ebs_volume
        if elastic_load_balancer is not None:
            self._values["elastic_load_balancer"] = elastic_load_balancer
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_shutdown_timeout is not None:
            self._values["instance_shutdown_timeout"] = instance_shutdown_timeout
        if name is not None:
            self._values["name"] = name
        if system_packages is not None:
            self._values["system_packages"] = system_packages
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if use_ebs_optimized_instances is not None:
            self._values["use_ebs_optimized_instances"] = use_ebs_optimized_instances

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
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#stack_id OpsworksPhpAppLayer#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_assign_elastic_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#auto_assign_elastic_ips OpsworksPhpAppLayer#auto_assign_elastic_ips}.'''
        result = self._values.get("auto_assign_elastic_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_assign_public_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#auto_assign_public_ips OpsworksPhpAppLayer#auto_assign_public_ips}.'''
        result = self._values.get("auto_assign_public_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#auto_healing OpsworksPhpAppLayer#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def custom_configure_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_configure_recipes OpsworksPhpAppLayer#custom_configure_recipes}.'''
        result = self._values.get("custom_configure_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_deploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_deploy_recipes OpsworksPhpAppLayer#custom_deploy_recipes}.'''
        result = self._values.get("custom_deploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_instance_profile_arn OpsworksPhpAppLayer#custom_instance_profile_arn}.'''
        result = self._values.get("custom_instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_json OpsworksPhpAppLayer#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_security_group_ids OpsworksPhpAppLayer#custom_security_group_ids}.'''
        result = self._values.get("custom_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_setup_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_setup_recipes OpsworksPhpAppLayer#custom_setup_recipes}.'''
        result = self._values.get("custom_setup_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_shutdown_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_shutdown_recipes OpsworksPhpAppLayer#custom_shutdown_recipes}.'''
        result = self._values.get("custom_shutdown_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_undeploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#custom_undeploy_recipes OpsworksPhpAppLayer#custom_undeploy_recipes}.'''
        result = self._values.get("custom_undeploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drain_elb_on_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#drain_elb_on_shutdown OpsworksPhpAppLayer#drain_elb_on_shutdown}.'''
        result = self._values.get("drain_elb_on_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_volume(
        self,
    ) -> typing.Optional[typing.List["OpsworksPhpAppLayerEbsVolume"]]:
        '''ebs_volume block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#ebs_volume OpsworksPhpAppLayer#ebs_volume}
        '''
        result = self._values.get("ebs_volume")
        return typing.cast(typing.Optional[typing.List["OpsworksPhpAppLayerEbsVolume"]], result)

    @builtins.property
    def elastic_load_balancer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#elastic_load_balancer OpsworksPhpAppLayer#elastic_load_balancer}.'''
        result = self._values.get("elastic_load_balancer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#install_updates_on_boot OpsworksPhpAppLayer#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_shutdown_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#instance_shutdown_timeout OpsworksPhpAppLayer#instance_shutdown_timeout}.'''
        result = self._values.get("instance_shutdown_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#name OpsworksPhpAppLayer#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def system_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#system_packages OpsworksPhpAppLayer#system_packages}.'''
        result = self._values.get("system_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#tags OpsworksPhpAppLayer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#tags_all OpsworksPhpAppLayer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#use_ebs_optimized_instances OpsworksPhpAppLayer#use_ebs_optimized_instances}.'''
        result = self._values.get("use_ebs_optimized_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksPhpAppLayerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksPhpAppLayerEbsVolume",
    jsii_struct_bases=[],
    name_mapping={
        "mount_point": "mountPoint",
        "number_of_disks": "numberOfDisks",
        "size": "size",
        "encrypted": "encrypted",
        "iops": "iops",
        "raid_level": "raidLevel",
        "type": "type",
    },
)
class OpsworksPhpAppLayerEbsVolume:
    def __init__(
        self,
        *,
        mount_point: builtins.str,
        number_of_disks: jsii.Number,
        size: jsii.Number,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        raid_level: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mount_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#mount_point OpsworksPhpAppLayer#mount_point}.
        :param number_of_disks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#number_of_disks OpsworksPhpAppLayer#number_of_disks}.
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#size OpsworksPhpAppLayer#size}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#encrypted OpsworksPhpAppLayer#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#iops OpsworksPhpAppLayer#iops}.
        :param raid_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#raid_level OpsworksPhpAppLayer#raid_level}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#type OpsworksPhpAppLayer#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mount_point": mount_point,
            "number_of_disks": number_of_disks,
            "size": size,
        }
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if raid_level is not None:
            self._values["raid_level"] = raid_level
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#mount_point OpsworksPhpAppLayer#mount_point}.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_disks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#number_of_disks OpsworksPhpAppLayer#number_of_disks}.'''
        result = self._values.get("number_of_disks")
        assert result is not None, "Required property 'number_of_disks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#size OpsworksPhpAppLayer#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#encrypted OpsworksPhpAppLayer#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#iops OpsworksPhpAppLayer#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raid_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#raid_level OpsworksPhpAppLayer#raid_level}.'''
        result = self._values.get("raid_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_php_app_layer#type OpsworksPhpAppLayer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksPhpAppLayerEbsVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksRailsAppLayer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksRailsAppLayer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer aws_opsworks_rails_app_layer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        stack_id: builtins.str,
        app_server: typing.Optional[builtins.str] = None,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        bundler_version: typing.Optional[builtins.str] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksRailsAppLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        manage_bundler: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        passenger_version: typing.Optional[builtins.str] = None,
        rubygems_version: typing.Optional[builtins.str] = None,
        ruby_version: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer aws_opsworks_rails_app_layer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#stack_id OpsworksRailsAppLayer#stack_id}.
        :param app_server: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#app_server OpsworksRailsAppLayer#app_server}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#auto_assign_elastic_ips OpsworksRailsAppLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#auto_assign_public_ips OpsworksRailsAppLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#auto_healing OpsworksRailsAppLayer#auto_healing}.
        :param bundler_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#bundler_version OpsworksRailsAppLayer#bundler_version}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_configure_recipes OpsworksRailsAppLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_deploy_recipes OpsworksRailsAppLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_instance_profile_arn OpsworksRailsAppLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_json OpsworksRailsAppLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_security_group_ids OpsworksRailsAppLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_setup_recipes OpsworksRailsAppLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_shutdown_recipes OpsworksRailsAppLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_undeploy_recipes OpsworksRailsAppLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#drain_elb_on_shutdown OpsworksRailsAppLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#ebs_volume OpsworksRailsAppLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#elastic_load_balancer OpsworksRailsAppLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#install_updates_on_boot OpsworksRailsAppLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#instance_shutdown_timeout OpsworksRailsAppLayer#instance_shutdown_timeout}.
        :param manage_bundler: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#manage_bundler OpsworksRailsAppLayer#manage_bundler}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#name OpsworksRailsAppLayer#name}.
        :param passenger_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#passenger_version OpsworksRailsAppLayer#passenger_version}.
        :param rubygems_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#rubygems_version OpsworksRailsAppLayer#rubygems_version}.
        :param ruby_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#ruby_version OpsworksRailsAppLayer#ruby_version}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#system_packages OpsworksRailsAppLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#tags OpsworksRailsAppLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#tags_all OpsworksRailsAppLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#use_ebs_optimized_instances OpsworksRailsAppLayer#use_ebs_optimized_instances}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksRailsAppLayerConfig(
            stack_id=stack_id,
            app_server=app_server,
            auto_assign_elastic_ips=auto_assign_elastic_ips,
            auto_assign_public_ips=auto_assign_public_ips,
            auto_healing=auto_healing,
            bundler_version=bundler_version,
            custom_configure_recipes=custom_configure_recipes,
            custom_deploy_recipes=custom_deploy_recipes,
            custom_instance_profile_arn=custom_instance_profile_arn,
            custom_json=custom_json,
            custom_security_group_ids=custom_security_group_ids,
            custom_setup_recipes=custom_setup_recipes,
            custom_shutdown_recipes=custom_shutdown_recipes,
            custom_undeploy_recipes=custom_undeploy_recipes,
            drain_elb_on_shutdown=drain_elb_on_shutdown,
            ebs_volume=ebs_volume,
            elastic_load_balancer=elastic_load_balancer,
            install_updates_on_boot=install_updates_on_boot,
            instance_shutdown_timeout=instance_shutdown_timeout,
            manage_bundler=manage_bundler,
            name=name,
            passenger_version=passenger_version,
            rubygems_version=rubygems_version,
            ruby_version=ruby_version,
            system_packages=system_packages,
            tags=tags,
            tags_all=tags_all,
            use_ebs_optimized_instances=use_ebs_optimized_instances,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAppServer")
    def reset_app_server(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppServer", []))

    @jsii.member(jsii_name="resetAutoAssignElasticIps")
    def reset_auto_assign_elastic_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignElasticIps", []))

    @jsii.member(jsii_name="resetAutoAssignPublicIps")
    def reset_auto_assign_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignPublicIps", []))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetBundlerVersion")
    def reset_bundler_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBundlerVersion", []))

    @jsii.member(jsii_name="resetCustomConfigureRecipes")
    def reset_custom_configure_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomConfigureRecipes", []))

    @jsii.member(jsii_name="resetCustomDeployRecipes")
    def reset_custom_deploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDeployRecipes", []))

    @jsii.member(jsii_name="resetCustomInstanceProfileArn")
    def reset_custom_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomInstanceProfileArn", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetCustomSecurityGroupIds")
    def reset_custom_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupIds", []))

    @jsii.member(jsii_name="resetCustomSetupRecipes")
    def reset_custom_setup_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSetupRecipes", []))

    @jsii.member(jsii_name="resetCustomShutdownRecipes")
    def reset_custom_shutdown_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomShutdownRecipes", []))

    @jsii.member(jsii_name="resetCustomUndeployRecipes")
    def reset_custom_undeploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUndeployRecipes", []))

    @jsii.member(jsii_name="resetDrainElbOnShutdown")
    def reset_drain_elb_on_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainElbOnShutdown", []))

    @jsii.member(jsii_name="resetEbsVolume")
    def reset_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolume", []))

    @jsii.member(jsii_name="resetElasticLoadBalancer")
    def reset_elastic_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticLoadBalancer", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceShutdownTimeout")
    def reset_instance_shutdown_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceShutdownTimeout", []))

    @jsii.member(jsii_name="resetManageBundler")
    def reset_manage_bundler(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManageBundler", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPassengerVersion")
    def reset_passenger_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassengerVersion", []))

    @jsii.member(jsii_name="resetRubygemsVersion")
    def reset_rubygems_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRubygemsVersion", []))

    @jsii.member(jsii_name="resetRubyVersion")
    def reset_ruby_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRubyVersion", []))

    @jsii.member(jsii_name="resetSystemPackages")
    def reset_system_packages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemPackages", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUseEbsOptimizedInstances")
    def reset_use_ebs_optimized_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseEbsOptimizedInstances", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appServerInput")
    def app_server_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appServerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIpsInput")
    def auto_assign_elastic_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignElasticIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIpsInput")
    def auto_assign_public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignPublicIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundlerVersionInput")
    def bundler_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bundlerVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipesInput")
    def custom_configure_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customConfigureRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipesInput")
    def custom_deploy_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customDeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArnInput")
    def custom_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdsInput")
    def custom_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipesInput")
    def custom_setup_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSetupRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipesInput")
    def custom_shutdown_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customShutdownRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipesInput")
    def custom_undeploy_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customUndeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdownInput")
    def drain_elb_on_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "drainElbOnShutdownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeInput")
    def ebs_volume_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksRailsAppLayerEbsVolume"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksRailsAppLayerEbsVolume"]], jsii.get(self, "ebsVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancerInput")
    def elastic_load_balancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticLoadBalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeoutInput")
    def instance_shutdown_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceShutdownTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manageBundlerInput")
    def manage_bundler_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "manageBundlerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passengerVersionInput")
    def passenger_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passengerVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rubygemsVersionInput")
    def rubygems_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rubygemsVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rubyVersionInput")
    def ruby_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rubyVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackagesInput")
    def system_packages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "systemPackagesInput"))

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
    @jsii.member(jsii_name="useEbsOptimizedInstancesInput")
    def use_ebs_optimized_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useEbsOptimizedInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appServer")
    def app_server(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appServer"))

    @app_server.setter
    def app_server(self, value: builtins.str) -> None:
        jsii.set(self, "appServer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIps")
    def auto_assign_elastic_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignElasticIps"))

    @auto_assign_elastic_ips.setter
    def auto_assign_elastic_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignElasticIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIps")
    def auto_assign_public_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignPublicIps"))

    @auto_assign_public_ips.setter
    def auto_assign_public_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignPublicIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoHealing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundlerVersion")
    def bundler_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bundlerVersion"))

    @bundler_version.setter
    def bundler_version(self, value: builtins.str) -> None:
        jsii.set(self, "bundlerVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipes")
    def custom_configure_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customConfigureRecipes"))

    @custom_configure_recipes.setter
    def custom_configure_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customConfigureRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipes")
    def custom_deploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDeployRecipes"))

    @custom_deploy_recipes.setter
    def custom_deploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customDeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArn")
    def custom_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customInstanceProfileArn"))

    @custom_instance_profile_arn.setter
    def custom_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "customInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIds")
    def custom_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSecurityGroupIds"))

    @custom_security_group_ids.setter
    def custom_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipes")
    def custom_setup_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSetupRecipes"))

    @custom_setup_recipes.setter
    def custom_setup_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSetupRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipes")
    def custom_shutdown_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customShutdownRecipes"))

    @custom_shutdown_recipes.setter
    def custom_shutdown_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customShutdownRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipes")
    def custom_undeploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customUndeployRecipes"))

    @custom_undeploy_recipes.setter
    def custom_undeploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customUndeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdown")
    def drain_elb_on_shutdown(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "drainElbOnShutdown"))

    @drain_elb_on_shutdown.setter
    def drain_elb_on_shutdown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "drainElbOnShutdown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolume")
    def ebs_volume(self) -> typing.List["OpsworksRailsAppLayerEbsVolume"]:
        return typing.cast(typing.List["OpsworksRailsAppLayerEbsVolume"], jsii.get(self, "ebsVolume"))

    @ebs_volume.setter
    def ebs_volume(self, value: typing.List["OpsworksRailsAppLayerEbsVolume"]) -> None:
        jsii.set(self, "ebsVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancer")
    def elastic_load_balancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticLoadBalancer"))

    @elastic_load_balancer.setter
    def elastic_load_balancer(self, value: builtins.str) -> None:
        jsii.set(self, "elasticLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeout")
    def instance_shutdown_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceShutdownTimeout"))

    @instance_shutdown_timeout.setter
    def instance_shutdown_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceShutdownTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manageBundler")
    def manage_bundler(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "manageBundler"))

    @manage_bundler.setter
    def manage_bundler(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "manageBundler", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passengerVersion")
    def passenger_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passengerVersion"))

    @passenger_version.setter
    def passenger_version(self, value: builtins.str) -> None:
        jsii.set(self, "passengerVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rubygemsVersion")
    def rubygems_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rubygemsVersion"))

    @rubygems_version.setter
    def rubygems_version(self, value: builtins.str) -> None:
        jsii.set(self, "rubygemsVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rubyVersion")
    def ruby_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rubyVersion"))

    @ruby_version.setter
    def ruby_version(self, value: builtins.str) -> None:
        jsii.set(self, "rubyVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackages")
    def system_packages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "systemPackages"))

    @system_packages.setter
    def system_packages(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "systemPackages", value)

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
    @jsii.member(jsii_name="useEbsOptimizedInstances")
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useEbsOptimizedInstances"))

    @use_ebs_optimized_instances.setter
    def use_ebs_optimized_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useEbsOptimizedInstances", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksRailsAppLayerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "stack_id": "stackId",
        "app_server": "appServer",
        "auto_assign_elastic_ips": "autoAssignElasticIps",
        "auto_assign_public_ips": "autoAssignPublicIps",
        "auto_healing": "autoHealing",
        "bundler_version": "bundlerVersion",
        "custom_configure_recipes": "customConfigureRecipes",
        "custom_deploy_recipes": "customDeployRecipes",
        "custom_instance_profile_arn": "customInstanceProfileArn",
        "custom_json": "customJson",
        "custom_security_group_ids": "customSecurityGroupIds",
        "custom_setup_recipes": "customSetupRecipes",
        "custom_shutdown_recipes": "customShutdownRecipes",
        "custom_undeploy_recipes": "customUndeployRecipes",
        "drain_elb_on_shutdown": "drainElbOnShutdown",
        "ebs_volume": "ebsVolume",
        "elastic_load_balancer": "elasticLoadBalancer",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_shutdown_timeout": "instanceShutdownTimeout",
        "manage_bundler": "manageBundler",
        "name": "name",
        "passenger_version": "passengerVersion",
        "rubygems_version": "rubygemsVersion",
        "ruby_version": "rubyVersion",
        "system_packages": "systemPackages",
        "tags": "tags",
        "tags_all": "tagsAll",
        "use_ebs_optimized_instances": "useEbsOptimizedInstances",
    },
)
class OpsworksRailsAppLayerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        stack_id: builtins.str,
        app_server: typing.Optional[builtins.str] = None,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        bundler_version: typing.Optional[builtins.str] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksRailsAppLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        manage_bundler: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        passenger_version: typing.Optional[builtins.str] = None,
        rubygems_version: typing.Optional[builtins.str] = None,
        ruby_version: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#stack_id OpsworksRailsAppLayer#stack_id}.
        :param app_server: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#app_server OpsworksRailsAppLayer#app_server}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#auto_assign_elastic_ips OpsworksRailsAppLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#auto_assign_public_ips OpsworksRailsAppLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#auto_healing OpsworksRailsAppLayer#auto_healing}.
        :param bundler_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#bundler_version OpsworksRailsAppLayer#bundler_version}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_configure_recipes OpsworksRailsAppLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_deploy_recipes OpsworksRailsAppLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_instance_profile_arn OpsworksRailsAppLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_json OpsworksRailsAppLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_security_group_ids OpsworksRailsAppLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_setup_recipes OpsworksRailsAppLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_shutdown_recipes OpsworksRailsAppLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_undeploy_recipes OpsworksRailsAppLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#drain_elb_on_shutdown OpsworksRailsAppLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#ebs_volume OpsworksRailsAppLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#elastic_load_balancer OpsworksRailsAppLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#install_updates_on_boot OpsworksRailsAppLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#instance_shutdown_timeout OpsworksRailsAppLayer#instance_shutdown_timeout}.
        :param manage_bundler: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#manage_bundler OpsworksRailsAppLayer#manage_bundler}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#name OpsworksRailsAppLayer#name}.
        :param passenger_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#passenger_version OpsworksRailsAppLayer#passenger_version}.
        :param rubygems_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#rubygems_version OpsworksRailsAppLayer#rubygems_version}.
        :param ruby_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#ruby_version OpsworksRailsAppLayer#ruby_version}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#system_packages OpsworksRailsAppLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#tags OpsworksRailsAppLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#tags_all OpsworksRailsAppLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#use_ebs_optimized_instances OpsworksRailsAppLayer#use_ebs_optimized_instances}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "stack_id": stack_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if app_server is not None:
            self._values["app_server"] = app_server
        if auto_assign_elastic_ips is not None:
            self._values["auto_assign_elastic_ips"] = auto_assign_elastic_ips
        if auto_assign_public_ips is not None:
            self._values["auto_assign_public_ips"] = auto_assign_public_ips
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if bundler_version is not None:
            self._values["bundler_version"] = bundler_version
        if custom_configure_recipes is not None:
            self._values["custom_configure_recipes"] = custom_configure_recipes
        if custom_deploy_recipes is not None:
            self._values["custom_deploy_recipes"] = custom_deploy_recipes
        if custom_instance_profile_arn is not None:
            self._values["custom_instance_profile_arn"] = custom_instance_profile_arn
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if custom_security_group_ids is not None:
            self._values["custom_security_group_ids"] = custom_security_group_ids
        if custom_setup_recipes is not None:
            self._values["custom_setup_recipes"] = custom_setup_recipes
        if custom_shutdown_recipes is not None:
            self._values["custom_shutdown_recipes"] = custom_shutdown_recipes
        if custom_undeploy_recipes is not None:
            self._values["custom_undeploy_recipes"] = custom_undeploy_recipes
        if drain_elb_on_shutdown is not None:
            self._values["drain_elb_on_shutdown"] = drain_elb_on_shutdown
        if ebs_volume is not None:
            self._values["ebs_volume"] = ebs_volume
        if elastic_load_balancer is not None:
            self._values["elastic_load_balancer"] = elastic_load_balancer
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_shutdown_timeout is not None:
            self._values["instance_shutdown_timeout"] = instance_shutdown_timeout
        if manage_bundler is not None:
            self._values["manage_bundler"] = manage_bundler
        if name is not None:
            self._values["name"] = name
        if passenger_version is not None:
            self._values["passenger_version"] = passenger_version
        if rubygems_version is not None:
            self._values["rubygems_version"] = rubygems_version
        if ruby_version is not None:
            self._values["ruby_version"] = ruby_version
        if system_packages is not None:
            self._values["system_packages"] = system_packages
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if use_ebs_optimized_instances is not None:
            self._values["use_ebs_optimized_instances"] = use_ebs_optimized_instances

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
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#stack_id OpsworksRailsAppLayer#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_server(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#app_server OpsworksRailsAppLayer#app_server}.'''
        result = self._values.get("app_server")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_assign_elastic_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#auto_assign_elastic_ips OpsworksRailsAppLayer#auto_assign_elastic_ips}.'''
        result = self._values.get("auto_assign_elastic_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_assign_public_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#auto_assign_public_ips OpsworksRailsAppLayer#auto_assign_public_ips}.'''
        result = self._values.get("auto_assign_public_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#auto_healing OpsworksRailsAppLayer#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def bundler_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#bundler_version OpsworksRailsAppLayer#bundler_version}.'''
        result = self._values.get("bundler_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_configure_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_configure_recipes OpsworksRailsAppLayer#custom_configure_recipes}.'''
        result = self._values.get("custom_configure_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_deploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_deploy_recipes OpsworksRailsAppLayer#custom_deploy_recipes}.'''
        result = self._values.get("custom_deploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_instance_profile_arn OpsworksRailsAppLayer#custom_instance_profile_arn}.'''
        result = self._values.get("custom_instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_json OpsworksRailsAppLayer#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_security_group_ids OpsworksRailsAppLayer#custom_security_group_ids}.'''
        result = self._values.get("custom_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_setup_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_setup_recipes OpsworksRailsAppLayer#custom_setup_recipes}.'''
        result = self._values.get("custom_setup_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_shutdown_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_shutdown_recipes OpsworksRailsAppLayer#custom_shutdown_recipes}.'''
        result = self._values.get("custom_shutdown_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_undeploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#custom_undeploy_recipes OpsworksRailsAppLayer#custom_undeploy_recipes}.'''
        result = self._values.get("custom_undeploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drain_elb_on_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#drain_elb_on_shutdown OpsworksRailsAppLayer#drain_elb_on_shutdown}.'''
        result = self._values.get("drain_elb_on_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_volume(
        self,
    ) -> typing.Optional[typing.List["OpsworksRailsAppLayerEbsVolume"]]:
        '''ebs_volume block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#ebs_volume OpsworksRailsAppLayer#ebs_volume}
        '''
        result = self._values.get("ebs_volume")
        return typing.cast(typing.Optional[typing.List["OpsworksRailsAppLayerEbsVolume"]], result)

    @builtins.property
    def elastic_load_balancer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#elastic_load_balancer OpsworksRailsAppLayer#elastic_load_balancer}.'''
        result = self._values.get("elastic_load_balancer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#install_updates_on_boot OpsworksRailsAppLayer#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_shutdown_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#instance_shutdown_timeout OpsworksRailsAppLayer#instance_shutdown_timeout}.'''
        result = self._values.get("instance_shutdown_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def manage_bundler(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#manage_bundler OpsworksRailsAppLayer#manage_bundler}.'''
        result = self._values.get("manage_bundler")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#name OpsworksRailsAppLayer#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def passenger_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#passenger_version OpsworksRailsAppLayer#passenger_version}.'''
        result = self._values.get("passenger_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rubygems_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#rubygems_version OpsworksRailsAppLayer#rubygems_version}.'''
        result = self._values.get("rubygems_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ruby_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#ruby_version OpsworksRailsAppLayer#ruby_version}.'''
        result = self._values.get("ruby_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def system_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#system_packages OpsworksRailsAppLayer#system_packages}.'''
        result = self._values.get("system_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#tags OpsworksRailsAppLayer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#tags_all OpsworksRailsAppLayer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#use_ebs_optimized_instances OpsworksRailsAppLayer#use_ebs_optimized_instances}.'''
        result = self._values.get("use_ebs_optimized_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksRailsAppLayerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksRailsAppLayerEbsVolume",
    jsii_struct_bases=[],
    name_mapping={
        "mount_point": "mountPoint",
        "number_of_disks": "numberOfDisks",
        "size": "size",
        "encrypted": "encrypted",
        "iops": "iops",
        "raid_level": "raidLevel",
        "type": "type",
    },
)
class OpsworksRailsAppLayerEbsVolume:
    def __init__(
        self,
        *,
        mount_point: builtins.str,
        number_of_disks: jsii.Number,
        size: jsii.Number,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        raid_level: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mount_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#mount_point OpsworksRailsAppLayer#mount_point}.
        :param number_of_disks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#number_of_disks OpsworksRailsAppLayer#number_of_disks}.
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#size OpsworksRailsAppLayer#size}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#encrypted OpsworksRailsAppLayer#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#iops OpsworksRailsAppLayer#iops}.
        :param raid_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#raid_level OpsworksRailsAppLayer#raid_level}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#type OpsworksRailsAppLayer#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mount_point": mount_point,
            "number_of_disks": number_of_disks,
            "size": size,
        }
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if raid_level is not None:
            self._values["raid_level"] = raid_level
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#mount_point OpsworksRailsAppLayer#mount_point}.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_disks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#number_of_disks OpsworksRailsAppLayer#number_of_disks}.'''
        result = self._values.get("number_of_disks")
        assert result is not None, "Required property 'number_of_disks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#size OpsworksRailsAppLayer#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#encrypted OpsworksRailsAppLayer#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#iops OpsworksRailsAppLayer#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raid_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#raid_level OpsworksRailsAppLayer#raid_level}.'''
        result = self._values.get("raid_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rails_app_layer#type OpsworksRailsAppLayer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksRailsAppLayerEbsVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksRdsDbInstance(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksRdsDbInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance aws_opsworks_rds_db_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_password: builtins.str,
        db_user: builtins.str,
        rds_db_instance_arn: builtins.str,
        stack_id: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance aws_opsworks_rds_db_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param db_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#db_password OpsworksRdsDbInstance#db_password}.
        :param db_user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#db_user OpsworksRdsDbInstance#db_user}.
        :param rds_db_instance_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#rds_db_instance_arn OpsworksRdsDbInstance#rds_db_instance_arn}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#stack_id OpsworksRdsDbInstance#stack_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksRdsDbInstanceConfig(
            db_password=db_password,
            db_user=db_user,
            rds_db_instance_arn=rds_db_instance_arn,
            stack_id=stack_id,
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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbPasswordInput")
    def db_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbPasswordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbUserInput")
    def db_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbUserInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rdsDbInstanceArnInput")
    def rds_db_instance_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rdsDbInstanceArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbPassword")
    def db_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbPassword"))

    @db_password.setter
    def db_password(self, value: builtins.str) -> None:
        jsii.set(self, "dbPassword", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbUser")
    def db_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbUser"))

    @db_user.setter
    def db_user(self, value: builtins.str) -> None:
        jsii.set(self, "dbUser", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rdsDbInstanceArn")
    def rds_db_instance_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rdsDbInstanceArn"))

    @rds_db_instance_arn.setter
    def rds_db_instance_arn(self, value: builtins.str) -> None:
        jsii.set(self, "rdsDbInstanceArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksRdsDbInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "db_password": "dbPassword",
        "db_user": "dbUser",
        "rds_db_instance_arn": "rdsDbInstanceArn",
        "stack_id": "stackId",
    },
)
class OpsworksRdsDbInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        db_password: builtins.str,
        db_user: builtins.str,
        rds_db_instance_arn: builtins.str,
        stack_id: builtins.str,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param db_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#db_password OpsworksRdsDbInstance#db_password}.
        :param db_user: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#db_user OpsworksRdsDbInstance#db_user}.
        :param rds_db_instance_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#rds_db_instance_arn OpsworksRdsDbInstance#rds_db_instance_arn}.
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#stack_id OpsworksRdsDbInstance#stack_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "db_password": db_password,
            "db_user": db_user,
            "rds_db_instance_arn": rds_db_instance_arn,
            "stack_id": stack_id,
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
    def db_password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#db_password OpsworksRdsDbInstance#db_password}.'''
        result = self._values.get("db_password")
        assert result is not None, "Required property 'db_password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_user(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#db_user OpsworksRdsDbInstance#db_user}.'''
        result = self._values.get("db_user")
        assert result is not None, "Required property 'db_user' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rds_db_instance_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#rds_db_instance_arn OpsworksRdsDbInstance#rds_db_instance_arn}.'''
        result = self._values.get("rds_db_instance_arn")
        assert result is not None, "Required property 'rds_db_instance_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_rds_db_instance#stack_id OpsworksRdsDbInstance#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksRdsDbInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksStack(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksStack",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack aws_opsworks_stack}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        default_instance_profile_arn: builtins.str,
        name: builtins.str,
        region: builtins.str,
        service_role_arn: builtins.str,
        agent_version: typing.Optional[builtins.str] = None,
        berkshelf_version: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        configuration_manager_name: typing.Optional[builtins.str] = None,
        configuration_manager_version: typing.Optional[builtins.str] = None,
        custom_cookbooks_source: typing.Optional[typing.Sequence["OpsworksStackCustomCookbooksSource"]] = None,
        custom_json: typing.Optional[builtins.str] = None,
        default_availability_zone: typing.Optional[builtins.str] = None,
        default_os: typing.Optional[builtins.str] = None,
        default_root_device_type: typing.Optional[builtins.str] = None,
        default_ssh_key_name: typing.Optional[builtins.str] = None,
        default_subnet_id: typing.Optional[builtins.str] = None,
        hostname_theme: typing.Optional[builtins.str] = None,
        manage_berkshelf: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_custom_cookbooks: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        use_opsworks_security_groups: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        vpc_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack aws_opsworks_stack} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param default_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_instance_profile_arn OpsworksStack#default_instance_profile_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#name OpsworksStack#name}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#region OpsworksStack#region}.
        :param service_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#service_role_arn OpsworksStack#service_role_arn}.
        :param agent_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#agent_version OpsworksStack#agent_version}.
        :param berkshelf_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#berkshelf_version OpsworksStack#berkshelf_version}.
        :param color: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#color OpsworksStack#color}.
        :param configuration_manager_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#configuration_manager_name OpsworksStack#configuration_manager_name}.
        :param configuration_manager_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#configuration_manager_version OpsworksStack#configuration_manager_version}.
        :param custom_cookbooks_source: custom_cookbooks_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#custom_cookbooks_source OpsworksStack#custom_cookbooks_source}
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#custom_json OpsworksStack#custom_json}.
        :param default_availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_availability_zone OpsworksStack#default_availability_zone}.
        :param default_os: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_os OpsworksStack#default_os}.
        :param default_root_device_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_root_device_type OpsworksStack#default_root_device_type}.
        :param default_ssh_key_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_ssh_key_name OpsworksStack#default_ssh_key_name}.
        :param default_subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_subnet_id OpsworksStack#default_subnet_id}.
        :param hostname_theme: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#hostname_theme OpsworksStack#hostname_theme}.
        :param manage_berkshelf: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#manage_berkshelf OpsworksStack#manage_berkshelf}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#tags OpsworksStack#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#tags_all OpsworksStack#tags_all}.
        :param use_custom_cookbooks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#use_custom_cookbooks OpsworksStack#use_custom_cookbooks}.
        :param use_opsworks_security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#use_opsworks_security_groups OpsworksStack#use_opsworks_security_groups}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#vpc_id OpsworksStack#vpc_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksStackConfig(
            default_instance_profile_arn=default_instance_profile_arn,
            name=name,
            region=region,
            service_role_arn=service_role_arn,
            agent_version=agent_version,
            berkshelf_version=berkshelf_version,
            color=color,
            configuration_manager_name=configuration_manager_name,
            configuration_manager_version=configuration_manager_version,
            custom_cookbooks_source=custom_cookbooks_source,
            custom_json=custom_json,
            default_availability_zone=default_availability_zone,
            default_os=default_os,
            default_root_device_type=default_root_device_type,
            default_ssh_key_name=default_ssh_key_name,
            default_subnet_id=default_subnet_id,
            hostname_theme=hostname_theme,
            manage_berkshelf=manage_berkshelf,
            tags=tags,
            tags_all=tags_all,
            use_custom_cookbooks=use_custom_cookbooks,
            use_opsworks_security_groups=use_opsworks_security_groups,
            vpc_id=vpc_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAgentVersion")
    def reset_agent_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAgentVersion", []))

    @jsii.member(jsii_name="resetBerkshelfVersion")
    def reset_berkshelf_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBerkshelfVersion", []))

    @jsii.member(jsii_name="resetColor")
    def reset_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetColor", []))

    @jsii.member(jsii_name="resetConfigurationManagerName")
    def reset_configuration_manager_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurationManagerName", []))

    @jsii.member(jsii_name="resetConfigurationManagerVersion")
    def reset_configuration_manager_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigurationManagerVersion", []))

    @jsii.member(jsii_name="resetCustomCookbooksSource")
    def reset_custom_cookbooks_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomCookbooksSource", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetDefaultAvailabilityZone")
    def reset_default_availability_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultAvailabilityZone", []))

    @jsii.member(jsii_name="resetDefaultOs")
    def reset_default_os(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultOs", []))

    @jsii.member(jsii_name="resetDefaultRootDeviceType")
    def reset_default_root_device_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultRootDeviceType", []))

    @jsii.member(jsii_name="resetDefaultSshKeyName")
    def reset_default_ssh_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultSshKeyName", []))

    @jsii.member(jsii_name="resetDefaultSubnetId")
    def reset_default_subnet_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultSubnetId", []))

    @jsii.member(jsii_name="resetHostnameTheme")
    def reset_hostname_theme(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostnameTheme", []))

    @jsii.member(jsii_name="resetManageBerkshelf")
    def reset_manage_berkshelf(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetManageBerkshelf", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUseCustomCookbooks")
    def reset_use_custom_cookbooks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseCustomCookbooks", []))

    @jsii.member(jsii_name="resetUseOpsworksSecurityGroups")
    def reset_use_opsworks_security_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseOpsworksSecurityGroups", []))

    @jsii.member(jsii_name="resetVpcId")
    def reset_vpc_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcId", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackEndpoint")
    def stack_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentVersionInput")
    def agent_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="berkshelfVersionInput")
    def berkshelf_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "berkshelfVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="colorInput")
    def color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "colorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationManagerNameInput")
    def configuration_manager_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configurationManagerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationManagerVersionInput")
    def configuration_manager_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configurationManagerVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customCookbooksSourceInput")
    def custom_cookbooks_source_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksStackCustomCookbooksSource"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksStackCustomCookbooksSource"]], jsii.get(self, "customCookbooksSourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultAvailabilityZoneInput")
    def default_availability_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultAvailabilityZoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultInstanceProfileArnInput")
    def default_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultOsInput")
    def default_os_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultOsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRootDeviceTypeInput")
    def default_root_device_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultRootDeviceTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultSshKeyNameInput")
    def default_ssh_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultSshKeyNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultSubnetIdInput")
    def default_subnet_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultSubnetIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostnameThemeInput")
    def hostname_theme_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameThemeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manageBerkshelfInput")
    def manage_berkshelf_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "manageBerkshelfInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleArnInput")
    def service_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceRoleArnInput"))

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
    @jsii.member(jsii_name="useCustomCookbooksInput")
    def use_custom_cookbooks_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useCustomCookbooksInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useOpsworksSecurityGroupsInput")
    def use_opsworks_security_groups_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useOpsworksSecurityGroupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="agentVersion")
    def agent_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "agentVersion"))

    @agent_version.setter
    def agent_version(self, value: builtins.str) -> None:
        jsii.set(self, "agentVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="berkshelfVersion")
    def berkshelf_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "berkshelfVersion"))

    @berkshelf_version.setter
    def berkshelf_version(self, value: builtins.str) -> None:
        jsii.set(self, "berkshelfVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="color")
    def color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "color"))

    @color.setter
    def color(self, value: builtins.str) -> None:
        jsii.set(self, "color", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationManagerName")
    def configuration_manager_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationManagerName"))

    @configuration_manager_name.setter
    def configuration_manager_name(self, value: builtins.str) -> None:
        jsii.set(self, "configurationManagerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationManagerVersion")
    def configuration_manager_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationManagerVersion"))

    @configuration_manager_version.setter
    def configuration_manager_version(self, value: builtins.str) -> None:
        jsii.set(self, "configurationManagerVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customCookbooksSource")
    def custom_cookbooks_source(
        self,
    ) -> typing.List["OpsworksStackCustomCookbooksSource"]:
        return typing.cast(typing.List["OpsworksStackCustomCookbooksSource"], jsii.get(self, "customCookbooksSource"))

    @custom_cookbooks_source.setter
    def custom_cookbooks_source(
        self,
        value: typing.List["OpsworksStackCustomCookbooksSource"],
    ) -> None:
        jsii.set(self, "customCookbooksSource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultAvailabilityZone")
    def default_availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultAvailabilityZone"))

    @default_availability_zone.setter
    def default_availability_zone(self, value: builtins.str) -> None:
        jsii.set(self, "defaultAvailabilityZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultInstanceProfileArn")
    def default_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultInstanceProfileArn"))

    @default_instance_profile_arn.setter
    def default_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "defaultInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultOs")
    def default_os(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultOs"))

    @default_os.setter
    def default_os(self, value: builtins.str) -> None:
        jsii.set(self, "defaultOs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRootDeviceType")
    def default_root_device_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultRootDeviceType"))

    @default_root_device_type.setter
    def default_root_device_type(self, value: builtins.str) -> None:
        jsii.set(self, "defaultRootDeviceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultSshKeyName")
    def default_ssh_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultSshKeyName"))

    @default_ssh_key_name.setter
    def default_ssh_key_name(self, value: builtins.str) -> None:
        jsii.set(self, "defaultSshKeyName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultSubnetId")
    def default_subnet_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultSubnetId"))

    @default_subnet_id.setter
    def default_subnet_id(self, value: builtins.str) -> None:
        jsii.set(self, "defaultSubnetId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostnameTheme")
    def hostname_theme(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostnameTheme"))

    @hostname_theme.setter
    def hostname_theme(self, value: builtins.str) -> None:
        jsii.set(self, "hostnameTheme", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manageBerkshelf")
    def manage_berkshelf(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "manageBerkshelf"))

    @manage_berkshelf.setter
    def manage_berkshelf(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "manageBerkshelf", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRoleArn")
    def service_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceRoleArn"))

    @service_role_arn.setter
    def service_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "serviceRoleArn", value)

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
    @jsii.member(jsii_name="useCustomCookbooks")
    def use_custom_cookbooks(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useCustomCookbooks"))

    @use_custom_cookbooks.setter
    def use_custom_cookbooks(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useCustomCookbooks", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useOpsworksSecurityGroups")
    def use_opsworks_security_groups(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useOpsworksSecurityGroups"))

    @use_opsworks_security_groups.setter
    def use_opsworks_security_groups(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useOpsworksSecurityGroups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        jsii.set(self, "vpcId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksStackConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "default_instance_profile_arn": "defaultInstanceProfileArn",
        "name": "name",
        "region": "region",
        "service_role_arn": "serviceRoleArn",
        "agent_version": "agentVersion",
        "berkshelf_version": "berkshelfVersion",
        "color": "color",
        "configuration_manager_name": "configurationManagerName",
        "configuration_manager_version": "configurationManagerVersion",
        "custom_cookbooks_source": "customCookbooksSource",
        "custom_json": "customJson",
        "default_availability_zone": "defaultAvailabilityZone",
        "default_os": "defaultOs",
        "default_root_device_type": "defaultRootDeviceType",
        "default_ssh_key_name": "defaultSshKeyName",
        "default_subnet_id": "defaultSubnetId",
        "hostname_theme": "hostnameTheme",
        "manage_berkshelf": "manageBerkshelf",
        "tags": "tags",
        "tags_all": "tagsAll",
        "use_custom_cookbooks": "useCustomCookbooks",
        "use_opsworks_security_groups": "useOpsworksSecurityGroups",
        "vpc_id": "vpcId",
    },
)
class OpsworksStackConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        default_instance_profile_arn: builtins.str,
        name: builtins.str,
        region: builtins.str,
        service_role_arn: builtins.str,
        agent_version: typing.Optional[builtins.str] = None,
        berkshelf_version: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        configuration_manager_name: typing.Optional[builtins.str] = None,
        configuration_manager_version: typing.Optional[builtins.str] = None,
        custom_cookbooks_source: typing.Optional[typing.Sequence["OpsworksStackCustomCookbooksSource"]] = None,
        custom_json: typing.Optional[builtins.str] = None,
        default_availability_zone: typing.Optional[builtins.str] = None,
        default_os: typing.Optional[builtins.str] = None,
        default_root_device_type: typing.Optional[builtins.str] = None,
        default_ssh_key_name: typing.Optional[builtins.str] = None,
        default_subnet_id: typing.Optional[builtins.str] = None,
        hostname_theme: typing.Optional[builtins.str] = None,
        manage_berkshelf: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_custom_cookbooks: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        use_opsworks_security_groups: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param default_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_instance_profile_arn OpsworksStack#default_instance_profile_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#name OpsworksStack#name}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#region OpsworksStack#region}.
        :param service_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#service_role_arn OpsworksStack#service_role_arn}.
        :param agent_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#agent_version OpsworksStack#agent_version}.
        :param berkshelf_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#berkshelf_version OpsworksStack#berkshelf_version}.
        :param color: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#color OpsworksStack#color}.
        :param configuration_manager_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#configuration_manager_name OpsworksStack#configuration_manager_name}.
        :param configuration_manager_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#configuration_manager_version OpsworksStack#configuration_manager_version}.
        :param custom_cookbooks_source: custom_cookbooks_source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#custom_cookbooks_source OpsworksStack#custom_cookbooks_source}
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#custom_json OpsworksStack#custom_json}.
        :param default_availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_availability_zone OpsworksStack#default_availability_zone}.
        :param default_os: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_os OpsworksStack#default_os}.
        :param default_root_device_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_root_device_type OpsworksStack#default_root_device_type}.
        :param default_ssh_key_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_ssh_key_name OpsworksStack#default_ssh_key_name}.
        :param default_subnet_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_subnet_id OpsworksStack#default_subnet_id}.
        :param hostname_theme: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#hostname_theme OpsworksStack#hostname_theme}.
        :param manage_berkshelf: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#manage_berkshelf OpsworksStack#manage_berkshelf}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#tags OpsworksStack#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#tags_all OpsworksStack#tags_all}.
        :param use_custom_cookbooks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#use_custom_cookbooks OpsworksStack#use_custom_cookbooks}.
        :param use_opsworks_security_groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#use_opsworks_security_groups OpsworksStack#use_opsworks_security_groups}.
        :param vpc_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#vpc_id OpsworksStack#vpc_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "default_instance_profile_arn": default_instance_profile_arn,
            "name": name,
            "region": region,
            "service_role_arn": service_role_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if agent_version is not None:
            self._values["agent_version"] = agent_version
        if berkshelf_version is not None:
            self._values["berkshelf_version"] = berkshelf_version
        if color is not None:
            self._values["color"] = color
        if configuration_manager_name is not None:
            self._values["configuration_manager_name"] = configuration_manager_name
        if configuration_manager_version is not None:
            self._values["configuration_manager_version"] = configuration_manager_version
        if custom_cookbooks_source is not None:
            self._values["custom_cookbooks_source"] = custom_cookbooks_source
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if default_availability_zone is not None:
            self._values["default_availability_zone"] = default_availability_zone
        if default_os is not None:
            self._values["default_os"] = default_os
        if default_root_device_type is not None:
            self._values["default_root_device_type"] = default_root_device_type
        if default_ssh_key_name is not None:
            self._values["default_ssh_key_name"] = default_ssh_key_name
        if default_subnet_id is not None:
            self._values["default_subnet_id"] = default_subnet_id
        if hostname_theme is not None:
            self._values["hostname_theme"] = hostname_theme
        if manage_berkshelf is not None:
            self._values["manage_berkshelf"] = manage_berkshelf
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if use_custom_cookbooks is not None:
            self._values["use_custom_cookbooks"] = use_custom_cookbooks
        if use_opsworks_security_groups is not None:
            self._values["use_opsworks_security_groups"] = use_opsworks_security_groups
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id

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
    def default_instance_profile_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_instance_profile_arn OpsworksStack#default_instance_profile_arn}.'''
        result = self._values.get("default_instance_profile_arn")
        assert result is not None, "Required property 'default_instance_profile_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#name OpsworksStack#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#region OpsworksStack#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#service_role_arn OpsworksStack#service_role_arn}.'''
        result = self._values.get("service_role_arn")
        assert result is not None, "Required property 'service_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#agent_version OpsworksStack#agent_version}.'''
        result = self._values.get("agent_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def berkshelf_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#berkshelf_version OpsworksStack#berkshelf_version}.'''
        result = self._values.get("berkshelf_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def color(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#color OpsworksStack#color}.'''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configuration_manager_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#configuration_manager_name OpsworksStack#configuration_manager_name}.'''
        result = self._values.get("configuration_manager_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configuration_manager_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#configuration_manager_version OpsworksStack#configuration_manager_version}.'''
        result = self._values.get("configuration_manager_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_cookbooks_source(
        self,
    ) -> typing.Optional[typing.List["OpsworksStackCustomCookbooksSource"]]:
        '''custom_cookbooks_source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#custom_cookbooks_source OpsworksStack#custom_cookbooks_source}
        '''
        result = self._values.get("custom_cookbooks_source")
        return typing.cast(typing.Optional[typing.List["OpsworksStackCustomCookbooksSource"]], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#custom_json OpsworksStack#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_availability_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_availability_zone OpsworksStack#default_availability_zone}.'''
        result = self._values.get("default_availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_os(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_os OpsworksStack#default_os}.'''
        result = self._values.get("default_os")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_root_device_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_root_device_type OpsworksStack#default_root_device_type}.'''
        result = self._values.get("default_root_device_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_ssh_key_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_ssh_key_name OpsworksStack#default_ssh_key_name}.'''
        result = self._values.get("default_ssh_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_subnet_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#default_subnet_id OpsworksStack#default_subnet_id}.'''
        result = self._values.get("default_subnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hostname_theme(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#hostname_theme OpsworksStack#hostname_theme}.'''
        result = self._values.get("hostname_theme")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def manage_berkshelf(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#manage_berkshelf OpsworksStack#manage_berkshelf}.'''
        result = self._values.get("manage_berkshelf")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#tags OpsworksStack#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#tags_all OpsworksStack#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_custom_cookbooks(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#use_custom_cookbooks OpsworksStack#use_custom_cookbooks}.'''
        result = self._values.get("use_custom_cookbooks")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def use_opsworks_security_groups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#use_opsworks_security_groups OpsworksStack#use_opsworks_security_groups}.'''
        result = self._values.get("use_opsworks_security_groups")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#vpc_id OpsworksStack#vpc_id}.'''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksStackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksStackCustomCookbooksSource",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "url": "url",
        "password": "password",
        "revision": "revision",
        "ssh_key": "sshKey",
        "username": "username",
    },
)
class OpsworksStackCustomCookbooksSource:
    def __init__(
        self,
        *,
        type: builtins.str,
        url: builtins.str,
        password: typing.Optional[builtins.str] = None,
        revision: typing.Optional[builtins.str] = None,
        ssh_key: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#type OpsworksStack#type}.
        :param url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#url OpsworksStack#url}.
        :param password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#password OpsworksStack#password}.
        :param revision: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#revision OpsworksStack#revision}.
        :param ssh_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#ssh_key OpsworksStack#ssh_key}.
        :param username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#username OpsworksStack#username}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
            "url": url,
        }
        if password is not None:
            self._values["password"] = password
        if revision is not None:
            self._values["revision"] = revision
        if ssh_key is not None:
            self._values["ssh_key"] = ssh_key
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#type OpsworksStack#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#url OpsworksStack#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#password OpsworksStack#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def revision(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#revision OpsworksStack#revision}.'''
        result = self._values.get("revision")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#ssh_key OpsworksStack#ssh_key}.'''
        result = self._values.get("ssh_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_stack#username OpsworksStack#username}.'''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksStackCustomCookbooksSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksStaticWebLayer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksStaticWebLayer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer aws_opsworks_static_web_layer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksStaticWebLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer aws_opsworks_static_web_layer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#stack_id OpsworksStaticWebLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#auto_assign_elastic_ips OpsworksStaticWebLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#auto_assign_public_ips OpsworksStaticWebLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#auto_healing OpsworksStaticWebLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_configure_recipes OpsworksStaticWebLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_deploy_recipes OpsworksStaticWebLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_instance_profile_arn OpsworksStaticWebLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_json OpsworksStaticWebLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_security_group_ids OpsworksStaticWebLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_setup_recipes OpsworksStaticWebLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_shutdown_recipes OpsworksStaticWebLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_undeploy_recipes OpsworksStaticWebLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#drain_elb_on_shutdown OpsworksStaticWebLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#ebs_volume OpsworksStaticWebLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#elastic_load_balancer OpsworksStaticWebLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#install_updates_on_boot OpsworksStaticWebLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#instance_shutdown_timeout OpsworksStaticWebLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#name OpsworksStaticWebLayer#name}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#system_packages OpsworksStaticWebLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#tags OpsworksStaticWebLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#tags_all OpsworksStaticWebLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#use_ebs_optimized_instances OpsworksStaticWebLayer#use_ebs_optimized_instances}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksStaticWebLayerConfig(
            stack_id=stack_id,
            auto_assign_elastic_ips=auto_assign_elastic_ips,
            auto_assign_public_ips=auto_assign_public_ips,
            auto_healing=auto_healing,
            custom_configure_recipes=custom_configure_recipes,
            custom_deploy_recipes=custom_deploy_recipes,
            custom_instance_profile_arn=custom_instance_profile_arn,
            custom_json=custom_json,
            custom_security_group_ids=custom_security_group_ids,
            custom_setup_recipes=custom_setup_recipes,
            custom_shutdown_recipes=custom_shutdown_recipes,
            custom_undeploy_recipes=custom_undeploy_recipes,
            drain_elb_on_shutdown=drain_elb_on_shutdown,
            ebs_volume=ebs_volume,
            elastic_load_balancer=elastic_load_balancer,
            install_updates_on_boot=install_updates_on_boot,
            instance_shutdown_timeout=instance_shutdown_timeout,
            name=name,
            system_packages=system_packages,
            tags=tags,
            tags_all=tags_all,
            use_ebs_optimized_instances=use_ebs_optimized_instances,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAutoAssignElasticIps")
    def reset_auto_assign_elastic_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignElasticIps", []))

    @jsii.member(jsii_name="resetAutoAssignPublicIps")
    def reset_auto_assign_public_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoAssignPublicIps", []))

    @jsii.member(jsii_name="resetAutoHealing")
    def reset_auto_healing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoHealing", []))

    @jsii.member(jsii_name="resetCustomConfigureRecipes")
    def reset_custom_configure_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomConfigureRecipes", []))

    @jsii.member(jsii_name="resetCustomDeployRecipes")
    def reset_custom_deploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomDeployRecipes", []))

    @jsii.member(jsii_name="resetCustomInstanceProfileArn")
    def reset_custom_instance_profile_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomInstanceProfileArn", []))

    @jsii.member(jsii_name="resetCustomJson")
    def reset_custom_json(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomJson", []))

    @jsii.member(jsii_name="resetCustomSecurityGroupIds")
    def reset_custom_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSecurityGroupIds", []))

    @jsii.member(jsii_name="resetCustomSetupRecipes")
    def reset_custom_setup_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomSetupRecipes", []))

    @jsii.member(jsii_name="resetCustomShutdownRecipes")
    def reset_custom_shutdown_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomShutdownRecipes", []))

    @jsii.member(jsii_name="resetCustomUndeployRecipes")
    def reset_custom_undeploy_recipes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUndeployRecipes", []))

    @jsii.member(jsii_name="resetDrainElbOnShutdown")
    def reset_drain_elb_on_shutdown(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrainElbOnShutdown", []))

    @jsii.member(jsii_name="resetEbsVolume")
    def reset_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEbsVolume", []))

    @jsii.member(jsii_name="resetElasticLoadBalancer")
    def reset_elastic_load_balancer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElasticLoadBalancer", []))

    @jsii.member(jsii_name="resetInstallUpdatesOnBoot")
    def reset_install_updates_on_boot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallUpdatesOnBoot", []))

    @jsii.member(jsii_name="resetInstanceShutdownTimeout")
    def reset_instance_shutdown_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstanceShutdownTimeout", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSystemPackages")
    def reset_system_packages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSystemPackages", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUseEbsOptimizedInstances")
    def reset_use_ebs_optimized_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseEbsOptimizedInstances", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIpsInput")
    def auto_assign_elastic_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignElasticIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIpsInput")
    def auto_assign_public_ips_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoAssignPublicIpsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealingInput")
    def auto_healing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoHealingInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipesInput")
    def custom_configure_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customConfigureRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipesInput")
    def custom_deploy_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customDeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArnInput")
    def custom_instance_profile_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customInstanceProfileArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJsonInput")
    def custom_json_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customJsonInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIdsInput")
    def custom_security_group_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSecurityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipesInput")
    def custom_setup_recipes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customSetupRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipesInput")
    def custom_shutdown_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customShutdownRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipesInput")
    def custom_undeploy_recipes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customUndeployRecipesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdownInput")
    def drain_elb_on_shutdown_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "drainElbOnShutdownInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolumeInput")
    def ebs_volume_input(
        self,
    ) -> typing.Optional[typing.List["OpsworksStaticWebLayerEbsVolume"]]:
        return typing.cast(typing.Optional[typing.List["OpsworksStaticWebLayerEbsVolume"]], jsii.get(self, "ebsVolumeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancerInput")
    def elastic_load_balancer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "elasticLoadBalancerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBootInput")
    def install_updates_on_boot_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "installUpdatesOnBootInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeoutInput")
    def instance_shutdown_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "instanceShutdownTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackIdInput")
    def stack_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stackIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackagesInput")
    def system_packages_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "systemPackagesInput"))

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
    @jsii.member(jsii_name="useEbsOptimizedInstancesInput")
    def use_ebs_optimized_instances_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useEbsOptimizedInstancesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignElasticIps")
    def auto_assign_elastic_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignElasticIps"))

    @auto_assign_elastic_ips.setter
    def auto_assign_elastic_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignElasticIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoAssignPublicIps")
    def auto_assign_public_ips(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoAssignPublicIps"))

    @auto_assign_public_ips.setter
    def auto_assign_public_ips(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoAssignPublicIps", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoHealing")
    def auto_healing(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoHealing"))

    @auto_healing.setter
    def auto_healing(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoHealing", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customConfigureRecipes")
    def custom_configure_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customConfigureRecipes"))

    @custom_configure_recipes.setter
    def custom_configure_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customConfigureRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDeployRecipes")
    def custom_deploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customDeployRecipes"))

    @custom_deploy_recipes.setter
    def custom_deploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customDeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customInstanceProfileArn")
    def custom_instance_profile_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customInstanceProfileArn"))

    @custom_instance_profile_arn.setter
    def custom_instance_profile_arn(self, value: builtins.str) -> None:
        jsii.set(self, "customInstanceProfileArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customJson")
    def custom_json(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customJson"))

    @custom_json.setter
    def custom_json(self, value: builtins.str) -> None:
        jsii.set(self, "customJson", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSecurityGroupIds")
    def custom_security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSecurityGroupIds"))

    @custom_security_group_ids.setter
    def custom_security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSecurityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customSetupRecipes")
    def custom_setup_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customSetupRecipes"))

    @custom_setup_recipes.setter
    def custom_setup_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customSetupRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customShutdownRecipes")
    def custom_shutdown_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customShutdownRecipes"))

    @custom_shutdown_recipes.setter
    def custom_shutdown_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customShutdownRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customUndeployRecipes")
    def custom_undeploy_recipes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customUndeployRecipes"))

    @custom_undeploy_recipes.setter
    def custom_undeploy_recipes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "customUndeployRecipes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drainElbOnShutdown")
    def drain_elb_on_shutdown(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "drainElbOnShutdown"))

    @drain_elb_on_shutdown.setter
    def drain_elb_on_shutdown(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "drainElbOnShutdown", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ebsVolume")
    def ebs_volume(self) -> typing.List["OpsworksStaticWebLayerEbsVolume"]:
        return typing.cast(typing.List["OpsworksStaticWebLayerEbsVolume"], jsii.get(self, "ebsVolume"))

    @ebs_volume.setter
    def ebs_volume(self, value: typing.List["OpsworksStaticWebLayerEbsVolume"]) -> None:
        jsii.set(self, "ebsVolume", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="elasticLoadBalancer")
    def elastic_load_balancer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "elasticLoadBalancer"))

    @elastic_load_balancer.setter
    def elastic_load_balancer(self, value: builtins.str) -> None:
        jsii.set(self, "elasticLoadBalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="installUpdatesOnBoot")
    def install_updates_on_boot(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "installUpdatesOnBoot"))

    @install_updates_on_boot.setter
    def install_updates_on_boot(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "installUpdatesOnBoot", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceShutdownTimeout")
    def instance_shutdown_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "instanceShutdownTimeout"))

    @instance_shutdown_timeout.setter
    def instance_shutdown_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "instanceShutdownTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stackId")
    def stack_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stackId"))

    @stack_id.setter
    def stack_id(self, value: builtins.str) -> None:
        jsii.set(self, "stackId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="systemPackages")
    def system_packages(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "systemPackages"))

    @system_packages.setter
    def system_packages(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "systemPackages", value)

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
    @jsii.member(jsii_name="useEbsOptimizedInstances")
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useEbsOptimizedInstances"))

    @use_ebs_optimized_instances.setter
    def use_ebs_optimized_instances(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useEbsOptimizedInstances", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksStaticWebLayerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "stack_id": "stackId",
        "auto_assign_elastic_ips": "autoAssignElasticIps",
        "auto_assign_public_ips": "autoAssignPublicIps",
        "auto_healing": "autoHealing",
        "custom_configure_recipes": "customConfigureRecipes",
        "custom_deploy_recipes": "customDeployRecipes",
        "custom_instance_profile_arn": "customInstanceProfileArn",
        "custom_json": "customJson",
        "custom_security_group_ids": "customSecurityGroupIds",
        "custom_setup_recipes": "customSetupRecipes",
        "custom_shutdown_recipes": "customShutdownRecipes",
        "custom_undeploy_recipes": "customUndeployRecipes",
        "drain_elb_on_shutdown": "drainElbOnShutdown",
        "ebs_volume": "ebsVolume",
        "elastic_load_balancer": "elasticLoadBalancer",
        "install_updates_on_boot": "installUpdatesOnBoot",
        "instance_shutdown_timeout": "instanceShutdownTimeout",
        "name": "name",
        "system_packages": "systemPackages",
        "tags": "tags",
        "tags_all": "tagsAll",
        "use_ebs_optimized_instances": "useEbsOptimizedInstances",
    },
)
class OpsworksStaticWebLayerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        stack_id: builtins.str,
        auto_assign_elastic_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_assign_public_ips: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        auto_healing: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        custom_configure_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_deploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_instance_profile_arn: typing.Optional[builtins.str] = None,
        custom_json: typing.Optional[builtins.str] = None,
        custom_security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_setup_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_shutdown_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_undeploy_recipes: typing.Optional[typing.Sequence[builtins.str]] = None,
        drain_elb_on_shutdown: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ebs_volume: typing.Optional[typing.Sequence["OpsworksStaticWebLayerEbsVolume"]] = None,
        elastic_load_balancer: typing.Optional[builtins.str] = None,
        install_updates_on_boot: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        instance_shutdown_timeout: typing.Optional[jsii.Number] = None,
        name: typing.Optional[builtins.str] = None,
        system_packages: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        use_ebs_optimized_instances: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param stack_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#stack_id OpsworksStaticWebLayer#stack_id}.
        :param auto_assign_elastic_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#auto_assign_elastic_ips OpsworksStaticWebLayer#auto_assign_elastic_ips}.
        :param auto_assign_public_ips: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#auto_assign_public_ips OpsworksStaticWebLayer#auto_assign_public_ips}.
        :param auto_healing: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#auto_healing OpsworksStaticWebLayer#auto_healing}.
        :param custom_configure_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_configure_recipes OpsworksStaticWebLayer#custom_configure_recipes}.
        :param custom_deploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_deploy_recipes OpsworksStaticWebLayer#custom_deploy_recipes}.
        :param custom_instance_profile_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_instance_profile_arn OpsworksStaticWebLayer#custom_instance_profile_arn}.
        :param custom_json: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_json OpsworksStaticWebLayer#custom_json}.
        :param custom_security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_security_group_ids OpsworksStaticWebLayer#custom_security_group_ids}.
        :param custom_setup_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_setup_recipes OpsworksStaticWebLayer#custom_setup_recipes}.
        :param custom_shutdown_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_shutdown_recipes OpsworksStaticWebLayer#custom_shutdown_recipes}.
        :param custom_undeploy_recipes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_undeploy_recipes OpsworksStaticWebLayer#custom_undeploy_recipes}.
        :param drain_elb_on_shutdown: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#drain_elb_on_shutdown OpsworksStaticWebLayer#drain_elb_on_shutdown}.
        :param ebs_volume: ebs_volume block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#ebs_volume OpsworksStaticWebLayer#ebs_volume}
        :param elastic_load_balancer: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#elastic_load_balancer OpsworksStaticWebLayer#elastic_load_balancer}.
        :param install_updates_on_boot: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#install_updates_on_boot OpsworksStaticWebLayer#install_updates_on_boot}.
        :param instance_shutdown_timeout: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#instance_shutdown_timeout OpsworksStaticWebLayer#instance_shutdown_timeout}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#name OpsworksStaticWebLayer#name}.
        :param system_packages: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#system_packages OpsworksStaticWebLayer#system_packages}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#tags OpsworksStaticWebLayer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#tags_all OpsworksStaticWebLayer#tags_all}.
        :param use_ebs_optimized_instances: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#use_ebs_optimized_instances OpsworksStaticWebLayer#use_ebs_optimized_instances}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "stack_id": stack_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auto_assign_elastic_ips is not None:
            self._values["auto_assign_elastic_ips"] = auto_assign_elastic_ips
        if auto_assign_public_ips is not None:
            self._values["auto_assign_public_ips"] = auto_assign_public_ips
        if auto_healing is not None:
            self._values["auto_healing"] = auto_healing
        if custom_configure_recipes is not None:
            self._values["custom_configure_recipes"] = custom_configure_recipes
        if custom_deploy_recipes is not None:
            self._values["custom_deploy_recipes"] = custom_deploy_recipes
        if custom_instance_profile_arn is not None:
            self._values["custom_instance_profile_arn"] = custom_instance_profile_arn
        if custom_json is not None:
            self._values["custom_json"] = custom_json
        if custom_security_group_ids is not None:
            self._values["custom_security_group_ids"] = custom_security_group_ids
        if custom_setup_recipes is not None:
            self._values["custom_setup_recipes"] = custom_setup_recipes
        if custom_shutdown_recipes is not None:
            self._values["custom_shutdown_recipes"] = custom_shutdown_recipes
        if custom_undeploy_recipes is not None:
            self._values["custom_undeploy_recipes"] = custom_undeploy_recipes
        if drain_elb_on_shutdown is not None:
            self._values["drain_elb_on_shutdown"] = drain_elb_on_shutdown
        if ebs_volume is not None:
            self._values["ebs_volume"] = ebs_volume
        if elastic_load_balancer is not None:
            self._values["elastic_load_balancer"] = elastic_load_balancer
        if install_updates_on_boot is not None:
            self._values["install_updates_on_boot"] = install_updates_on_boot
        if instance_shutdown_timeout is not None:
            self._values["instance_shutdown_timeout"] = instance_shutdown_timeout
        if name is not None:
            self._values["name"] = name
        if system_packages is not None:
            self._values["system_packages"] = system_packages
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if use_ebs_optimized_instances is not None:
            self._values["use_ebs_optimized_instances"] = use_ebs_optimized_instances

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
    def stack_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#stack_id OpsworksStaticWebLayer#stack_id}.'''
        result = self._values.get("stack_id")
        assert result is not None, "Required property 'stack_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_assign_elastic_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#auto_assign_elastic_ips OpsworksStaticWebLayer#auto_assign_elastic_ips}.'''
        result = self._values.get("auto_assign_elastic_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_assign_public_ips(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#auto_assign_public_ips OpsworksStaticWebLayer#auto_assign_public_ips}.'''
        result = self._values.get("auto_assign_public_ips")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def auto_healing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#auto_healing OpsworksStaticWebLayer#auto_healing}.'''
        result = self._values.get("auto_healing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def custom_configure_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_configure_recipes OpsworksStaticWebLayer#custom_configure_recipes}.'''
        result = self._values.get("custom_configure_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_deploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_deploy_recipes OpsworksStaticWebLayer#custom_deploy_recipes}.'''
        result = self._values.get("custom_deploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_instance_profile_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_instance_profile_arn OpsworksStaticWebLayer#custom_instance_profile_arn}.'''
        result = self._values.get("custom_instance_profile_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_json(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_json OpsworksStaticWebLayer#custom_json}.'''
        result = self._values.get("custom_json")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_security_group_ids OpsworksStaticWebLayer#custom_security_group_ids}.'''
        result = self._values.get("custom_security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_setup_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_setup_recipes OpsworksStaticWebLayer#custom_setup_recipes}.'''
        result = self._values.get("custom_setup_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_shutdown_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_shutdown_recipes OpsworksStaticWebLayer#custom_shutdown_recipes}.'''
        result = self._values.get("custom_shutdown_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_undeploy_recipes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#custom_undeploy_recipes OpsworksStaticWebLayer#custom_undeploy_recipes}.'''
        result = self._values.get("custom_undeploy_recipes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drain_elb_on_shutdown(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#drain_elb_on_shutdown OpsworksStaticWebLayer#drain_elb_on_shutdown}.'''
        result = self._values.get("drain_elb_on_shutdown")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ebs_volume(
        self,
    ) -> typing.Optional[typing.List["OpsworksStaticWebLayerEbsVolume"]]:
        '''ebs_volume block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#ebs_volume OpsworksStaticWebLayer#ebs_volume}
        '''
        result = self._values.get("ebs_volume")
        return typing.cast(typing.Optional[typing.List["OpsworksStaticWebLayerEbsVolume"]], result)

    @builtins.property
    def elastic_load_balancer(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#elastic_load_balancer OpsworksStaticWebLayer#elastic_load_balancer}.'''
        result = self._values.get("elastic_load_balancer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def install_updates_on_boot(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#install_updates_on_boot OpsworksStaticWebLayer#install_updates_on_boot}.'''
        result = self._values.get("install_updates_on_boot")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def instance_shutdown_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#instance_shutdown_timeout OpsworksStaticWebLayer#instance_shutdown_timeout}.'''
        result = self._values.get("instance_shutdown_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#name OpsworksStaticWebLayer#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def system_packages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#system_packages OpsworksStaticWebLayer#system_packages}.'''
        result = self._values.get("system_packages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#tags OpsworksStaticWebLayer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#tags_all OpsworksStaticWebLayer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def use_ebs_optimized_instances(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#use_ebs_optimized_instances OpsworksStaticWebLayer#use_ebs_optimized_instances}.'''
        result = self._values.get("use_ebs_optimized_instances")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksStaticWebLayerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksStaticWebLayerEbsVolume",
    jsii_struct_bases=[],
    name_mapping={
        "mount_point": "mountPoint",
        "number_of_disks": "numberOfDisks",
        "size": "size",
        "encrypted": "encrypted",
        "iops": "iops",
        "raid_level": "raidLevel",
        "type": "type",
    },
)
class OpsworksStaticWebLayerEbsVolume:
    def __init__(
        self,
        *,
        mount_point: builtins.str,
        number_of_disks: jsii.Number,
        size: jsii.Number,
        encrypted: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        iops: typing.Optional[jsii.Number] = None,
        raid_level: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mount_point: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#mount_point OpsworksStaticWebLayer#mount_point}.
        :param number_of_disks: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#number_of_disks OpsworksStaticWebLayer#number_of_disks}.
        :param size: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#size OpsworksStaticWebLayer#size}.
        :param encrypted: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#encrypted OpsworksStaticWebLayer#encrypted}.
        :param iops: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#iops OpsworksStaticWebLayer#iops}.
        :param raid_level: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#raid_level OpsworksStaticWebLayer#raid_level}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#type OpsworksStaticWebLayer#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "mount_point": mount_point,
            "number_of_disks": number_of_disks,
            "size": size,
        }
        if encrypted is not None:
            self._values["encrypted"] = encrypted
        if iops is not None:
            self._values["iops"] = iops
        if raid_level is not None:
            self._values["raid_level"] = raid_level
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def mount_point(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#mount_point OpsworksStaticWebLayer#mount_point}.'''
        result = self._values.get("mount_point")
        assert result is not None, "Required property 'mount_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def number_of_disks(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#number_of_disks OpsworksStaticWebLayer#number_of_disks}.'''
        result = self._values.get("number_of_disks")
        assert result is not None, "Required property 'number_of_disks' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#size OpsworksStaticWebLayer#size}.'''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def encrypted(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#encrypted OpsworksStaticWebLayer#encrypted}.'''
        result = self._values.get("encrypted")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#iops OpsworksStaticWebLayer#iops}.'''
        result = self._values.get("iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raid_level(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#raid_level OpsworksStaticWebLayer#raid_level}.'''
        result = self._values.get("raid_level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_static_web_layer#type OpsworksStaticWebLayer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksStaticWebLayerEbsVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpsworksUserProfile(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksUserProfile",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile aws_opsworks_user_profile}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ssh_username: builtins.str,
        user_arn: builtins.str,
        allow_self_management: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ssh_public_key: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile aws_opsworks_user_profile} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param ssh_username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#ssh_username OpsworksUserProfile#ssh_username}.
        :param user_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#user_arn OpsworksUserProfile#user_arn}.
        :param allow_self_management: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#allow_self_management OpsworksUserProfile#allow_self_management}.
        :param ssh_public_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#ssh_public_key OpsworksUserProfile#ssh_public_key}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = OpsworksUserProfileConfig(
            ssh_username=ssh_username,
            user_arn=user_arn,
            allow_self_management=allow_self_management,
            ssh_public_key=ssh_public_key,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAllowSelfManagement")
    def reset_allow_self_management(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowSelfManagement", []))

    @jsii.member(jsii_name="resetSshPublicKey")
    def reset_ssh_public_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshPublicKey", []))

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
    @jsii.member(jsii_name="allowSelfManagementInput")
    def allow_self_management_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "allowSelfManagementInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshPublicKeyInput")
    def ssh_public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sshPublicKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshUsernameInput")
    def ssh_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sshUsernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userArnInput")
    def user_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowSelfManagement")
    def allow_self_management(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "allowSelfManagement"))

    @allow_self_management.setter
    def allow_self_management(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "allowSelfManagement", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshPublicKey")
    def ssh_public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshPublicKey"))

    @ssh_public_key.setter
    def ssh_public_key(self, value: builtins.str) -> None:
        jsii.set(self, "sshPublicKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sshUsername")
    def ssh_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sshUsername"))

    @ssh_username.setter
    def ssh_username(self, value: builtins.str) -> None:
        jsii.set(self, "sshUsername", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userArn")
    def user_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userArn"))

    @user_arn.setter
    def user_arn(self, value: builtins.str) -> None:
        jsii.set(self, "userArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.opsworks.OpsworksUserProfileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "ssh_username": "sshUsername",
        "user_arn": "userArn",
        "allow_self_management": "allowSelfManagement",
        "ssh_public_key": "sshPublicKey",
    },
)
class OpsworksUserProfileConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        ssh_username: builtins.str,
        user_arn: builtins.str,
        allow_self_management: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ssh_public_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS OpsWorks.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param ssh_username: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#ssh_username OpsworksUserProfile#ssh_username}.
        :param user_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#user_arn OpsworksUserProfile#user_arn}.
        :param allow_self_management: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#allow_self_management OpsworksUserProfile#allow_self_management}.
        :param ssh_public_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#ssh_public_key OpsworksUserProfile#ssh_public_key}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "ssh_username": ssh_username,
            "user_arn": user_arn,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if allow_self_management is not None:
            self._values["allow_self_management"] = allow_self_management
        if ssh_public_key is not None:
            self._values["ssh_public_key"] = ssh_public_key

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
    def ssh_username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#ssh_username OpsworksUserProfile#ssh_username}.'''
        result = self._values.get("ssh_username")
        assert result is not None, "Required property 'ssh_username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#user_arn OpsworksUserProfile#user_arn}.'''
        result = self._values.get("user_arn")
        assert result is not None, "Required property 'user_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_self_management(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#allow_self_management OpsworksUserProfile#allow_self_management}.'''
        result = self._values.get("allow_self_management")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ssh_public_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/opsworks_user_profile#ssh_public_key OpsworksUserProfile#ssh_public_key}.'''
        result = self._values.get("ssh_public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpsworksUserProfileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "OpsworksApplication",
    "OpsworksApplicationAppSource",
    "OpsworksApplicationConfig",
    "OpsworksApplicationEnvironment",
    "OpsworksApplicationSslConfiguration",
    "OpsworksCustomLayer",
    "OpsworksCustomLayerConfig",
    "OpsworksCustomLayerEbsVolume",
    "OpsworksGangliaLayer",
    "OpsworksGangliaLayerConfig",
    "OpsworksGangliaLayerEbsVolume",
    "OpsworksHaproxyLayer",
    "OpsworksHaproxyLayerConfig",
    "OpsworksHaproxyLayerEbsVolume",
    "OpsworksInstance",
    "OpsworksInstanceConfig",
    "OpsworksInstanceEbsBlockDevice",
    "OpsworksInstanceEphemeralBlockDevice",
    "OpsworksInstanceRootBlockDevice",
    "OpsworksInstanceTimeouts",
    "OpsworksInstanceTimeoutsOutputReference",
    "OpsworksJavaAppLayer",
    "OpsworksJavaAppLayerConfig",
    "OpsworksJavaAppLayerEbsVolume",
    "OpsworksMemcachedLayer",
    "OpsworksMemcachedLayerConfig",
    "OpsworksMemcachedLayerEbsVolume",
    "OpsworksMysqlLayer",
    "OpsworksMysqlLayerConfig",
    "OpsworksMysqlLayerEbsVolume",
    "OpsworksNodejsAppLayer",
    "OpsworksNodejsAppLayerConfig",
    "OpsworksNodejsAppLayerEbsVolume",
    "OpsworksPermission",
    "OpsworksPermissionConfig",
    "OpsworksPhpAppLayer",
    "OpsworksPhpAppLayerConfig",
    "OpsworksPhpAppLayerEbsVolume",
    "OpsworksRailsAppLayer",
    "OpsworksRailsAppLayerConfig",
    "OpsworksRailsAppLayerEbsVolume",
    "OpsworksRdsDbInstance",
    "OpsworksRdsDbInstanceConfig",
    "OpsworksStack",
    "OpsworksStackConfig",
    "OpsworksStackCustomCookbooksSource",
    "OpsworksStaticWebLayer",
    "OpsworksStaticWebLayerConfig",
    "OpsworksStaticWebLayerEbsVolume",
    "OpsworksUserProfile",
    "OpsworksUserProfileConfig",
]

publication.publish()
