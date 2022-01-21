from typing import List
from suds import WebFault
from suds.sudsobject import asdict

from .types import BingError, BingErrorDetail


def parse_bing_response(response):
    """Parse Suds object response into a dict"""
    return _recursive_asdict(response)


def _recursive_asdict(d):
    """
    Convert Suds object into serializable format.

    Courtesy of https://stackoverflow.com/a/48928384
    """
    out = {}
    for k, v in asdict(d).items():
        if hasattr(v, '__keylist__'):
            out[k] = _recursive_asdict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(_recursive_asdict(item))
                elif not isinstance(item, list):
                    out[k] = item
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out


def parse_webfault_errors(ex: WebFault) -> BingError:
    """From https://docs.microsoft.com/en-us/advertising/guides/walkthrough-desktop-application-python?view=bingads-13"""

    if not hasattr(ex.fault, "detail"):
        raise Exception("Unknown WebFault")

    error_attribute_sets = (
        ["ApiFault", "OperationErrors", "OperationError"],
        ["AdApiFaultDetail", "Errors", "AdApiError"],
        ["ApiFaultDetail", "BatchErrors", "BatchError"],
        ["ApiFaultDetail", "OperationErrors", "OperationError"],
        ["EditorialApiFaultDetail", "BatchErrors", "BatchError"],
        ["EditorialApiFaultDetail", "EditorialErrors", "EditorialError"],
        ["EditorialApiFaultDetail", "OperationErrors", "OperationError"],
    )

    bing_errors: List[BingErrorDetail] = []
    for error_attribute_set in error_attribute_sets:
        bing_errors += _parse_error_detail(ex.fault.detail, error_attribute_set)

    tracking_id = ex.document.childAtPath('Envelope/Body/Fault/detail/AdApiFaultDetail/TrackingId')
    if tracking_id is not None:
        tracking_id = tracking_id.getText()

    return BingError(
        tracking_id=tracking_id,
        errors=bing_errors
    )


def _parse_bing_ads_webfault_error(error) -> BingErrorDetail:
    bing_error = BingErrorDetail()
    if hasattr(error, 'ErrorCode'):
        bing_error.error_code = error.ErrorCode
    if hasattr(error, 'Code'):
        bing_error.code = error.Code
    if hasattr(error, 'Details'):
        bing_error.details = error.Details
    if hasattr(error, 'Message'):
        bing_error.message = error.Message
    return bing_error


def _parse_error_detail(error_detail, error_attribute_set) -> List[BingErrorDetail]:
    bing_errors: List[BingErrorDetail] = []
    api_errors = error_detail
    for field in error_attribute_set:
        api_errors = getattr(api_errors, field, None)
    if api_errors is None:
        return bing_errors
    if isinstance(api_errors, list):
        for api_error in api_errors:
            bing_errors.append(_parse_bing_ads_webfault_error(api_error))
    else:
        bing_errors.append(_parse_bing_ads_webfault_error(api_errors))
    return bing_errors
