from typing import List

import typer
import asyncio

cli = typer.Typer()


# @cli.command()
# def install():
#     print("Not implemented")
#
#
# @cli.command()
# def seed():
#     print("Not implemented")

@cli.command()
def export_code_docs():
    """Script to export the microservice code as HTML docs. Exports to /docs"""
    from pathlib import Path

    from ehelply_bootstrapper.utils.docs import export_code_docs as lib_export_code_docs

    from ehelply_microservice_library.cli.cli_state import CLIState

    class DocsService(CLIState.service):
        def if_dev_launch_dev_server(self) -> bool:
            return False

        def after_fast_api(self):
            asyncio.run(super().startup_event())

        def is_load_service_routers(self) -> bool:
            return False

    service = DocsService()

    lib_export_code_docs(
        root_path=Path(service.get_service_package_path()).resolve(),
        modules=["src"]
    )


@cli.command()
def export_api_docs(
    include_service_routers: bool = typer.Option(False, help="Include service routers in the docs"),
    include_ehelply_header: bool = typer.Option(True, help="Include eHelply header on the docs page"),
):
    """Script to export the ReDoc documentation page into a standalone HTML file. Exports to /api-docs"""

    with typer.progressbar(length=8, label="Exporting") as progress:

        typer.echo("Starting doc exports. Expect to see lots of bootstrap text in the log")

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

        service = DocsService()

        progress.update(3)

        if service.fastapi_driver:
            app = service.fastapi_driver.instance

            required_integrations: str = ""
            for integration in service.get_service_required_integrations():
                integration_name = integration.replace("-", " ").capitalize().replace("Ehelply", "eHelply")
                required_integrations += '<li><a href="https://github.com/eHelply/{integration}">{integration_name}</a></li>'.format(integration=integration, integration_name=integration_name)
                
            optional_integrations: str = ""
            for integration in service.get_service_optional_integrations():
                integration_name = integration.replace("-", " ").capitalize().replace("Ehelply", "eHelply")
                optional_integrations += '<li><a href="https://github.com/eHelply/{integration}">{integration_name}</a></li>'.format(integration=integration, integration_name=integration_name)

            if include_ehelply_header:
                HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>{service_name} {service_version} - Docs</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="{ehelply_logo_url}">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
    <style data-styled="" data-styled-version="4.4.1"></style>
</head>
<body>

    <div style='padding:25px;'>

        <h3>eHelply Microservice Documentation</h3>
        <a href="https://github.com/eHelply/docs-ehelply-microservices">Documentation Repository</a>

        <h4>{service_name} - {service_version}</h4>
        <a href="https://github.com/eHelply/docs-ehelply-microservices/{service_key}">{service_name} Documentation Revisions</a>

        <h5>Required Integrations</h5>
        <ul>
        {required_integrations}
        </ul>
        
        <h5>Optional Integrations</h5>
        <ul>
        {optional_integrations}
        </ul>
    </div>

    <hr>

    <div id="redoc-container"></div>
    <script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"> </script>
    <script>
        var spec = %s;
        Redoc.init(spec, {{}}, document.getElementById("redoc-container"));
    </script>
</body>
</html>
                """.format(
                    service_name=service.service_meta.name,
                    service_key=service.service_meta.key,
                    service_version=service.service_meta.version,
                    required_integrations=required_integrations,
                    optional_integrations=optional_integrations,
                    ehelply_logo_url="https://assets.ehelply.com/logo/ehelply/base/symbol_transparent_white.png",
                )

            else:
                HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>{service_name} {service_version} - Docs</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="{ehelply_logo_url}">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
    <style data-styled="" data-styled-version="4.4.1"></style>
</head>
<body>
    <div id="redoc-container"></div>
    <script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"> </script>
    <script>
        var spec = %s;
        Redoc.init(spec, {{}}, document.getElementById("redoc-container"));
    </script>
</body>
</html>
                """.format(
                    service_name=service.service_meta.name,
                    service_version=service.service_meta.version,
                    ehelply_logo_url="https://assets.ehelply.com/logo/ehelply/base/symbol_transparent_white.png",
                )

            docs_file: str = datetime.utcnow().strftime(
                "api-docs_" + service.service_meta.version + "_%Y%m%d-%H%M%S-utc.html")

            docs_location = Path(service.get_service_package_path()).resolve().joinpath('api-docs')
            docs_location.mkdir(exist_ok=True)

            progress.update(1)

            with open(docs_location.joinpath(docs_file), "w") as fd:
                print(HTML_TEMPLATE % json.dumps(app.openapi()), file=fd)

            progress.update(3)

        typer.echo("Doc export complete. Please check the api-docs folder.")

        sys.exit()


@cli.command()
def export_api_spec(
    include_service_routers: bool = typer.Option(False, help="Include service routers in the spec"),
):
    """Script to export Open API JSON spec to a file. Exports to /api-specs"""

    with typer.progressbar(length=8, label="Exporting") as progress:
        typer.echo("Starting spec export. Expect to see lots of bootstrap text in the log")

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

        service = DocsService()

        progress.update(2)

        if service.fastapi_driver:
            app = service.fastapi_driver.instance

            docs_file: str = datetime.utcnow().strftime(
                "api-spec_" + service.service_meta.version + "_%Y%m%d-%H%M%S-utc.json")

            latest_docs_file: str = "latest.json"

            docs_location = Path(service.get_service_package_path()).resolve().joinpath('api-specs')
            docs_location.mkdir(exist_ok=True)

            progress.update(1)

            data: dict = app.openapi()

            progress.update(3)

            with open(docs_location.joinpath(docs_file), "w") as fd:
                json.dump(data, fd)

            with open(docs_location.joinpath(latest_docs_file), "w") as fd:
                json.dump(data, fd)

            progress.update(1)

        typer.echo("Doc export complete. Please check the api-specs folder.")

        sys.exit()


if __name__ == '__main__':
    cli()
