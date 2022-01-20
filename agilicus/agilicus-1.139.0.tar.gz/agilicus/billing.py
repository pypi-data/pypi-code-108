import datetime
import os
import agilicus
from agilicus import ApiException

import json
from .input_helpers import get_org_from_input_or_ctx
from .output import output_if_console
from .context import get_apiclient_from_ctx
import operator

from .output.table import (
    column,
    spec_column,
    status_column,
    metadata_column,
    format_table,
    subtable,
)


def delete_billing_account(ctx, billing_account_id=None, **kwargs):
    client = get_apiclient_from_ctx(ctx)
    return client.billing_api.delete_billing_account(billing_account_id, **kwargs)


def get_billing_account(ctx, billing_account_id=None, **kwargs):
    client = get_apiclient_from_ctx(ctx)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    if org_id:
        kwargs["org_id"] = org_id
    else:
        kwargs.pop("org_id")
    return client.billing_api.get_billing_account(billing_account_id, **kwargs)


def list_accounts(ctx, **kwargs):
    client = get_apiclient_from_ctx(ctx)

    org_id = get_org_from_input_or_ctx(ctx, **kwargs)
    if org_id:
        kwargs["org_id"] = org_id
    else:
        kwargs.pop("org_id")
    return client.billing_api.list_billing_accounts(**kwargs)


def format_accounts(ctx, accounts):
    orgs_column = [column("id"), column("organisation")]
    products_column = [
        column("name"),
    ]
    columns = [
        metadata_column("id"),
        spec_column("customer_id"),
        spec_column("dev_mode"),
        spec_column("product_id"),
        status_column("product.spec.name", optional=True),
        status_column("customer", optional=True),
        subtable(ctx, "products", products_column, subobject_name="status"),
        subtable(ctx, "orgs", orgs_column, subobject_name="status"),
    ]
    return format_table(ctx, accounts, columns)


def add_billing_account(ctx, customer_id=None, dev_mode=None, **kwargs):
    client = get_apiclient_from_ctx(ctx)
    spec = agilicus.BillingAccountSpec(customer_id=customer_id)

    if dev_mode is not None:
        spec.dev_mode = dev_mode

    account = agilicus.BillingAccount(spec=spec)

    return client.billing_api.create_billing_account(account)


def add_org(ctx, billing_account_id=None, org_id=None, **kwargs):
    client = get_apiclient_from_ctx(ctx)
    billing_org = agilicus.BillingOrg._from_openapi_data(org_id=org_id)
    return client.billing_api.add_org_to_billing_account(
        billing_account_id, billing_org=billing_org
    )


def remove_org(ctx, billing_account_id=None, org_id=None, **kwargs):
    client = get_apiclient_from_ctx(ctx)
    return client.billing_api.remove_org_from_billing_account(billing_account_id, org_id)


def replace_billing_account(
    ctx,
    billing_account_id=None,
    customer_id=None,
    dev_mode=None,
    product_id=None,
    **kwargs,
):
    client = get_apiclient_from_ctx(ctx)

    existing = client.billing_api.get_billing_account(billing_account_id)
    if customer_id is not None:
        existing.spec.customer_id = customer_id
    if dev_mode is not None:
        existing.spec.dev_mode = dev_mode
    if product_id is not None:
        existing.spec.product_id = product_id
    return client.billing_api.replace_billing_account(
        billing_account_id, billing_account=existing
    )


def format_usage_records(ctx, records):
    columns = [
        column("id"),
        column("period"),
        column("total_usage"),
    ]
    return format_table(ctx, records, columns, getter=operator.itemgetter)


def get_usage_records(ctx, billing_account_id=None, **kwargs):
    client = get_apiclient_from_ctx(ctx)
    return client.billing_api.get_usage_records(billing_account_id)


def _dump_billing_failure(ctx, exception_description, account):
    account_info = {}
    try:
        account_info = account.to_dict()
    except Exception as exc:
        output_if_console(
            ctx,
            f"Failed to dump account info when handling billing failure: {str(exc)}",
        )
    error_message = {
        "time": datetime.datetime.now(datetime.timezone.utc),
        "msg": "error",
        "reason": str(exception_description),
        "account": account_info,
    }
    try:
        print(json.dumps(error_message, default=str))
    except Exception as exc:
        output_if_console(ctx, f"Failed to json.dumps failure info: {str(exc)}")


def run_billing_um_all_accounts(
    ctx, client, dry_run=False, push_to_prometheus_on_success=True, **kwargs
):
    accounts = client.billing_api.list_billing_accounts()
    record = agilicus.CreateBillingUsageRecords(dry_run=dry_run)
    numSuccess = 0
    numSkipped = 0
    numFail = 0
    now = datetime.datetime.now(datetime.timezone.utc)

    for account in accounts.billing_accounts:

        if not account.spec.customer_id:
            numSkipped += 1
            continue
        try:

            skip = False

            # Handle the case where an org is disabled or deleted,
            # w/o the corresponding stripe account. Give a 2 day
            # grace period (to allow the trailing stat to be written),
            # then stop attempting.
            for oid in account.status.orgs:
                if (
                    oid.admin_state == agilicus.OrganisationStateSelector("disabled")
                    or oid.admin_state == agilicus.OrganisationStateSelector("deleted")
                ) and ((now - oid.updated).total_seconds()) > 2 * 86400:
                    skip = True
                else:
                    skip = False

            if skip or len(account.status.orgs) == 0:
                numSkipped += 1
                print(
                    json.dumps(
                        {
                            "skip": True,
                            "billing_account": account.metadata.id,
                            "customer_id": account.spec.customer_id,
                        }
                    )
                )
                continue

            base_result = client.billing_api.add_billing_usage_record(
                account.metadata.id, create_billing_usage_records=record
            )
            success = False
            if base_result:
                result = base_result.to_dict()
                success = True
            else:
                result = {}

            result["billing_account"] = account.metadata.id
            result["customer_id"] = account.spec.customer_id
            result["orgs"] = [
                {"id": org.id, "organisation": org.organisation}
                for org in account.status.orgs
            ]
            if success:
                numSuccess += 1
                result["published"] = True
            else:
                numSkipped += 1
                result["published"] = False
            print(json.dumps(result))
        except ApiException as exc:
            numFail += 1
            _dump_billing_failure(ctx, exc.body, account)
        except Exception as exc:
            numFail += 1
            _dump_billing_failure(ctx, exc, account)

    if push_to_prometheus_on_success:
        try:
            from prometheus_client import (
                CollectorRegistry,
                Gauge,
                push_to_gateway,
            )
        except ModuleNotFoundError:
            output_if_console(ctx, "Not posting success to prometheus_client.")
            output_if_console(
                ctx, "Add the 'billing' option to the install to gain access"
            )
            return

        registry = CollectorRegistry()
        gSuccess = Gauge(
            "billing_usage_records_created_count",
            "number of billing accounts that have created a usage record",
            registry=registry,
        )

        gFail = Gauge(
            "billing_usage_records_failed_count",
            "number of billing accounts that failed to create a usage record",
            registry=registry,
        )
        gSkipped = Gauge(
            "billing_usage_records_skipped_count",
            "number of billing accounts that were skipped",
            registry=registry,
        )

        push_gateway = os.environ.get(
            "PROMETHEUS_PUSH_GATEWAY",
            "push-prometheus-pushgateway.prometheus-pushgateway:9091",
        )
        job_name = os.environ.get("JOB_NAME", "billing_usage_job")
        gSuccess.set(numSuccess)
        gFail.set(numFail)
        gSkipped.set(numSkipped)
        push_to_gateway(push_gateway, job=job_name, registry=registry)


def create_usage_record(
    ctx, billing_account_id=None, all_accounts=None, dry_run=False, **kwargs
):
    client = get_apiclient_from_ctx(ctx)
    record = agilicus.BillingUsageRecord(dry_run=dry_run)
    if billing_account_id is not None:
        result = client.billing_api.add_billing_usage_record(
            billing_account_id, billing_usage_record=record
        )
        print(json.dumps(result.to_dict()))
    elif all_accounts is not None:
        run_billing_um_all_accounts(ctx, client, dry_run=dry_run, **kwargs)
    else:
        raise Exception("Need to choose --billing-account-or or --all-accounts")


def list_products(ctx, **kwargs):
    client = get_apiclient_from_ctx(ctx)
    return client.billing_api.list_products(**kwargs)


def format_products(ctx, products_obj):
    products = products_obj.to_dict()

    def get_product_name(record, key):
        return record["product"]["name"]

    product_price_column = [
        column("id", optional=True),
        column("product name", getter=get_product_name, optional=True),
        column("unit_amount", optional=True),
    ]
    columns = [
        metadata_column("id"),
        spec_column("name"),
        spec_column("dev_mode", optional=True),
        subtable(
            ctx,
            "billing_product_prices",
            product_price_column,
            table_getter=operator.itemgetter,
            subobject_name="status",
            optional=True,
        ),
    ]
    return format_table(
        ctx, products.get("products"), columns, getter=operator.itemgetter
    )


def add_product(ctx, name=None, dev_mode=None, product_price_ids=[], **kwargs):
    client = get_apiclient_from_ctx(ctx)
    prices = []
    for price_id in product_price_ids:
        prices.append(agilicus.BillingProductPrice(id=price_id))
    spec = agilicus.ProductSpec(name=name, billing_product_prices=prices)

    if dev_mode is not None:
        spec.dev_mode = dev_mode

    product = agilicus.Product(spec=spec)

    return client.billing_api.create_product(product)


def delete_product(ctx, product_id=None, **kwargs):
    client = get_apiclient_from_ctx(ctx)
    return client.billing_api.delete_product(product_id)


def get_product(ctx, product_id=None, **kwargs):
    client = get_apiclient_from_ctx(ctx)
    return client.billing_api.get_product(product_id)


def update_product(
    ctx,
    product_id=None,
    dev_mode=None,
    name=None,
    product_price_ids=None,
    remove_product_price_ids=None,
    **kwargs,
):
    client = get_apiclient_from_ctx(ctx)

    product = client.billing_api.get_product(product_id)

    if remove_product_price_ids is not None:
        old_prices = product.spec.billing_product_prices
        product.spec.billing_product_prices = []
        for price in old_prices:
            if price.id in remove_product_price_ids:
                # needs to be removed.
                continue
            product.spec.billing_product_prices.append(price)

    if product_price_ids is not None:
        for price_id in product_price_ids:
            product.spec.billing_product_prices.append(
                agilicus.BillingProductPrice(id=price_id)
            )

    if dev_mode is not None:
        product.spec.dev_mode = dev_mode
    if name is not None:
        product.spec.name = name
    return client.billing_api.replace_product(
        product_id,
        product=product,
    )
