'''
# cdk8s-operator

> Create Kubernetes CRD Operators using CDK8s Constructs

This is a multi-language (jsii) library and a command-line tool that allows you
to create Kubernetes operators for CRDs (Custom Resource Definitions) using
CDK8s.

## Getting Started

Let's create our first CRD served by a CDK8s construct using TypeScript.

### Install CDK8s

Make sure your system has the required CDK8s [prerequisites](https://cdk8s.io/docs/latest/getting-started/#prerequisites).

Install the CDK8s CLI globally through npm:

```shell
$ npm i -g cdk8s-cli
Installing...

# Verify installation
$ cdk8s --version
1.0.0-beta.3
```

### Create a new CDK8s app

Now, let's create a new CDK8s typescript app:

```shell
mkdir hello-operator && cd hello-operator
git init
cdk8s init typescript-app
```

### Install cdk8s-operator

Next, let's install this module as a dependency of our TypeScript project:

```shell
npm install cdk8s-operator
```

### Construct

We will start by creating the construct that implements the abstraction. This is
is just a normal CDK8s custom construct:

Let's create a construct called `PodCollection` which represents a collection of
pods:

`pod-collection.ts`:

```python
import { Pod } from 'cdk8s-plus-17';
import { Construct } from 'constructs';

export interface PodCollectionProps {
  /** Number of pods */
  readonly count: number;
  /** The docker image to deploy */
  readonly image: string;
}

export class PodCollection extends Construct {
  constructor(scope: Construct, id: string, props: PodCollectionProps) {
    super(scope, id);

    for (let i = 0; i < props.count; ++i) {
      new Pod(this, `pod-${i}`, {
        containers: [ { image: props.image } ]
      });
    }
  }
}
```

### Operator App

Now, we will need to replace out `main.ts` file with an "operator app", which is
a special kind of CDK8s app designed to be executed by the `cdk8s-server` CLI
which is included in this module.

The `Operator` app construct can be used to create "CDK8s Operators" which are
CDK8s apps that accept input from a file (or STDIN) with a Kubernetes manifest,
instantiates a construct with the `spec` as its input and emits the resulting
manifest to STDOUT.

Replace the contents of `main.ts` with the following. We initialize an
`Operator` app and then register a provider which handles resources of API
version `samples.cdk8s.org/v1alpha1` and kind `PodCollection`.

`main.ts`:

```python
import { Operator } from 'cdk8s-operator';
import { PodCollection } from './pod-collection';

const app = new Operator();

app.addProvider({
  apiVersion: 'samples.cdk8s.org/v1alpha1',
  kind: 'PodCollection',
  handler: {
    apply: (scope, id, props) => new PodCollection(scope, id, props)
  }
})

app.synth();
```

> A single operator can handle any number of resource kinds. Simply call
> `addProvider()` for each apiVersion/kind.

## Using Operators

To use this operator, create an `input.json` file, e.g:

`input.json`:

```json
{
  "apiVersion": "samples.cdk8s.org/v1alpha1",
  "kind": "PodCollection",
  "metadata": {
    "name": "my-collection"
  },
  "spec": {
    "image": "paulbouwer/hello-kubernetes",
    "count": 5
  }
}
```

Compile your code:

```shell
# delete `main.test.ts` since it has some code that won't compile
$ rm -f main.test.*

# compile
$ npm run compile
```

And run:

```shell
$ node main.js input.json
```

<details>
  <summary>STDOUT</summary>

```yaml
apiVersion: "v1"
kind: "Pod"
metadata:
  name: "my-collection-pod-0-c8735c52"
spec:
  containers:
    - env: []
      image: "paulbouwer/hello-kubernetes"
      imagePullPolicy: "Always"
      name: "main"
      ports: []
      volumeMounts: []
  volumes: []
---
apiVersion: "v1"
kind: "Pod"
metadata:
  name: "my-collection-pod-1-c89f58d7"
spec:
  containers:
    - env: []
      image: "paulbouwer/hello-kubernetes"
      imagePullPolicy: "Always"
      name: "main"
      ports: []
      volumeMounts: []
  volumes: []
---
apiVersion: "v1"
kind: "Pod"
metadata:
  name: "my-collection-pod-2-c88d4268"
spec:
  containers:
    - env: []
      image: "paulbouwer/hello-kubernetes"
      imagePullPolicy: "Always"
      name: "main"
      ports: []
      volumeMounts: []
  volumes: []
---
apiVersion: "v1"
kind: "Pod"
metadata:
  name: "my-collection-pod-3-c86866b1"
spec:
  containers:
    - env: []
      image: "paulbouwer/hello-kubernetes"
      imagePullPolicy: "Always"
      name: "main"
      ports: []
      volumeMounts: []
  volumes: []
---
apiVersion: "v1"
kind: "Pod"
metadata:
  name: "my-collection-pod-4-c8b74b1d"
spec:
  containers:
    - env: []
      image: "paulbouwer/hello-kubernetes"
      imagePullPolicy: "Always"
      name: "main"
      ports: []
      volumeMounts: []
  volumes: []
```

</details>

## `cdk8s-server`

This library is shipped with a program called `cdk8s-server` which can be used
to host your operator inside an HTTP server. This server can be used as a
sidecar container with a generic CRD operator (TBD).

```shell
$ PORT=8080 npx cdk8s-server
Listening on 8080
- App command: node main.js
- Request body should include a single k8s resource in JSON format
- Request will be piped through STDIN to "node main.js"
- Response is the STDOUT and expected to be a multi-resource yaml manifest
```

Now, you can send `input.json` over HTTP:

```shell
$ curl -d @input.json http://localhost:8080
MANIFEST...
```

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

import cdk8s
import constructs


@jsii.data_type(
    jsii_type="cdk8s-operator.CustomResourceProvider",
    jsii_struct_bases=[],
    name_mapping={"api_version": "apiVersion", "handler": "handler", "kind": "kind"},
)
class CustomResourceProvider:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        handler: "ICustomResourceProviderHandler",
        kind: builtins.str,
    ) -> None:
        '''
        :param api_version: API version of the custom resource. Default: "v1"
        :param handler: The construct handler.
        :param kind: Kind of this custom resource.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_version": api_version,
            "handler": handler,
            "kind": kind,
        }

    @builtins.property
    def api_version(self) -> builtins.str:
        '''API version of the custom resource.

        :default: "v1"
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def handler(self) -> "ICustomResourceProviderHandler":
        '''The construct handler.'''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast("ICustomResourceProviderHandler", result)

    @builtins.property
    def kind(self) -> builtins.str:
        '''Kind of this custom resource.'''
        result = self._values.get("kind")
        assert result is not None, "Required property 'kind' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomResourceProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cdk8s-operator.ICustomResourceProviderHandler")
class ICustomResourceProviderHandler(typing_extensions.Protocol):
    '''The handler for this custom resource provider.'''

    @jsii.member(jsii_name="apply")
    def apply(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        spec: typing.Any,
    ) -> constructs.Construct:
        '''
        :param scope: -
        :param id: -
        :param spec: -
        '''
        ...


class _ICustomResourceProviderHandlerProxy:
    '''The handler for this custom resource provider.'''

    __jsii_type__: typing.ClassVar[str] = "cdk8s-operator.ICustomResourceProviderHandler"

    @jsii.member(jsii_name="apply")
    def apply(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        spec: typing.Any,
    ) -> constructs.Construct:
        '''
        :param scope: -
        :param id: -
        :param spec: -
        '''
        return typing.cast(constructs.Construct, jsii.invoke(self, "apply", [scope, id, spec]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICustomResourceProviderHandler).__jsii_proxy_class__ = lambda : _ICustomResourceProviderHandlerProxy


class Operator(cdk8s.App, metaclass=jsii.JSIIMeta, jsii_type="cdk8s-operator.Operator"):
    '''A CDK8s app which allows implementing Kubernetes operators using CDK8s constructs.'''

    def __init__(
        self,
        *,
        input_file: typing.Optional[builtins.str] = None,
        output_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param input_file: A Kubernetes JSON manifest with a single resource that is matched against one of the providers within this operator. Default: - first position command-line argument or "/dev/stdin"
        :param output_file: Where to write the synthesized output. Default: "/dev/stdout"
        '''
        props = OperatorProps(input_file=input_file, output_file=output_file)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addProvider")
    def add_provider(
        self,
        *,
        api_version: builtins.str,
        handler: ICustomResourceProviderHandler,
        kind: builtins.str,
    ) -> None:
        '''Adds a custom resource provider to this operator.

        :param api_version: API version of the custom resource. Default: "v1"
        :param handler: The construct handler.
        :param kind: Kind of this custom resource.
        '''
        provider = CustomResourceProvider(
            api_version=api_version, handler=handler, kind=kind
        )

        return typing.cast(None, jsii.invoke(self, "addProvider", [provider]))

    @jsii.member(jsii_name="synth")
    def synth(self) -> None:
        '''Reads a Kubernetes manifest in JSON format from STDIN or the file specified as the first positional command-line argument.

        This manifest is expected to
        include a single Kubernetes resource. Then, we match ``apiVersion`` and
        ``kind`` to one of the registered providers and if we do, we invoke
        ``apply()``, passing it the ``spec`` of the input manifest and a chart as a
        scope. The chart is then synthesized and the output manifest is written to
        STDOUT.
        '''
        return typing.cast(None, jsii.invoke(self, "synth", []))


@jsii.data_type(
    jsii_type="cdk8s-operator.OperatorProps",
    jsii_struct_bases=[],
    name_mapping={"input_file": "inputFile", "output_file": "outputFile"},
)
class OperatorProps:
    def __init__(
        self,
        *,
        input_file: typing.Optional[builtins.str] = None,
        output_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param input_file: A Kubernetes JSON manifest with a single resource that is matched against one of the providers within this operator. Default: - first position command-line argument or "/dev/stdin"
        :param output_file: Where to write the synthesized output. Default: "/dev/stdout"
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if input_file is not None:
            self._values["input_file"] = input_file
        if output_file is not None:
            self._values["output_file"] = output_file

    @builtins.property
    def input_file(self) -> typing.Optional[builtins.str]:
        '''A Kubernetes JSON manifest with a single resource that is matched against one of the providers within this operator.

        :default: - first position command-line argument or "/dev/stdin"
        '''
        result = self._values.get("input_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output_file(self) -> typing.Optional[builtins.str]:
        '''Where to write the synthesized output.

        :default: "/dev/stdout"
        '''
        result = self._values.get("output_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OperatorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Server(metaclass=jsii.JSIIMeta, jsii_type="cdk8s-operator.Server"):
    def __init__(self, *, app_command: builtins.str) -> None:
        '''
        :param app_command: The command to execute in order to synthesize the CDK app.
        '''
        props = ServerProps(app_command=app_command)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="close")
    def close(self) -> None:
        '''Stop server.'''
        return typing.cast(None, jsii.invoke(self, "close", []))

    @jsii.member(jsii_name="listen")
    def listen(self, port: typing.Optional[jsii.Number] = None) -> jsii.Number:
        '''Starts HTTP server.

        :param port: The port to listen to. If not specified, the ``PORT`` environment variable will be used. If that's not specified an available port will be auto-selected.
        '''
        return typing.cast(jsii.Number, jsii.ainvoke(self, "listen", [port]))


@jsii.data_type(
    jsii_type="cdk8s-operator.ServerProps",
    jsii_struct_bases=[],
    name_mapping={"app_command": "appCommand"},
)
class ServerProps:
    def __init__(self, *, app_command: builtins.str) -> None:
        '''
        :param app_command: The command to execute in order to synthesize the CDK app.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_command": app_command,
        }

    @builtins.property
    def app_command(self) -> builtins.str:
        '''The command to execute in order to synthesize the CDK app.'''
        result = self._values.get("app_command")
        assert result is not None, "Required property 'app_command' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CustomResourceProvider",
    "ICustomResourceProviderHandler",
    "Operator",
    "OperatorProps",
    "Server",
    "ServerProps",
]

publication.publish()
