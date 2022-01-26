'''
# Construct Hub

This project maintains a [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) construct library
that can be used to deploy instances of the Construct Hub in any AWS Account.

This software backs the public instance of the
[ConstructHub](https://constructs.dev), and can be used to deploy a self-hosted
instance with personalized configuration.

## :question: Getting Started

> :warning: Disclaimer
>
> The [public instance of ConstructHub](https://constructs.dev) is Generally Available.
>
> Self-hosted ConstructHub instances are however in active development and
> should be considered *experimental*. Breaking changes to the public API of
> this package are expected to be released without prior notice, and the
> infrastructure and operational posture of ConstructHub instances may also
> significantly change.
>
> You are welcome to deploy self-hosted instances of ConstructHub for evaluation
> purposes, and we welcome any feedback (good or bad) from your experience in
> doing so.

### Quick Start

Once you have installed the `construct-hub` library in your project, the
simplest way to get started is to create an instance of the `ConstructHub`
construct:

```python
import { App, Stack } from '@aws-cdk/core';
import { ConstructHub } from 'construct-hub';

// The usual... you might have used `cdk init app` instead!
const app = new App();
const stack = new Stack(app, 'StackName', { /* ... */ });

// Now to business!
new ConstructHub(stack, 'ConstructHub');
```

### Personalization

#### Using a custom domain name

In order to use a custom domain for your ConstructHub instance instead of the
default CloudFront domain name, specify the `domain` property with the following
elements:

Attribute                     | Description
------------------------------|---------------------------------------------------------------------
`zone`                        | A Route53 Hosted Zone, where DNS records will be added.
`cert`                        | An Amazon Certificate Manager certificate, which must be in the `us-east-1` region.
`monitorCertificateExpiration`| Set to `false` if you do not want an alarm to be created when the certificate is close to expiry.

Your self-hosted ConstructHub instance will be served from the root of the
provided `zone`, so the certificate must match this name.

#### Alternate package sources

By default, ConstructHub has a single package source configured: the public
`npmjs.com` registry. Self-hosted instances typically should list packages from
alternate sources, either in addition to packages from `npmjs.com`, or instead
of those.

The `packageSources` property can be used to replace the default set of package
sources configured on the instance. ConstructHub provides `IPackageSource`
implementations for the public `npmjs.com` registry as well as for private
CodeArtifact repositories:

```python
import * as codeartifact from '@aws-cdk/aws-codeartifact';
import { App, Stack } from '@aws-cdk/core';
import { sources, ConstructHub } from 'construct-hub';

// The usual... you might have used `cdk init app` instead!
const app = new App();
const stack = new Stack(app, 'StackName', { /* ... */ });

// Now to business!
const registry = new codeartifact.CfnRegistry(stack, 'Registry', {
  // ....
});
new ConstructHub(stack, 'ConstructHub', {
  packageSources: [
    new sources.NpmJs(), // Remove if you do NOT want npmjs.com packages
    new sources.CodeArtifact({ registry }),
  ],
});
```

You may also implement a custom `IPackageSource` if you want to index packages
from alternate locations. In this case, the component you provide will be
responsible for sending notifications to an SQS Queue about newly discovered
packages. You may refer to the [sources.NpmJs](src/package-sources/npmjs.ts) and [sources.CodeArtifact](src/package-sources/code-artifact.ts)
implementations as a reference for hos this can be done.

By default, download counts of NPM packages will be fetched periodically from
NPM's public API by a Lambda. Since this is not desirable if you are using a
private package registry, this is automatically disabled if you specify your own
value for `packageSources`. (But this can be re-enabled through the
`fetchPackageStats` property if needed).

#### Package deny list

Certain packages may be undesirable to show in your self-hosted ConstructHub
instance. In order to prevent a package from ever being listed in construct hub,
the `denyList` property can be configured with a set of `DenyListRule` objects
that specify which package or package versions should never be lested:

```python
import { App, Stack } from '@aws-cdk/core';
import { ConstructHub } from 'construct-hub';

// The usual... you might have used `cdk init app` instead!
const app = new App();
const stack = new Stack(app, 'StackName', { /* ... */ });

// Now to business!
new ConstructHub(stack, 'ConstructHub', {
  denyList: [
    // Denying _all_ versions of the "sneaky-hackery" package
    { packageName: 'sneaky-hackery', reason: 'Mines bitcoins wherever it gets installed' },
    // Denying _a specific_ version of the "bad-release" package
    { packageName: 'bad-release', version: '1.2.3', reason: 'CVE-####-#####' },
  ],
});
```

#### Redirecting from additional domains

You can add additional domains that will be redirected to your primary Construct
Hub domain:

```python
import * as r53 from '@aws-cdk/aws-route53';

const myDomainZone = r53.HostedZone.fromHostedZoneAttributes(this, 'MyDomainZone', {
  hostedZoneId: 'AZ1234',
  zoneName: 'my.domain.com',
});

new ConstructHub(this, 'ConstructHub', {
  additionalDomains: [ { hostedZone: myDomainZone } ]
});
```

This will set up full domain redirect using Amazon S3 and Amazon CloudFront. All
requests will be redirected to your primary Construct Hub domain.

#### Decrease deployment footprint

By default, ConstructHub executes the documentation rendering process in the
context of isolated subnets. This is a defense-in-depth mechanism to mitigate
the risks associated with downloading aribtrary (un-trusted) *npm packages* and
their dependency closures.

This layer of security implies the creation of a number of resources that can
increase the operating cost of your self-hosted instance: several VPC endpoints
are created, an internal CodeArtifact repository needs to be provisioned, etc...

While we generally recommend leaving these features enabled, if your self-hosted
ConstructHub instance only indexes *trusted* packages (as could be the case for
an instance that does not list packages from the public `npmjs.com` registry),
you may set the `isolateLambdas` setting to `false`.

## :gear: Operating a self-hosted instance

1. [Application Overview](./docs/application-overview.md) provides a high-level
   description of the components that make a ConstructHub instance. This is a
   great starting point for people who consider operating a self-hosted instance
   of ConstructHub; and for new operators on-boarding the platform.
2. [Operator Runbook](./docs/operator-runbook.md) is a series of diagnostics and
   troubleshooting guides indended for operators to have a quick and easy way to
   navigate a ConstructHub instance when they are reacting to an alarm or bug
   report.

### :baby_chick: Deployment Canaries

Construct Hub provides several built-in validation mechanisms to make sure the
deployment of your instance is continuously operating as expected.

These mechanisms come in the form of canary testers that are part of the
ConstructHub deployment stack. Each canary runs periodically and performs a
different check, triggering a different CloudWatch alarm in case it detects a
failure.

We recommend that you use staged deployments, and block promotions to the
production stage in case any preivous stage triggers an alarm within a specific
timeframe.

#### Discovery Canary

When configuring an `NpmJs` package source, a package discovery canary can be
enabled using the `enableCanary` property (and optionally configured using the
`canaryPackage` and `canarySla` properties). This feature is activated by
default and monitors availability of releases of the `construct-hub-probe` npm
package in the ConstructHub instance.

Probe packages, such as `construct-hub-probe` are published frequently (e.g:
every 3 hours or more frequently), and can be used to ensure the ConstructHub
instance correctly discovers, indexes and represents those packages.

If a different package or SLA should be used, you can configure the `NpmJs`
package source manually like so:

```python
import * as codeartifact from '@aws-cdk/aws-codeartifact';
import { App, Stack } from '@aws-cdk/core';
import { sources, ConstructHub } from 'construct-hub';

const app = new App();
const stack = new Stack(app, 'StackName', { /* ... */ });

new ConstructHub(stack, 'ConstructHub', {
  // ...
  packageSources: [
    // ...
    new sources.NpmJs({
      enableCanary: true, // This is the default
      canaryPackage: '@acme/my-constructhub-probe',
      canarySla: Duration.minutes(30),
    }),
    // ...
  ],
  // ...
});
```

In case the new package isn't fully available in the predefined SLA, a
**high severity** CloudWatch alarm will trigger, which will in turn trigger
the configured action for low severity alarms.

> See [Monitoring & Alarms](./docs/application-overview.md#monitoring--alarming)

The operator runbook contains [instructions](./docs/operator-runbook.md) on how
to diagnose and mitigate the root cause of the failure.

### :nail_care: Customizing the frontend

There are a number of customizations available in order to make your private
construct hub better tailored to your organization.

#### Package Tags

Configuring package tags allows you to compute additional labels to be applied
to packages. These can be used to indicate to users which packages are owned by
trusted organizations, or any other arbitrary conditions, and can be referenced
while searching.

For example:

```python
new ConstructHub(this, "ConstructHub", {
  ...myProps,
  packageTags: [{
    id: 'official',
    condition: TagCondition.field('name').eq('construct-hub'),
    keyword: {
      label: 'Official',
      color: '#00FF00',
    },
    highlight: {
      label: 'Vended by AWS',
      color: '#00FF00',
    }
  }]
});
```

The above example will result in packages with the `name` of `construct-hub` to
receive the `Official` tag, which is colored green and displayed amongst the
list of keywords. Additionally the `highlight` key shows this as a highlighted
item on the package's card.

The `searchFilter` key can also be used to show tags as search filters grouped
together.

```python
const authorsGroup = new PackageTagGroup("authors", {
  label: "Authors",
  tooltip: "Information about the authors filter",
  filterType: FilterType.checkbox(),
});

const isAws = TagCondition.field('name').eq('construct-hub');
new ConstructHub(this, "ConstructHub", {
  ...myProps,
  packageTags: [{
    id: 'AWS',
    condition: isAws,
    searchFilter: {
      group: authorsGroup,
      display: 'AWS',
    },
  }, {
    id: 'Community',
    condition: TagCondition.not(isAws),
    searchFilter: {
      group: authorsGroup,
      display: 'AWS',
    },
  }]
});
```

The above will show a list of `Authors` filters on the search results page
with a checkbox for each `AWS` and `Community` packages, allowing users to
filter results by the presence of these tags.

Combinations of conditions are also supported:

```python
new ConstructHub(this, "ConstructHub", {
  ...myProps,
  packageTags: [{
    label: 'Official',
    color: '#00FF00',
    condition: TagCondition.or(
      TagCondition.field('name').eq('construct-hub'),
      TagCondition.field('name').eq('construct-hub-webapp'),
    ),
  }]
});

// or more succintly if you have a long list
condition: TagCondition.or(
  ...['construct-hub', 'construct-hub-webapp', '...',]
    .map(name => TagCondition.field('name').eq(name))
),
```

You can assert against any value within package json including nested ones.

```python
TagCondition.field('constructHub', 'nested', 'key').eq('value');

// checks
packageJson?.constructHub?.nested?.key === value;
```

You can also assert that a string occurs at least a certain number of times
within the package's README.

```python
TagCondition.readme().includes('ECS');
TagCondition.readme().includes('fargate', { atLeast: 3, caseSensitive: false });
```

#### Package Links

Configuring package links allows you to replace the `Repository`, `License`,
and `Registry` links on the package details page with whatever you choose.

For example:

```python
new ConstructHub(this, "ConstructHub", {
  ...myProps,
  packageLinks: [{
    linkLabel: 'Service Level Agreement',
    configKey: 'SLA',
  }, {
    linkLabel: 'Contact',
    configKey: 'Contact',
    linkText: 'Email Me!',
    allowedDomains: ['me.com'],
  }]
});
```

This would allow publishers to add the following to their package.json:

```json
"constructHub": {
  "packageLinks": {
    "SLA": "https://support.mypackage.com",
    "Contact": "me.com/contact"
  }
}
```

Then the links on the corresponding package page would show these items as
configured.

#### Home Page

The home page is divided into sections, each with a header and list of packages.
Currently, for a given section you can display either the most recently updated
packages, or a curated list of packages.

For example:

```python
new ConstructHub(this, "ConstructHub", {
  ...myProps,
  featuredPackages: {
    sections: [
      {
        name: "Recently updated",
        showLastUpdated: 4
      },
      {
        name: "From the AWS CDK",
        showPackages: [
          {
            name: "@aws-cdk/core"
          },
          {
            name: "@aws-cdk/aws-s3",
            comment: "One of the most popular AWS CDK libraries!"
          },
          {
            name: "@aws-cdk/aws-lambda"
          },
          {
            name: "@aws-cdk/pipelines"
            comment: "The pipelines L3 construct library abstracts away many of the details of managing software deployment within AWS."
          }
        ]
      }
    ]
  }
});
```

#### Browse Categories

The Construct Hub home page includes a section that displays a set of buttons
that represent browsing categories (e.g. "Databases", "Monitoring",
"Serverless", etc).

You can use the `categories` option to configure these categories. Each category
is defined by a `title` and a `url`, which will be the link associated with the
button.

```python
new ConstructHub(this, "ConstructHub", {
  ...myProps,
  categories: [
    { title: 'Databases', url: '?keywords=databases' },
    { title: 'Monitoring', url: '?q=monitoring' },
    { title: 'Partners', url: '?tags=aws-partner' }
  ]
});
```

#### Feature Flags

Feature flags for the web app can be used to enable or disable experimental
features. These can be customized through the `featureFlags` property - for
more information about the available flags, check the documentation for
[https://github.com/cdklabs/construct-hub-webapp/](https://github.com/cdklabs/construct-hub-webapp/).

## :raised_hand: Contributing

If you are looking to contribute to this project, but don't know where to start,
have a look at our [contributing guide](CONTRIBUTING.md)!

## :cop: Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more
information.

## :balance_scale: License

This project is licensed under the Apache-2.0 License.
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

import aws_cdk.aws_certificatemanager
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.aws_route53
import aws_cdk.aws_s3
import aws_cdk.aws_sqs
import aws_cdk.core
import constructs


@jsii.data_type(
    jsii_type="construct-hub.AlarmActions",
    jsii_struct_bases=[],
    name_mapping={
        "high_severity": "highSeverity",
        "high_severity_action": "highSeverityAction",
        "normal_severity": "normalSeverity",
        "normal_severity_action": "normalSeverityAction",
    },
)
class AlarmActions:
    def __init__(
        self,
        *,
        high_severity: typing.Optional[builtins.str] = None,
        high_severity_action: typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction] = None,
        normal_severity: typing.Optional[builtins.str] = None,
        normal_severity_action: typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction] = None,
    ) -> None:
        '''(experimental) CloudWatch alarm actions to perform.

        :param high_severity: (experimental) The ARN of the CloudWatch alarm action to take for alarms of high-severity alarms. This must be an ARN that can be used with CloudWatch alarms.
        :param high_severity_action: (experimental) The CloudWatch alarm action to take for alarms of high-severity alarms. This must be an ARN that can be used with CloudWatch alarms.
        :param normal_severity: (experimental) The ARN of the CloudWatch alarm action to take for alarms of normal severity. This must be an ARN that can be used with CloudWatch alarms. Default: - no actions are taken in response to alarms of normal severity
        :param normal_severity_action: (experimental) The CloudWatch alarm action to take for alarms of normal severity. This must be an ARN that can be used with CloudWatch alarms. Default: - no actions are taken in response to alarms of normal severity

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if high_severity is not None:
            self._values["high_severity"] = high_severity
        if high_severity_action is not None:
            self._values["high_severity_action"] = high_severity_action
        if normal_severity is not None:
            self._values["normal_severity"] = normal_severity
        if normal_severity_action is not None:
            self._values["normal_severity_action"] = normal_severity_action

    @builtins.property
    def high_severity(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the CloudWatch alarm action to take for alarms of high-severity alarms.

        This must be an ARN that can be used with CloudWatch alarms.

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html#alarms-and-actions
        :stability: experimental
        '''
        result = self._values.get("high_severity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def high_severity_action(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction]:
        '''(experimental) The CloudWatch alarm action to take for alarms of high-severity alarms.

        This must be an ARN that can be used with CloudWatch alarms.

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html#alarms-and-actions
        :stability: experimental
        '''
        result = self._values.get("high_severity_action")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction], result)

    @builtins.property
    def normal_severity(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the CloudWatch alarm action to take for alarms of normal severity.

        This must be an ARN that can be used with CloudWatch alarms.

        :default: - no actions are taken in response to alarms of normal severity

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html#alarms-and-actions
        :stability: experimental
        '''
        result = self._values.get("normal_severity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def normal_severity_action(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction]:
        '''(experimental) The CloudWatch alarm action to take for alarms of normal severity.

        This must be an ARN that can be used with CloudWatch alarms.

        :default: - no actions are taken in response to alarms of normal severity

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html#alarms-and-actions
        :stability: experimental
        '''
        result = self._values.get("normal_severity_action")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudwatch.IAlarmAction], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlarmActions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.Category",
    jsii_struct_bases=[],
    name_mapping={"title": "title", "url": "url"},
)
class Category:
    def __init__(self, *, title: builtins.str, url: builtins.str) -> None:
        '''(experimental) A category of packages.

        :param title: (experimental) The title on the category button as it appears in the Construct Hub home page.
        :param url: (experimental) The URL that this category links to. This is the full path to the link that this category button will have. You can use any query options such as ``?keywords=``, ``?q=``, or a combination thereof.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "title": title,
            "url": url,
        }

    @builtins.property
    def title(self) -> builtins.str:
        '''(experimental) The title on the category button as it appears in the Construct Hub home page.

        :stability: experimental
        '''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''(experimental) The URL that this category links to.

        This is the full path to the link that
        this category button will have. You can use any query options such as
        ``?keywords=``, ``?q=``, or a combination thereof.

        :stability: experimental

        Example::

            "/search?keywords=monitoring"
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Category(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.CodeArtifactDomainProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "upstreams": "upstreams"},
)
class CodeArtifactDomainProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        upstreams: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Information pertaining to an existing CodeArtifact Domain.

        :param name: (experimental) The name of the CodeArtifact domain.
        :param upstreams: (experimental) Any upstream repositories in this CodeArtifact domain that should be configured on the internal CodeArtifact repository.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if upstreams is not None:
            self._values["upstreams"] = upstreams

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the CodeArtifact domain.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def upstreams(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Any upstream repositories in this CodeArtifact domain that should be configured on the internal CodeArtifact repository.

        :stability: experimental
        '''
        result = self._values.get("upstreams")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeArtifactDomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_iam.IGrantable)
class ConstructHub(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="construct-hub.ConstructHub",
):
    '''(experimental) Construct Hub.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        additional_domains: typing.Optional[typing.Sequence["DomainRedirectSource"]] = None,
        alarm_actions: typing.Optional[AlarmActions] = None,
        allowed_licenses: typing.Optional[typing.Sequence["SpdxLicense"]] = None,
        backend_dashboard_name: typing.Optional[builtins.str] = None,
        categories: typing.Optional[typing.Sequence[Category]] = None,
        code_artifact_domain: typing.Optional[CodeArtifactDomainProps] = None,
        deny_list: typing.Optional[typing.Sequence["DenyListRule"]] = None,
        domain: typing.Optional["Domain"] = None,
        failover_storage: typing.Optional[builtins.bool] = None,
        featured_packages: typing.Optional["FeaturedPackages"] = None,
        feature_flags: typing.Optional["FeatureFlags"] = None,
        fetch_package_stats: typing.Optional[builtins.bool] = None,
        isolate_sensitive_tasks: typing.Optional[builtins.bool] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        package_links: typing.Optional[typing.Sequence["PackageLinkConfig"]] = None,
        package_sources: typing.Optional[typing.Sequence["IPackageSource"]] = None,
        package_tag_groups: typing.Optional[typing.Sequence["PackageTagGroup"]] = None,
        package_tags: typing.Optional[typing.Sequence["PackageTag"]] = None,
        preload_script: typing.Optional["PreloadFile"] = None,
        reprocess_frequency: typing.Optional[aws_cdk.core.Duration] = None,
        sensitive_task_isolation: typing.Optional["Isolation"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param additional_domains: (experimental) Additional domains which will be set up to redirect to the primary construct hub domain. Default: []
        :param alarm_actions: (experimental) Actions to perform when alarms are set.
        :param allowed_licenses: (experimental) The allowed licenses for packages indexed by this instance of ConstructHub. Default: [...SpdxLicense.apache(),...SpdxLicense.bsd(),...SpdxLicense.cddl(),...SpdxLicense.epl(),SpdxLicense.ISC,...SpdxLicense.mit(),SpdxLicense.MPL_2_0]
        :param backend_dashboard_name: (experimental) The name of the CloudWatch dashboard that represents the health of backend systems.
        :param categories: (experimental) Browse categories. Each category will appear in the home page as a button with a link to the relevant search query.
        :param code_artifact_domain: (experimental) When using a CodeArtifact package source, it is often desirable to have ConstructHub provision it's internal CodeArtifact repository in the same CodeArtifact domain, and to configure the package source repository as an upstream of the internal repository. This way, all packages in the source are available to ConstructHub's backend processing. Default: - none.
        :param deny_list: (experimental) A list of packages to block from the construct hub. Default: []
        :param domain: (experimental) Connect the hub to a domain (requires a hosted zone and a certificate).
        :param failover_storage: (experimental) Wire construct hub to use the failover storage buckets. Do not activate this property until you've populated your failover buckets with the necessary data. Default: false
        :param featured_packages: (experimental) Configuration for packages to feature on the home page. Default: - Display the 10 most recently updated packages
        :param feature_flags: (experimental) Configure feature flags for the web app.
        :param fetch_package_stats: (experimental) Configure whether or not the backend should periodically query NPM for the number of downloads a package has in the past week, and display download counts on the web app. Default: - true if packageSources is not specified (the defaults are used), false otherwise
        :param isolate_sensitive_tasks: (deprecated) Whether compute environments for sensitive tasks (which operate on un-trusted complex data, such as the transliterator, which operates with externally-sourced npm package tarballs) should run in network-isolated environments. This implies the creation of additonal resources, including: - A VPC with only isolated subnets. - VPC Endpoints (CloudWatch Logs, CodeArtifact, CodeArtifact API, S3, ...) - A CodeArtifact Repository with an external connection to npmjs.com
        :param log_retention: (experimental) How long to retain CloudWatch logs for.
        :param package_links: (experimental) Configuration for custom package page links.
        :param package_sources: (experimental) The package sources to register with this ConstructHub instance. Default: - a standard npmjs.com package source will be configured.
        :param package_tag_groups: (experimental) Optional configuration for grouping custom package tags.
        :param package_tags: (experimental) Configuration for custom package tags.
        :param preload_script: (experimental) Javascript to run on webapp before app loads.
        :param reprocess_frequency: (experimental) How frequently all packages should get fully reprocessed. See the operator runbook for more information about reprocessing. Default: - never
        :param sensitive_task_isolation: (experimental) Whether compute environments for sensitive tasks (which operate on un-trusted complex data, such as the transliterator, which operates with externally-sourced npm package tarballs) should run in network-isolated environments. This implies the creation of additonal resources, including: - A VPC with only isolated subnets. - VPC Endpoints (CloudWatch Logs, CodeArtifact, CodeArtifact API, S3, ...) - A CodeArtifact Repository with an external connection to npmjs.com Default: Isolation.NO_INTERNET_ACCESS

        :stability: experimental
        '''
        props = ConstructHubProps(
            additional_domains=additional_domains,
            alarm_actions=alarm_actions,
            allowed_licenses=allowed_licenses,
            backend_dashboard_name=backend_dashboard_name,
            categories=categories,
            code_artifact_domain=code_artifact_domain,
            deny_list=deny_list,
            domain=domain,
            failover_storage=failover_storage,
            featured_packages=featured_packages,
            feature_flags=feature_flags,
            fetch_package_stats=fetch_package_stats,
            isolate_sensitive_tasks=isolate_sensitive_tasks,
            log_retention=log_retention,
            package_links=package_links,
            package_sources=package_sources,
            package_tag_groups=package_tag_groups,
            package_tags=package_tags,
            preload_script=preload_script,
            reprocess_frequency=reprocess_frequency,
            sensitive_task_isolation=sensitive_task_isolation,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingestionQueue")
    def ingestion_queue(self) -> aws_cdk.aws_sqs.IQueue:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_sqs.IQueue, jsii.get(self, "ingestionQueue"))


@jsii.data_type(
    jsii_type="construct-hub.ConstructHubProps",
    jsii_struct_bases=[],
    name_mapping={
        "additional_domains": "additionalDomains",
        "alarm_actions": "alarmActions",
        "allowed_licenses": "allowedLicenses",
        "backend_dashboard_name": "backendDashboardName",
        "categories": "categories",
        "code_artifact_domain": "codeArtifactDomain",
        "deny_list": "denyList",
        "domain": "domain",
        "failover_storage": "failoverStorage",
        "featured_packages": "featuredPackages",
        "feature_flags": "featureFlags",
        "fetch_package_stats": "fetchPackageStats",
        "isolate_sensitive_tasks": "isolateSensitiveTasks",
        "log_retention": "logRetention",
        "package_links": "packageLinks",
        "package_sources": "packageSources",
        "package_tag_groups": "packageTagGroups",
        "package_tags": "packageTags",
        "preload_script": "preloadScript",
        "reprocess_frequency": "reprocessFrequency",
        "sensitive_task_isolation": "sensitiveTaskIsolation",
    },
)
class ConstructHubProps:
    def __init__(
        self,
        *,
        additional_domains: typing.Optional[typing.Sequence["DomainRedirectSource"]] = None,
        alarm_actions: typing.Optional[AlarmActions] = None,
        allowed_licenses: typing.Optional[typing.Sequence["SpdxLicense"]] = None,
        backend_dashboard_name: typing.Optional[builtins.str] = None,
        categories: typing.Optional[typing.Sequence[Category]] = None,
        code_artifact_domain: typing.Optional[CodeArtifactDomainProps] = None,
        deny_list: typing.Optional[typing.Sequence["DenyListRule"]] = None,
        domain: typing.Optional["Domain"] = None,
        failover_storage: typing.Optional[builtins.bool] = None,
        featured_packages: typing.Optional["FeaturedPackages"] = None,
        feature_flags: typing.Optional["FeatureFlags"] = None,
        fetch_package_stats: typing.Optional[builtins.bool] = None,
        isolate_sensitive_tasks: typing.Optional[builtins.bool] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        package_links: typing.Optional[typing.Sequence["PackageLinkConfig"]] = None,
        package_sources: typing.Optional[typing.Sequence["IPackageSource"]] = None,
        package_tag_groups: typing.Optional[typing.Sequence["PackageTagGroup"]] = None,
        package_tags: typing.Optional[typing.Sequence["PackageTag"]] = None,
        preload_script: typing.Optional["PreloadFile"] = None,
        reprocess_frequency: typing.Optional[aws_cdk.core.Duration] = None,
        sensitive_task_isolation: typing.Optional["Isolation"] = None,
    ) -> None:
        '''(experimental) Props for ``ConstructHub``.

        :param additional_domains: (experimental) Additional domains which will be set up to redirect to the primary construct hub domain. Default: []
        :param alarm_actions: (experimental) Actions to perform when alarms are set.
        :param allowed_licenses: (experimental) The allowed licenses for packages indexed by this instance of ConstructHub. Default: [...SpdxLicense.apache(),...SpdxLicense.bsd(),...SpdxLicense.cddl(),...SpdxLicense.epl(),SpdxLicense.ISC,...SpdxLicense.mit(),SpdxLicense.MPL_2_0]
        :param backend_dashboard_name: (experimental) The name of the CloudWatch dashboard that represents the health of backend systems.
        :param categories: (experimental) Browse categories. Each category will appear in the home page as a button with a link to the relevant search query.
        :param code_artifact_domain: (experimental) When using a CodeArtifact package source, it is often desirable to have ConstructHub provision it's internal CodeArtifact repository in the same CodeArtifact domain, and to configure the package source repository as an upstream of the internal repository. This way, all packages in the source are available to ConstructHub's backend processing. Default: - none.
        :param deny_list: (experimental) A list of packages to block from the construct hub. Default: []
        :param domain: (experimental) Connect the hub to a domain (requires a hosted zone and a certificate).
        :param failover_storage: (experimental) Wire construct hub to use the failover storage buckets. Do not activate this property until you've populated your failover buckets with the necessary data. Default: false
        :param featured_packages: (experimental) Configuration for packages to feature on the home page. Default: - Display the 10 most recently updated packages
        :param feature_flags: (experimental) Configure feature flags for the web app.
        :param fetch_package_stats: (experimental) Configure whether or not the backend should periodically query NPM for the number of downloads a package has in the past week, and display download counts on the web app. Default: - true if packageSources is not specified (the defaults are used), false otherwise
        :param isolate_sensitive_tasks: (deprecated) Whether compute environments for sensitive tasks (which operate on un-trusted complex data, such as the transliterator, which operates with externally-sourced npm package tarballs) should run in network-isolated environments. This implies the creation of additonal resources, including: - A VPC with only isolated subnets. - VPC Endpoints (CloudWatch Logs, CodeArtifact, CodeArtifact API, S3, ...) - A CodeArtifact Repository with an external connection to npmjs.com
        :param log_retention: (experimental) How long to retain CloudWatch logs for.
        :param package_links: (experimental) Configuration for custom package page links.
        :param package_sources: (experimental) The package sources to register with this ConstructHub instance. Default: - a standard npmjs.com package source will be configured.
        :param package_tag_groups: (experimental) Optional configuration for grouping custom package tags.
        :param package_tags: (experimental) Configuration for custom package tags.
        :param preload_script: (experimental) Javascript to run on webapp before app loads.
        :param reprocess_frequency: (experimental) How frequently all packages should get fully reprocessed. See the operator runbook for more information about reprocessing. Default: - never
        :param sensitive_task_isolation: (experimental) Whether compute environments for sensitive tasks (which operate on un-trusted complex data, such as the transliterator, which operates with externally-sourced npm package tarballs) should run in network-isolated environments. This implies the creation of additonal resources, including: - A VPC with only isolated subnets. - VPC Endpoints (CloudWatch Logs, CodeArtifact, CodeArtifact API, S3, ...) - A CodeArtifact Repository with an external connection to npmjs.com Default: Isolation.NO_INTERNET_ACCESS

        :stability: experimental
        '''
        if isinstance(alarm_actions, dict):
            alarm_actions = AlarmActions(**alarm_actions)
        if isinstance(code_artifact_domain, dict):
            code_artifact_domain = CodeArtifactDomainProps(**code_artifact_domain)
        if isinstance(domain, dict):
            domain = Domain(**domain)
        if isinstance(featured_packages, dict):
            featured_packages = FeaturedPackages(**featured_packages)
        if isinstance(feature_flags, dict):
            feature_flags = FeatureFlags(**feature_flags)
        self._values: typing.Dict[str, typing.Any] = {}
        if additional_domains is not None:
            self._values["additional_domains"] = additional_domains
        if alarm_actions is not None:
            self._values["alarm_actions"] = alarm_actions
        if allowed_licenses is not None:
            self._values["allowed_licenses"] = allowed_licenses
        if backend_dashboard_name is not None:
            self._values["backend_dashboard_name"] = backend_dashboard_name
        if categories is not None:
            self._values["categories"] = categories
        if code_artifact_domain is not None:
            self._values["code_artifact_domain"] = code_artifact_domain
        if deny_list is not None:
            self._values["deny_list"] = deny_list
        if domain is not None:
            self._values["domain"] = domain
        if failover_storage is not None:
            self._values["failover_storage"] = failover_storage
        if featured_packages is not None:
            self._values["featured_packages"] = featured_packages
        if feature_flags is not None:
            self._values["feature_flags"] = feature_flags
        if fetch_package_stats is not None:
            self._values["fetch_package_stats"] = fetch_package_stats
        if isolate_sensitive_tasks is not None:
            self._values["isolate_sensitive_tasks"] = isolate_sensitive_tasks
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if package_links is not None:
            self._values["package_links"] = package_links
        if package_sources is not None:
            self._values["package_sources"] = package_sources
        if package_tag_groups is not None:
            self._values["package_tag_groups"] = package_tag_groups
        if package_tags is not None:
            self._values["package_tags"] = package_tags
        if preload_script is not None:
            self._values["preload_script"] = preload_script
        if reprocess_frequency is not None:
            self._values["reprocess_frequency"] = reprocess_frequency
        if sensitive_task_isolation is not None:
            self._values["sensitive_task_isolation"] = sensitive_task_isolation

    @builtins.property
    def additional_domains(
        self,
    ) -> typing.Optional[typing.List["DomainRedirectSource"]]:
        '''(experimental) Additional domains which will be set up to redirect to the primary construct hub domain.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("additional_domains")
        return typing.cast(typing.Optional[typing.List["DomainRedirectSource"]], result)

    @builtins.property
    def alarm_actions(self) -> typing.Optional[AlarmActions]:
        '''(experimental) Actions to perform when alarms are set.

        :stability: experimental
        '''
        result = self._values.get("alarm_actions")
        return typing.cast(typing.Optional[AlarmActions], result)

    @builtins.property
    def allowed_licenses(self) -> typing.Optional[typing.List["SpdxLicense"]]:
        '''(experimental) The allowed licenses for packages indexed by this instance of ConstructHub.

        :default: [...SpdxLicense.apache(),...SpdxLicense.bsd(),...SpdxLicense.cddl(),...SpdxLicense.epl(),SpdxLicense.ISC,...SpdxLicense.mit(),SpdxLicense.MPL_2_0]

        :stability: experimental
        '''
        result = self._values.get("allowed_licenses")
        return typing.cast(typing.Optional[typing.List["SpdxLicense"]], result)

    @builtins.property
    def backend_dashboard_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the CloudWatch dashboard that represents the health of backend systems.

        :stability: experimental
        '''
        result = self._values.get("backend_dashboard_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def categories(self) -> typing.Optional[typing.List[Category]]:
        '''(experimental) Browse categories.

        Each category will appear in the home page as a button
        with a link to the relevant search query.

        :stability: experimental
        '''
        result = self._values.get("categories")
        return typing.cast(typing.Optional[typing.List[Category]], result)

    @builtins.property
    def code_artifact_domain(self) -> typing.Optional[CodeArtifactDomainProps]:
        '''(experimental) When using a CodeArtifact package source, it is often desirable to have ConstructHub provision it's internal CodeArtifact repository in the same CodeArtifact domain, and to configure the package source repository as an upstream of the internal repository.

        This way, all packages in the source
        are available to ConstructHub's backend processing.

        :default: - none.

        :stability: experimental
        '''
        result = self._values.get("code_artifact_domain")
        return typing.cast(typing.Optional[CodeArtifactDomainProps], result)

    @builtins.property
    def deny_list(self) -> typing.Optional[typing.List["DenyListRule"]]:
        '''(experimental) A list of packages to block from the construct hub.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("deny_list")
        return typing.cast(typing.Optional[typing.List["DenyListRule"]], result)

    @builtins.property
    def domain(self) -> typing.Optional["Domain"]:
        '''(experimental) Connect the hub to a domain (requires a hosted zone and a certificate).

        :stability: experimental
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional["Domain"], result)

    @builtins.property
    def failover_storage(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Wire construct hub to use the failover storage buckets.

        Do not activate this property until you've populated your failover buckets
        with the necessary data.

        :default: false

        :see: https://github.com/cdklabs/construct-hub/blob/dev/docs/operator-runbook.md#storage-disaster
        :stability: experimental
        '''
        result = self._values.get("failover_storage")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def featured_packages(self) -> typing.Optional["FeaturedPackages"]:
        '''(experimental) Configuration for packages to feature on the home page.

        :default: - Display the 10 most recently updated packages

        :stability: experimental
        '''
        result = self._values.get("featured_packages")
        return typing.cast(typing.Optional["FeaturedPackages"], result)

    @builtins.property
    def feature_flags(self) -> typing.Optional["FeatureFlags"]:
        '''(experimental) Configure feature flags for the web app.

        :stability: experimental
        '''
        result = self._values.get("feature_flags")
        return typing.cast(typing.Optional["FeatureFlags"], result)

    @builtins.property
    def fetch_package_stats(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Configure whether or not the backend should periodically query NPM for the number of downloads a package has in the past week, and display download counts on the web app.

        :default:

        - true if packageSources is not specified (the defaults are
        used), false otherwise

        :stability: experimental
        '''
        result = self._values.get("fetch_package_stats")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def isolate_sensitive_tasks(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether compute environments for sensitive tasks (which operate on un-trusted complex data, such as the transliterator, which operates with externally-sourced npm package tarballs) should run in network-isolated environments.

        This implies the creation of additonal resources, including:

        - A VPC with only isolated subnets.
        - VPC Endpoints (CloudWatch Logs, CodeArtifact, CodeArtifact API, S3, ...)
        - A CodeArtifact Repository with an external connection to npmjs.com

        :deprecated: use sensitiveTaskIsolation instead.

        :stability: deprecated
        '''
        result = self._values.get("isolate_sensitive_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''(experimental) How long to retain CloudWatch logs for.

        :stability: experimental
        :defaults: RetentionDays.TEN_YEARS
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def package_links(self) -> typing.Optional[typing.List["PackageLinkConfig"]]:
        '''(experimental) Configuration for custom package page links.

        :stability: experimental
        '''
        result = self._values.get("package_links")
        return typing.cast(typing.Optional[typing.List["PackageLinkConfig"]], result)

    @builtins.property
    def package_sources(self) -> typing.Optional[typing.List["IPackageSource"]]:
        '''(experimental) The package sources to register with this ConstructHub instance.

        :default: - a standard npmjs.com package source will be configured.

        :stability: experimental
        '''
        result = self._values.get("package_sources")
        return typing.cast(typing.Optional[typing.List["IPackageSource"]], result)

    @builtins.property
    def package_tag_groups(self) -> typing.Optional[typing.List["PackageTagGroup"]]:
        '''(experimental) Optional configuration for grouping custom package tags.

        :stability: experimental
        '''
        result = self._values.get("package_tag_groups")
        return typing.cast(typing.Optional[typing.List["PackageTagGroup"]], result)

    @builtins.property
    def package_tags(self) -> typing.Optional[typing.List["PackageTag"]]:
        '''(experimental) Configuration for custom package tags.

        :stability: experimental
        '''
        result = self._values.get("package_tags")
        return typing.cast(typing.Optional[typing.List["PackageTag"]], result)

    @builtins.property
    def preload_script(self) -> typing.Optional["PreloadFile"]:
        '''(experimental) Javascript to run on webapp before app loads.

        :stability: experimental
        '''
        result = self._values.get("preload_script")
        return typing.cast(typing.Optional["PreloadFile"], result)

    @builtins.property
    def reprocess_frequency(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''(experimental) How frequently all packages should get fully reprocessed.

        See the operator runbook for more information about reprocessing.

        :default: - never

        :see: https://github.com/cdklabs/construct-hub/blob/main/docs/operator-runbook.md
        :stability: experimental
        '''
        result = self._values.get("reprocess_frequency")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def sensitive_task_isolation(self) -> typing.Optional["Isolation"]:
        '''(experimental) Whether compute environments for sensitive tasks (which operate on un-trusted complex data, such as the transliterator, which operates with externally-sourced npm package tarballs) should run in network-isolated environments.

        This implies the creation of additonal resources, including:

        - A VPC with only isolated subnets.
        - VPC Endpoints (CloudWatch Logs, CodeArtifact, CodeArtifact API, S3, ...)
        - A CodeArtifact Repository with an external connection to npmjs.com

        :default: Isolation.NO_INTERNET_ACCESS

        :stability: experimental
        '''
        result = self._values.get("sensitive_task_isolation")
        return typing.cast(typing.Optional["Isolation"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConstructHubProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.DenyListMap",
    jsii_struct_bases=[],
    name_mapping={},
)
class DenyListMap:
    def __init__(self) -> None:
        '''(experimental) The contents of the deny list file in S3.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DenyListMap(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.DenyListRule",
    jsii_struct_bases=[],
    name_mapping={
        "package_name": "packageName",
        "reason": "reason",
        "version": "version",
    },
)
class DenyListRule:
    def __init__(
        self,
        *,
        package_name: builtins.str,
        reason: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) An entry in the list of packages blocked from display in the construct hub.

        :param package_name: (experimental) The name of the package to block (npm).
        :param reason: (experimental) The reason why this package/version is denied. This information will be emitted to the construct hub logs.
        :param version: (experimental) The package version to block (must be a valid version such as "1.0.3"). Default: - all versions of this package are blocked.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "package_name": package_name,
            "reason": reason,
        }
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def package_name(self) -> builtins.str:
        '''(experimental) The name of the package to block (npm).

        :stability: experimental
        '''
        result = self._values.get("package_name")
        assert result is not None, "Required property 'package_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def reason(self) -> builtins.str:
        '''(experimental) The reason why this package/version is denied.

        This information will be
        emitted to the construct hub logs.

        :stability: experimental
        '''
        result = self._values.get("reason")
        assert result is not None, "Required property 'reason' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The package version to block (must be a valid version such as "1.0.3").

        :default: - all versions of this package are blocked.

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DenyListRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.Domain",
    jsii_struct_bases=[],
    name_mapping={
        "cert": "cert",
        "zone": "zone",
        "monitor_certificate_expiration": "monitorCertificateExpiration",
    },
)
class Domain:
    def __init__(
        self,
        *,
        cert: aws_cdk.aws_certificatemanager.ICertificate,
        zone: aws_cdk.aws_route53.IHostedZone,
        monitor_certificate_expiration: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Domain configuration for the website.

        :param cert: (experimental) The certificate to use for serving the Construct Hub over a custom domain. Default: - a DNS-Validated certificate will be provisioned using the provided ``hostedZone``.
        :param zone: (experimental) The root domain name where this instance of Construct Hub will be served.
        :param monitor_certificate_expiration: (experimental) Whether the certificate should be monitored for expiration, meaning high severity alarms will be raised if it is due to expire in less than 45 days. Default: true

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cert": cert,
            "zone": zone,
        }
        if monitor_certificate_expiration is not None:
            self._values["monitor_certificate_expiration"] = monitor_certificate_expiration

    @builtins.property
    def cert(self) -> aws_cdk.aws_certificatemanager.ICertificate:
        '''(experimental) The certificate to use for serving the Construct Hub over a custom domain.

        :default:

        - a DNS-Validated certificate will be provisioned using the
        provided ``hostedZone``.

        :stability: experimental
        '''
        result = self._values.get("cert")
        assert result is not None, "Required property 'cert' is missing"
        return typing.cast(aws_cdk.aws_certificatemanager.ICertificate, result)

    @builtins.property
    def zone(self) -> aws_cdk.aws_route53.IHostedZone:
        '''(experimental) The root domain name where this instance of Construct Hub will be served.

        :stability: experimental
        '''
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    @builtins.property
    def monitor_certificate_expiration(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the certificate should be monitored for expiration, meaning high severity alarms will be raised if it is due to expire in less than 45 days.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("monitor_certificate_expiration")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Domain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.DomainRedirectSource",
    jsii_struct_bases=[],
    name_mapping={"hosted_zone": "hostedZone", "certificate": "certificate"},
)
class DomainRedirectSource:
    def __init__(
        self,
        *,
        hosted_zone: aws_cdk.aws_route53.IHostedZone,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
    ) -> None:
        '''(experimental) Source domain of the redirect.

        :param hosted_zone: (experimental) The route53 zone which hosts the source domain.
        :param certificate: (experimental) The ACM certificate to use for the CloudFront distribution. Default: - a certificate is created for this domain.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hosted_zone": hosted_zone,
        }
        if certificate is not None:
            self._values["certificate"] = certificate

    @builtins.property
    def hosted_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        '''(experimental) The route53 zone which hosts the source domain.

        :stability: experimental
        '''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''(experimental) The ACM certificate to use for the CloudFront distribution.

        :default: - a certificate is created for this domain.

        :stability: experimental
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainRedirectSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.FeatureFlags",
    jsii_struct_bases=[],
    name_mapping={
        "home_redesign": "homeRedesign",
        "search_redesign": "searchRedesign",
    },
)
class FeatureFlags:
    def __init__(
        self,
        *,
        home_redesign: typing.Optional[builtins.bool] = None,
        search_redesign: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Enable/disable features for the web app.

        :param home_redesign: 
        :param search_redesign: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if home_redesign is not None:
            self._values["home_redesign"] = home_redesign
        if search_redesign is not None:
            self._values["search_redesign"] = search_redesign

    @builtins.property
    def home_redesign(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("home_redesign")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def search_redesign(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("search_redesign")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FeatureFlags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.FeaturedPackages",
    jsii_struct_bases=[],
    name_mapping={"sections": "sections"},
)
class FeaturedPackages:
    def __init__(self, *, sections: typing.Sequence["FeaturedPackagesSection"]) -> None:
        '''(experimental) Configuration for packages to feature on the home page.

        :param sections: (experimental) Grouped sections of packages on the homepage.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "sections": sections,
        }

    @builtins.property
    def sections(self) -> typing.List["FeaturedPackagesSection"]:
        '''(experimental) Grouped sections of packages on the homepage.

        :stability: experimental
        '''
        result = self._values.get("sections")
        assert result is not None, "Required property 'sections' is missing"
        return typing.cast(typing.List["FeaturedPackagesSection"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FeaturedPackages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.FeaturedPackagesDetail",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "comment": "comment"},
)
class FeaturedPackagesDetail:
    def __init__(
        self,
        *,
        name: builtins.str,
        comment: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Customization options for a specific package on the home page.

        :param name: (experimental) The name of the package.
        :param comment: (experimental) An additional comment to include with the package.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if comment is not None:
            self._values["comment"] = comment

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the package.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''(experimental) An additional comment to include with the package.

        :stability: experimental
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FeaturedPackagesDetail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.FeaturedPackagesSection",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "show_last_updated": "showLastUpdated",
        "show_packages": "showPackages",
    },
)
class FeaturedPackagesSection:
    def __init__(
        self,
        *,
        name: builtins.str,
        show_last_updated: typing.Optional[jsii.Number] = None,
        show_packages: typing.Optional[typing.Sequence[FeaturedPackagesDetail]] = None,
    ) -> None:
        '''(experimental) Customization options for one section of the home page.

        :param name: (experimental) The name of the section (displayed as a header).
        :param show_last_updated: (experimental) Show the N most recently updated packages in this section. Cannot be used with ``showPackages``.
        :param show_packages: (experimental) Show an explicit list of packages. Cannot be used with ``showLastUpdated``.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if show_last_updated is not None:
            self._values["show_last_updated"] = show_last_updated
        if show_packages is not None:
            self._values["show_packages"] = show_packages

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the section (displayed as a header).

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def show_last_updated(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Show the N most recently updated packages in this section.

        Cannot be used with ``showPackages``.

        :stability: experimental
        '''
        result = self._values.get("show_last_updated")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def show_packages(self) -> typing.Optional[typing.List[FeaturedPackagesDetail]]:
        '''(experimental) Show an explicit list of packages.

        Cannot be used with ``showLastUpdated``.

        :stability: experimental
        '''
        result = self._values.get("show_packages")
        return typing.cast(typing.Optional[typing.List[FeaturedPackagesDetail]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FeaturedPackagesSection(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FilterType(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="construct-hub.FilterType",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="checkbox") # type: ignore[misc]
    @builtins.classmethod
    def checkbox(cls) -> "FilterType":
        '''
        :stability: experimental
        '''
        return typing.cast("FilterType", jsii.sinvoke(cls, "checkbox", []))

    @jsii.member(jsii_name="radio") # type: ignore[misc]
    @builtins.classmethod
    def radio(cls) -> "FilterType":
        '''
        :stability: experimental
        '''
        return typing.cast("FilterType", jsii.sinvoke(cls, "radio", []))

    @jsii.member(jsii_name="bind") # type: ignore[misc]
    @abc.abstractmethod
    def bind(self) -> "FilterTypeValue":
        '''
        :stability: experimental
        '''
        ...


class _FilterTypeProxy(FilterType):
    @jsii.member(jsii_name="bind")
    def bind(self) -> "FilterTypeValue":
        '''
        :stability: experimental
        '''
        return typing.cast("FilterTypeValue", jsii.invoke(self, "bind", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, FilterType).__jsii_proxy_class__ = lambda : _FilterTypeProxy


@jsii.data_type(
    jsii_type="construct-hub.FilterTypeValue",
    jsii_struct_bases=[],
    name_mapping={"type": "type"},
)
class FilterTypeValue:
    def __init__(self, *, type: builtins.str) -> None:
        '''
        :param type: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }

    @builtins.property
    def type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FilterTypeValue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.Highlight",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "color": "color", "icon": "icon"},
)
class Highlight:
    def __init__(
        self,
        *,
        label: builtins.str,
        color: typing.Optional[builtins.str] = None,
        icon: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param label: (experimental) The label for the tag being applied.
        :param color: (experimental) The hex value string for the color of the tag when displayed.
        :param icon: (experimental) Icon displayed next to highlight on package card.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
        }
        if color is not None:
            self._values["color"] = color
        if icon is not None:
            self._values["icon"] = icon

    @builtins.property
    def label(self) -> builtins.str:
        '''(experimental) The label for the tag being applied.

        :stability: experimental
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def color(self) -> typing.Optional[builtins.str]:
        '''(experimental) The hex value string for the color of the tag when displayed.

        :stability: experimental
        '''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def icon(self) -> typing.Optional[builtins.str]:
        '''(experimental) Icon displayed next to highlight on package card.

        :stability: experimental
        '''
        result = self._values.get("icon")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Highlight(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="construct-hub.IDenyList")
class IDenyList(typing_extensions.Protocol):
    '''(experimental) DenyList features exposed to extension points.

    :stability: experimental
    '''

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, handler: aws_cdk.aws_lambda.Function) -> None:
        '''(experimental) Grants an AWS Lambda function permissions to read the deny list, and adds the relevant environment variables expected by the ``DenyListClient``.

        :param handler: -

        :stability: experimental
        '''
        ...


class _IDenyListProxy:
    '''(experimental) DenyList features exposed to extension points.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "construct-hub.IDenyList"

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, handler: aws_cdk.aws_lambda.Function) -> None:
        '''(experimental) Grants an AWS Lambda function permissions to read the deny list, and adds the relevant environment variables expected by the ``DenyListClient``.

        :param handler: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "grantRead", [handler]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDenyList).__jsii_proxy_class__ = lambda : _IDenyListProxy


@jsii.interface(jsii_type="construct-hub.ILicenseList")
class ILicenseList(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, handler: aws_cdk.aws_lambda.Function) -> None:
        '''(experimental) Grants an AWS Lambda function permissions to read the license allow list, and adds the relevant environment variables expected by the ``LicenseListClient``.

        :param handler: -

        :stability: experimental
        '''
        ...


class _ILicenseListProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "construct-hub.ILicenseList"

    @jsii.member(jsii_name="grantRead")
    def grant_read(self, handler: aws_cdk.aws_lambda.Function) -> None:
        '''(experimental) Grants an AWS Lambda function permissions to read the license allow list, and adds the relevant environment variables expected by the ``LicenseListClient``.

        :param handler: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "grantRead", [handler]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILicenseList).__jsii_proxy_class__ = lambda : _ILicenseListProxy


@jsii.interface(jsii_type="construct-hub.IMonitoring")
class IMonitoring(typing_extensions.Protocol):
    '''(experimental) ConstructHub monitoring features exposed to extension points.

    :stability: experimental
    '''

    @jsii.member(jsii_name="addHighSeverityAlarm")
    def add_high_severity_alarm(
        self,
        title: builtins.str,
        alarm: aws_cdk.aws_cloudwatch.Alarm,
    ) -> None:
        '''(experimental) Adds a high-severity alarm.

        If this alarm goes off, the action specified in
        ``highSeverityAlarmActionArn`` is triggered.

        :param title: a user-friendly title for the alarm (will be rendered on the high-severity CloudWatch dashboard).
        :param alarm: the alarm to be added to the high-severity dashboard.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addLowSeverityAlarm")
    def add_low_severity_alarm(
        self,
        title: builtins.str,
        alarm: aws_cdk.aws_cloudwatch.Alarm,
    ) -> None:
        '''(experimental) Adds a low-severity alarm.

        If this alarm goes off, the action specified in
        ``normalAlarmAction`` is triggered.

        :param title: a user-friendly title for the alarm (not currently used).
        :param alarm: the alarm to be added.

        :stability: experimental
        '''
        ...


class _IMonitoringProxy:
    '''(experimental) ConstructHub monitoring features exposed to extension points.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "construct-hub.IMonitoring"

    @jsii.member(jsii_name="addHighSeverityAlarm")
    def add_high_severity_alarm(
        self,
        title: builtins.str,
        alarm: aws_cdk.aws_cloudwatch.Alarm,
    ) -> None:
        '''(experimental) Adds a high-severity alarm.

        If this alarm goes off, the action specified in
        ``highSeverityAlarmActionArn`` is triggered.

        :param title: a user-friendly title for the alarm (will be rendered on the high-severity CloudWatch dashboard).
        :param alarm: the alarm to be added to the high-severity dashboard.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addHighSeverityAlarm", [title, alarm]))

    @jsii.member(jsii_name="addLowSeverityAlarm")
    def add_low_severity_alarm(
        self,
        title: builtins.str,
        alarm: aws_cdk.aws_cloudwatch.Alarm,
    ) -> None:
        '''(experimental) Adds a low-severity alarm.

        If this alarm goes off, the action specified in
        ``normalAlarmAction`` is triggered.

        :param title: a user-friendly title for the alarm (not currently used).
        :param alarm: the alarm to be added.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addLowSeverityAlarm", [title, alarm]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMonitoring).__jsii_proxy_class__ = lambda : _IMonitoringProxy


@jsii.interface(jsii_type="construct-hub.IPackageSource")
class IPackageSource(typing_extensions.Protocol):
    '''(experimental) A package source for ConstructHub.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: aws_cdk.core.Construct,
        *,
        base_url: builtins.str,
        ingestion: aws_cdk.aws_iam.IGrantable,
        license_list: ILicenseList,
        monitoring: IMonitoring,
        queue: aws_cdk.aws_sqs.IQueue,
        deny_list: typing.Optional[IDenyList] = None,
        repository: typing.Optional["IRepository"] = None,
    ) -> "PackageSourceBindResult":
        '''(experimental) Binds the package source to a scope and target queue.

        :param scope: the construct scope in which the binding happens.
        :param base_url: (experimental) The base URL of the bound ConstructHub instance.
        :param ingestion: (experimental) The ``IGrantable`` that will process downstream messages from the bound package source. It needs to be granted permissions to read package data from the URLs sent to the ``queue``.
        :param license_list: (experimental) The license list applied by the bound Construct Hub instance. This can be used to filter down the package only to those which will pass the license filter.
        :param monitoring: (experimental) The monitoring instance to use for registering alarms, etc.
        :param queue: (experimental) The SQS queue to which messages should be sent. Sent objects should match the package discovery schema.
        :param deny_list: (experimental) The configured ``DenyList`` for the bound Construct Hub instance, if any.
        :param repository: (experimental) The CodeArtifact repository that is internally used by ConstructHub. This may be undefined if no CodeArtifact repository is internally used.

        :return:

        a dependable resource that can be used to create a CloudFormation
        dependency on the bound source.

        :stability: experimental
        '''
        ...


class _IPackageSourceProxy:
    '''(experimental) A package source for ConstructHub.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "construct-hub.IPackageSource"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: aws_cdk.core.Construct,
        *,
        base_url: builtins.str,
        ingestion: aws_cdk.aws_iam.IGrantable,
        license_list: ILicenseList,
        monitoring: IMonitoring,
        queue: aws_cdk.aws_sqs.IQueue,
        deny_list: typing.Optional[IDenyList] = None,
        repository: typing.Optional["IRepository"] = None,
    ) -> "PackageSourceBindResult":
        '''(experimental) Binds the package source to a scope and target queue.

        :param scope: the construct scope in which the binding happens.
        :param base_url: (experimental) The base URL of the bound ConstructHub instance.
        :param ingestion: (experimental) The ``IGrantable`` that will process downstream messages from the bound package source. It needs to be granted permissions to read package data from the URLs sent to the ``queue``.
        :param license_list: (experimental) The license list applied by the bound Construct Hub instance. This can be used to filter down the package only to those which will pass the license filter.
        :param monitoring: (experimental) The monitoring instance to use for registering alarms, etc.
        :param queue: (experimental) The SQS queue to which messages should be sent. Sent objects should match the package discovery schema.
        :param deny_list: (experimental) The configured ``DenyList`` for the bound Construct Hub instance, if any.
        :param repository: (experimental) The CodeArtifact repository that is internally used by ConstructHub. This may be undefined if no CodeArtifact repository is internally used.

        :return:

        a dependable resource that can be used to create a CloudFormation
        dependency on the bound source.

        :stability: experimental
        '''
        opts = PackageSourceBindOptions(
            base_url=base_url,
            ingestion=ingestion,
            license_list=license_list,
            monitoring=monitoring,
            queue=queue,
            deny_list=deny_list,
            repository=repository,
        )

        return typing.cast("PackageSourceBindResult", jsii.invoke(self, "bind", [scope, opts]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPackageSource).__jsii_proxy_class__ = lambda : _IPackageSourceProxy


@jsii.interface(jsii_type="construct-hub.IRepository")
class IRepository(typing_extensions.Protocol):
    '''(experimental) The CodeArtifact repository API exposed to extensions.

    :stability: experimental
    '''

    @jsii.member(jsii_name="addExternalConnection")
    def add_external_connection(self, id: builtins.str) -> None:
        '''(experimental) Adds an external connection to this repository.

        :param id: the id of the external connection (i.e: ``public:npmjs``).

        :stability: experimental
        '''
        ...


class _IRepositoryProxy:
    '''(experimental) The CodeArtifact repository API exposed to extensions.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "construct-hub.IRepository"

    @jsii.member(jsii_name="addExternalConnection")
    def add_external_connection(self, id: builtins.str) -> None:
        '''(experimental) Adds an external connection to this repository.

        :param id: the id of the external connection (i.e: ``public:npmjs``).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addExternalConnection", [id]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRepository).__jsii_proxy_class__ = lambda : _IRepositoryProxy


@jsii.enum(jsii_type="construct-hub.Isolation")
class Isolation(enum.Enum):
    '''(experimental) How possibly risky operations (such as doc-generation, which requires installing the indexed packages in order to trans-literate sample code) are isolated to mitigate possible arbitrary code execution vulnerabilities in and around ``npm install`` or the transliterator's use of the TypeScript compiler.

    :stability: experimental
    '''

    UNLIMITED_INTERNET_ACCESS = "UNLIMITED_INTERNET_ACCESS"
    '''(experimental) No isolation is done whatsoever. The doc-generation process still is provisioned with least-privilege permissions, but retains complete access to internet.

    While this maximizes the chances of successfully installing packages (and
    hence successfully generating documentation for those), it is also the
    least secure mode of operation.

    We advise you only consider using this isolation mode if you are hosting a
    ConstructHub instance that only indexes trusted packages (including
    transitive dependencies).

    :stability: experimental
    '''
    LIMITED_INTERNET_ACCESS = "LIMITED_INTERNET_ACCESS"
    '''(experimental) The same protections as ``UNLIMITED_INTERNET_ACCESS``, except outbound internet connections are limited to IP address ranges corresponding to hosting endpoints for npmjs.com.

    :stability: experimental
    '''
    NO_INTERNET_ACCESS = "NO_INTERNET_ACCESS"
    '''(experimental) The same protections as ``LIMITED_INTERNET_ACCESS``, except all remaining internet access is removed.

    All traffic to AWS service endpoints is routed
    through VPC Endpoints, as the compute nodes are jailed in a completely
    isolated VPC.

    This is the most secure (and recommended) mode of operation for
    ConstructHub instances.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="construct-hub.Keyword",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "color": "color"},
)
class Keyword:
    def __init__(
        self,
        *,
        label: builtins.str,
        color: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param label: (experimental) The label for the tag being applied.
        :param color: (experimental) The hex value string for the color of the tag when displayed.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
        }
        if color is not None:
            self._values["color"] = color

    @builtins.property
    def label(self) -> builtins.str:
        '''(experimental) The label for the tag being applied.

        :stability: experimental
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def color(self) -> typing.Optional[builtins.str]:
        '''(experimental) The hex value string for the color of the tag when displayed.

        :stability: experimental
        '''
        result = self._values.get("color")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Keyword(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.LinkedResource",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "url": "url", "primary": "primary"},
)
class LinkedResource:
    def __init__(
        self,
        *,
        name: builtins.str,
        url: builtins.str,
        primary: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param name: (experimental) The name of the linked resource.
        :param url: (experimental) The URL where the linked resource can be found.
        :param primary: (experimental) Whether this is the primary resource of the bound package source. It is not necessary that there is one, and there could be multiple primary resources. The buttons for those will be rendered with a different style on the dashboard.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "url": url,
        }
        if primary is not None:
            self._values["primary"] = primary

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the linked resource.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''(experimental) The URL where the linked resource can be found.

        :stability: experimental
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def primary(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether this is the primary resource of the bound package source.

        It is not
        necessary that there is one, and there could be multiple primary resources.
        The buttons for those will be rendered with a different style on the
        dashboard.

        :stability: experimental
        '''
        result = self._values.get("primary")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LinkedResource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.PackageLinkConfig",
    jsii_struct_bases=[],
    name_mapping={
        "config_key": "configKey",
        "link_label": "linkLabel",
        "allowed_domains": "allowedDomains",
        "link_text": "linkText",
    },
)
class PackageLinkConfig:
    def __init__(
        self,
        *,
        config_key: builtins.str,
        link_label: builtins.str,
        allowed_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        link_text: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config_key: (experimental) The location of the value inside the constructHub.packageLinks key of a module's package.json.
        :param link_label: (experimental) The name of the link, appears before the ":" on the website.
        :param allowed_domains: (experimental) allowList of domains for this link. Default: all domains allowed
        :param link_text: (experimental) optional text to display as the hyperlink text. Default: the url of the link

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "config_key": config_key,
            "link_label": link_label,
        }
        if allowed_domains is not None:
            self._values["allowed_domains"] = allowed_domains
        if link_text is not None:
            self._values["link_text"] = link_text

    @builtins.property
    def config_key(self) -> builtins.str:
        '''(experimental) The location of the value inside the constructHub.packageLinks key of a module's package.json.

        :stability: experimental
        '''
        result = self._values.get("config_key")
        assert result is not None, "Required property 'config_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def link_label(self) -> builtins.str:
        '''(experimental) The name of the link, appears before the ":" on the website.

        :stability: experimental
        '''
        result = self._values.get("link_label")
        assert result is not None, "Required property 'link_label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) allowList of domains for this link.

        :default: all domains allowed

        :stability: experimental
        '''
        result = self._values.get("allowed_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def link_text(self) -> typing.Optional[builtins.str]:
        '''(experimental) optional text to display as the hyperlink text.

        :default: the url of the link

        :stability: experimental
        '''
        result = self._values.get("link_text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PackageLinkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.PackageSourceBindOptions",
    jsii_struct_bases=[],
    name_mapping={
        "base_url": "baseUrl",
        "ingestion": "ingestion",
        "license_list": "licenseList",
        "monitoring": "monitoring",
        "queue": "queue",
        "deny_list": "denyList",
        "repository": "repository",
    },
)
class PackageSourceBindOptions:
    def __init__(
        self,
        *,
        base_url: builtins.str,
        ingestion: aws_cdk.aws_iam.IGrantable,
        license_list: ILicenseList,
        monitoring: IMonitoring,
        queue: aws_cdk.aws_sqs.IQueue,
        deny_list: typing.Optional[IDenyList] = None,
        repository: typing.Optional[IRepository] = None,
    ) -> None:
        '''(experimental) Options for binding a package source.

        :param base_url: (experimental) The base URL of the bound ConstructHub instance.
        :param ingestion: (experimental) The ``IGrantable`` that will process downstream messages from the bound package source. It needs to be granted permissions to read package data from the URLs sent to the ``queue``.
        :param license_list: (experimental) The license list applied by the bound Construct Hub instance. This can be used to filter down the package only to those which will pass the license filter.
        :param monitoring: (experimental) The monitoring instance to use for registering alarms, etc.
        :param queue: (experimental) The SQS queue to which messages should be sent. Sent objects should match the package discovery schema.
        :param deny_list: (experimental) The configured ``DenyList`` for the bound Construct Hub instance, if any.
        :param repository: (experimental) The CodeArtifact repository that is internally used by ConstructHub. This may be undefined if no CodeArtifact repository is internally used.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "base_url": base_url,
            "ingestion": ingestion,
            "license_list": license_list,
            "monitoring": monitoring,
            "queue": queue,
        }
        if deny_list is not None:
            self._values["deny_list"] = deny_list
        if repository is not None:
            self._values["repository"] = repository

    @builtins.property
    def base_url(self) -> builtins.str:
        '''(experimental) The base URL of the bound ConstructHub instance.

        :stability: experimental
        '''
        result = self._values.get("base_url")
        assert result is not None, "Required property 'base_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ingestion(self) -> aws_cdk.aws_iam.IGrantable:
        '''(experimental) The ``IGrantable`` that will process downstream messages from the bound package source.

        It needs to be granted permissions to read package data
        from the URLs sent to the ``queue``.

        :stability: experimental
        '''
        result = self._values.get("ingestion")
        assert result is not None, "Required property 'ingestion' is missing"
        return typing.cast(aws_cdk.aws_iam.IGrantable, result)

    @builtins.property
    def license_list(self) -> ILicenseList:
        '''(experimental) The license list applied by the bound Construct Hub instance.

        This can be
        used to filter down the package only to those which will pass the license
        filter.

        :stability: experimental
        '''
        result = self._values.get("license_list")
        assert result is not None, "Required property 'license_list' is missing"
        return typing.cast(ILicenseList, result)

    @builtins.property
    def monitoring(self) -> IMonitoring:
        '''(experimental) The monitoring instance to use for registering alarms, etc.

        :stability: experimental
        '''
        result = self._values.get("monitoring")
        assert result is not None, "Required property 'monitoring' is missing"
        return typing.cast(IMonitoring, result)

    @builtins.property
    def queue(self) -> aws_cdk.aws_sqs.IQueue:
        '''(experimental) The SQS queue to which messages should be sent.

        Sent objects should match
        the package discovery schema.

        :stability: experimental
        '''
        result = self._values.get("queue")
        assert result is not None, "Required property 'queue' is missing"
        return typing.cast(aws_cdk.aws_sqs.IQueue, result)

    @builtins.property
    def deny_list(self) -> typing.Optional[IDenyList]:
        '''(experimental) The configured ``DenyList`` for the bound Construct Hub instance, if any.

        :stability: experimental
        '''
        result = self._values.get("deny_list")
        return typing.cast(typing.Optional[IDenyList], result)

    @builtins.property
    def repository(self) -> typing.Optional[IRepository]:
        '''(experimental) The CodeArtifact repository that is internally used by ConstructHub.

        This
        may be undefined if no CodeArtifact repository is internally used.

        :stability: experimental
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[IRepository], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PackageSourceBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.PackageSourceBindResult",
    jsii_struct_bases=[],
    name_mapping={
        "dashboard_widgets": "dashboardWidgets",
        "name": "name",
        "links": "links",
    },
)
class PackageSourceBindResult:
    def __init__(
        self,
        *,
        dashboard_widgets: typing.Sequence[typing.Sequence[aws_cdk.aws_cloudwatch.IWidget]],
        name: builtins.str,
        links: typing.Optional[typing.Sequence[LinkedResource]] = None,
    ) -> None:
        '''(experimental) The result of binding a package source.

        :param dashboard_widgets: (experimental) Widgets to add to the operator dashbaord for monitoring the health of the bound package source. It is not necessary for this list of widgets to include a title section (this will be added automatically). One array represents a row of widgets on the dashboard.
        :param name: (experimental) The name of the bound package source. It will be used to render operator dashboards (so it should be a meaningful identification of the source).
        :param links: (experimental) An optional list of linked resources to be displayed on the monitoring dashboard.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dashboard_widgets": dashboard_widgets,
            "name": name,
        }
        if links is not None:
            self._values["links"] = links

    @builtins.property
    def dashboard_widgets(
        self,
    ) -> typing.List[typing.List[aws_cdk.aws_cloudwatch.IWidget]]:
        '''(experimental) Widgets to add to the operator dashbaord for monitoring the health of the bound package source.

        It is not necessary for this list of widgets to
        include a title section (this will be added automatically). One array
        represents a row of widgets on the dashboard.

        :stability: experimental
        '''
        result = self._values.get("dashboard_widgets")
        assert result is not None, "Required property 'dashboard_widgets' is missing"
        return typing.cast(typing.List[typing.List[aws_cdk.aws_cloudwatch.IWidget]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the bound package source.

        It will be used to render operator
        dashboards (so it should be a meaningful identification of the source).

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def links(self) -> typing.Optional[typing.List[LinkedResource]]:
        '''(experimental) An optional list of linked resources to be displayed on the monitoring dashboard.

        :stability: experimental
        '''
        result = self._values.get("links")
        return typing.cast(typing.Optional[typing.List[LinkedResource]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PackageSourceBindResult(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.PackageTagBase",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "highlight": "highlight",
        "keyword": "keyword",
        "search_filter": "searchFilter",
    },
)
class PackageTagBase:
    def __init__(
        self,
        *,
        id: builtins.str,
        highlight: typing.Optional[Highlight] = None,
        keyword: typing.Optional[Keyword] = None,
        search_filter: typing.Optional["SearchFilter"] = None,
    ) -> None:
        '''
        :param id: (experimental) Identifier for tag, used for search. Must be unique amongst tags.
        :param highlight: (experimental) Configuration for higlighting tag on package card. Default: don't highlight tag
        :param keyword: (experimental) Configuration for showing tag as keyword. Default: don't show tag in keyword list
        :param search_filter: (experimental) Configuration for showing tag as search filter. Default: don't show tag in search filters

        :stability: experimental
        '''
        if isinstance(highlight, dict):
            highlight = Highlight(**highlight)
        if isinstance(keyword, dict):
            keyword = Keyword(**keyword)
        if isinstance(search_filter, dict):
            search_filter = SearchFilter(**search_filter)
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }
        if highlight is not None:
            self._values["highlight"] = highlight
        if keyword is not None:
            self._values["keyword"] = keyword
        if search_filter is not None:
            self._values["search_filter"] = search_filter

    @builtins.property
    def id(self) -> builtins.str:
        '''(experimental) Identifier for tag, used for search.

        Must be unique amongst tags.

        :stability: experimental
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def highlight(self) -> typing.Optional[Highlight]:
        '''(experimental) Configuration for higlighting tag on package card.

        :default: don't highlight tag

        :stability: experimental
        '''
        result = self._values.get("highlight")
        return typing.cast(typing.Optional[Highlight], result)

    @builtins.property
    def keyword(self) -> typing.Optional[Keyword]:
        '''(experimental) Configuration for showing tag as keyword.

        :default: don't show tag in keyword list

        :stability: experimental
        '''
        result = self._values.get("keyword")
        return typing.cast(typing.Optional[Keyword], result)

    @builtins.property
    def search_filter(self) -> typing.Optional["SearchFilter"]:
        '''(experimental) Configuration for showing tag as search filter.

        :default: don't show tag in search filters

        :stability: experimental
        '''
        result = self._values.get("search_filter")
        return typing.cast(typing.Optional["SearchFilter"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PackageTagBase(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.PackageTagConfig",
    jsii_struct_bases=[PackageTagBase],
    name_mapping={
        "id": "id",
        "highlight": "highlight",
        "keyword": "keyword",
        "search_filter": "searchFilter",
        "condition": "condition",
    },
)
class PackageTagConfig(PackageTagBase):
    def __init__(
        self,
        *,
        id: builtins.str,
        highlight: typing.Optional[Highlight] = None,
        keyword: typing.Optional[Keyword] = None,
        search_filter: typing.Optional["SearchFilter"] = None,
        condition: "TagConditionConfig",
    ) -> None:
        '''(experimental) Serialized tag declaration to be passed to lambdas via environment variables.

        :param id: (experimental) Identifier for tag, used for search. Must be unique amongst tags.
        :param highlight: (experimental) Configuration for higlighting tag on package card. Default: don't highlight tag
        :param keyword: (experimental) Configuration for showing tag as keyword. Default: don't show tag in keyword list
        :param search_filter: (experimental) Configuration for showing tag as search filter. Default: don't show tag in search filters
        :param condition: 

        :stability: experimental
        '''
        if isinstance(highlight, dict):
            highlight = Highlight(**highlight)
        if isinstance(keyword, dict):
            keyword = Keyword(**keyword)
        if isinstance(search_filter, dict):
            search_filter = SearchFilter(**search_filter)
        if isinstance(condition, dict):
            condition = TagConditionConfig(**condition)
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
            "condition": condition,
        }
        if highlight is not None:
            self._values["highlight"] = highlight
        if keyword is not None:
            self._values["keyword"] = keyword
        if search_filter is not None:
            self._values["search_filter"] = search_filter

    @builtins.property
    def id(self) -> builtins.str:
        '''(experimental) Identifier for tag, used for search.

        Must be unique amongst tags.

        :stability: experimental
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def highlight(self) -> typing.Optional[Highlight]:
        '''(experimental) Configuration for higlighting tag on package card.

        :default: don't highlight tag

        :stability: experimental
        '''
        result = self._values.get("highlight")
        return typing.cast(typing.Optional[Highlight], result)

    @builtins.property
    def keyword(self) -> typing.Optional[Keyword]:
        '''(experimental) Configuration for showing tag as keyword.

        :default: don't show tag in keyword list

        :stability: experimental
        '''
        result = self._values.get("keyword")
        return typing.cast(typing.Optional[Keyword], result)

    @builtins.property
    def search_filter(self) -> typing.Optional["SearchFilter"]:
        '''(experimental) Configuration for showing tag as search filter.

        :default: don't show tag in search filters

        :stability: experimental
        '''
        result = self._values.get("search_filter")
        return typing.cast(typing.Optional["SearchFilter"], result)

    @builtins.property
    def condition(self) -> "TagConditionConfig":
        '''
        :stability: experimental
        '''
        result = self._values.get("condition")
        assert result is not None, "Required property 'condition' is missing"
        return typing.cast("TagConditionConfig", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PackageTagConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PackageTagGroup(
    metaclass=jsii.JSIIMeta,
    jsii_type="construct-hub.PackageTagGroup",
):
    '''(experimental) Defines a custom package tag group.

    :stability: experimental
    '''

    def __init__(
        self,
        id: builtins.str,
        *,
        filter_type: typing.Optional[FilterType] = None,
        label: typing.Optional[builtins.str] = None,
        tooltip: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: -
        :param filter_type: (experimental) Allows to specify the group filter type. Defaults to checkbox if not specified
        :param label: (experimental) Group label to display. Falls back to id if not provided
        :param tooltip: (experimental) Optional message to show within a tooltip next to the filter label.

        :stability: experimental
        '''
        props = PackageTagGroupProps(
            filter_type=filter_type, label=label, tooltip=tooltip
        )

        jsii.create(self.__class__, self, [id, props])

    @jsii.member(jsii_name="bind")
    def bind(self) -> "PackageTagGroupConfig":
        '''
        :stability: experimental
        '''
        return typing.cast("PackageTagGroupConfig", jsii.invoke(self, "bind", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterType")
    def filter_type(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "filterType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "label"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tooltip")
    def tooltip(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tooltip"))


@jsii.data_type(
    jsii_type="construct-hub.PackageTagGroupConfig",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "filter_type": "filterType",
        "label": "label",
        "tooltip": "tooltip",
    },
)
class PackageTagGroupConfig:
    def __init__(
        self,
        *,
        id: builtins.str,
        filter_type: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        tooltip: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: 
        :param filter_type: 
        :param label: 
        :param tooltip: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }
        if filter_type is not None:
            self._values["filter_type"] = filter_type
        if label is not None:
            self._values["label"] = label
        if tooltip is not None:
            self._values["tooltip"] = tooltip

    @builtins.property
    def id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter_type(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("filter_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tooltip(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("tooltip")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PackageTagGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.PackageTagGroupProps",
    jsii_struct_bases=[],
    name_mapping={"filter_type": "filterType", "label": "label", "tooltip": "tooltip"},
)
class PackageTagGroupProps:
    def __init__(
        self,
        *,
        filter_type: typing.Optional[FilterType] = None,
        label: typing.Optional[builtins.str] = None,
        tooltip: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param filter_type: (experimental) Allows to specify the group filter type. Defaults to checkbox if not specified
        :param label: (experimental) Group label to display. Falls back to id if not provided
        :param tooltip: (experimental) Optional message to show within a tooltip next to the filter label.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if filter_type is not None:
            self._values["filter_type"] = filter_type
        if label is not None:
            self._values["label"] = label
        if tooltip is not None:
            self._values["tooltip"] = tooltip

    @builtins.property
    def filter_type(self) -> typing.Optional[FilterType]:
        '''(experimental) Allows to specify the group filter type.

        Defaults to checkbox if not specified

        :stability: experimental
        '''
        result = self._values.get("filter_type")
        return typing.cast(typing.Optional[FilterType], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''(experimental) Group label to display.

        Falls back to id if not provided

        :stability: experimental
        '''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tooltip(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional message to show within a tooltip next to the filter label.

        :stability: experimental
        '''
        result = self._values.get("tooltip")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PackageTagGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PreloadFile(metaclass=jsii.JSIIMeta, jsii_type="construct-hub.PreloadFile"):
    '''(experimental) Represents a javascript file to load before the webapp.

    This can allow operators to add their own client monitors or analytics if they wish

    :stability: experimental
    '''

    def __init__(self, data: builtins.str) -> None:
        '''
        :param data: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [data])

    @jsii.member(jsii_name="fromCode") # type: ignore[misc]
    @builtins.classmethod
    def from_code(cls, code: builtins.str) -> "PreloadFile":
        '''(experimental) Creates a PreloadFile instance directly from source code.

        :param code: -

        :stability: experimental
        '''
        return typing.cast("PreloadFile", jsii.sinvoke(cls, "fromCode", [code]))

    @jsii.member(jsii_name="fromFile") # type: ignore[misc]
    @builtins.classmethod
    def from_file(cls, path: builtins.str) -> "PreloadFile":
        '''(experimental) Creates a PreloadFile instance from a filepath to load.

        :param path: -

        :stability: experimental
        '''
        return typing.cast("PreloadFile", jsii.sinvoke(cls, "fromFile", [path]))

    @jsii.member(jsii_name="bind")
    def bind(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "bind", []))


class S3StorageFactory(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="construct-hub.S3StorageFactory",
):
    '''(experimental) Create s3 storage resources.

    :stability: experimental
    '''

    @jsii.member(jsii_name="getOrCreate") # type: ignore[misc]
    @builtins.classmethod
    def get_or_create(
        cls,
        scope: aws_cdk.core.Construct,
        *,
        failover: typing.Optional[builtins.bool] = None,
    ) -> "S3StorageFactory":
        '''(experimental) Retrieve or create the storage factory for the current scope.

        This is stack singleton.

        :param scope: -
        :param failover: (experimental) When enabled, the factory will return the failover buckets instead of the primary. Default: false

        :stability: experimental
        '''
        props = S3StorageFactoryProps(failover=failover)

        return typing.cast("S3StorageFactory", jsii.sinvoke(cls, "getOrCreate", [scope, props]))

    @jsii.member(jsii_name="newBucket")
    def new_bucket(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        access_control: typing.Optional[aws_cdk.aws_s3.BucketAccessControl] = None,
        auto_delete_objects: typing.Optional[builtins.bool] = None,
        block_public_access: typing.Optional[aws_cdk.aws_s3.BlockPublicAccess] = None,
        bucket_key_enabled: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors: typing.Optional[typing.Sequence[aws_cdk.aws_s3.CorsRule]] = None,
        encryption: typing.Optional[aws_cdk.aws_s3.BucketEncryption] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        enforce_ssl: typing.Optional[builtins.bool] = None,
        inventories: typing.Optional[typing.Sequence[aws_cdk.aws_s3.Inventory]] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[aws_cdk.aws_s3.LifecycleRule]] = None,
        metrics: typing.Optional[typing.Sequence[aws_cdk.aws_s3.BucketMetrics]] = None,
        object_ownership: typing.Optional[aws_cdk.aws_s3.ObjectOwnership] = None,
        public_read_access: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        server_access_logs_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        server_access_logs_prefix: typing.Optional[builtins.str] = None,
        versioned: typing.Optional[builtins.bool] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        website_redirect: typing.Optional[aws_cdk.aws_s3.RedirectTarget] = None,
        website_routing_rules: typing.Optional[typing.Sequence[aws_cdk.aws_s3.RoutingRule]] = None,
    ) -> aws_cdk.aws_s3.Bucket:
        '''(experimental) Create a new bucket in a storage config aware manner.

        :param scope: -
        :param id: -
        :param access_control: Specifies a canned ACL that grants predefined permissions to the bucket. Default: BucketAccessControl.PRIVATE
        :param auto_delete_objects: Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted. Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``. **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``, switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to all objects in the bucket being deleted. Be sure to update your bucket resources by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``. Default: false
        :param block_public_access: The block public access configuration of this bucket. Default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access
        :param bucket_key_enabled: Specifies whether Amazon S3 should use an S3 Bucket Key with server-side encryption using KMS (SSE-KMS) for new objects in the bucket. Only relevant, when Encryption is set to {@link BucketEncryption.KMS} Default: - false
        :param bucket_name: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
        :param cors: The CORS configuration of this bucket. Default: - No CORS configuration.
        :param encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``Kms`` if ``encryptionKey`` is specified, or ``Unencrypted`` otherwise.
        :param encryption_key: External KMS key to use for bucket encryption. The 'encryption' property must be either not specified or set to "Kms". An error will be emitted if encryption is set to "Unencrypted" or "Managed". Default: - If encryption is set to "Kms" and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param enforce_ssl: Enforces SSL for requests. S3.5 of the AWS Foundational Security Best Practices Regarding S3. Default: false
        :param inventories: The inventory configuration of the bucket. Default: - No inventory configuration
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
        :param metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
        :param object_ownership: The objectOwnership of the bucket. Default: - No ObjectOwnership configuration, uploading account will own the object.
        :param public_read_access: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()`` Default: false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param server_access_logs_bucket: Destination bucket for the server access logs. Default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        :param server_access_logs_prefix: Optional log file prefix to use for the bucket's access logs. If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix. Default: - No log file prefix
        :param versioned: Whether this bucket should have versioning turned on or not. Default: false
        :param website_error_document: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
        :param website_index_document: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.
        :param website_redirect: Specifies the redirect behavior of all requests to a website endpoint of a bucket. If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules". Default: - No redirection.
        :param website_routing_rules: Rules that define when a redirect is applied and the redirect behavior. Default: - No redirection rules.

        :return: s3.Bucket

        :stability: experimental
        '''
        props = aws_cdk.aws_s3.BucketProps(
            access_control=access_control,
            auto_delete_objects=auto_delete_objects,
            block_public_access=block_public_access,
            bucket_key_enabled=bucket_key_enabled,
            bucket_name=bucket_name,
            cors=cors,
            encryption=encryption,
            encryption_key=encryption_key,
            enforce_ssl=enforce_ssl,
            inventories=inventories,
            lifecycle_rules=lifecycle_rules,
            metrics=metrics,
            object_ownership=object_ownership,
            public_read_access=public_read_access,
            removal_policy=removal_policy,
            server_access_logs_bucket=server_access_logs_bucket,
            server_access_logs_prefix=server_access_logs_prefix,
            versioned=versioned,
            website_error_document=website_error_document,
            website_index_document=website_index_document,
            website_redirect=website_redirect,
            website_routing_rules=website_routing_rules,
        )

        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.invoke(self, "newBucket", [scope, id, props]))


@jsii.data_type(
    jsii_type="construct-hub.S3StorageFactoryProps",
    jsii_struct_bases=[],
    name_mapping={"failover": "failover"},
)
class S3StorageFactoryProps:
    def __init__(self, *, failover: typing.Optional[builtins.bool] = None) -> None:
        '''(experimental) Properties for ``S3StorageFactory``.

        :param failover: (experimental) When enabled, the factory will return the failover buckets instead of the primary. Default: false

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if failover is not None:
            self._values["failover"] = failover

    @builtins.property
    def failover(self) -> typing.Optional[builtins.bool]:
        '''(experimental) When enabled, the factory will return the failover buckets instead of the primary.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("failover")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3StorageFactoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="construct-hub.SearchFilter",
    jsii_struct_bases=[],
    name_mapping={"display": "display", "group": "group", "group_by": "groupBy"},
)
class SearchFilter:
    def __init__(
        self,
        *,
        display: builtins.str,
        group: typing.Optional[PackageTagGroup] = None,
        group_by: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param display: (experimental) Display name for filter.
        :param group: (experimental) PackageTagGroup to include filter in.
        :param group_by: (deprecated) Name of group to include filter in.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "display": display,
        }
        if group is not None:
            self._values["group"] = group
        if group_by is not None:
            self._values["group_by"] = group_by

    @builtins.property
    def display(self) -> builtins.str:
        '''(experimental) Display name for filter.

        :stability: experimental
        '''
        result = self._values.get("display")
        assert result is not None, "Required property 'display' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group(self) -> typing.Optional[PackageTagGroup]:
        '''(experimental) PackageTagGroup to include filter in.

        :stability: experimental
        '''
        result = self._values.get("group")
        return typing.cast(typing.Optional[PackageTagGroup], result)

    @builtins.property
    def group_by(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Name of group to include filter in.

        :deprecated: use ``group`` instead

        :stability: deprecated
        '''
        result = self._values.get("group_by")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SearchFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SpdxLicense(metaclass=jsii.JSIIMeta, jsii_type="construct-hub.SpdxLicense"):
    '''(experimental) Valid SPDX License identifiers.

    :stability: experimental
    '''

    @jsii.member(jsii_name="all") # type: ignore[misc]
    @builtins.classmethod
    def all(cls) -> typing.List["SpdxLicense"]:
        '''(experimental) All valid SPDX Licenses.

        :stability: experimental
        '''
        return typing.cast(typing.List["SpdxLicense"], jsii.sinvoke(cls, "all", []))

    @jsii.member(jsii_name="apache") # type: ignore[misc]
    @builtins.classmethod
    def apache(cls) -> typing.List["SpdxLicense"]:
        '''(experimental) The Apache family of licenses.

        :stability: experimental
        '''
        return typing.cast(typing.List["SpdxLicense"], jsii.sinvoke(cls, "apache", []))

    @jsii.member(jsii_name="bsd") # type: ignore[misc]
    @builtins.classmethod
    def bsd(cls) -> typing.List["SpdxLicense"]:
        '''(experimental) The BSD family of licenses.

        :stability: experimental
        '''
        return typing.cast(typing.List["SpdxLicense"], jsii.sinvoke(cls, "bsd", []))

    @jsii.member(jsii_name="cddl") # type: ignore[misc]
    @builtins.classmethod
    def cddl(cls) -> typing.List["SpdxLicense"]:
        '''(experimental) The CDDL family of licenses.

        :stability: experimental
        '''
        return typing.cast(typing.List["SpdxLicense"], jsii.sinvoke(cls, "cddl", []))

    @jsii.member(jsii_name="epl") # type: ignore[misc]
    @builtins.classmethod
    def epl(cls) -> typing.List["SpdxLicense"]:
        '''(experimental) The EPL family of licenses.

        :stability: experimental
        '''
        return typing.cast(typing.List["SpdxLicense"], jsii.sinvoke(cls, "epl", []))

    @jsii.member(jsii_name="mit") # type: ignore[misc]
    @builtins.classmethod
    def mit(cls) -> typing.List["SpdxLicense"]:
        '''(experimental) The MIT family of licenses.

        :stability: experimental
        '''
        return typing.cast(typing.List["SpdxLicense"], jsii.sinvoke(cls, "mit", []))

    @jsii.member(jsii_name="mpl") # type: ignore[misc]
    @builtins.classmethod
    def mpl(cls) -> typing.List["SpdxLicense"]:
        '''(experimental) The MPL family of licenses.

        :stability: experimental
        '''
        return typing.cast(typing.List["SpdxLicense"], jsii.sinvoke(cls, "mpl", []))

    @jsii.member(jsii_name="osiApproved") # type: ignore[misc]
    @builtins.classmethod
    def osi_approved(cls) -> typing.List["SpdxLicense"]:
        '''(experimental) All OSI-Approved SPDX Licenses.

        :stability: experimental
        '''
        return typing.cast(typing.List["SpdxLicense"], jsii.sinvoke(cls, "osiApproved", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AAL")
    def AAL(cls) -> "SpdxLicense":
        '''(experimental) Attribution Assurance License.

        :see: https://opensource.org/licenses/attribution
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AAL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ABSTYLES")
    def ABSTYLES(cls) -> "SpdxLicense":
        '''(experimental) Abstyles License.

        :see: https://fedoraproject.org/wiki/Licensing/Abstyles
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ABSTYLES"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ADOBE_2006")
    def ADOBE_2006(cls) -> "SpdxLicense":
        '''(experimental) Adobe Systems Incorporated Source Code License Agreement.

        :see: https://fedoraproject.org/wiki/Licensing/AdobeLicense
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ADOBE_2006"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ADOBE_GLYPH")
    def ADOBE_GLYPH(cls) -> "SpdxLicense":
        '''(experimental) Adobe Glyph List License.

        :see: https://fedoraproject.org/wiki/Licensing/MIT#AdobeGlyph
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ADOBE_GLYPH"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ADSL")
    def ADSL(cls) -> "SpdxLicense":
        '''(experimental) Amazon Digital Services License.

        :see: https://fedoraproject.org/wiki/Licensing/AmazonDigitalServicesLicense
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ADSL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AFL_1_1")
    def AFL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Academic Free License v1.1.

        :see: http://opensource.linux-mirror.org/licenses/afl-1.1.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AFL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AFL_1_2")
    def AFL_1_2(cls) -> "SpdxLicense":
        '''(experimental) Academic Free License v1.2.

        :see: http://opensource.linux-mirror.org/licenses/afl-1.2.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AFL_1_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AFL_2_0")
    def AFL_2_0(cls) -> "SpdxLicense":
        '''(experimental) Academic Free License v2.0.

        :see: http://wayback.archive.org/web/20060924134533/http://www.opensource.org/licenses/afl-2.0.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AFL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AFL_2_1")
    def AFL_2_1(cls) -> "SpdxLicense":
        '''(experimental) Academic Free License v2.1.

        :see: http://opensource.linux-mirror.org/licenses/afl-2.1.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AFL_2_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AFL_3_0")
    def AFL_3_0(cls) -> "SpdxLicense":
        '''(experimental) Academic Free License v3.0.

        :see: http://www.rosenlaw.com/AFL3.0.htm
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AFL_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AFMPARSE")
    def AFMPARSE(cls) -> "SpdxLicense":
        '''(experimental) Afmparse License.

        :see: https://fedoraproject.org/wiki/Licensing/Afmparse
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AFMPARSE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AGPL_1_0")
    def AGPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Affero General Public License v1.0.

        :see: http://www.affero.org/oagpl.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AGPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AGPL_1_0_ONLY")
    def AGPL_1_0_ONLY(cls) -> "SpdxLicense":
        '''(experimental) Affero General Public License v1.0 only.

        :see: http://www.affero.org/oagpl.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AGPL_1_0_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AGPL_1_0_OR_LATER")
    def AGPL_1_0_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) Affero General Public License v1.0 or later.

        :see: http://www.affero.org/oagpl.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AGPL_1_0_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AGPL_3_0")
    def AGPL_3_0(cls) -> "SpdxLicense":
        '''(experimental) GNU Affero General Public License v3.0.

        :see: https://www.gnu.org/licenses/agpl.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AGPL_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AGPL_3_0_ONLY")
    def AGPL_3_0_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Affero General Public License v3.0 only.

        :see: https://www.gnu.org/licenses/agpl.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AGPL_3_0_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AGPL_3_0_OR_LATER")
    def AGPL_3_0_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Affero General Public License v3.0 or later.

        :see: https://www.gnu.org/licenses/agpl.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AGPL_3_0_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ALADDIN")
    def ALADDIN(cls) -> "SpdxLicense":
        '''(experimental) Aladdin Free Public License.

        :see: http://pages.cs.wisc.edu/~ghost/doc/AFPL/6.01/Public.htm
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ALADDIN"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AMDPLPA")
    def AMDPLPA(cls) -> "SpdxLicense":
        '''(experimental) AMD's plpa_map.c License.

        :see: https://fedoraproject.org/wiki/Licensing/AMD_plpa_map_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AMDPLPA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AML")
    def AML(cls) -> "SpdxLicense":
        '''(experimental) Apple MIT License.

        :see: https://fedoraproject.org/wiki/Licensing/Apple_MIT_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AML"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AMPAS")
    def AMPAS(cls) -> "SpdxLicense":
        '''(experimental) Academy of Motion Picture Arts and Sciences BSD.

        :see: https://fedoraproject.org/wiki/Licensing/BSD#AMPASBSD
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "AMPAS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ANTLR_PD")
    def ANTLR_PD(cls) -> "SpdxLicense":
        '''(experimental) ANTLR Software Rights Notice.

        :see: http://www.antlr2.org/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ANTLR_PD"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ANTLR_PD_FALLBACK")
    def ANTLR_PD_FALLBACK(cls) -> "SpdxLicense":
        '''(experimental) ANTLR Software Rights Notice with license fallback.

        :see: http://www.antlr2.org/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ANTLR_PD_FALLBACK"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="APACHE_1_0")
    def APACHE_1_0(cls) -> "SpdxLicense":
        '''(experimental) Apache License 1.0.

        :see: http://www.apache.org/licenses/LICENSE-1.0
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "APACHE_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="APACHE_1_1")
    def APACHE_1_1(cls) -> "SpdxLicense":
        '''(experimental) Apache License 1.1.

        :see: http://apache.org/licenses/LICENSE-1.1
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "APACHE_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="APACHE_2_0")
    def APACHE_2_0(cls) -> "SpdxLicense":
        '''(experimental) Apache License 2.0.

        :see: http://www.apache.org/licenses/LICENSE-2.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "APACHE_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="APAFML")
    def APAFML(cls) -> "SpdxLicense":
        '''(experimental) Adobe Postscript AFM License.

        :see: https://fedoraproject.org/wiki/Licensing/AdobePostscriptAFM
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "APAFML"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="APL_1_0")
    def APL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Adaptive Public License 1.0.

        :see: https://opensource.org/licenses/APL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "APL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="APSL_1_0")
    def APSL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Apple Public Source License 1.0.

        :see: https://fedoraproject.org/wiki/Licensing/Apple_Public_Source_License_1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "APSL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="APSL_1_1")
    def APSL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Apple Public Source License 1.1.

        :see: http://www.opensource.apple.com/source/IOSerialFamily/IOSerialFamily-7/APPLE_LICENSE
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "APSL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="APSL_1_2")
    def APSL_1_2(cls) -> "SpdxLicense":
        '''(experimental) Apple Public Source License 1.2.

        :see: http://www.samurajdata.se/opensource/mirror/licenses/apsl.php
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "APSL_1_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="APSL_2_0")
    def APSL_2_0(cls) -> "SpdxLicense":
        '''(experimental) Apple Public Source License 2.0.

        :see: http://www.opensource.apple.com/license/apsl/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "APSL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ARTISTIC_1_0")
    def ARTISTIC_1_0(cls) -> "SpdxLicense":
        '''(experimental) Artistic License 1.0.

        :see: https://opensource.org/licenses/Artistic-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ARTISTIC_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ARTISTIC_1_0_CL8")
    def ARTISTIC_1_0_CL8(cls) -> "SpdxLicense":
        '''(experimental) Artistic License 1.0 w/clause 8.

        :see: https://opensource.org/licenses/Artistic-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ARTISTIC_1_0_CL8"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ARTISTIC_1_0_PERL")
    def ARTISTIC_1_0_PERL(cls) -> "SpdxLicense":
        '''(experimental) Artistic License 1.0 (Perl).

        :see: http://dev.perl.org/licenses/artistic.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ARTISTIC_1_0_PERL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ARTISTIC_2_0")
    def ARTISTIC_2_0(cls) -> "SpdxLicense":
        '''(experimental) Artistic License 2.0.

        :see: http://www.perlfoundation.org/artistic_license_2_0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ARTISTIC_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BAHYPH")
    def BAHYPH(cls) -> "SpdxLicense":
        '''(experimental) Bahyph License.

        :see: https://fedoraproject.org/wiki/Licensing/Bahyph
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BAHYPH"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BARR")
    def BARR(cls) -> "SpdxLicense":
        '''(experimental) Barr License.

        :see: https://fedoraproject.org/wiki/Licensing/Barr
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BARR"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BEERWARE")
    def BEERWARE(cls) -> "SpdxLicense":
        '''(experimental) Beerware License.

        :see: https://fedoraproject.org/wiki/Licensing/Beerware
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BEERWARE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BITTORRENT_1_0")
    def BITTORRENT_1_0(cls) -> "SpdxLicense":
        '''(experimental) BitTorrent Open Source License v1.0.

        :see: http://sources.gentoo.org/cgi-bin/viewvc.cgi/gentoo-x86/licenses/BitTorrent?r1=1.1&r2=1.1.1.1&diff_format=s
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BITTORRENT_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BITTORRENT_1_1")
    def BITTORRENT_1_1(cls) -> "SpdxLicense":
        '''(experimental) BitTorrent Open Source License v1.1.

        :see: http://directory.fsf.org/wiki/License:BitTorrentOSL1.1
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BITTORRENT_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BLESSING")
    def BLESSING(cls) -> "SpdxLicense":
        '''(experimental) SQLite Blessing.

        :see: https://www.sqlite.org/src/artifact/e33a4df7e32d742a?ln=4-9
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BLESSING"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BLUEOAK_1_0_0")
    def BLUEOAK_1_0_0(cls) -> "SpdxLicense":
        '''(experimental) Blue Oak Model License 1.0.0.

        :see: https://blueoakcouncil.org/license/1.0.0
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BLUEOAK_1_0_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BORCEUX")
    def BORCEUX(cls) -> "SpdxLicense":
        '''(experimental) Borceux license.

        :see: https://fedoraproject.org/wiki/Licensing/Borceux
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BORCEUX"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_1_CLAUSE")
    def BSD_1_CLAUSE(cls) -> "SpdxLicense":
        '''(experimental) BSD 1-Clause License.

        :see: https://svnweb.freebsd.org/base/head/include/ifaddrs.h?revision=326823
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_1_CLAUSE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_2_CLAUSE")
    def BSD_2_CLAUSE(cls) -> "SpdxLicense":
        '''(experimental) BSD 2-Clause "Simplified" License.

        :see: https://opensource.org/licenses/BSD-2-Clause
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_2_CLAUSE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_2_CLAUSE_FREEBSD")
    def BSD_2_CLAUSE_FREEBSD(cls) -> "SpdxLicense":
        '''(experimental) BSD 2-Clause FreeBSD License.

        :see: http://www.freebsd.org/copyright/freebsd-license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_2_CLAUSE_FREEBSD"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_2_CLAUSE_NETBSD")
    def BSD_2_CLAUSE_NETBSD(cls) -> "SpdxLicense":
        '''(experimental) BSD 2-Clause NetBSD License.

        :see: http://www.netbsd.org/about/redistribution.html#default
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_2_CLAUSE_NETBSD"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_2_CLAUSE_PATENT")
    def BSD_2_CLAUSE_PATENT(cls) -> "SpdxLicense":
        '''(experimental) BSD-2-Clause Plus Patent License.

        :see: https://opensource.org/licenses/BSDplusPatent
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_2_CLAUSE_PATENT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_2_CLAUSE_VIEWS")
    def BSD_2_CLAUSE_VIEWS(cls) -> "SpdxLicense":
        '''(experimental) BSD 2-Clause with views sentence.

        :see: http://www.freebsd.org/copyright/freebsd-license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_2_CLAUSE_VIEWS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_3_CLAUSE")
    def BSD_3_CLAUSE(cls) -> "SpdxLicense":
        '''(experimental) BSD 3-Clause "New" or "Revised" License.

        :see: https://opensource.org/licenses/BSD-3-Clause
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_3_CLAUSE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_3_CLAUSE_ATTRIBUTION")
    def BSD_3_CLAUSE_ATTRIBUTION(cls) -> "SpdxLicense":
        '''(experimental) BSD with attribution.

        :see: https://fedoraproject.org/wiki/Licensing/BSD_with_Attribution
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_3_CLAUSE_ATTRIBUTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_3_CLAUSE_CLEAR")
    def BSD_3_CLAUSE_CLEAR(cls) -> "SpdxLicense":
        '''(experimental) BSD 3-Clause Clear License.

        :see: http://labs.metacarta.com/license-explanation.html#license
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_3_CLAUSE_CLEAR"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_3_CLAUSE_LBNL")
    def BSD_3_CLAUSE_LBNL(cls) -> "SpdxLicense":
        '''(experimental) Lawrence Berkeley National Labs BSD variant license.

        :see: https://fedoraproject.org/wiki/Licensing/LBNLBSD
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_3_CLAUSE_LBNL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_3_CLAUSE_NO_NUCLEAR_LICENSE")
    def BSD_3_CLAUSE_NO_NUCLEAR_LICENSE(cls) -> "SpdxLicense":
        '''(experimental) BSD 3-Clause No Nuclear License.

        :see: http://download.oracle.com/otn-pub/java/licenses/bsd.txt?AuthParam=1467140197_43d516ce1776bd08a58235a7785be1cc
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_3_CLAUSE_NO_NUCLEAR_LICENSE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_3_CLAUSE_NO_NUCLEAR_LICENSE_2014")
    def BSD_3_CLAUSE_NO_NUCLEAR_LICENSE_2014(cls) -> "SpdxLicense":
        '''(experimental) BSD 3-Clause No Nuclear License 2014.

        :see: https://java.net/projects/javaeetutorial/pages/BerkeleyLicense
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_3_CLAUSE_NO_NUCLEAR_LICENSE_2014"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_3_CLAUSE_NO_NUCLEAR_WARRANTY")
    def BSD_3_CLAUSE_NO_NUCLEAR_WARRANTY(cls) -> "SpdxLicense":
        '''(experimental) BSD 3-Clause No Nuclear Warranty.

        :see: https://jogamp.org/git/?p=gluegen.git;a=blob_plain;f=LICENSE.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_3_CLAUSE_NO_NUCLEAR_WARRANTY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_3_CLAUSE_OPEN_MPI")
    def BSD_3_CLAUSE_OPEN_MPI(cls) -> "SpdxLicense":
        '''(experimental) BSD 3-Clause Open MPI variant.

        :see: https://www.open-mpi.org/community/license.php
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_3_CLAUSE_OPEN_MPI"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_4_CLAUSE")
    def BSD_4_CLAUSE(cls) -> "SpdxLicense":
        '''(experimental) BSD 4-Clause "Original" or "Old" License.

        :see: http://directory.fsf.org/wiki/License:BSD_4Clause
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_4_CLAUSE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_4_CLAUSE_UC")
    def BSD_4_CLAUSE_UC(cls) -> "SpdxLicense":
        '''(experimental) BSD-4-Clause (University of California-Specific).

        :see: http://www.freebsd.org/copyright/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_4_CLAUSE_UC"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_PROTECTION")
    def BSD_PROTECTION(cls) -> "SpdxLicense":
        '''(experimental) BSD Protection License.

        :see: https://fedoraproject.org/wiki/Licensing/BSD_Protection_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_PROTECTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSD_SOURCE_CODE")
    def BSD_SOURCE_CODE(cls) -> "SpdxLicense":
        '''(experimental) BSD Source Code Attribution.

        :see: https://github.com/robbiehanson/CocoaHTTPServer/blob/master/LICENSE.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSD_SOURCE_CODE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BSL_1_0")
    def BSL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Boost Software License 1.0.

        :see: http://www.boost.org/LICENSE_1_0.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BSL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BUSL_1_1")
    def BUSL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Business Source License 1.1.

        :see: https://mariadb.com/bsl11/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BUSL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BZIP2_1_0_5")
    def BZIP2_1_0_5(cls) -> "SpdxLicense":
        '''(experimental) bzip2 and libbzip2 License v1.0.5.

        :see: https://sourceware.org/bzip2/1.0.5/bzip2-manual-1.0.5.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BZIP2_1_0_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="BZIP2_1_0_6")
    def BZIP2_1_0_6(cls) -> "SpdxLicense":
        '''(experimental) bzip2 and libbzip2 License v1.0.6.

        :see: https://sourceware.org/git/?p=bzip2.git;a=blob;f=LICENSE;hb=bzip2-1.0.6
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "BZIP2_1_0_6"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CAL_1_0")
    def CAL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Cryptographic Autonomy License 1.0.

        :see: http://cryptographicautonomylicense.com/license-text.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CAL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CAL_1_0_COMBINED_WORK_EXCEPTION")
    def CAL_1_0_COMBINED_WORK_EXCEPTION(cls) -> "SpdxLicense":
        '''(experimental) Cryptographic Autonomy License 1.0 (Combined Work Exception).

        :see: http://cryptographicautonomylicense.com/license-text.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CAL_1_0_COMBINED_WORK_EXCEPTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CALDERA")
    def CALDERA(cls) -> "SpdxLicense":
        '''(experimental) Caldera License.

        :see: http://www.lemis.com/grog/UNIX/ancient-source-all.pdf
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CALDERA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CATOSL_1_1")
    def CATOSL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Computer Associates Trusted Open Source License 1.1.

        :see: https://opensource.org/licenses/CATOSL-1.1
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CATOSL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_1_0")
    def CC_BY_1_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution 1.0 Generic.

        :see: https://creativecommons.org/licenses/by/1.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_2_0")
    def CC_BY_2_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution 2.0 Generic.

        :see: https://creativecommons.org/licenses/by/2.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_2_5")
    def CC_BY_2_5(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution 2.5 Generic.

        :see: https://creativecommons.org/licenses/by/2.5/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_2_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_3_0")
    def CC_BY_3_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution 3.0 Unported.

        :see: https://creativecommons.org/licenses/by/3.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_3_0_AT")
    def CC_BY_3_0_AT(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution 3.0 Austria.

        :see: https://creativecommons.org/licenses/by/3.0/at/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_3_0_AT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_3_0_US")
    def CC_BY_3_0_US(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution 3.0 United States.

        :see: https://creativecommons.org/licenses/by/3.0/us/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_3_0_US"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_4_0")
    def CC_BY_4_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution 4.0 International.

        :see: https://creativecommons.org/licenses/by/4.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_4_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_1_0")
    def CC_BY_NC_1_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial 1.0 Generic.

        :see: https://creativecommons.org/licenses/by-nc/1.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_2_0")
    def CC_BY_NC_2_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial 2.0 Generic.

        :see: https://creativecommons.org/licenses/by-nc/2.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_2_5")
    def CC_BY_NC_2_5(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial 2.5 Generic.

        :see: https://creativecommons.org/licenses/by-nc/2.5/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_2_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_3_0")
    def CC_BY_NC_3_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial 3.0 Unported.

        :see: https://creativecommons.org/licenses/by-nc/3.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_4_0")
    def CC_BY_NC_4_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial 4.0 International.

        :see: https://creativecommons.org/licenses/by-nc/4.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_4_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_ND_1_0")
    def CC_BY_NC_ND_1_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial No Derivatives 1.0 Generic.

        :see: https://creativecommons.org/licenses/by-nd-nc/1.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_ND_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_ND_2_0")
    def CC_BY_NC_ND_2_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial No Derivatives 2.0 Generic.

        :see: https://creativecommons.org/licenses/by-nc-nd/2.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_ND_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_ND_2_5")
    def CC_BY_NC_ND_2_5(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial No Derivatives 2.5 Generic.

        :see: https://creativecommons.org/licenses/by-nc-nd/2.5/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_ND_2_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_ND_3_0")
    def CC_BY_NC_ND_3_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial No Derivatives 3.0 Unported.

        :see: https://creativecommons.org/licenses/by-nc-nd/3.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_ND_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_ND_3_0_IGO")
    def CC_BY_NC_ND_3_0_IGO(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial No Derivatives 3.0 IGO.

        :see: https://creativecommons.org/licenses/by-nc-nd/3.0/igo/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_ND_3_0_IGO"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_ND_4_0")
    def CC_BY_NC_ND_4_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial No Derivatives 4.0 International.

        :see: https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_ND_4_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_SA_1_0")
    def CC_BY_NC_SA_1_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial Share Alike 1.0 Generic.

        :see: https://creativecommons.org/licenses/by-nc-sa/1.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_SA_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_SA_2_0")
    def CC_BY_NC_SA_2_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial Share Alike 2.0 Generic.

        :see: https://creativecommons.org/licenses/by-nc-sa/2.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_SA_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_SA_2_5")
    def CC_BY_NC_SA_2_5(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial Share Alike 2.5 Generic.

        :see: https://creativecommons.org/licenses/by-nc-sa/2.5/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_SA_2_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_SA_3_0")
    def CC_BY_NC_SA_3_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial Share Alike 3.0 Unported.

        :see: https://creativecommons.org/licenses/by-nc-sa/3.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_SA_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_NC_SA_4_0")
    def CC_BY_NC_SA_4_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Non Commercial Share Alike 4.0 International.

        :see: https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_NC_SA_4_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_ND_1_0")
    def CC_BY_ND_1_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution No Derivatives 1.0 Generic.

        :see: https://creativecommons.org/licenses/by-nd/1.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_ND_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_ND_2_0")
    def CC_BY_ND_2_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution No Derivatives 2.0 Generic.

        :see: https://creativecommons.org/licenses/by-nd/2.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_ND_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_ND_2_5")
    def CC_BY_ND_2_5(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution No Derivatives 2.5 Generic.

        :see: https://creativecommons.org/licenses/by-nd/2.5/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_ND_2_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_ND_3_0")
    def CC_BY_ND_3_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution No Derivatives 3.0 Unported.

        :see: https://creativecommons.org/licenses/by-nd/3.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_ND_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_ND_4_0")
    def CC_BY_ND_4_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution No Derivatives 4.0 International.

        :see: https://creativecommons.org/licenses/by-nd/4.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_ND_4_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_SA_1_0")
    def CC_BY_SA_1_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Share Alike 1.0 Generic.

        :see: https://creativecommons.org/licenses/by-sa/1.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_SA_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_SA_2_0")
    def CC_BY_SA_2_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Share Alike 2.0 Generic.

        :see: https://creativecommons.org/licenses/by-sa/2.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_SA_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_SA_2_0_UK")
    def CC_BY_SA_2_0_UK(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Share Alike 2.0 England and Wales.

        :see: https://creativecommons.org/licenses/by-sa/2.0/uk/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_SA_2_0_UK"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_SA_2_5")
    def CC_BY_SA_2_5(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Share Alike 2.5 Generic.

        :see: https://creativecommons.org/licenses/by-sa/2.5/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_SA_2_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_SA_3_0")
    def CC_BY_SA_3_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Share Alike 3.0 Unported.

        :see: https://creativecommons.org/licenses/by-sa/3.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_SA_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_SA_3_0_AT")
    def CC_BY_SA_3_0_AT(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution-Share Alike 3.0 Austria.

        :see: https://creativecommons.org/licenses/by-sa/3.0/at/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_SA_3_0_AT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_BY_SA_4_0")
    def CC_BY_SA_4_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Attribution Share Alike 4.0 International.

        :see: https://creativecommons.org/licenses/by-sa/4.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_BY_SA_4_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC_PDDC")
    def CC_PDDC(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Public Domain Dedication and Certification.

        :see: https://creativecommons.org/licenses/publicdomain/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC_PDDC"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CC0_1_0")
    def CC0_1_0(cls) -> "SpdxLicense":
        '''(experimental) Creative Commons Zero v1.0 Universal.

        :see: https://creativecommons.org/publicdomain/zero/1.0/legalcode
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CC0_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CDDL_1_0")
    def CDDL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Common Development and Distribution License 1.0.

        :see: https://opensource.org/licenses/cddl1
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CDDL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CDDL_1_1")
    def CDDL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Common Development and Distribution License 1.1.

        :see: http://glassfish.java.net/public/CDDL+GPL_1_1.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CDDL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CDLA_PERMISSIVE_1_0")
    def CDLA_PERMISSIVE_1_0(cls) -> "SpdxLicense":
        '''(experimental) Community Data License Agreement Permissive 1.0.

        :see: https://cdla.io/permissive-1-0
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CDLA_PERMISSIVE_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CDLA_SHARING_1_0")
    def CDLA_SHARING_1_0(cls) -> "SpdxLicense":
        '''(experimental) Community Data License Agreement Sharing 1.0.

        :see: https://cdla.io/sharing-1-0
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CDLA_SHARING_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CECILL_1_0")
    def CECILL_1_0(cls) -> "SpdxLicense":
        '''(experimental) CeCILL Free Software License Agreement v1.0.

        :see: http://www.cecill.info/licences/Licence_CeCILL_V1-fr.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CECILL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CECILL_1_1")
    def CECILL_1_1(cls) -> "SpdxLicense":
        '''(experimental) CeCILL Free Software License Agreement v1.1.

        :see: http://www.cecill.info/licences/Licence_CeCILL_V1.1-US.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CECILL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CECILL_2_0")
    def CECILL_2_0(cls) -> "SpdxLicense":
        '''(experimental) CeCILL Free Software License Agreement v2.0.

        :see: http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CECILL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CECILL_2_1")
    def CECILL_2_1(cls) -> "SpdxLicense":
        '''(experimental) CeCILL Free Software License Agreement v2.1.

        :see: http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CECILL_2_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CECILL_B")
    def CECILL_B(cls) -> "SpdxLicense":
        '''(experimental) CeCILL-B Free Software License Agreement.

        :see: http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CECILL_B"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CECILL_C")
    def CECILL_C(cls) -> "SpdxLicense":
        '''(experimental) CeCILL-C Free Software License Agreement.

        :see: http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CECILL_C"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CERN_OHL_1_1")
    def CERN_OHL_1_1(cls) -> "SpdxLicense":
        '''(experimental) CERN Open Hardware Licence v1.1.

        :see: https://www.ohwr.org/project/licenses/wikis/cern-ohl-v1.1
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CERN_OHL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CERN_OHL_1_2")
    def CERN_OHL_1_2(cls) -> "SpdxLicense":
        '''(experimental) CERN Open Hardware Licence v1.2.

        :see: https://www.ohwr.org/project/licenses/wikis/cern-ohl-v1.2
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CERN_OHL_1_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CERN_OHL_P_2_0")
    def CERN_OHL_P_2_0(cls) -> "SpdxLicense":
        '''(experimental) CERN Open Hardware Licence Version 2 - Permissive.

        :see: https://www.ohwr.org/project/cernohl/wikis/Documents/CERN-OHL-version-2
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CERN_OHL_P_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CERN_OHL_S_2_0")
    def CERN_OHL_S_2_0(cls) -> "SpdxLicense":
        '''(experimental) CERN Open Hardware Licence Version 2 - Strongly Reciprocal.

        :see: https://www.ohwr.org/project/cernohl/wikis/Documents/CERN-OHL-version-2
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CERN_OHL_S_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CERN_OHL_W_2_0")
    def CERN_OHL_W_2_0(cls) -> "SpdxLicense":
        '''(experimental) CERN Open Hardware Licence Version 2 - Weakly Reciprocal.

        :see: https://www.ohwr.org/project/cernohl/wikis/Documents/CERN-OHL-version-2
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CERN_OHL_W_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CL_ARTISTIC")
    def CL_ARTISTIC(cls) -> "SpdxLicense":
        '''(experimental) Clarified Artistic License.

        :see: http://gianluca.dellavedova.org/2011/01/03/clarified-artistic-license/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CL_ARTISTIC"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CNRI_JYTHON")
    def CNRI_JYTHON(cls) -> "SpdxLicense":
        '''(experimental) CNRI Jython License.

        :see: http://www.jython.org/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CNRI_JYTHON"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CNRI_PYTHON")
    def CNRI_PYTHON(cls) -> "SpdxLicense":
        '''(experimental) CNRI Python License.

        :see: https://opensource.org/licenses/CNRI-Python
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CNRI_PYTHON"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CNRI_PYTHON_GPL_COMPATIBLE")
    def CNRI_PYTHON_GPL_COMPATIBLE(cls) -> "SpdxLicense":
        '''(experimental) CNRI Python Open Source GPL Compatible License Agreement.

        :see: http://www.python.org/download/releases/1.6.1/download_win/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CNRI_PYTHON_GPL_COMPATIBLE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CONDOR_1_1")
    def CONDOR_1_1(cls) -> "SpdxLicense":
        '''(experimental) Condor Public License v1.1.

        :see: http://research.cs.wisc.edu/condor/license.html#condor
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CONDOR_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="COPYLEFT_NEXT_0_3_0")
    def COPYLEFT_NEXT_0_3_0(cls) -> "SpdxLicense":
        '''(experimental) copyleft-next 0.3.0.

        :see: https://github.com/copyleft-next/copyleft-next/blob/master/Releases/copyleft-next-0.3.0
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "COPYLEFT_NEXT_0_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="COPYLEFT_NEXT_0_3_1")
    def COPYLEFT_NEXT_0_3_1(cls) -> "SpdxLicense":
        '''(experimental) copyleft-next 0.3.1.

        :see: https://github.com/copyleft-next/copyleft-next/blob/master/Releases/copyleft-next-0.3.1
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "COPYLEFT_NEXT_0_3_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CPAL_1_0")
    def CPAL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Common Public Attribution License 1.0.

        :see: https://opensource.org/licenses/CPAL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CPAL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CPL_1_0")
    def CPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Common Public License 1.0.

        :see: https://opensource.org/licenses/CPL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CPOL_1_02")
    def CPOL_1_02(cls) -> "SpdxLicense":
        '''(experimental) Code Project Open License 1.02.

        :see: http://www.codeproject.com/info/cpol10.aspx
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CPOL_1_02"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CROSSWORD")
    def CROSSWORD(cls) -> "SpdxLicense":
        '''(experimental) Crossword License.

        :see: https://fedoraproject.org/wiki/Licensing/Crossword
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CROSSWORD"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CRYSTAL_STACKER")
    def CRYSTAL_STACKER(cls) -> "SpdxLicense":
        '''(experimental) CrystalStacker License.

        :see: https://fedoraproject.org/wiki/Licensing:CrystalStacker?rd=Licensing/CrystalStacker
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CRYSTAL_STACKER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CUA_OPL_1_0")
    def CUA_OPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) CUA Office Public License v1.0.

        :see: https://opensource.org/licenses/CUA-OPL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CUA_OPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CUBE")
    def CUBE(cls) -> "SpdxLicense":
        '''(experimental) Cube License.

        :see: https://fedoraproject.org/wiki/Licensing/Cube
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CUBE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CURL")
    def CURL(cls) -> "SpdxLicense":
        '''(experimental) curl License.

        :see: https://github.com/bagder/curl/blob/master/COPYING
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "CURL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="D_FSL_1_0")
    def D_FSL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Deutsche Freie Software Lizenz.

        :see: http://www.dipp.nrw.de/d-fsl/lizenzen/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "D_FSL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DIFFMARK")
    def DIFFMARK(cls) -> "SpdxLicense":
        '''(experimental) diffmark license.

        :see: https://fedoraproject.org/wiki/Licensing/diffmark
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "DIFFMARK"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DOC")
    def DOC(cls) -> "SpdxLicense":
        '''(experimental) DOC License.

        :see: http://www.cs.wustl.edu/~schmidt/ACE-copying.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "DOC"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DOTSEQN")
    def DOTSEQN(cls) -> "SpdxLicense":
        '''(experimental) Dotseqn License.

        :see: https://fedoraproject.org/wiki/Licensing/Dotseqn
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "DOTSEQN"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DSDP")
    def DSDP(cls) -> "SpdxLicense":
        '''(experimental) DSDP License.

        :see: https://fedoraproject.org/wiki/Licensing/DSDP
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "DSDP"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DVIPDFM")
    def DVIPDFM(cls) -> "SpdxLicense":
        '''(experimental) dvipdfm License.

        :see: https://fedoraproject.org/wiki/Licensing/dvipdfm
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "DVIPDFM"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="E_GENIX")
    def E_GENIX(cls) -> "SpdxLicense":
        '''(experimental) eGenix.com Public License 1.1.0.

        :see: http://www.egenix.com/products/eGenix.com-Public-License-1.1.0.pdf
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "E_GENIX"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ECL_1_0")
    def ECL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Educational Community License v1.0.

        :see: https://opensource.org/licenses/ECL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ECL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ECL_2_0")
    def ECL_2_0(cls) -> "SpdxLicense":
        '''(experimental) Educational Community License v2.0.

        :see: https://opensource.org/licenses/ECL-2.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ECL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ECOS_2_0")
    def ECOS_2_0(cls) -> "SpdxLicense":
        '''(experimental) eCos license version 2.0.

        :see: https://www.gnu.org/licenses/ecos-license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ECOS_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="EFL_1_0")
    def EFL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Eiffel Forum License v1.0.

        :see: http://www.eiffel-nice.org/license/forum.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "EFL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="EFL_2_0")
    def EFL_2_0(cls) -> "SpdxLicense":
        '''(experimental) Eiffel Forum License v2.0.

        :see: http://www.eiffel-nice.org/license/eiffel-forum-license-2.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "EFL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ENTESSA")
    def ENTESSA(cls) -> "SpdxLicense":
        '''(experimental) Entessa Public License v1.0.

        :see: https://opensource.org/licenses/Entessa
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ENTESSA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="EPICS")
    def EPICS(cls) -> "SpdxLicense":
        '''(experimental) EPICS Open License.

        :see: https://epics.anl.gov/license/open.php
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "EPICS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="EPL_1_0")
    def EPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Eclipse Public License 1.0.

        :see: http://www.eclipse.org/legal/epl-v10.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "EPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="EPL_2_0")
    def EPL_2_0(cls) -> "SpdxLicense":
        '''(experimental) Eclipse Public License 2.0.

        :see: https://www.eclipse.org/legal/epl-2.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "EPL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ERLPL_1_1")
    def ERLPL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Erlang Public License v1.1.

        :see: http://www.erlang.org/EPLICENSE
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ERLPL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ETALAB_2_0")
    def ETALAB_2_0(cls) -> "SpdxLicense":
        '''(experimental) Etalab Open License 2.0.

        :see: https://github.com/DISIC/politique-de-contribution-open-source/blob/master/LICENSE.pdf
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ETALAB_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="EUDATAGRID")
    def EUDATAGRID(cls) -> "SpdxLicense":
        '''(experimental) EU DataGrid Software License.

        :see: http://eu-datagrid.web.cern.ch/eu-datagrid/license.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "EUDATAGRID"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="EUPL_1_0")
    def EUPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) European Union Public License 1.0.

        :see: http://ec.europa.eu/idabc/en/document/7330.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "EUPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="EUPL_1_1")
    def EUPL_1_1(cls) -> "SpdxLicense":
        '''(experimental) European Union Public License 1.1.

        :see: https://joinup.ec.europa.eu/software/page/eupl/licence-eupl
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "EUPL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="EUPL_1_2")
    def EUPL_1_2(cls) -> "SpdxLicense":
        '''(experimental) European Union Public License 1.2.

        :see: https://joinup.ec.europa.eu/page/eupl-text-11-12
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "EUPL_1_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="EUROSYM")
    def EUROSYM(cls) -> "SpdxLicense":
        '''(experimental) Eurosym License.

        :see: https://fedoraproject.org/wiki/Licensing/Eurosym
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "EUROSYM"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FAIR")
    def FAIR(cls) -> "SpdxLicense":
        '''(experimental) Fair License.

        :see: http://fairlicense.org/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "FAIR"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FRAMEWORX_1_0")
    def FRAMEWORX_1_0(cls) -> "SpdxLicense":
        '''(experimental) Frameworx Open License 1.0.

        :see: https://opensource.org/licenses/Frameworx-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "FRAMEWORX_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FREE_IMAGE")
    def FREE_IMAGE(cls) -> "SpdxLicense":
        '''(experimental) FreeImage Public License v1.0.

        :see: http://freeimage.sourceforge.net/freeimage-license.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "FREE_IMAGE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FSFAP")
    def FSFAP(cls) -> "SpdxLicense":
        '''(experimental) FSF All Permissive License.

        :see: https://www.gnu.org/prep/maintain/html_node/License-Notices-for-Other-Files.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "FSFAP"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FSFUL")
    def FSFUL(cls) -> "SpdxLicense":
        '''(experimental) FSF Unlimited License.

        :see: https://fedoraproject.org/wiki/Licensing/FSF_Unlimited_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "FSFUL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FSFULLR")
    def FSFULLR(cls) -> "SpdxLicense":
        '''(experimental) FSF Unlimited License (with License Retention).

        :see: https://fedoraproject.org/wiki/Licensing/FSF_Unlimited_License#License_Retention_Variant
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "FSFULLR"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FTL")
    def FTL(cls) -> "SpdxLicense":
        '''(experimental) Freetype Project License.

        :see: http://freetype.fis.uniroma2.it/FTL.TXT
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "FTL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_1")
    def GFDL_1_1(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.1.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.1.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_1_INVARIANTS_ONLY")
    def GFDL_1_1_INVARIANTS_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.1 only - invariants.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.1.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_1_INVARIANTS_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_1_INVARIANTS_OR_LATER")
    def GFDL_1_1_INVARIANTS_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.1 or later - invariants.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.1.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_1_INVARIANTS_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_1_NO_INVARIANTS_ONLY")
    def GFDL_1_1_NO_INVARIANTS_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.1 only - no invariants.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.1.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_1_NO_INVARIANTS_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_1_NO_INVARIANTS_OR_LATER")
    def GFDL_1_1_NO_INVARIANTS_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.1 or later - no invariants.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.1.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_1_NO_INVARIANTS_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_1_ONLY")
    def GFDL_1_1_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.1 only.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.1.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_1_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_1_OR_LATER")
    def GFDL_1_1_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.1 or later.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.1.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_1_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_2")
    def GFDL_1_2(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.2.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.2.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_2_INVARIANTS_ONLY")
    def GFDL_1_2_INVARIANTS_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.2 only - invariants.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.2.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_2_INVARIANTS_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_2_INVARIANTS_OR_LATER")
    def GFDL_1_2_INVARIANTS_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.2 or later - invariants.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.2.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_2_INVARIANTS_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_2_NO_INVARIANTS_ONLY")
    def GFDL_1_2_NO_INVARIANTS_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.2 only - no invariants.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.2.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_2_NO_INVARIANTS_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_2_NO_INVARIANTS_OR_LATER")
    def GFDL_1_2_NO_INVARIANTS_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.2 or later - no invariants.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.2.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_2_NO_INVARIANTS_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_2_ONLY")
    def GFDL_1_2_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.2 only.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.2.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_2_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_2_OR_LATER")
    def GFDL_1_2_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.2 or later.

        :see: https://www.gnu.org/licenses/old-licenses/fdl-1.2.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_2_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_3")
    def GFDL_1_3(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.3.

        :see: https://www.gnu.org/licenses/fdl-1.3.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_3_INVARIANTS_ONLY")
    def GFDL_1_3_INVARIANTS_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.3 only - invariants.

        :see: https://www.gnu.org/licenses/fdl-1.3.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_3_INVARIANTS_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_3_INVARIANTS_OR_LATER")
    def GFDL_1_3_INVARIANTS_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.3 or later - invariants.

        :see: https://www.gnu.org/licenses/fdl-1.3.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_3_INVARIANTS_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_3_NO_INVARIANTS_ONLY")
    def GFDL_1_3_NO_INVARIANTS_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.3 only - no invariants.

        :see: https://www.gnu.org/licenses/fdl-1.3.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_3_NO_INVARIANTS_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_3_NO_INVARIANTS_OR_LATER")
    def GFDL_1_3_NO_INVARIANTS_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.3 or later - no invariants.

        :see: https://www.gnu.org/licenses/fdl-1.3.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_3_NO_INVARIANTS_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_3_ONLY")
    def GFDL_1_3_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.3 only.

        :see: https://www.gnu.org/licenses/fdl-1.3.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_3_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GFDL_1_3_OR_LATER")
    def GFDL_1_3_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Free Documentation License v1.3 or later.

        :see: https://www.gnu.org/licenses/fdl-1.3.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GFDL_1_3_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GIFTWARE")
    def GIFTWARE(cls) -> "SpdxLicense":
        '''(experimental) Giftware License.

        :see: http://liballeg.org/license.html#allegro-4-the-giftware-license
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GIFTWARE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GL2_P_S")
    def GL2_P_S(cls) -> "SpdxLicense":
        '''(experimental) GL2PS License.

        :see: http://www.geuz.org/gl2ps/COPYING.GL2PS
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GL2_P_S"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GLIDE")
    def GLIDE(cls) -> "SpdxLicense":
        '''(experimental) 3dfx Glide License.

        :see: http://www.users.on.net/~triforce/glidexp/COPYING.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GLIDE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GLULXE")
    def GLULXE(cls) -> "SpdxLicense":
        '''(experimental) Glulxe License.

        :see: https://fedoraproject.org/wiki/Licensing/Glulxe
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GLULXE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GLWTPL")
    def GLWTPL(cls) -> "SpdxLicense":
        '''(experimental) Good Luck With That Public License.

        :see: https://github.com/me-shaon/GLWTPL/commit/da5f6bc734095efbacb442c0b31e33a65b9d6e85
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GLWTPL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GNUPLOT")
    def GNUPLOT(cls) -> "SpdxLicense":
        '''(experimental) gnuplot License.

        :see: https://fedoraproject.org/wiki/Licensing/Gnuplot
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GNUPLOT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_1_0")
    def GPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v1.0 only.

        :see: https://www.gnu.org/licenses/old-licenses/gpl-1.0-standalone.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_1_0_ONLY")
    def GPL_1_0_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v1.0 only.

        :see: https://www.gnu.org/licenses/old-licenses/gpl-1.0-standalone.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_1_0_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_1_0_OR_LATER")
    def GPL_1_0_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v1.0 or later.

        :see: https://www.gnu.org/licenses/old-licenses/gpl-1.0-standalone.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_1_0_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_1_0_PLUS")
    def GPL_1_0_PLUS(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v1.0 or later.

        :see: https://www.gnu.org/licenses/old-licenses/gpl-1.0-standalone.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_1_0_PLUS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_2_0")
    def GPL_2_0(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v2.0 only.

        :see: https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_2_0_ONLY")
    def GPL_2_0_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v2.0 only.

        :see: https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_2_0_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_2_0_OR_LATER")
    def GPL_2_0_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v2.0 or later.

        :see: https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_2_0_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_2_0_PLUS")
    def GPL_2_0_PLUS(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v2.0 or later.

        :see: https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_2_0_PLUS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_2_0_WITH_AUTOCONF_EXCEPTION")
    def GPL_2_0_WITH_AUTOCONF_EXCEPTION(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v2.0 w/Autoconf exception.

        :see: http://ac-archive.sourceforge.net/doc/copyright.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_2_0_WITH_AUTOCONF_EXCEPTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_2_0_WITH_BISON_EXCEPTION")
    def GPL_2_0_WITH_BISON_EXCEPTION(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v2.0 w/Bison exception.

        :see: http://git.savannah.gnu.org/cgit/bison.git/tree/data/yacc.c?id=193d7c7054ba7197b0789e14965b739162319b5e#n141
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_2_0_WITH_BISON_EXCEPTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_2_0_WITH_CLASSPATH_EXCEPTION")
    def GPL_2_0_WITH_CLASSPATH_EXCEPTION(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v2.0 w/Classpath exception.

        :see: https://www.gnu.org/software/classpath/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_2_0_WITH_CLASSPATH_EXCEPTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_2_0_WITH_FONT_EXCEPTION")
    def GPL_2_0_WITH_FONT_EXCEPTION(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v2.0 w/Font exception.

        :see: https://www.gnu.org/licenses/gpl-faq.html#FontException
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_2_0_WITH_FONT_EXCEPTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_2_0_WITH_GCC_EXCEPTION")
    def GPL_2_0_WITH_GCC_EXCEPTION(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v2.0 w/GCC Runtime Library exception.

        :see: https://gcc.gnu.org/git/?p=gcc.git;a=blob;f=gcc/libgcc1.c;h=762f5143fc6eed57b6797c82710f3538aa52b40b;hb=cb143a3ce4fb417c68f5fa2691a1b1b1053dfba9#l10
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_2_0_WITH_GCC_EXCEPTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_3_0")
    def GPL_3_0(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v3.0 only.

        :see: https://www.gnu.org/licenses/gpl-3.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_3_0_ONLY")
    def GPL_3_0_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v3.0 only.

        :see: https://www.gnu.org/licenses/gpl-3.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_3_0_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_3_0_OR_LATER")
    def GPL_3_0_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v3.0 or later.

        :see: https://www.gnu.org/licenses/gpl-3.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_3_0_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_3_0_PLUS")
    def GPL_3_0_PLUS(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v3.0 or later.

        :see: https://www.gnu.org/licenses/gpl-3.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_3_0_PLUS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_3_0_WITH_AUTOCONF_EXCEPTION")
    def GPL_3_0_WITH_AUTOCONF_EXCEPTION(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v3.0 w/Autoconf exception.

        :see: https://www.gnu.org/licenses/autoconf-exception-3.0.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_3_0_WITH_AUTOCONF_EXCEPTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GPL_3_0_WITH_GCC_EXCEPTION")
    def GPL_3_0_WITH_GCC_EXCEPTION(cls) -> "SpdxLicense":
        '''(experimental) GNU General Public License v3.0 w/GCC Runtime Library exception.

        :see: https://www.gnu.org/licenses/gcc-exception-3.1.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GPL_3_0_WITH_GCC_EXCEPTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GSOAP_1_3B")
    def GSOAP_1_3_B(cls) -> "SpdxLicense":
        '''(experimental) gSOAP Public License v1.3b.

        :see: http://www.cs.fsu.edu/~engelen/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "GSOAP_1_3B"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="HASKELL_REPORT")
    def HASKELL_REPORT(cls) -> "SpdxLicense":
        '''(experimental) Haskell Language Report License.

        :see: https://fedoraproject.org/wiki/Licensing/Haskell_Language_Report_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "HASKELL_REPORT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="HIPPOCRATIC_2_1")
    def HIPPOCRATIC_2_1(cls) -> "SpdxLicense":
        '''(experimental) Hippocratic License 2.1.

        :see: https://firstdonoharm.dev/version/2/1/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "HIPPOCRATIC_2_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="HPND")
    def HPND(cls) -> "SpdxLicense":
        '''(experimental) Historical Permission Notice and Disclaimer.

        :see: https://opensource.org/licenses/HPND
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "HPND"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="HPND_SELL_VARIANT")
    def HPND_SELL_VARIANT(cls) -> "SpdxLicense":
        '''(experimental) Historical Permission Notice and Disclaimer - sell variant.

        :see: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/sunrpc/auth_gss/gss_generic_token.c?h=v4.19
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "HPND_SELL_VARIANT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="HTMLTIDY")
    def HTMLTIDY(cls) -> "SpdxLicense":
        '''(experimental) HTML Tidy License.

        :see: https://github.com/htacg/tidy-html5/blob/next/README/LICENSE.md
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "HTMLTIDY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="I_MATIX")
    def I_MATIX(cls) -> "SpdxLicense":
        '''(experimental) iMatix Standard Function Library Agreement.

        :see: http://legacy.imatix.com/html/sfl/sfl4.htm#license
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "I_MATIX"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="IBM_PIBS")
    def IBM_PIBS(cls) -> "SpdxLicense":
        '''(experimental) IBM PowerPC Initialization and Boot Software.

        :see: http://git.denx.de/?p=u-boot.git;a=blob;f=arch/powerpc/cpu/ppc4xx/miiphy.c;h=297155fdafa064b955e53e9832de93bfb0cfb85b;hb=9fab4bf4cc077c21e43941866f3f2c196f28670d
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "IBM_PIBS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ICU")
    def ICU(cls) -> "SpdxLicense":
        '''(experimental) ICU License.

        :see: http://source.icu-project.org/repos/icu/icu/trunk/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ICU"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="IJG")
    def IJG(cls) -> "SpdxLicense":
        '''(experimental) Independent JPEG Group License.

        :see: http://dev.w3.org/cvsweb/Amaya/libjpeg/Attic/README?rev=1.2
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "IJG"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="IMAGE_MAGICK")
    def IMAGE_MAGICK(cls) -> "SpdxLicense":
        '''(experimental) ImageMagick License.

        :see: http://www.imagemagick.org/script/license.php
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "IMAGE_MAGICK"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="IMLIB2")
    def IMLIB2(cls) -> "SpdxLicense":
        '''(experimental) Imlib2 License.

        :see: http://trac.enlightenment.org/e/browser/trunk/imlib2/COPYING
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "IMLIB2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="INFO_ZIP")
    def INFO_ZIP(cls) -> "SpdxLicense":
        '''(experimental) Info-ZIP License.

        :see: http://www.info-zip.org/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "INFO_ZIP"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="INTEL")
    def INTEL(cls) -> "SpdxLicense":
        '''(experimental) Intel Open Source License.

        :see: https://opensource.org/licenses/Intel
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "INTEL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="INTEL_ACPI")
    def INTEL_ACPI(cls) -> "SpdxLicense":
        '''(experimental) Intel ACPI Software License Agreement.

        :see: https://fedoraproject.org/wiki/Licensing/Intel_ACPI_Software_License_Agreement
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "INTEL_ACPI"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="INTERBASE_1_0")
    def INTERBASE_1_0(cls) -> "SpdxLicense":
        '''(experimental) Interbase Public License v1.0.

        :see: https://web.archive.org/web/20060319014854/http://info.borland.com/devsupport/interbase/opensource/IPL.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "INTERBASE_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="IPA")
    def IPA(cls) -> "SpdxLicense":
        '''(experimental) IPA Font License.

        :see: https://opensource.org/licenses/IPA
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "IPA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="IPL_1_0")
    def IPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) IBM Public License v1.0.

        :see: https://opensource.org/licenses/IPL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "IPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ISC")
    def ISC(cls) -> "SpdxLicense":
        '''(experimental) ISC License.

        :see: https://www.isc.org/downloads/software-support-policy/isc-license/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ISC"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="JASPER_2_0")
    def JASPER_2_0(cls) -> "SpdxLicense":
        '''(experimental) JasPer License.

        :see: http://www.ece.uvic.ca/~mdadams/jasper/LICENSE
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "JASPER_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="JPNIC")
    def JPNIC(cls) -> "SpdxLicense":
        '''(experimental) Japan Network Information Center License.

        :see: https://gitlab.isc.org/isc-projects/bind9/blob/master/COPYRIGHT#L366
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "JPNIC"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="JSON")
    def JSON(cls) -> "SpdxLicense":
        '''(experimental) JSON License.

        :see: http://www.json.org/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "JSON"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LAL_1_2")
    def LAL_1_2(cls) -> "SpdxLicense":
        '''(experimental) Licence Art Libre 1.2.

        :see: http://artlibre.org/licence/lal/licence-art-libre-12/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LAL_1_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LAL_1_3")
    def LAL_1_3(cls) -> "SpdxLicense":
        '''(experimental) Licence Art Libre 1.3.

        :see: https://artlibre.org/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LAL_1_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LATEX2_E")
    def LATEX2_E(cls) -> "SpdxLicense":
        '''(experimental) Latex2e License.

        :see: https://fedoraproject.org/wiki/Licensing/Latex2e
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LATEX2_E"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LEPTONICA")
    def LEPTONICA(cls) -> "SpdxLicense":
        '''(experimental) Leptonica License.

        :see: https://fedoraproject.org/wiki/Licensing/Leptonica
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LEPTONICA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_2_0")
    def LGPL_2_0(cls) -> "SpdxLicense":
        '''(experimental) GNU Library General Public License v2 only.

        :see: https://www.gnu.org/licenses/old-licenses/lgpl-2.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_2_0_ONLY")
    def LGPL_2_0_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Library General Public License v2 only.

        :see: https://www.gnu.org/licenses/old-licenses/lgpl-2.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_2_0_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_2_0_OR_LATER")
    def LGPL_2_0_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Library General Public License v2 or later.

        :see: https://www.gnu.org/licenses/old-licenses/lgpl-2.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_2_0_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_2_0_PLUS")
    def LGPL_2_0_PLUS(cls) -> "SpdxLicense":
        '''(experimental) GNU Library General Public License v2 or later.

        :see: https://www.gnu.org/licenses/old-licenses/lgpl-2.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_2_0_PLUS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_2_1")
    def LGPL_2_1(cls) -> "SpdxLicense":
        '''(experimental) GNU Lesser General Public License v2.1 only.

        :see: https://www.gnu.org/licenses/old-licenses/lgpl-2.1-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_2_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_2_1_ONLY")
    def LGPL_2_1_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Lesser General Public License v2.1 only.

        :see: https://www.gnu.org/licenses/old-licenses/lgpl-2.1-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_2_1_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_2_1_OR_LATER")
    def LGPL_2_1_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Lesser General Public License v2.1 or later.

        :see: https://www.gnu.org/licenses/old-licenses/lgpl-2.1-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_2_1_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_2_1_PLUS")
    def LGPL_2_1_PLUS(cls) -> "SpdxLicense":
        '''(experimental) GNU Library General Public License v2.1 or later.

        :see: https://www.gnu.org/licenses/old-licenses/lgpl-2.1-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_2_1_PLUS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_3_0")
    def LGPL_3_0(cls) -> "SpdxLicense":
        '''(experimental) GNU Lesser General Public License v3.0 only.

        :see: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_3_0_ONLY")
    def LGPL_3_0_ONLY(cls) -> "SpdxLicense":
        '''(experimental) GNU Lesser General Public License v3.0 only.

        :see: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_3_0_ONLY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_3_0_OR_LATER")
    def LGPL_3_0_OR_LATER(cls) -> "SpdxLicense":
        '''(experimental) GNU Lesser General Public License v3.0 or later.

        :see: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_3_0_OR_LATER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPL_3_0_PLUS")
    def LGPL_3_0_PLUS(cls) -> "SpdxLicense":
        '''(experimental) GNU Lesser General Public License v3.0 or later.

        :see: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPL_3_0_PLUS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LGPLLR")
    def LGPLLR(cls) -> "SpdxLicense":
        '''(experimental) Lesser General Public License For Linguistic Resources.

        :see: http://www-igm.univ-mlv.fr/~unitex/lgpllr.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LGPLLR"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LIBPNG")
    def LIBPNG(cls) -> "SpdxLicense":
        '''(experimental) libpng License.

        :see: http://www.libpng.org/pub/png/src/libpng-LICENSE.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LIBPNG"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LIBPNG_2_0")
    def LIBPNG_2_0(cls) -> "SpdxLicense":
        '''(experimental) PNG Reference Library version 2.

        :see: http://www.libpng.org/pub/png/src/libpng-LICENSE.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LIBPNG_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LIBSELINUX_1_0")
    def LIBSELINUX_1_0(cls) -> "SpdxLicense":
        '''(experimental) libselinux public domain notice.

        :see: https://github.com/SELinuxProject/selinux/blob/master/libselinux/LICENSE
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LIBSELINUX_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LIBTIFF")
    def LIBTIFF(cls) -> "SpdxLicense":
        '''(experimental) libtiff License.

        :see: https://fedoraproject.org/wiki/Licensing/libtiff
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LIBTIFF"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LILIQ_P_1_1")
    def LILIQ_P_1_1(cls) -> "SpdxLicense":
        '''(experimental) Licence Libre du Québec – Permissive version 1.1.

        :see: https://forge.gouv.qc.ca/licence/fr/liliq-v1-1/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LILIQ_P_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LILIQ_R_1_1")
    def LILIQ_R_1_1(cls) -> "SpdxLicense":
        '''(experimental) Licence Libre du Québec – Réciprocité version 1.1.

        :see: https://www.forge.gouv.qc.ca/participez/licence-logicielle/licence-libre-du-quebec-liliq-en-francais/licence-libre-du-quebec-reciprocite-liliq-r-v1-1/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LILIQ_R_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LILIQ_RPLUS_1_1")
    def LILIQ_RPLUS_1_1(cls) -> "SpdxLicense":
        '''(experimental) Licence Libre du Québec – Réciprocité forte version 1.1.

        :see: https://www.forge.gouv.qc.ca/participez/licence-logicielle/licence-libre-du-quebec-liliq-en-francais/licence-libre-du-quebec-reciprocite-forte-liliq-r-v1-1/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LILIQ_RPLUS_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LINUX_OPENIB")
    def LINUX_OPENIB(cls) -> "SpdxLicense":
        '''(experimental) Linux Kernel Variant of OpenIB.org license.

        :see: https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/drivers/infiniband/core/sa.h
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LINUX_OPENIB"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LPL_1_0")
    def LPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Lucent Public License Version 1.0.

        :see: https://opensource.org/licenses/LPL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LPL_1_02")
    def LPL_1_02(cls) -> "SpdxLicense":
        '''(experimental) Lucent Public License v1.02.

        :see: http://plan9.bell-labs.com/plan9/license.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LPL_1_02"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LPPL_1_0")
    def LPPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) LaTeX Project Public License v1.0.

        :see: http://www.latex-project.org/lppl/lppl-1-0.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LPPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LPPL_1_1")
    def LPPL_1_1(cls) -> "SpdxLicense":
        '''(experimental) LaTeX Project Public License v1.1.

        :see: http://www.latex-project.org/lppl/lppl-1-1.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LPPL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LPPL_1_2")
    def LPPL_1_2(cls) -> "SpdxLicense":
        '''(experimental) LaTeX Project Public License v1.2.

        :see: http://www.latex-project.org/lppl/lppl-1-2.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LPPL_1_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LPPL_1_3A")
    def LPPL_1_3_A(cls) -> "SpdxLicense":
        '''(experimental) LaTeX Project Public License v1.3a.

        :see: http://www.latex-project.org/lppl/lppl-1-3a.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LPPL_1_3A"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="LPPL_1_3C")
    def LPPL_1_3_C(cls) -> "SpdxLicense":
        '''(experimental) LaTeX Project Public License v1.3c.

        :see: http://www.latex-project.org/lppl/lppl-1-3c.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "LPPL_1_3C"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MAKE_INDEX")
    def MAKE_INDEX(cls) -> "SpdxLicense":
        '''(experimental) MakeIndex License.

        :see: https://fedoraproject.org/wiki/Licensing/MakeIndex
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MAKE_INDEX"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MIR_O_S")
    def MIR_O_S(cls) -> "SpdxLicense":
        '''(experimental) The MirOS Licence.

        :see: https://opensource.org/licenses/MirOS
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MIR_O_S"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MIT")
    def MIT(cls) -> "SpdxLicense":
        '''(experimental) MIT License.

        :see: https://opensource.org/licenses/MIT
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MIT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MIT_0")
    def MIT_0(cls) -> "SpdxLicense":
        '''(experimental) MIT No Attribution.

        :see: https://github.com/aws/mit-0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MIT_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MIT_ADVERTISING")
    def MIT_ADVERTISING(cls) -> "SpdxLicense":
        '''(experimental) Enlightenment License (e16).

        :see: https://fedoraproject.org/wiki/Licensing/MIT_With_Advertising
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MIT_ADVERTISING"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MIT_CMU")
    def MIT_CMU(cls) -> "SpdxLicense":
        '''(experimental) CMU License.

        :see: https://fedoraproject.org/wiki/Licensing:MIT?rd=Licensing/MIT#CMU_Style
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MIT_CMU"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MIT_ENNA")
    def MIT_ENNA(cls) -> "SpdxLicense":
        '''(experimental) enna License.

        :see: https://fedoraproject.org/wiki/Licensing/MIT#enna
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MIT_ENNA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MIT_FEH")
    def MIT_FEH(cls) -> "SpdxLicense":
        '''(experimental) feh License.

        :see: https://fedoraproject.org/wiki/Licensing/MIT#feh
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MIT_FEH"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MIT_OPEN_GROUP")
    def MIT_OPEN_GROUP(cls) -> "SpdxLicense":
        '''(experimental) MIT Open Group variant.

        :see: https://gitlab.freedesktop.org/xorg/app/iceauth/-/blob/master/COPYING
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MIT_OPEN_GROUP"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MITNFA")
    def MITNFA(cls) -> "SpdxLicense":
        '''(experimental) MIT +no-false-attribs license.

        :see: https://fedoraproject.org/wiki/Licensing/MITNFA
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MITNFA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MOTOSOTO")
    def MOTOSOTO(cls) -> "SpdxLicense":
        '''(experimental) Motosoto License.

        :see: https://opensource.org/licenses/Motosoto
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MOTOSOTO"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MPICH2")
    def MPICH2(cls) -> "SpdxLicense":
        '''(experimental) mpich2 License.

        :see: https://fedoraproject.org/wiki/Licensing/MIT
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MPICH2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MPL_1_0")
    def MPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Mozilla Public License 1.0.

        :see: http://www.mozilla.org/MPL/MPL-1.0.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MPL_1_1")
    def MPL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Mozilla Public License 1.1.

        :see: http://www.mozilla.org/MPL/MPL-1.1.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MPL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MPL_2_0")
    def MPL_2_0(cls) -> "SpdxLicense":
        '''(experimental) Mozilla Public License 2.0.

        :see: http://www.mozilla.org/MPL/2.0/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MPL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MPL_2_0_NO_COPYLEFT_EXCEPTION")
    def MPL_2_0_NO_COPYLEFT_EXCEPTION(cls) -> "SpdxLicense":
        '''(experimental) Mozilla Public License 2.0 (no copyleft exception).

        :see: http://www.mozilla.org/MPL/2.0/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MPL_2_0_NO_COPYLEFT_EXCEPTION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MS_PL")
    def MS_PL(cls) -> "SpdxLicense":
        '''(experimental) Microsoft Public License.

        :see: http://www.microsoft.com/opensource/licenses.mspx
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MS_PL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MS_RL")
    def MS_RL(cls) -> "SpdxLicense":
        '''(experimental) Microsoft Reciprocal License.

        :see: http://www.microsoft.com/opensource/licenses.mspx
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MS_RL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MTLL")
    def MTLL(cls) -> "SpdxLicense":
        '''(experimental) Matrix Template Library License.

        :see: https://fedoraproject.org/wiki/Licensing/Matrix_Template_Library_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MTLL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MULANPSL_1_0")
    def MULANPSL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Mulan Permissive Software License, Version 1.

        :see: https://license.coscl.org.cn/MulanPSL/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MULANPSL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MULANPSL_2_0")
    def MULANPSL_2_0(cls) -> "SpdxLicense":
        '''(experimental) Mulan Permissive Software License, Version 2.

        :see: https://license.coscl.org.cn/MulanPSL2/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MULANPSL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MULTICS")
    def MULTICS(cls) -> "SpdxLicense":
        '''(experimental) Multics License.

        :see: https://opensource.org/licenses/Multics
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MULTICS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MUP")
    def MUP(cls) -> "SpdxLicense":
        '''(experimental) Mup License.

        :see: https://fedoraproject.org/wiki/Licensing/Mup
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "MUP"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NASA_1_3")
    def NASA_1_3(cls) -> "SpdxLicense":
        '''(experimental) NASA Open Source Agreement 1.3.

        :see: http://ti.arc.nasa.gov/opensource/nosa/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NASA_1_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NAUMEN")
    def NAUMEN(cls) -> "SpdxLicense":
        '''(experimental) Naumen Public License.

        :see: https://opensource.org/licenses/Naumen
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NAUMEN"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NBPL_1_0")
    def NBPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Net Boolean Public License v1.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=37b4b3f6cc4bf34e1d3dec61e69914b9819d8894
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NBPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NCGL_UK_2_0")
    def NCGL_UK_2_0(cls) -> "SpdxLicense":
        '''(experimental) Non-Commercial Government Licence.

        :see: https://github.com/spdx/license-list-XML/blob/master/src/Apache-2.0.xml
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NCGL_UK_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NCSA")
    def NCSA(cls) -> "SpdxLicense":
        '''(experimental) University of Illinois/NCSA Open Source License.

        :see: http://otm.illinois.edu/uiuc_openSource
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NCSA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NET_CD_F")
    def NET_CD_F(cls) -> "SpdxLicense":
        '''(experimental) NetCDF license.

        :see: http://www.unidata.ucar.edu/software/netcdf/copyright.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NET_CD_F"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NET_SNMP")
    def NET_SNMP(cls) -> "SpdxLicense":
        '''(experimental) Net-SNMP License.

        :see: http://net-snmp.sourceforge.net/about/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NET_SNMP"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NEWSLETR")
    def NEWSLETR(cls) -> "SpdxLicense":
        '''(experimental) Newsletr License.

        :see: https://fedoraproject.org/wiki/Licensing/Newsletr
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NEWSLETR"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NGPL")
    def NGPL(cls) -> "SpdxLicense":
        '''(experimental) Nethack General Public License.

        :see: https://opensource.org/licenses/NGPL
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NGPL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NIST_PD")
    def NIST_PD(cls) -> "SpdxLicense":
        '''(experimental) NIST Public Domain Notice.

        :see: https://github.com/tcheneau/simpleRPL/blob/e645e69e38dd4e3ccfeceb2db8cba05b7c2e0cd3/LICENSE.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NIST_PD"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NIST_PD_FALLBACK")
    def NIST_PD_FALLBACK(cls) -> "SpdxLicense":
        '''(experimental) NIST Public Domain Notice with license fallback.

        :see: https://github.com/usnistgov/jsip/blob/59700e6926cbe96c5cdae897d9a7d2656b42abe3/LICENSE
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NIST_PD_FALLBACK"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NLOD_1_0")
    def NLOD_1_0(cls) -> "SpdxLicense":
        '''(experimental) Norwegian Licence for Open Government Data.

        :see: http://data.norge.no/nlod/en/1.0
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NLOD_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NLPL")
    def NLPL(cls) -> "SpdxLicense":
        '''(experimental) No Limit Public License.

        :see: https://fedoraproject.org/wiki/Licensing/NLPL
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NLPL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NOKIA")
    def NOKIA(cls) -> "SpdxLicense":
        '''(experimental) Nokia Open Source License.

        :see: https://opensource.org/licenses/nokia
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NOKIA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NOSL")
    def NOSL(cls) -> "SpdxLicense":
        '''(experimental) Netizen Open Source License.

        :see: http://bits.netizen.com.au/licenses/NOSL/nosl.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NOSL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NOWEB")
    def NOWEB(cls) -> "SpdxLicense":
        '''(experimental) Noweb License.

        :see: https://fedoraproject.org/wiki/Licensing/Noweb
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NOWEB"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NPL_1_0")
    def NPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Netscape Public License v1.0.

        :see: http://www.mozilla.org/MPL/NPL/1.0/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NPL_1_1")
    def NPL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Netscape Public License v1.1.

        :see: http://www.mozilla.org/MPL/NPL/1.1/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NPL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NPOSL_3_0")
    def NPOSL_3_0(cls) -> "SpdxLicense":
        '''(experimental) Non-Profit Open Software License 3.0.

        :see: https://opensource.org/licenses/NOSL3.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NPOSL_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NRL")
    def NRL(cls) -> "SpdxLicense":
        '''(experimental) NRL License.

        :see: http://web.mit.edu/network/isakmp/nrllicense.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NRL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NTP")
    def NTP(cls) -> "SpdxLicense":
        '''(experimental) NTP License.

        :see: https://opensource.org/licenses/NTP
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NTP"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NTP_0")
    def NTP_0(cls) -> "SpdxLicense":
        '''(experimental) NTP No Attribution.

        :see: https://github.com/tytso/e2fsprogs/blob/master/lib/et/et_name.c
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NTP_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NUNIT")
    def NUNIT(cls) -> "SpdxLicense":
        '''(experimental) Nunit License.

        :see: https://fedoraproject.org/wiki/Licensing/Nunit
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "NUNIT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="O_UDA_1_0")
    def O_UDA_1_0(cls) -> "SpdxLicense":
        '''(experimental) Open Use of Data Agreement v1.0.

        :see: https://github.com/microsoft/Open-Use-of-Data-Agreement/blob/v1.0/O-UDA-1.0.md
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "O_UDA_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OCCT_PL")
    def OCCT_PL(cls) -> "SpdxLicense":
        '''(experimental) Open CASCADE Technology Public License.

        :see: http://www.opencascade.com/content/occt-public-license
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OCCT_PL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OCLC_2_0")
    def OCLC_2_0(cls) -> "SpdxLicense":
        '''(experimental) OCLC Research Public License 2.0.

        :see: http://www.oclc.org/research/activities/software/license/v2final.htm
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OCLC_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ODBL_1_0")
    def ODBL_1_0(cls) -> "SpdxLicense":
        '''(experimental) ODC Open Database License v1.0.

        :see: http://www.opendatacommons.org/licenses/odbl/1.0/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ODBL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ODC_BY_1_0")
    def ODC_BY_1_0(cls) -> "SpdxLicense":
        '''(experimental) Open Data Commons Attribution License v1.0.

        :see: https://opendatacommons.org/licenses/by/1.0/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ODC_BY_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OFL_1_0")
    def OFL_1_0(cls) -> "SpdxLicense":
        '''(experimental) SIL Open Font License 1.0.

        :see: http://scripts.sil.org/cms/scripts/page.php?item_id=OFL10_web
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OFL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OFL_1_0_NO_RFN")
    def OFL_1_0_NO_RFN(cls) -> "SpdxLicense":
        '''(experimental) SIL Open Font License 1.0 with no Reserved Font Name.

        :see: http://scripts.sil.org/cms/scripts/page.php?item_id=OFL10_web
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OFL_1_0_NO_RFN"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OFL_1_0_RFN")
    def OFL_1_0_RFN(cls) -> "SpdxLicense":
        '''(experimental) SIL Open Font License 1.0 with Reserved Font Name.

        :see: http://scripts.sil.org/cms/scripts/page.php?item_id=OFL10_web
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OFL_1_0_RFN"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OFL_1_1")
    def OFL_1_1(cls) -> "SpdxLicense":
        '''(experimental) SIL Open Font License 1.1.

        :see: http://scripts.sil.org/cms/scripts/page.php?item_id=OFL_web
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OFL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OFL_1_1_NO_RFN")
    def OFL_1_1_NO_RFN(cls) -> "SpdxLicense":
        '''(experimental) SIL Open Font License 1.1 with no Reserved Font Name.

        :see: http://scripts.sil.org/cms/scripts/page.php?item_id=OFL_web
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OFL_1_1_NO_RFN"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OFL_1_1_RFN")
    def OFL_1_1_RFN(cls) -> "SpdxLicense":
        '''(experimental) SIL Open Font License 1.1 with Reserved Font Name.

        :see: http://scripts.sil.org/cms/scripts/page.php?item_id=OFL_web
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OFL_1_1_RFN"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OGC_1_0")
    def OGC_1_0(cls) -> "SpdxLicense":
        '''(experimental) OGC Software License, Version 1.0.

        :see: https://www.ogc.org/ogc/software/1.0
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OGC_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OGL_CANADA_2_0")
    def OGL_CANADA_2_0(cls) -> "SpdxLicense":
        '''(experimental) Open Government Licence - Canada.

        :see: https://open.canada.ca/en/open-government-licence-canada
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OGL_CANADA_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OGL_UK_1_0")
    def OGL_UK_1_0(cls) -> "SpdxLicense":
        '''(experimental) Open Government Licence v1.0.

        :see: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/1/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OGL_UK_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OGL_UK_2_0")
    def OGL_UK_2_0(cls) -> "SpdxLicense":
        '''(experimental) Open Government Licence v2.0.

        :see: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OGL_UK_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OGL_UK_3_0")
    def OGL_UK_3_0(cls) -> "SpdxLicense":
        '''(experimental) Open Government Licence v3.0.

        :see: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OGL_UK_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OGTSL")
    def OGTSL(cls) -> "SpdxLicense":
        '''(experimental) Open Group Test Suite License.

        :see: http://www.opengroup.org/testing/downloads/The_Open_Group_TSL.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OGTSL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_1_1")
    def OLDAP_1_1(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v1.1.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=806557a5ad59804ef3a44d5abfbe91d706b0791f
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_1_2")
    def OLDAP_1_2(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v1.2.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=42b0383c50c299977b5893ee695cf4e486fb0dc7
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_1_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_1_3")
    def OLDAP_1_3(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v1.3.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=e5f8117f0ce088d0bd7a8e18ddf37eaa40eb09b1
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_1_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_1_4")
    def OLDAP_1_4(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v1.4.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=c9f95c2f3f2ffb5e0ae55fe7388af75547660941
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_1_4"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_0")
    def OLDAP_2_0(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.0 (or possibly 2.0A and 2.0B).

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=cbf50f4e1185a21abd4c0a54d3f4341fe28f36ea
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_0_1")
    def OLDAP_2_0_1(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.0.1.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=b6d68acd14e51ca3aab4428bf26522aa74873f0e
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_0_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_1")
    def OLDAP_2_1(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.1.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=b0d176738e96a0d3b9f85cb51e140a86f21be715
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_2")
    def OLDAP_2_2(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.2.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=470b0c18ec67621c85881b2733057fecf4a1acc3
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_2_1")
    def OLDAP_2_2_1(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.2.1.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=4bc786f34b50aa301be6f5600f58a980070f481e
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_2_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_2_2")
    def OLDAP_2_2_2(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License 2.2.2.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=df2cc1e21eb7c160695f5b7cffd6296c151ba188
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_2_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_3")
    def OLDAP_2_3(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.3.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=d32cf54a32d581ab475d23c810b0a7fbaf8d63c3
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_4")
    def OLDAP_2_4(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.4.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=cd1284c4a91a8a380d904eee68d1583f989ed386
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_4"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_5")
    def OLDAP_2_5(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.5.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=6852b9d90022e8593c98205413380536b1b5a7cf
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_6")
    def OLDAP_2_6(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.6.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=1cae062821881f41b73012ba816434897abf4205
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_6"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_7")
    def OLDAP_2_7(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.7.

        :see: http://www.openldap.org/devel/gitweb.cgi?p=openldap.git;a=blob;f=LICENSE;hb=47c2415c1df81556eeb39be6cad458ef87c534a2
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_7"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OLDAP_2_8")
    def OLDAP_2_8(cls) -> "SpdxLicense":
        '''(experimental) Open LDAP Public License v2.8.

        :see: http://www.openldap.org/software/release/license.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OLDAP_2_8"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OML")
    def OML(cls) -> "SpdxLicense":
        '''(experimental) Open Market License.

        :see: https://fedoraproject.org/wiki/Licensing/Open_Market_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OML"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OPEN_SS_L")
    def OPEN_SS_L(cls) -> "SpdxLicense":
        '''(experimental) OpenSSL License.

        :see: http://www.openssl.org/source/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OPEN_SS_L"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OPL_1_0")
    def OPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Open Public License v1.0.

        :see: http://old.koalateam.com/jackaroo/OPL_1_0.TXT
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OSET_PL_2_1")
    def OSET_PL_2_1(cls) -> "SpdxLicense":
        '''(experimental) OSET Public License version 2.1.

        :see: http://www.osetfoundation.org/public-license
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OSET_PL_2_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OSL_1_0")
    def OSL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Open Software License 1.0.

        :see: https://opensource.org/licenses/OSL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OSL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OSL_1_1")
    def OSL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Open Software License 1.1.

        :see: https://fedoraproject.org/wiki/Licensing/OSL1.1
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OSL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OSL_2_0")
    def OSL_2_0(cls) -> "SpdxLicense":
        '''(experimental) Open Software License 2.0.

        :see: http://web.archive.org/web/20041020171434/http://www.rosenlaw.com/osl2.0.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OSL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OSL_2_1")
    def OSL_2_1(cls) -> "SpdxLicense":
        '''(experimental) Open Software License 2.1.

        :see: http://web.archive.org/web/20050212003940/http://www.rosenlaw.com/osl21.htm
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OSL_2_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="OSL_3_0")
    def OSL_3_0(cls) -> "SpdxLicense":
        '''(experimental) Open Software License 3.0.

        :see: https://web.archive.org/web/20120101081418/http://rosenlaw.com:80/OSL3.0.htm
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "OSL_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PARITY_6_0_0")
    def PARITY_6_0_0(cls) -> "SpdxLicense":
        '''(experimental) The Parity Public License 6.0.0.

        :see: https://paritylicense.com/versions/6.0.0.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "PARITY_6_0_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PARITY_7_0_0")
    def PARITY_7_0_0(cls) -> "SpdxLicense":
        '''(experimental) The Parity Public License 7.0.0.

        :see: https://paritylicense.com/versions/7.0.0.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "PARITY_7_0_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PDDL_1_0")
    def PDDL_1_0(cls) -> "SpdxLicense":
        '''(experimental) ODC Public Domain Dedication & License 1.0.

        :see: http://opendatacommons.org/licenses/pddl/1.0/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "PDDL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PHP_3_0")
    def PHP_3_0(cls) -> "SpdxLicense":
        '''(experimental) PHP License v3.0.

        :see: http://www.php.net/license/3_0.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "PHP_3_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PHP_3_01")
    def PHP_3_01(cls) -> "SpdxLicense":
        '''(experimental) PHP License v3.01.

        :see: http://www.php.net/license/3_01.txt
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "PHP_3_01"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PLEXUS")
    def PLEXUS(cls) -> "SpdxLicense":
        '''(experimental) Plexus Classworlds License.

        :see: https://fedoraproject.org/wiki/Licensing/Plexus_Classworlds_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "PLEXUS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="POLYFORM_NONCOMMERCIAL_1_0_0")
    def POLYFORM_NONCOMMERCIAL_1_0_0(cls) -> "SpdxLicense":
        '''(experimental) PolyForm Noncommercial License 1.0.0.

        :see: https://polyformproject.org/licenses/noncommercial/1.0.0
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "POLYFORM_NONCOMMERCIAL_1_0_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="POLYFORM_SMALL_BUSINESS_1_0_0")
    def POLYFORM_SMALL_BUSINESS_1_0_0(cls) -> "SpdxLicense":
        '''(experimental) PolyForm Small Business License 1.0.0.

        :see: https://polyformproject.org/licenses/small-business/1.0.0
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "POLYFORM_SMALL_BUSINESS_1_0_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="POSTGRE_SQ_L")
    def POSTGRE_SQ_L(cls) -> "SpdxLicense":
        '''(experimental) PostgreSQL License.

        :see: http://www.postgresql.org/about/licence
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "POSTGRE_SQ_L"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PSF_2_0")
    def PSF_2_0(cls) -> "SpdxLicense":
        '''(experimental) Python Software Foundation License 2.0.

        :see: https://opensource.org/licenses/Python-2.0
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "PSF_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PSFRAG")
    def PSFRAG(cls) -> "SpdxLicense":
        '''(experimental) psfrag License.

        :see: https://fedoraproject.org/wiki/Licensing/psfrag
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "PSFRAG"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PSUTILS")
    def PSUTILS(cls) -> "SpdxLicense":
        '''(experimental) psutils License.

        :see: https://fedoraproject.org/wiki/Licensing/psutils
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "PSUTILS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PYTHON_2_0")
    def PYTHON_2_0(cls) -> "SpdxLicense":
        '''(experimental) Python License 2.0.

        :see: https://opensource.org/licenses/Python-2.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "PYTHON_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="QHULL")
    def QHULL(cls) -> "SpdxLicense":
        '''(experimental) Qhull License.

        :see: https://fedoraproject.org/wiki/Licensing/Qhull
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "QHULL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="QPL_1_0")
    def QPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Q Public License 1.0.

        :see: http://doc.qt.nokia.com/3.3/license.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "QPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RDISC")
    def RDISC(cls) -> "SpdxLicense":
        '''(experimental) Rdisc License.

        :see: https://fedoraproject.org/wiki/Licensing/Rdisc_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "RDISC"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RHECOS_1_1")
    def RHECOS_1_1(cls) -> "SpdxLicense":
        '''(experimental) Red Hat eCos Public License v1.1.

        :see: http://ecos.sourceware.org/old-license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "RHECOS_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RPL_1_1")
    def RPL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Reciprocal Public License 1.1.

        :see: https://opensource.org/licenses/RPL-1.1
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "RPL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RPL_1_5")
    def RPL_1_5(cls) -> "SpdxLicense":
        '''(experimental) Reciprocal Public License 1.5.

        :see: https://opensource.org/licenses/RPL-1.5
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "RPL_1_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RPSL_1_0")
    def RPSL_1_0(cls) -> "SpdxLicense":
        '''(experimental) RealNetworks Public Source License v1.0.

        :see: https://helixcommunity.org/content/rpsl
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "RPSL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RSA_MD")
    def RSA_MD(cls) -> "SpdxLicense":
        '''(experimental) RSA Message-Digest License.

        :see: http://www.faqs.org/rfcs/rfc1321.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "RSA_MD"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RSCPL")
    def RSCPL(cls) -> "SpdxLicense":
        '''(experimental) Ricoh Source Code Public License.

        :see: http://wayback.archive.org/web/20060715140826/http://www.risource.org/RPL/RPL-1.0A.shtml
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "RSCPL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RUBY")
    def RUBY(cls) -> "SpdxLicense":
        '''(experimental) Ruby License.

        :see: http://www.ruby-lang.org/en/LICENSE.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "RUBY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SAX_PD")
    def SAX_PD(cls) -> "SpdxLicense":
        '''(experimental) Sax Public Domain Notice.

        :see: http://www.saxproject.org/copying.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SAX_PD"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SAXPATH")
    def SAXPATH(cls) -> "SpdxLicense":
        '''(experimental) Saxpath License.

        :see: https://fedoraproject.org/wiki/Licensing/Saxpath_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SAXPATH"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SCEA")
    def SCEA(cls) -> "SpdxLicense":
        '''(experimental) SCEA Shared Source License.

        :see: http://research.scea.com/scea_shared_source_license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SCEA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SENDMAIL")
    def SENDMAIL(cls) -> "SpdxLicense":
        '''(experimental) Sendmail License.

        :see: http://www.sendmail.com/pdfs/open_source/sendmail_license.pdf
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SENDMAIL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SENDMAIL_8_23")
    def SENDMAIL_8_23(cls) -> "SpdxLicense":
        '''(experimental) Sendmail License 8.23.

        :see: https://www.proofpoint.com/sites/default/files/sendmail-license.pdf
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SENDMAIL_8_23"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SGI_B_1_0")
    def SGI_B_1_0(cls) -> "SpdxLicense":
        '''(experimental) SGI Free Software License B v1.0.

        :see: http://oss.sgi.com/projects/FreeB/SGIFreeSWLicB.1.0.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SGI_B_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SGI_B_1_1")
    def SGI_B_1_1(cls) -> "SpdxLicense":
        '''(experimental) SGI Free Software License B v1.1.

        :see: http://oss.sgi.com/projects/FreeB/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SGI_B_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SGI_B_2_0")
    def SGI_B_2_0(cls) -> "SpdxLicense":
        '''(experimental) SGI Free Software License B v2.0.

        :see: http://oss.sgi.com/projects/FreeB/SGIFreeSWLicB.2.0.pdf
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SGI_B_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SHL_0_5")
    def SHL_0_5(cls) -> "SpdxLicense":
        '''(experimental) Solderpad Hardware License v0.5.

        :see: https://solderpad.org/licenses/SHL-0.5/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SHL_0_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SHL_0_51")
    def SHL_0_51(cls) -> "SpdxLicense":
        '''(experimental) Solderpad Hardware License, Version 0.51.

        :see: https://solderpad.org/licenses/SHL-0.51/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SHL_0_51"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SIMPL_2_0")
    def SIMPL_2_0(cls) -> "SpdxLicense":
        '''(experimental) Simple Public License 2.0.

        :see: https://opensource.org/licenses/SimPL-2.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SIMPL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SISSL")
    def SISSL(cls) -> "SpdxLicense":
        '''(experimental) Sun Industry Standards Source License v1.1.

        :see: http://www.openoffice.org/licenses/sissl_license.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SISSL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SISSL_1_2")
    def SISSL_1_2(cls) -> "SpdxLicense":
        '''(experimental) Sun Industry Standards Source License v1.2.

        :see: http://gridscheduler.sourceforge.net/Gridengine_SISSL_license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SISSL_1_2"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SLEEPYCAT")
    def SLEEPYCAT(cls) -> "SpdxLicense":
        '''(experimental) Sleepycat License.

        :see: https://opensource.org/licenses/Sleepycat
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SLEEPYCAT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SMLNJ")
    def SMLNJ(cls) -> "SpdxLicense":
        '''(experimental) Standard ML of New Jersey License.

        :see: https://www.smlnj.org/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SMLNJ"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SMPPL")
    def SMPPL(cls) -> "SpdxLicense":
        '''(experimental) Secure Messaging Protocol Public License.

        :see: https://github.com/dcblake/SMP/blob/master/Documentation/License.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SMPPL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SNIA")
    def SNIA(cls) -> "SpdxLicense":
        '''(experimental) SNIA Public License 1.1.

        :see: https://fedoraproject.org/wiki/Licensing/SNIA_Public_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SNIA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SPENCER_86")
    def SPENCER_86(cls) -> "SpdxLicense":
        '''(experimental) Spencer License 86.

        :see: https://fedoraproject.org/wiki/Licensing/Henry_Spencer_Reg-Ex_Library_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SPENCER_86"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SPENCER_94")
    def SPENCER_94(cls) -> "SpdxLicense":
        '''(experimental) Spencer License 94.

        :see: https://fedoraproject.org/wiki/Licensing/Henry_Spencer_Reg-Ex_Library_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SPENCER_94"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SPENCER_99")
    def SPENCER_99(cls) -> "SpdxLicense":
        '''(experimental) Spencer License 99.

        :see: http://www.opensource.apple.com/source/tcl/tcl-5/tcl/generic/regfronts.c
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SPENCER_99"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SPL_1_0")
    def SPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Sun Public License v1.0.

        :see: https://opensource.org/licenses/SPL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SSH_OPENSSH")
    def SSH_OPENSSH(cls) -> "SpdxLicense":
        '''(experimental) SSH OpenSSH license.

        :see: https://github.com/openssh/openssh-portable/blob/1b11ea7c58cd5c59838b5fa574cd456d6047b2d4/LICENCE#L10
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SSH_OPENSSH"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SSH_SHORT")
    def SSH_SHORT(cls) -> "SpdxLicense":
        '''(experimental) SSH short notice.

        :see: https://github.com/openssh/openssh-portable/blob/1b11ea7c58cd5c59838b5fa574cd456d6047b2d4/pathnames.h
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SSH_SHORT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SSPL_1_0")
    def SSPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Server Side Public License, v 1.

        :see: https://www.mongodb.com/licensing/server-side-public-license
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SSPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="STANDARDML_NJ")
    def STANDARDML_NJ(cls) -> "SpdxLicense":
        '''(experimental) Standard ML of New Jersey License.

        :see: http://www.smlnj.org//license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "STANDARDML_NJ"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SUGARCRM_1_1_3")
    def SUGARCRM_1_1_3(cls) -> "SpdxLicense":
        '''(experimental) SugarCRM Public License v1.1.3.

        :see: http://www.sugarcrm.com/crm/SPL
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SUGARCRM_1_1_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SWL")
    def SWL(cls) -> "SpdxLicense":
        '''(experimental) Scheme Widget Library (SWL) Software License Agreement.

        :see: https://fedoraproject.org/wiki/Licensing/SWL
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "SWL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TAPR_OHL_1_0")
    def TAPR_OHL_1_0(cls) -> "SpdxLicense":
        '''(experimental) TAPR Open Hardware License v1.0.

        :see: https://www.tapr.org/OHL
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "TAPR_OHL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TCL")
    def TCL(cls) -> "SpdxLicense":
        '''(experimental) TCL/TK License.

        :see: http://www.tcl.tk/software/tcltk/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "TCL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TCP_WRAPPERS")
    def TCP_WRAPPERS(cls) -> "SpdxLicense":
        '''(experimental) TCP Wrappers License.

        :see: http://rc.quest.com/topics/openssh/license.php#tcpwrappers
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "TCP_WRAPPERS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TMATE")
    def TMATE(cls) -> "SpdxLicense":
        '''(experimental) TMate Open Source License.

        :see: http://svnkit.com/license.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "TMATE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TORQUE_1_1")
    def TORQUE_1_1(cls) -> "SpdxLicense":
        '''(experimental) TORQUE v2.5+ Software License v1.1.

        :see: https://fedoraproject.org/wiki/Licensing/TORQUEv1.1
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "TORQUE_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TOSL")
    def TOSL(cls) -> "SpdxLicense":
        '''(experimental) Trusster Open Source License.

        :see: https://fedoraproject.org/wiki/Licensing/TOSL
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "TOSL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TU_BERLIN_1_0")
    def TU_BERLIN_1_0(cls) -> "SpdxLicense":
        '''(experimental) Technische Universitaet Berlin License 1.0.

        :see: https://github.com/swh/ladspa/blob/7bf6f3799fdba70fda297c2d8fd9f526803d9680/gsm/COPYRIGHT
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "TU_BERLIN_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TU_BERLIN_2_0")
    def TU_BERLIN_2_0(cls) -> "SpdxLicense":
        '''(experimental) Technische Universitaet Berlin License 2.0.

        :see: https://github.com/CorsixTH/deps/blob/fd339a9f526d1d9c9f01ccf39e438a015da50035/licences/libgsm.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "TU_BERLIN_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="UCL_1_0")
    def UCL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Upstream Compatibility License v1.0.

        :see: https://opensource.org/licenses/UCL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "UCL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="UNICODE_DFS_2015")
    def UNICODE_DFS_2015(cls) -> "SpdxLicense":
        '''(experimental) Unicode License Agreement - Data Files and Software (2015).

        :see: https://web.archive.org/web/20151224134844/http://unicode.org/copyright.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "UNICODE_DFS_2015"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="UNICODE_DFS_2016")
    def UNICODE_DFS_2016(cls) -> "SpdxLicense":
        '''(experimental) Unicode License Agreement - Data Files and Software (2016).

        :see: http://www.unicode.org/copyright.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "UNICODE_DFS_2016"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="UNICODE_TOU")
    def UNICODE_TOU(cls) -> "SpdxLicense":
        '''(experimental) Unicode Terms of Use.

        :see: http://www.unicode.org/copyright.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "UNICODE_TOU"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="UNLICENSE")
    def UNLICENSE(cls) -> "SpdxLicense":
        '''(experimental) The Unlicense.

        :see: https://unlicense.org/
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "UNLICENSE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="UNLICENSED")
    def UNLICENSED(cls) -> "SpdxLicense":
        '''(experimental) Packages that have not been licensed.

        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "UNLICENSED"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="UPL_1_0")
    def UPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Universal Permissive License v1.0.

        :see: https://opensource.org/licenses/UPL
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "UPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="VIM")
    def VIM(cls) -> "SpdxLicense":
        '''(experimental) Vim License.

        :see: http://vimdoc.sourceforge.net/htmldoc/uganda.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "VIM"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="VOSTROM")
    def VOSTROM(cls) -> "SpdxLicense":
        '''(experimental) VOSTROM Public License for Open Source.

        :see: https://fedoraproject.org/wiki/Licensing/VOSTROM
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "VOSTROM"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="VSL_1_0")
    def VSL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Vovida Software License v1.0.

        :see: https://opensource.org/licenses/VSL-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "VSL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="W3_C")
    def W3_C(cls) -> "SpdxLicense":
        '''(experimental) W3C Software Notice and License (2002-12-31).

        :see: http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "W3_C"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="W3C_19980720")
    def W3_C_19980720(cls) -> "SpdxLicense":
        '''(experimental) W3C Software Notice and License (1998-07-20).

        :see: http://www.w3.org/Consortium/Legal/copyright-software-19980720.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "W3C_19980720"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="W3C_20150513")
    def W3_C_20150513(cls) -> "SpdxLicense":
        '''(experimental) W3C Software Notice and Document License (2015-05-13).

        :see: https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "W3C_20150513"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="WATCOM_1_0")
    def WATCOM_1_0(cls) -> "SpdxLicense":
        '''(experimental) Sybase Open Watcom Public License 1.0.

        :see: https://opensource.org/licenses/Watcom-1.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "WATCOM_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="WSUIPA")
    def WSUIPA(cls) -> "SpdxLicense":
        '''(experimental) Wsuipa License.

        :see: https://fedoraproject.org/wiki/Licensing/Wsuipa
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "WSUIPA"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="WTFPL")
    def WTFPL(cls) -> "SpdxLicense":
        '''(experimental) Do What The F*ck You Want To Public License.

        :see: http://www.wtfpl.net/about/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "WTFPL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="WX_WINDOWS")
    def WX_WINDOWS(cls) -> "SpdxLicense":
        '''(experimental) wxWindows Library License.

        :see: https://opensource.org/licenses/WXwindows
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "WX_WINDOWS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="X11")
    def X11(cls) -> "SpdxLicense":
        '''(experimental) X11 License.

        :see: http://www.xfree86.org/3.3.6/COPYRIGHT2.html#3
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "X11"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="XEROX")
    def XEROX(cls) -> "SpdxLicense":
        '''(experimental) Xerox License.

        :see: https://fedoraproject.org/wiki/Licensing/Xerox
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "XEROX"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="XFREE86_1_1")
    def XFREE86_1_1(cls) -> "SpdxLicense":
        '''(experimental) XFree86 License 1.1.

        :see: http://www.xfree86.org/current/LICENSE4.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "XFREE86_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="XINETD")
    def XINETD(cls) -> "SpdxLicense":
        '''(experimental) xinetd License.

        :see: https://fedoraproject.org/wiki/Licensing/Xinetd_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "XINETD"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="XNET")
    def XNET(cls) -> "SpdxLicense":
        '''(experimental) X.Net License.

        :see: https://opensource.org/licenses/Xnet
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "XNET"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="XPP")
    def XPP(cls) -> "SpdxLicense":
        '''(experimental) XPP License.

        :see: https://fedoraproject.org/wiki/Licensing/xpp
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "XPP"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="XSKAT")
    def XSKAT(cls) -> "SpdxLicense":
        '''(experimental) XSkat License.

        :see: https://fedoraproject.org/wiki/Licensing/XSkat_License
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "XSKAT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="YPL_1_0")
    def YPL_1_0(cls) -> "SpdxLicense":
        '''(experimental) Yahoo!

        Public License v1.0

        :see: http://www.zimbra.com/license/yahoo_public_license_1.0.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "YPL_1_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="YPL_1_1")
    def YPL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Yahoo!

        Public License v1.1

        :see: http://www.zimbra.com/license/yahoo_public_license_1.1.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "YPL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZED")
    def ZED(cls) -> "SpdxLicense":
        '''(experimental) Zed License.

        :see: https://fedoraproject.org/wiki/Licensing/Zed
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ZED"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZEND_2_0")
    def ZEND_2_0(cls) -> "SpdxLicense":
        '''(experimental) Zend License v2.0.

        :see: https://web.archive.org/web/20130517195954/http://www.zend.com/license/2_00.txt
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ZEND_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZERO_BSD")
    def ZERO_BSD(cls) -> "SpdxLicense":
        '''(experimental) BSD Zero Clause License.

        :see: http://landley.net/toybox/license.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ZERO_BSD"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZIMBRA_1_3")
    def ZIMBRA_1_3(cls) -> "SpdxLicense":
        '''(experimental) Zimbra Public License v1.3.

        :see: http://web.archive.org/web/20100302225219/http://www.zimbra.com/license/zimbra-public-license-1-3.html
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ZIMBRA_1_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZIMBRA_1_4")
    def ZIMBRA_1_4(cls) -> "SpdxLicense":
        '''(experimental) Zimbra Public License v1.4.

        :see: http://www.zimbra.com/legal/zimbra-public-license-1-4
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ZIMBRA_1_4"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZLIB")
    def ZLIB(cls) -> "SpdxLicense":
        '''(experimental) zlib License.

        :see: http://www.zlib.net/zlib_license.html
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ZLIB"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZLIB_ACKNOWLEDGEMENT")
    def ZLIB_ACKNOWLEDGEMENT(cls) -> "SpdxLicense":
        '''(experimental) zlib/libpng License with Acknowledgement.

        :see: https://fedoraproject.org/wiki/Licensing/ZlibWithAcknowledgement
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ZLIB_ACKNOWLEDGEMENT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZPL_1_1")
    def ZPL_1_1(cls) -> "SpdxLicense":
        '''(experimental) Zope Public License 1.1.

        :see: http://old.zope.org/Resources/License/ZPL-1.1
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ZPL_1_1"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZPL_2_0")
    def ZPL_2_0(cls) -> "SpdxLicense":
        '''(experimental) Zope Public License 2.0.

        :see: http://old.zope.org/Resources/License/ZPL-2.0
        :stability: experimental
        :osiApproved: true
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ZPL_2_0"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZPL_2_1")
    def ZPL_2_1(cls) -> "SpdxLicense":
        '''(experimental) Zope Public License 2.1.

        :see: http://old.zope.org/Resources/ZPL/
        :stability: experimental
        '''
        return typing.cast("SpdxLicense", jsii.sget(cls, "ZPL_2_1"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "id"))


class TagCondition(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="construct-hub.TagCondition",
):
    '''(experimental) Condition for applying a custom tag to a package.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="and") # type: ignore[misc]
    @builtins.classmethod
    def and_(cls, *conds: "TagCondition") -> "TagCondition":
        '''(experimental) Create an && condition which applies only when all condition arguments are true.

        :param conds: -

        :stability: experimental
        '''
        return typing.cast("TagCondition", jsii.sinvoke(cls, "and", [*conds]))

    @jsii.member(jsii_name="field") # type: ignore[misc]
    @builtins.classmethod
    def field(cls, *keys: builtins.str) -> "TagConditionField":
        '''(experimental) Target a field within the ``package.json`` to assert against. Nested fields can be accessed by passing multiple keys. ``TagCondition.field('key1', 'key2')`` will access ``packageJson?.key1?.key2``.

        :param keys: -

        :stability: experimental
        '''
        return typing.cast("TagConditionField", jsii.sinvoke(cls, "field", [*keys]))

    @jsii.member(jsii_name="not") # type: ignore[misc]
    @builtins.classmethod
    def not_(cls, *conds: "TagCondition") -> "TagCondition":
        '''(experimental) Create a !

        condition which applies if the condition argument is false

        :param conds: -

        :stability: experimental
        '''
        return typing.cast("TagCondition", jsii.sinvoke(cls, "not", [*conds]))

    @jsii.member(jsii_name="or") # type: ignore[misc]
    @builtins.classmethod
    def or_(cls, *conds: "TagCondition") -> "TagCondition":
        '''(experimental) Create an || condition which applies if any of the condition arguments are true.

        :param conds: -

        :stability: experimental
        '''
        return typing.cast("TagCondition", jsii.sinvoke(cls, "or", [*conds]))

    @jsii.member(jsii_name="readme") # type: ignore[misc]
    @builtins.classmethod
    def readme(cls) -> "TagConditionReadme":
        '''(experimental) Create a condition with logic targeting the README of the package.

        :stability: experimental
        '''
        return typing.cast("TagConditionReadme", jsii.sinvoke(cls, "readme", []))

    @jsii.member(jsii_name="bind") # type: ignore[misc]
    @abc.abstractmethod
    def bind(self) -> "TagConditionConfig":
        '''
        :stability: experimental
        '''
        ...


class _TagConditionProxy(TagCondition):
    @jsii.member(jsii_name="bind")
    def bind(self) -> "TagConditionConfig":
        '''
        :stability: experimental
        '''
        return typing.cast("TagConditionConfig", jsii.invoke(self, "bind", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, TagCondition).__jsii_proxy_class__ = lambda : _TagConditionProxy


@jsii.data_type(
    jsii_type="construct-hub.TagConditionConfig",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "children": "children",
        "key": "key",
        "options": "options",
        "source": "source",
        "value": "value",
    },
)
class TagConditionConfig:
    def __init__(
        self,
        *,
        type: "TagConditionLogicType",
        children: typing.Optional[typing.Sequence["TagConditionConfig"]] = None,
        key: typing.Optional[typing.Sequence[builtins.str]] = None,
        options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        source: typing.Optional["TagConditionSource"] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Serialized config for a tag condition.

        :param type: 
        :param children: 
        :param key: 
        :param options: 
        :param source: 
        :param value: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if children is not None:
            self._values["children"] = children
        if key is not None:
            self._values["key"] = key
        if options is not None:
            self._values["options"] = options
        if source is not None:
            self._values["source"] = source
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def type(self) -> "TagConditionLogicType":
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("TagConditionLogicType", result)

    @builtins.property
    def children(self) -> typing.Optional[typing.List["TagConditionConfig"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("children")
        return typing.cast(typing.Optional[typing.List["TagConditionConfig"]], result)

    @builtins.property
    def key(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def source(self) -> typing.Optional["TagConditionSource"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional["TagConditionSource"], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TagConditionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TagConditionField(
    metaclass=jsii.JSIIMeta,
    jsii_type="construct-hub.TagConditionField",
):
    '''(experimental) Target a field to use in logic to dictate whether a tag is relevant.

    :stability: experimental
    '''

    def __init__(self, field: typing.Sequence[builtins.str]) -> None:
        '''
        :param field: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [field])

    @jsii.member(jsii_name="eq")
    def eq(self, value: typing.Any) -> TagCondition:
        '''(experimental) Create a === condition which applies if the specified field within the package's package.json is equal to the passed value.

        :param value: -

        :stability: experimental
        '''
        return typing.cast(TagCondition, jsii.invoke(self, "eq", [value]))

    @jsii.member(jsii_name="includes")
    def includes(
        self,
        value: typing.Any,
        *,
        at_least: typing.Optional[jsii.Number] = None,
        case_sensitive: typing.Optional[builtins.bool] = None,
    ) -> TagCondition:
        '''(experimental) Create a ``field.includes(value)`` condition which applies if the specified field within the package's package.json includes the value. This works for arrays or strings.

        :param value: -
        :param at_least: (experimental) The value must appear at least this many times. Default: 1
        :param case_sensitive: (experimental) String matches must match the casing of the original string. This option is ignored if the value we are checking is an array. Default: false

        :stability: experimental
        '''
        options = TagConditionIncludesOptions(
            at_least=at_least, case_sensitive=case_sensitive
        )

        return typing.cast(TagCondition, jsii.invoke(self, "includes", [value, options]))

    @jsii.member(jsii_name="startsWith")
    def starts_with(self, value: builtins.str) -> TagCondition:
        '''(experimental) Create a ``field.startsWith(value)`` condition which applies if the specified field within the package's package.json begins with the value. This works only for string values.

        :param value: -

        :stability: experimental
        '''
        return typing.cast(TagCondition, jsii.invoke(self, "startsWith", [value]))


@jsii.data_type(
    jsii_type="construct-hub.TagConditionIncludesOptions",
    jsii_struct_bases=[],
    name_mapping={"at_least": "atLeast", "case_sensitive": "caseSensitive"},
)
class TagConditionIncludesOptions:
    def __init__(
        self,
        *,
        at_least: typing.Optional[jsii.Number] = None,
        case_sensitive: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for ``includes`` operator.

        :param at_least: (experimental) The value must appear at least this many times. Default: 1
        :param case_sensitive: (experimental) String matches must match the casing of the original string. This option is ignored if the value we are checking is an array. Default: false

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if at_least is not None:
            self._values["at_least"] = at_least
        if case_sensitive is not None:
            self._values["case_sensitive"] = case_sensitive

    @builtins.property
    def at_least(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The value must appear at least this many times.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("at_least")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def case_sensitive(self) -> typing.Optional[builtins.bool]:
        '''(experimental) String matches must match the casing of the original string.

        This option
        is ignored if the value we are checking is an array.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("case_sensitive")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TagConditionIncludesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="construct-hub.TagConditionLogicType")
class TagConditionLogicType(enum.Enum):
    '''(experimental) Logic operators for performing specific conditional logic.

    :stability: experimental
    '''

    AND = "AND"
    '''
    :stability: experimental
    '''
    OR = "OR"
    '''
    :stability: experimental
    '''
    NOT = "NOT"
    '''
    :stability: experimental
    '''
    EQUALS = "EQUALS"
    '''
    :stability: experimental
    '''
    INCLUDES = "INCLUDES"
    '''
    :stability: experimental
    '''
    STARTS_WITH = "STARTS_WITH"
    '''
    :stability: experimental
    '''


class TagConditionReadme(
    metaclass=jsii.JSIIMeta,
    jsii_type="construct-hub.TagConditionReadme",
):
    '''(experimental) Target the README of the package to dictate whether a tag is relevant.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="includes")
    def includes(
        self,
        value: builtins.str,
        *,
        at_least: typing.Optional[jsii.Number] = None,
        case_sensitive: typing.Optional[builtins.bool] = None,
    ) -> TagCondition:
        '''(experimental) Create a ``readme.includes(value)`` condition which applies if the README includes the specified string.

        :param value: -
        :param at_least: (experimental) The value must appear at least this many times. Default: 1
        :param case_sensitive: (experimental) String matches must match the casing of the original string. This option is ignored if the value we are checking is an array. Default: false

        :stability: experimental
        '''
        options = TagConditionIncludesOptions(
            at_least=at_least, case_sensitive=case_sensitive
        )

        return typing.cast(TagCondition, jsii.invoke(self, "includes", [value, options]))


@jsii.enum(jsii_type="construct-hub.TagConditionSource")
class TagConditionSource(enum.Enum):
    '''
    :stability: experimental
    '''

    PACKAGE_JSON = "PACKAGE_JSON"
    '''
    :stability: experimental
    '''
    README = "README"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="construct-hub.PackageTag",
    jsii_struct_bases=[PackageTagBase],
    name_mapping={
        "id": "id",
        "highlight": "highlight",
        "keyword": "keyword",
        "search_filter": "searchFilter",
        "condition": "condition",
    },
)
class PackageTag(PackageTagBase):
    def __init__(
        self,
        *,
        id: builtins.str,
        highlight: typing.Optional[Highlight] = None,
        keyword: typing.Optional[Keyword] = None,
        search_filter: typing.Optional[SearchFilter] = None,
        condition: TagCondition,
    ) -> None:
        '''(experimental) Configuration for applying custom tags to relevant packages.

        Custom tags are
        displayed on the package details page, and can be used for searching.

        :param id: (experimental) Identifier for tag, used for search. Must be unique amongst tags.
        :param highlight: (experimental) Configuration for higlighting tag on package card. Default: don't highlight tag
        :param keyword: (experimental) Configuration for showing tag as keyword. Default: don't show tag in keyword list
        :param search_filter: (experimental) Configuration for showing tag as search filter. Default: don't show tag in search filters
        :param condition: (experimental) The description of the logic that dictates whether the package has the tag applied.

        :stability: experimental
        '''
        if isinstance(highlight, dict):
            highlight = Highlight(**highlight)
        if isinstance(keyword, dict):
            keyword = Keyword(**keyword)
        if isinstance(search_filter, dict):
            search_filter = SearchFilter(**search_filter)
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
            "condition": condition,
        }
        if highlight is not None:
            self._values["highlight"] = highlight
        if keyword is not None:
            self._values["keyword"] = keyword
        if search_filter is not None:
            self._values["search_filter"] = search_filter

    @builtins.property
    def id(self) -> builtins.str:
        '''(experimental) Identifier for tag, used for search.

        Must be unique amongst tags.

        :stability: experimental
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def highlight(self) -> typing.Optional[Highlight]:
        '''(experimental) Configuration for higlighting tag on package card.

        :default: don't highlight tag

        :stability: experimental
        '''
        result = self._values.get("highlight")
        return typing.cast(typing.Optional[Highlight], result)

    @builtins.property
    def keyword(self) -> typing.Optional[Keyword]:
        '''(experimental) Configuration for showing tag as keyword.

        :default: don't show tag in keyword list

        :stability: experimental
        '''
        result = self._values.get("keyword")
        return typing.cast(typing.Optional[Keyword], result)

    @builtins.property
    def search_filter(self) -> typing.Optional[SearchFilter]:
        '''(experimental) Configuration for showing tag as search filter.

        :default: don't show tag in search filters

        :stability: experimental
        '''
        result = self._values.get("search_filter")
        return typing.cast(typing.Optional[SearchFilter], result)

    @builtins.property
    def condition(self) -> TagCondition:
        '''(experimental) The description of the logic that dictates whether the package has the tag applied.

        :stability: experimental
        '''
        result = self._values.get("condition")
        assert result is not None, "Required property 'condition' is missing"
        return typing.cast(TagCondition, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PackageTag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AlarmActions",
    "Category",
    "CodeArtifactDomainProps",
    "ConstructHub",
    "ConstructHubProps",
    "DenyListMap",
    "DenyListRule",
    "Domain",
    "DomainRedirectSource",
    "FeatureFlags",
    "FeaturedPackages",
    "FeaturedPackagesDetail",
    "FeaturedPackagesSection",
    "FilterType",
    "FilterTypeValue",
    "Highlight",
    "IDenyList",
    "ILicenseList",
    "IMonitoring",
    "IPackageSource",
    "IRepository",
    "Isolation",
    "Keyword",
    "LinkedResource",
    "PackageLinkConfig",
    "PackageSourceBindOptions",
    "PackageSourceBindResult",
    "PackageTag",
    "PackageTagBase",
    "PackageTagConfig",
    "PackageTagGroup",
    "PackageTagGroupConfig",
    "PackageTagGroupProps",
    "PreloadFile",
    "S3StorageFactory",
    "S3StorageFactoryProps",
    "SearchFilter",
    "SpdxLicense",
    "TagCondition",
    "TagConditionConfig",
    "TagConditionField",
    "TagConditionIncludesOptions",
    "TagConditionLogicType",
    "TagConditionReadme",
    "TagConditionSource",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import sources
