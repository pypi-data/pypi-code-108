import CloudFlare
from loguru import logger


class Cloudflare(object):
    """
    Prepares cloudflare api client to execute api v4 calls on specific account
    """

    def __init__(self, cf_email: str, cf_key: str):
        self.cf_email = cf_email
        self.cf_key = cf_key
        self.cf_api = CloudFlare.CloudFlare(
            email=self.cf_email, token=self.cf_key)

    @logger.catch
    def purge_all_files(self, zone_name: str):
        zone_id = self.get_zone_id(zone_name)
        purge_cache_result = self.purge_cache(
            zone_id, {'purge_everything': True})
        return purge_cache_result

    @logger.catch
    def purge_files_by_url(self, zone_name: str, urls: list):
        zone_id = self.get_zone_id(zone_name)
        purge_cache_result = self.purge_cache(zone_id, {'files': urls})
        return purge_cache_result

    @logger.catch
    def disable_dns_record_proxy(self, zone_name: str, fqdn: str):
        zone_id = self.get_zone_id(zone_name)
        try:
            record_id = self.get_dns_record_value(zone_name, fqdn)[0]['id']
            return self.cf_api.zones.dns_records.patch(zone_id, record_id, data={'name': fqdn, 'proxied': False})
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/zones/dns_records %s - %d %s - api call failed' % (fqdn, e, e))

    @logger.catch
    def enable_dns_record_proxy(self, zone_name: str, fqdn: str):
        zone_id = self.get_zone_id(zone_name)
        try:
            record_id = self.get_dns_record_value(zone_name, fqdn)[0]['id']
            return self.cf_api.zones.dns_records.patch(zone_id, record_id, data={'name': fqdn, 'proxied': True})
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/zones/dns_records %s - %d %s - api call failed' % (fqdn, e, e))

    @logger.catch
    def get_zone_id(self, zone_name: str):
        """

        :param zone_name: domain name
        :return: id of the domain name
        """
        zones_returned = self.cf_api.zones.get(params={'name': f'{zone_name}'})
        zone_id = zones_returned[0]['id']
        return zone_id

    @logger.catch
    def get_dns_record_value(self, zone_name: str, fqdn: str):
        zone_id = self.get_zone_id(zone_name)
        return self.cf_api.zones.dns_records.get(zone_id, params={'name': fqdn, 'type': 'A'})

    @logger.catch
    def purge_cache(self, zone_id: str, payload: dict):
        """
        :param zone_id: cloudflare_zone_id
        :param payload: {'purge_everything': True} or {'files': ['/', '/index.html']}
        :return: {'id': 'zone_id'} or exception
        """
        return self.cf_api.zones.purge_cache.post(zone_id, data=payload)

    @logger.catch
    def create_zone(self, zone_name: str, account_id: str):
        return self.cf_api.zones.post(data={"name": zone_name,
                                            "account": {"id": account_id},
                                            "jump_start": True,
                                            "type": "full"})

    @logger.catch
    def buy_new_domain(self, account_id: str, zone_name: str):
        return self.cf_api.accounts.registrar.domains.get(account_id, zone_name)

    @logger.catch
    def list_domains(self, account_id: str):
        return self.cf_api.accounts.registrar.domains.get(account_id)

    @logger.catch
    def update_dns_record(self, zone_name: str, fqdn: str, value: str):
        zone_id = self.get_zone_id(zone_name)
        try:
            record_id = self.get_dns_record_value(zone_name, fqdn)[0]['id']
            return self.cf_api.zones.dns_records.put(zone_id, record_id,
                                                     data={'type': 'A', 'name': fqdn, 'content': value, 'ttl': 1})
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/zones/dns_records %s - %d %s - api call failed' % (fqdn, e, e))
