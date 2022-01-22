'''
# cdk-dynamo-table-viewer

An AWS CDK construct which exposes a public HTTP endpoint which displays an HTML
page with the contents of a DynamoDB table in your stack.

**SECURITY NOTE**: this construct was built for demonstration purposes and
using it in production is probably a really bad idea. It exposes the entire
contents of a DynamoDB table in your account to the general public.

The library is published under the following names:

|Language|Repository
|--------|-----------
|JavaScript/TypeScript|[cdk-dynamo-table-viewer](https://www.npmjs.com/package/cdk-dynamo-table-viewer)
|Python|[cdk-dynamo-table-viewer](https://pypi.org/project/cdk-dynamo-table-viewer/)
|.NET|[Eladb.DynamoTableViewer](https://www.nuget.org/packages/Eladb.DynamoTableViewer/)
|Java|[com.github.eladb/cdk-dynamo-table-viewer](https://search.maven.org/artifact/com.github.eladb/cdk-dynamo-table-viewer)

## Usage (TypeScript/JavaScript)

Install via npm:

```shell
$ npm i cdk-dynamo-table-viewer
```

Add to your CDK stack:

```python
import { TableViewer } from 'cdk-dynamo-table-viewer'

const viewer = new TableViewer(this, 'CookiesViewer', {
  table: cookiesTable,
  title: 'Cookie Sales', // optional
  sortBy: '-sales'       // optional ("-" denotes descending order)
});
```

Notes:

* The endpoint will be available (as an deploy-time value) under `viewer.endpoint`.
  It will also be exported as a stack output.
* Paging is not supported. This means that only the first 1MB of items will be
  displayed (again, this is a demo...)
* Supports CDK version 0.38.0 and above

## License

Apache 2.0
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

import aws_cdk.aws_apigateway
import aws_cdk.aws_dynamodb
import constructs


class TableViewer(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-dynamo-table-viewer.TableViewer",
):
    '''Installs an endpoint in your stack that allows users to view the contents of a DynamoDB table through their browser.'''

    def __init__(
        self,
        parent: constructs.Construct,
        id: builtins.str,
        *,
        table: aws_cdk.aws_dynamodb.Table,
        endpoint_type: typing.Optional[aws_cdk.aws_apigateway.EndpointType] = None,
        sort_by: typing.Optional[builtins.str] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param parent: -
        :param id: -
        :param table: The DynamoDB table to view. Note that all contents of this table will be visible to the public.
        :param endpoint_type: The endpoint type of the `LambdaRestApi <https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.LambdaRestApi.html>`_ that will be created. Default: - EDGE
        :param sort_by: Name of the column to sort by, prefix with "-" for descending order. Default: - No sort
        :param title: The web page title. Default: - No title
        '''
        props = TableViewerProps(
            table=table, endpoint_type=endpoint_type, sort_by=sort_by, title=title
        )

        jsii.create(self.__class__, self, [parent, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))


@jsii.data_type(
    jsii_type="cdk-dynamo-table-viewer.TableViewerProps",
    jsii_struct_bases=[],
    name_mapping={
        "table": "table",
        "endpoint_type": "endpointType",
        "sort_by": "sortBy",
        "title": "title",
    },
)
class TableViewerProps:
    def __init__(
        self,
        *,
        table: aws_cdk.aws_dynamodb.Table,
        endpoint_type: typing.Optional[aws_cdk.aws_apigateway.EndpointType] = None,
        sort_by: typing.Optional[builtins.str] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param table: The DynamoDB table to view. Note that all contents of this table will be visible to the public.
        :param endpoint_type: The endpoint type of the `LambdaRestApi <https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.LambdaRestApi.html>`_ that will be created. Default: - EDGE
        :param sort_by: Name of the column to sort by, prefix with "-" for descending order. Default: - No sort
        :param title: The web page title. Default: - No title
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "table": table,
        }
        if endpoint_type is not None:
            self._values["endpoint_type"] = endpoint_type
        if sort_by is not None:
            self._values["sort_by"] = sort_by
        if title is not None:
            self._values["title"] = title

    @builtins.property
    def table(self) -> aws_cdk.aws_dynamodb.Table:
        '''The DynamoDB table to view.

        Note that all contents of this table will be
        visible to the public.
        '''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(aws_cdk.aws_dynamodb.Table, result)

    @builtins.property
    def endpoint_type(self) -> typing.Optional[aws_cdk.aws_apigateway.EndpointType]:
        '''The endpoint type of the `LambdaRestApi <https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.LambdaRestApi.html>`_ that will be created.

        :default: - EDGE
        '''
        result = self._values.get("endpoint_type")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.EndpointType], result)

    @builtins.property
    def sort_by(self) -> typing.Optional[builtins.str]:
        '''Name of the column to sort by, prefix with "-" for descending order.

        :default: - No sort
        '''
        result = self._values.get("sort_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def title(self) -> typing.Optional[builtins.str]:
        '''The web page title.

        :default: - No title
        '''
        result = self._values.get("title")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TableViewerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TableViewer",
    "TableViewerProps",
]

publication.publish()
