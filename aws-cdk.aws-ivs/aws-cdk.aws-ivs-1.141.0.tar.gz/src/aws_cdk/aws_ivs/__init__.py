'''
# AWS::IVS Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

> All classes with the `Cfn` prefix in this module ([CFN Resources](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) are always stable and safe to use.

![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

Amazon Interactive Video Service (Amazon IVS) is a managed live streaming
solution that is quick and easy to set up, and ideal for creating interactive
video experiences. Send your live streams to Amazon IVS using streaming software
and the service does everything you need to make low-latency live video
available to any viewer around the world, letting you focus on building
interactive experiences alongside the live video. You can easily customize and
enhance the audience experience through the Amazon IVS player SDK and timed
metadata APIs, allowing you to build a more valuable relationship with your
viewers on your own websites and applications.

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

## Channels

An Amazon IVS channel stores configuration information related to your live
stream. You first create a channel and then contribute video to it using the
channel’s stream key to start your live stream.

You can create a channel

```python
my_channel = ivs.Channel(self, "Channel")
```

### Importing an existing channel

You can reference an existing channel, for example, if you need to create a
stream key for an existing channel

```python
my_channel = ivs.Channel.from_channel_arn(self, "Channel", my_channel_arn)
```

## Stream Keys

A Stream Key is used by a broadcast encoder to initiate a stream and identify
to Amazon IVS which customer and channel the stream is for. If you are
storing this value, it should be treated as if it were a password.

You can create a stream key for a given channel

```python
my_stream_key = my_channel.add_stream_key("StreamKey")
```

## Private Channels

Amazon IVS offers the ability to create private channels, allowing
you to restrict your streams by channel or viewer. You control access
to video playback by enabling playback authorization on channels and
generating signed JSON Web Tokens (JWTs) for authorized playback requests.

A playback token is a JWT that you sign (with a playback authorization key)
and include with every playback request for a channel that has playback
authorization enabled.

In order for Amazon IVS to validate the token, you need to upload
the public key that corresponds to the private key you use to sign the token.

```python
key_pair = ivs.PlaybackKeyPair(self, "PlaybackKeyPair",
    public_key_material=my_public_key_pem_string
)
```

Then, when creating a channel, specify the authorized property

```python
my_channel = ivs.Channel(self, "Channel",
    authorized=True
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

import aws_cdk.core
import constructs


@jsii.implements(aws_cdk.core.IInspectable)
class CfnChannel(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs.CfnChannel",
):
    '''A CloudFormation ``AWS::IVS::Channel``.

    The ``AWS::IVS::Channel`` resource specifies an  channel. A channel stores configuration information related to your live stream. For more information, see `CreateChannel <https://docs.aws.amazon.com/ivs/latest/APIReference/API_CreateChannel.html>`_ in the *Amazon Interactive Video Service API Reference* .
    .. epigraph::

       By default, the IVS API CreateChannel endpoint creates a stream key in addition to a channel. The  Channel resource *does not* create a stream key; to create a stream key, use the StreamKey resource instead.

    :cloudformationResource: AWS::IVS::Channel
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_ivs as ivs
        
        cfn_channel = ivs.CfnChannel(self, "MyCfnChannel",
            authorized=False,
            latency_mode="latencyMode",
            name="name",
            recording_configuration_arn="recordingConfigurationArn",
            tags=[CfnTag(
                key="key",
                value="value"
            )],
            type="type"
        )
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        authorized: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
        latency_mode: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        recording_configuration_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new ``AWS::IVS::Channel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param authorized: Whether the channel is authorized. *Default* : ``false``
        :param latency_mode: Channel latency mode. Valid values:. - ``NORMAL`` : Use NORMAL to broadcast and deliver live video up to Full HD. - ``LOW`` : Use LOW for near real-time interactions with viewers. .. epigraph:: In the console, ``LOW`` and ``NORMAL`` correspond to ``Ultra-low`` and ``Standard`` , respectively. *Default* : ``LOW``
        :param name: Channel name.
        :param recording_configuration_arn: The ARN of a RecordingConfiguration resource. An empty string indicates that recording is disabled for the channel. A RecordingConfiguration ARN indicates that recording is enabled using the specified recording configuration. See the `RecordingConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html>`_ resource for more information and an example. *Default* : "" (empty string, recording is disabled)
        :param tags: An array of key-value pairs to apply to this resource. For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .
        :param type: The channel type, which determines the allowable resolution and bitrate. *If you exceed the allowable resolution or bitrate, the stream probably will disconnect immediately.* Valid values: - ``STANDARD`` : Multiple qualities are generated from the original input, to automatically give viewers the best experience for their devices and network conditions. Resolution can be up to 1080p and bitrate can be up to 8.5 Mbps. Audio is transcoded only for renditions 360p and below; above that, audio is passed through. - ``BASIC`` : delivers the original input to viewers. The viewer’s video-quality choice is limited to the original input. Resolution can be up to 480p and bitrate can be up to 1.5 Mbps. *Default* : ``STANDARD``
        '''
        props = CfnChannelProps(
            authorized=authorized,
            latency_mode=latency_mode,
            name=name,
            recording_configuration_arn=recording_configuration_arn,
            tags=tags,
            type=type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''The channel ARN.

        For example: ``arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh``

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrIngestEndpoint")
    def attr_ingest_endpoint(self) -> builtins.str:
        '''Channel ingest endpoint, part of the definition of an ingest server, used when you set up streaming software.

        For example: ``a1b2c3d4e5f6.global-contribute.live-video.net``

        :cloudformationAttribute: IngestEndpoint
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrIngestEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrPlaybackUrl")
    def attr_playback_url(self) -> builtins.str:
        '''Channel playback URL.

        For example: ``https://a1b2c3d4e5f6.us-west-2.playback.live-video.net/api/video/v1/us-west-2.123456789012.channel.abcdEFGH.m3u8``

        :cloudformationAttribute: PlaybackUrl
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrPlaybackUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''An array of key-value pairs to apply to this resource.

        For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorized")
    def authorized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
        '''Whether the channel is authorized.

        *Default* : ``false``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-authorized
        '''
        return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], jsii.get(self, "authorized"))

    @authorized.setter
    def authorized(
        self,
        value: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]],
    ) -> None:
        jsii.set(self, "authorized", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latencyMode")
    def latency_mode(self) -> typing.Optional[builtins.str]:
        '''Channel latency mode. Valid values:.

        - ``NORMAL`` : Use NORMAL to broadcast and deliver live video up to Full HD.
        - ``LOW`` : Use LOW for near real-time interactions with viewers.

        .. epigraph::

           In the  console, ``LOW`` and ``NORMAL`` correspond to ``Ultra-low`` and ``Standard`` , respectively.

        *Default* : ``LOW``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-latencymode
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "latencyMode"))

    @latency_mode.setter
    def latency_mode(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "latencyMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''Channel name.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recordingConfigurationArn")
    def recording_configuration_arn(self) -> typing.Optional[builtins.str]:
        '''The ARN of a RecordingConfiguration resource.

        An empty string indicates that recording is disabled for the channel. A RecordingConfiguration ARN indicates that recording is enabled using the specified recording configuration. See the `RecordingConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html>`_ resource for more information and an example.

        *Default* : "" (empty string, recording is disabled)

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-recordingconfigurationarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "recordingConfigurationArn"))

    @recording_configuration_arn.setter
    def recording_configuration_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "recordingConfigurationArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> typing.Optional[builtins.str]:
        '''The channel type, which determines the allowable resolution and bitrate.

        *If you exceed the allowable resolution or bitrate, the stream probably will disconnect immediately.* Valid values:

        - ``STANDARD`` : Multiple qualities are generated from the original input, to automatically give viewers the best experience for their devices and network conditions. Resolution can be up to 1080p and bitrate can be up to 8.5 Mbps. Audio is transcoded only for renditions 360p and below; above that, audio is passed through.
        - ``BASIC`` : delivers the original input to viewers. The viewer’s video-quality choice is limited to the original input. Resolution can be up to 480p and bitrate can be up to 1.5 Mbps.

        *Default* : ``STANDARD``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-type
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "type"))

    @type.setter
    def type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs.CfnChannelProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorized": "authorized",
        "latency_mode": "latencyMode",
        "name": "name",
        "recording_configuration_arn": "recordingConfigurationArn",
        "tags": "tags",
        "type": "type",
    },
)
class CfnChannelProps:
    def __init__(
        self,
        *,
        authorized: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
        latency_mode: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        recording_configuration_arn: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for defining a ``CfnChannel``.

        :param authorized: Whether the channel is authorized. *Default* : ``false``
        :param latency_mode: Channel latency mode. Valid values:. - ``NORMAL`` : Use NORMAL to broadcast and deliver live video up to Full HD. - ``LOW`` : Use LOW for near real-time interactions with viewers. .. epigraph:: In the console, ``LOW`` and ``NORMAL`` correspond to ``Ultra-low`` and ``Standard`` , respectively. *Default* : ``LOW``
        :param name: Channel name.
        :param recording_configuration_arn: The ARN of a RecordingConfiguration resource. An empty string indicates that recording is disabled for the channel. A RecordingConfiguration ARN indicates that recording is enabled using the specified recording configuration. See the `RecordingConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html>`_ resource for more information and an example. *Default* : "" (empty string, recording is disabled)
        :param tags: An array of key-value pairs to apply to this resource. For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .
        :param type: The channel type, which determines the allowable resolution and bitrate. *If you exceed the allowable resolution or bitrate, the stream probably will disconnect immediately.* Valid values: - ``STANDARD`` : Multiple qualities are generated from the original input, to automatically give viewers the best experience for their devices and network conditions. Resolution can be up to 1080p and bitrate can be up to 8.5 Mbps. Audio is transcoded only for renditions 360p and below; above that, audio is passed through. - ``BASIC`` : delivers the original input to viewers. The viewer’s video-quality choice is limited to the original input. Resolution can be up to 480p and bitrate can be up to 1.5 Mbps. *Default* : ``STANDARD``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_ivs as ivs
            
            cfn_channel_props = ivs.CfnChannelProps(
                authorized=False,
                latency_mode="latencyMode",
                name="name",
                recording_configuration_arn="recordingConfigurationArn",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )],
                type="type"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if authorized is not None:
            self._values["authorized"] = authorized
        if latency_mode is not None:
            self._values["latency_mode"] = latency_mode
        if name is not None:
            self._values["name"] = name
        if recording_configuration_arn is not None:
            self._values["recording_configuration_arn"] = recording_configuration_arn
        if tags is not None:
            self._values["tags"] = tags
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def authorized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
        '''Whether the channel is authorized.

        *Default* : ``false``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-authorized
        '''
        result = self._values.get("authorized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]], result)

    @builtins.property
    def latency_mode(self) -> typing.Optional[builtins.str]:
        '''Channel latency mode. Valid values:.

        - ``NORMAL`` : Use NORMAL to broadcast and deliver live video up to Full HD.
        - ``LOW`` : Use LOW for near real-time interactions with viewers.

        .. epigraph::

           In the  console, ``LOW`` and ``NORMAL`` correspond to ``Ultra-low`` and ``Standard`` , respectively.

        *Default* : ``LOW``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-latencymode
        '''
        result = self._values.get("latency_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Channel name.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recording_configuration_arn(self) -> typing.Optional[builtins.str]:
        '''The ARN of a RecordingConfiguration resource.

        An empty string indicates that recording is disabled for the channel. A RecordingConfiguration ARN indicates that recording is enabled using the specified recording configuration. See the `RecordingConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html>`_ resource for more information and an example.

        *Default* : "" (empty string, recording is disabled)

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-recordingconfigurationarn
        '''
        result = self._values.get("recording_configuration_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        '''An array of key-value pairs to apply to this resource.

        For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.core.CfnTag]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''The channel type, which determines the allowable resolution and bitrate.

        *If you exceed the allowable resolution or bitrate, the stream probably will disconnect immediately.* Valid values:

        - ``STANDARD`` : Multiple qualities are generated from the original input, to automatically give viewers the best experience for their devices and network conditions. Resolution can be up to 1080p and bitrate can be up to 8.5 Mbps. Audio is transcoded only for renditions 360p and below; above that, audio is passed through.
        - ``BASIC`` : delivers the original input to viewers. The viewer’s video-quality choice is limited to the original input. Resolution can be up to 480p and bitrate can be up to 1.5 Mbps.

        *Default* : ``STANDARD``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html#cfn-ivs-channel-type
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnChannelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnPlaybackKeyPair(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs.CfnPlaybackKeyPair",
):
    '''A CloudFormation ``AWS::IVS::PlaybackKeyPair``.

    The ``AWS::IVS::PlaybackKeyPair`` resource specifies an  playback key pair.  uses a public playback key to validate playback tokens that have been signed with the corresponding private key. For more information, see `Setting Up Private Channels <https://docs.aws.amazon.com/ivs/latest/userguide/private-channels.html>`_ in the *Amazon Interactive Video Service User Guide* .

    :cloudformationResource: AWS::IVS::PlaybackKeyPair
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_ivs as ivs
        
        cfn_playback_key_pair = ivs.CfnPlaybackKeyPair(self, "MyCfnPlaybackKeyPair",
            public_key_material="publicKeyMaterial",
        
            # the properties below are optional
            name="name",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        public_key_material: builtins.str,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Create a new ``AWS::IVS::PlaybackKeyPair``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param public_key_material: The public portion of a customer-generated key pair.
        :param name: Playback-key-pair name. The value does not need to be unique.
        :param tags: An array of key-value pairs to apply to this resource. For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .
        '''
        props = CfnPlaybackKeyPairProps(
            public_key_material=public_key_material, name=name, tags=tags
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''Key-pair ARN.

        For example: ``arn:aws:ivs:us-west-2:693991300569:playback-key/f99cde61-c2b0-4df3-8941-ca7d38acca1a``

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrFingerprint")
    def attr_fingerprint(self) -> builtins.str:
        '''Key-pair identifier.

        For example: ``98:0d:1a:a0:19:96:1e:ea:0a:0a:2c:9a:42:19:2b:e7``

        :cloudformationAttribute: Fingerprint
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrFingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''An array of key-value pairs to apply to this resource.

        For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyMaterial")
    def public_key_material(self) -> builtins.str:
        '''The public portion of a customer-generated key pair.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-publickeymaterial
        '''
        return typing.cast(builtins.str, jsii.get(self, "publicKeyMaterial"))

    @public_key_material.setter
    def public_key_material(self, value: builtins.str) -> None:
        jsii.set(self, "publicKeyMaterial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''Playback-key-pair name.

        The value does not need to be unique.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs.CfnPlaybackKeyPairProps",
    jsii_struct_bases=[],
    name_mapping={
        "public_key_material": "publicKeyMaterial",
        "name": "name",
        "tags": "tags",
    },
)
class CfnPlaybackKeyPairProps:
    def __init__(
        self,
        *,
        public_key_material: builtins.str,
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Properties for defining a ``CfnPlaybackKeyPair``.

        :param public_key_material: The public portion of a customer-generated key pair.
        :param name: Playback-key-pair name. The value does not need to be unique.
        :param tags: An array of key-value pairs to apply to this resource. For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_ivs as ivs
            
            cfn_playback_key_pair_props = ivs.CfnPlaybackKeyPairProps(
                public_key_material="publicKeyMaterial",
            
                # the properties below are optional
                name="name",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "public_key_material": public_key_material,
        }
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def public_key_material(self) -> builtins.str:
        '''The public portion of a customer-generated key pair.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-publickeymaterial
        '''
        result = self._values.get("public_key_material")
        assert result is not None, "Required property 'public_key_material' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Playback-key-pair name.

        The value does not need to be unique.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        '''An array of key-value pairs to apply to this resource.

        For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-playbackkeypair.html#cfn-ivs-playbackkeypair-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.core.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnPlaybackKeyPairProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnRecordingConfiguration(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs.CfnRecordingConfiguration",
):
    '''A CloudFormation ``AWS::IVS::RecordingConfiguration``.

    The ``AWS::IVS::RecordingConfiguration`` resource specifies an  recording configuration. A recording configuration enables the recording of a channel’s live streams to a data store. Multiple channels can reference the same recording configuration. For more information, see `RecordingConfiguration <https://docs.aws.amazon.com/ivs/latest/APIReference/API_RecordingConfiguration.html>`_ in the *Amazon Interactive Video Service API Reference* .

    :cloudformationResource: AWS::IVS::RecordingConfiguration
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_ivs as ivs
        
        cfn_recording_configuration = ivs.CfnRecordingConfiguration(self, "MyCfnRecordingConfiguration",
            destination_configuration=ivs.CfnRecordingConfiguration.DestinationConfigurationProperty(
                s3=ivs.CfnRecordingConfiguration.S3DestinationConfigurationProperty(
                    bucket_name="bucketName"
                )
            ),
        
            # the properties below are optional
            name="name",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        destination_configuration: typing.Union[aws_cdk.core.IResolvable, "CfnRecordingConfiguration.DestinationConfigurationProperty"],
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Create a new ``AWS::IVS::RecordingConfiguration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param destination_configuration: A destination configuration contains information about where recorded video will be stored. See the `DestinationConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-destinationconfiguration.html>`_ property type for more information.
        :param name: Recording-configuration name. The value does not need to be unique.
        :param tags: An array of key-value pairs to apply to this resource. For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .
        '''
        props = CfnRecordingConfigurationProps(
            destination_configuration=destination_configuration, name=name, tags=tags
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''The recording configuration ARN.

        For example: ``arn:aws:ivs:us-west-2:123456789012:recording-configuration/abcdABCDefgh``

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrState")
    def attr_state(self) -> builtins.str:
        '''Indicates the current state of the recording configuration.

        When the state is ``ACTIVE`` , the configuration is ready to record a channel stream. Valid values: ``CREATING`` | ``CREATE_FAILED`` | ``ACTIVE`` .

        :cloudformationAttribute: State
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrState"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''An array of key-value pairs to apply to this resource.

        For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destinationConfiguration")
    def destination_configuration(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, "CfnRecordingConfiguration.DestinationConfigurationProperty"]:
        '''A destination configuration contains information about where recorded video will be stored.

        See the `DestinationConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-destinationconfiguration.html>`_ property type for more information.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-destinationconfiguration
        '''
        return typing.cast(typing.Union[aws_cdk.core.IResolvable, "CfnRecordingConfiguration.DestinationConfigurationProperty"], jsii.get(self, "destinationConfiguration"))

    @destination_configuration.setter
    def destination_configuration(
        self,
        value: typing.Union[aws_cdk.core.IResolvable, "CfnRecordingConfiguration.DestinationConfigurationProperty"],
    ) -> None:
        jsii.set(self, "destinationConfiguration", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''Recording-configuration name.

        The value does not need to be unique.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-ivs.CfnRecordingConfiguration.DestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"s3": "s3"},
    )
    class DestinationConfigurationProperty:
        def __init__(
            self,
            *,
            s3: typing.Union[aws_cdk.core.IResolvable, "CfnRecordingConfiguration.S3DestinationConfigurationProperty"],
        ) -> None:
            '''The DestinationConfiguration property type describes the location where recorded videos will be stored.

            Each member represents a type of destination configuration. For recording, you define one and only one type of destination configuration.

            :param s3: An S3 destination configuration where recorded videos will be stored. See the `S3DestinationConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-s3destinationconfiguration.html>`_ property type for more information.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-destinationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_ivs as ivs
                
                destination_configuration_property = ivs.CfnRecordingConfiguration.DestinationConfigurationProperty(
                    s3=ivs.CfnRecordingConfiguration.S3DestinationConfigurationProperty(
                        bucket_name="bucketName"
                    )
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "s3": s3,
            }

        @builtins.property
        def s3(
            self,
        ) -> typing.Union[aws_cdk.core.IResolvable, "CfnRecordingConfiguration.S3DestinationConfigurationProperty"]:
            '''An S3 destination configuration where recorded videos will be stored.

            See the `S3DestinationConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-s3destinationconfiguration.html>`_ property type for more information.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-destinationconfiguration.html#cfn-ivs-recordingconfiguration-destinationconfiguration-s3
            '''
            result = self._values.get("s3")
            assert result is not None, "Required property 's3' is missing"
            return typing.cast(typing.Union[aws_cdk.core.IResolvable, "CfnRecordingConfiguration.S3DestinationConfigurationProperty"], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-ivs.CfnRecordingConfiguration.S3DestinationConfigurationProperty",
        jsii_struct_bases=[],
        name_mapping={"bucket_name": "bucketName"},
    )
    class S3DestinationConfigurationProperty:
        def __init__(self, *, bucket_name: builtins.str) -> None:
            '''The S3DestinationConfiguration property type describes an S3 location where recorded videos will be stored.

            :param bucket_name: Location (S3 bucket name) where recorded videos will be stored.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-s3destinationconfiguration.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                import aws_cdk.aws_ivs as ivs
                
                s3_destination_configuration_property = ivs.CfnRecordingConfiguration.S3DestinationConfigurationProperty(
                    bucket_name="bucketName"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "bucket_name": bucket_name,
            }

        @builtins.property
        def bucket_name(self) -> builtins.str:
            '''Location (S3 bucket name) where recorded videos will be stored.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-s3destinationconfiguration.html#cfn-ivs-recordingconfiguration-s3destinationconfiguration-bucketname
            '''
            result = self._values.get("bucket_name")
            assert result is not None, "Required property 'bucket_name' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "S3DestinationConfigurationProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs.CfnRecordingConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "destination_configuration": "destinationConfiguration",
        "name": "name",
        "tags": "tags",
    },
)
class CfnRecordingConfigurationProps:
    def __init__(
        self,
        *,
        destination_configuration: typing.Union[aws_cdk.core.IResolvable, CfnRecordingConfiguration.DestinationConfigurationProperty],
        name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Properties for defining a ``CfnRecordingConfiguration``.

        :param destination_configuration: A destination configuration contains information about where recorded video will be stored. See the `DestinationConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-destinationconfiguration.html>`_ property type for more information.
        :param name: Recording-configuration name. The value does not need to be unique.
        :param tags: An array of key-value pairs to apply to this resource. For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_ivs as ivs
            
            cfn_recording_configuration_props = ivs.CfnRecordingConfigurationProps(
                destination_configuration=ivs.CfnRecordingConfiguration.DestinationConfigurationProperty(
                    s3=ivs.CfnRecordingConfiguration.S3DestinationConfigurationProperty(
                        bucket_name="bucketName"
                    )
                ),
            
                # the properties below are optional
                name="name",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destination_configuration": destination_configuration,
        }
        if name is not None:
            self._values["name"] = name
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def destination_configuration(
        self,
    ) -> typing.Union[aws_cdk.core.IResolvable, CfnRecordingConfiguration.DestinationConfigurationProperty]:
        '''A destination configuration contains information about where recorded video will be stored.

        See the `DestinationConfiguration <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ivs-recordingconfiguration-destinationconfiguration.html>`_ property type for more information.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-destinationconfiguration
        '''
        result = self._values.get("destination_configuration")
        assert result is not None, "Required property 'destination_configuration' is missing"
        return typing.cast(typing.Union[aws_cdk.core.IResolvable, CfnRecordingConfiguration.DestinationConfigurationProperty], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Recording-configuration name.

        The value does not need to be unique.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        '''An array of key-value pairs to apply to this resource.

        For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-recordingconfiguration.html#cfn-ivs-recordingconfiguration-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.core.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnRecordingConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnStreamKey(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs.CfnStreamKey",
):
    '''A CloudFormation ``AWS::IVS::StreamKey``.

    The ``AWS::IVS::StreamKey`` resource specifies an  stream key associated with the referenced channel. Use a stream key to initiate a live stream.

    :cloudformationResource: AWS::IVS::StreamKey
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_ivs as ivs
        
        cfn_stream_key = ivs.CfnStreamKey(self, "MyCfnStreamKey",
            channel_arn="channelArn",
        
            # the properties below are optional
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        channel_arn: builtins.str,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Create a new ``AWS::IVS::StreamKey``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param channel_arn: Channel ARN for the stream.
        :param tags: An array of key-value pairs to apply to this resource. For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .
        '''
        props = CfnStreamKeyProps(channel_arn=channel_arn, tags=tags)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
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
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''The stream-key ARN.

        For example: ``arn:aws:ivs:us-west-2:123456789012:stream-key/g1H2I3j4k5L6``

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrValue")
    def attr_value(self) -> builtins.str:
        '''The stream-key value.

        For example: ``sk_us-west-2_abcdABCDefgh_567890abcdef``

        :cloudformationAttribute: Value
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        '''An array of key-value pairs to apply to this resource.

        For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html#cfn-ivs-streamkey-tags
        '''
        return typing.cast(aws_cdk.core.TagManager, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelArn")
    def channel_arn(self) -> builtins.str:
        '''Channel ARN for the stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html#cfn-ivs-streamkey-channelarn
        '''
        return typing.cast(builtins.str, jsii.get(self, "channelArn"))

    @channel_arn.setter
    def channel_arn(self, value: builtins.str) -> None:
        jsii.set(self, "channelArn", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs.CfnStreamKeyProps",
    jsii_struct_bases=[],
    name_mapping={"channel_arn": "channelArn", "tags": "tags"},
)
class CfnStreamKeyProps:
    def __init__(
        self,
        *,
        channel_arn: builtins.str,
        tags: typing.Optional[typing.Sequence[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        '''Properties for defining a ``CfnStreamKey``.

        :param channel_arn: Channel ARN for the stream.
        :param tags: An array of key-value pairs to apply to this resource. For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_ivs as ivs
            
            cfn_stream_key_props = ivs.CfnStreamKeyProps(
                channel_arn="channelArn",
            
                # the properties below are optional
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "channel_arn": channel_arn,
        }
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def channel_arn(self) -> builtins.str:
        '''Channel ARN for the stream.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html#cfn-ivs-streamkey-channelarn
        '''
        result = self._values.get("channel_arn")
        assert result is not None, "Required property 'channel_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        '''An array of key-value pairs to apply to this resource.

        For more information, see `Tag <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-streamkey.html#cfn-ivs-streamkey-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[aws_cdk.core.CfnTag]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnStreamKeyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs.ChannelProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorized": "authorized",
        "latency_mode": "latencyMode",
        "name": "name",
        "type": "type",
    },
)
class ChannelProps:
    def __init__(
        self,
        *,
        authorized: typing.Optional[builtins.bool] = None,
        latency_mode: typing.Optional["LatencyMode"] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional["ChannelType"] = None,
    ) -> None:
        '''(experimental) Properties for creating a new Channel.

        :param authorized: (experimental) Whether the channel is authorized. If you wish to make an authorized channel, you will need to ensure that a PlaybackKeyPair has been uploaded to your account as this is used to validate the signed JWT that is required for authorization Default: false
        :param latency_mode: (experimental) Channel latency mode. Default: LatencyMode.LOW
        :param name: (experimental) Channel name. Default: - None
        :param type: (experimental) The channel type, which determines the allowable resolution and bitrate. If you exceed the allowable resolution or bitrate, the stream will disconnect immediately Default: ChannelType.STANDARD

        :stability: experimental
        :exampleMetadata: infused

        Example::

            my_channel = ivs.Channel(self, "Channel",
                authorized=True
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if authorized is not None:
            self._values["authorized"] = authorized
        if latency_mode is not None:
            self._values["latency_mode"] = latency_mode
        if name is not None:
            self._values["name"] = name
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def authorized(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the channel is authorized.

        If you wish to make an authorized channel, you will need to ensure that
        a PlaybackKeyPair has been uploaded to your account as this is used to
        validate the signed JWT that is required for authorization

        :default: false

        :stability: experimental
        '''
        result = self._values.get("authorized")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def latency_mode(self) -> typing.Optional["LatencyMode"]:
        '''(experimental) Channel latency mode.

        :default: LatencyMode.LOW

        :stability: experimental
        '''
        result = self._values.get("latency_mode")
        return typing.cast(typing.Optional["LatencyMode"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Channel name.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional["ChannelType"]:
        '''(experimental) The channel type, which determines the allowable resolution and bitrate.

        If you exceed the allowable resolution or bitrate, the stream will disconnect immediately

        :default: ChannelType.STANDARD

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["ChannelType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ChannelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-ivs.ChannelType")
class ChannelType(enum.Enum):
    '''(experimental) The channel type, which determines the allowable resolution and bitrate.

    If you exceed the allowable resolution or bitrate, the stream probably will disconnect immediately.

    :stability: experimental
    '''

    STANDARD = "STANDARD"
    '''(experimental) Multiple qualities are generated from the original input, to automatically give viewers the best experience for their devices and network conditions.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html
    :stability: experimental
    '''
    BASIC = "BASIC"
    '''(experimental) delivers the original input to viewers.

    The viewer’s video-quality choice is limited to the original input.

    :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ivs-channel.html
    :stability: experimental
    '''


@jsii.interface(jsii_type="@aws-cdk/aws-ivs.IChannel")
class IChannel(aws_cdk.core.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an IVS Channel.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelArn")
    def channel_arn(self) -> builtins.str:
        '''(experimental) The channel ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="addStreamKey")
    def add_stream_key(self, id: builtins.str) -> "StreamKey":
        '''(experimental) Adds a stream key for this IVS Channel.

        :param id: construct ID.

        :stability: experimental
        '''
        ...


class _IChannelProxy(
    jsii.proxy_for(aws_cdk.core.IResource) # type: ignore[misc]
):
    '''(experimental) Represents an IVS Channel.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-ivs.IChannel"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelArn")
    def channel_arn(self) -> builtins.str:
        '''(experimental) The channel ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "channelArn"))

    @jsii.member(jsii_name="addStreamKey")
    def add_stream_key(self, id: builtins.str) -> "StreamKey":
        '''(experimental) Adds a stream key for this IVS Channel.

        :param id: construct ID.

        :stability: experimental
        '''
        return typing.cast("StreamKey", jsii.invoke(self, "addStreamKey", [id]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IChannel).__jsii_proxy_class__ = lambda : _IChannelProxy


@jsii.interface(jsii_type="@aws-cdk/aws-ivs.IPlaybackKeyPair")
class IPlaybackKeyPair(aws_cdk.core.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an IVS Playback Key Pair.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="playbackKeyPairArn")
    def playback_key_pair_arn(self) -> builtins.str:
        '''(experimental) Key-pair ARN.

        For example: arn:aws:ivs:us-west-2:693991300569:playback-key/f99cde61-c2b0-4df3-8941-ca7d38acca1a

        :stability: experimental
        :attribute: true
        '''
        ...


class _IPlaybackKeyPairProxy(
    jsii.proxy_for(aws_cdk.core.IResource) # type: ignore[misc]
):
    '''(experimental) Represents an IVS Playback Key Pair.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-ivs.IPlaybackKeyPair"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="playbackKeyPairArn")
    def playback_key_pair_arn(self) -> builtins.str:
        '''(experimental) Key-pair ARN.

        For example: arn:aws:ivs:us-west-2:693991300569:playback-key/f99cde61-c2b0-4df3-8941-ca7d38acca1a

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "playbackKeyPairArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPlaybackKeyPair).__jsii_proxy_class__ = lambda : _IPlaybackKeyPairProxy


@jsii.interface(jsii_type="@aws-cdk/aws-ivs.IStreamKey")
class IStreamKey(aws_cdk.core.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an IVS Stream Key.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamKeyArn")
    def stream_key_arn(self) -> builtins.str:
        '''(experimental) The stream-key ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:stream-key/g1H2I3j4k5L6

        :stability: experimental
        :attribute: true
        '''
        ...


class _IStreamKeyProxy(
    jsii.proxy_for(aws_cdk.core.IResource) # type: ignore[misc]
):
    '''(experimental) Represents an IVS Stream Key.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-ivs.IStreamKey"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamKeyArn")
    def stream_key_arn(self) -> builtins.str:
        '''(experimental) The stream-key ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:stream-key/g1H2I3j4k5L6

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "streamKeyArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStreamKey).__jsii_proxy_class__ = lambda : _IStreamKeyProxy


@jsii.enum(jsii_type="@aws-cdk/aws-ivs.LatencyMode")
class LatencyMode(enum.Enum):
    '''(experimental) Channel latency mode.

    :stability: experimental
    '''

    LOW = "LOW"
    '''(experimental) Use LOW to minimize broadcaster-to-viewer latency for interactive broadcasts.

    :stability: experimental
    '''
    NORMAL = "NORMAL"
    '''(experimental) Use NORMAL for broadcasts that do not require viewer interaction.

    :stability: experimental
    '''


@jsii.implements(IPlaybackKeyPair)
class PlaybackKeyPair(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs.PlaybackKeyPair",
):
    '''(experimental) A new IVS Playback Key Pair.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        key_pair = ivs.PlaybackKeyPair(self, "PlaybackKeyPair",
            public_key_material=my_public_key_pem_string
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        public_key_material: builtins.str,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param public_key_material: (experimental) The public portion of a customer-generated key pair.
        :param name: (experimental) An arbitrary string (a nickname) assigned to a playback key pair that helps the customer identify that resource. The value does not need to be unique. Default: None

        :stability: experimental
        '''
        props = PlaybackKeyPairProps(
            public_key_material=public_key_material, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="playbackKeyPairArn")
    def playback_key_pair_arn(self) -> builtins.str:
        '''(experimental) Key-pair ARN.

        For example: arn:aws:ivs:us-west-2:693991300569:playback-key/f99cde61-c2b0-4df3-8941-ca7d38acca1a

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "playbackKeyPairArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="playbackKeyPairFingerprint")
    def playback_key_pair_fingerprint(self) -> builtins.str:
        '''(experimental) Key-pair identifier.

        For example: 98:0d:1a:a0:19:96:1e:ea:0a:0a:2c:9a:42:19:2b:e7

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "playbackKeyPairFingerprint"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs.PlaybackKeyPairProps",
    jsii_struct_bases=[],
    name_mapping={"public_key_material": "publicKeyMaterial", "name": "name"},
)
class PlaybackKeyPairProps:
    def __init__(
        self,
        *,
        public_key_material: builtins.str,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for creating a new Playback Key Pair.

        :param public_key_material: (experimental) The public portion of a customer-generated key pair.
        :param name: (experimental) An arbitrary string (a nickname) assigned to a playback key pair that helps the customer identify that resource. The value does not need to be unique. Default: None

        :stability: experimental
        :exampleMetadata: infused

        Example::

            key_pair = ivs.PlaybackKeyPair(self, "PlaybackKeyPair",
                public_key_material=my_public_key_pem_string
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "public_key_material": public_key_material,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def public_key_material(self) -> builtins.str:
        '''(experimental) The public portion of a customer-generated key pair.

        :stability: experimental
        '''
        result = self._values.get("public_key_material")
        assert result is not None, "Required property 'public_key_material' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) An arbitrary string (a nickname) assigned to a playback key pair that helps the customer identify that resource.

        The value does not need to be unique.

        :default: None

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PlaybackKeyPairProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IStreamKey)
class StreamKey(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs.StreamKey",
):
    '''(experimental) A new IVS Stream Key.

    :stability: experimental
    :exampleMetadata: fixture=with-channel infused

    Example::

        my_stream_key = my_channel.add_stream_key("StreamKey")
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        channel: IChannel,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param channel: (experimental) Channel ARN for the stream.

        :stability: experimental
        '''
        props = StreamKeyProps(channel=channel)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamKeyArn")
    def stream_key_arn(self) -> builtins.str:
        '''(experimental) The stream-key ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:stream-key/g1H2I3j4k5L6

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "streamKeyArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamKeyValue")
    def stream_key_value(self) -> builtins.str:
        '''(experimental) The stream-key value.

        For example: sk_us-west-2_abcdABCDefgh_567890abcdef

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "streamKeyValue"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-ivs.StreamKeyProps",
    jsii_struct_bases=[],
    name_mapping={"channel": "channel"},
)
class StreamKeyProps:
    def __init__(self, *, channel: IChannel) -> None:
        '''(experimental) Properties for creating a new Stream Key.

        :param channel: (experimental) Channel ARN for the stream.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_ivs as ivs
            
            # channel: ivs.Channel
            
            stream_key_props = ivs.StreamKeyProps(
                channel=channel
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "channel": channel,
        }

    @builtins.property
    def channel(self) -> IChannel:
        '''(experimental) Channel ARN for the stream.

        :stability: experimental
        '''
        result = self._values.get("channel")
        assert result is not None, "Required property 'channel' is missing"
        return typing.cast(IChannel, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamKeyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IChannel)
class Channel(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-ivs.Channel",
):
    '''(experimental) A new IVS channel.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        my_channel = ivs.Channel(self, "Channel")
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        authorized: typing.Optional[builtins.bool] = None,
        latency_mode: typing.Optional[LatencyMode] = None,
        name: typing.Optional[builtins.str] = None,
        type: typing.Optional[ChannelType] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param authorized: (experimental) Whether the channel is authorized. If you wish to make an authorized channel, you will need to ensure that a PlaybackKeyPair has been uploaded to your account as this is used to validate the signed JWT that is required for authorization Default: false
        :param latency_mode: (experimental) Channel latency mode. Default: LatencyMode.LOW
        :param name: (experimental) Channel name. Default: - None
        :param type: (experimental) The channel type, which determines the allowable resolution and bitrate. If you exceed the allowable resolution or bitrate, the stream will disconnect immediately Default: ChannelType.STANDARD

        :stability: experimental
        '''
        props = ChannelProps(
            authorized=authorized, latency_mode=latency_mode, name=name, type=type
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromChannelArn") # type: ignore[misc]
    @builtins.classmethod
    def from_channel_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        channel_arn: builtins.str,
    ) -> IChannel:
        '''(experimental) Import an existing channel.

        :param scope: -
        :param id: -
        :param channel_arn: -

        :stability: experimental
        '''
        return typing.cast(IChannel, jsii.sinvoke(cls, "fromChannelArn", [scope, id, channel_arn]))

    @jsii.member(jsii_name="addStreamKey")
    def add_stream_key(self, id: builtins.str) -> StreamKey:
        '''(experimental) Adds a stream key for this IVS Channel.

        :param id: -

        :stability: experimental
        '''
        return typing.cast(StreamKey, jsii.invoke(self, "addStreamKey", [id]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelArn")
    def channel_arn(self) -> builtins.str:
        '''(experimental) The channel ARN.

        For example: arn:aws:ivs:us-west-2:123456789012:channel/abcdABCDefgh

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "channelArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelIngestEndpoint")
    def channel_ingest_endpoint(self) -> builtins.str:
        '''(experimental) Channel ingest endpoint, part of the definition of an ingest server, used when you set up streaming software.

        For example: a1b2c3d4e5f6.global-contribute.live-video.net

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "channelIngestEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="channelPlaybackUrl")
    def channel_playback_url(self) -> builtins.str:
        '''(experimental) Channel playback URL.

        For example:
        https://a1b2c3d4e5f6.us-west-2.playback.live-video.net/api/video/v1/us-west-2.123456789012.channel.abcdEFGH.m3u8

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "channelPlaybackUrl"))


__all__ = [
    "CfnChannel",
    "CfnChannelProps",
    "CfnPlaybackKeyPair",
    "CfnPlaybackKeyPairProps",
    "CfnRecordingConfiguration",
    "CfnRecordingConfigurationProps",
    "CfnStreamKey",
    "CfnStreamKeyProps",
    "Channel",
    "ChannelProps",
    "ChannelType",
    "IChannel",
    "IPlaybackKeyPair",
    "IStreamKey",
    "LatencyMode",
    "PlaybackKeyPair",
    "PlaybackKeyPairProps",
    "StreamKey",
    "StreamKeyProps",
]

publication.publish()
