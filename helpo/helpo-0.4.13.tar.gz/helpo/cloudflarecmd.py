import json
import os
import sys

import typer
from loguru import logger

from helpo.cloudflare import Cloudflare

app = typer.Typer()


@logger.catch
@app.command()
def purge_all_files(zone_name: str,
                    cf_email: str = os.environ.get('CF_API_EMAIL'),
                    cf_key: str = os.environ.get('CF_API_KEY')):
    cf_api = Cloudflare(cf_email, cf_key)
    purge_result = cf_api.purge_all_files(zone_name)
    if purge_result:
        typer.echo(purge_result)
    else:
        sys.exit(1)


@logger.catch
@app.command()
def purge_files_by_url(zone_name: str, urls: str,
                       cf_email: str = os.environ.get('CF_API_EMAIL'),
                       cf_key: str = os.environ.get('CF_API_KEY')):
    cf_api = Cloudflare(cf_email, cf_key)
    urls_list = urls.split(',')
    purge_result = cf_api.purge_files_by_url(zone_name, urls_list)
    if purge_result:
        typer.echo(purge_result)
    else:
        sys.exit(1)


@logger.catch
@app.command()
def get_dns_record_value(zone_name: str, fqdn: str,
                         cf_email: str = os.environ.get('CF_API_EMAIL'),
                         cf_key: str = os.environ.get('CF_API_KEY')):
    cf_api = Cloudflare(cf_email, cf_key)
    record = cf_api.get_dns_record_value(zone_name, fqdn)[0]
    if record:
        typer.echo(json.dumps(
            {'name': record['name'], 'content': record['content']}))
    else:
        sys.exit(1)


@logger.catch
@app.command()
def create_zone(zone_name: str, account_id: str,
                cf_email: str = os.environ.get('CF_API_EMAIL'),
                cf_key: str = os.environ.get('CF_API_KEY')):
    cf_api = Cloudflare(cf_email, cf_key)
    zone_info = cf_api.create_zone(zone_name, account_id)
    if zone_info:
        typer.echo(json.dumps(
            {'name': zone_info['name'], 'id': zone_info['id']}))
    else:
        sys.exit(1)


@logger.catch
@app.command()
def buy_new_domain(zone_name: str, account_id: str,
                   cf_email: str = os.environ.get('CF_API_EMAIL'),
                   cf_key: str = os.environ.get('CF_API_KEY')):
    cf_api = Cloudflare(cf_email, cf_key)
    zone_info = cf_api.buy_new_domain(account_id, zone_name)
    if zone_info and zone_info['available']:
        typer.echo(zone_info)
    else:
        typer.echo(f'unavailable domain: {zone_name}')
        sys.exit(1)


@logger.catch
@app.command()
def list_domains(account_id: str,
                 cf_email: str = os.environ.get('CF_API_EMAIL'),
                 cf_key: str = os.environ.get('CF_API_KEY')):
    cf_api = Cloudflare(cf_email, cf_key)
    zone_info = cf_api.list_domains(account_id)
    if zone_info:
        typer.echo(zone_info)
    else:
        sys.exit(1)


@logger.catch
@app.command()
def disable_dns_record_proxy(zone_name: str, fqdn: str,
                             cf_email: str = os.environ.get('CF_API_EMAIL'),
                             cf_key: str = os.environ.get('CF_API_KEY')):
    cf_api = Cloudflare(cf_email, cf_key)
    record = cf_api.disable_dns_record_proxy(zone_name, fqdn)
    if record:
        typer.echo(record)
    else:
        sys.exit(1)


@logger.catch
@app.command()
def enable_dns_record_proxy(zone_name: str, fqdn: str,
                            cf_email: str = os.environ.get('CF_API_EMAIL'),
                            cf_key: str = os.environ.get('CF_API_KEY')):
    cf_api = Cloudflare(cf_email, cf_key)
    record = cf_api.enable_dns_record_proxy(zone_name, fqdn)
    if record:
        typer.echo(record)
    else:
        sys.exit(1)


@logger.catch
@app.command()
def update_dns_record(zone_name: str, fqdn: str, value: str,
                      cf_email: str = os.environ.get('CF_API_EMAIL'),
                      cf_key: str = os.environ.get('CF_API_KEY')):
    cf_api = Cloudflare(cf_email, cf_key)
    record = cf_api.update_dns_record(zone_name, fqdn, value)
    if record:
        typer.echo(record)
    else:
        sys.exit(1)


if __name__ == "__main__":
    app()
