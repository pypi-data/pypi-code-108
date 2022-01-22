'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-responsive-email-template

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-responsive-email-template)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-responsive-email-template/)

> Responsive [mjml](https://documentation.mjml.io/) email template for aws ses

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-responsive-email-template
```

Python:

```bash
pip install cloudcomponents.cdk-responsive-email-template
```

## How to use

```python
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { ResponsiveEmailTemplate, TemplatePart } from '@cloudcomponents/cdk-responsive-email-template';

export class ResponsiveEmailTemplateStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    new ResponsiveEmailTemplate(this, 'EmailTemplate', {
      templateName: 'demo',
      subjectPart: 'cloudcomponents - {{ title }}',
      textPart: TemplatePart.fromInline('text message'),
      htmlPart: TemplatePart.fromInline(`<mjml>
    <mj-head>
      <mj-title>cloudcomponents - {{ title }}</mj-title>
    </mj-head>
    <mj-body>
      <mj-section>
        <mj-column>
          <mj-text>
            Hello {{ name }}!
          </mj-text>
        </mj-column>
      </mj-section>
    </mj-body>
  </mjml>`),
      parsingOptions: {
        beautify: true,
      },
    });
  }
}
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-responsive-email-template/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-responsive-email-template/LICENSE)
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


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-responsive-email-template.ParsingOptions",
    jsii_struct_bases=[],
    name_mapping={
        "beautify": "beautify",
        "file_path": "filePath",
        "fonts": "fonts",
        "keep_comments": "keepComments",
        "minify": "minify",
        "mjml_config_path": "mjmlConfigPath",
        "validation_level": "validationLevel",
    },
)
class ParsingOptions:
    def __init__(
        self,
        *,
        beautify: typing.Optional[builtins.bool] = None,
        file_path: typing.Optional[builtins.str] = None,
        fonts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        keep_comments: typing.Optional[builtins.bool] = None,
        minify: typing.Optional[builtins.bool] = None,
        mjml_config_path: typing.Optional[builtins.str] = None,
        validation_level: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param beautify: Option to beautify the HTML output. Default: : false
        :param file_path: Full path of the specified file to use when resolving paths from mj-include components. Default: : templateDir or '.'
        :param fonts: Default fonts imported in the HTML rendered by HTML ie. { 'Open Sans': 'https://fonts.googleapis.com/css?family=Open+Sans:300,400,500,700' } Default: :
        :param keep_comments: Option to keep comments in the HTML output. Default: : true
        :param minify: Option to minify the HTML output. Default: : false
        :param mjml_config_path: The path or directory of the .mjmlconfig file default: process.cwd().
        :param validation_level: How to validate your MJML. skip: your document is rendered without going through validation soft: your document is going through validation and is rendered, even if it has errors strict: your document is going through validation and is not rendered if it has any error Default: : soft
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if beautify is not None:
            self._values["beautify"] = beautify
        if file_path is not None:
            self._values["file_path"] = file_path
        if fonts is not None:
            self._values["fonts"] = fonts
        if keep_comments is not None:
            self._values["keep_comments"] = keep_comments
        if minify is not None:
            self._values["minify"] = minify
        if mjml_config_path is not None:
            self._values["mjml_config_path"] = mjml_config_path
        if validation_level is not None:
            self._values["validation_level"] = validation_level

    @builtins.property
    def beautify(self) -> typing.Optional[builtins.bool]:
        '''Option to beautify the HTML output.

        :default: : false
        '''
        result = self._values.get("beautify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def file_path(self) -> typing.Optional[builtins.str]:
        '''Full path of the specified file to use when resolving paths from mj-include components.

        :default: : templateDir or '.'
        '''
        result = self._values.get("file_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fonts(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Default fonts imported in the HTML rendered by HTML ie.

        { 'Open Sans': 'https://fonts.googleapis.com/css?family=Open+Sans:300,400,500,700' }

        :default: :

        :see: https://github.com/mjmlio/mjml/blob/master/packages/mjml-core/src/index.js
        '''
        result = self._values.get("fonts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def keep_comments(self) -> typing.Optional[builtins.bool]:
        '''Option to keep comments in the HTML output.

        :default: : true
        '''
        result = self._values.get("keep_comments")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def minify(self) -> typing.Optional[builtins.bool]:
        '''Option to minify the HTML output.

        :default: : false
        '''
        result = self._values.get("minify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mjml_config_path(self) -> typing.Optional[builtins.str]:
        '''The path or directory of the .mjmlconfig file default: process.cwd().'''
        result = self._values.get("mjml_config_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def validation_level(self) -> typing.Optional[builtins.str]:
        '''How to validate your MJML.

        skip: your document is rendered without going through validation
        soft: your document is going through validation and is rendered, even if it has errors
        strict: your document is going through validation and is not rendered if it has any error

        :default: : soft
        '''
        result = self._values.get("validation_level")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ParsingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ResponsiveEmailTemplate(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-responsive-email-template.ResponsiveEmailTemplate",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        html_part: "TemplatePart",
        subject_part: builtins.str,
        template_name: builtins.str,
        parsing_options: typing.Optional[ParsingOptions] = None,
        text_part: typing.Optional["TemplatePart"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param html_part: -
        :param subject_part: -
        :param template_name: -
        :param parsing_options: -
        :param text_part: -
        '''
        props = ResponsiveEmailTemplateProps(
            html_part=html_part,
            subject_part=subject_part,
            template_name=template_name,
            parsing_options=parsing_options,
            text_part=text_part,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-responsive-email-template.ResponsiveEmailTemplateProps",
    jsii_struct_bases=[],
    name_mapping={
        "html_part": "htmlPart",
        "subject_part": "subjectPart",
        "template_name": "templateName",
        "parsing_options": "parsingOptions",
        "text_part": "textPart",
    },
)
class ResponsiveEmailTemplateProps:
    def __init__(
        self,
        *,
        html_part: "TemplatePart",
        subject_part: builtins.str,
        template_name: builtins.str,
        parsing_options: typing.Optional[ParsingOptions] = None,
        text_part: typing.Optional["TemplatePart"] = None,
    ) -> None:
        '''
        :param html_part: -
        :param subject_part: -
        :param template_name: -
        :param parsing_options: -
        :param text_part: -
        '''
        if isinstance(parsing_options, dict):
            parsing_options = ParsingOptions(**parsing_options)
        self._values: typing.Dict[str, typing.Any] = {
            "html_part": html_part,
            "subject_part": subject_part,
            "template_name": template_name,
        }
        if parsing_options is not None:
            self._values["parsing_options"] = parsing_options
        if text_part is not None:
            self._values["text_part"] = text_part

    @builtins.property
    def html_part(self) -> "TemplatePart":
        result = self._values.get("html_part")
        assert result is not None, "Required property 'html_part' is missing"
        return typing.cast("TemplatePart", result)

    @builtins.property
    def subject_part(self) -> builtins.str:
        result = self._values.get("subject_part")
        assert result is not None, "Required property 'subject_part' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def template_name(self) -> builtins.str:
        result = self._values.get("template_name")
        assert result is not None, "Required property 'template_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parsing_options(self) -> typing.Optional[ParsingOptions]:
        result = self._values.get("parsing_options")
        return typing.cast(typing.Optional[ParsingOptions], result)

    @builtins.property
    def text_part(self) -> typing.Optional["TemplatePart"]:
        result = self._values.get("text_part")
        return typing.cast(typing.Optional["TemplatePart"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResponsiveEmailTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TemplatePart(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cloudcomponents/cdk-responsive-email-template.TemplatePart",
):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromFile") # type: ignore[misc]
    @builtins.classmethod
    def from_file(cls, file_path: builtins.str) -> "TemplatePart":
        '''
        :param file_path: -
        '''
        return typing.cast("TemplatePart", jsii.sinvoke(cls, "fromFile", [file_path]))

    @jsii.member(jsii_name="fromInline") # type: ignore[misc]
    @builtins.classmethod
    def from_inline(cls, source: builtins.str) -> "TemplatePart":
        '''
        :param source: -
        '''
        return typing.cast("TemplatePart", jsii.sinvoke(cls, "fromInline", [source]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    @abc.abstractmethod
    def source(self) -> builtins.str:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultFilePath")
    @abc.abstractmethod
    def default_file_path(self) -> typing.Optional[builtins.str]:
        ...


class _TemplatePartProxy(TemplatePart):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultFilePath")
    def default_file_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultFilePath"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, TemplatePart).__jsii_proxy_class__ = lambda : _TemplatePartProxy


__all__ = [
    "ParsingOptions",
    "ResponsiveEmailTemplate",
    "ResponsiveEmailTemplateProps",
    "TemplatePart",
]

publication.publish()
