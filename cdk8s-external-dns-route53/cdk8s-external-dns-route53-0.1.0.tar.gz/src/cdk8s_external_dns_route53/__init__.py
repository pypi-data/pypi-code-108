'''
# cdk8s-external-dns-route53

![Release](https://github.com/opencdk8s/cdk8s-external-dns-route53/workflows/Release/badge.svg?branch=development)
[![npm version](https://badge.fury.io/js/%40opencdk8s%2Fcdk8s-external-dns-route53.svg)](https://badge.fury.io/js/%40opencdk8s%2Fcdk8s-external-dns-route53)
[![PyPI version](https://badge.fury.io/py/cdk8s-external-dns-route53.svg)](https://badge.fury.io/py/cdk8s-external-dns-route53)
![npm](https://img.shields.io/npm/dt/@opencdk8s/cdk8s-external-dns-route53?label=npm&color=green)

Upstream Fork of [this repo](https://github.com/guan840912/cdk8s-external-dns)

Synths an install manifest for [ExternalDNS - Route53](https://github.com/kubernetes-sigs/external-dns/blob/master/docs/tutorials/aws.md)

## Controller version : `v0.7.6`

## Overview

### `install.yaml` example

```python
import { Construct } from 'constructs';
import { App, Chart, ChartProps } from 'cdk8s';
import { AwsExternalDns } from '@opencdk8s/cdk8s-external-dns-route53';

export class MyChart extends Chart {
  constructor(scope: Construct, id: string, props: ChartProps = { }) {
    super(scope, id, props);

    new AwsExternalDns(this, 'example', {
      args: [
        '--custom-arg=custom'
      ]
    })


  }
}

const app = new App();
new MyChart(app, 'example');
app.synth();
```

<details>
<summary>install.k8s.yaml</summary>

```yaml
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRole
metadata:
  name: external-dns
rules:
  - apiGroups:
      - ""
    resources:
      - services
      - endpoints
      - pods
    verbs:
      - get
      - watch
      - list
  - apiGroups:
      - extensions
      - networking.k8s.io
    resources:
      - ingresses
    verbs:
      - get
      - watch
      - list
  - apiGroups:
      - ""
    resources:
      - nodes
    verbs:
      - list
      - watch
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: external-dns-viewer
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: external-dns
subjects:
  - kind: ServiceAccount
    name: external-dns
    namespace: default
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-dns
  namespace: default
spec:
  selector:
    matchLabels:
      app: external-dns
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: external-dns
    spec:
      containers:
        - args:
            - --source=service
            - --source=ingress
            - --provider=aws
            - --registry=txt
            - --txt-owner-id=external-dns
            - --custom-arg=custom
          image: k8s.gcr.io/external-dns/external-dns:v0.7.6
          name: external-dns
      securityContext:
        fsGroup: 65534
      serviceAccountName: external-dns
```

</details>

## Installation

### TypeScript

Use `yarn` or `npm` to install.

```sh
$ npm install @opencdk8s/cdk8s-external-dns-route53
```

```sh
$ yarn add @opencdk8s/cdk8s-external-dns-route53
```

### Python

```sh
$ pip install cdk8s-external-dns-route53
```

## Contribution

1. Fork ([link](https://github.com/opencdk8s/cdk8s-external-dns-route53/fork))
2. Bootstrap the repo:

   ```bash
   npx projen   # generates package.json
   yarn install # installs dependencies
   ```
3. Development scripts:
   |Command|Description
   |-|-
   |`yarn compile`|Compiles typescript => javascript
   |`yarn watch`|Watch & compile
   |`yarn test`|Run unit test & linter through jest
   |`yarn test -u`|Update jest snapshots
   |`yarn run package`|Creates a `dist` with packages for all languages.
   |`yarn build`|Compile + test + package
   |`yarn bump`|Bump version (with changelog) based on [conventional commits]
   |`yarn release`|Bump + push to `master`
4. Create a feature branch
5. Commit your changes
6. Rebase your local changes against the master branch
7. Create a new Pull Request (use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) for the title please)

## Licence

[Apache License, Version 2.0](./LICENSE)

## Author

[Hunter-Thompson](https://github.com/Hunter-Thompson)
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

import constructs


class AwsExternalDns(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-external-dns-route53.AwsExternalDns",
):
    '''(experimental) Generate external-dns config yaml.

    see https://github.com/kubernetes-sigs/external-dns/blob/master/docs/tutorials/aws.md

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        image: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        service_account_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param args: (experimental) Args for controller. Default: - None
        :param image: (experimental) image for external-dns. Default: - k8s.gcr.io/external-dns/external-dns:v0.7.6
        :param namespace: (experimental) Namespace for external-dns. Default: - default
        :param service_account_name: (experimental) Service Account Name for external-dns. Default: - external-dns

        :stability: experimental
        '''
        options = AwsExternalDnsOptions(
            args=args,
            image=image,
            namespace=namespace,
            service_account_name=service_account_name,
        )

        jsii.create(self.__class__, self, [scope, id, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentName")
    def deployment_name(self) -> builtins.str:
        '''(experimental) Kubernetes Deployment Name for external-dns.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "deploymentName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        '''(experimental) image for external-dns.

        :default: - k8s.gcr.io/external-dns/external-dns:v0.7.6

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        '''(experimental) Namespace for external-dns.

        :default: - default

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccountName")
    def service_account_name(self) -> builtins.str:
        '''(experimental) Service Account Name for external-dns.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountName"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-external-dns-route53.AwsExternalDnsOptions",
    jsii_struct_bases=[],
    name_mapping={
        "args": "args",
        "image": "image",
        "namespace": "namespace",
        "service_account_name": "serviceAccountName",
    },
)
class AwsExternalDnsOptions:
    def __init__(
        self,
        *,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        image: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        service_account_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param args: (experimental) Args for controller. Default: - None
        :param image: (experimental) image for external-dns. Default: - k8s.gcr.io/external-dns/external-dns:v0.7.6
        :param namespace: (experimental) Namespace for external-dns. Default: - default
        :param service_account_name: (experimental) Service Account Name for external-dns. Default: - external-dns

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if args is not None:
            self._values["args"] = args
        if image is not None:
            self._values["image"] = image
        if namespace is not None:
            self._values["namespace"] = namespace
        if service_account_name is not None:
            self._values["service_account_name"] = service_account_name

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Args for controller.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        '''(experimental) image for external-dns.

        :default: - k8s.gcr.io/external-dns/external-dns:v0.7.6

        :stability: experimental
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) Namespace for external-dns.

        :default: - default

        :stability: experimental
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_account_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Service Account Name for external-dns.

        :default: - external-dns

        :stability: experimental
        '''
        result = self._values.get("service_account_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsExternalDnsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AwsExternalDnsPolicyHelper(
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-external-dns-route53.AwsExternalDnsPolicyHelper",
):
    '''(experimental) Aws External Dns Policy class ,help you add policy to your Iam Role for service account.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="addPolicy") # type: ignore[misc]
    @builtins.classmethod
    def add_policy(cls, role: typing.Any) -> typing.Any:
        '''
        :param role: -

        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.sinvoke(cls, "addPolicy", [role]))


__all__ = [
    "AwsExternalDns",
    "AwsExternalDnsOptions",
    "AwsExternalDnsPolicyHelper",
]

publication.publish()
