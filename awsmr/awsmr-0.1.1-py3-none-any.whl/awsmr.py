import sys

import awscli.clidriver
from awscli.clidriver import CLIDriver, CLIOperationCaller
from awscli.formatter import (
    FullyBufferedFormatter,
    JSONFormatter,
    TableFormatter,
    TextFormatter,
    is_response_paginated,
)
from botocore.compat import OrderedDict

from multiregion import multiregion, response_or_exception


def multi_region_invoke(self, service_name, operation_name, parameters, parsed_globals):
    mr = multiregion(make_regional_client_call, region_names=parsed_globals.region_list)
    response = mr(self, service_name, operation_name, parameters, parsed_globals)
    self._display_response(operation_name, response, parsed_globals)
    return 0


def make_regional_client_call(
    self, service_name, operation_name, parameters, parsed_globals, *, region_name
):
    client = self._session.create_client(
        service_name,
        region_name=region_name,
        endpoint_url=parsed_globals.endpoint_url,
        verify=parsed_globals.verify_ssl,
    )
    return self._make_client_call(client, operation_name, parameters, parsed_globals)


def multi_region_formatter(format_type, args):
    if format_type == "json":
        return JSONMultiRegionFormatter(args)
    if format_type == "table":
        return TableMultiRegionFormatter(args)
    if format_type == "text":
        return TextMultiRegionFormatter(args)
    raise ValueError("Unknown output type %s" % format_type)


class MultiRegionFormatter(FullyBufferedFormatter):
    def _remove_request_id(self, response_data):
        for region in response_data:
            if "Exception" not in region:
                FullyBufferedFormatter._remove_request_id(self, region["Response"])

    def __call__(self, command_name, response, stream=None):
        def full_result_or_exception(region):
            if "Exception" not in region and is_response_paginated(region["Response"]):
                return {
                    "RegionName": region["RegionName"],
                    **response_or_exception(
                        lambda: region["Response"].build_full_result()
                    ),
                }
            return region

        response = [full_result_or_exception(region) for region in response]

        return FullyBufferedFormatter.__call__(self, command_name, response, stream)


class JSONMultiRegionFormatter(JSONFormatter, MultiRegionFormatter):
    pass


class TableMultiRegionFormatter(TableFormatter, MultiRegionFormatter):
    pass


class TextMultiRegionFormatter(TextFormatter, MultiRegionFormatter):
    def __init__(*args, **kwargs):
        raise NotImplemented("TextFormatter is not fully buffered")


def patch_get_cli_data(original):

    cli_data = None

    def _get_cli_data(self):
        nonlocal cli_data
        if cli_data is None:
            cli_data = original(self)
            cli_data["options"]["region-list"] = OrderedDict(
                [
                    ("type", "list"),
                    ("required", "True"),
                    (
                        "help",
                        "<p>The list of regions to use.  Overrides config/env settings.</p>",
                    ),
                ]
            )
        return cli_data

    return _get_cli_data


def main():
    CLIDriver._get_cli_data = patch_get_cli_data(CLIDriver._get_cli_data)
    CLIOperationCaller.invoke = multi_region_invoke
    awscli.clidriver.get_formatter = multi_region_formatter
    driver = awscli.clidriver.create_clidriver()
    sys.exit(driver.main())


if __name__ == "__main__":
    main()
