'''
# cdk8s-cluster-autoscaler-aws

![Release](https://github.com/opencdk8s/cdk8s-cluster-autoscaler-aws/workflows/Release/badge.svg?branch=development)
[![npm version](https://badge.fury.io/js/%40opencdk8s%2Fcdk8s-cluster-autoscaler-aws.svg)](https://badge.fury.io/js/%40opencdk8s%2Fcdk8s-cluster-autoscaler-aws)
[![PyPI version](https://badge.fury.io/py/cdk8s-cluster-autoscaler-aws.svg)](https://badge.fury.io/py/cdk8s-cluster-autoscaler-aws)
![npm](https://img.shields.io/npm/dt/@opencdk8s/cdk8s-cluster-autoscaler-aws?label=npm&color=green)

Synths an install manifest for [cluster-autoscaler AWS](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)

## Controller version : `v1.17.3`

## Overview

### `cluster-autoscaler-autodiscover.yaml` example

```python
import { Construct } from 'constructs';
import { App, Chart, ChartProps } from 'cdk8s';
import { ClusterAutoScaler } from '@opencdk8s/cdk8s-cluster-autoscaler-aws';


export class MyChart extends Chart {
  constructor(scope: Construct, id: string, props: ChartProps = { }) {
    super(scope, id, props);

    const clusterName = 'example';

    new ClusterAutoScaler(this, 'example', {
      createServiceAccount: true,
      command: [
        `--node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/${clusterName}`,
      ],
    })

  }
}

const app = new App();
new MyChart(app, 'example');
app.synth();
```

<details>
<summary>cluster-autoscaler-autodiscover.yaml</summary>

```yaml

apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
  name: cluster-autoscaler
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
  name: cluster-autoscaler
rules:
  - apiGroups:
      - ""
    resources:
      - events
      - endpoints
    verbs:
      - create
      - patch
  - apiGroups:
      - ""
    resources:
      - pods/eviction
    verbs:
      - create
  - apiGroups:
      - ""
    resources:
      - pods/status
    verbs:
      - update
  - apiGroups:
      - ""
    resourceNames:
      - cluster-autoscaler
    resources:
      - endpoints
    verbs:
      - get
      - update
  - apiGroups:
      - ""
    resources:
      - nodes
    verbs:
      - watch
      - list
      - get
      - update
  - apiGroups:
      - ""
    resources:
      - pods
      - services
      - replicationcontrollers
      - persistentvolumeclaims
      - persistentvolumes
    verbs:
      - watch
      - list
      - get
  - apiGroups:
      - extensions
    resources:
      - replicasets
      - daemonsets
    verbs:
      - watch
      - list
      - get
  - apiGroups:
      - policy
    resources:
      - poddisruptionbudgets
    verbs:
      - watch
      - list
  - apiGroups:
      - apps
    resources:
      - statefulsets
      - replicasets
      - daemonsets
    verbs:
      - watch
      - list
      - get
  - apiGroups:
      - storage.k8s.io
    resources:
      - storageclasses
      - csinodes
    verbs:
      - watch
      - list
      - get
  - apiGroups:
      - batch
      - extensions
    resources:
      - jobs
    verbs:
      - get
      - list
      - watch
      - patch
  - apiGroups:
      - coordination.k8s.io
    resources:
      - leases
    verbs:
      - create
  - apiGroups:
      - coordination.k8s.io
    resourceNames:
      - cluster-autoscaler
    resources:
      - leases
    verbs:
      - get
      - update
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
  name: cluster-autoscaler
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-autoscaler
subjects:
  - kind: ServiceAccount
    name: cluster-autoscaler
    namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
  name: cluster-autoscaler
  namespace: kube-system
rules:
  - apiGroups:
      - ""
    resources:
      - configmaps
    verbs:
      - create
      - list
      - watch
  - apiGroups:
      - ""
    resourceNames:
      - cluster-autoscaler-status
      - cluster-autoscaler-priority-expander
    resources:
      - configmaps
    verbs:
      - delete
      - get
      - update
      - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
  name: cluster-autoscaler
  namespace: kube-system
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: cluster-autoscaler
subjects:
  - kind: ServiceAccount
    name: cluster-autoscaler
    namespace: kube-system
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: cluster-autoscaler
  name: cluster-autoscaler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      annotations:
        prometheus.io/port: "8085"
        prometheus.io/scrape: "true"
      labels:
        app: cluster-autoscaler
    spec:
      containers:
        - command:
            - ./cluster-autoscaler
            - --v=4
            - ----stderrthreshold=info
            - --cloud-provider=aws
            - --skip-nodes-with-local-storage=false
            - --expander=least-waste
            - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/example
          image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.17.3
          imagePullPolicy: Always
          name: cluster-autoscaler
          resources:
            limits:
              cpu: 100m
              memory: 300Mi
            requests:
              cpu: 100m
              memory: 300Mi
          volumeMounts:
            - mountPath: /etc/ssl/certs/ca-certificates.crt
              name: ssl-certs
              readOnly: true
      serviceAccountName: cluster-autoscaler
      volumes:
        - hostPath:
            path: /etc/ssl/certs/ca-bundle.crt
          name: ssl-certs

```

</details>

## Installation

### TypeScript

Use `yarn` or `npm` to install.

```sh
$ npm install @opencdk8s/cdk8s-cluster-autoscaler-aws
```

```sh
$ yarn add @opencdk8s/cdk8s-cluster-autoscaler-aws
```

### Python

```sh
$ pip install cdk8s-cluster-autoscaler-aws
```

## Contribution

1. Fork ([link](https://github.com/opencdk8s/cdk8s-cluster-autoscaler-aws/fork))
2. Bootstrap the repo:

   ```bash
   npx projen   # generates package.json
   yarn install # installs dependencies
   ```
3. Development scripts:
   |Command|Description
   |-|-
   |`yarn compile`|Compiles typescript => javascript
   |`yarn watch`| watch & compile
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


class AwsClusterAutoScalerPolicyHelper(
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-cluster-autoscaler-aws.AwsClusterAutoScalerPolicyHelper",
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


class ClusterAutoScaler(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@opencdk8s/cdk8s-cluster-autoscaler-aws.ClusterAutoScaler",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        name: builtins.str,
        *,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        create_service_account: typing.Optional[builtins.bool] = None,
        image: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        service_account_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param name: -
        :param command: (experimental) Extra commands for controller. Default: - [ './cluster-autoscaler', '--v=4', '----stderrthreshold=info', '--cloud-provider=aws', '--skip-nodes-with-local-storage=false', '--expander=least-waste' ]
        :param create_service_account: (experimental) service account for aws-load-balancer-controller. Default: - true
        :param image: (experimental) image for deployment.
        :param namespace: (experimental) Namespace. Default: - kube-system
        :param service_account_name: (experimental) Service Account Name. Default: - cluster-autoscaler

        :stability: experimental
        '''
        opts = ClusterAutoScalerOptions(
            command=command,
            create_service_account=create_service_account,
            image=image,
            namespace=namespace,
            service_account_name=service_account_name,
        )

        jsii.create(self.__class__, self, [scope, name, opts])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="command")
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Extra commands for controller.

        :default:

        - [
        './cluster-autoscaler',
        '--v=4',
        '----stderrthreshold=info',
        '--cloud-provider=aws',
        '--skip-nodes-with-local-storage=false',
        '--expander=least-waste'
        ]

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "command"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createServiceAccount")
    def create_service_account(self) -> typing.Optional[builtins.bool]:
        '''(experimental) service account for aws-load-balancer-controller.

        :default: - true

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "createServiceAccount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> typing.Optional[builtins.str]:
        '''(experimental) image for deployment.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "image"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) Namespace.

        :default: - kube-system

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespace"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceAccountName")
    def service_account_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Service Account Name.

        :default: - cluster-autoscaler

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountName"))


@jsii.data_type(
    jsii_type="@opencdk8s/cdk8s-cluster-autoscaler-aws.ClusterAutoScalerOptions",
    jsii_struct_bases=[],
    name_mapping={
        "command": "command",
        "create_service_account": "createServiceAccount",
        "image": "image",
        "namespace": "namespace",
        "service_account_name": "serviceAccountName",
    },
)
class ClusterAutoScalerOptions:
    def __init__(
        self,
        *,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        create_service_account: typing.Optional[builtins.bool] = None,
        image: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        service_account_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param command: (experimental) Extra commands for controller. Default: - [ './cluster-autoscaler', '--v=4', '----stderrthreshold=info', '--cloud-provider=aws', '--skip-nodes-with-local-storage=false', '--expander=least-waste' ]
        :param create_service_account: (experimental) service account for aws-load-balancer-controller. Default: - true
        :param image: (experimental) image for deployment.
        :param namespace: (experimental) Namespace. Default: - kube-system
        :param service_account_name: (experimental) Service Account Name. Default: - cluster-autoscaler

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if command is not None:
            self._values["command"] = command
        if create_service_account is not None:
            self._values["create_service_account"] = create_service_account
        if image is not None:
            self._values["image"] = image
        if namespace is not None:
            self._values["namespace"] = namespace
        if service_account_name is not None:
            self._values["service_account_name"] = service_account_name

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Extra commands for controller.

        :default:

        - [
        './cluster-autoscaler',
        '--v=4',
        '----stderrthreshold=info',
        '--cloud-provider=aws',
        '--skip-nodes-with-local-storage=false',
        '--expander=least-waste'
        ]

        :stability: experimental
        '''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def create_service_account(self) -> typing.Optional[builtins.bool]:
        '''(experimental) service account for aws-load-balancer-controller.

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("create_service_account")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        '''(experimental) image for deployment.

        :stability: experimental
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) Namespace.

        :default: - kube-system

        :stability: experimental
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_account_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Service Account Name.

        :default: - cluster-autoscaler

        :stability: experimental
        '''
        result = self._values.get("service_account_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterAutoScalerOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AwsClusterAutoScalerPolicyHelper",
    "ClusterAutoScaler",
    "ClusterAutoScalerOptions",
]

publication.publish()
