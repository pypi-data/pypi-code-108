'''
# Amazon Managed Streaming for Apache Kafka Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

[Amazon MSK](https://aws.amazon.com/msk/) is a fully managed service that makes it easy for you to build and run applications that use Apache Kafka to process streaming data.

The following example creates an MSK Cluster.

```python
# vpc: ec2.Vpc

cluster = msk.Cluster(self, "Cluster",
    cluster_name="myCluster",
    kafka_version=msk.KafkaVersion.V2_8_1,
    vpc=vpc
)
```

## Allowing Connections

To control who can access the Cluster, use the `.connections` attribute. For a list of ports used by MSK, refer to the [MSK documentation](https://docs.aws.amazon.com/msk/latest/developerguide/client-access.html#port-info).

```python
# vpc: ec2.Vpc

cluster = msk.Cluster(self, "Cluster",
    cluster_name="myCluster",
    kafka_version=msk.KafkaVersion.V2_8_1,
    vpc=vpc
)

cluster.connections.allow_from(
    ec2.Peer.ipv4("1.2.3.4/8"),
    ec2.Port.tcp(2181))
cluster.connections.allow_from(
    ec2.Peer.ipv4("1.2.3.4/8"),
    ec2.Port.tcp(9094))
```

## Cluster Endpoints

You can use the following attributes to get a list of the Kafka broker or ZooKeeper node endpoints

```python
# cluster: msk.Cluster

CfnOutput(self, "BootstrapBrokers", value=cluster.bootstrap_brokers)
CfnOutput(self, "BootstrapBrokersTls", value=cluster.bootstrap_brokers_tls)
CfnOutput(self, "BootstrapBrokersSaslScram", value=cluster.bootstrap_brokers_sasl_scram)
CfnOutput(self, "ZookeeperConnection", value=cluster.zookeeper_connection_string)
CfnOutput(self, "ZookeeperConnectionTls", value=cluster.zookeeper_connection_string_tls)
```

## Importing an existing Cluster

To import an existing MSK cluster into your CDK app use the `.fromClusterArn()` method.

```python
cluster = msk.Cluster.from_cluster_arn(self, "Cluster", "arn:aws:kafka:us-west-2:1234567890:cluster/a-cluster/11111111-1111-1111-1111-111111111111-1")
```

## Client Authentication

[MSK supports](https://docs.aws.amazon.com/msk/latest/developerguide/kafka_apis_iam.html) the following authentication mechanisms.

> Only one authentication method can be enabled.

### TLS

To enable client authentication with TLS set the `certificateAuthorityArns` property to reference your ACM Private CA. [More info on Private CAs.](https://docs.aws.amazon.com/msk/latest/developerguide/msk-authentication.html)

```python
import aws_cdk.aws_acmpca as acmpca

# vpc: ec2.Vpc

cluster = msk.Cluster(self, "Cluster",
    cluster_name="myCluster",
    kafka_version=msk.KafkaVersion.V2_8_1,
    vpc=vpc,
    encryption_in_transit=msk.EncryptionInTransitConfig(
        client_broker=msk.ClientBrokerEncryption.TLS
    ),
    client_authentication=msk.ClientAuthentication.tls(
        certificate_authorities=[
            acmpca.CertificateAuthority.from_certificate_authority_arn(self, "CertificateAuthority", "arn:aws:acm-pca:us-west-2:1234567890:certificate-authority/11111111-1111-1111-1111-111111111111")
        ]
    )
)
```

### SASL/SCRAM

Enable client authentication with [SASL/SCRAM](https://docs.aws.amazon.com/msk/latest/developerguide/msk-password.html):

```python
# vpc: ec2.Vpc

cluster = msk.Cluster(self, "cluster",
    cluster_name="myCluster",
    kafka_version=msk.KafkaVersion.V2_8_1,
    vpc=vpc,
    encryption_in_transit=msk.EncryptionInTransitConfig(
        client_broker=msk.ClientBrokerEncryption.TLS
    ),
    client_authentication=msk.ClientAuthentication.sasl(
        scram=True
    )
)
```

### SASL/IAM

Enable client authentication with [IAM](https://docs.aws.amazon.com/msk/latest/developerguide/iam-access-control.html):

```python
# vpc: ec2.Vpc

cluster = msk.Cluster(self, "cluster",
    cluster_name="myCluster",
    kafka_version=msk.KafkaVersion.V2_8_1,
    vpc=vpc,
    encryption_in_transit=msk.EncryptionInTransitConfig(
        client_broker=msk.ClientBrokerEncryption.TLS
    ),
    client_authentication=msk.ClientAuthentication.sasl(
        iam=True
    )
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
import aws_cdk.aws_acmpca
import aws_cdk.aws_ec2
import aws_cdk.aws_kms
import aws_cdk.aws_logs
import aws_cdk.aws_s3
import constructs


@jsii.data_type(
    jsii_type="@aws-cdk/aws-msk-alpha.BrokerLogging",
    jsii_struct_bases=[],
    name_mapping={
        "cloudwatch_log_group": "cloudwatchLogGroup",
        "firehose_delivery_stream_name": "firehoseDeliveryStreamName",
        "s3": "s3",
    },
)
class BrokerLogging:
    def __init__(
        self,
        *,
        cloudwatch_log_group: typing.Optional[aws_cdk.aws_logs.ILogGroup] = None,
        firehose_delivery_stream_name: typing.Optional[builtins.str] = None,
        s3: typing.Optional["S3LoggingConfiguration"] = None,
    ) -> None:
        '''(experimental) Configuration details related to broker logs.

        :param cloudwatch_log_group: (experimental) The CloudWatch Logs group that is the destination for broker logs. Default: - disabled
        :param firehose_delivery_stream_name: (experimental) The Kinesis Data Firehose delivery stream that is the destination for broker logs. Default: - disabled
        :param s3: (experimental) Details of the Amazon S3 destination for broker logs. Default: - disabled

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_msk_alpha as msk_alpha
            from aws_cdk import aws_logs as logs
            from aws_cdk import aws_s3 as s3
            
            # bucket: s3.Bucket
            # log_group: logs.LogGroup
            
            broker_logging = msk_alpha.BrokerLogging(
                cloudwatch_log_group=log_group,
                firehose_delivery_stream_name="firehoseDeliveryStreamName",
                s3=msk_alpha.S3LoggingConfiguration(
                    bucket=bucket,
            
                    # the properties below are optional
                    prefix="prefix"
                )
            )
        '''
        if isinstance(s3, dict):
            s3 = S3LoggingConfiguration(**s3)
        self._values: typing.Dict[str, typing.Any] = {}
        if cloudwatch_log_group is not None:
            self._values["cloudwatch_log_group"] = cloudwatch_log_group
        if firehose_delivery_stream_name is not None:
            self._values["firehose_delivery_stream_name"] = firehose_delivery_stream_name
        if s3 is not None:
            self._values["s3"] = s3

    @builtins.property
    def cloudwatch_log_group(self) -> typing.Optional[aws_cdk.aws_logs.ILogGroup]:
        '''(experimental) The CloudWatch Logs group that is the destination for broker logs.

        :default: - disabled

        :stability: experimental
        '''
        result = self._values.get("cloudwatch_log_group")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.ILogGroup], result)

    @builtins.property
    def firehose_delivery_stream_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Kinesis Data Firehose delivery stream that is the destination for broker logs.

        :default: - disabled

        :stability: experimental
        '''
        result = self._values.get("firehose_delivery_stream_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3(self) -> typing.Optional["S3LoggingConfiguration"]:
        '''(experimental) Details of the Amazon S3 destination for broker logs.

        :default: - disabled

        :stability: experimental
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional["S3LoggingConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BrokerLogging(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClientAuthentication(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-msk-alpha.ClientAuthentication",
):
    '''(experimental) Configuration properties for client authentication.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # vpc: ec2.Vpc
        
        cluster = msk.Cluster(self, "cluster",
            cluster_name="myCluster",
            kafka_version=msk.KafkaVersion.V2_8_1,
            vpc=vpc,
            encryption_in_transit=msk.EncryptionInTransitConfig(
                client_broker=msk.ClientBrokerEncryption.TLS
            ),
            client_authentication=msk.ClientAuthentication.sasl(
                scram=True
            )
        )
    '''

    @jsii.member(jsii_name="sasl") # type: ignore[misc]
    @builtins.classmethod
    def sasl(
        cls,
        *,
        iam: typing.Optional[builtins.bool] = None,
        key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        scram: typing.Optional[builtins.bool] = None,
    ) -> "ClientAuthentication":
        '''(experimental) SASL authentication.

        :param iam: (experimental) Enable IAM access control. Default: false
        :param key: (experimental) KMS Key to encrypt SASL/SCRAM secrets. You must use a customer master key (CMK) when creating users in secrets manager. You cannot use a Secret with Amazon MSK that uses the default Secrets Manager encryption key. Default: - CMK will be created with alias msk/{clusterName}/sasl/scram
        :param scram: (experimental) Enable SASL/SCRAM authentication. Default: false

        :stability: experimental
        '''
        props = SaslAuthProps(iam=iam, key=key, scram=scram)

        return typing.cast("ClientAuthentication", jsii.sinvoke(cls, "sasl", [props]))

    @jsii.member(jsii_name="tls") # type: ignore[misc]
    @builtins.classmethod
    def tls(
        cls,
        *,
        certificate_authorities: typing.Optional[typing.Sequence[aws_cdk.aws_acmpca.ICertificateAuthority]] = None,
    ) -> "ClientAuthentication":
        '''(experimental) TLS authentication.

        :param certificate_authorities: (experimental) List of ACM Certificate Authorities to enable TLS authentication. Default: - none

        :stability: experimental
        '''
        props = TlsAuthProps(certificate_authorities=certificate_authorities)

        return typing.cast("ClientAuthentication", jsii.sinvoke(cls, "tls", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="saslProps")
    def sasl_props(self) -> typing.Optional["SaslAuthProps"]:
        '''(experimental) - properties for SASL authentication.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["SaslAuthProps"], jsii.get(self, "saslProps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsProps")
    def tls_props(self) -> typing.Optional["TlsAuthProps"]:
        '''(experimental) - properties for TLS authentication.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["TlsAuthProps"], jsii.get(self, "tlsProps"))


@jsii.enum(jsii_type="@aws-cdk/aws-msk-alpha.ClientBrokerEncryption")
class ClientBrokerEncryption(enum.Enum):
    '''(experimental) Indicates the encryption setting for data in transit between clients and brokers.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # vpc: ec2.Vpc
        
        cluster = msk.Cluster(self, "cluster",
            cluster_name="myCluster",
            kafka_version=msk.KafkaVersion.V2_8_1,
            vpc=vpc,
            encryption_in_transit=msk.EncryptionInTransitConfig(
                client_broker=msk.ClientBrokerEncryption.TLS
            ),
            client_authentication=msk.ClientAuthentication.sasl(
                scram=True
            )
        )
    '''

    TLS = "TLS"
    '''(experimental) TLS means that client-broker communication is enabled with TLS only.

    :stability: experimental
    '''
    TLS_PLAINTEXT = "TLS_PLAINTEXT"
    '''(experimental) TLS_PLAINTEXT means that client-broker communication is enabled for both TLS-encrypted, as well as plaintext data.

    :stability: experimental
    '''
    PLAINTEXT = "PLAINTEXT"
    '''(experimental) PLAINTEXT means that client-broker communication is enabled in plaintext only.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-msk-alpha.ClusterConfigurationInfo",
    jsii_struct_bases=[],
    name_mapping={"arn": "arn", "revision": "revision"},
)
class ClusterConfigurationInfo:
    def __init__(self, *, arn: builtins.str, revision: jsii.Number) -> None:
        '''(experimental) The Amazon MSK configuration to use for the cluster.

        Note: There is currently no Cloudformation Resource to create a Configuration

        :param arn: (experimental) The Amazon Resource Name (ARN) of the MSK configuration to use. For example, arn:aws:kafka:us-east-1:123456789012:configuration/example-configuration-name/abcdabcd-1234-abcd-1234-abcd123e8e8e-1.
        :param revision: (experimental) The revision of the Amazon MSK configuration to use.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_msk_alpha as msk_alpha
            
            cluster_configuration_info = msk_alpha.ClusterConfigurationInfo(
                arn="arn",
                revision=123
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
            "revision": revision,
        }

    @builtins.property
    def arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the MSK configuration to use.

        For example, arn:aws:kafka:us-east-1:123456789012:configuration/example-configuration-name/abcdabcd-1234-abcd-1234-abcd123e8e8e-1.

        :stability: experimental
        '''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def revision(self) -> jsii.Number:
        '''(experimental) The revision of the Amazon MSK configuration to use.

        :stability: experimental
        '''
        result = self._values.get("revision")
        assert result is not None, "Required property 'revision' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterConfigurationInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-msk-alpha.ClusterMonitoringLevel")
class ClusterMonitoringLevel(enum.Enum):
    '''(experimental) The level of monitoring for the MSK cluster.

    :see: https://docs.aws.amazon.com/msk/latest/developerguide/monitoring.html#metrics-details
    :stability: experimental
    '''

    DEFAULT = "DEFAULT"
    '''(experimental) Default metrics are the essential metrics to monitor.

    :stability: experimental
    '''
    PER_BROKER = "PER_BROKER"
    '''(experimental) Per Broker metrics give you metrics at the broker level.

    :stability: experimental
    '''
    PER_TOPIC_PER_BROKER = "PER_TOPIC_PER_BROKER"
    '''(experimental) Per Topic Per Broker metrics help you understand volume at the topic level.

    :stability: experimental
    '''
    PER_TOPIC_PER_PARTITION = "PER_TOPIC_PER_PARTITION"
    '''(experimental) Per Topic Per Partition metrics help you understand consumer group lag at the topic partition level.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-msk-alpha.ClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_name": "clusterName",
        "kafka_version": "kafkaVersion",
        "vpc": "vpc",
        "client_authentication": "clientAuthentication",
        "configuration_info": "configurationInfo",
        "ebs_storage_info": "ebsStorageInfo",
        "encryption_in_transit": "encryptionInTransit",
        "instance_type": "instanceType",
        "logging": "logging",
        "monitoring": "monitoring",
        "number_of_broker_nodes": "numberOfBrokerNodes",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "vpc_subnets": "vpcSubnets",
    },
)
class ClusterProps:
    def __init__(
        self,
        *,
        cluster_name: builtins.str,
        kafka_version: "KafkaVersion",
        vpc: aws_cdk.aws_ec2.IVpc,
        client_authentication: typing.Optional[ClientAuthentication] = None,
        configuration_info: typing.Optional[ClusterConfigurationInfo] = None,
        ebs_storage_info: typing.Optional["EbsStorageInfo"] = None,
        encryption_in_transit: typing.Optional["EncryptionInTransitConfig"] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        logging: typing.Optional[BrokerLogging] = None,
        monitoring: typing.Optional["MonitoringConfiguration"] = None,
        number_of_broker_nodes: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''(experimental) Properties for a MSK Cluster.

        :param cluster_name: (experimental) The physical name of the cluster.
        :param kafka_version: (experimental) The version of Apache Kafka.
        :param vpc: (experimental) Defines the virtual networking environment for this cluster. Must have at least 2 subnets in two different AZs.
        :param client_authentication: (experimental) Configuration properties for client authentication. MSK supports using private TLS certificates or SASL/SCRAM to authenticate the identity of clients. Default: - disabled
        :param configuration_info: (experimental) The Amazon MSK configuration to use for the cluster. Default: - none
        :param ebs_storage_info: (experimental) Information about storage volumes attached to MSK broker nodes. Default: - 1000 GiB EBS volume
        :param encryption_in_transit: (experimental) Config details for encryption in transit. Default: - enabled
        :param instance_type: (experimental) The EC2 instance type that you want Amazon MSK to use when it creates your brokers. Default: kafka.m5.large
        :param logging: (experimental) Configure your MSK cluster to send broker logs to different destination types. Default: - disabled
        :param monitoring: (experimental) Cluster monitoring configuration. Default: - DEFAULT monitoring level
        :param number_of_broker_nodes: (experimental) Number of Apache Kafka brokers deployed in each Availability Zone. Default: 1
        :param removal_policy: (experimental) What to do when this resource is deleted from a stack. Default: RemovalPolicy.RETAIN
        :param security_groups: (experimental) The AWS security groups to associate with the elastic network interfaces in order to specify who can connect to and communicate with the Amazon MSK cluster. Default: - create new security group
        :param vpc_subnets: (experimental) Where to place the nodes within the VPC. Amazon MSK distributes the broker nodes evenly across the subnets that you specify. The subnets that you specify must be in distinct Availability Zones. Client subnets can't be in Availability Zone us-east-1e. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            
            cluster = msk.Cluster(self, "cluster",
                cluster_name="myCluster",
                kafka_version=msk.KafkaVersion.V2_8_1,
                vpc=vpc,
                encryption_in_transit=msk.EncryptionInTransitConfig(
                    client_broker=msk.ClientBrokerEncryption.TLS
                ),
                client_authentication=msk.ClientAuthentication.sasl(
                    scram=True
                )
            )
        '''
        if isinstance(configuration_info, dict):
            configuration_info = ClusterConfigurationInfo(**configuration_info)
        if isinstance(ebs_storage_info, dict):
            ebs_storage_info = EbsStorageInfo(**ebs_storage_info)
        if isinstance(encryption_in_transit, dict):
            encryption_in_transit = EncryptionInTransitConfig(**encryption_in_transit)
        if isinstance(logging, dict):
            logging = BrokerLogging(**logging)
        if isinstance(monitoring, dict):
            monitoring = MonitoringConfiguration(**monitoring)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_name": cluster_name,
            "kafka_version": kafka_version,
            "vpc": vpc,
        }
        if client_authentication is not None:
            self._values["client_authentication"] = client_authentication
        if configuration_info is not None:
            self._values["configuration_info"] = configuration_info
        if ebs_storage_info is not None:
            self._values["ebs_storage_info"] = ebs_storage_info
        if encryption_in_transit is not None:
            self._values["encryption_in_transit"] = encryption_in_transit
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if logging is not None:
            self._values["logging"] = logging
        if monitoring is not None:
            self._values["monitoring"] = monitoring
        if number_of_broker_nodes is not None:
            self._values["number_of_broker_nodes"] = number_of_broker_nodes
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def cluster_name(self) -> builtins.str:
        '''(experimental) The physical name of the cluster.

        :stability: experimental
        '''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kafka_version(self) -> "KafkaVersion":
        '''(experimental) The version of Apache Kafka.

        :stability: experimental
        '''
        result = self._values.get("kafka_version")
        assert result is not None, "Required property 'kafka_version' is missing"
        return typing.cast("KafkaVersion", result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''(experimental) Defines the virtual networking environment for this cluster.

        Must have at least 2 subnets in two different AZs.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def client_authentication(self) -> typing.Optional[ClientAuthentication]:
        '''(experimental) Configuration properties for client authentication.

        MSK supports using private TLS certificates or SASL/SCRAM to authenticate the identity of clients.

        :default: - disabled

        :stability: experimental
        '''
        result = self._values.get("client_authentication")
        return typing.cast(typing.Optional[ClientAuthentication], result)

    @builtins.property
    def configuration_info(self) -> typing.Optional[ClusterConfigurationInfo]:
        '''(experimental) The Amazon MSK configuration to use for the cluster.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("configuration_info")
        return typing.cast(typing.Optional[ClusterConfigurationInfo], result)

    @builtins.property
    def ebs_storage_info(self) -> typing.Optional["EbsStorageInfo"]:
        '''(experimental) Information about storage volumes attached to MSK broker nodes.

        :default: - 1000 GiB EBS volume

        :stability: experimental
        '''
        result = self._values.get("ebs_storage_info")
        return typing.cast(typing.Optional["EbsStorageInfo"], result)

    @builtins.property
    def encryption_in_transit(self) -> typing.Optional["EncryptionInTransitConfig"]:
        '''(experimental) Config details for encryption in transit.

        :default: - enabled

        :stability: experimental
        '''
        result = self._values.get("encryption_in_transit")
        return typing.cast(typing.Optional["EncryptionInTransitConfig"], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''(experimental) The EC2 instance type that you want Amazon MSK to use when it creates your brokers.

        :default: kafka.m5.large

        :see: https://docs.aws.amazon.com/msk/latest/developerguide/msk-create-cluster.html#broker-instance-types
        :stability: experimental
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def logging(self) -> typing.Optional[BrokerLogging]:
        '''(experimental) Configure your MSK cluster to send broker logs to different destination types.

        :default: - disabled

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[BrokerLogging], result)

    @builtins.property
    def monitoring(self) -> typing.Optional["MonitoringConfiguration"]:
        '''(experimental) Cluster monitoring configuration.

        :default: - DEFAULT monitoring level

        :stability: experimental
        '''
        result = self._values.get("monitoring")
        return typing.cast(typing.Optional["MonitoringConfiguration"], result)

    @builtins.property
    def number_of_broker_nodes(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of Apache Kafka brokers deployed in each Availability Zone.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("number_of_broker_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) What to do when this resource is deleted from a stack.

        :default: RemovalPolicy.RETAIN

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        '''(experimental) The AWS security groups to associate with the elastic network interfaces in order to specify who can connect to and communicate with the Amazon MSK cluster.

        :default: - create new security group

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''(experimental) Where to place the nodes within the VPC.

        Amazon MSK distributes the broker nodes evenly across the subnets that you specify.
        The subnets that you specify must be in distinct Availability Zones.
        Client subnets can't be in Availability Zone us-east-1e.

        :default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-msk-alpha.EbsStorageInfo",
    jsii_struct_bases=[],
    name_mapping={"encryption_key": "encryptionKey", "volume_size": "volumeSize"},
)
class EbsStorageInfo:
    def __init__(
        self,
        *,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        volume_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) EBS volume information.

        :param encryption_key: (experimental) The AWS KMS key for encrypting data at rest. Default: Uses AWS managed CMK (aws/kafka)
        :param volume_size: (experimental) The size in GiB of the EBS volume for the data drive on each broker node. Default: 1000

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_msk_alpha as msk_alpha
            from aws_cdk import aws_kms as kms
            
            # key: kms.Key
            
            ebs_storage_info = msk_alpha.EbsStorageInfo(
                encryption_key=key,
                volume_size=123
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if volume_size is not None:
            self._values["volume_size"] = volume_size

    @builtins.property
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''(experimental) The AWS KMS key for encrypting data at rest.

        :default: Uses AWS managed CMK (aws/kafka)

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], result)

    @builtins.property
    def volume_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The size in GiB of the EBS volume for the data drive on each broker node.

        :default: 1000

        :stability: experimental
        '''
        result = self._values.get("volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EbsStorageInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-msk-alpha.EncryptionInTransitConfig",
    jsii_struct_bases=[],
    name_mapping={
        "client_broker": "clientBroker",
        "enable_in_cluster": "enableInCluster",
    },
)
class EncryptionInTransitConfig:
    def __init__(
        self,
        *,
        client_broker: typing.Optional[ClientBrokerEncryption] = None,
        enable_in_cluster: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) The settings for encrypting data in transit.

        :param client_broker: (experimental) Indicates the encryption setting for data in transit between clients and brokers. Default: - TLS
        :param enable_in_cluster: (experimental) Indicates that data communication among the broker nodes of the cluster is encrypted. Default: true

        :see: https://docs.aws.amazon.com/msk/latest/developerguide/msk-encryption.html#msk-encryption-in-transit
        :stability: experimental
        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            
            cluster = msk.Cluster(self, "cluster",
                cluster_name="myCluster",
                kafka_version=msk.KafkaVersion.V2_8_1,
                vpc=vpc,
                encryption_in_transit=msk.EncryptionInTransitConfig(
                    client_broker=msk.ClientBrokerEncryption.TLS
                ),
                client_authentication=msk.ClientAuthentication.sasl(
                    scram=True
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if client_broker is not None:
            self._values["client_broker"] = client_broker
        if enable_in_cluster is not None:
            self._values["enable_in_cluster"] = enable_in_cluster

    @builtins.property
    def client_broker(self) -> typing.Optional[ClientBrokerEncryption]:
        '''(experimental) Indicates the encryption setting for data in transit between clients and brokers.

        :default: - TLS

        :stability: experimental
        '''
        result = self._values.get("client_broker")
        return typing.cast(typing.Optional[ClientBrokerEncryption], result)

    @builtins.property
    def enable_in_cluster(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates that data communication among the broker nodes of the cluster is encrypted.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enable_in_cluster")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptionInTransitConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-msk-alpha.ICluster")
class ICluster(
    aws_cdk.IResource,
    aws_cdk.aws_ec2.IConnectable,
    typing_extensions.Protocol,
):
    '''(experimental) Represents a MSK Cluster.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        '''(experimental) The ARN of cluster.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''(experimental) The physical name of the cluster.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IClusterProxy(
    jsii.proxy_for(aws_cdk.IResource), # type: ignore[misc]
    jsii.proxy_for(aws_cdk.aws_ec2.IConnectable), # type: ignore[misc]
):
    '''(experimental) Represents a MSK Cluster.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-msk-alpha.ICluster"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        '''(experimental) The ARN of cluster.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''(experimental) The physical name of the cluster.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICluster).__jsii_proxy_class__ = lambda : _IClusterProxy


class KafkaVersion(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-msk-alpha.KafkaVersion",
):
    '''(experimental) Kafka cluster version.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # vpc: ec2.Vpc
        
        cluster = msk.Cluster(self, "cluster",
            cluster_name="myCluster",
            kafka_version=msk.KafkaVersion.V2_8_1,
            vpc=vpc,
            encryption_in_transit=msk.EncryptionInTransitConfig(
                client_broker=msk.ClientBrokerEncryption.TLS
            ),
            client_authentication=msk.ClientAuthentication.sasl(
                scram=True
            )
        )
    '''

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, version: builtins.str) -> "KafkaVersion":
        '''(experimental) Custom cluster version.

        :param version: custom version number.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sinvoke(cls, "of", [version]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_1_1")
    def V1_1_1(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 1.1.1.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V1_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_2_1")
    def V2_2_1(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.2.1.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_2_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_3_1")
    def V2_3_1(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.3.1.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_3_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_4_1_1")
    def V2_4_1_1(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.4.1.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_4_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_5_1")
    def V2_5_1(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.5.1.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_5_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_6_0")
    def V2_6_0(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.6.0.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_6_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_6_1")
    def V2_6_1(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.6.1.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_6_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_6_2")
    def V2_6_2(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.6.2.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_6_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_6_3")
    def V2_6_3(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.6.3.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_6_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_7_0")
    def V2_7_0(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.7.0.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_7_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_7_1")
    def V2_7_1(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.7.1.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_7_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_7_2")
    def V2_7_2(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.7.2.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_7_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_8_0")
    def V2_8_0(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.8.0.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_8_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V2_8_1")
    def V2_8_1(cls) -> "KafkaVersion":
        '''(experimental) Kafka version 2.8.1.

        :stability: experimental
        '''
        return typing.cast("KafkaVersion", jsii.sget(cls, "V2_8_1"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''(experimental) cluster version number.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-msk-alpha.MonitoringConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_monitoring_level": "clusterMonitoringLevel",
        "enable_prometheus_jmx_exporter": "enablePrometheusJmxExporter",
        "enable_prometheus_node_exporter": "enablePrometheusNodeExporter",
    },
)
class MonitoringConfiguration:
    def __init__(
        self,
        *,
        cluster_monitoring_level: typing.Optional[ClusterMonitoringLevel] = None,
        enable_prometheus_jmx_exporter: typing.Optional[builtins.bool] = None,
        enable_prometheus_node_exporter: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Monitoring Configuration.

        :param cluster_monitoring_level: (experimental) Specifies the level of monitoring for the MSK cluster. Default: DEFAULT
        :param enable_prometheus_jmx_exporter: (experimental) Indicates whether you want to enable or disable the JMX Exporter. Default: false
        :param enable_prometheus_node_exporter: (experimental) Indicates whether you want to enable or disable the Prometheus Node Exporter. You can use the Prometheus Node Exporter to get CPU and disk metrics for the broker nodes. Default: false

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_msk_alpha as msk_alpha
            
            monitoring_configuration = msk_alpha.MonitoringConfiguration(
                cluster_monitoring_level=msk_alpha.ClusterMonitoringLevel.DEFAULT,
                enable_prometheus_jmx_exporter=False,
                enable_prometheus_node_exporter=False
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cluster_monitoring_level is not None:
            self._values["cluster_monitoring_level"] = cluster_monitoring_level
        if enable_prometheus_jmx_exporter is not None:
            self._values["enable_prometheus_jmx_exporter"] = enable_prometheus_jmx_exporter
        if enable_prometheus_node_exporter is not None:
            self._values["enable_prometheus_node_exporter"] = enable_prometheus_node_exporter

    @builtins.property
    def cluster_monitoring_level(self) -> typing.Optional[ClusterMonitoringLevel]:
        '''(experimental) Specifies the level of monitoring for the MSK cluster.

        :default: DEFAULT

        :stability: experimental
        '''
        result = self._values.get("cluster_monitoring_level")
        return typing.cast(typing.Optional[ClusterMonitoringLevel], result)

    @builtins.property
    def enable_prometheus_jmx_exporter(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether you want to enable or disable the JMX Exporter.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_prometheus_jmx_exporter")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_prometheus_node_exporter(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Indicates whether you want to enable or disable the Prometheus Node Exporter.

        You can use the Prometheus Node Exporter to get CPU and disk metrics for the broker nodes.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_prometheus_node_exporter")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MonitoringConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-msk-alpha.S3LoggingConfiguration",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "prefix": "prefix"},
)
class S3LoggingConfiguration:
    def __init__(
        self,
        *,
        bucket: aws_cdk.aws_s3.IBucket,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Details of the Amazon S3 destination for broker logs.

        :param bucket: (experimental) The S3 bucket that is the destination for broker logs.
        :param prefix: (experimental) The S3 prefix that is the destination for broker logs. Default: - no prefix

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_msk_alpha as msk_alpha
            from aws_cdk import aws_s3 as s3
            
            # bucket: s3.Bucket
            
            s3_logging_configuration = msk_alpha.S3LoggingConfiguration(
                bucket=bucket,
            
                # the properties below are optional
                prefix="prefix"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket": bucket,
        }
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def bucket(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) The S3 bucket that is the destination for broker logs.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) The S3 prefix that is the destination for broker logs.

        :default: - no prefix

        :stability: experimental
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3LoggingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-msk-alpha.SaslAuthProps",
    jsii_struct_bases=[],
    name_mapping={"iam": "iam", "key": "key", "scram": "scram"},
)
class SaslAuthProps:
    def __init__(
        self,
        *,
        iam: typing.Optional[builtins.bool] = None,
        key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        scram: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) SASL authentication properties.

        :param iam: (experimental) Enable IAM access control. Default: false
        :param key: (experimental) KMS Key to encrypt SASL/SCRAM secrets. You must use a customer master key (CMK) when creating users in secrets manager. You cannot use a Secret with Amazon MSK that uses the default Secrets Manager encryption key. Default: - CMK will be created with alias msk/{clusterName}/sasl/scram
        :param scram: (experimental) Enable SASL/SCRAM authentication. Default: false

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # vpc: ec2.Vpc
            
            cluster = msk.Cluster(self, "cluster",
                cluster_name="myCluster",
                kafka_version=msk.KafkaVersion.V2_8_1,
                vpc=vpc,
                encryption_in_transit=msk.EncryptionInTransitConfig(
                    client_broker=msk.ClientBrokerEncryption.TLS
                ),
                client_authentication=msk.ClientAuthentication.sasl(
                    scram=True
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if iam is not None:
            self._values["iam"] = iam
        if key is not None:
            self._values["key"] = key
        if scram is not None:
            self._values["scram"] = scram

    @builtins.property
    def iam(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable IAM access control.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("iam")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''(experimental) KMS Key to encrypt SASL/SCRAM secrets.

        You must use a customer master key (CMK) when creating users in secrets manager.
        You cannot use a Secret with Amazon MSK that uses the default Secrets Manager encryption key.

        :default: - CMK will be created with alias msk/{clusterName}/sasl/scram

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], result)

    @builtins.property
    def scram(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable SASL/SCRAM authentication.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("scram")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SaslAuthProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-msk-alpha.TlsAuthProps",
    jsii_struct_bases=[],
    name_mapping={"certificate_authorities": "certificateAuthorities"},
)
class TlsAuthProps:
    def __init__(
        self,
        *,
        certificate_authorities: typing.Optional[typing.Sequence[aws_cdk.aws_acmpca.ICertificateAuthority]] = None,
    ) -> None:
        '''(experimental) TLS authentication properties.

        :param certificate_authorities: (experimental) List of ACM Certificate Authorities to enable TLS authentication. Default: - none

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_acmpca as acmpca
            
            # vpc: ec2.Vpc
            
            cluster = msk.Cluster(self, "Cluster",
                cluster_name="myCluster",
                kafka_version=msk.KafkaVersion.V2_8_1,
                vpc=vpc,
                encryption_in_transit=msk.EncryptionInTransitConfig(
                    client_broker=msk.ClientBrokerEncryption.TLS
                ),
                client_authentication=msk.ClientAuthentication.tls(
                    certificate_authorities=[
                        acmpca.CertificateAuthority.from_certificate_authority_arn(self, "CertificateAuthority", "arn:aws:acm-pca:us-west-2:1234567890:certificate-authority/11111111-1111-1111-1111-111111111111")
                    ]
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if certificate_authorities is not None:
            self._values["certificate_authorities"] = certificate_authorities

    @builtins.property
    def certificate_authorities(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_acmpca.ICertificateAuthority]]:
        '''(experimental) List of ACM Certificate Authorities to enable TLS authentication.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("certificate_authorities")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_acmpca.ICertificateAuthority]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TlsAuthProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ICluster)
class Cluster(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-msk-alpha.Cluster",
):
    '''(experimental) Create a MSK Cluster.

    :stability: experimental
    :exampleMetadata: infused
    :resource: AWS::MSK::Cluster

    Example::

        # vpc: ec2.Vpc
        
        cluster = msk.Cluster(self, "cluster",
            cluster_name="myCluster",
            kafka_version=msk.KafkaVersion.V2_8_1,
            vpc=vpc,
            encryption_in_transit=msk.EncryptionInTransitConfig(
                client_broker=msk.ClientBrokerEncryption.TLS
            ),
            client_authentication=msk.ClientAuthentication.sasl(
                scram=True
            )
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_name: builtins.str,
        kafka_version: KafkaVersion,
        vpc: aws_cdk.aws_ec2.IVpc,
        client_authentication: typing.Optional[ClientAuthentication] = None,
        configuration_info: typing.Optional[ClusterConfigurationInfo] = None,
        ebs_storage_info: typing.Optional[EbsStorageInfo] = None,
        encryption_in_transit: typing.Optional[EncryptionInTransitConfig] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        logging: typing.Optional[BrokerLogging] = None,
        monitoring: typing.Optional[MonitoringConfiguration] = None,
        number_of_broker_nodes: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster_name: (experimental) The physical name of the cluster.
        :param kafka_version: (experimental) The version of Apache Kafka.
        :param vpc: (experimental) Defines the virtual networking environment for this cluster. Must have at least 2 subnets in two different AZs.
        :param client_authentication: (experimental) Configuration properties for client authentication. MSK supports using private TLS certificates or SASL/SCRAM to authenticate the identity of clients. Default: - disabled
        :param configuration_info: (experimental) The Amazon MSK configuration to use for the cluster. Default: - none
        :param ebs_storage_info: (experimental) Information about storage volumes attached to MSK broker nodes. Default: - 1000 GiB EBS volume
        :param encryption_in_transit: (experimental) Config details for encryption in transit. Default: - enabled
        :param instance_type: (experimental) The EC2 instance type that you want Amazon MSK to use when it creates your brokers. Default: kafka.m5.large
        :param logging: (experimental) Configure your MSK cluster to send broker logs to different destination types. Default: - disabled
        :param monitoring: (experimental) Cluster monitoring configuration. Default: - DEFAULT monitoring level
        :param number_of_broker_nodes: (experimental) Number of Apache Kafka brokers deployed in each Availability Zone. Default: 1
        :param removal_policy: (experimental) What to do when this resource is deleted from a stack. Default: RemovalPolicy.RETAIN
        :param security_groups: (experimental) The AWS security groups to associate with the elastic network interfaces in order to specify who can connect to and communicate with the Amazon MSK cluster. Default: - create new security group
        :param vpc_subnets: (experimental) Where to place the nodes within the VPC. Amazon MSK distributes the broker nodes evenly across the subnets that you specify. The subnets that you specify must be in distinct Availability Zones. Client subnets can't be in Availability Zone us-east-1e. Default: - the Vpc default strategy if not specified.

        :stability: experimental
        '''
        props = ClusterProps(
            cluster_name=cluster_name,
            kafka_version=kafka_version,
            vpc=vpc,
            client_authentication=client_authentication,
            configuration_info=configuration_info,
            ebs_storage_info=ebs_storage_info,
            encryption_in_transit=encryption_in_transit,
            instance_type=instance_type,
            logging=logging,
            monitoring=monitoring,
            number_of_broker_nodes=number_of_broker_nodes,
            removal_policy=removal_policy,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromClusterArn") # type: ignore[misc]
    @builtins.classmethod
    def from_cluster_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        cluster_arn: builtins.str,
    ) -> ICluster:
        '''(experimental) Reference an existing cluster, defined outside of the CDK code, by name.

        :param scope: -
        :param id: -
        :param cluster_arn: -

        :stability: experimental
        '''
        return typing.cast(ICluster, jsii.sinvoke(cls, "fromClusterArn", [scope, id, cluster_arn]))

    @jsii.member(jsii_name="addUser")
    def add_user(self, *usernames: builtins.str) -> None:
        '''(experimental) A list of usersnames to register with the cluster.

        The password will automatically be generated using Secrets
        Manager and the { username, password } JSON object stored in Secrets Manager as ``AmazonMSK_username``.

        Must be using the SASL/SCRAM authentication mechanism.

        :param usernames: - username(s) to register with the cluster.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addUser", [*usernames]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokers")
    def bootstrap_brokers(self) -> builtins.str:
        '''(experimental) Get the list of brokers that a client application can use to bootstrap.

        Uses a Custom Resource to make an API call to ``getBootstrapBrokers`` using the Javascript SDK

        :return: - A string containing one or more hostname:port pairs.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersSaslScram")
    def bootstrap_brokers_sasl_scram(self) -> builtins.str:
        '''(experimental) Get the list of brokers that a SASL/SCRAM authenticated client application can use to bootstrap.

        Uses a Custom Resource to make an API call to ``getBootstrapBrokers`` using the Javascript SDK

        :return: - A string containing one or more dns name (or IP) and SASL SCRAM port pairs.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersSaslScram"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bootstrapBrokersTls")
    def bootstrap_brokers_tls(self) -> builtins.str:
        '''(experimental) Get the list of brokers that a TLS authenticated client application can use to bootstrap.

        Uses a Custom Resource to make an API call to ``getBootstrapBrokers`` using the Javascript SDK

        :return: - A string containing one or more DNS names (or IP) and TLS port pairs.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "bootstrapBrokersTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        '''(experimental) The ARN of cluster.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        '''(experimental) The physical name of the cluster.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''(experimental) Manages connections for the cluster.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zookeeperConnectionString")
    def zookeeper_connection_string(self) -> builtins.str:
        '''(experimental) Get the ZooKeeper Connection string.

        Uses a Custom Resource to make an API call to ``describeCluster`` using the Javascript SDK

        :return: - The connection string to use to connect to the Apache ZooKeeper cluster.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "zookeeperConnectionString"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zookeeperConnectionStringTls")
    def zookeeper_connection_string_tls(self) -> builtins.str:
        '''(experimental) Get the ZooKeeper Connection string for a TLS enabled cluster.

        Uses a Custom Resource to make an API call to ``describeCluster`` using the Javascript SDK

        :return: - The connection string to use to connect to zookeeper cluster on TLS port.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "zookeeperConnectionStringTls"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="saslScramAuthenticationKey")
    def sasl_scram_authentication_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''(experimental) Key used to encrypt SASL/SCRAM users.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], jsii.get(self, "saslScramAuthenticationKey"))


__all__ = [
    "BrokerLogging",
    "ClientAuthentication",
    "ClientBrokerEncryption",
    "Cluster",
    "ClusterConfigurationInfo",
    "ClusterMonitoringLevel",
    "ClusterProps",
    "EbsStorageInfo",
    "EncryptionInTransitConfig",
    "ICluster",
    "KafkaVersion",
    "MonitoringConfiguration",
    "S3LoggingConfiguration",
    "SaslAuthProps",
    "TlsAuthProps",
]

publication.publish()
