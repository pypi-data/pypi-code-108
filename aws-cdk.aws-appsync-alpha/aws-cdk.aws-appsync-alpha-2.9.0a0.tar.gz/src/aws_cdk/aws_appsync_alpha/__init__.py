'''
# AWS AppSync Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

The `@aws-cdk/aws-appsync` package contains constructs for building flexible
APIs that use GraphQL.

```python
import aws_cdk.aws_appsync_alpha as appsync
```

## Example

### DynamoDB

Example of a GraphQL API with `AWS_IAM` [authorization](#authorization) resolving into a DynamoDb
backend data source.

GraphQL schema file `schema.graphql`:

```gql
type demo {
  id: String!
  version: String!
}
type Query {
  getDemos: [ demo! ]
}
input DemoInput {
  version: String!
}
type Mutation {
  addDemo(input: DemoInput!): demo
}
```

CDK stack file `app-stack.ts`:

```python
api = appsync.GraphqlApi(self, "Api",
    name="demo",
    schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql")),
    authorization_config=appsync.AuthorizationConfig(
        default_authorization=appsync.AuthorizationMode(
            authorization_type=appsync.AuthorizationType.IAM
        )
    ),
    xray_enabled=True
)

demo_table = dynamodb.Table(self, "DemoTable",
    partition_key=dynamodb.Attribute(
        name="id",
        type=dynamodb.AttributeType.STRING
    )
)

demo_dS = api.add_dynamo_db_data_source("demoDataSource", demo_table)

# Resolver for the Query "getDemos" that scans the DynamoDb table and returns the entire list.
demo_dS.create_resolver(
    type_name="Query",
    field_name="getDemos",
    request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
    response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
)

# Resolver for the Mutation "addDemo" that puts the item into the DynamoDb table.
demo_dS.create_resolver(
    type_name="Mutation",
    field_name="addDemo",
    request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
        appsync.PrimaryKey.partition("id").auto(),
        appsync.Values.projecting("input")),
    response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
)
```

### Aurora Serverless

AppSync provides a data source for executing SQL commands against Amazon Aurora
Serverless clusters. You can use AppSync resolvers to execute SQL statements
against the Data API with GraphQL queries, mutations, and subscriptions.

```python
# Build a data source for AppSync to access the database.
# api: appsync.GraphqlApi
# Create username and password secret for DB Cluster
secret = rds.DatabaseSecret(self, "AuroraSecret",
    username="clusteradmin"
)

# The VPC to place the cluster in
vpc = ec2.Vpc(self, "AuroraVpc")

# Create the serverless cluster, provide all values needed to customise the database.
cluster = rds.ServerlessCluster(self, "AuroraCluster",
    engine=rds.DatabaseClusterEngine.AURORA_MYSQL,
    vpc=vpc,
    credentials={"username": "clusteradmin"},
    cluster_identifier="db-endpoint-test",
    default_database_name="demos"
)
rds_dS = api.add_rds_data_source("rds", cluster, secret, "demos")

# Set up a resolver for an RDS query.
rds_dS.create_resolver(
    type_name="Query",
    field_name="getDemosRds",
    request_mapping_template=appsync.MappingTemplate.from_string("""
          {
            "version": "2018-05-29",
            "statements": [
              "SELECT * FROM demos"
            ]
          }
          """),
    response_mapping_template=appsync.MappingTemplate.from_string("""
            $utils.toJson($utils.rds.toJsonObject($ctx.result)[0])
          """)
)

# Set up a resolver for an RDS mutation.
rds_dS.create_resolver(
    type_name="Mutation",
    field_name="addDemoRds",
    request_mapping_template=appsync.MappingTemplate.from_string("""
          {
            "version": "2018-05-29",
            "statements": [
              "INSERT INTO demos VALUES (:id, :version)",
              "SELECT * WHERE id = :id"
            ],
            "variableMap": {
              ":id": $util.toJson($util.autoId()),
              ":version": $util.toJson($ctx.args.version)
            }
          }
          """),
    response_mapping_template=appsync.MappingTemplate.from_string("""
            $utils.toJson($utils.rds.toJsonObject($ctx.result)[1][0])
          """)
)
```

### HTTP Endpoints

GraphQL schema file `schema.graphql`:

```gql
type job {
  id: String!
  version: String!
}

input DemoInput {
  version: String!
}

type Mutation {
  callStepFunction(input: DemoInput!): job
}
```

GraphQL request mapping template `request.vtl`:

```json
{
  "version": "2018-05-29",
  "method": "POST",
  "resourcePath": "/",
  "params": {
    "headers": {
      "content-type": "application/x-amz-json-1.0",
      "x-amz-target":"AWSStepFunctions.StartExecution"
    },
    "body": {
      "stateMachineArn": "<your step functions arn>",
      "input": "{ \"id\": \"$context.arguments.id\" }"
    }
  }
}
```

GraphQL response mapping template `response.vtl`:

```json
{
  "id": "${context.result.id}"
}
```

CDK stack file `app-stack.ts`:

```python
api = appsync.GraphqlApi(self, "api",
    name="api",
    schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql"))
)

http_ds = api.add_http_data_source("ds", "https://states.amazonaws.com",
    name="httpDsWithStepF",
    description="from appsync to StepFunctions Workflow",
    authorization_config=appsync.AwsIamConfig(
        signing_region="us-east-1",
        signing_service_name="states"
    )
)

http_ds.create_resolver(
    type_name="Mutation",
    field_name="callStepFunction",
    request_mapping_template=appsync.MappingTemplate.from_file("request.vtl"),
    response_mapping_template=appsync.MappingTemplate.from_file("response.vtl")
)
```

### Elasticsearch

AppSync has builtin support for Elasticsearch from domains that are provisioned
through your AWS account. You can use AppSync resolvers to perform GraphQL operations
such as queries, mutations, and subscriptions.

```python
import aws_cdk.aws_elasticsearch as es

# api: appsync.GraphqlApi


user = iam.User(self, "User")
domain = es.Domain(self, "Domain",
    version=es.ElasticsearchVersion.V7_1,
    removal_policy=RemovalPolicy.DESTROY,
    fine_grained_access_control=es.AdvancedSecurityOptions(master_user_arn=user.user_arn),
    encryption_at_rest=es.EncryptionAtRestOptions(enabled=True),
    node_to_node_encryption=True,
    enforce_https=True
)
ds = api.add_elasticsearch_data_source("ds", domain)

ds.create_resolver(
    type_name="Query",
    field_name="getTests",
    request_mapping_template=appsync.MappingTemplate.from_string(JSON.stringify({
        "version": "2017-02-28",
        "operation": "GET",
        "path": "/id/post/_search",
        "params": {
            "headers": {},
            "query_string": {},
            "body": {"from": 0, "size": 50}
        }
    })),
    response_mapping_template=appsync.MappingTemplate.from_string("""[
            #foreach($entry in $context.result.hits.hits)
            #if( $velocityCount > 1 ) , #end
            $utils.toJson($entry.get("_source"))
            #end
          ]""")
)
```

## Schema

Every GraphQL Api needs a schema to define the Api. CDK offers `appsync.Schema`
for static convenience methods for various types of schema declaration: code-first
or schema-first.

### Code-First

When declaring your GraphQL Api, CDK defaults to a code-first approach if the
`schema` property is not configured.

```python
api = appsync.GraphqlApi(self, "api", name="myApi")
```

CDK will declare a `Schema` class that will give your Api access functions to
define your schema code-first: `addType`, `addToSchema`, etc.

You can also declare your `Schema` class outside of your CDK stack, to define
your schema externally.

```python
schema = appsync.Schema()
schema.add_type(appsync.ObjectType("demo",
    definition={"id": appsync.GraphqlType.id()}
))
api = appsync.GraphqlApi(self, "api",
    name="myApi",
    schema=schema
)
```

See the [code-first schema](#Code-First-Schema) section for more details.

### Schema-First

You can define your GraphQL Schema from a file on disk. For convenience, use
the `appsync.Schema.fromAsset` to specify the file representing your schema.

```python
api = appsync.GraphqlApi(self, "api",
    name="myApi",
    schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphl"))
)
```

## Imports

Any GraphQL Api that has been created outside the stack can be imported from
another stack into your CDK app. Utilizing the `fromXxx` function, you have
the ability to add data sources and resolvers through a `IGraphqlApi` interface.

```python
# api: appsync.GraphqlApi
# table: dynamodb.Table

imported_api = appsync.GraphqlApi.from_graphql_api_attributes(self, "IApi",
    graphql_api_id=api.api_id,
    graphql_api_arn=api.arn
)
imported_api.add_dynamo_db_data_source("TableDataSource", table)
```

If you don't specify `graphqlArn` in `fromXxxAttributes`, CDK will autogenerate
the expected `arn` for the imported api, given the `apiId`. For creating data
sources and resolvers, an `apiId` is sufficient.

## Authorization

There are multiple authorization types available for GraphQL API to cater to different
access use cases. They are:

* API Keys (`AuthorizationType.API_KEY`)
* Amazon Cognito User Pools (`AuthorizationType.USER_POOL`)
* OpenID Connect (`AuthorizationType.OPENID_CONNECT`)
* AWS Identity and Access Management (`AuthorizationType.AWS_IAM`)
* AWS Lambda (`AuthorizationType.AWS_LAMBDA`)

These types can be used simultaneously in a single API, allowing different types of clients to
access data. When you specify an authorization type, you can also specify the corresponding
authorization mode to finish defining your authorization. For example, this is a GraphQL API
with AWS Lambda Authorization.

```python
import aws_cdk.aws_lambda as lambda_
# auth_function: lambda.Function


appsync.GraphqlApi(self, "api",
    name="api",
    schema=appsync.Schema.from_asset(path.join(__dirname, "appsync.test.graphql")),
    authorization_config=appsync.AuthorizationConfig(
        default_authorization=appsync.AuthorizationMode(
            authorization_type=appsync.AuthorizationType.LAMBDA,
            lambda_authorizer_config=appsync.LambdaAuthorizerConfig(
                handler=auth_function
            )
        )
    )
)
```

## Permissions

When using `AWS_IAM` as the authorization type for GraphQL API, an IAM Role
with correct permissions must be used for access to API.

When configuring permissions, you can specify specific resources to only be
accessible by `IAM` authorization. For example, if you want to only allow mutability
for `IAM` authorized access you would configure the following.

In `schema.graphql`:

```gql
type Mutation {
  updateExample(...): ...
    @aws_iam
}
```

In `IAM`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "appsync:GraphQL"
      ],
      "Resource": [
        "arn:aws:appsync:REGION:ACCOUNT_ID:apis/GRAPHQL_ID/types/Mutation/fields/updateExample"
      ]
    }
  ]
}
```

See [documentation](https://docs.aws.amazon.com/appsync/latest/devguide/security.html#aws-iam-authorization) for more details.

To make this easier, CDK provides `grant` API.

Use the `grant` function for more granular authorization.

```python
# api: appsync.GraphqlApi
role = iam.Role(self, "Role",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
)

api.grant(role, appsync.IamResource.custom("types/Mutation/fields/updateExample"), "appsync:GraphQL")
```

### IamResource

In order to use the `grant` functions, you need to use the class `IamResource`.

* `IamResource.custom(...arns)` permits custom ARNs and requires an argument.
* `IamResouce.ofType(type, ...fields)` permits ARNs for types and their fields.
* `IamResource.all()` permits ALL resources.

### Generic Permissions

Alternatively, you can use more generic `grant` functions to accomplish the same usage.

These include:

* grantMutation (use to grant access to Mutation fields)
* grantQuery (use to grant access to Query fields)
* grantSubscription (use to grant access to Subscription fields)

```python
# api: appsync.GraphqlApi
# role: iam.Role


# For generic types
api.grant_mutation(role, "updateExample")

# For custom types and granular design
api.grant(role, appsync.IamResource.of_type("Mutation", "updateExample"), "appsync:GraphQL")
```

## Pipeline Resolvers and AppSync Functions

AppSync Functions are local functions that perform certain operations onto a
backend data source. Developers can compose operations (Functions) and execute
them in sequence with Pipeline Resolvers.

```python
# api: appsync.GraphqlApi


appsync_function = appsync.AppsyncFunction(self, "function",
    name="appsync_function",
    api=api,
    data_source=api.add_none_data_source("none"),
    request_mapping_template=appsync.MappingTemplate.from_file("request.vtl"),
    response_mapping_template=appsync.MappingTemplate.from_file("response.vtl")
)
```

AppSync Functions are used in tandem with pipeline resolvers to compose multiple
operations.

```python
# api: appsync.GraphqlApi
# appsync_function: appsync.AppsyncFunction


pipeline_resolver = appsync.Resolver(self, "pipeline",
    api=api,
    data_source=api.add_none_data_source("none"),
    type_name="typeName",
    field_name="fieldName",
    request_mapping_template=appsync.MappingTemplate.from_file("beforeRequest.vtl"),
    pipeline_config=[appsync_function],
    response_mapping_template=appsync.MappingTemplate.from_file("afterResponse.vtl")
)
```

Learn more about Pipeline Resolvers and AppSync Functions [here](https://docs.aws.amazon.com/appsync/latest/devguide/pipeline-resolvers.html).

## Code-First Schema

CDK offers the ability to generate your schema in a code-first approach.
A code-first approach offers a developer workflow with:

* **modularity**: organizing schema type definitions into different files
* **reusability**: simplifying down boilerplate/repetitive code
* **consistency**: resolvers and schema definition will always be synced

The code-first approach allows for **dynamic** schema generation. You can generate your schema based on variables and templates to reduce code duplication.

### Code-First Example

To showcase the code-first approach. Let's try to model the following schema segment.

```gql
interface Node {
  id: String
}

type Query {
  allFilms(after: String, first: Int, before: String, last: Int): FilmConnection
}

type FilmNode implements Node {
  filmName: String
}

type FilmConnection {
  edges: [FilmEdge]
  films: [Film]
  totalCount: Int
}

type FilmEdge {
  node: Film
  cursor: String
}
```

Above we see a schema that allows for generating paginated responses. For example,
we can query `allFilms(first: 100)` since `FilmConnection` acts as an intermediary
for holding `FilmEdges` we can write a resolver to return the first 100 films.

In a separate file, we can declare our object types and related functions.
We will call this file `object-types.ts` and we will have created it in a way that
allows us to generate other `XxxConnection` and `XxxEdges` in the future.

```python
import aws_cdk.aws_appsync_alpha as appsync
pluralize = require("pluralize")

args = {
    "after": appsync.GraphqlType.string(),
    "first": appsync.GraphqlType.int(),
    "before": appsync.GraphqlType.string(),
    "last": appsync.GraphqlType.int()
}

Node = appsync.InterfaceType("Node",
    definition={"id": appsync.GraphqlType.string()}
)
FilmNode = appsync.ObjectType("FilmNode",
    interface_types=[Node],
    definition={"film_name": appsync.GraphqlType.string()}
)

def generate_edge_and_connection(base):
    edge = appsync.ObjectType(f"{base.name}Edge",
        definition={"node": base.attribute(), "cursor": appsync.GraphqlType.string()}
    )
    connection = appsync.ObjectType(f"{base.name}Connection",
        definition={
            "edges": edge.attribute(is_list=True),
            pluralize(base.name): base.attribute(is_list=True),
            "total_count": appsync.GraphqlType.int()
        }
    )
    return {"edge": edge, "connection": connection}
```

Finally, we will go to our `cdk-stack` and combine everything together
to generate our schema.

```python
# dummy_request: appsync.MappingTemplate
# dummy_response: appsync.MappingTemplate


api = appsync.GraphqlApi(self, "Api",
    name="demo"
)

object_types = [Node, FilmNode]

film_connections = generate_edge_and_connection(FilmNode)

api.add_query("allFilms", appsync.ResolvableField(
    return_type=film_connections.connection.attribute(),
    args=args,
    data_source=api.add_none_data_source("none"),
    request_mapping_template=dummy_request,
    response_mapping_template=dummy_response
))

api.add_type(Node)
api.add_type(FilmNode)
api.add_type(film_connections.edge)
api.add_type(film_connections.connection)
```

Notice how we can utilize the `generateEdgeAndConnection` function to generate
Object Types. In the future, if we wanted to create more Object Types, we can simply
create the base Object Type (i.e. Film) and from there we can generate its respective
`Connections` and `Edges`.

Check out a more in-depth example [here](https://github.com/BryanPan342/starwars-code-first).

## GraphQL Types

One of the benefits of GraphQL is its strongly typed nature. We define the
types within an object, query, mutation, interface, etc. as **GraphQL Types**.

GraphQL Types are the building blocks of types, whether they are scalar, objects,
interfaces, etc. GraphQL Types can be:

* [**Scalar Types**](https://docs.aws.amazon.com/appsync/latest/devguide/scalars.html): Id, Int, String, AWSDate, etc.
* [**Object Types**](#Object-Types): types that you generate (i.e. `demo` from the example above)
* [**Interface Types**](#Interface-Types): abstract types that define the base implementation of other
  Intermediate Types

More concretely, GraphQL Types are simply the types appended to variables.
Referencing the object type `Demo` in the previous example, the GraphQL Types
is `String!` and is applied to both the names `id` and `version`.

### Directives

`Directives` are attached to a field or type and affect the execution of queries,
mutations, and types. With AppSync, we use `Directives` to configure authorization.
CDK provides static functions to add directives to your Schema.

* `Directive.iam()` sets a type or field's authorization to be validated through `Iam`
* `Directive.apiKey()` sets a type or field's authorization to be validated through a `Api Key`
* `Directive.oidc()` sets a type or field's authorization to be validated through `OpenID Connect`
* `Directive.cognito(...groups: string[])` sets a type or field's authorization to be validated
  through `Cognito User Pools`

  * `groups` the name of the cognito groups to give access

To learn more about authorization and directives, read these docs [here](https://docs.aws.amazon.com/appsync/latest/devguide/security.html).

### Field and Resolvable Fields

While `GraphqlType` is a base implementation for GraphQL fields, we have abstractions
on top of `GraphqlType` that provide finer grain support.

### Field

`Field` extends `GraphqlType` and will allow you to define arguments. [**Interface Types**](#Interface-Types) are not resolvable and this class will allow you to define arguments,
but not its resolvers.

For example, if we want to create the following type:

```gql
type Node {
  test(argument: string): String
}
```

The CDK code required would be:

```python
field = appsync.Field(
    return_type=appsync.GraphqlType.string(),
    args={
        "argument": appsync.GraphqlType.string()
    }
)
type = appsync.InterfaceType("Node",
    definition={"test": field}
)
```

### Resolvable Fields

`ResolvableField` extends `Field` and will allow you to define arguments and its resolvers.
[**Object Types**](#Object-Types) can have fields that resolve and perform operations on
your backend.

You can also create resolvable fields for object types.

```gql
type Info {
  node(id: String): String
}
```

The CDK code required would be:

```python
# api: appsync.GraphqlApi
# dummy_request: appsync.MappingTemplate
# dummy_response: appsync.MappingTemplate

info = appsync.ObjectType("Info",
    definition={
        "node": appsync.ResolvableField(
            return_type=appsync.GraphqlType.string(),
            args={
                "id": appsync.GraphqlType.string()
            },
            data_source=api.add_none_data_source("none"),
            request_mapping_template=dummy_request,
            response_mapping_template=dummy_response
        )
    }
)
```

To nest resolvers, we can also create top level query types that call upon
other types. Building off the previous example, if we want the following graphql
type definition:

```gql
type Query {
  get(argument: string): Info
}
```

The CDK code required would be:

```python
# api: appsync.GraphqlApi
# dummy_request: appsync.MappingTemplate
# dummy_response: appsync.MappingTemplate

query = appsync.ObjectType("Query",
    definition={
        "get": appsync.ResolvableField(
            return_type=appsync.GraphqlType.string(),
            args={
                "argument": appsync.GraphqlType.string()
            },
            data_source=api.add_none_data_source("none"),
            request_mapping_template=dummy_request,
            response_mapping_template=dummy_response
        )
    }
)
```

Learn more about fields and resolvers [here](https://docs.aws.amazon.com/appsync/latest/devguide/resolver-mapping-template-reference-overview.html).

### Intermediate Types

Intermediate Types are defined by Graphql Types and Fields. They have a set of defined
fields, where each field corresponds to another type in the system. Intermediate
Types will be the meat of your GraphQL Schema as they are the types defined by you.

Intermediate Types include:

* [**Interface Types**](#Interface-Types)
* [**Object Types**](#Object-Types)
* [**Enum Types**](#Enum-Types)
* [**Input Types**](#Input-Types)
* [**Union Types**](#Union-Types)

#### Interface Types

**Interface Types** are abstract types that define the implementation of other
intermediate types. They are useful for eliminating duplication and can be used
to generate Object Types with less work.

You can create Interface Types ***externally***.

```python
node = appsync.InterfaceType("Node",
    definition={
        "id": appsync.GraphqlType.string(is_required=True)
    }
)
```

To learn more about **Interface Types**, read the docs [here](https://graphql.org/learn/schema/#interfaces).

#### Object Types

**Object Types** are types that you declare. For example, in the [code-first example](#code-first-example)
the `demo` variable is an **Object Type**. **Object Types** are defined by
GraphQL Types and are only usable when linked to a GraphQL Api.

You can create Object Types in two ways:

1. Object Types can be created ***externally***.

   ```python
   api = appsync.GraphqlApi(self, "Api",
       name="demo"
   )
   demo = appsync.ObjectType("Demo",
       definition={
           "id": appsync.GraphqlType.string(is_required=True),
           "version": appsync.GraphqlType.string(is_required=True)
       }
   )

   api.add_type(demo)
   ```

   > This method allows for reusability and modularity, ideal for larger projects.
   > For example, imagine moving all Object Type definition outside the stack.

   `object-types.ts` - a file for object type definitions

   ```python
   import aws_cdk.aws_appsync_alpha as appsync
   demo = appsync.ObjectType("Demo",
       definition={
           "id": appsync.GraphqlType.string(is_required=True),
           "version": appsync.GraphqlType.string(is_required=True)
       }
   )
   ```

   `cdk-stack.ts` - a file containing our cdk stack

   ```python
   # api: appsync.GraphqlApi

   api.add_type(demo)
   ```
2. Object Types can be created ***externally*** from an Interface Type.

   ```python
   node = appsync.InterfaceType("Node",
       definition={
           "id": appsync.GraphqlType.string(is_required=True)
       }
   )
   demo = appsync.ObjectType("Demo",
       interface_types=[node],
       definition={
           "version": appsync.GraphqlType.string(is_required=True)
       }
   )
   ```

   > This method allows for reusability and modularity, ideal for reducing code duplication.

To learn more about **Object Types**, read the docs [here](https://graphql.org/learn/schema/#object-types-and-fields).

#### Enum Types

**Enum Types** are a special type of Intermediate Type. They restrict a particular
set of allowed values for other Intermediate Types.

```gql
enum Episode {
  NEWHOPE
  EMPIRE
  JEDI
}
```

> This means that wherever we use the type Episode in our schema, we expect it to
> be exactly one of NEWHOPE, EMPIRE, or JEDI.

The above GraphQL Enumeration Type can be expressed in CDK as the following:

```python
# api: appsync.GraphqlApi

episode = appsync.EnumType("Episode",
    definition=["NEWHOPE", "EMPIRE", "JEDI"
    ]
)
api.add_type(episode)
```

To learn more about **Enum Types**, read the docs [here](https://graphql.org/learn/schema/#enumeration-types).

#### Input Types

**Input Types** are special types of Intermediate Types. They give users an
easy way to pass complex objects for top level Mutation and Queries.

```gql
input Review {
  stars: Int!
  commentary: String
}
```

The above GraphQL Input Type can be expressed in CDK as the following:

```python
# api: appsync.GraphqlApi

review = appsync.InputType("Review",
    definition={
        "stars": appsync.GraphqlType.int(is_required=True),
        "commentary": appsync.GraphqlType.string()
    }
)
api.add_type(review)
```

To learn more about **Input Types**, read the docs [here](https://graphql.org/learn/schema/#input-types).

#### Union Types

**Union Types** are a special type of Intermediate Type. They are similar to
Interface Types, but they cannot specify any common fields between types.

**Note:** the fields of a union type need to be `Object Types`. In other words, you
can't create a union type out of interfaces, other unions, or inputs.

```gql
union Search = Human | Droid | Starship
```

The above GraphQL Union Type encompasses the Object Types of Human, Droid and Starship. It
can be expressed in CDK as the following:

```python
# api: appsync.GraphqlApi

string = appsync.GraphqlType.string()
human = appsync.ObjectType("Human", definition={"name": string})
droid = appsync.ObjectType("Droid", definition={"name": string})
starship = appsync.ObjectType("Starship", definition={"name": string})
search = appsync.UnionType("Search",
    definition=[human, droid, starship]
)
api.add_type(search)
```

To learn more about **Union Types**, read the docs [here](https://graphql.org/learn/schema/#union-types).

### Query

Every schema requires a top level Query type. By default, the schema will look
for the `Object Type` named `Query`. The top level `Query` is the **only** exposed
type that users can access to perform `GET` operations on your Api.

To add fields for these queries, we can simply run the `addQuery` function to add
to the schema's `Query` type.

```python
# api: appsync.GraphqlApi
# film_connection: appsync.InterfaceType
# dummy_request: appsync.MappingTemplate
# dummy_response: appsync.MappingTemplate


string = appsync.GraphqlType.string()
int = appsync.GraphqlType.int()
api.add_query("allFilms", appsync.ResolvableField(
    return_type=film_connection.attribute(),
    args={"after": string, "first": int, "before": string, "last": int},
    data_source=api.add_none_data_source("none"),
    request_mapping_template=dummy_request,
    response_mapping_template=dummy_response
))
```

To learn more about top level operations, check out the docs [here](https://docs.aws.amazon.com/appsync/latest/devguide/graphql-overview.html).

### Mutation

Every schema **can** have a top level Mutation type. By default, the schema will look
for the `ObjectType` named `Mutation`. The top level `Mutation` Type is the only exposed
type that users can access to perform `mutable` operations on your Api.

To add fields for these mutations, we can simply run the `addMutation` function to add
to the schema's `Mutation` type.

```python
# api: appsync.GraphqlApi
# film_node: appsync.ObjectType
# dummy_request: appsync.MappingTemplate
# dummy_response: appsync.MappingTemplate


string = appsync.GraphqlType.string()
int = appsync.GraphqlType.int()
api.add_mutation("addFilm", appsync.ResolvableField(
    return_type=film_node.attribute(),
    args={"name": string, "film_number": int},
    data_source=api.add_none_data_source("none"),
    request_mapping_template=dummy_request,
    response_mapping_template=dummy_response
))
```

To learn more about top level operations, check out the docs [here](https://docs.aws.amazon.com/appsync/latest/devguide/graphql-overview.html).

### Subscription

Every schema **can** have a top level Subscription type. The top level `Subscription` Type
is the only exposed type that users can access to invoke a response to a mutation. `Subscriptions`
notify users when a mutation specific mutation is called. This means you can make any data source
real time by specify a GraphQL Schema directive on a mutation.

**Note**: The AWS AppSync client SDK automatically handles subscription connection management.

To add fields for these subscriptions, we can simply run the `addSubscription` function to add
to the schema's `Subscription` type.

```python
# api: appsync.GraphqlApi
# film: appsync.InterfaceType


api.add_subscription("addedFilm", appsync.Field(
    return_type=film.attribute(),
    args={"id": appsync.GraphqlType.id(is_required=True)},
    directives=[appsync.Directive.subscribe("addFilm")]
))
```

To learn more about top level operations, check out the docs [here](https://docs.aws.amazon.com/appsync/latest/devguide/real-time-data.html).
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
import aws_cdk.aws_appsync
import aws_cdk.aws_cognito
import aws_cdk.aws_dynamodb
import aws_cdk.aws_elasticsearch
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_rds
import aws_cdk.aws_secretsmanager
import constructs


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.AddFieldOptions",
    jsii_struct_bases=[],
    name_mapping={"field": "field", "field_name": "fieldName"},
)
class AddFieldOptions:
    def __init__(
        self,
        *,
        field: typing.Optional["IField"] = None,
        field_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) The options to add a field to an Intermediate Type.

        :param field: (experimental) The resolvable field to add. This option must be configured for Object, Interface, Input and Union Types. Default: - no IField
        :param field_name: (experimental) The name of the field. This option must be configured for Object, Interface, Input and Enum Types. Default: - no fieldName

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            # field: appsync_alpha.Field
            
            add_field_options = appsync_alpha.AddFieldOptions(
                field=field,
                field_name="fieldName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if field is not None:
            self._values["field"] = field
        if field_name is not None:
            self._values["field_name"] = field_name

    @builtins.property
    def field(self) -> typing.Optional["IField"]:
        '''(experimental) The resolvable field to add.

        This option must be configured for Object, Interface,
        Input and Union Types.

        :default: - no IField

        :stability: experimental
        '''
        result = self._values.get("field")
        return typing.cast(typing.Optional["IField"], result)

    @builtins.property
    def field_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the field.

        This option must be configured for Object, Interface,
        Input and Enum Types.

        :default: - no fieldName

        :stability: experimental
        '''
        result = self._values.get("field_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddFieldOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.ApiKeyConfig",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "expires": "expires", "name": "name"},
)
class ApiKeyConfig:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        expires: typing.Optional[aws_cdk.Expiration] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Configuration for API Key authorization in AppSync.

        :param description: (experimental) Description of API key. Default: - 'Default API Key created by CDK'
        :param expires: (experimental) The time from creation time after which the API key expires. It must be a minimum of 1 day and a maximum of 365 days from date of creation. Rounded down to the nearest hour. Default: - 7 days rounded down to nearest hour
        :param name: (experimental) Unique name of the API Key. Default: - 'DefaultAPIKey'

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            import aws_cdk as cdk
            
            # expiration: cdk.Expiration
            
            api_key_config = appsync_alpha.ApiKeyConfig(
                description="description",
                expires=expiration,
                name="name"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if expires is not None:
            self._values["expires"] = expires
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description of API key.

        :default: - 'Default API Key created by CDK'

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expires(self) -> typing.Optional[aws_cdk.Expiration]:
        '''(experimental) The time from creation time after which the API key expires.

        It must be a minimum of 1 day and a maximum of 365 days from date of creation.
        Rounded down to the nearest hour.

        :default: - 7 days rounded down to nearest hour

        :stability: experimental
        '''
        result = self._values.get("expires")
        return typing.cast(typing.Optional[aws_cdk.Expiration], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Unique name of the API Key.

        :default: - 'DefaultAPIKey'

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.AppsyncFunctionAttributes",
    jsii_struct_bases=[],
    name_mapping={"function_arn": "functionArn"},
)
class AppsyncFunctionAttributes:
    def __init__(self, *, function_arn: builtins.str) -> None:
        '''(experimental) The attributes for imported AppSync Functions.

        :param function_arn: (experimental) the ARN of the AppSync function.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            appsync_function_attributes = appsync_alpha.AppsyncFunctionAttributes(
                function_arn="functionArn"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "function_arn": function_arn,
        }

    @builtins.property
    def function_arn(self) -> builtins.str:
        '''(experimental) the ARN of the AppSync function.

        :stability: experimental
        '''
        result = self._values.get("function_arn")
        assert result is not None, "Required property 'function_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncFunctionAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Assign(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync-alpha.Assign"):
    '''(experimental) Utility class representing the assigment of a value to an attribute.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_appsync_alpha as appsync_alpha
        
        assign = appsync_alpha.Assign("attr", "arg")
    '''

    def __init__(self, attr: builtins.str, arg: builtins.str) -> None:
        '''
        :param attr: -
        :param arg: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [attr, arg])

    @jsii.member(jsii_name="putInMap")
    def put_in_map(self, map: builtins.str) -> builtins.str:
        '''(experimental) Renders the assignment as a map element.

        :param map: -

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "putInMap", [map]))

    @jsii.member(jsii_name="renderAsAssignment")
    def render_as_assignment(self) -> builtins.str:
        '''(experimental) Renders the assignment as a VTL string.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "renderAsAssignment", []))


class AttributeValues(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.AttributeValues",
):
    '''(experimental) Specifies the attribute value assignments.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        api = appsync.GraphqlApi(self, "Api",
            name="demo",
            schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql")),
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.IAM
                )
            ),
            xray_enabled=True
        )
        
        demo_table = dynamodb.Table(self, "DemoTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        demo_dS = api.add_dynamo_db_data_source("demoDataSource", demo_table)
        
        # Resolver for the Query "getDemos" that scans the DynamoDb table and returns the entire list.
        demo_dS.create_resolver(
            type_name="Query",
            field_name="getDemos",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
        )
        
        # Resolver for the Mutation "addDemo" that puts the item into the DynamoDb table.
        demo_dS.create_resolver(
            type_name="Mutation",
            field_name="addDemo",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
                appsync.PrimaryKey.partition("id").auto(),
                appsync.Values.projecting("input")),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
        )
    '''

    def __init__(
        self,
        container: builtins.str,
        assignments: typing.Optional[typing.Sequence[Assign]] = None,
    ) -> None:
        '''
        :param container: -
        :param assignments: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [container, assignments])

    @jsii.member(jsii_name="attribute")
    def attribute(self, attr: builtins.str) -> "AttributeValuesStep":
        '''(experimental) Allows assigning a value to the specified attribute.

        :param attr: -

        :stability: experimental
        '''
        return typing.cast("AttributeValuesStep", jsii.invoke(self, "attribute", [attr]))

    @jsii.member(jsii_name="renderTemplate")
    def render_template(self) -> builtins.str:
        '''(experimental) Renders the attribute value assingments to a VTL string.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "renderTemplate", []))

    @jsii.member(jsii_name="renderVariables")
    def render_variables(self) -> builtins.str:
        '''(experimental) Renders the variables required for ``renderTemplate``.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "renderVariables", []))


class AttributeValuesStep(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.AttributeValuesStep",
):
    '''(experimental) Utility class to allow assigning a value to an attribute.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_appsync_alpha as appsync_alpha
        
        # assign: appsync_alpha.Assign
        
        attribute_values_step = appsync_alpha.AttributeValuesStep("attr", "container", [assign])
    '''

    def __init__(
        self,
        attr: builtins.str,
        container: builtins.str,
        assignments: typing.Sequence[Assign],
    ) -> None:
        '''
        :param attr: -
        :param container: -
        :param assignments: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [attr, container, assignments])

    @jsii.member(jsii_name="is")
    def is_(self, val: builtins.str) -> AttributeValues:
        '''(experimental) Assign the value to the current attribute.

        :param val: -

        :stability: experimental
        '''
        return typing.cast(AttributeValues, jsii.invoke(self, "is", [val]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.AuthorizationConfig",
    jsii_struct_bases=[],
    name_mapping={
        "additional_authorization_modes": "additionalAuthorizationModes",
        "default_authorization": "defaultAuthorization",
    },
)
class AuthorizationConfig:
    def __init__(
        self,
        *,
        additional_authorization_modes: typing.Optional[typing.Sequence["AuthorizationMode"]] = None,
        default_authorization: typing.Optional["AuthorizationMode"] = None,
    ) -> None:
        '''(experimental) Configuration of the API authorization modes.

        :param additional_authorization_modes: (experimental) Additional authorization modes. Default: - No other modes
        :param default_authorization: (experimental) Optional authorization configuration. Default: - API Key authorization

        :stability: experimental
        :exampleMetadata: infused

        Example::

            api = appsync.GraphqlApi(self, "Api",
                name="demo",
                schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql")),
                authorization_config=appsync.AuthorizationConfig(
                    default_authorization=appsync.AuthorizationMode(
                        authorization_type=appsync.AuthorizationType.IAM
                    )
                ),
                xray_enabled=True
            )
            
            demo_table = dynamodb.Table(self, "DemoTable",
                partition_key=dynamodb.Attribute(
                    name="id",
                    type=dynamodb.AttributeType.STRING
                )
            )
            
            demo_dS = api.add_dynamo_db_data_source("demoDataSource", demo_table)
            
            # Resolver for the Query "getDemos" that scans the DynamoDb table and returns the entire list.
            demo_dS.create_resolver(
                type_name="Query",
                field_name="getDemos",
                request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
                response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
            )
            
            # Resolver for the Mutation "addDemo" that puts the item into the DynamoDb table.
            demo_dS.create_resolver(
                type_name="Mutation",
                field_name="addDemo",
                request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
                    appsync.PrimaryKey.partition("id").auto(),
                    appsync.Values.projecting("input")),
                response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
            )
        '''
        if isinstance(default_authorization, dict):
            default_authorization = AuthorizationMode(**default_authorization)
        self._values: typing.Dict[str, typing.Any] = {}
        if additional_authorization_modes is not None:
            self._values["additional_authorization_modes"] = additional_authorization_modes
        if default_authorization is not None:
            self._values["default_authorization"] = default_authorization

    @builtins.property
    def additional_authorization_modes(
        self,
    ) -> typing.Optional[typing.List["AuthorizationMode"]]:
        '''(experimental) Additional authorization modes.

        :default: - No other modes

        :stability: experimental
        '''
        result = self._values.get("additional_authorization_modes")
        return typing.cast(typing.Optional[typing.List["AuthorizationMode"]], result)

    @builtins.property
    def default_authorization(self) -> typing.Optional["AuthorizationMode"]:
        '''(experimental) Optional authorization configuration.

        :default: - API Key authorization

        :stability: experimental
        '''
        result = self._values.get("default_authorization")
        return typing.cast(typing.Optional["AuthorizationMode"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthorizationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.AuthorizationMode",
    jsii_struct_bases=[],
    name_mapping={
        "authorization_type": "authorizationType",
        "api_key_config": "apiKeyConfig",
        "lambda_authorizer_config": "lambdaAuthorizerConfig",
        "open_id_connect_config": "openIdConnectConfig",
        "user_pool_config": "userPoolConfig",
    },
)
class AuthorizationMode:
    def __init__(
        self,
        *,
        authorization_type: "AuthorizationType",
        api_key_config: typing.Optional[ApiKeyConfig] = None,
        lambda_authorizer_config: typing.Optional["LambdaAuthorizerConfig"] = None,
        open_id_connect_config: typing.Optional["OpenIdConnectConfig"] = None,
        user_pool_config: typing.Optional["UserPoolConfig"] = None,
    ) -> None:
        '''(experimental) Interface to specify default or additional authorization(s).

        :param authorization_type: (experimental) One of possible four values AppSync supports. Default: - ``AuthorizationType.API_KEY``
        :param api_key_config: (experimental) If authorizationType is ``AuthorizationType.API_KEY``, this option can be configured. Default: - name: 'DefaultAPIKey' | description: 'Default API Key created by CDK'
        :param lambda_authorizer_config: (experimental) If authorizationType is ``AuthorizationType.LAMBDA``, this option is required. Default: - none
        :param open_id_connect_config: (experimental) If authorizationType is ``AuthorizationType.OIDC``, this option is required. Default: - none
        :param user_pool_config: (experimental) If authorizationType is ``AuthorizationType.USER_POOL``, this option is required. Default: - none

        :stability: experimental
        :exampleMetadata: infused

        Example::

            api = appsync.GraphqlApi(self, "Api",
                name="demo",
                schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql")),
                authorization_config=appsync.AuthorizationConfig(
                    default_authorization=appsync.AuthorizationMode(
                        authorization_type=appsync.AuthorizationType.IAM
                    )
                ),
                xray_enabled=True
            )
            
            demo_table = dynamodb.Table(self, "DemoTable",
                partition_key=dynamodb.Attribute(
                    name="id",
                    type=dynamodb.AttributeType.STRING
                )
            )
            
            demo_dS = api.add_dynamo_db_data_source("demoDataSource", demo_table)
            
            # Resolver for the Query "getDemos" that scans the DynamoDb table and returns the entire list.
            demo_dS.create_resolver(
                type_name="Query",
                field_name="getDemos",
                request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
                response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
            )
            
            # Resolver for the Mutation "addDemo" that puts the item into the DynamoDb table.
            demo_dS.create_resolver(
                type_name="Mutation",
                field_name="addDemo",
                request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
                    appsync.PrimaryKey.partition("id").auto(),
                    appsync.Values.projecting("input")),
                response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
            )
        '''
        if isinstance(api_key_config, dict):
            api_key_config = ApiKeyConfig(**api_key_config)
        if isinstance(lambda_authorizer_config, dict):
            lambda_authorizer_config = LambdaAuthorizerConfig(**lambda_authorizer_config)
        if isinstance(open_id_connect_config, dict):
            open_id_connect_config = OpenIdConnectConfig(**open_id_connect_config)
        if isinstance(user_pool_config, dict):
            user_pool_config = UserPoolConfig(**user_pool_config)
        self._values: typing.Dict[str, typing.Any] = {
            "authorization_type": authorization_type,
        }
        if api_key_config is not None:
            self._values["api_key_config"] = api_key_config
        if lambda_authorizer_config is not None:
            self._values["lambda_authorizer_config"] = lambda_authorizer_config
        if open_id_connect_config is not None:
            self._values["open_id_connect_config"] = open_id_connect_config
        if user_pool_config is not None:
            self._values["user_pool_config"] = user_pool_config

    @builtins.property
    def authorization_type(self) -> "AuthorizationType":
        '''(experimental) One of possible four values AppSync supports.

        :default: - ``AuthorizationType.API_KEY``

        :see: https://docs.aws.amazon.com/appsync/latest/devguide/security.html
        :stability: experimental
        '''
        result = self._values.get("authorization_type")
        assert result is not None, "Required property 'authorization_type' is missing"
        return typing.cast("AuthorizationType", result)

    @builtins.property
    def api_key_config(self) -> typing.Optional[ApiKeyConfig]:
        '''(experimental) If authorizationType is ``AuthorizationType.API_KEY``, this option can be configured.

        :default: - name: 'DefaultAPIKey' | description: 'Default API Key created by CDK'

        :stability: experimental
        '''
        result = self._values.get("api_key_config")
        return typing.cast(typing.Optional[ApiKeyConfig], result)

    @builtins.property
    def lambda_authorizer_config(self) -> typing.Optional["LambdaAuthorizerConfig"]:
        '''(experimental) If authorizationType is ``AuthorizationType.LAMBDA``, this option is required.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("lambda_authorizer_config")
        return typing.cast(typing.Optional["LambdaAuthorizerConfig"], result)

    @builtins.property
    def open_id_connect_config(self) -> typing.Optional["OpenIdConnectConfig"]:
        '''(experimental) If authorizationType is ``AuthorizationType.OIDC``, this option is required.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("open_id_connect_config")
        return typing.cast(typing.Optional["OpenIdConnectConfig"], result)

    @builtins.property
    def user_pool_config(self) -> typing.Optional["UserPoolConfig"]:
        '''(experimental) If authorizationType is ``AuthorizationType.USER_POOL``, this option is required.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("user_pool_config")
        return typing.cast(typing.Optional["UserPoolConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthorizationMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-appsync-alpha.AuthorizationType")
class AuthorizationType(enum.Enum):
    '''(experimental) enum with all possible values for AppSync authorization type.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        api = appsync.GraphqlApi(self, "Api",
            name="demo",
            schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql")),
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.IAM
                )
            ),
            xray_enabled=True
        )
        
        demo_table = dynamodb.Table(self, "DemoTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        demo_dS = api.add_dynamo_db_data_source("demoDataSource", demo_table)
        
        # Resolver for the Query "getDemos" that scans the DynamoDb table and returns the entire list.
        demo_dS.create_resolver(
            type_name="Query",
            field_name="getDemos",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
        )
        
        # Resolver for the Mutation "addDemo" that puts the item into the DynamoDb table.
        demo_dS.create_resolver(
            type_name="Mutation",
            field_name="addDemo",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
                appsync.PrimaryKey.partition("id").auto(),
                appsync.Values.projecting("input")),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
        )
    '''

    API_KEY = "API_KEY"
    '''(experimental) API Key authorization type.

    :stability: experimental
    '''
    IAM = "IAM"
    '''(experimental) AWS IAM authorization type.

    Can be used with Cognito Identity Pool federated credentials

    :stability: experimental
    '''
    USER_POOL = "USER_POOL"
    '''(experimental) Cognito User Pool authorization type.

    :stability: experimental
    '''
    OIDC = "OIDC"
    '''(experimental) OpenID Connect authorization type.

    :stability: experimental
    '''
    LAMBDA = "LAMBDA"
    '''(experimental) Lambda authorization type.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.AwsIamConfig",
    jsii_struct_bases=[],
    name_mapping={
        "signing_region": "signingRegion",
        "signing_service_name": "signingServiceName",
    },
)
class AwsIamConfig:
    def __init__(
        self,
        *,
        signing_region: builtins.str,
        signing_service_name: builtins.str,
    ) -> None:
        '''(experimental) The authorization config in case the HTTP endpoint requires authorization.

        :param signing_region: (experimental) The signing region for AWS IAM authorization.
        :param signing_service_name: (experimental) The signing service name for AWS IAM authorization.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            api = appsync.GraphqlApi(self, "api",
                name="api",
                schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql"))
            )
            
            http_ds = api.add_http_data_source("ds", "https://states.amazonaws.com",
                name="httpDsWithStepF",
                description="from appsync to StepFunctions Workflow",
                authorization_config=appsync.AwsIamConfig(
                    signing_region="us-east-1",
                    signing_service_name="states"
                )
            )
            
            http_ds.create_resolver(
                type_name="Mutation",
                field_name="callStepFunction",
                request_mapping_template=appsync.MappingTemplate.from_file("request.vtl"),
                response_mapping_template=appsync.MappingTemplate.from_file("response.vtl")
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "signing_region": signing_region,
            "signing_service_name": signing_service_name,
        }

    @builtins.property
    def signing_region(self) -> builtins.str:
        '''(experimental) The signing region for AWS IAM authorization.

        :stability: experimental
        '''
        result = self._values.get("signing_region")
        assert result is not None, "Required property 'signing_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def signing_service_name(self) -> builtins.str:
        '''(experimental) The signing service name for AWS IAM authorization.

        :stability: experimental
        '''
        result = self._values.get("signing_service_name")
        assert result is not None, "Required property 'signing_service_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsIamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.BaseAppsyncFunctionProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "description": "description",
        "request_mapping_template": "requestMappingTemplate",
        "response_mapping_template": "responseMappingTemplate",
    },
)
class BaseAppsyncFunctionProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        request_mapping_template: typing.Optional["MappingTemplate"] = None,
        response_mapping_template: typing.Optional["MappingTemplate"] = None,
    ) -> None:
        '''(experimental) the base properties for AppSync Functions.

        :param name: (experimental) the name of the AppSync Function.
        :param description: (experimental) the description for this AppSync Function. Default: - no description
        :param request_mapping_template: (experimental) the request mapping template for the AppSync Function. Default: - no request mapping template
        :param response_mapping_template: (experimental) the response mapping template for the AppSync Function. Default: - no response mapping template

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            # mapping_template: appsync_alpha.MappingTemplate
            
            base_appsync_function_props = appsync_alpha.BaseAppsyncFunctionProps(
                name="name",
            
                # the properties below are optional
                description="description",
                request_mapping_template=mapping_template,
                response_mapping_template=mapping_template
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if description is not None:
            self._values["description"] = description
        if request_mapping_template is not None:
            self._values["request_mapping_template"] = request_mapping_template
        if response_mapping_template is not None:
            self._values["response_mapping_template"] = response_mapping_template

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) the name of the AppSync Function.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) the description for this AppSync Function.

        :default: - no description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_mapping_template(self) -> typing.Optional["MappingTemplate"]:
        '''(experimental) the request mapping template for the AppSync Function.

        :default: - no request mapping template

        :stability: experimental
        '''
        result = self._values.get("request_mapping_template")
        return typing.cast(typing.Optional["MappingTemplate"], result)

    @builtins.property
    def response_mapping_template(self) -> typing.Optional["MappingTemplate"]:
        '''(experimental) the response mapping template for the AppSync Function.

        :default: - no response mapping template

        :stability: experimental
        '''
        result = self._values.get("response_mapping_template")
        return typing.cast(typing.Optional["MappingTemplate"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseAppsyncFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BaseDataSource(
    constructs.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-appsync-alpha.BaseDataSource",
):
    '''(experimental) Abstract AppSync datasource implementation.

    Do not use directly but use subclasses for concrete datasources

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        # dummy_request: appsync.MappingTemplate
        # dummy_response: appsync.MappingTemplate
        
        info = appsync.ObjectType("Info",
            definition={
                "node": appsync.ResolvableField(
                    return_type=appsync.GraphqlType.string(),
                    args={
                        "id": appsync.GraphqlType.string()
                    },
                    data_source=api.add_none_data_source("none"),
                    request_mapping_template=dummy_request,
                    response_mapping_template=dummy_response
                )
            }
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: "BackedDataSourceProps",
        *,
        type: builtins.str,
        dynamo_db_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.DynamoDBConfigProperty, aws_cdk.IResolvable]] = None,
        elasticsearch_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.ElasticsearchConfigProperty, aws_cdk.IResolvable]] = None,
        http_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.HttpConfigProperty, aws_cdk.IResolvable]] = None,
        lambda_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.LambdaConfigProperty, aws_cdk.IResolvable]] = None,
        relational_database_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.RelationalDatabaseConfigProperty, aws_cdk.IResolvable]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        :param type: (experimental) the type of the AppSync datasource.
        :param dynamo_db_config: (experimental) configuration for DynamoDB Datasource. Default: - No config
        :param elasticsearch_config: (experimental) configuration for Elasticsearch Datasource. Default: - No config
        :param http_config: (experimental) configuration for HTTP Datasource. Default: - No config
        :param lambda_config: (experimental) configuration for Lambda Datasource. Default: - No config
        :param relational_database_config: (experimental) configuration for RDS Datasource. Default: - No config

        :stability: experimental
        '''
        extended = ExtendedDataSourceProps(
            type=type,
            dynamo_db_config=dynamo_db_config,
            elasticsearch_config=elasticsearch_config,
            http_config=http_config,
            lambda_config=lambda_config,
            relational_database_config=relational_database_config,
        )

        jsii.create(self.__class__, self, [scope, id, props, extended])

    @jsii.member(jsii_name="createFunction")
    def create_function(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        request_mapping_template: typing.Optional["MappingTemplate"] = None,
        response_mapping_template: typing.Optional["MappingTemplate"] = None,
    ) -> "AppsyncFunction":
        '''(experimental) creates a new appsync function for this datasource and API using the given properties.

        :param name: (experimental) the name of the AppSync Function.
        :param description: (experimental) the description for this AppSync Function. Default: - no description
        :param request_mapping_template: (experimental) the request mapping template for the AppSync Function. Default: - no request mapping template
        :param response_mapping_template: (experimental) the response mapping template for the AppSync Function. Default: - no response mapping template

        :stability: experimental
        '''
        props = BaseAppsyncFunctionProps(
            name=name,
            description=description,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
        )

        return typing.cast("AppsyncFunction", jsii.invoke(self, "createFunction", [props]))

    @jsii.member(jsii_name="createResolver")
    def create_resolver(
        self,
        *,
        field_name: builtins.str,
        type_name: builtins.str,
        caching_config: typing.Optional["CachingConfig"] = None,
        pipeline_config: typing.Optional[typing.Sequence["IAppsyncFunction"]] = None,
        request_mapping_template: typing.Optional["MappingTemplate"] = None,
        response_mapping_template: typing.Optional["MappingTemplate"] = None,
    ) -> "Resolver":
        '''(experimental) creates a new resolver for this datasource and API using the given properties.

        :param field_name: (experimental) name of the GraphQL field in the given type this resolver is attached to.
        :param type_name: (experimental) name of the GraphQL type this resolver is attached to.
        :param caching_config: (experimental) The caching configuration for this resolver. Default: - No caching configuration
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array | undefined sets resolver to be of kind, unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template

        :stability: experimental
        '''
        props = BaseResolverProps(
            field_name=field_name,
            type_name=type_name,
            caching_config=caching_config,
            pipeline_config=pipeline_config,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
        )

        return typing.cast("Resolver", jsii.invoke(self, "createResolver", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ds")
    def ds(self) -> aws_cdk.aws_appsync.CfnDataSource:
        '''(experimental) the underlying CFN data source resource.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_appsync.CfnDataSource, jsii.get(self, "ds"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) the name of the data source.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="api")
    def _api(self) -> "IGraphqlApi":
        '''
        :stability: experimental
        '''
        return typing.cast("IGraphqlApi", jsii.get(self, "api"))

    @_api.setter
    def _api(self, value: "IGraphqlApi") -> None:
        jsii.set(self, "api", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceRole")
    def _service_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], jsii.get(self, "serviceRole"))

    @_service_role.setter
    def _service_role(self, value: typing.Optional[aws_cdk.aws_iam.IRole]) -> None:
        jsii.set(self, "serviceRole", value)


class _BaseDataSourceProxy(BaseDataSource):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseDataSource).__jsii_proxy_class__ = lambda : _BaseDataSourceProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.BaseDataSourceProps",
    jsii_struct_bases=[],
    name_mapping={"api": "api", "description": "description", "name": "name"},
)
class BaseDataSourceProps:
    def __init__(
        self,
        *,
        api: "IGraphqlApi",
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Base properties for an AppSync datasource.

        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            # graphql_api: appsync_alpha.GraphqlApi
            
            base_data_source_props = appsync_alpha.BaseDataSourceProps(
                api=graphql_api,
            
                # the properties below are optional
                description="description",
                name="name"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api": api,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def api(self) -> "IGraphqlApi":
        '''(experimental) The API to attach this data source to.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast("IGraphqlApi", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) the description of the data source.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the data source.

        :default: - id of data source

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseDataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.BaseResolverProps",
    jsii_struct_bases=[],
    name_mapping={
        "field_name": "fieldName",
        "type_name": "typeName",
        "caching_config": "cachingConfig",
        "pipeline_config": "pipelineConfig",
        "request_mapping_template": "requestMappingTemplate",
        "response_mapping_template": "responseMappingTemplate",
    },
)
class BaseResolverProps:
    def __init__(
        self,
        *,
        field_name: builtins.str,
        type_name: builtins.str,
        caching_config: typing.Optional["CachingConfig"] = None,
        pipeline_config: typing.Optional[typing.Sequence["IAppsyncFunction"]] = None,
        request_mapping_template: typing.Optional["MappingTemplate"] = None,
        response_mapping_template: typing.Optional["MappingTemplate"] = None,
    ) -> None:
        '''(experimental) Basic properties for an AppSync resolver.

        :param field_name: (experimental) name of the GraphQL field in the given type this resolver is attached to.
        :param type_name: (experimental) name of the GraphQL type this resolver is attached to.
        :param caching_config: (experimental) The caching configuration for this resolver. Default: - No caching configuration
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array | undefined sets resolver to be of kind, unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Build a data source for AppSync to access the database.
            # api: appsync.GraphqlApi
            # Create username and password secret for DB Cluster
            secret = rds.DatabaseSecret(self, "AuroraSecret",
                username="clusteradmin"
            )
            
            # The VPC to place the cluster in
            vpc = ec2.Vpc(self, "AuroraVpc")
            
            # Create the serverless cluster, provide all values needed to customise the database.
            cluster = rds.ServerlessCluster(self, "AuroraCluster",
                engine=rds.DatabaseClusterEngine.AURORA_MYSQL,
                vpc=vpc,
                credentials={"username": "clusteradmin"},
                cluster_identifier="db-endpoint-test",
                default_database_name="demos"
            )
            rds_dS = api.add_rds_data_source("rds", cluster, secret, "demos")
            
            # Set up a resolver for an RDS query.
            rds_dS.create_resolver(
                type_name="Query",
                field_name="getDemosRds",
                request_mapping_template=appsync.MappingTemplate.from_string("""
                      {
                        "version": "2018-05-29",
                        "statements": [
                          "SELECT * FROM demos"
                        ]
                      }
                      """),
                response_mapping_template=appsync.MappingTemplate.from_string("""
                        $utils.toJson($utils.rds.toJsonObject($ctx.result)[0])
                      """)
            )
            
            # Set up a resolver for an RDS mutation.
            rds_dS.create_resolver(
                type_name="Mutation",
                field_name="addDemoRds",
                request_mapping_template=appsync.MappingTemplate.from_string("""
                      {
                        "version": "2018-05-29",
                        "statements": [
                          "INSERT INTO demos VALUES (:id, :version)",
                          "SELECT * WHERE id = :id"
                        ],
                        "variableMap": {
                          ":id": $util.toJson($util.autoId()),
                          ":version": $util.toJson($ctx.args.version)
                        }
                      }
                      """),
                response_mapping_template=appsync.MappingTemplate.from_string("""
                        $utils.toJson($utils.rds.toJsonObject($ctx.result)[1][0])
                      """)
            )
        '''
        if isinstance(caching_config, dict):
            caching_config = CachingConfig(**caching_config)
        self._values: typing.Dict[str, typing.Any] = {
            "field_name": field_name,
            "type_name": type_name,
        }
        if caching_config is not None:
            self._values["caching_config"] = caching_config
        if pipeline_config is not None:
            self._values["pipeline_config"] = pipeline_config
        if request_mapping_template is not None:
            self._values["request_mapping_template"] = request_mapping_template
        if response_mapping_template is not None:
            self._values["response_mapping_template"] = response_mapping_template

    @builtins.property
    def field_name(self) -> builtins.str:
        '''(experimental) name of the GraphQL field in the given type this resolver is attached to.

        :stability: experimental
        '''
        result = self._values.get("field_name")
        assert result is not None, "Required property 'field_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type_name(self) -> builtins.str:
        '''(experimental) name of the GraphQL type this resolver is attached to.

        :stability: experimental
        '''
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def caching_config(self) -> typing.Optional["CachingConfig"]:
        '''(experimental) The caching configuration for this resolver.

        :default: - No caching configuration

        :stability: experimental
        '''
        result = self._values.get("caching_config")
        return typing.cast(typing.Optional["CachingConfig"], result)

    @builtins.property
    def pipeline_config(self) -> typing.Optional[typing.List["IAppsyncFunction"]]:
        '''(experimental) configuration of the pipeline resolver.

        :default:

        - no pipeline resolver configuration
        An empty array | undefined sets resolver to be of kind, unit

        :stability: experimental
        '''
        result = self._values.get("pipeline_config")
        return typing.cast(typing.Optional[typing.List["IAppsyncFunction"]], result)

    @builtins.property
    def request_mapping_template(self) -> typing.Optional["MappingTemplate"]:
        '''(experimental) The request mapping template for this resolver.

        :default: - No mapping template

        :stability: experimental
        '''
        result = self._values.get("request_mapping_template")
        return typing.cast(typing.Optional["MappingTemplate"], result)

    @builtins.property
    def response_mapping_template(self) -> typing.Optional["MappingTemplate"]:
        '''(experimental) The response mapping template for this resolver.

        :default: - No mapping template

        :stability: experimental
        '''
        result = self._values.get("response_mapping_template")
        return typing.cast(typing.Optional["MappingTemplate"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseResolverProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.BaseTypeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "is_list": "isList",
        "is_required": "isRequired",
        "is_required_list": "isRequiredList",
    },
)
class BaseTypeOptions:
    def __init__(
        self,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Base options for GraphQL Types.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        :exampleMetadata: infused
        :option: isRequiredList - is this attribute a non-nullable list

        Example::

            api = appsync.GraphqlApi(self, "Api",
                name="demo"
            )
            demo = appsync.ObjectType("Demo",
                definition={
                    "id": appsync.GraphqlType.string(is_required=True),
                    "version": appsync.GraphqlType.string(is_required=True)
                }
            )
            
            api.add_type(demo)
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if is_list is not None:
            self._values["is_list"] = is_list
        if is_required is not None:
            self._values["is_required"] = is_required
        if is_required_list is not None:
            self._values["is_required_list"] = is_required_list

    @builtins.property
    def is_list(self) -> typing.Optional[builtins.bool]:
        '''(experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type].

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("is_list")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def is_required(self) -> typing.Optional[builtins.bool]:
        '''(experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type!

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("is_required")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def is_required_list(self) -> typing.Optional[builtins.bool]:
        '''(experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]!

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("is_required_list")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseTypeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.CachingConfig",
    jsii_struct_bases=[],
    name_mapping={"ttl": "ttl", "caching_keys": "cachingKeys"},
)
class CachingConfig:
    def __init__(
        self,
        *,
        ttl: aws_cdk.Duration,
        caching_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) CachingConfig for AppSync resolvers.

        :param ttl: (experimental) The TTL in seconds for a resolver that has caching enabled. Valid values are between 1 and 3600 seconds.
        :param caching_keys: (experimental) The caching keys for a resolver that has caching enabled. Valid values are entries from the $context.arguments, $context.source, and $context.identity maps. Default: - No caching keys

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            import aws_cdk as cdk
            
            caching_config = appsync_alpha.CachingConfig(
                ttl=cdk.Duration.minutes(30),
            
                # the properties below are optional
                caching_keys=["cachingKeys"]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "ttl": ttl,
        }
        if caching_keys is not None:
            self._values["caching_keys"] = caching_keys

    @builtins.property
    def ttl(self) -> aws_cdk.Duration:
        '''(experimental) The TTL in seconds for a resolver that has caching enabled.

        Valid values are between 1 and 3600 seconds.

        :stability: experimental
        '''
        result = self._values.get("ttl")
        assert result is not None, "Required property 'ttl' is missing"
        return typing.cast(aws_cdk.Duration, result)

    @builtins.property
    def caching_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The caching keys for a resolver that has caching enabled.

        Valid values are entries from the $context.arguments, $context.source, and $context.identity maps.

        :default: - No caching keys

        :stability: experimental
        '''
        result = self._values.get("caching_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CachingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.DataSourceOptions",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "name": "name"},
)
class DataSourceOptions:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Optional configuration for data sources.

        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            data_source_options = appsync_alpha.DataSourceOptions(
                description="description",
                name="name"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the data source.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the data source, overrides the id given by cdk.

        :default: - generated by cdk given the id

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataSourceOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Directive(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.Directive",
):
    '''(experimental) Directives for types.

    i.e. @aws_iam or @aws_subscribe

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        # film: appsync.InterfaceType
        
        
        api.add_subscription("addedFilm", appsync.Field(
            return_type=film.attribute(),
            args={"id": appsync.GraphqlType.id(is_required=True)},
            directives=[appsync.Directive.subscribe("addFilm")]
        ))
    '''

    @jsii.member(jsii_name="apiKey") # type: ignore[misc]
    @builtins.classmethod
    def api_key(cls) -> "Directive":
        '''(experimental) Add the @aws_api_key directive.

        :stability: experimental
        '''
        return typing.cast("Directive", jsii.sinvoke(cls, "apiKey", []))

    @jsii.member(jsii_name="cognito") # type: ignore[misc]
    @builtins.classmethod
    def cognito(cls, *groups: builtins.str) -> "Directive":
        '''(experimental) Add the @aws_auth or @aws_cognito_user_pools directive.

        :param groups: the groups to allow access to.

        :stability: experimental
        '''
        return typing.cast("Directive", jsii.sinvoke(cls, "cognito", [*groups]))

    @jsii.member(jsii_name="custom") # type: ignore[misc]
    @builtins.classmethod
    def custom(cls, statement: builtins.str) -> "Directive":
        '''(experimental) Add a custom directive.

        :param statement: - the directive statement to append.

        :stability: experimental
        '''
        return typing.cast("Directive", jsii.sinvoke(cls, "custom", [statement]))

    @jsii.member(jsii_name="iam") # type: ignore[misc]
    @builtins.classmethod
    def iam(cls) -> "Directive":
        '''(experimental) Add the @aws_iam directive.

        :stability: experimental
        '''
        return typing.cast("Directive", jsii.sinvoke(cls, "iam", []))

    @jsii.member(jsii_name="oidc") # type: ignore[misc]
    @builtins.classmethod
    def oidc(cls) -> "Directive":
        '''(experimental) Add the @aws_oidc directive.

        :stability: experimental
        '''
        return typing.cast("Directive", jsii.sinvoke(cls, "oidc", []))

    @jsii.member(jsii_name="subscribe") # type: ignore[misc]
    @builtins.classmethod
    def subscribe(cls, *mutations: builtins.str) -> "Directive":
        '''(experimental) Add the @aws_subscribe directive.

        Only use for top level Subscription type.

        :param mutations: the mutation fields to link to.

        :stability: experimental
        '''
        return typing.cast("Directive", jsii.sinvoke(cls, "subscribe", [*mutations]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the directive statement.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> typing.Optional[AuthorizationType]:
        '''(experimental) The authorization type of this directive.

        :default: - not an authorization directive

        :stability: experimental
        '''
        return typing.cast(typing.Optional[AuthorizationType], jsii.get(self, "mode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mutationFields")
    def mutation_fields(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Mutation fields for a subscription directive.

        :default: - not a subscription directive

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "mutationFields"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modes")
    def _modes(self) -> typing.Optional[typing.List[AuthorizationType]]:
        '''(experimental) the authorization modes for this intermediate type.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[AuthorizationType]], jsii.get(self, "modes"))

    @_modes.setter
    def _modes(self, value: typing.Optional[typing.List[AuthorizationType]]) -> None:
        jsii.set(self, "modes", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.EnumTypeOptions",
    jsii_struct_bases=[],
    name_mapping={"definition": "definition"},
)
class EnumTypeOptions:
    def __init__(self, *, definition: typing.Sequence[builtins.str]) -> None:
        '''(experimental) Properties for configuring an Enum Type.

        :param definition: (experimental) the attributes of this type.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # api: appsync.GraphqlApi
            
            episode = appsync.EnumType("Episode",
                definition=["NEWHOPE", "EMPIRE", "JEDI"
                ]
            )
            api.add_type(episode)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "definition": definition,
        }

    @builtins.property
    def definition(self) -> typing.List[builtins.str]:
        '''(experimental) the attributes of this type.

        :stability: experimental
        '''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnumTypeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.ExtendedDataSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "dynamo_db_config": "dynamoDbConfig",
        "elasticsearch_config": "elasticsearchConfig",
        "http_config": "httpConfig",
        "lambda_config": "lambdaConfig",
        "relational_database_config": "relationalDatabaseConfig",
    },
)
class ExtendedDataSourceProps:
    def __init__(
        self,
        *,
        type: builtins.str,
        dynamo_db_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.DynamoDBConfigProperty, aws_cdk.IResolvable]] = None,
        elasticsearch_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.ElasticsearchConfigProperty, aws_cdk.IResolvable]] = None,
        http_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.HttpConfigProperty, aws_cdk.IResolvable]] = None,
        lambda_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.LambdaConfigProperty, aws_cdk.IResolvable]] = None,
        relational_database_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.RelationalDatabaseConfigProperty, aws_cdk.IResolvable]] = None,
    ) -> None:
        '''(experimental) props used by implementations of BaseDataSource to provide configuration.

        Should not be used directly.

        :param type: (experimental) the type of the AppSync datasource.
        :param dynamo_db_config: (experimental) configuration for DynamoDB Datasource. Default: - No config
        :param elasticsearch_config: (experimental) configuration for Elasticsearch Datasource. Default: - No config
        :param http_config: (experimental) configuration for HTTP Datasource. Default: - No config
        :param lambda_config: (experimental) configuration for Lambda Datasource. Default: - No config
        :param relational_database_config: (experimental) configuration for RDS Datasource. Default: - No config

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            extended_data_source_props = appsync_alpha.ExtendedDataSourceProps(
                type="type",
            
                # the properties below are optional
                dynamo_db_config=DynamoDBConfigProperty(
                    aws_region="awsRegion",
                    table_name="tableName",
            
                    # the properties below are optional
                    delta_sync_config=DeltaSyncConfigProperty(
                        base_table_ttl="baseTableTtl",
                        delta_sync_table_name="deltaSyncTableName",
                        delta_sync_table_ttl="deltaSyncTableTtl"
                    ),
                    use_caller_credentials=False,
                    versioned=False
                ),
                elasticsearch_config=ElasticsearchConfigProperty(
                    aws_region="awsRegion",
                    endpoint="endpoint"
                ),
                http_config=HttpConfigProperty(
                    endpoint="endpoint",
            
                    # the properties below are optional
                    authorization_config=AuthorizationConfigProperty(
                        authorization_type="authorizationType",
            
                        # the properties below are optional
                        aws_iam_config=AwsIamConfigProperty(
                            signing_region="signingRegion",
                            signing_service_name="signingServiceName"
                        )
                    )
                ),
                lambda_config=LambdaConfigProperty(
                    lambda_function_arn="lambdaFunctionArn"
                ),
                relational_database_config=RelationalDatabaseConfigProperty(
                    relational_database_source_type="relationalDatabaseSourceType",
            
                    # the properties below are optional
                    rds_http_endpoint_config=RdsHttpEndpointConfigProperty(
                        aws_region="awsRegion",
                        aws_secret_store_arn="awsSecretStoreArn",
                        db_cluster_identifier="dbClusterIdentifier",
            
                        # the properties below are optional
                        database_name="databaseName",
                        schema="schema"
                    )
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if dynamo_db_config is not None:
            self._values["dynamo_db_config"] = dynamo_db_config
        if elasticsearch_config is not None:
            self._values["elasticsearch_config"] = elasticsearch_config
        if http_config is not None:
            self._values["http_config"] = http_config
        if lambda_config is not None:
            self._values["lambda_config"] = lambda_config
        if relational_database_config is not None:
            self._values["relational_database_config"] = relational_database_config

    @builtins.property
    def type(self) -> builtins.str:
        '''(experimental) the type of the AppSync datasource.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dynamo_db_config(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.DynamoDBConfigProperty, aws_cdk.IResolvable]]:
        '''(experimental) configuration for DynamoDB Datasource.

        :default: - No config

        :stability: experimental
        '''
        result = self._values.get("dynamo_db_config")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.DynamoDBConfigProperty, aws_cdk.IResolvable]], result)

    @builtins.property
    def elasticsearch_config(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.ElasticsearchConfigProperty, aws_cdk.IResolvable]]:
        '''(experimental) configuration for Elasticsearch Datasource.

        :default: - No config

        :stability: experimental
        '''
        result = self._values.get("elasticsearch_config")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.ElasticsearchConfigProperty, aws_cdk.IResolvable]], result)

    @builtins.property
    def http_config(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.HttpConfigProperty, aws_cdk.IResolvable]]:
        '''(experimental) configuration for HTTP Datasource.

        :default: - No config

        :stability: experimental
        '''
        result = self._values.get("http_config")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.HttpConfigProperty, aws_cdk.IResolvable]], result)

    @builtins.property
    def lambda_config(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.LambdaConfigProperty, aws_cdk.IResolvable]]:
        '''(experimental) configuration for Lambda Datasource.

        :default: - No config

        :stability: experimental
        '''
        result = self._values.get("lambda_config")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.LambdaConfigProperty, aws_cdk.IResolvable]], result)

    @builtins.property
    def relational_database_config(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.RelationalDatabaseConfigProperty, aws_cdk.IResolvable]]:
        '''(experimental) configuration for RDS Datasource.

        :default: - No config

        :stability: experimental
        '''
        result = self._values.get("relational_database_config")
        return typing.cast(typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.RelationalDatabaseConfigProperty, aws_cdk.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExtendedDataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.ExtendedResolverProps",
    jsii_struct_bases=[BaseResolverProps],
    name_mapping={
        "field_name": "fieldName",
        "type_name": "typeName",
        "caching_config": "cachingConfig",
        "pipeline_config": "pipelineConfig",
        "request_mapping_template": "requestMappingTemplate",
        "response_mapping_template": "responseMappingTemplate",
        "data_source": "dataSource",
    },
)
class ExtendedResolverProps(BaseResolverProps):
    def __init__(
        self,
        *,
        field_name: builtins.str,
        type_name: builtins.str,
        caching_config: typing.Optional[CachingConfig] = None,
        pipeline_config: typing.Optional[typing.Sequence["IAppsyncFunction"]] = None,
        request_mapping_template: typing.Optional["MappingTemplate"] = None,
        response_mapping_template: typing.Optional["MappingTemplate"] = None,
        data_source: typing.Optional[BaseDataSource] = None,
    ) -> None:
        '''(experimental) Additional property for an AppSync resolver for data source reference.

        :param field_name: (experimental) name of the GraphQL field in the given type this resolver is attached to.
        :param type_name: (experimental) name of the GraphQL type this resolver is attached to.
        :param caching_config: (experimental) The caching configuration for this resolver. Default: - No caching configuration
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array | undefined sets resolver to be of kind, unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template
        :param data_source: (experimental) The data source this resolver is using. Default: - No datasource

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            import aws_cdk as cdk
            
            # appsync_function: appsync_alpha.AppsyncFunction
            # base_data_source: appsync_alpha.BaseDataSource
            # mapping_template: appsync_alpha.MappingTemplate
            
            extended_resolver_props = appsync_alpha.ExtendedResolverProps(
                field_name="fieldName",
                type_name="typeName",
            
                # the properties below are optional
                caching_config=appsync_alpha.CachingConfig(
                    ttl=cdk.Duration.minutes(30),
            
                    # the properties below are optional
                    caching_keys=["cachingKeys"]
                ),
                data_source=base_data_source,
                pipeline_config=[appsync_function],
                request_mapping_template=mapping_template,
                response_mapping_template=mapping_template
            )
        '''
        if isinstance(caching_config, dict):
            caching_config = CachingConfig(**caching_config)
        self._values: typing.Dict[str, typing.Any] = {
            "field_name": field_name,
            "type_name": type_name,
        }
        if caching_config is not None:
            self._values["caching_config"] = caching_config
        if pipeline_config is not None:
            self._values["pipeline_config"] = pipeline_config
        if request_mapping_template is not None:
            self._values["request_mapping_template"] = request_mapping_template
        if response_mapping_template is not None:
            self._values["response_mapping_template"] = response_mapping_template
        if data_source is not None:
            self._values["data_source"] = data_source

    @builtins.property
    def field_name(self) -> builtins.str:
        '''(experimental) name of the GraphQL field in the given type this resolver is attached to.

        :stability: experimental
        '''
        result = self._values.get("field_name")
        assert result is not None, "Required property 'field_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type_name(self) -> builtins.str:
        '''(experimental) name of the GraphQL type this resolver is attached to.

        :stability: experimental
        '''
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def caching_config(self) -> typing.Optional[CachingConfig]:
        '''(experimental) The caching configuration for this resolver.

        :default: - No caching configuration

        :stability: experimental
        '''
        result = self._values.get("caching_config")
        return typing.cast(typing.Optional[CachingConfig], result)

    @builtins.property
    def pipeline_config(self) -> typing.Optional[typing.List["IAppsyncFunction"]]:
        '''(experimental) configuration of the pipeline resolver.

        :default:

        - no pipeline resolver configuration
        An empty array | undefined sets resolver to be of kind, unit

        :stability: experimental
        '''
        result = self._values.get("pipeline_config")
        return typing.cast(typing.Optional[typing.List["IAppsyncFunction"]], result)

    @builtins.property
    def request_mapping_template(self) -> typing.Optional["MappingTemplate"]:
        '''(experimental) The request mapping template for this resolver.

        :default: - No mapping template

        :stability: experimental
        '''
        result = self._values.get("request_mapping_template")
        return typing.cast(typing.Optional["MappingTemplate"], result)

    @builtins.property
    def response_mapping_template(self) -> typing.Optional["MappingTemplate"]:
        '''(experimental) The response mapping template for this resolver.

        :default: - No mapping template

        :stability: experimental
        '''
        result = self._values.get("response_mapping_template")
        return typing.cast(typing.Optional["MappingTemplate"], result)

    @builtins.property
    def data_source(self) -> typing.Optional[BaseDataSource]:
        '''(experimental) The data source this resolver is using.

        :default: - No datasource

        :stability: experimental
        '''
        result = self._values.get("data_source")
        return typing.cast(typing.Optional[BaseDataSource], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExtendedResolverProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-appsync-alpha.FieldLogLevel")
class FieldLogLevel(enum.Enum):
    '''(experimental) log-level for fields in AppSync.

    :stability: experimental
    '''

    NONE = "NONE"
    '''(experimental) No logging.

    :stability: experimental
    '''
    ERROR = "ERROR"
    '''(experimental) Error logging.

    :stability: experimental
    '''
    ALL = "ALL"
    '''(experimental) All logging.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.FieldOptions",
    jsii_struct_bases=[],
    name_mapping={
        "return_type": "returnType",
        "args": "args",
        "directives": "directives",
    },
)
class FieldOptions:
    def __init__(
        self,
        *,
        return_type: "GraphqlType",
        args: typing.Optional[typing.Mapping[builtins.str, "GraphqlType"]] = None,
        directives: typing.Optional[typing.Sequence[Directive]] = None,
    ) -> None:
        '''(experimental) Properties for configuring a field.

        :param return_type: (experimental) The return type for this field.
        :param args: (experimental) The arguments for this field. i.e. type Example (first: String second: String) {} - where 'first' and 'second' are key values for args and 'String' is the GraphqlType Default: - no arguments
        :param directives: (experimental) the directives for this field. Default: - no directives

        :stability: experimental
        :exampleMetadata: infused
        :options:

        args - the variables and types that define the arguments

        i.e. { string: GraphqlType, string: GraphqlType }

        Example::

            field = appsync.Field(
                return_type=appsync.GraphqlType.string(),
                args={
                    "argument": appsync.GraphqlType.string()
                }
            )
            type = appsync.InterfaceType("Node",
                definition={"test": field}
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "return_type": return_type,
        }
        if args is not None:
            self._values["args"] = args
        if directives is not None:
            self._values["directives"] = directives

    @builtins.property
    def return_type(self) -> "GraphqlType":
        '''(experimental) The return type for this field.

        :stability: experimental
        '''
        result = self._values.get("return_type")
        assert result is not None, "Required property 'return_type' is missing"
        return typing.cast("GraphqlType", result)

    @builtins.property
    def args(self) -> typing.Optional[typing.Mapping[builtins.str, "GraphqlType"]]:
        '''(experimental) The arguments for this field.

        i.e. type Example (first: String second: String) {}

        - where 'first' and 'second' are key values for args
          and 'String' is the GraphqlType

        :default: - no arguments

        :stability: experimental
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "GraphqlType"]], result)

    @builtins.property
    def directives(self) -> typing.Optional[typing.List[Directive]]:
        '''(experimental) the directives for this field.

        :default: - no directives

        :stability: experimental
        '''
        result = self._values.get("directives")
        return typing.cast(typing.Optional[typing.List[Directive]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FieldOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.GraphqlApiAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "graphql_api_id": "graphqlApiId",
        "graphql_api_arn": "graphqlApiArn",
    },
)
class GraphqlApiAttributes:
    def __init__(
        self,
        *,
        graphql_api_id: builtins.str,
        graphql_api_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attributes for GraphQL imports.

        :param graphql_api_id: (experimental) an unique AWS AppSync GraphQL API identifier i.e. 'lxz775lwdrgcndgz3nurvac7oa'.
        :param graphql_api_arn: (experimental) the arn for the GraphQL Api. Default: - autogenerated arn

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # api: appsync.GraphqlApi
            # table: dynamodb.Table
            
            imported_api = appsync.GraphqlApi.from_graphql_api_attributes(self, "IApi",
                graphql_api_id=api.api_id,
                graphql_api_arn=api.arn
            )
            imported_api.add_dynamo_db_data_source("TableDataSource", table)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "graphql_api_id": graphql_api_id,
        }
        if graphql_api_arn is not None:
            self._values["graphql_api_arn"] = graphql_api_arn

    @builtins.property
    def graphql_api_id(self) -> builtins.str:
        '''(experimental) an unique AWS AppSync GraphQL API identifier i.e. 'lxz775lwdrgcndgz3nurvac7oa'.

        :stability: experimental
        '''
        result = self._values.get("graphql_api_id")
        assert result is not None, "Required property 'graphql_api_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def graphql_api_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) the arn for the GraphQL Api.

        :default: - autogenerated arn

        :stability: experimental
        '''
        result = self._values.get("graphql_api_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GraphqlApiAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.GraphqlApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "authorization_config": "authorizationConfig",
        "log_config": "logConfig",
        "schema": "schema",
        "xray_enabled": "xrayEnabled",
    },
)
class GraphqlApiProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        authorization_config: typing.Optional[AuthorizationConfig] = None,
        log_config: typing.Optional["LogConfig"] = None,
        schema: typing.Optional["Schema"] = None,
        xray_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for an AppSync GraphQL API.

        :param name: (experimental) the name of the GraphQL API.
        :param authorization_config: (experimental) Optional authorization configuration. Default: - API Key authorization
        :param log_config: (experimental) Logging configuration for this api. Default: - None
        :param schema: (experimental) GraphQL schema definition. Specify how you want to define your schema. Schema.fromFile(filePath: string) allows schema definition through schema.graphql file Default: - schema will be generated code-first (i.e. addType, addObjectType, etc.)
        :param xray_enabled: (experimental) A flag indicating whether or not X-Ray tracing is enabled for the GraphQL API. Default: - false

        :stability: experimental
        :exampleMetadata: infused

        Example::

            api = appsync.GraphqlApi(self, "Api",
                name="demo"
            )
            demo = appsync.ObjectType("Demo",
                definition={
                    "id": appsync.GraphqlType.string(is_required=True),
                    "version": appsync.GraphqlType.string(is_required=True)
                }
            )
            
            api.add_type(demo)
        '''
        if isinstance(authorization_config, dict):
            authorization_config = AuthorizationConfig(**authorization_config)
        if isinstance(log_config, dict):
            log_config = LogConfig(**log_config)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if authorization_config is not None:
            self._values["authorization_config"] = authorization_config
        if log_config is not None:
            self._values["log_config"] = log_config
        if schema is not None:
            self._values["schema"] = schema
        if xray_enabled is not None:
            self._values["xray_enabled"] = xray_enabled

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) the name of the GraphQL API.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorization_config(self) -> typing.Optional[AuthorizationConfig]:
        '''(experimental) Optional authorization configuration.

        :default: - API Key authorization

        :stability: experimental
        '''
        result = self._values.get("authorization_config")
        return typing.cast(typing.Optional[AuthorizationConfig], result)

    @builtins.property
    def log_config(self) -> typing.Optional["LogConfig"]:
        '''(experimental) Logging configuration for this api.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("log_config")
        return typing.cast(typing.Optional["LogConfig"], result)

    @builtins.property
    def schema(self) -> typing.Optional["Schema"]:
        '''(experimental) GraphQL schema definition. Specify how you want to define your schema.

        Schema.fromFile(filePath: string) allows schema definition through schema.graphql file

        :default: - schema will be generated code-first (i.e. addType, addObjectType, etc.)

        :stability: experimental
        '''
        result = self._values.get("schema")
        return typing.cast(typing.Optional["Schema"], result)

    @builtins.property
    def xray_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) A flag indicating whether or not X-Ray tracing is enabled for the GraphQL API.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("xray_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GraphqlApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.GraphqlTypeOptions",
    jsii_struct_bases=[BaseTypeOptions],
    name_mapping={
        "is_list": "isList",
        "is_required": "isRequired",
        "is_required_list": "isRequiredList",
        "intermediate_type": "intermediateType",
    },
)
class GraphqlTypeOptions(BaseTypeOptions):
    def __init__(
        self,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
        intermediate_type: typing.Optional["IIntermediateType"] = None,
    ) -> None:
        '''(experimental) Options for GraphQL Types.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false
        :param intermediate_type: (experimental) the intermediate type linked to this attribute. Default: - no intermediate type

        :stability: experimental
        :option: objectType - the object type linked to this attribute
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            # intermediate_type: appsync_alpha.IIntermediateType
            
            graphql_type_options = appsync_alpha.GraphqlTypeOptions(
                intermediate_type=intermediate_type,
                is_list=False,
                is_required=False,
                is_required_list=False
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if is_list is not None:
            self._values["is_list"] = is_list
        if is_required is not None:
            self._values["is_required"] = is_required
        if is_required_list is not None:
            self._values["is_required_list"] = is_required_list
        if intermediate_type is not None:
            self._values["intermediate_type"] = intermediate_type

    @builtins.property
    def is_list(self) -> typing.Optional[builtins.bool]:
        '''(experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type].

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("is_list")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def is_required(self) -> typing.Optional[builtins.bool]:
        '''(experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type!

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("is_required")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def is_required_list(self) -> typing.Optional[builtins.bool]:
        '''(experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]!

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("is_required_list")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def intermediate_type(self) -> typing.Optional["IIntermediateType"]:
        '''(experimental) the intermediate type linked to this attribute.

        :default: - no intermediate type

        :stability: experimental
        '''
        result = self._values.get("intermediate_type")
        return typing.cast(typing.Optional["IIntermediateType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GraphqlTypeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.HttpDataSourceOptions",
    jsii_struct_bases=[DataSourceOptions],
    name_mapping={
        "description": "description",
        "name": "name",
        "authorization_config": "authorizationConfig",
    },
)
class HttpDataSourceOptions(DataSourceOptions):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        authorization_config: typing.Optional[AwsIamConfig] = None,
    ) -> None:
        '''(experimental) Optional configuration for Http data sources.

        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id
        :param authorization_config: (experimental) The authorization config in case the HTTP endpoint requires authorization. Default: - none

        :stability: experimental
        :exampleMetadata: infused

        Example::

            api = appsync.GraphqlApi(self, "api",
                name="api",
                schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql"))
            )
            
            http_ds = api.add_http_data_source("ds", "https://states.amazonaws.com",
                name="httpDsWithStepF",
                description="from appsync to StepFunctions Workflow",
                authorization_config=appsync.AwsIamConfig(
                    signing_region="us-east-1",
                    signing_service_name="states"
                )
            )
            
            http_ds.create_resolver(
                type_name="Mutation",
                field_name="callStepFunction",
                request_mapping_template=appsync.MappingTemplate.from_file("request.vtl"),
                response_mapping_template=appsync.MappingTemplate.from_file("response.vtl")
            )
        '''
        if isinstance(authorization_config, dict):
            authorization_config = AwsIamConfig(**authorization_config)
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if authorization_config is not None:
            self._values["authorization_config"] = authorization_config

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the data source.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the data source, overrides the id given by cdk.

        :default: - generated by cdk given the id

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorization_config(self) -> typing.Optional[AwsIamConfig]:
        '''(experimental) The authorization config in case the HTTP endpoint requires authorization.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("authorization_config")
        return typing.cast(typing.Optional[AwsIamConfig], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpDataSourceOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.HttpDataSourceProps",
    jsii_struct_bases=[BaseDataSourceProps],
    name_mapping={
        "api": "api",
        "description": "description",
        "name": "name",
        "endpoint": "endpoint",
        "authorization_config": "authorizationConfig",
    },
)
class HttpDataSourceProps(BaseDataSourceProps):
    def __init__(
        self,
        *,
        api: "IGraphqlApi",
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        endpoint: builtins.str,
        authorization_config: typing.Optional[AwsIamConfig] = None,
    ) -> None:
        '''(experimental) Properties for an AppSync http datasource.

        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source
        :param endpoint: (experimental) The http endpoint.
        :param authorization_config: (experimental) The authorization config in case the HTTP endpoint requires authorization. Default: - none

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            # graphql_api: appsync_alpha.GraphqlApi
            
            http_data_source_props = appsync_alpha.HttpDataSourceProps(
                api=graphql_api,
                endpoint="endpoint",
            
                # the properties below are optional
                authorization_config=appsync_alpha.AwsIamConfig(
                    signing_region="signingRegion",
                    signing_service_name="signingServiceName"
                ),
                description="description",
                name="name"
            )
        '''
        if isinstance(authorization_config, dict):
            authorization_config = AwsIamConfig(**authorization_config)
        self._values: typing.Dict[str, typing.Any] = {
            "api": api,
            "endpoint": endpoint,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if authorization_config is not None:
            self._values["authorization_config"] = authorization_config

    @builtins.property
    def api(self) -> "IGraphqlApi":
        '''(experimental) The API to attach this data source to.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast("IGraphqlApi", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) the description of the data source.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the data source.

        :default: - id of data source

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint(self) -> builtins.str:
        '''(experimental) The http endpoint.

        :stability: experimental
        '''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorization_config(self) -> typing.Optional[AwsIamConfig]:
        '''(experimental) The authorization config in case the HTTP endpoint requires authorization.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("authorization_config")
        return typing.cast(typing.Optional[AwsIamConfig], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpDataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-appsync-alpha.IAppsyncFunction")
class IAppsyncFunction(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) Interface for AppSync Functions.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''(experimental) the ARN of the AppSync function.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionId")
    def function_id(self) -> builtins.str:
        '''(experimental) the name of this AppSync Function.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IAppsyncFunctionProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) Interface for AppSync Functions.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appsync-alpha.IAppsyncFunction"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''(experimental) the ARN of the AppSync function.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionId")
    def function_id(self) -> builtins.str:
        '''(experimental) the name of this AppSync Function.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "functionId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAppsyncFunction).__jsii_proxy_class__ = lambda : _IAppsyncFunctionProxy


@jsii.interface(jsii_type="@aws-cdk/aws-appsync-alpha.IField")
class IField(typing_extensions.Protocol):
    '''(experimental) A Graphql Field.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isList")
    def is_list(self) -> builtins.bool:
        '''(experimental) property determining if this attribute is a list i.e. if true, attribute would be ``[Type]``.

        :default: false

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isRequired")
    def is_required(self) -> builtins.bool:
        '''(experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be ``Type!`` and this attribute must always have a value.

        :default: false

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isRequiredList")
    def is_required_list(self) -> builtins.bool:
        '''(experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be ``[ Type ]!`` and this attribute's list must always have a value.

        :default: false

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> "Type":
        '''(experimental) the type of attribute.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldOptions")
    def field_options(self) -> typing.Optional["ResolvableFieldOptions"]:
        '''(experimental) The options to make this field resolvable.

        :default: - not a resolvable field

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intermediateType")
    def intermediate_type(self) -> typing.Optional["IIntermediateType"]:
        '''(experimental) the intermediate type linked to this attribute (i.e. an interface or an object).

        :default: - no intermediate type

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="argsToString")
    def args_to_string(self) -> builtins.str:
        '''(experimental) Generate the arguments for this field.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="directivesToString")
    def directives_to_string(
        self,
        modes: typing.Optional[typing.Sequence[AuthorizationType]] = None,
    ) -> builtins.str:
        '''(experimental) Generate the directives for this field.

        :param modes: the authorization modes of the graphql api.

        :default: - no authorization modes

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the string for this attribute.

        :stability: experimental
        '''
        ...


class _IFieldProxy:
    '''(experimental) A Graphql Field.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appsync-alpha.IField"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isList")
    def is_list(self) -> builtins.bool:
        '''(experimental) property determining if this attribute is a list i.e. if true, attribute would be ``[Type]``.

        :default: false

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isList"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isRequired")
    def is_required(self) -> builtins.bool:
        '''(experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be ``Type!`` and this attribute must always have a value.

        :default: false

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isRequired"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isRequiredList")
    def is_required_list(self) -> builtins.bool:
        '''(experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be ``[ Type ]!`` and this attribute's list must always have a value.

        :default: false

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isRequiredList"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> "Type":
        '''(experimental) the type of attribute.

        :stability: experimental
        '''
        return typing.cast("Type", jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldOptions")
    def field_options(self) -> typing.Optional["ResolvableFieldOptions"]:
        '''(experimental) The options to make this field resolvable.

        :default: - not a resolvable field

        :stability: experimental
        '''
        return typing.cast(typing.Optional["ResolvableFieldOptions"], jsii.get(self, "fieldOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intermediateType")
    def intermediate_type(self) -> typing.Optional["IIntermediateType"]:
        '''(experimental) the intermediate type linked to this attribute (i.e. an interface or an object).

        :default: - no intermediate type

        :stability: experimental
        '''
        return typing.cast(typing.Optional["IIntermediateType"], jsii.get(self, "intermediateType"))

    @jsii.member(jsii_name="argsToString")
    def args_to_string(self) -> builtins.str:
        '''(experimental) Generate the arguments for this field.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "argsToString", []))

    @jsii.member(jsii_name="directivesToString")
    def directives_to_string(
        self,
        modes: typing.Optional[typing.Sequence[AuthorizationType]] = None,
    ) -> builtins.str:
        '''(experimental) Generate the directives for this field.

        :param modes: the authorization modes of the graphql api.

        :default: - no authorization modes

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "directivesToString", [modes]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the string for this attribute.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IField).__jsii_proxy_class__ = lambda : _IFieldProxy


@jsii.interface(jsii_type="@aws-cdk/aws-appsync-alpha.IGraphqlApi")
class IGraphqlApi(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) Interface for GraphQL.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''(experimental) an unique AWS AppSync GraphQL API identifier i.e. 'lxz775lwdrgcndgz3nurvac7oa'.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) the ARN of the API.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="addDynamoDbDataSource")
    def add_dynamo_db_data_source(
        self,
        id: builtins.str,
        table: aws_cdk.aws_dynamodb.ITable,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "DynamoDbDataSource":
        '''(experimental) add a new DynamoDB data source to this API.

        :param id: The data source's id.
        :param table: The DynamoDB table backing this data source.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addElasticsearchDataSource")
    def add_elasticsearch_data_source(
        self,
        id: builtins.str,
        domain: aws_cdk.aws_elasticsearch.IDomain,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "ElasticsearchDataSource":
        '''(experimental) add a new elasticsearch data source to this API.

        :param id: The data source's id.
        :param domain: The elasticsearch domain for this data source.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addHttpDataSource")
    def add_http_data_source(
        self,
        id: builtins.str,
        endpoint: builtins.str,
        *,
        authorization_config: typing.Optional[AwsIamConfig] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "HttpDataSource":
        '''(experimental) add a new http data source to this API.

        :param id: The data source's id.
        :param endpoint: The http endpoint.
        :param authorization_config: (experimental) The authorization config in case the HTTP endpoint requires authorization. Default: - none
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addLambdaDataSource")
    def add_lambda_data_source(
        self,
        id: builtins.str,
        lambda_function: aws_cdk.aws_lambda.IFunction,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "LambdaDataSource":
        '''(experimental) add a new Lambda data source to this API.

        :param id: The data source's id.
        :param lambda_function: The Lambda function to call to interact with this data source.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addNoneDataSource")
    def add_none_data_source(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "NoneDataSource":
        '''(experimental) add a new dummy data source to this API.

        Useful for pipeline resolvers
        and for backend changes that don't require a data source.

        :param id: The data source's id.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addRdsDataSource")
    def add_rds_data_source(
        self,
        id: builtins.str,
        serverless_cluster: aws_cdk.aws_rds.IServerlessCluster,
        secret_store: aws_cdk.aws_secretsmanager.ISecret,
        database_name: typing.Optional[builtins.str] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "RdsDataSource":
        '''(experimental) add a new Rds data source to this API.

        :param id: The data source's id.
        :param serverless_cluster: The serverless cluster to interact with this data source.
        :param secret_store: The secret store that contains the username and password for the serverless cluster.
        :param database_name: The optional name of the database to use within the cluster.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addSchemaDependency")
    def add_schema_dependency(self, construct: aws_cdk.CfnResource) -> builtins.bool:
        '''(experimental) Add schema dependency if not imported.

        :param construct: the dependee.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="createResolver")
    def create_resolver(
        self,
        *,
        data_source: typing.Optional[BaseDataSource] = None,
        field_name: builtins.str,
        type_name: builtins.str,
        caching_config: typing.Optional[CachingConfig] = None,
        pipeline_config: typing.Optional[typing.Sequence[IAppsyncFunction]] = None,
        request_mapping_template: typing.Optional["MappingTemplate"] = None,
        response_mapping_template: typing.Optional["MappingTemplate"] = None,
    ) -> "Resolver":
        '''(experimental) creates a new resolver for this datasource and API using the given properties.

        :param data_source: (experimental) The data source this resolver is using. Default: - No datasource
        :param field_name: (experimental) name of the GraphQL field in the given type this resolver is attached to.
        :param type_name: (experimental) name of the GraphQL type this resolver is attached to.
        :param caching_config: (experimental) The caching configuration for this resolver. Default: - No caching configuration
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array | undefined sets resolver to be of kind, unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template

        :stability: experimental
        '''
        ...


class _IGraphqlApiProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) Interface for GraphQL.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appsync-alpha.IGraphqlApi"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''(experimental) an unique AWS AppSync GraphQL API identifier i.e. 'lxz775lwdrgcndgz3nurvac7oa'.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) the ARN of the API.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @jsii.member(jsii_name="addDynamoDbDataSource")
    def add_dynamo_db_data_source(
        self,
        id: builtins.str,
        table: aws_cdk.aws_dynamodb.ITable,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "DynamoDbDataSource":
        '''(experimental) add a new DynamoDB data source to this API.

        :param id: The data source's id.
        :param table: The DynamoDB table backing this data source.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = DataSourceOptions(description=description, name=name)

        return typing.cast("DynamoDbDataSource", jsii.invoke(self, "addDynamoDbDataSource", [id, table, options]))

    @jsii.member(jsii_name="addElasticsearchDataSource")
    def add_elasticsearch_data_source(
        self,
        id: builtins.str,
        domain: aws_cdk.aws_elasticsearch.IDomain,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "ElasticsearchDataSource":
        '''(experimental) add a new elasticsearch data source to this API.

        :param id: The data source's id.
        :param domain: The elasticsearch domain for this data source.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = DataSourceOptions(description=description, name=name)

        return typing.cast("ElasticsearchDataSource", jsii.invoke(self, "addElasticsearchDataSource", [id, domain, options]))

    @jsii.member(jsii_name="addHttpDataSource")
    def add_http_data_source(
        self,
        id: builtins.str,
        endpoint: builtins.str,
        *,
        authorization_config: typing.Optional[AwsIamConfig] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "HttpDataSource":
        '''(experimental) add a new http data source to this API.

        :param id: The data source's id.
        :param endpoint: The http endpoint.
        :param authorization_config: (experimental) The authorization config in case the HTTP endpoint requires authorization. Default: - none
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = HttpDataSourceOptions(
            authorization_config=authorization_config,
            description=description,
            name=name,
        )

        return typing.cast("HttpDataSource", jsii.invoke(self, "addHttpDataSource", [id, endpoint, options]))

    @jsii.member(jsii_name="addLambdaDataSource")
    def add_lambda_data_source(
        self,
        id: builtins.str,
        lambda_function: aws_cdk.aws_lambda.IFunction,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "LambdaDataSource":
        '''(experimental) add a new Lambda data source to this API.

        :param id: The data source's id.
        :param lambda_function: The Lambda function to call to interact with this data source.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = DataSourceOptions(description=description, name=name)

        return typing.cast("LambdaDataSource", jsii.invoke(self, "addLambdaDataSource", [id, lambda_function, options]))

    @jsii.member(jsii_name="addNoneDataSource")
    def add_none_data_source(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "NoneDataSource":
        '''(experimental) add a new dummy data source to this API.

        Useful for pipeline resolvers
        and for backend changes that don't require a data source.

        :param id: The data source's id.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = DataSourceOptions(description=description, name=name)

        return typing.cast("NoneDataSource", jsii.invoke(self, "addNoneDataSource", [id, options]))

    @jsii.member(jsii_name="addRdsDataSource")
    def add_rds_data_source(
        self,
        id: builtins.str,
        serverless_cluster: aws_cdk.aws_rds.IServerlessCluster,
        secret_store: aws_cdk.aws_secretsmanager.ISecret,
        database_name: typing.Optional[builtins.str] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "RdsDataSource":
        '''(experimental) add a new Rds data source to this API.

        :param id: The data source's id.
        :param serverless_cluster: The serverless cluster to interact with this data source.
        :param secret_store: The secret store that contains the username and password for the serverless cluster.
        :param database_name: The optional name of the database to use within the cluster.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = DataSourceOptions(description=description, name=name)

        return typing.cast("RdsDataSource", jsii.invoke(self, "addRdsDataSource", [id, serverless_cluster, secret_store, database_name, options]))

    @jsii.member(jsii_name="addSchemaDependency")
    def add_schema_dependency(self, construct: aws_cdk.CfnResource) -> builtins.bool:
        '''(experimental) Add schema dependency if not imported.

        :param construct: the dependee.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "addSchemaDependency", [construct]))

    @jsii.member(jsii_name="createResolver")
    def create_resolver(
        self,
        *,
        data_source: typing.Optional[BaseDataSource] = None,
        field_name: builtins.str,
        type_name: builtins.str,
        caching_config: typing.Optional[CachingConfig] = None,
        pipeline_config: typing.Optional[typing.Sequence[IAppsyncFunction]] = None,
        request_mapping_template: typing.Optional["MappingTemplate"] = None,
        response_mapping_template: typing.Optional["MappingTemplate"] = None,
    ) -> "Resolver":
        '''(experimental) creates a new resolver for this datasource and API using the given properties.

        :param data_source: (experimental) The data source this resolver is using. Default: - No datasource
        :param field_name: (experimental) name of the GraphQL field in the given type this resolver is attached to.
        :param type_name: (experimental) name of the GraphQL type this resolver is attached to.
        :param caching_config: (experimental) The caching configuration for this resolver. Default: - No caching configuration
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array | undefined sets resolver to be of kind, unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template

        :stability: experimental
        '''
        props = ExtendedResolverProps(
            data_source=data_source,
            field_name=field_name,
            type_name=type_name,
            caching_config=caching_config,
            pipeline_config=pipeline_config,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
        )

        return typing.cast("Resolver", jsii.invoke(self, "createResolver", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IGraphqlApi).__jsii_proxy_class__ = lambda : _IGraphqlApiProxy


@jsii.interface(jsii_type="@aws-cdk/aws-appsync-alpha.IIntermediateType")
class IIntermediateType(typing_extensions.Protocol):
    '''(experimental) Intermediate Types are types that includes a certain set of fields that define the entirety of your schema.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.Mapping[builtins.str, IField]:
        '''(experimental) the attributes of this type.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) the name of this type.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directives")
    def directives(self) -> typing.Optional[typing.List[Directive]]:
        '''(experimental) the directives for this object type.

        :default: - no directives

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interfaceTypes")
    def interface_types(self) -> typing.Optional[typing.List["InterfaceType"]]:
        '''(experimental) The Interface Types this Intermediate Type implements.

        :default: - no interface types

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intermediateType")
    def intermediate_type(self) -> typing.Optional["IIntermediateType"]:
        '''(experimental) the intermediate type linked to this attribute (i.e. an interface or an object).

        :default: - no intermediate type

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resolvers")
    def resolvers(self) -> typing.Optional[typing.List["Resolver"]]:
        '''(experimental) The resolvers linked to this data source.

        :stability: experimental
        '''
        ...

    @resolvers.setter
    def resolvers(self, value: typing.Optional[typing.List["Resolver"]]) -> None:
        ...

    @jsii.member(jsii_name="addField")
    def add_field(
        self,
        *,
        field: typing.Optional[IField] = None,
        field_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add a field to this Intermediate Type.

        :param field: (experimental) The resolvable field to add. This option must be configured for Object, Interface, Input and Union Types. Default: - no IField
        :param field_name: (experimental) The name of the field. This option must be configured for Object, Interface, Input and Enum Types. Default: - no fieldName

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="attribute")
    def attribute(
        self,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) Create an GraphQL Type representing this Intermediate Type.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the string of this object type.

        :stability: experimental
        '''
        ...


class _IIntermediateTypeProxy:
    '''(experimental) Intermediate Types are types that includes a certain set of fields that define the entirety of your schema.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-appsync-alpha.IIntermediateType"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.Mapping[builtins.str, IField]:
        '''(experimental) the attributes of this type.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, IField], jsii.get(self, "definition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) the name of this type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directives")
    def directives(self) -> typing.Optional[typing.List[Directive]]:
        '''(experimental) the directives for this object type.

        :default: - no directives

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[Directive]], jsii.get(self, "directives"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interfaceTypes")
    def interface_types(self) -> typing.Optional[typing.List["InterfaceType"]]:
        '''(experimental) The Interface Types this Intermediate Type implements.

        :default: - no interface types

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List["InterfaceType"]], jsii.get(self, "interfaceTypes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intermediateType")
    def intermediate_type(self) -> typing.Optional[IIntermediateType]:
        '''(experimental) the intermediate type linked to this attribute (i.e. an interface or an object).

        :default: - no intermediate type

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IIntermediateType], jsii.get(self, "intermediateType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resolvers")
    def resolvers(self) -> typing.Optional[typing.List["Resolver"]]:
        '''(experimental) The resolvers linked to this data source.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List["Resolver"]], jsii.get(self, "resolvers"))

    @resolvers.setter
    def resolvers(self, value: typing.Optional[typing.List["Resolver"]]) -> None:
        jsii.set(self, "resolvers", value)

    @jsii.member(jsii_name="addField")
    def add_field(
        self,
        *,
        field: typing.Optional[IField] = None,
        field_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add a field to this Intermediate Type.

        :param field: (experimental) The resolvable field to add. This option must be configured for Object, Interface, Input and Union Types. Default: - no IField
        :param field_name: (experimental) The name of the field. This option must be configured for Object, Interface, Input and Enum Types. Default: - no fieldName

        :stability: experimental
        '''
        options = AddFieldOptions(field=field, field_name=field_name)

        return typing.cast(None, jsii.invoke(self, "addField", [options]))

    @jsii.member(jsii_name="attribute")
    def attribute(
        self,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) Create an GraphQL Type representing this Intermediate Type.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.invoke(self, "attribute", [options]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the string of this object type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IIntermediateType).__jsii_proxy_class__ = lambda : _IIntermediateTypeProxy


class IamResource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.IamResource",
):
    '''(experimental) A class used to generate resource arns for AppSync.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        role = iam.Role(self, "Role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        
        api.grant(role, appsync.IamResource.custom("types/Mutation/fields/updateExample"), "appsync:GraphQL")
    '''

    @jsii.member(jsii_name="all") # type: ignore[misc]
    @builtins.classmethod
    def all(cls) -> "IamResource":
        '''(experimental) Generate the resource names that accepts all types: ``*``.

        :stability: experimental
        '''
        return typing.cast("IamResource", jsii.sinvoke(cls, "all", []))

    @jsii.member(jsii_name="custom") # type: ignore[misc]
    @builtins.classmethod
    def custom(cls, *arns: builtins.str) -> "IamResource":
        '''(experimental) Generate the resource names given custom arns.

        :param arns: The custom arns that need to be permissioned. Example: custom('/types/Query/fields/getExample')

        :stability: experimental
        '''
        return typing.cast("IamResource", jsii.sinvoke(cls, "custom", [*arns]))

    @jsii.member(jsii_name="ofType") # type: ignore[misc]
    @builtins.classmethod
    def of_type(cls, type: builtins.str, *fields: builtins.str) -> "IamResource":
        '''(experimental) Generate the resource names given a type and fields.

        :param type: The type that needs to be allowed.
        :param fields: The fields that need to be allowed, if empty grant permissions to ALL fields. Example: ofType('Query', 'GetExample')

        :stability: experimental
        '''
        return typing.cast("IamResource", jsii.sinvoke(cls, "ofType", [type, *fields]))

    @jsii.member(jsii_name="resourceArns")
    def resource_arns(self, api: "GraphqlApi") -> typing.List[builtins.str]:
        '''(experimental) Return the Resource ARN.

        :param api: The GraphQL API to give permissions.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "resourceArns", [api]))


@jsii.implements(IIntermediateType)
class InputType(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.InputType",
):
    '''(experimental) Input Types are abstract types that define complex objects.

    They are used in arguments to represent

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        
        review = appsync.InputType("Review",
            definition={
                "stars": appsync.GraphqlType.int(is_required=True),
                "commentary": appsync.GraphqlType.string()
            }
        )
        api.add_type(review)
    '''

    def __init__(
        self,
        name: builtins.str,
        *,
        definition: typing.Mapping[builtins.str, IField],
        directives: typing.Optional[typing.Sequence[Directive]] = None,
    ) -> None:
        '''
        :param name: -
        :param definition: (experimental) the attributes of this type.
        :param directives: (experimental) the directives for this object type. Default: - no directives

        :stability: experimental
        '''
        props = IntermediateTypeOptions(definition=definition, directives=directives)

        jsii.create(self.__class__, self, [name, props])

    @jsii.member(jsii_name="addField")
    def add_field(
        self,
        *,
        field: typing.Optional[IField] = None,
        field_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add a field to this Input Type.

        Input Types must have both fieldName and field options.

        :param field: (experimental) The resolvable field to add. This option must be configured for Object, Interface, Input and Union Types. Default: - no IField
        :param field_name: (experimental) The name of the field. This option must be configured for Object, Interface, Input and Enum Types. Default: - no fieldName

        :stability: experimental
        '''
        options = AddFieldOptions(field=field, field_name=field_name)

        return typing.cast(None, jsii.invoke(self, "addField", [options]))

    @jsii.member(jsii_name="attribute")
    def attribute(
        self,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) Create a GraphQL Type representing this Input Type.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.invoke(self, "attribute", [options]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the string of this input type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.Mapping[builtins.str, IField]:
        '''(experimental) the attributes of this type.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, IField], jsii.get(self, "definition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) the name of this type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modes")
    def _modes(self) -> typing.Optional[typing.List[AuthorizationType]]:
        '''(experimental) the authorization modes for this intermediate type.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[AuthorizationType]], jsii.get(self, "modes"))

    @_modes.setter
    def _modes(self, value: typing.Optional[typing.List[AuthorizationType]]) -> None:
        jsii.set(self, "modes", value)


@jsii.implements(IIntermediateType)
class InterfaceType(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.InterfaceType",
):
    '''(experimental) Interface Types are abstract types that includes a certain set of fields that other types must include if they implement the interface.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        node = appsync.InterfaceType("Node",
            definition={
                "id": appsync.GraphqlType.string(is_required=True)
            }
        )
        demo = appsync.ObjectType("Demo",
            interface_types=[node],
            definition={
                "version": appsync.GraphqlType.string(is_required=True)
            }
        )
    '''

    def __init__(
        self,
        name: builtins.str,
        *,
        definition: typing.Mapping[builtins.str, IField],
        directives: typing.Optional[typing.Sequence[Directive]] = None,
    ) -> None:
        '''
        :param name: -
        :param definition: (experimental) the attributes of this type.
        :param directives: (experimental) the directives for this object type. Default: - no directives

        :stability: experimental
        '''
        props = IntermediateTypeOptions(definition=definition, directives=directives)

        jsii.create(self.__class__, self, [name, props])

    @jsii.member(jsii_name="addField")
    def add_field(
        self,
        *,
        field: typing.Optional[IField] = None,
        field_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add a field to this Interface Type.

        Interface Types must have both fieldName and field options.

        :param field: (experimental) The resolvable field to add. This option must be configured for Object, Interface, Input and Union Types. Default: - no IField
        :param field_name: (experimental) The name of the field. This option must be configured for Object, Interface, Input and Enum Types. Default: - no fieldName

        :stability: experimental
        '''
        options = AddFieldOptions(field=field, field_name=field_name)

        return typing.cast(None, jsii.invoke(self, "addField", [options]))

    @jsii.member(jsii_name="attribute")
    def attribute(
        self,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) Create a GraphQL Type representing this Intermediate Type.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.invoke(self, "attribute", [options]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the string of this object type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.Mapping[builtins.str, IField]:
        '''(experimental) the attributes of this type.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, IField], jsii.get(self, "definition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) the name of this type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directives")
    def directives(self) -> typing.Optional[typing.List[Directive]]:
        '''(experimental) the directives for this object type.

        :default: - no directives

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[Directive]], jsii.get(self, "directives"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modes")
    def _modes(self) -> typing.Optional[typing.List[AuthorizationType]]:
        '''(experimental) the authorization modes for this intermediate type.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[AuthorizationType]], jsii.get(self, "modes"))

    @_modes.setter
    def _modes(self, value: typing.Optional[typing.List[AuthorizationType]]) -> None:
        jsii.set(self, "modes", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.IntermediateTypeOptions",
    jsii_struct_bases=[],
    name_mapping={"definition": "definition", "directives": "directives"},
)
class IntermediateTypeOptions:
    def __init__(
        self,
        *,
        definition: typing.Mapping[builtins.str, IField],
        directives: typing.Optional[typing.Sequence[Directive]] = None,
    ) -> None:
        '''(experimental) Properties for configuring an Intermediate Type.

        :param definition: (experimental) the attributes of this type.
        :param directives: (experimental) the directives for this object type. Default: - no directives

        :stability: experimental
        :exampleMetadata: infused

        Example::

            node = appsync.InterfaceType("Node",
                definition={
                    "id": appsync.GraphqlType.string(is_required=True)
                }
            )
            demo = appsync.ObjectType("Demo",
                interface_types=[node],
                definition={
                    "version": appsync.GraphqlType.string(is_required=True)
                }
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "definition": definition,
        }
        if directives is not None:
            self._values["directives"] = directives

    @builtins.property
    def definition(self) -> typing.Mapping[builtins.str, IField]:
        '''(experimental) the attributes of this type.

        :stability: experimental
        '''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(typing.Mapping[builtins.str, IField], result)

    @builtins.property
    def directives(self) -> typing.Optional[typing.List[Directive]]:
        '''(experimental) the directives for this object type.

        :default: - no directives

        :stability: experimental
        '''
        result = self._values.get("directives")
        return typing.cast(typing.Optional[typing.List[Directive]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IntermediateTypeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class KeyCondition(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.KeyCondition",
):
    '''(experimental) Factory class for DynamoDB key conditions.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_appsync_alpha as appsync_alpha
        
        key_condition = appsync_alpha.KeyCondition.begins_with("keyName", "arg")
    '''

    @jsii.member(jsii_name="beginsWith") # type: ignore[misc]
    @builtins.classmethod
    def begins_with(cls, key_name: builtins.str, arg: builtins.str) -> "KeyCondition":
        '''(experimental) Condition (k, arg).

        True if the key attribute k begins with the Query argument.

        :param key_name: -
        :param arg: -

        :stability: experimental
        '''
        return typing.cast("KeyCondition", jsii.sinvoke(cls, "beginsWith", [key_name, arg]))

    @jsii.member(jsii_name="between") # type: ignore[misc]
    @builtins.classmethod
    def between(
        cls,
        key_name: builtins.str,
        arg1: builtins.str,
        arg2: builtins.str,
    ) -> "KeyCondition":
        '''(experimental) Condition k BETWEEN arg1 AND arg2, true if k >= arg1 and k <= arg2.

        :param key_name: -
        :param arg1: -
        :param arg2: -

        :stability: experimental
        '''
        return typing.cast("KeyCondition", jsii.sinvoke(cls, "between", [key_name, arg1, arg2]))

    @jsii.member(jsii_name="eq") # type: ignore[misc]
    @builtins.classmethod
    def eq(cls, key_name: builtins.str, arg: builtins.str) -> "KeyCondition":
        '''(experimental) Condition k = arg, true if the key attribute k is equal to the Query argument.

        :param key_name: -
        :param arg: -

        :stability: experimental
        '''
        return typing.cast("KeyCondition", jsii.sinvoke(cls, "eq", [key_name, arg]))

    @jsii.member(jsii_name="ge") # type: ignore[misc]
    @builtins.classmethod
    def ge(cls, key_name: builtins.str, arg: builtins.str) -> "KeyCondition":
        '''(experimental) Condition k >= arg, true if the key attribute k is greater or equal to the Query argument.

        :param key_name: -
        :param arg: -

        :stability: experimental
        '''
        return typing.cast("KeyCondition", jsii.sinvoke(cls, "ge", [key_name, arg]))

    @jsii.member(jsii_name="gt") # type: ignore[misc]
    @builtins.classmethod
    def gt(cls, key_name: builtins.str, arg: builtins.str) -> "KeyCondition":
        '''(experimental) Condition k > arg, true if the key attribute k is greater than the the Query argument.

        :param key_name: -
        :param arg: -

        :stability: experimental
        '''
        return typing.cast("KeyCondition", jsii.sinvoke(cls, "gt", [key_name, arg]))

    @jsii.member(jsii_name="le") # type: ignore[misc]
    @builtins.classmethod
    def le(cls, key_name: builtins.str, arg: builtins.str) -> "KeyCondition":
        '''(experimental) Condition k <= arg, true if the key attribute k is less than or equal to the Query argument.

        :param key_name: -
        :param arg: -

        :stability: experimental
        '''
        return typing.cast("KeyCondition", jsii.sinvoke(cls, "le", [key_name, arg]))

    @jsii.member(jsii_name="lt") # type: ignore[misc]
    @builtins.classmethod
    def lt(cls, key_name: builtins.str, arg: builtins.str) -> "KeyCondition":
        '''(experimental) Condition k < arg, true if the key attribute k is less than the Query argument.

        :param key_name: -
        :param arg: -

        :stability: experimental
        '''
        return typing.cast("KeyCondition", jsii.sinvoke(cls, "lt", [key_name, arg]))

    @jsii.member(jsii_name="and")
    def and_(self, key_cond: "KeyCondition") -> "KeyCondition":
        '''(experimental) Conjunction between two conditions.

        :param key_cond: -

        :stability: experimental
        '''
        return typing.cast("KeyCondition", jsii.invoke(self, "and", [key_cond]))

    @jsii.member(jsii_name="renderTemplate")
    def render_template(self) -> builtins.str:
        '''(experimental) Renders the key condition to a VTL string.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "renderTemplate", []))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.LambdaAuthorizerConfig",
    jsii_struct_bases=[],
    name_mapping={
        "handler": "handler",
        "results_cache_ttl": "resultsCacheTtl",
        "validation_regex": "validationRegex",
    },
)
class LambdaAuthorizerConfig:
    def __init__(
        self,
        *,
        handler: aws_cdk.aws_lambda.IFunction,
        results_cache_ttl: typing.Optional[aws_cdk.Duration] = None,
        validation_regex: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Configuration for Lambda authorization in AppSync.

        Note that you can only have a single AWS Lambda function configured to authorize your API.

        :param handler: (experimental) The authorizer lambda function. Note: This Lambda function must have the following resource-based policy assigned to it. When configuring Lambda authorizers in the console, this is done for you. To do so with the AWS CLI, run the following: ``aws lambda add-permission --function-name "arn:aws:lambda:us-east-2:111122223333:function:my-function" --statement-id "appsync" --principal appsync.amazonaws.com --action lambda:InvokeFunction``
        :param results_cache_ttl: (experimental) How long the results are cached. Disable caching by setting this to 0. Default: Duration.minutes(5)
        :param validation_regex: (experimental) A regular expression for validation of tokens before the Lambda function is called. Default: - no regex filter will be applied.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import aws_cdk.aws_lambda as lambda_
            # auth_function: lambda.Function
            
            
            appsync.GraphqlApi(self, "api",
                name="api",
                schema=appsync.Schema.from_asset(path.join(__dirname, "appsync.test.graphql")),
                authorization_config=appsync.AuthorizationConfig(
                    default_authorization=appsync.AuthorizationMode(
                        authorization_type=appsync.AuthorizationType.LAMBDA,
                        lambda_authorizer_config=appsync.LambdaAuthorizerConfig(
                            handler=auth_function
                        )
                    )
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "handler": handler,
        }
        if results_cache_ttl is not None:
            self._values["results_cache_ttl"] = results_cache_ttl
        if validation_regex is not None:
            self._values["validation_regex"] = validation_regex

    @builtins.property
    def handler(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The authorizer lambda function.

        Note: This Lambda function must have the following resource-based policy assigned to it.
        When configuring Lambda authorizers in the console, this is done for you.
        To do so with the AWS CLI, run the following:

        ``aws lambda add-permission --function-name "arn:aws:lambda:us-east-2:111122223333:function:my-function" --statement-id "appsync" --principal appsync.amazonaws.com --action lambda:InvokeFunction``

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appsync-graphqlapi-lambdaauthorizerconfig.html
        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    @builtins.property
    def results_cache_ttl(self) -> typing.Optional[aws_cdk.Duration]:
        '''(experimental) How long the results are cached.

        Disable caching by setting this to 0.

        :default: Duration.minutes(5)

        :stability: experimental
        '''
        result = self._values.get("results_cache_ttl")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def validation_regex(self) -> typing.Optional[builtins.str]:
        '''(experimental) A regular expression for validation of tokens before the Lambda function is called.

        :default: - no regex filter will be applied.

        :stability: experimental
        '''
        result = self._values.get("validation_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaAuthorizerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.LogConfig",
    jsii_struct_bases=[],
    name_mapping={
        "exclude_verbose_content": "excludeVerboseContent",
        "field_log_level": "fieldLogLevel",
        "role": "role",
    },
)
class LogConfig:
    def __init__(
        self,
        *,
        exclude_verbose_content: typing.Optional[typing.Union[builtins.bool, aws_cdk.IResolvable]] = None,
        field_log_level: typing.Optional[FieldLogLevel] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''(experimental) Logging configuration for AppSync.

        :param exclude_verbose_content: (experimental) exclude verbose content. Default: false
        :param field_log_level: (experimental) log level for fields. Default: - Use AppSync default
        :param role: (experimental) The role for CloudWatch Logs. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            from aws_cdk import aws_iam as iam
            
            # role: iam.Role
            
            log_config = appsync_alpha.LogConfig(
                exclude_verbose_content=False,
                field_log_level=appsync_alpha.FieldLogLevel.NONE,
                role=role
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if exclude_verbose_content is not None:
            self._values["exclude_verbose_content"] = exclude_verbose_content
        if field_log_level is not None:
            self._values["field_log_level"] = field_log_level
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def exclude_verbose_content(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.IResolvable]]:
        '''(experimental) exclude verbose content.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("exclude_verbose_content")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.IResolvable]], result)

    @builtins.property
    def field_log_level(self) -> typing.Optional[FieldLogLevel]:
        '''(experimental) log level for fields.

        :default: - Use AppSync default

        :stability: experimental
        '''
        result = self._values.get("field_log_level")
        return typing.cast(typing.Optional[FieldLogLevel], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The role for CloudWatch Logs.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LogConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MappingTemplate(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-appsync-alpha.MappingTemplate",
):
    '''(experimental) MappingTemplates for AppSync resolvers.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        # dummy_request: appsync.MappingTemplate
        # dummy_response: appsync.MappingTemplate
        
        info = appsync.ObjectType("Info",
            definition={
                "node": appsync.ResolvableField(
                    return_type=appsync.GraphqlType.string(),
                    args={
                        "id": appsync.GraphqlType.string()
                    },
                    data_source=api.add_none_data_source("none"),
                    request_mapping_template=dummy_request,
                    response_mapping_template=dummy_response
                )
            }
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="dynamoDbDeleteItem") # type: ignore[misc]
    @builtins.classmethod
    def dynamo_db_delete_item(
        cls,
        key_name: builtins.str,
        id_arg: builtins.str,
    ) -> "MappingTemplate":
        '''(experimental) Mapping template to delete a single item from a DynamoDB table.

        :param key_name: the name of the hash key field.
        :param id_arg: the name of the Mutation argument.

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "dynamoDbDeleteItem", [key_name, id_arg]))

    @jsii.member(jsii_name="dynamoDbGetItem") # type: ignore[misc]
    @builtins.classmethod
    def dynamo_db_get_item(
        cls,
        key_name: builtins.str,
        id_arg: builtins.str,
    ) -> "MappingTemplate":
        '''(experimental) Mapping template to get a single item from a DynamoDB table.

        :param key_name: the name of the hash key field.
        :param id_arg: the name of the Query argument.

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "dynamoDbGetItem", [key_name, id_arg]))

    @jsii.member(jsii_name="dynamoDbPutItem") # type: ignore[misc]
    @builtins.classmethod
    def dynamo_db_put_item(
        cls,
        key: "PrimaryKey",
        values: AttributeValues,
    ) -> "MappingTemplate":
        '''(experimental) Mapping template to save a single item to a DynamoDB table.

        :param key: the assigment of Mutation values to the primary key.
        :param values: the assignment of Mutation values to the table attributes.

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "dynamoDbPutItem", [key, values]))

    @jsii.member(jsii_name="dynamoDbQuery") # type: ignore[misc]
    @builtins.classmethod
    def dynamo_db_query(
        cls,
        cond: KeyCondition,
        index_name: typing.Optional[builtins.str] = None,
    ) -> "MappingTemplate":
        '''(experimental) Mapping template to query a set of items from a DynamoDB table.

        :param cond: the key condition for the query.
        :param index_name: -

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "dynamoDbQuery", [cond, index_name]))

    @jsii.member(jsii_name="dynamoDbResultItem") # type: ignore[misc]
    @builtins.classmethod
    def dynamo_db_result_item(cls) -> "MappingTemplate":
        '''(experimental) Mapping template for a single result item from DynamoDB.

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "dynamoDbResultItem", []))

    @jsii.member(jsii_name="dynamoDbResultList") # type: ignore[misc]
    @builtins.classmethod
    def dynamo_db_result_list(cls) -> "MappingTemplate":
        '''(experimental) Mapping template for a result list from DynamoDB.

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "dynamoDbResultList", []))

    @jsii.member(jsii_name="dynamoDbScanTable") # type: ignore[misc]
    @builtins.classmethod
    def dynamo_db_scan_table(cls) -> "MappingTemplate":
        '''(experimental) Mapping template to scan a DynamoDB table to fetch all entries.

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "dynamoDbScanTable", []))

    @jsii.member(jsii_name="fromFile") # type: ignore[misc]
    @builtins.classmethod
    def from_file(cls, file_name: builtins.str) -> "MappingTemplate":
        '''(experimental) Create a mapping template from the given file.

        :param file_name: -

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "fromFile", [file_name]))

    @jsii.member(jsii_name="fromString") # type: ignore[misc]
    @builtins.classmethod
    def from_string(cls, template: builtins.str) -> "MappingTemplate":
        '''(experimental) Create a mapping template from the given string.

        :param template: -

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "fromString", [template]))

    @jsii.member(jsii_name="lambdaRequest") # type: ignore[misc]
    @builtins.classmethod
    def lambda_request(
        cls,
        payload: typing.Optional[builtins.str] = None,
        operation: typing.Optional[builtins.str] = None,
    ) -> "MappingTemplate":
        '''(experimental) Mapping template to invoke a Lambda function.

        :param payload: the VTL template snippet of the payload to send to the lambda. If no payload is provided all available context fields are sent to the Lambda function
        :param operation: the type of operation AppSync should perform on the data source.

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "lambdaRequest", [payload, operation]))

    @jsii.member(jsii_name="lambdaResult") # type: ignore[misc]
    @builtins.classmethod
    def lambda_result(cls) -> "MappingTemplate":
        '''(experimental) Mapping template to return the Lambda result to the caller.

        :stability: experimental
        '''
        return typing.cast("MappingTemplate", jsii.sinvoke(cls, "lambdaResult", []))

    @jsii.member(jsii_name="renderTemplate") # type: ignore[misc]
    @abc.abstractmethod
    def render_template(self) -> builtins.str:
        '''(experimental) this is called to render the mapping template to a VTL string.

        :stability: experimental
        '''
        ...


class _MappingTemplateProxy(MappingTemplate):
    @jsii.member(jsii_name="renderTemplate")
    def render_template(self) -> builtins.str:
        '''(experimental) this is called to render the mapping template to a VTL string.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "renderTemplate", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, MappingTemplate).__jsii_proxy_class__ = lambda : _MappingTemplateProxy


class NoneDataSource(
    BaseDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.NoneDataSource",
):
    '''(experimental) An AppSync dummy datasource.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_appsync_alpha as appsync_alpha
        
        # graphql_api: appsync_alpha.GraphqlApi
        
        none_data_source = appsync_alpha.NoneDataSource(self, "MyNoneDataSource",
            api=graphql_api,
        
            # the properties below are optional
            description="description",
            name="name"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source

        :stability: experimental
        '''
        props = NoneDataSourceProps(api=api, description=description, name=name)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.NoneDataSourceProps",
    jsii_struct_bases=[BaseDataSourceProps],
    name_mapping={"api": "api", "description": "description", "name": "name"},
)
class NoneDataSourceProps(BaseDataSourceProps):
    def __init__(
        self,
        *,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for an AppSync dummy datasource.

        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            # graphql_api: appsync_alpha.GraphqlApi
            
            none_data_source_props = appsync_alpha.NoneDataSourceProps(
                api=graphql_api,
            
                # the properties below are optional
                description="description",
                name="name"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api": api,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def api(self) -> IGraphqlApi:
        '''(experimental) The API to attach this data source to.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(IGraphqlApi, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) the description of the data source.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the data source.

        :default: - id of data source

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NoneDataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IIntermediateType)
class ObjectType(
    InterfaceType,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.ObjectType",
):
    '''(experimental) Object Types are types declared by you.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        # dummy_request: appsync.MappingTemplate
        # dummy_response: appsync.MappingTemplate
        
        info = appsync.ObjectType("Info",
            definition={
                "node": appsync.ResolvableField(
                    return_type=appsync.GraphqlType.string(),
                    args={
                        "id": appsync.GraphqlType.string()
                    },
                    data_source=api.add_none_data_source("none"),
                    request_mapping_template=dummy_request,
                    response_mapping_template=dummy_response
                )
            }
        )
    '''

    def __init__(
        self,
        name: builtins.str,
        *,
        interface_types: typing.Optional[typing.Sequence[InterfaceType]] = None,
        definition: typing.Mapping[builtins.str, IField],
        directives: typing.Optional[typing.Sequence[Directive]] = None,
    ) -> None:
        '''
        :param name: -
        :param interface_types: (experimental) The Interface Types this Object Type implements. Default: - no interface types
        :param definition: (experimental) the attributes of this type.
        :param directives: (experimental) the directives for this object type. Default: - no directives

        :stability: experimental
        '''
        props = ObjectTypeOptions(
            interface_types=interface_types,
            definition=definition,
            directives=directives,
        )

        jsii.create(self.__class__, self, [name, props])

    @jsii.member(jsii_name="addField")
    def add_field(
        self,
        *,
        field: typing.Optional[IField] = None,
        field_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add a field to this Object Type.

        Object Types must have both fieldName and field options.

        :param field: (experimental) The resolvable field to add. This option must be configured for Object, Interface, Input and Union Types. Default: - no IField
        :param field_name: (experimental) The name of the field. This option must be configured for Object, Interface, Input and Enum Types. Default: - no fieldName

        :stability: experimental
        '''
        options = AddFieldOptions(field=field, field_name=field_name)

        return typing.cast(None, jsii.invoke(self, "addField", [options]))

    @jsii.member(jsii_name="generateResolver")
    def _generate_resolver(
        self,
        api: IGraphqlApi,
        field_name: builtins.str,
        *,
        data_source: typing.Optional[BaseDataSource] = None,
        pipeline_config: typing.Optional[typing.Sequence[IAppsyncFunction]] = None,
        request_mapping_template: typing.Optional[MappingTemplate] = None,
        response_mapping_template: typing.Optional[MappingTemplate] = None,
        return_type: "GraphqlType",
        args: typing.Optional[typing.Mapping[builtins.str, "GraphqlType"]] = None,
        directives: typing.Optional[typing.Sequence[Directive]] = None,
    ) -> "Resolver":
        '''(experimental) Generate the resolvers linked to this Object Type.

        :param api: -
        :param field_name: -
        :param data_source: (experimental) The data source creating linked to this resolvable field. Default: - no data source
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array or undefined prop will set resolver to be of type unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template
        :param return_type: (experimental) The return type for this field.
        :param args: (experimental) The arguments for this field. i.e. type Example (first: String second: String) {} - where 'first' and 'second' are key values for args and 'String' is the GraphqlType Default: - no arguments
        :param directives: (experimental) the directives for this field. Default: - no directives

        :stability: experimental
        '''
        options = ResolvableFieldOptions(
            data_source=data_source,
            pipeline_config=pipeline_config,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
            return_type=return_type,
            args=args,
            directives=directives,
        )

        return typing.cast("Resolver", jsii.invoke(self, "generateResolver", [api, field_name, options]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the string of this object type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interfaceTypes")
    def interface_types(self) -> typing.Optional[typing.List[InterfaceType]]:
        '''(experimental) The Interface Types this Object Type implements.

        :default: - no interface types

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[InterfaceType]], jsii.get(self, "interfaceTypes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resolvers")
    def resolvers(self) -> typing.Optional[typing.List["Resolver"]]:
        '''(experimental) The resolvers linked to this data source.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List["Resolver"]], jsii.get(self, "resolvers"))

    @resolvers.setter
    def resolvers(self, value: typing.Optional[typing.List["Resolver"]]) -> None:
        jsii.set(self, "resolvers", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.ObjectTypeOptions",
    jsii_struct_bases=[IntermediateTypeOptions],
    name_mapping={
        "definition": "definition",
        "directives": "directives",
        "interface_types": "interfaceTypes",
    },
)
class ObjectTypeOptions(IntermediateTypeOptions):
    def __init__(
        self,
        *,
        definition: typing.Mapping[builtins.str, IField],
        directives: typing.Optional[typing.Sequence[Directive]] = None,
        interface_types: typing.Optional[typing.Sequence[InterfaceType]] = None,
    ) -> None:
        '''(experimental) Properties for configuring an Object Type.

        :param definition: (experimental) the attributes of this type.
        :param directives: (experimental) the directives for this object type. Default: - no directives
        :param interface_types: (experimental) The Interface Types this Object Type implements. Default: - no interface types

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # api: appsync.GraphqlApi
            # dummy_request: appsync.MappingTemplate
            # dummy_response: appsync.MappingTemplate
            
            info = appsync.ObjectType("Info",
                definition={
                    "node": appsync.ResolvableField(
                        return_type=appsync.GraphqlType.string(),
                        args={
                            "id": appsync.GraphqlType.string()
                        },
                        data_source=api.add_none_data_source("none"),
                        request_mapping_template=dummy_request,
                        response_mapping_template=dummy_response
                    )
                }
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "definition": definition,
        }
        if directives is not None:
            self._values["directives"] = directives
        if interface_types is not None:
            self._values["interface_types"] = interface_types

    @builtins.property
    def definition(self) -> typing.Mapping[builtins.str, IField]:
        '''(experimental) the attributes of this type.

        :stability: experimental
        '''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(typing.Mapping[builtins.str, IField], result)

    @builtins.property
    def directives(self) -> typing.Optional[typing.List[Directive]]:
        '''(experimental) the directives for this object type.

        :default: - no directives

        :stability: experimental
        '''
        result = self._values.get("directives")
        return typing.cast(typing.Optional[typing.List[Directive]], result)

    @builtins.property
    def interface_types(self) -> typing.Optional[typing.List[InterfaceType]]:
        '''(experimental) The Interface Types this Object Type implements.

        :default: - no interface types

        :stability: experimental
        '''
        result = self._values.get("interface_types")
        return typing.cast(typing.Optional[typing.List[InterfaceType]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ObjectTypeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.OpenIdConnectConfig",
    jsii_struct_bases=[],
    name_mapping={
        "oidc_provider": "oidcProvider",
        "client_id": "clientId",
        "token_expiry_from_auth": "tokenExpiryFromAuth",
        "token_expiry_from_issue": "tokenExpiryFromIssue",
    },
)
class OpenIdConnectConfig:
    def __init__(
        self,
        *,
        oidc_provider: builtins.str,
        client_id: typing.Optional[builtins.str] = None,
        token_expiry_from_auth: typing.Optional[jsii.Number] = None,
        token_expiry_from_issue: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Configuration for OpenID Connect authorization in AppSync.

        :param oidc_provider: (experimental) The issuer for the OIDC configuration. The issuer returned by discovery must exactly match the value of ``iss`` in the OIDC token.
        :param client_id: (experimental) The client identifier of the Relying party at the OpenID identity provider. A regular expression can be specified so AppSync can validate against multiple client identifiers at a time. Default: - - (All)
        :param token_expiry_from_auth: (experimental) The number of milliseconds an OIDC token is valid after being authenticated by OIDC provider. ``auth_time`` claim in OIDC token is required for this validation to work. Default: - no validation
        :param token_expiry_from_issue: (experimental) The number of milliseconds an OIDC token is valid after being issued to a user. This validation uses ``iat`` claim of OIDC token. Default: - no validation

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            open_id_connect_config = appsync_alpha.OpenIdConnectConfig(
                oidc_provider="oidcProvider",
            
                # the properties below are optional
                client_id="clientId",
                token_expiry_from_auth=123,
                token_expiry_from_issue=123
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "oidc_provider": oidc_provider,
        }
        if client_id is not None:
            self._values["client_id"] = client_id
        if token_expiry_from_auth is not None:
            self._values["token_expiry_from_auth"] = token_expiry_from_auth
        if token_expiry_from_issue is not None:
            self._values["token_expiry_from_issue"] = token_expiry_from_issue

    @builtins.property
    def oidc_provider(self) -> builtins.str:
        '''(experimental) The issuer for the OIDC configuration.

        The issuer returned by discovery must exactly match the value of ``iss`` in the OIDC token.

        :stability: experimental
        '''
        result = self._values.get("oidc_provider")
        assert result is not None, "Required property 'oidc_provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The client identifier of the Relying party at the OpenID identity provider.

        A regular expression can be specified so AppSync can validate against multiple client identifiers at a time.

        :default:

        -
        - (All)

        :stability: experimental

        Example::

            -"ABCD|CDEF"
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_expiry_from_auth(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of milliseconds an OIDC token is valid after being authenticated by OIDC provider.

        ``auth_time`` claim in OIDC token is required for this validation to work.

        :default: - no validation

        :stability: experimental
        '''
        result = self._values.get("token_expiry_from_auth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_expiry_from_issue(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of milliseconds an OIDC token is valid after being issued to a user.

        This validation uses ``iat`` claim of OIDC token.

        :default: - no validation

        :stability: experimental
        '''
        result = self._values.get("token_expiry_from_issue")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpenIdConnectConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PartitionKeyStep(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.PartitionKeyStep",
):
    '''(experimental) Utility class to allow assigning a value or an auto-generated id to a partition key.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_appsync_alpha as appsync_alpha
        
        partition_key_step = appsync_alpha.PartitionKeyStep("key")
    '''

    def __init__(self, key: builtins.str) -> None:
        '''
        :param key: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [key])

    @jsii.member(jsii_name="auto")
    def auto(self) -> "PartitionKey":
        '''(experimental) Assign an auto-generated value to the partition key.

        :stability: experimental
        '''
        return typing.cast("PartitionKey", jsii.invoke(self, "auto", []))

    @jsii.member(jsii_name="is")
    def is_(self, val: builtins.str) -> "PartitionKey":
        '''(experimental) Assign an auto-generated value to the partition key.

        :param val: -

        :stability: experimental
        '''
        return typing.cast("PartitionKey", jsii.invoke(self, "is", [val]))


class PrimaryKey(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.PrimaryKey",
):
    '''(experimental) Specifies the assignment to the primary key.

    It either
    contains the full primary key or only the partition key.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        api = appsync.GraphqlApi(self, "Api",
            name="demo",
            schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql")),
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.IAM
                )
            ),
            xray_enabled=True
        )
        
        demo_table = dynamodb.Table(self, "DemoTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        demo_dS = api.add_dynamo_db_data_source("demoDataSource", demo_table)
        
        # Resolver for the Query "getDemos" that scans the DynamoDb table and returns the entire list.
        demo_dS.create_resolver(
            type_name="Query",
            field_name="getDemos",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
        )
        
        # Resolver for the Mutation "addDemo" that puts the item into the DynamoDb table.
        demo_dS.create_resolver(
            type_name="Mutation",
            field_name="addDemo",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
                appsync.PrimaryKey.partition("id").auto(),
                appsync.Values.projecting("input")),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
        )
    '''

    def __init__(self, pkey: Assign, skey: typing.Optional[Assign] = None) -> None:
        '''
        :param pkey: -
        :param skey: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [pkey, skey])

    @jsii.member(jsii_name="partition") # type: ignore[misc]
    @builtins.classmethod
    def partition(cls, key: builtins.str) -> PartitionKeyStep:
        '''(experimental) Allows assigning a value to the partition key.

        :param key: -

        :stability: experimental
        '''
        return typing.cast(PartitionKeyStep, jsii.sinvoke(cls, "partition", [key]))

    @jsii.member(jsii_name="renderTemplate")
    def render_template(self) -> builtins.str:
        '''(experimental) Renders the key assignment to a VTL string.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "renderTemplate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pkey")
    def _pkey(self) -> Assign:
        '''
        :stability: experimental
        '''
        return typing.cast(Assign, jsii.get(self, "pkey"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.ResolvableFieldOptions",
    jsii_struct_bases=[FieldOptions],
    name_mapping={
        "return_type": "returnType",
        "args": "args",
        "directives": "directives",
        "data_source": "dataSource",
        "pipeline_config": "pipelineConfig",
        "request_mapping_template": "requestMappingTemplate",
        "response_mapping_template": "responseMappingTemplate",
    },
)
class ResolvableFieldOptions(FieldOptions):
    def __init__(
        self,
        *,
        return_type: "GraphqlType",
        args: typing.Optional[typing.Mapping[builtins.str, "GraphqlType"]] = None,
        directives: typing.Optional[typing.Sequence[Directive]] = None,
        data_source: typing.Optional[BaseDataSource] = None,
        pipeline_config: typing.Optional[typing.Sequence[IAppsyncFunction]] = None,
        request_mapping_template: typing.Optional[MappingTemplate] = None,
        response_mapping_template: typing.Optional[MappingTemplate] = None,
    ) -> None:
        '''(experimental) Properties for configuring a resolvable field.

        :param return_type: (experimental) The return type for this field.
        :param args: (experimental) The arguments for this field. i.e. type Example (first: String second: String) {} - where 'first' and 'second' are key values for args and 'String' is the GraphqlType Default: - no arguments
        :param directives: (experimental) the directives for this field. Default: - no directives
        :param data_source: (experimental) The data source creating linked to this resolvable field. Default: - no data source
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array or undefined prop will set resolver to be of type unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template

        :stability: experimental
        :exampleMetadata: infused
        :options: responseMappingTemplate - the mapping template for responses from this resolver

        Example::

            # api: appsync.GraphqlApi
            # film_node: appsync.ObjectType
            # dummy_request: appsync.MappingTemplate
            # dummy_response: appsync.MappingTemplate
            
            
            string = appsync.GraphqlType.string()
            int = appsync.GraphqlType.int()
            api.add_mutation("addFilm", appsync.ResolvableField(
                return_type=film_node.attribute(),
                args={"name": string, "film_number": int},
                data_source=api.add_none_data_source("none"),
                request_mapping_template=dummy_request,
                response_mapping_template=dummy_response
            ))
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "return_type": return_type,
        }
        if args is not None:
            self._values["args"] = args
        if directives is not None:
            self._values["directives"] = directives
        if data_source is not None:
            self._values["data_source"] = data_source
        if pipeline_config is not None:
            self._values["pipeline_config"] = pipeline_config
        if request_mapping_template is not None:
            self._values["request_mapping_template"] = request_mapping_template
        if response_mapping_template is not None:
            self._values["response_mapping_template"] = response_mapping_template

    @builtins.property
    def return_type(self) -> "GraphqlType":
        '''(experimental) The return type for this field.

        :stability: experimental
        '''
        result = self._values.get("return_type")
        assert result is not None, "Required property 'return_type' is missing"
        return typing.cast("GraphqlType", result)

    @builtins.property
    def args(self) -> typing.Optional[typing.Mapping[builtins.str, "GraphqlType"]]:
        '''(experimental) The arguments for this field.

        i.e. type Example (first: String second: String) {}

        - where 'first' and 'second' are key values for args
          and 'String' is the GraphqlType

        :default: - no arguments

        :stability: experimental
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "GraphqlType"]], result)

    @builtins.property
    def directives(self) -> typing.Optional[typing.List[Directive]]:
        '''(experimental) the directives for this field.

        :default: - no directives

        :stability: experimental
        '''
        result = self._values.get("directives")
        return typing.cast(typing.Optional[typing.List[Directive]], result)

    @builtins.property
    def data_source(self) -> typing.Optional[BaseDataSource]:
        '''(experimental) The data source creating linked to this resolvable field.

        :default: - no data source

        :stability: experimental
        '''
        result = self._values.get("data_source")
        return typing.cast(typing.Optional[BaseDataSource], result)

    @builtins.property
    def pipeline_config(self) -> typing.Optional[typing.List[IAppsyncFunction]]:
        '''(experimental) configuration of the pipeline resolver.

        :default:

        - no pipeline resolver configuration
        An empty array or undefined prop will set resolver to be of type unit

        :stability: experimental
        '''
        result = self._values.get("pipeline_config")
        return typing.cast(typing.Optional[typing.List[IAppsyncFunction]], result)

    @builtins.property
    def request_mapping_template(self) -> typing.Optional[MappingTemplate]:
        '''(experimental) The request mapping template for this resolver.

        :default: - No mapping template

        :stability: experimental
        '''
        result = self._values.get("request_mapping_template")
        return typing.cast(typing.Optional[MappingTemplate], result)

    @builtins.property
    def response_mapping_template(self) -> typing.Optional[MappingTemplate]:
        '''(experimental) The response mapping template for this resolver.

        :default: - No mapping template

        :stability: experimental
        '''
        result = self._values.get("response_mapping_template")
        return typing.cast(typing.Optional[MappingTemplate], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResolvableFieldOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Resolver(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.Resolver",
):
    '''(experimental) An AppSync resolver.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        # appsync_function: appsync.AppsyncFunction
        
        
        pipeline_resolver = appsync.Resolver(self, "pipeline",
            api=api,
            data_source=api.add_none_data_source("none"),
            type_name="typeName",
            field_name="fieldName",
            request_mapping_template=appsync.MappingTemplate.from_file("beforeRequest.vtl"),
            pipeline_config=[appsync_function],
            response_mapping_template=appsync.MappingTemplate.from_file("afterResponse.vtl")
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api: IGraphqlApi,
        data_source: typing.Optional[BaseDataSource] = None,
        field_name: builtins.str,
        type_name: builtins.str,
        caching_config: typing.Optional[CachingConfig] = None,
        pipeline_config: typing.Optional[typing.Sequence[IAppsyncFunction]] = None,
        request_mapping_template: typing.Optional[MappingTemplate] = None,
        response_mapping_template: typing.Optional[MappingTemplate] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api: (experimental) The API this resolver is attached to.
        :param data_source: (experimental) The data source this resolver is using. Default: - No datasource
        :param field_name: (experimental) name of the GraphQL field in the given type this resolver is attached to.
        :param type_name: (experimental) name of the GraphQL type this resolver is attached to.
        :param caching_config: (experimental) The caching configuration for this resolver. Default: - No caching configuration
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array | undefined sets resolver to be of kind, unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template

        :stability: experimental
        '''
        props = ResolverProps(
            api=api,
            data_source=data_source,
            field_name=field_name,
            type_name=type_name,
            caching_config=caching_config,
            pipeline_config=pipeline_config,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) the ARN of the resolver.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.ResolverProps",
    jsii_struct_bases=[ExtendedResolverProps],
    name_mapping={
        "field_name": "fieldName",
        "type_name": "typeName",
        "caching_config": "cachingConfig",
        "pipeline_config": "pipelineConfig",
        "request_mapping_template": "requestMappingTemplate",
        "response_mapping_template": "responseMappingTemplate",
        "data_source": "dataSource",
        "api": "api",
    },
)
class ResolverProps(ExtendedResolverProps):
    def __init__(
        self,
        *,
        field_name: builtins.str,
        type_name: builtins.str,
        caching_config: typing.Optional[CachingConfig] = None,
        pipeline_config: typing.Optional[typing.Sequence[IAppsyncFunction]] = None,
        request_mapping_template: typing.Optional[MappingTemplate] = None,
        response_mapping_template: typing.Optional[MappingTemplate] = None,
        data_source: typing.Optional[BaseDataSource] = None,
        api: IGraphqlApi,
    ) -> None:
        '''(experimental) Additional property for an AppSync resolver for GraphQL API reference.

        :param field_name: (experimental) name of the GraphQL field in the given type this resolver is attached to.
        :param type_name: (experimental) name of the GraphQL type this resolver is attached to.
        :param caching_config: (experimental) The caching configuration for this resolver. Default: - No caching configuration
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array | undefined sets resolver to be of kind, unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template
        :param data_source: (experimental) The data source this resolver is using. Default: - No datasource
        :param api: (experimental) The API this resolver is attached to.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # api: appsync.GraphqlApi
            # appsync_function: appsync.AppsyncFunction
            
            
            pipeline_resolver = appsync.Resolver(self, "pipeline",
                api=api,
                data_source=api.add_none_data_source("none"),
                type_name="typeName",
                field_name="fieldName",
                request_mapping_template=appsync.MappingTemplate.from_file("beforeRequest.vtl"),
                pipeline_config=[appsync_function],
                response_mapping_template=appsync.MappingTemplate.from_file("afterResponse.vtl")
            )
        '''
        if isinstance(caching_config, dict):
            caching_config = CachingConfig(**caching_config)
        self._values: typing.Dict[str, typing.Any] = {
            "field_name": field_name,
            "type_name": type_name,
            "api": api,
        }
        if caching_config is not None:
            self._values["caching_config"] = caching_config
        if pipeline_config is not None:
            self._values["pipeline_config"] = pipeline_config
        if request_mapping_template is not None:
            self._values["request_mapping_template"] = request_mapping_template
        if response_mapping_template is not None:
            self._values["response_mapping_template"] = response_mapping_template
        if data_source is not None:
            self._values["data_source"] = data_source

    @builtins.property
    def field_name(self) -> builtins.str:
        '''(experimental) name of the GraphQL field in the given type this resolver is attached to.

        :stability: experimental
        '''
        result = self._values.get("field_name")
        assert result is not None, "Required property 'field_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type_name(self) -> builtins.str:
        '''(experimental) name of the GraphQL type this resolver is attached to.

        :stability: experimental
        '''
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def caching_config(self) -> typing.Optional[CachingConfig]:
        '''(experimental) The caching configuration for this resolver.

        :default: - No caching configuration

        :stability: experimental
        '''
        result = self._values.get("caching_config")
        return typing.cast(typing.Optional[CachingConfig], result)

    @builtins.property
    def pipeline_config(self) -> typing.Optional[typing.List[IAppsyncFunction]]:
        '''(experimental) configuration of the pipeline resolver.

        :default:

        - no pipeline resolver configuration
        An empty array | undefined sets resolver to be of kind, unit

        :stability: experimental
        '''
        result = self._values.get("pipeline_config")
        return typing.cast(typing.Optional[typing.List[IAppsyncFunction]], result)

    @builtins.property
    def request_mapping_template(self) -> typing.Optional[MappingTemplate]:
        '''(experimental) The request mapping template for this resolver.

        :default: - No mapping template

        :stability: experimental
        '''
        result = self._values.get("request_mapping_template")
        return typing.cast(typing.Optional[MappingTemplate], result)

    @builtins.property
    def response_mapping_template(self) -> typing.Optional[MappingTemplate]:
        '''(experimental) The response mapping template for this resolver.

        :default: - No mapping template

        :stability: experimental
        '''
        result = self._values.get("response_mapping_template")
        return typing.cast(typing.Optional[MappingTemplate], result)

    @builtins.property
    def data_source(self) -> typing.Optional[BaseDataSource]:
        '''(experimental) The data source this resolver is using.

        :default: - No datasource

        :stability: experimental
        '''
        result = self._values.get("data_source")
        return typing.cast(typing.Optional[BaseDataSource], result)

    @builtins.property
    def api(self) -> IGraphqlApi:
        '''(experimental) The API this resolver is attached to.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(IGraphqlApi, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResolverProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Schema(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync-alpha.Schema"):
    '''(experimental) The Schema for a GraphQL Api.

    If no options are configured, schema will be generated
    code-first.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        api = appsync.GraphqlApi(self, "api",
            name="api",
            schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql"))
        )
        
        http_ds = api.add_http_data_source("ds", "https://states.amazonaws.com",
            name="httpDsWithStepF",
            description="from appsync to StepFunctions Workflow",
            authorization_config=appsync.AwsIamConfig(
                signing_region="us-east-1",
                signing_service_name="states"
            )
        )
        
        http_ds.create_resolver(
            type_name="Mutation",
            field_name="callStepFunction",
            request_mapping_template=appsync.MappingTemplate.from_file("request.vtl"),
            response_mapping_template=appsync.MappingTemplate.from_file("response.vtl")
        )
    '''

    def __init__(self, *, file_path: typing.Optional[builtins.str] = None) -> None:
        '''
        :param file_path: (experimental) The file path for the schema. When this option is configured, then the schema will be generated from an existing file from disk. Default: - schema not configured through disk asset

        :stability: experimental
        '''
        options = SchemaOptions(file_path=file_path)

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="fromAsset") # type: ignore[misc]
    @builtins.classmethod
    def from_asset(cls, file_path: builtins.str) -> "Schema":
        '''(experimental) Generate a Schema from file.

        :param file_path: the file path of the schema file.

        :return: ``SchemaAsset`` with immutable schema defintion

        :stability: experimental
        '''
        return typing.cast("Schema", jsii.sinvoke(cls, "fromAsset", [file_path]))

    @jsii.member(jsii_name="addMutation")
    def add_mutation(
        self,
        field_name: builtins.str,
        field: "ResolvableField",
    ) -> ObjectType:
        '''(experimental) Add a mutation field to the schema's Mutation. CDK will create an Object Type called 'Mutation'. For example,.

        type Mutation {
        fieldName: Field.returnType
        }

        :param field_name: the name of the Mutation.
        :param field: the resolvable field to for this Mutation.

        :stability: experimental
        '''
        return typing.cast(ObjectType, jsii.invoke(self, "addMutation", [field_name, field]))

    @jsii.member(jsii_name="addQuery")
    def add_query(
        self,
        field_name: builtins.str,
        field: "ResolvableField",
    ) -> ObjectType:
        '''(experimental) Add a query field to the schema's Query. CDK will create an Object Type called 'Query'. For example,.

        type Query {
        fieldName: Field.returnType
        }

        :param field_name: the name of the query.
        :param field: the resolvable field to for this query.

        :stability: experimental
        '''
        return typing.cast(ObjectType, jsii.invoke(self, "addQuery", [field_name, field]))

    @jsii.member(jsii_name="addSubscription")
    def add_subscription(self, field_name: builtins.str, field: "Field") -> ObjectType:
        '''(experimental) Add a subscription field to the schema's Subscription. CDK will create an Object Type called 'Subscription'. For example,.

        type Subscription {
        fieldName: Field.returnType
        }

        :param field_name: the name of the Subscription.
        :param field: the resolvable field to for this Subscription.

        :stability: experimental
        '''
        return typing.cast(ObjectType, jsii.invoke(self, "addSubscription", [field_name, field]))

    @jsii.member(jsii_name="addToSchema")
    def add_to_schema(
        self,
        addition: builtins.str,
        delimiter: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Escape hatch to add to Schema as desired.

        Will always result
        in a newline.

        :param addition: the addition to add to schema.
        :param delimiter: the delimiter between schema and addition.

        :default: - ''

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addToSchema", [addition, delimiter]))

    @jsii.member(jsii_name="addType")
    def add_type(self, type: IIntermediateType) -> IIntermediateType:
        '''(experimental) Add type to the schema.

        :param type: the intermediate type to add to the schema.

        :stability: experimental
        '''
        return typing.cast(IIntermediateType, jsii.invoke(self, "addType", [type]))

    @jsii.member(jsii_name="bind")
    def bind(self, api: "GraphqlApi") -> aws_cdk.aws_appsync.CfnGraphQLSchema:
        '''(experimental) Called when the GraphQL Api is initialized to allow this object to bind to the stack.

        :param api: The binding GraphQL Api.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_appsync.CfnGraphQLSchema, jsii.invoke(self, "bind", [api]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> builtins.str:
        '''(experimental) The definition for this schema.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "definition"))

    @definition.setter
    def definition(self, value: builtins.str) -> None:
        jsii.set(self, "definition", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.SchemaOptions",
    jsii_struct_bases=[],
    name_mapping={"file_path": "filePath"},
)
class SchemaOptions:
    def __init__(self, *, file_path: typing.Optional[builtins.str] = None) -> None:
        '''(experimental) The options for configuring a schema.

        If no options are specified, then the schema will
        be generated code-first.

        :param file_path: (experimental) The file path for the schema. When this option is configured, then the schema will be generated from an existing file from disk. Default: - schema not configured through disk asset

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            
            schema_options = appsync_alpha.SchemaOptions(
                file_path="filePath"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if file_path is not None:
            self._values["file_path"] = file_path

    @builtins.property
    def file_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) The file path for the schema.

        When this option is
        configured, then the schema will be generated from an
        existing file from disk.

        :default: - schema not configured through disk asset

        :stability: experimental
        '''
        result = self._values.get("file_path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SchemaOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SortKeyStep(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.SortKeyStep",
):
    '''(experimental) Utility class to allow assigning a value or an auto-generated id to a sort key.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_appsync_alpha as appsync_alpha
        
        # assign: appsync_alpha.Assign
        
        sort_key_step = appsync_alpha.SortKeyStep(assign, "skey")
    '''

    def __init__(self, pkey: Assign, skey: builtins.str) -> None:
        '''
        :param pkey: -
        :param skey: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [pkey, skey])

    @jsii.member(jsii_name="auto")
    def auto(self) -> PrimaryKey:
        '''(experimental) Assign an auto-generated value to the sort key.

        :stability: experimental
        '''
        return typing.cast(PrimaryKey, jsii.invoke(self, "auto", []))

    @jsii.member(jsii_name="is")
    def is_(self, val: builtins.str) -> PrimaryKey:
        '''(experimental) Assign an auto-generated value to the sort key.

        :param val: -

        :stability: experimental
        '''
        return typing.cast(PrimaryKey, jsii.invoke(self, "is", [val]))


@jsii.enum(jsii_type="@aws-cdk/aws-appsync-alpha.Type")
class Type(enum.Enum):
    '''(experimental) Enum containing the Types that can be used to define ObjectTypes.

    :stability: experimental
    '''

    ID = "ID"
    '''(experimental) ``ID`` scalar type is a unique identifier. ``ID`` type is serialized similar to ``String``.

    Often used as a key for a cache and not intended to be human-readable.

    :stability: experimental
    '''
    STRING = "STRING"
    '''(experimental) ``String`` scalar type is a free-form human-readable text.

    :stability: experimental
    '''
    INT = "INT"
    '''(experimental) ``Int`` scalar type is a signed non-fractional numerical value.

    :stability: experimental
    '''
    FLOAT = "FLOAT"
    '''(experimental) ``Float`` scalar type is a signed double-precision fractional value.

    :stability: experimental
    '''
    BOOLEAN = "BOOLEAN"
    '''(experimental) ``Boolean`` scalar type is a boolean value: true or false.

    :stability: experimental
    '''
    AWS_DATE = "AWS_DATE"
    '''(experimental) ``AWSDate`` scalar type represents a valid extended ``ISO 8601 Date`` string.

    In other words, accepts date strings in the form of ``YYYY-MM-DD``. It accepts time zone offsets.

    :see: https://en.wikipedia.org/wiki/ISO_8601#Calendar_dates
    :stability: experimental
    '''
    AWS_TIME = "AWS_TIME"
    '''(experimental) ``AWSTime`` scalar type represents a valid extended ``ISO 8601 Time`` string.

    In other words, accepts date strings in the form of ``hh:mm:ss.sss``. It accepts time zone offsets.

    :see: https://en.wikipedia.org/wiki/ISO_8601#Times
    :stability: experimental
    '''
    AWS_DATE_TIME = "AWS_DATE_TIME"
    '''(experimental) ``AWSDateTime`` scalar type represents a valid extended ``ISO 8601 DateTime`` string.

    In other words, accepts date strings in the form of ``YYYY-MM-DDThh:mm:ss.sssZ``. It accepts time zone offsets.

    :see: https://en.wikipedia.org/wiki/ISO_8601#Combined_date_and_time_representations
    :stability: experimental
    '''
    AWS_TIMESTAMP = "AWS_TIMESTAMP"
    '''(experimental) ``AWSTimestamp`` scalar type represents the number of seconds since ``1970-01-01T00:00Z``.

    Timestamps are serialized and deserialized as numbers.

    :stability: experimental
    '''
    AWS_EMAIL = "AWS_EMAIL"
    '''(experimental) ``AWSEmail`` scalar type represents an email address string (i.e.``username@example.com``).

    :stability: experimental
    '''
    AWS_JSON = "AWS_JSON"
    '''(experimental) ``AWSJson`` scalar type represents a JSON string.

    :stability: experimental
    '''
    AWS_URL = "AWS_URL"
    '''(experimental) ``AWSURL`` scalar type represetns a valid URL string.

    URLs wihtout schemes or contain double slashes are considered invalid.

    :stability: experimental
    '''
    AWS_PHONE = "AWS_PHONE"
    '''(experimental) ``AWSPhone`` scalar type represents a valid phone number. Phone numbers maybe be whitespace delimited or hyphenated.

    The number can specify a country code at the beginning, but is not required for US phone numbers.

    :stability: experimental
    '''
    AWS_IP_ADDRESS = "AWS_IP_ADDRESS"
    '''(experimental) ``AWSIPAddress`` scalar type respresents a valid ``IPv4`` of ``IPv6`` address string.

    :stability: experimental
    '''
    INTERMEDIATE = "INTERMEDIATE"
    '''(experimental) Type used for Intermediate Types (i.e. an interface or an object type).

    :stability: experimental
    '''


@jsii.implements(IIntermediateType)
class UnionType(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.UnionType",
):
    '''(experimental) Union Types are abstract types that are similar to Interface Types, but they cannot to specify any common fields between types.

    Note that fields of a union type need to be object types. In other words,
    you can't create a union type out of interfaces, other unions, or inputs.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        
        string = appsync.GraphqlType.string()
        human = appsync.ObjectType("Human", definition={"name": string})
        droid = appsync.ObjectType("Droid", definition={"name": string})
        starship = appsync.ObjectType("Starship", definition={"name": string})
        search = appsync.UnionType("Search",
            definition=[human, droid, starship]
        )
        api.add_type(search)
    '''

    def __init__(
        self,
        name: builtins.str,
        *,
        definition: typing.Sequence[IIntermediateType],
    ) -> None:
        '''
        :param name: -
        :param definition: (experimental) the object types for this union type.

        :stability: experimental
        '''
        options = UnionTypeOptions(definition=definition)

        jsii.create(self.__class__, self, [name, options])

    @jsii.member(jsii_name="addField")
    def add_field(
        self,
        *,
        field: typing.Optional[IField] = None,
        field_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add a field to this Union Type.

        Input Types must have field options and the IField must be an Object Type.

        :param field: (experimental) The resolvable field to add. This option must be configured for Object, Interface, Input and Union Types. Default: - no IField
        :param field_name: (experimental) The name of the field. This option must be configured for Object, Interface, Input and Enum Types. Default: - no fieldName

        :stability: experimental
        '''
        options = AddFieldOptions(field=field, field_name=field_name)

        return typing.cast(None, jsii.invoke(self, "addField", [options]))

    @jsii.member(jsii_name="attribute")
    def attribute(
        self,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) Create a GraphQL Type representing this Union Type.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.invoke(self, "attribute", [options]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the string of this Union type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.Mapping[builtins.str, IField]:
        '''(experimental) the attributes of this type.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, IField], jsii.get(self, "definition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) the name of this type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modes")
    def _modes(self) -> typing.Optional[typing.List[AuthorizationType]]:
        '''(experimental) the authorization modes supported by this intermediate type.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[AuthorizationType]], jsii.get(self, "modes"))

    @_modes.setter
    def _modes(self, value: typing.Optional[typing.List[AuthorizationType]]) -> None:
        jsii.set(self, "modes", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.UnionTypeOptions",
    jsii_struct_bases=[],
    name_mapping={"definition": "definition"},
)
class UnionTypeOptions:
    def __init__(self, *, definition: typing.Sequence[IIntermediateType]) -> None:
        '''(experimental) Properties for configuring an Union Type.

        :param definition: (experimental) the object types for this union type.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # api: appsync.GraphqlApi
            
            string = appsync.GraphqlType.string()
            human = appsync.ObjectType("Human", definition={"name": string})
            droid = appsync.ObjectType("Droid", definition={"name": string})
            starship = appsync.ObjectType("Starship", definition={"name": string})
            search = appsync.UnionType("Search",
                definition=[human, droid, starship]
            )
            api.add_type(search)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "definition": definition,
        }

    @builtins.property
    def definition(self) -> typing.List[IIntermediateType]:
        '''(experimental) the object types for this union type.

        :stability: experimental
        '''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast(typing.List[IIntermediateType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UnionTypeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.UserPoolConfig",
    jsii_struct_bases=[],
    name_mapping={
        "user_pool": "userPool",
        "app_id_client_regex": "appIdClientRegex",
        "default_action": "defaultAction",
    },
)
class UserPoolConfig:
    def __init__(
        self,
        *,
        user_pool: aws_cdk.aws_cognito.IUserPool,
        app_id_client_regex: typing.Optional[builtins.str] = None,
        default_action: typing.Optional["UserPoolDefaultAction"] = None,
    ) -> None:
        '''(experimental) Configuration for Cognito user-pools in AppSync.

        :param user_pool: (experimental) The Cognito user pool to use as identity source.
        :param app_id_client_regex: (experimental) the optional app id regex. Default: - None
        :param default_action: (experimental) Default auth action. Default: ALLOW

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            from aws_cdk import aws_cognito as cognito
            
            # user_pool: cognito.UserPool
            
            user_pool_config = appsync_alpha.UserPoolConfig(
                user_pool=user_pool,
            
                # the properties below are optional
                app_id_client_regex="appIdClientRegex",
                default_action=appsync_alpha.UserPoolDefaultAction.ALLOW
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool": user_pool,
        }
        if app_id_client_regex is not None:
            self._values["app_id_client_regex"] = app_id_client_regex
        if default_action is not None:
            self._values["default_action"] = default_action

    @builtins.property
    def user_pool(self) -> aws_cdk.aws_cognito.IUserPool:
        '''(experimental) The Cognito user pool to use as identity source.

        :stability: experimental
        '''
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(aws_cdk.aws_cognito.IUserPool, result)

    @builtins.property
    def app_id_client_regex(self) -> typing.Optional[builtins.str]:
        '''(experimental) the optional app id regex.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("app_id_client_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_action(self) -> typing.Optional["UserPoolDefaultAction"]:
        '''(experimental) Default auth action.

        :default: ALLOW

        :stability: experimental
        '''
        result = self._values.get("default_action")
        return typing.cast(typing.Optional["UserPoolDefaultAction"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserPoolConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-appsync-alpha.UserPoolDefaultAction")
class UserPoolDefaultAction(enum.Enum):
    '''(experimental) enum with all possible values for Cognito user-pool default actions.

    :stability: experimental
    '''

    ALLOW = "ALLOW"
    '''(experimental) ALLOW access to API.

    :stability: experimental
    '''
    DENY = "DENY"
    '''(experimental) DENY access to API.

    :stability: experimental
    '''


class Values(metaclass=jsii.JSIIMeta, jsii_type="@aws-cdk/aws-appsync-alpha.Values"):
    '''(experimental) Factory class for attribute value assignments.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        api = appsync.GraphqlApi(self, "Api",
            name="demo",
            schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql")),
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.IAM
                )
            ),
            xray_enabled=True
        )
        
        demo_table = dynamodb.Table(self, "DemoTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        demo_dS = api.add_dynamo_db_data_source("demoDataSource", demo_table)
        
        # Resolver for the Query "getDemos" that scans the DynamoDb table and returns the entire list.
        demo_dS.create_resolver(
            type_name="Query",
            field_name="getDemos",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
        )
        
        # Resolver for the Mutation "addDemo" that puts the item into the DynamoDb table.
        demo_dS.create_resolver(
            type_name="Mutation",
            field_name="addDemo",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
                appsync.PrimaryKey.partition("id").auto(),
                appsync.Values.projecting("input")),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="attribute") # type: ignore[misc]
    @builtins.classmethod
    def attribute(cls, attr: builtins.str) -> AttributeValuesStep:
        '''(experimental) Allows assigning a value to the specified attribute.

        :param attr: -

        :stability: experimental
        '''
        return typing.cast(AttributeValuesStep, jsii.sinvoke(cls, "attribute", [attr]))

    @jsii.member(jsii_name="projecting") # type: ignore[misc]
    @builtins.classmethod
    def projecting(cls, arg: typing.Optional[builtins.str] = None) -> AttributeValues:
        '''(experimental) Treats the specified object as a map of assignments, where the property names represent attribute names.

        It’s opinionated about how it represents
        some of the nested objects: e.g., it will use lists (“L”) rather than sets
        (“SS”, “NS”, “BS”). By default it projects the argument container ("$ctx.args").

        :param arg: -

        :stability: experimental
        '''
        return typing.cast(AttributeValues, jsii.sinvoke(cls, "projecting", [arg]))


@jsii.implements(IAppsyncFunction)
class AppsyncFunction(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.AppsyncFunction",
):
    '''(experimental) AppSync Functions are local functions that perform certain operations onto a backend data source.

    Developers can compose operations (Functions)
    and execute them in sequence with Pipeline Resolvers.

    :stability: experimental
    :exampleMetadata: infused
    :resource: AWS::AppSync::FunctionConfiguration

    Example::

        # api: appsync.GraphqlApi
        
        
        appsync_function = appsync.AppsyncFunction(self, "function",
            name="appsync_function",
            api=api,
            data_source=api.add_none_data_source("none"),
            request_mapping_template=appsync.MappingTemplate.from_file("request.vtl"),
            response_mapping_template=appsync.MappingTemplate.from_file("response.vtl")
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api: IGraphqlApi,
        data_source: BaseDataSource,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        request_mapping_template: typing.Optional[MappingTemplate] = None,
        response_mapping_template: typing.Optional[MappingTemplate] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api: (experimental) the GraphQL Api linked to this AppSync Function.
        :param data_source: (experimental) the data source linked to this AppSync Function.
        :param name: (experimental) the name of the AppSync Function.
        :param description: (experimental) the description for this AppSync Function. Default: - no description
        :param request_mapping_template: (experimental) the request mapping template for the AppSync Function. Default: - no request mapping template
        :param response_mapping_template: (experimental) the response mapping template for the AppSync Function. Default: - no response mapping template

        :stability: experimental
        '''
        props = AppsyncFunctionProps(
            api=api,
            data_source=data_source,
            name=name,
            description=description,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAppsyncFunctionAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_appsync_function_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function_arn: builtins.str,
    ) -> IAppsyncFunction:
        '''(experimental) Import Appsync Function from arn.

        :param scope: -
        :param id: -
        :param function_arn: (experimental) the ARN of the AppSync function.

        :stability: experimental
        '''
        attrs = AppsyncFunctionAttributes(function_arn=function_arn)

        return typing.cast(IAppsyncFunction, jsii.sinvoke(cls, "fromAppsyncFunctionAttributes", [scope, id, attrs]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataSource")
    def data_source(self) -> BaseDataSource:
        '''(experimental) the data source of this AppSync Function.

        :stability: experimental
        :attribute: DataSourceName
        '''
        return typing.cast(BaseDataSource, jsii.get(self, "dataSource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionArn")
    def function_arn(self) -> builtins.str:
        '''(experimental) the ARN of the AppSync function.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "functionArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionId")
    def function_id(self) -> builtins.str:
        '''(experimental) the ID of the AppSync function.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "functionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        '''(experimental) the name of this AppSync Function.

        :stability: experimental
        :attribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "functionName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.AppsyncFunctionProps",
    jsii_struct_bases=[BaseAppsyncFunctionProps],
    name_mapping={
        "name": "name",
        "description": "description",
        "request_mapping_template": "requestMappingTemplate",
        "response_mapping_template": "responseMappingTemplate",
        "api": "api",
        "data_source": "dataSource",
    },
)
class AppsyncFunctionProps(BaseAppsyncFunctionProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        request_mapping_template: typing.Optional[MappingTemplate] = None,
        response_mapping_template: typing.Optional[MappingTemplate] = None,
        api: IGraphqlApi,
        data_source: BaseDataSource,
    ) -> None:
        '''(experimental) the CDK properties for AppSync Functions.

        :param name: (experimental) the name of the AppSync Function.
        :param description: (experimental) the description for this AppSync Function. Default: - no description
        :param request_mapping_template: (experimental) the request mapping template for the AppSync Function. Default: - no request mapping template
        :param response_mapping_template: (experimental) the response mapping template for the AppSync Function. Default: - no response mapping template
        :param api: (experimental) the GraphQL Api linked to this AppSync Function.
        :param data_source: (experimental) the data source linked to this AppSync Function.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # api: appsync.GraphqlApi
            
            
            appsync_function = appsync.AppsyncFunction(self, "function",
                name="appsync_function",
                api=api,
                data_source=api.add_none_data_source("none"),
                request_mapping_template=appsync.MappingTemplate.from_file("request.vtl"),
                response_mapping_template=appsync.MappingTemplate.from_file("response.vtl")
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "api": api,
            "data_source": data_source,
        }
        if description is not None:
            self._values["description"] = description
        if request_mapping_template is not None:
            self._values["request_mapping_template"] = request_mapping_template
        if response_mapping_template is not None:
            self._values["response_mapping_template"] = response_mapping_template

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) the name of the AppSync Function.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) the description for this AppSync Function.

        :default: - no description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_mapping_template(self) -> typing.Optional[MappingTemplate]:
        '''(experimental) the request mapping template for the AppSync Function.

        :default: - no request mapping template

        :stability: experimental
        '''
        result = self._values.get("request_mapping_template")
        return typing.cast(typing.Optional[MappingTemplate], result)

    @builtins.property
    def response_mapping_template(self) -> typing.Optional[MappingTemplate]:
        '''(experimental) the response mapping template for the AppSync Function.

        :default: - no response mapping template

        :stability: experimental
        '''
        result = self._values.get("response_mapping_template")
        return typing.cast(typing.Optional[MappingTemplate], result)

    @builtins.property
    def api(self) -> IGraphqlApi:
        '''(experimental) the GraphQL Api linked to this AppSync Function.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(IGraphqlApi, result)

    @builtins.property
    def data_source(self) -> BaseDataSource:
        '''(experimental) the data source linked to this AppSync Function.

        :stability: experimental
        '''
        result = self._values.get("data_source")
        assert result is not None, "Required property 'data_source' is missing"
        return typing.cast(BaseDataSource, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppsyncFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_iam.IGrantable)
class BackedDataSource(
    BaseDataSource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-appsync-alpha.BackedDataSource",
):
    '''(experimental) Abstract AppSync datasource implementation.

    Do not use directly but use subclasses for resource backed datasources

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: "BackedDataSourceProps",
        *,
        type: builtins.str,
        dynamo_db_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.DynamoDBConfigProperty, aws_cdk.IResolvable]] = None,
        elasticsearch_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.ElasticsearchConfigProperty, aws_cdk.IResolvable]] = None,
        http_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.HttpConfigProperty, aws_cdk.IResolvable]] = None,
        lambda_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.LambdaConfigProperty, aws_cdk.IResolvable]] = None,
        relational_database_config: typing.Optional[typing.Union[aws_cdk.aws_appsync.CfnDataSource.RelationalDatabaseConfigProperty, aws_cdk.IResolvable]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        :param type: (experimental) the type of the AppSync datasource.
        :param dynamo_db_config: (experimental) configuration for DynamoDB Datasource. Default: - No config
        :param elasticsearch_config: (experimental) configuration for Elasticsearch Datasource. Default: - No config
        :param http_config: (experimental) configuration for HTTP Datasource. Default: - No config
        :param lambda_config: (experimental) configuration for Lambda Datasource. Default: - No config
        :param relational_database_config: (experimental) configuration for RDS Datasource. Default: - No config

        :stability: experimental
        '''
        extended = ExtendedDataSourceProps(
            type=type,
            dynamo_db_config=dynamo_db_config,
            elasticsearch_config=elasticsearch_config,
            http_config=http_config,
            lambda_config=lambda_config,
            relational_database_config=relational_database_config,
        )

        jsii.create(self.__class__, self, [scope, id, props, extended])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) the principal of the data source to be IGrantable.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))


class _BackedDataSourceProxy(
    BackedDataSource, jsii.proxy_for(BaseDataSource) # type: ignore[misc]
):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BackedDataSource).__jsii_proxy_class__ = lambda : _BackedDataSourceProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.BackedDataSourceProps",
    jsii_struct_bases=[BaseDataSourceProps],
    name_mapping={
        "api": "api",
        "description": "description",
        "name": "name",
        "service_role": "serviceRole",
    },
)
class BackedDataSourceProps(BaseDataSourceProps):
    def __init__(
        self,
        *,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''(experimental) properties for an AppSync datasource backed by a resource.

        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source
        :param service_role: (experimental) The IAM service role to be assumed by AppSync to interact with the data source. Default: - Create a new role

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            from aws_cdk import aws_iam as iam
            
            # graphql_api: appsync_alpha.GraphqlApi
            # role: iam.Role
            
            backed_data_source_props = appsync_alpha.BackedDataSourceProps(
                api=graphql_api,
            
                # the properties below are optional
                description="description",
                name="name",
                service_role=role
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api": api,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if service_role is not None:
            self._values["service_role"] = service_role

    @builtins.property
    def api(self) -> IGraphqlApi:
        '''(experimental) The API to attach this data source to.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(IGraphqlApi, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) the description of the data source.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the data source.

        :default: - id of data source

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM service role to be assumed by AppSync to interact with the data source.

        :default: - Create a new role

        :stability: experimental
        '''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackedDataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamoDbDataSource(
    BackedDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.DynamoDbDataSource",
):
    '''(experimental) An AppSync datasource backed by a DynamoDB table.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        api = appsync.GraphqlApi(self, "Api",
            name="demo",
            schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql")),
            authorization_config=appsync.AuthorizationConfig(
                default_authorization=appsync.AuthorizationMode(
                    authorization_type=appsync.AuthorizationType.IAM
                )
            ),
            xray_enabled=True
        )
        
        demo_table = dynamodb.Table(self, "DemoTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        demo_dS = api.add_dynamo_db_data_source("demoDataSource", demo_table)
        
        # Resolver for the Query "getDemos" that scans the DynamoDb table and returns the entire list.
        demo_dS.create_resolver(
            type_name="Query",
            field_name="getDemos",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_scan_table(),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_list()
        )
        
        # Resolver for the Mutation "addDemo" that puts the item into the DynamoDb table.
        demo_dS.create_resolver(
            type_name="Mutation",
            field_name="addDemo",
            request_mapping_template=appsync.MappingTemplate.dynamo_db_put_item(
                appsync.PrimaryKey.partition("id").auto(),
                appsync.Values.projecting("input")),
            response_mapping_template=appsync.MappingTemplate.dynamo_db_result_item()
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        table: aws_cdk.aws_dynamodb.ITable,
        read_only_access: typing.Optional[builtins.bool] = None,
        use_caller_credentials: typing.Optional[builtins.bool] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param table: (experimental) The DynamoDB table backing this data source.
        :param read_only_access: (experimental) Specify whether this DS is read only or has read and write permissions to the DynamoDB table. Default: false
        :param use_caller_credentials: (experimental) use credentials of caller to access DynamoDB. Default: false
        :param service_role: (experimental) The IAM service role to be assumed by AppSync to interact with the data source. Default: - Create a new role
        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source

        :stability: experimental
        '''
        props = DynamoDbDataSourceProps(
            table=table,
            read_only_access=read_only_access,
            use_caller_credentials=use_caller_credentials,
            service_role=service_role,
            api=api,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.DynamoDbDataSourceProps",
    jsii_struct_bases=[BackedDataSourceProps],
    name_mapping={
        "api": "api",
        "description": "description",
        "name": "name",
        "service_role": "serviceRole",
        "table": "table",
        "read_only_access": "readOnlyAccess",
        "use_caller_credentials": "useCallerCredentials",
    },
)
class DynamoDbDataSourceProps(BackedDataSourceProps):
    def __init__(
        self,
        *,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        table: aws_cdk.aws_dynamodb.ITable,
        read_only_access: typing.Optional[builtins.bool] = None,
        use_caller_credentials: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Properties for an AppSync DynamoDB datasource.

        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source
        :param service_role: (experimental) The IAM service role to be assumed by AppSync to interact with the data source. Default: - Create a new role
        :param table: (experimental) The DynamoDB table backing this data source.
        :param read_only_access: (experimental) Specify whether this DS is read only or has read and write permissions to the DynamoDB table. Default: false
        :param use_caller_credentials: (experimental) use credentials of caller to access DynamoDB. Default: false

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            from aws_cdk import aws_dynamodb as dynamodb
            from aws_cdk import aws_iam as iam
            
            # graphql_api: appsync_alpha.GraphqlApi
            # role: iam.Role
            # table: dynamodb.Table
            
            dynamo_db_data_source_props = appsync_alpha.DynamoDbDataSourceProps(
                api=graphql_api,
                table=table,
            
                # the properties below are optional
                description="description",
                name="name",
                read_only_access=False,
                service_role=role,
                use_caller_credentials=False
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api": api,
            "table": table,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if service_role is not None:
            self._values["service_role"] = service_role
        if read_only_access is not None:
            self._values["read_only_access"] = read_only_access
        if use_caller_credentials is not None:
            self._values["use_caller_credentials"] = use_caller_credentials

    @builtins.property
    def api(self) -> IGraphqlApi:
        '''(experimental) The API to attach this data source to.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(IGraphqlApi, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) the description of the data source.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the data source.

        :default: - id of data source

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM service role to be assumed by AppSync to interact with the data source.

        :default: - Create a new role

        :stability: experimental
        '''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''(experimental) The DynamoDB table backing this data source.

        :stability: experimental
        '''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(aws_cdk.aws_dynamodb.ITable, result)

    @builtins.property
    def read_only_access(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specify whether this DS is read only or has read and write permissions to the DynamoDB table.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("read_only_access")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def use_caller_credentials(self) -> typing.Optional[builtins.bool]:
        '''(experimental) use credentials of caller to access DynamoDB.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("use_caller_credentials")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamoDbDataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ElasticsearchDataSource(
    BackedDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.ElasticsearchDataSource",
):
    '''(experimental) An Appsync datasource backed by Elasticsearch.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import aws_cdk.aws_elasticsearch as es
        
        # api: appsync.GraphqlApi
        
        
        user = iam.User(self, "User")
        domain = es.Domain(self, "Domain",
            version=es.ElasticsearchVersion.V7_1,
            removal_policy=RemovalPolicy.DESTROY,
            fine_grained_access_control=es.AdvancedSecurityOptions(master_user_arn=user.user_arn),
            encryption_at_rest=es.EncryptionAtRestOptions(enabled=True),
            node_to_node_encryption=True,
            enforce_https=True
        )
        ds = api.add_elasticsearch_data_source("ds", domain)
        
        ds.create_resolver(
            type_name="Query",
            field_name="getTests",
            request_mapping_template=appsync.MappingTemplate.from_string(JSON.stringify({
                "version": "2017-02-28",
                "operation": "GET",
                "path": "/id/post/_search",
                "params": {
                    "headers": {},
                    "query_string": {},
                    "body": {"from": 0, "size": 50}
                }
            })),
            response_mapping_template=appsync.MappingTemplate.from_string("""[
                    #foreach($entry in $context.result.hits.hits)
                    #if( $velocityCount > 1 ) , #end
                    $utils.toJson($entry.get("_source"))
                    #end
                  ]""")
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: aws_cdk.aws_elasticsearch.IDomain,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain: (experimental) The elasticsearch domain containing the endpoint for the data source.
        :param service_role: (experimental) The IAM service role to be assumed by AppSync to interact with the data source. Default: - Create a new role
        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source

        :stability: experimental
        '''
        props = ElasticsearchDataSourceProps(
            domain=domain,
            service_role=service_role,
            api=api,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.ElasticsearchDataSourceProps",
    jsii_struct_bases=[BackedDataSourceProps],
    name_mapping={
        "api": "api",
        "description": "description",
        "name": "name",
        "service_role": "serviceRole",
        "domain": "domain",
    },
)
class ElasticsearchDataSourceProps(BackedDataSourceProps):
    def __init__(
        self,
        *,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        domain: aws_cdk.aws_elasticsearch.IDomain,
    ) -> None:
        '''(experimental) Properities for the Elasticsearch Data Source.

        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source
        :param service_role: (experimental) The IAM service role to be assumed by AppSync to interact with the data source. Default: - Create a new role
        :param domain: (experimental) The elasticsearch domain containing the endpoint for the data source.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            from aws_cdk import aws_elasticsearch as elasticsearch
            from aws_cdk import aws_iam as iam
            
            # domain: elasticsearch.Domain
            # graphql_api: appsync_alpha.GraphqlApi
            # role: iam.Role
            
            elasticsearch_data_source_props = appsync_alpha.ElasticsearchDataSourceProps(
                api=graphql_api,
                domain=domain,
            
                # the properties below are optional
                description="description",
                name="name",
                service_role=role
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api": api,
            "domain": domain,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if service_role is not None:
            self._values["service_role"] = service_role

    @builtins.property
    def api(self) -> IGraphqlApi:
        '''(experimental) The API to attach this data source to.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(IGraphqlApi, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) the description of the data source.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the data source.

        :default: - id of data source

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM service role to be assumed by AppSync to interact with the data source.

        :default: - Create a new role

        :stability: experimental
        '''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def domain(self) -> aws_cdk.aws_elasticsearch.IDomain:
        '''(experimental) The elasticsearch domain containing the endpoint for the data source.

        :stability: experimental
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(aws_cdk.aws_elasticsearch.IDomain, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ElasticsearchDataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IIntermediateType)
class EnumType(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.EnumType",
):
    '''(experimental) Enum Types are abstract types that includes a set of fields that represent the strings this type can create.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        
        episode = appsync.EnumType("Episode",
            definition=["NEWHOPE", "EMPIRE", "JEDI"
            ]
        )
        api.add_type(episode)
    '''

    def __init__(
        self,
        name: builtins.str,
        *,
        definition: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: -
        :param definition: (experimental) the attributes of this type.

        :stability: experimental
        '''
        options = EnumTypeOptions(definition=definition)

        jsii.create(self.__class__, self, [name, options])

    @jsii.member(jsii_name="addField")
    def add_field(
        self,
        *,
        field: typing.Optional[IField] = None,
        field_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Add a field to this Enum Type.

        To add a field to this Enum Type, you must only configure
        addField with the fieldName options.

        :param field: (experimental) The resolvable field to add. This option must be configured for Object, Interface, Input and Union Types. Default: - no IField
        :param field_name: (experimental) The name of the field. This option must be configured for Object, Interface, Input and Enum Types. Default: - no fieldName

        :stability: experimental
        '''
        options = AddFieldOptions(field=field, field_name=field_name)

        return typing.cast(None, jsii.invoke(self, "addField", [options]))

    @jsii.member(jsii_name="attribute")
    def attribute(
        self,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) Create an GraphQL Type representing this Enum Type.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.invoke(self, "attribute", [options]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the string of this enum type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> typing.Mapping[builtins.str, IField]:
        '''(experimental) the attributes of this type.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, IField], jsii.get(self, "definition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) the name of this type.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modes")
    def _modes(self) -> typing.Optional[typing.List[AuthorizationType]]:
        '''(experimental) the authorization modes for this intermediate type.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[AuthorizationType]], jsii.get(self, "modes"))

    @_modes.setter
    def _modes(self, value: typing.Optional[typing.List[AuthorizationType]]) -> None:
        jsii.set(self, "modes", value)


@jsii.implements(IGraphqlApi)
class GraphqlApiBase(
    aws_cdk.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-appsync-alpha.GraphqlApiBase",
):
    '''(experimental) Base Class for GraphQL API.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        props = aws_cdk.ResourceProps(
            account=account,
            environment_from_arn=environment_from_arn,
            physical_name=physical_name,
            region=region,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addDynamoDbDataSource")
    def add_dynamo_db_data_source(
        self,
        id: builtins.str,
        table: aws_cdk.aws_dynamodb.ITable,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> DynamoDbDataSource:
        '''(experimental) add a new DynamoDB data source to this API.

        :param id: The data source's id.
        :param table: The DynamoDB table backing this data source.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = DataSourceOptions(description=description, name=name)

        return typing.cast(DynamoDbDataSource, jsii.invoke(self, "addDynamoDbDataSource", [id, table, options]))

    @jsii.member(jsii_name="addElasticsearchDataSource")
    def add_elasticsearch_data_source(
        self,
        id: builtins.str,
        domain: aws_cdk.aws_elasticsearch.IDomain,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> ElasticsearchDataSource:
        '''(experimental) add a new elasticsearch data source to this API.

        :param id: The data source's id.
        :param domain: The elasticsearch domain for this data source.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = DataSourceOptions(description=description, name=name)

        return typing.cast(ElasticsearchDataSource, jsii.invoke(self, "addElasticsearchDataSource", [id, domain, options]))

    @jsii.member(jsii_name="addHttpDataSource")
    def add_http_data_source(
        self,
        id: builtins.str,
        endpoint: builtins.str,
        *,
        authorization_config: typing.Optional[AwsIamConfig] = None,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "HttpDataSource":
        '''(experimental) add a new http data source to this API.

        :param id: The data source's id.
        :param endpoint: The http endpoint.
        :param authorization_config: (experimental) The authorization config in case the HTTP endpoint requires authorization. Default: - none
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = HttpDataSourceOptions(
            authorization_config=authorization_config,
            description=description,
            name=name,
        )

        return typing.cast("HttpDataSource", jsii.invoke(self, "addHttpDataSource", [id, endpoint, options]))

    @jsii.member(jsii_name="addLambdaDataSource")
    def add_lambda_data_source(
        self,
        id: builtins.str,
        lambda_function: aws_cdk.aws_lambda.IFunction,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "LambdaDataSource":
        '''(experimental) add a new Lambda data source to this API.

        :param id: The data source's id.
        :param lambda_function: The Lambda function to call to interact with this data source.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = DataSourceOptions(description=description, name=name)

        return typing.cast("LambdaDataSource", jsii.invoke(self, "addLambdaDataSource", [id, lambda_function, options]))

    @jsii.member(jsii_name="addNoneDataSource")
    def add_none_data_source(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> NoneDataSource:
        '''(experimental) add a new dummy data source to this API.

        Useful for pipeline resolvers
        and for backend changes that don't require a data source.

        :param id: The data source's id.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = DataSourceOptions(description=description, name=name)

        return typing.cast(NoneDataSource, jsii.invoke(self, "addNoneDataSource", [id, options]))

    @jsii.member(jsii_name="addRdsDataSource")
    def add_rds_data_source(
        self,
        id: builtins.str,
        serverless_cluster: aws_cdk.aws_rds.IServerlessCluster,
        secret_store: aws_cdk.aws_secretsmanager.ISecret,
        database_name: typing.Optional[builtins.str] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> "RdsDataSource":
        '''(experimental) add a new Rds data source to this API.

        :param id: The data source's id.
        :param serverless_cluster: The serverless cluster to interact with this data source.
        :param secret_store: The secret store that contains the username and password for the serverless cluster.
        :param database_name: The optional name of the database to use within the cluster.
        :param description: (experimental) The description of the data source. Default: - No description
        :param name: (experimental) The name of the data source, overrides the id given by cdk. Default: - generated by cdk given the id

        :stability: experimental
        '''
        options = DataSourceOptions(description=description, name=name)

        return typing.cast("RdsDataSource", jsii.invoke(self, "addRdsDataSource", [id, serverless_cluster, secret_store, database_name, options]))

    @jsii.member(jsii_name="addSchemaDependency")
    def add_schema_dependency(self, construct: aws_cdk.CfnResource) -> builtins.bool:
        '''(experimental) Add schema dependency if not imported.

        :param construct: the dependee.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "addSchemaDependency", [construct]))

    @jsii.member(jsii_name="createResolver")
    def create_resolver(
        self,
        *,
        data_source: typing.Optional[BaseDataSource] = None,
        field_name: builtins.str,
        type_name: builtins.str,
        caching_config: typing.Optional[CachingConfig] = None,
        pipeline_config: typing.Optional[typing.Sequence[IAppsyncFunction]] = None,
        request_mapping_template: typing.Optional[MappingTemplate] = None,
        response_mapping_template: typing.Optional[MappingTemplate] = None,
    ) -> Resolver:
        '''(experimental) creates a new resolver for this datasource and API using the given properties.

        :param data_source: (experimental) The data source this resolver is using. Default: - No datasource
        :param field_name: (experimental) name of the GraphQL field in the given type this resolver is attached to.
        :param type_name: (experimental) name of the GraphQL type this resolver is attached to.
        :param caching_config: (experimental) The caching configuration for this resolver. Default: - No caching configuration
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array | undefined sets resolver to be of kind, unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template

        :stability: experimental
        '''
        props = ExtendedResolverProps(
            data_source=data_source,
            field_name=field_name,
            type_name=type_name,
            caching_config=caching_config,
            pipeline_config=pipeline_config,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
        )

        return typing.cast(Resolver, jsii.invoke(self, "createResolver", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    @abc.abstractmethod
    def api_id(self) -> builtins.str:
        '''(experimental) an unique AWS AppSync GraphQL API identifier i.e. 'lxz775lwdrgcndgz3nurvac7oa'.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    @abc.abstractmethod
    def arn(self) -> builtins.str:
        '''(experimental) the ARN of the API.

        :stability: experimental
        '''
        ...


class _GraphqlApiBaseProxy(
    GraphqlApiBase, jsii.proxy_for(aws_cdk.Resource) # type: ignore[misc]
):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''(experimental) an unique AWS AppSync GraphQL API identifier i.e. 'lxz775lwdrgcndgz3nurvac7oa'.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) the ARN of the API.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, GraphqlApiBase).__jsii_proxy_class__ = lambda : _GraphqlApiBaseProxy


@jsii.implements(IField)
class GraphqlType(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.GraphqlType",
):
    '''(experimental) The GraphQL Types in AppSync's GraphQL.

    GraphQL Types are the
    building blocks for object types, queries, mutations, etc. They are
    types like String, Int, Id or even Object Types you create.

    i.e. ``String``, ``String!``, ``[String]``, ``[String!]``, ``[String]!``

    GraphQL Types are used to define the entirety of schema.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        # dummy_request: appsync.MappingTemplate
        # dummy_response: appsync.MappingTemplate
        
        info = appsync.ObjectType("Info",
            definition={
                "node": appsync.ResolvableField(
                    return_type=appsync.GraphqlType.string(),
                    args={
                        "id": appsync.GraphqlType.string()
                    },
                    data_source=api.add_none_data_source("none"),
                    request_mapping_template=dummy_request,
                    response_mapping_template=dummy_response
                )
            }
        )
    '''

    def __init__(
        self,
        type: Type,
        *,
        intermediate_type: typing.Optional[IIntermediateType] = None,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param type: -
        :param intermediate_type: (experimental) the intermediate type linked to this attribute. Default: - no intermediate type
        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = GraphqlTypeOptions(
            intermediate_type=intermediate_type,
            is_list=is_list,
            is_required=is_required,
            is_required_list=is_required_list,
        )

        jsii.create(self.__class__, self, [type, options])

    @jsii.member(jsii_name="awsDate") # type: ignore[misc]
    @builtins.classmethod
    def aws_date(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``AWSDate`` scalar type represents a valid extended ``ISO 8601 Date`` string.

        In other words, accepts date strings in the form of ``YYYY-MM-DD``. It accepts time zone offsets.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "awsDate", [options]))

    @jsii.member(jsii_name="awsDateTime") # type: ignore[misc]
    @builtins.classmethod
    def aws_date_time(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``AWSDateTime`` scalar type represents a valid extended ``ISO 8601 DateTime`` string.

        In other words, accepts date strings in the form of ``YYYY-MM-DDThh:mm:ss.sssZ``. It accepts time zone offsets.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "awsDateTime", [options]))

    @jsii.member(jsii_name="awsEmail") # type: ignore[misc]
    @builtins.classmethod
    def aws_email(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``AWSEmail`` scalar type represents an email address string (i.e.``username@example.com``).

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "awsEmail", [options]))

    @jsii.member(jsii_name="awsIpAddress") # type: ignore[misc]
    @builtins.classmethod
    def aws_ip_address(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``AWSIPAddress`` scalar type respresents a valid ``IPv4`` of ``IPv6`` address string.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "awsIpAddress", [options]))

    @jsii.member(jsii_name="awsJson") # type: ignore[misc]
    @builtins.classmethod
    def aws_json(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``AWSJson`` scalar type represents a JSON string.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "awsJson", [options]))

    @jsii.member(jsii_name="awsPhone") # type: ignore[misc]
    @builtins.classmethod
    def aws_phone(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``AWSPhone`` scalar type represents a valid phone number. Phone numbers maybe be whitespace delimited or hyphenated.

        The number can specify a country code at the beginning, but is not required for US phone numbers.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "awsPhone", [options]))

    @jsii.member(jsii_name="awsTime") # type: ignore[misc]
    @builtins.classmethod
    def aws_time(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``AWSTime`` scalar type represents a valid extended ``ISO 8601 Time`` string.

        In other words, accepts date strings in the form of ``hh:mm:ss.sss``. It accepts time zone offsets.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "awsTime", [options]))

    @jsii.member(jsii_name="awsTimestamp") # type: ignore[misc]
    @builtins.classmethod
    def aws_timestamp(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``AWSTimestamp`` scalar type represents the number of seconds since ``1970-01-01T00:00Z``.

        Timestamps are serialized and deserialized as numbers.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "awsTimestamp", [options]))

    @jsii.member(jsii_name="awsUrl") # type: ignore[misc]
    @builtins.classmethod
    def aws_url(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``AWSURL`` scalar type represetns a valid URL string.

        URLs wihtout schemes or contain double slashes are considered invalid.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "awsUrl", [options]))

    @jsii.member(jsii_name="boolean") # type: ignore[misc]
    @builtins.classmethod
    def boolean(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``Boolean`` scalar type is a boolean value: true or false.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "boolean", [options]))

    @jsii.member(jsii_name="float") # type: ignore[misc]
    @builtins.classmethod
    def float(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``Float`` scalar type is a signed double-precision fractional value.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "float", [options]))

    @jsii.member(jsii_name="id") # type: ignore[misc]
    @builtins.classmethod
    def id(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``ID`` scalar type is a unique identifier. ``ID`` type is serialized similar to ``String``.

        Often used as a key for a cache and not intended to be human-readable.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "id", [options]))

    @jsii.member(jsii_name="int") # type: ignore[misc]
    @builtins.classmethod
    def int(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``Int`` scalar type is a signed non-fractional numerical value.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "int", [options]))

    @jsii.member(jsii_name="intermediate") # type: ignore[misc]
    @builtins.classmethod
    def intermediate(
        cls,
        *,
        intermediate_type: typing.Optional[IIntermediateType] = None,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) an intermediate type to be added as an attribute (i.e. an interface or an object type).

        :param intermediate_type: (experimental) the intermediate type linked to this attribute. Default: - no intermediate type
        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = GraphqlTypeOptions(
            intermediate_type=intermediate_type,
            is_list=is_list,
            is_required=is_required,
            is_required_list=is_required_list,
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "intermediate", [options]))

    @jsii.member(jsii_name="string") # type: ignore[misc]
    @builtins.classmethod
    def string(
        cls,
        *,
        is_list: typing.Optional[builtins.bool] = None,
        is_required: typing.Optional[builtins.bool] = None,
        is_required_list: typing.Optional[builtins.bool] = None,
    ) -> "GraphqlType":
        '''(experimental) ``String`` scalar type is a free-form human-readable text.

        :param is_list: (experimental) property determining if this attribute is a list i.e. if true, attribute would be [Type]. Default: - false
        :param is_required: (experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be Type! Default: - false
        :param is_required_list: (experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be [ Type ]! or if isRequired true, attribe would be [ Type! ]! Default: - false

        :stability: experimental
        '''
        options = BaseTypeOptions(
            is_list=is_list, is_required=is_required, is_required_list=is_required_list
        )

        return typing.cast("GraphqlType", jsii.sinvoke(cls, "string", [options]))

    @jsii.member(jsii_name="argsToString")
    def args_to_string(self) -> builtins.str:
        '''(experimental) Generate the arguments for this field.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "argsToString", []))

    @jsii.member(jsii_name="directivesToString")
    def directives_to_string(
        self,
        _modes: typing.Optional[typing.Sequence[AuthorizationType]] = None,
    ) -> builtins.str:
        '''(experimental) Generate the directives for this field.

        :param _modes: -

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "directivesToString", [_modes]))

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''(experimental) Generate the string for this attribute.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isList")
    def is_list(self) -> builtins.bool:
        '''(experimental) property determining if this attribute is a list i.e. if true, attribute would be ``[Type]``.

        :default: - false

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isList"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isRequired")
    def is_required(self) -> builtins.bool:
        '''(experimental) property determining if this attribute is non-nullable i.e. if true, attribute would be ``Type!`` and this attribute must always have a value.

        :default: - false

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isRequired"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isRequiredList")
    def is_required_list(self) -> builtins.bool:
        '''(experimental) property determining if this attribute is a non-nullable list i.e. if true, attribute would be ``[ Type ]!`` and this attribute's list must always have a value.

        :default: - false

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isRequiredList"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> Type:
        '''(experimental) the type of attribute.

        :stability: experimental
        '''
        return typing.cast(Type, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intermediateType")
    def intermediate_type(self) -> typing.Optional[IIntermediateType]:
        '''(experimental) the intermediate type linked to this attribute (i.e. an interface or an object).

        :default: - no intermediate type

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IIntermediateType], jsii.get(self, "intermediateType"))


class HttpDataSource(
    BackedDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.HttpDataSource",
):
    '''(experimental) An AppSync datasource backed by a http endpoint.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        api = appsync.GraphqlApi(self, "api",
            name="api",
            schema=appsync.Schema.from_asset(path.join(__dirname, "schema.graphql"))
        )
        
        http_ds = api.add_http_data_source("ds", "https://states.amazonaws.com",
            name="httpDsWithStepF",
            description="from appsync to StepFunctions Workflow",
            authorization_config=appsync.AwsIamConfig(
                signing_region="us-east-1",
                signing_service_name="states"
            )
        )
        
        http_ds.create_resolver(
            type_name="Mutation",
            field_name="callStepFunction",
            request_mapping_template=appsync.MappingTemplate.from_file("request.vtl"),
            response_mapping_template=appsync.MappingTemplate.from_file("response.vtl")
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        endpoint: builtins.str,
        authorization_config: typing.Optional[AwsIamConfig] = None,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param endpoint: (experimental) The http endpoint.
        :param authorization_config: (experimental) The authorization config in case the HTTP endpoint requires authorization. Default: - none
        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source

        :stability: experimental
        '''
        props = HttpDataSourceProps(
            endpoint=endpoint,
            authorization_config=authorization_config,
            api=api,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class LambdaDataSource(
    BackedDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.LambdaDataSource",
):
    '''(experimental) An AppSync datasource backed by a Lambda function.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_appsync_alpha as appsync_alpha
        from aws_cdk import aws_iam as iam
        from aws_cdk import aws_lambda as lambda_
        
        # function_: lambda.Function
        # graphql_api: appsync_alpha.GraphqlApi
        # role: iam.Role
        
        lambda_data_source = appsync_alpha.LambdaDataSource(self, "MyLambdaDataSource",
            api=graphql_api,
            lambda_function=function_,
        
            # the properties below are optional
            description="description",
            name="name",
            service_role=role
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        lambda_function: aws_cdk.aws_lambda.IFunction,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param lambda_function: (experimental) The Lambda function to call to interact with this data source.
        :param service_role: (experimental) The IAM service role to be assumed by AppSync to interact with the data source. Default: - Create a new role
        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source

        :stability: experimental
        '''
        props = LambdaDataSourceProps(
            lambda_function=lambda_function,
            service_role=service_role,
            api=api,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.LambdaDataSourceProps",
    jsii_struct_bases=[BackedDataSourceProps],
    name_mapping={
        "api": "api",
        "description": "description",
        "name": "name",
        "service_role": "serviceRole",
        "lambda_function": "lambdaFunction",
    },
)
class LambdaDataSourceProps(BackedDataSourceProps):
    def __init__(
        self,
        *,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        lambda_function: aws_cdk.aws_lambda.IFunction,
    ) -> None:
        '''(experimental) Properties for an AppSync Lambda datasource.

        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source
        :param service_role: (experimental) The IAM service role to be assumed by AppSync to interact with the data source. Default: - Create a new role
        :param lambda_function: (experimental) The Lambda function to call to interact with this data source.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            from aws_cdk import aws_iam as iam
            from aws_cdk import aws_lambda as lambda_
            
            # function_: lambda.Function
            # graphql_api: appsync_alpha.GraphqlApi
            # role: iam.Role
            
            lambda_data_source_props = appsync_alpha.LambdaDataSourceProps(
                api=graphql_api,
                lambda_function=function_,
            
                # the properties below are optional
                description="description",
                name="name",
                service_role=role
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api": api,
            "lambda_function": lambda_function,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if service_role is not None:
            self._values["service_role"] = service_role

    @builtins.property
    def api(self) -> IGraphqlApi:
        '''(experimental) The API to attach this data source to.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(IGraphqlApi, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) the description of the data source.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the data source.

        :default: - id of data source

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM service role to be assumed by AppSync to interact with the data source.

        :default: - Create a new role

        :stability: experimental
        '''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def lambda_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The Lambda function to call to interact with this data source.

        :stability: experimental
        '''
        result = self._values.get("lambda_function")
        assert result is not None, "Required property 'lambda_function' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaDataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PartitionKey(
    PrimaryKey,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.PartitionKey",
):
    '''(experimental) Specifies the assignment to the partition key.

    It can be
    enhanced with the assignment of the sort key.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_appsync_alpha as appsync_alpha
        
        # assign: appsync_alpha.Assign
        
        partition_key = appsync_alpha.PartitionKey(assign)
    '''

    def __init__(self, pkey: Assign) -> None:
        '''
        :param pkey: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [pkey])

    @jsii.member(jsii_name="sort")
    def sort(self, key: builtins.str) -> SortKeyStep:
        '''(experimental) Allows assigning a value to the sort key.

        :param key: -

        :stability: experimental
        '''
        return typing.cast(SortKeyStep, jsii.invoke(self, "sort", [key]))


class RdsDataSource(
    BackedDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.RdsDataSource",
):
    '''(experimental) An AppSync datasource backed by RDS.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Build a data source for AppSync to access the database.
        # api: appsync.GraphqlApi
        # Create username and password secret for DB Cluster
        secret = rds.DatabaseSecret(self, "AuroraSecret",
            username="clusteradmin"
        )
        
        # The VPC to place the cluster in
        vpc = ec2.Vpc(self, "AuroraVpc")
        
        # Create the serverless cluster, provide all values needed to customise the database.
        cluster = rds.ServerlessCluster(self, "AuroraCluster",
            engine=rds.DatabaseClusterEngine.AURORA_MYSQL,
            vpc=vpc,
            credentials={"username": "clusteradmin"},
            cluster_identifier="db-endpoint-test",
            default_database_name="demos"
        )
        rds_dS = api.add_rds_data_source("rds", cluster, secret, "demos")
        
        # Set up a resolver for an RDS query.
        rds_dS.create_resolver(
            type_name="Query",
            field_name="getDemosRds",
            request_mapping_template=appsync.MappingTemplate.from_string("""
                  {
                    "version": "2018-05-29",
                    "statements": [
                      "SELECT * FROM demos"
                    ]
                  }
                  """),
            response_mapping_template=appsync.MappingTemplate.from_string("""
                    $utils.toJson($utils.rds.toJsonObject($ctx.result)[0])
                  """)
        )
        
        # Set up a resolver for an RDS mutation.
        rds_dS.create_resolver(
            type_name="Mutation",
            field_name="addDemoRds",
            request_mapping_template=appsync.MappingTemplate.from_string("""
                  {
                    "version": "2018-05-29",
                    "statements": [
                      "INSERT INTO demos VALUES (:id, :version)",
                      "SELECT * WHERE id = :id"
                    ],
                    "variableMap": {
                      ":id": $util.toJson($util.autoId()),
                      ":version": $util.toJson($ctx.args.version)
                    }
                  }
                  """),
            response_mapping_template=appsync.MappingTemplate.from_string("""
                    $utils.toJson($utils.rds.toJsonObject($ctx.result)[1][0])
                  """)
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        secret_store: aws_cdk.aws_secretsmanager.ISecret,
        serverless_cluster: aws_cdk.aws_rds.IServerlessCluster,
        database_name: typing.Optional[builtins.str] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param secret_store: (experimental) The secret containing the credentials for the database.
        :param serverless_cluster: (experimental) The serverless cluster to call to interact with this data source.
        :param database_name: (experimental) The name of the database to use within the cluster. Default: - None
        :param service_role: (experimental) The IAM service role to be assumed by AppSync to interact with the data source. Default: - Create a new role
        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source

        :stability: experimental
        '''
        props = RdsDataSourceProps(
            secret_store=secret_store,
            serverless_cluster=serverless_cluster,
            database_name=database_name,
            service_role=service_role,
            api=api,
            description=description,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-appsync-alpha.RdsDataSourceProps",
    jsii_struct_bases=[BackedDataSourceProps],
    name_mapping={
        "api": "api",
        "description": "description",
        "name": "name",
        "service_role": "serviceRole",
        "secret_store": "secretStore",
        "serverless_cluster": "serverlessCluster",
        "database_name": "databaseName",
    },
)
class RdsDataSourceProps(BackedDataSourceProps):
    def __init__(
        self,
        *,
        api: IGraphqlApi,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        service_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        secret_store: aws_cdk.aws_secretsmanager.ISecret,
        serverless_cluster: aws_cdk.aws_rds.IServerlessCluster,
        database_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for an AppSync RDS datasource.

        :param api: (experimental) The API to attach this data source to.
        :param description: (experimental) the description of the data source. Default: - None
        :param name: (experimental) The name of the data source. Default: - id of data source
        :param service_role: (experimental) The IAM service role to be assumed by AppSync to interact with the data source. Default: - Create a new role
        :param secret_store: (experimental) The secret containing the credentials for the database.
        :param serverless_cluster: (experimental) The serverless cluster to call to interact with this data source.
        :param database_name: (experimental) The name of the database to use within the cluster. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_appsync_alpha as appsync_alpha
            from aws_cdk import aws_iam as iam
            from aws_cdk import aws_rds as rds
            from aws_cdk import aws_secretsmanager as secretsmanager
            
            # graphql_api: appsync_alpha.GraphqlApi
            # role: iam.Role
            # secret: secretsmanager.Secret
            # serverless_cluster: rds.ServerlessCluster
            
            rds_data_source_props = appsync_alpha.RdsDataSourceProps(
                api=graphql_api,
                secret_store=secret,
                serverless_cluster=serverless_cluster,
            
                # the properties below are optional
                database_name="databaseName",
                description="description",
                name="name",
                service_role=role
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api": api,
            "secret_store": secret_store,
            "serverless_cluster": serverless_cluster,
        }
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if service_role is not None:
            self._values["service_role"] = service_role
        if database_name is not None:
            self._values["database_name"] = database_name

    @builtins.property
    def api(self) -> IGraphqlApi:
        '''(experimental) The API to attach this data source to.

        :stability: experimental
        '''
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(IGraphqlApi, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) the description of the data source.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the data source.

        :default: - id of data source

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM service role to be assumed by AppSync to interact with the data source.

        :default: - Create a new role

        :stability: experimental
        '''
        result = self._values.get("service_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def secret_store(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''(experimental) The secret containing the credentials for the database.

        :stability: experimental
        '''
        result = self._values.get("secret_store")
        assert result is not None, "Required property 'secret_store' is missing"
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, result)

    @builtins.property
    def serverless_cluster(self) -> aws_cdk.aws_rds.IServerlessCluster:
        '''(experimental) The serverless cluster to call to interact with this data source.

        :stability: experimental
        '''
        result = self._values.get("serverless_cluster")
        assert result is not None, "Required property 'serverless_cluster' is missing"
        return typing.cast(aws_cdk.aws_rds.IServerlessCluster, result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the database to use within the cluster.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsDataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IField)
class Field(
    GraphqlType,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.Field",
):
    '''(experimental) Fields build upon Graphql Types and provide typing and arguments.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        field = appsync.Field(
            return_type=appsync.GraphqlType.string(),
            args={
                "argument": appsync.GraphqlType.string()
            }
        )
        type = appsync.InterfaceType("Node",
            definition={"test": field}
        )
    '''

    def __init__(
        self,
        *,
        return_type: GraphqlType,
        args: typing.Optional[typing.Mapping[builtins.str, GraphqlType]] = None,
        directives: typing.Optional[typing.Sequence[Directive]] = None,
    ) -> None:
        '''
        :param return_type: (experimental) The return type for this field.
        :param args: (experimental) The arguments for this field. i.e. type Example (first: String second: String) {} - where 'first' and 'second' are key values for args and 'String' is the GraphqlType Default: - no arguments
        :param directives: (experimental) the directives for this field. Default: - no directives

        :stability: experimental
        '''
        options = FieldOptions(
            return_type=return_type, args=args, directives=directives
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="argsToString")
    def args_to_string(self) -> builtins.str:
        '''(experimental) Generate the args string of this resolvable field.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "argsToString", []))

    @jsii.member(jsii_name="directivesToString")
    def directives_to_string(
        self,
        modes: typing.Optional[typing.Sequence[AuthorizationType]] = None,
    ) -> builtins.str:
        '''(experimental) Generate the directives for this field.

        :param modes: -

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "directivesToString", [modes]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldOptions")
    def field_options(self) -> typing.Optional[ResolvableFieldOptions]:
        '''(experimental) The options for this field.

        :default: - no arguments

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ResolvableFieldOptions], jsii.get(self, "fieldOptions"))


class GraphqlApi(
    GraphqlApiBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.GraphqlApi",
):
    '''(experimental) An AppSync GraphQL API.

    :stability: experimental
    :exampleMetadata: infused
    :resource: AWS::AppSync::GraphQLApi

    Example::

        api = appsync.GraphqlApi(self, "Api",
            name="demo"
        )
        demo = appsync.ObjectType("Demo",
            definition={
                "id": appsync.GraphqlType.string(is_required=True),
                "version": appsync.GraphqlType.string(is_required=True)
            }
        )
        
        api.add_type(demo)
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        authorization_config: typing.Optional[AuthorizationConfig] = None,
        log_config: typing.Optional[LogConfig] = None,
        schema: typing.Optional[Schema] = None,
        xray_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param name: (experimental) the name of the GraphQL API.
        :param authorization_config: (experimental) Optional authorization configuration. Default: - API Key authorization
        :param log_config: (experimental) Logging configuration for this api. Default: - None
        :param schema: (experimental) GraphQL schema definition. Specify how you want to define your schema. Schema.fromFile(filePath: string) allows schema definition through schema.graphql file Default: - schema will be generated code-first (i.e. addType, addObjectType, etc.)
        :param xray_enabled: (experimental) A flag indicating whether or not X-Ray tracing is enabled for the GraphQL API. Default: - false

        :stability: experimental
        '''
        props = GraphqlApiProps(
            name=name,
            authorization_config=authorization_config,
            log_config=log_config,
            schema=schema,
            xray_enabled=xray_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromGraphqlApiAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_graphql_api_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        graphql_api_id: builtins.str,
        graphql_api_arn: typing.Optional[builtins.str] = None,
    ) -> IGraphqlApi:
        '''(experimental) Import a GraphQL API through this function.

        :param scope: scope.
        :param id: id.
        :param graphql_api_id: (experimental) an unique AWS AppSync GraphQL API identifier i.e. 'lxz775lwdrgcndgz3nurvac7oa'.
        :param graphql_api_arn: (experimental) the arn for the GraphQL Api. Default: - autogenerated arn

        :stability: experimental
        '''
        attrs = GraphqlApiAttributes(
            graphql_api_id=graphql_api_id, graphql_api_arn=graphql_api_arn
        )

        return typing.cast(IGraphqlApi, jsii.sinvoke(cls, "fromGraphqlApiAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addMutation")
    def add_mutation(
        self,
        field_name: builtins.str,
        field: "ResolvableField",
    ) -> ObjectType:
        '''(experimental) Add a mutation field to the schema's Mutation. CDK will create an Object Type called 'Mutation'. For example,.

        type Mutation {
        fieldName: Field.returnType
        }

        :param field_name: the name of the Mutation.
        :param field: the resolvable field to for this Mutation.

        :stability: experimental
        '''
        return typing.cast(ObjectType, jsii.invoke(self, "addMutation", [field_name, field]))

    @jsii.member(jsii_name="addQuery")
    def add_query(
        self,
        field_name: builtins.str,
        field: "ResolvableField",
    ) -> ObjectType:
        '''(experimental) Add a query field to the schema's Query. CDK will create an Object Type called 'Query'. For example,.

        type Query {
        fieldName: Field.returnType
        }

        :param field_name: the name of the query.
        :param field: the resolvable field to for this query.

        :stability: experimental
        '''
        return typing.cast(ObjectType, jsii.invoke(self, "addQuery", [field_name, field]))

    @jsii.member(jsii_name="addSchemaDependency")
    def add_schema_dependency(self, construct: aws_cdk.CfnResource) -> builtins.bool:
        '''(experimental) Add schema dependency to a given construct.

        :param construct: the dependee.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "addSchemaDependency", [construct]))

    @jsii.member(jsii_name="addSubscription")
    def add_subscription(
        self,
        field_name: builtins.str,
        field: "ResolvableField",
    ) -> ObjectType:
        '''(experimental) Add a subscription field to the schema's Subscription. CDK will create an Object Type called 'Subscription'. For example,.

        type Subscription {
        fieldName: Field.returnType
        }

        :param field_name: the name of the Subscription.
        :param field: the resolvable field to for this Subscription.

        :stability: experimental
        '''
        return typing.cast(ObjectType, jsii.invoke(self, "addSubscription", [field_name, field]))

    @jsii.member(jsii_name="addToSchema")
    def add_to_schema(
        self,
        addition: builtins.str,
        delimiter: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Escape hatch to append to Schema as desired.

        Will always result
        in a newline.

        :param addition: the addition to add to schema.
        :param delimiter: the delimiter between schema and addition.

        :default: - ''

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addToSchema", [addition, delimiter]))

    @jsii.member(jsii_name="addType")
    def add_type(self, type: IIntermediateType) -> IIntermediateType:
        '''(experimental) Add type to the schema.

        :param type: the intermediate type to add to the schema.

        :stability: experimental
        '''
        return typing.cast(IIntermediateType, jsii.invoke(self, "addType", [type]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        resources: IamResource,
        *actions: builtins.str,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Adds an IAM policy statement associated with this GraphQLApi to an IAM principal's policy.

        :param grantee: The principal.
        :param resources: The set of resources to allow (i.e. ...:[region]:[accountId]:apis/GraphQLId/...).
        :param actions: The actions that should be granted to the principal (i.e. appsync:graphql ).

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grant", [grantee, resources, *actions]))

    @jsii.member(jsii_name="grantMutation")
    def grant_mutation(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        *fields: builtins.str,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Adds an IAM policy statement for Mutation access to this GraphQLApi to an IAM principal's policy.

        :param grantee: The principal.
        :param fields: The fields to grant access to that are Mutations (leave blank for all).

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantMutation", [grantee, *fields]))

    @jsii.member(jsii_name="grantQuery")
    def grant_query(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        *fields: builtins.str,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Adds an IAM policy statement for Query access to this GraphQLApi to an IAM principal's policy.

        :param grantee: The principal.
        :param fields: The fields to grant access to that are Queries (leave blank for all).

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantQuery", [grantee, *fields]))

    @jsii.member(jsii_name="grantSubscription")
    def grant_subscription(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        *fields: builtins.str,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Adds an IAM policy statement for Subscription access to this GraphQLApi to an IAM principal's policy.

        :param grantee: The principal.
        :param fields: The fields to grant access to that are Subscriptions (leave blank for all).

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantSubscription", [grantee, *fields]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiId")
    def api_id(self) -> builtins.str:
        '''(experimental) an unique AWS AppSync GraphQL API identifier i.e. 'lxz775lwdrgcndgz3nurvac7oa'.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "apiId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) the ARN of the API.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="graphqlUrl")
    def graphql_url(self) -> builtins.str:
        '''(experimental) the URL of the endpoint created by AppSync.

        :stability: experimental
        :attribute: GraphQlUrl
        '''
        return typing.cast(builtins.str, jsii.get(self, "graphqlUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modes")
    def modes(self) -> typing.List[AuthorizationType]:
        '''(experimental) The Authorization Types for this GraphQL Api.

        :stability: experimental
        '''
        return typing.cast(typing.List[AuthorizationType], jsii.get(self, "modes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) the name of the API.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schema")
    def schema(self) -> Schema:
        '''(experimental) the schema attached to this api.

        :stability: experimental
        '''
        return typing.cast(Schema, jsii.get(self, "schema"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> typing.Optional[builtins.str]:
        '''(experimental) the configured API key, if present.

        :default: - no api key

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKey"))


@jsii.implements(IField)
class ResolvableField(
    Field,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-appsync-alpha.ResolvableField",
):
    '''(experimental) Resolvable Fields build upon Graphql Types and provide fields that can resolve into operations on a data source.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # api: appsync.GraphqlApi
        # dummy_request: appsync.MappingTemplate
        # dummy_response: appsync.MappingTemplate
        
        info = appsync.ObjectType("Info",
            definition={
                "node": appsync.ResolvableField(
                    return_type=appsync.GraphqlType.string(),
                    args={
                        "id": appsync.GraphqlType.string()
                    },
                    data_source=api.add_none_data_source("none"),
                    request_mapping_template=dummy_request,
                    response_mapping_template=dummy_response
                )
            }
        )
    '''

    def __init__(
        self,
        *,
        data_source: typing.Optional[BaseDataSource] = None,
        pipeline_config: typing.Optional[typing.Sequence[IAppsyncFunction]] = None,
        request_mapping_template: typing.Optional[MappingTemplate] = None,
        response_mapping_template: typing.Optional[MappingTemplate] = None,
        return_type: GraphqlType,
        args: typing.Optional[typing.Mapping[builtins.str, GraphqlType]] = None,
        directives: typing.Optional[typing.Sequence[Directive]] = None,
    ) -> None:
        '''
        :param data_source: (experimental) The data source creating linked to this resolvable field. Default: - no data source
        :param pipeline_config: (experimental) configuration of the pipeline resolver. Default: - no pipeline resolver configuration An empty array or undefined prop will set resolver to be of type unit
        :param request_mapping_template: (experimental) The request mapping template for this resolver. Default: - No mapping template
        :param response_mapping_template: (experimental) The response mapping template for this resolver. Default: - No mapping template
        :param return_type: (experimental) The return type for this field.
        :param args: (experimental) The arguments for this field. i.e. type Example (first: String second: String) {} - where 'first' and 'second' are key values for args and 'String' is the GraphqlType Default: - no arguments
        :param directives: (experimental) the directives for this field. Default: - no directives

        :stability: experimental
        '''
        options = ResolvableFieldOptions(
            data_source=data_source,
            pipeline_config=pipeline_config,
            request_mapping_template=request_mapping_template,
            response_mapping_template=response_mapping_template,
            return_type=return_type,
            args=args,
            directives=directives,
        )

        jsii.create(self.__class__, self, [options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fieldOptions")
    def field_options(self) -> typing.Optional[ResolvableFieldOptions]:
        '''(experimental) The options to make this field resolvable.

        :default: - not a resolvable field

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ResolvableFieldOptions], jsii.get(self, "fieldOptions"))


__all__ = [
    "AddFieldOptions",
    "ApiKeyConfig",
    "AppsyncFunction",
    "AppsyncFunctionAttributes",
    "AppsyncFunctionProps",
    "Assign",
    "AttributeValues",
    "AttributeValuesStep",
    "AuthorizationConfig",
    "AuthorizationMode",
    "AuthorizationType",
    "AwsIamConfig",
    "BackedDataSource",
    "BackedDataSourceProps",
    "BaseAppsyncFunctionProps",
    "BaseDataSource",
    "BaseDataSourceProps",
    "BaseResolverProps",
    "BaseTypeOptions",
    "CachingConfig",
    "DataSourceOptions",
    "Directive",
    "DynamoDbDataSource",
    "DynamoDbDataSourceProps",
    "ElasticsearchDataSource",
    "ElasticsearchDataSourceProps",
    "EnumType",
    "EnumTypeOptions",
    "ExtendedDataSourceProps",
    "ExtendedResolverProps",
    "Field",
    "FieldLogLevel",
    "FieldOptions",
    "GraphqlApi",
    "GraphqlApiAttributes",
    "GraphqlApiBase",
    "GraphqlApiProps",
    "GraphqlType",
    "GraphqlTypeOptions",
    "HttpDataSource",
    "HttpDataSourceOptions",
    "HttpDataSourceProps",
    "IAppsyncFunction",
    "IField",
    "IGraphqlApi",
    "IIntermediateType",
    "IamResource",
    "InputType",
    "InterfaceType",
    "IntermediateTypeOptions",
    "KeyCondition",
    "LambdaAuthorizerConfig",
    "LambdaDataSource",
    "LambdaDataSourceProps",
    "LogConfig",
    "MappingTemplate",
    "NoneDataSource",
    "NoneDataSourceProps",
    "ObjectType",
    "ObjectTypeOptions",
    "OpenIdConnectConfig",
    "PartitionKey",
    "PartitionKeyStep",
    "PrimaryKey",
    "RdsDataSource",
    "RdsDataSourceProps",
    "ResolvableField",
    "ResolvableFieldOptions",
    "Resolver",
    "ResolverProps",
    "Schema",
    "SchemaOptions",
    "SortKeyStep",
    "Type",
    "UnionType",
    "UnionTypeOptions",
    "UserPoolConfig",
    "UserPoolDefaultAction",
    "Values",
]

publication.publish()
