import requests, json, logging
from requests.auth import HTTPBasicAuth

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

class DeliveryCenterController:

    @classmethod
    def post_products(self, url, username, password, store_id, product):
        headers = dict()
        headers['Content-Type'] = 'application/json'

        r = requests.post(f'{url}/stores/{store_id}/products',
            headers=headers,
            data=json.dumps(product),
            auth=HTTPBasicAuth(username, password)
        )

        if r.status_code == 201 or r.status_code == 200:
            logging.info(f'Product sent... [{r.status_code}]')
        else:
            logging.error(f'Failed to send Product [{r.status_code}] - {r.content.decode("utf-8")}')

        return r

    @classmethod
    def patch_products(self, url, username, password, store_id, product_id, product):
        headers = dict()
        headers['Content-Type'] = 'application/json'

        r = requests.patch(f'{url}/stores/{store_id}/products/{product_id}',
            headers=headers,
            data=json.dumps(product),
            auth=HTTPBasicAuth(username, password)
        )

        if r.status_code == 201 or r.status_code == 200:
            logging.info(f'Product sent... [{r.status_code}]')
        else:
            logging.error(f'Failed to send Product [{r.status_code}] - {r.content.decode("utf-8")}')

        return r

    @classmethod
    def post_variants(self, url, username, password, store_id, product_id, variants):
        headers = dict()
        headers['Content-Type'] = 'application/json'

        r = requests.post(f'{url}/stores/{store_id}/products/{product_id}/variants',
            headers=headers,
            data=json.dumps(variants),
            auth=HTTPBasicAuth(username, password)
        )

        if r.status_code == 201 or r.status_code == 200:
            logging.info(f'Product sent... [{r.status_code}]')
        else:
            logging.error(f'Failed to create variants [{r.status_code}] - {r.content.decode("utf-8")}')

        return r

    @classmethod
    def patch_variants(self, url, username, password, store_id, product_id, variant_id, variants):
        headers = dict()
        headers['Content-Type'] = 'application/json'

        r = requests.patch(f'{url}/stores/{store_id}/products/{product_id}/variants/{variant_id}',
            headers=headers,
            data=json.dumps(variants),
            auth=HTTPBasicAuth(username, password)
        )

        if r.status_code == 201 or r.status_code == 200:
            logging.info(f'Inventory update... [{r.status_code}]')
        else:
            logging.error(f'Failed to update variants [{r.status_code}] - {r.content.decode("utf-8")}')

        return r
