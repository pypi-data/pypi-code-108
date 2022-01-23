from typing import List, Dict
from ehelply_bootstrapper.utils.state import State

import typer
import asyncio

cli = typer.Typer()

"""
CONSTANTS
"""
RESERVED_WORDS: List[str] = ["playground", "test", "testing", "privileged"]
EHELPLY_HEADERS: str = "ehelply-active-participant,ehelply-project,ehelply-data,sentry-trace"
WEB_ACL_ARN: str = "arn:aws:wafv2:ca-central-1:330779307994:regional/webacl/ehelply-test/5d87bb76-a08c-4136-a875-f6f5f89e4dd2"


@cli.command()
def sync_api_gateway(
        include_service_routers: bool = typer.Option(False, help="Include service routers in the spec"),
        ignore_prefixes: int = typer.Option(1,
                                            help="How many prefixes in the path to ignore. Typically you will want to set this to 1 (and it is 1 by default) unless you are syncing a service with multiple root routers. In that case, set this to 0."),
        target_group_port: str = typer.Option(
            ..., prompt=True
        ),
):
    """Script to export Open API JSON spec to a file. Exports to /api-specs"""

    typer.echo()
    typer.echo("=========================================")
    typer.echo(" CONFIRM PARAMETERS:")
    typer.echo(f" Target Group Port: {target_group_port}")
    typer.echo(f" Ignore Prefixes: {ignore_prefixes}")
    typer.echo()
    typer.echo(
        " API Gateway Sync'ing is a destructive process. Your ENTIRE API Gateway API will be overwritten while doing this. Please ensure that you intend to do this.")
    typer.echo()
    typer.echo(
        " Quick explanation of 'ignore_prefixes': How many prefixes in the path to ignore. Typically you will want to set this to 1 (and it is 1 by default) unless you are syncing a service with multiple root routers. In that case, set this to 0.")
    typer.echo("=========================================")
    typer.echo()

    confirm = typer.confirm("Are you sure you want to continue with these parameters?")
    if not confirm:
        raise typer.Abort()

    with typer.progressbar(length=8, label="Syncing") as progress:
        typer.echo("Starting API Gateway Sync. Expect to see lots of bootstrap text in the log")

        import json

        import sys

        from pathlib import Path

        from datetime import datetime

        from ehelply_microservice_library.cli.cli_state import CLIState

        class DocsService(CLIState.service):
            def if_dev_launch_dev_server(self) -> bool:
                return False

            def after_fast_api(self):
                asyncio.run(super().startup_event())

            def is_load_service_routers(self) -> bool:
                return include_service_routers

        progress.update(1)
        typer.echo()

        service = DocsService()

        typer.echo()
        progress.update(2)
        typer.echo()

        if service.fastapi_driver:
            app = service.fastapi_driver.instance

            service_meta = service.service_meta
            api_spec: dict = app.openapi()

            # Remove "eHelply" from the name.
            temp_name = service_meta.name.split(" ")
            temp_name.remove("eHelply")

            api_name: str = "".join(temp_name) + " (AutoGen)"

            apigateway_client = State.aws.make_client(name='apigateway')

            apigateway: dict = None

            # Get API Gateway if it exists
            for apigateway_api in apigateway_client.get_rest_apis(limit=500)['items']:
                if api_name == apigateway_api['name']:
                    apigateway = apigateway_api

            typer.echo()

            # Make a new API in API Gateway if it doesn't exist
            if not apigateway:
                typer.echo("Didn't find an existing API. Creating a new API")
                apigateway = apigateway_client.create_rest_api(
                    name=api_name,
                    description=service_meta.summary,
                    endpointConfiguration={
                        "types": ["REGIONAL"]
                    },
                    disableExecuteApiEndpoint=True
                )
            else:
                typer.echo("Found existing API.")

            typer.echo()
            progress.update(1)
            typer.echo()

            api_id: str = apigateway['id']

            root_resource_id: str = ""

            typer.echo()
            typer.echo("Nuking old resources.")
            typer.echo()

            # Clear out all resources (and by extension their methods)
            for resource in apigateway_client.get_resources(restApiId=api_id, limit=500)['items']:
                if resource['path'] == "/":
                    root_resource_id = resource['id']
                else:
                    try:
                        apigateway_client.delete_resource(
                            restApiId=api_id,
                            resourceId=resource['id']
                        )
                    except:
                        # Depending on the order that paths are retrieved in, we may delete a parent path before the child paths and that would cause an exception.
                        pass

            progress.update(2)
            typer.echo()

            typer.echo()
            typer.echo("Creating resources, methods, and integrations.")
            typer.echo()
            typer.echo("Reserved keywords: " + str(RESERVED_WORDS))
            typer.echo("Any endpoint with a reserved keyword inside of the path will be IGNORED.")
            typer.echo()
            typer.echo("Please wait...")
            typer.echo()

            # Maps a str path to the AWS API Gateway resource ID
            resources: Dict[str, str] = {}

            def create_resources(path_components: List[str]) -> str:
                """
                Recursive algorithm which builds up paths in API Gateway regardless of the order that the paths come in
                """
                full_path: str = "/".join(path_components)
                if full_path in resources:
                    return resources[full_path]

                if len(path_components) == 1:
                    parent_resource_id: str = root_resource_id
                else:
                    parent_resource_id: str = create_resources(path_components=path_components[0:-1])

                new_resource_id = apigateway_client.create_resource(
                    restApiId=api_id,
                    parentId=parent_resource_id,
                    pathPart=path_components[-1]
                )["id"]

                resources[full_path] = new_resource_id

                return new_resource_id

            for endpoint_path, endpoint_methods in api_spec["paths"].items():

                # Remove prefixed '/'
                full_unaltered_path: str = endpoint_path[1:]

                # Remove prefixed '/' and ignored prefixes
                endpoint_path = endpoint_path[1:]
                if ignore_prefixes > 0:
                    endpoint_path = endpoint_path.split("/")
                    endpoint_path = endpoint_path[ignore_prefixes:]
                    endpoint_path = "/".join(endpoint_path)

                # Ignore paths which contain a reserved word
                ignore: bool = False
                endpoint_path_components: List[str] = endpoint_path.split("/")
                for endpoint_path_component in endpoint_path_components:
                    if endpoint_path_component in RESERVED_WORDS:
                        ignore = True
                        break

                if ignore:
                    continue

                resource_id: str = create_resources(path_components=endpoint_path_components)

                methods: List[str] = ["OPTIONS"]

                # Adds methods from the spec: POST, GET, PUT, DELETE, etc.
                for endpoint_method, endpoint_details in endpoint_methods.items():
                    methods.append(endpoint_method.upper())

                    # Building the dicts for the method and integration, so that path parameters work
                    full_unaltered_path_components: List[str] = full_unaltered_path.split("/")
                    method_request_parameters: Dict[str, str] = {}
                    integration_request_parameters: Dict[str, str] = {}
                    for component in full_unaltered_path_components:
                        if component[0] == "{" and component[-1] == "}":
                            method_request_parameters[f"method.request.path.{component[1:-1]}"] = True
                            integration_request_parameters[
                                f"integration.request.path.{component[1:-1]}"] = f"method.request.path.{component[1:-1]}"

                    apigateway_client.put_method(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod=endpoint_method.upper(),
                        authorizationType="NONE",
                        requestParameters=method_request_parameters
                    )

                    apigateway_client.put_integration(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod=endpoint_method.upper(),
                        type="HTTP_PROXY",
                        integrationHttpMethod=endpoint_method.upper(),
                        uri=f"http://${{stageVariables.lb}}:{target_group_port}/{full_unaltered_path}",
                        requestParameters=integration_request_parameters,
                        connectionType="VPC_LINK",
                        connectionId="${stageVariables.vpc}"
                    )

                    apigateway_client.put_method_response(
                        restApiId=api_id,
                        resourceId=resource_id,
                        httpMethod=endpoint_method.upper(),
                        statusCode="200",
                        responseParameters={
                            'method.response.header.Access-Control-Allow-Origin': False
                        },
                        responseModels={
                            'application/json': 'Empty'
                        }
                    )

                # Sets up CORS by adding the OPTION method
                apigateway_client.put_method(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod="OPTIONS",
                    authorizationType="NONE"
                )

                apigateway_client.put_integration(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod="OPTIONS",
                    type="MOCK",
                    requestTemplates={
                        'application/json': '{"statusCode": 200}'
                    }
                )

                apigateway_client.put_method_response(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod="OPTIONS",
                    statusCode="200",
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Headers': False,
                        'method.response.header.Access-Control-Allow-Origin': False,
                        'method.response.header.Access-Control-Allow-Methods': False
                    },
                    responseModels={
                        'application/json': 'Empty'
                    }
                )

                method_str: str = ""
                for method in methods:
                    if len(method_str) == 0:
                        method_str += f"{method}"
                    else:
                        method_str += f",{method}"

                apigateway_client.put_integration_response(
                    restApiId=api_id,
                    resourceId=resource_id,
                    httpMethod="OPTIONS",
                    statusCode="200",
                    responseParameters={
                        'method.response.header.Access-Control-Allow-Headers': f"'{EHELPLY_HEADERS},Content-Type,X-Amz-Date,Authorization,X-Access-Token,X-Secret-Token,X-Api-Key,X-Amz-Security-Token'",
                        'method.response.header.Access-Control-Allow-Methods': f"'{method_str}'",
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    },
                    responseTemplates={
                        'application/json': ''
                    }
                )

            progress.update(1)
            typer.echo()
            typer.echo()

            typer.echo("Checking for deployment stages")

            # Setting up stages if they do not already exist
            stages: List[str] = []
            for stage in apigateway_client.get_stages(restApiId=api_id)['item']:
                stages.append(stage['stageName'])

            created_test: bool = False

            from time import sleep

            if "test" not in stages:
                typer.echo()
                typer.echo("Creating a deployment stage for the 'test' environment")

                created_test = True

                apigateway_client.create_deployment(
                    restApiId=api_id,
                    stageName="test",
                    stageDescription="Test environment",
                    variables={'lb': 'eHelply-Test-Network-LB-8595beb95bd6a14a.elb.ca-central-1.amazonaws.com',
                               'vpc': 'hcp323'}
                )

                typer.echo()
                typer.echo("Adding WAF integration to the 'test' deployment stage")

                waf_client = State.aws.make_client(name="wafv2")

                waf_client.associate_web_acl(
                    WebACLArn=WEB_ACL_ARN,
                    ResourceArn=f"arn:aws:apigateway:ca-central-1::/restapis/{api_id}/stages/test"
                )

            if "prod" not in stages:
                typer.echo()
                typer.echo("Creating a deployment stage for the 'prod' environment")

                if created_test:
                    typer.echo("Waiting out API throttling... (15s)")
                    sleep(15)

                apigateway_client.create_deployment(
                    restApiId=api_id,
                    stageName="prod",
                    stageDescription="Production environment",
                    variables={'lb': 'eHelply-Prod-Network-LB-913c7576c63aee8d.elb.ca-central-1.amazonaws.com',
                               'vpc': 'pe40zx'}
                )

        typer.echo()
        progress.update(1)
        typer.echo()
        typer.echo()

        typer.echo("API Gateway sync complete.")
        typer.echo()
        typer.echo(
            "If this is your first time using API Gateway sync on this microservice, please remember to add or adjust custom domain name path mapping where needed.")
        typer.echo()
        typer.echo(
            "NOTE: This sync does not automatically deploy your API. This is a safety pre-caution. You will need to login to API Gateway and deploy to whichever deployment stages you desire.")

        sys.exit()

