import requests, json, base64, logging

# set logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

class ShopifyController:
    @classmethod
    def create_product(self, domain='', app_key='', app_secret='', product=''):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        url = f"https://{app_key}:{app_secret}@{domain}/admin/products.json"
        
        title = product['product']['title']
        r = requests.post(url, json=product,  headers=headers)
        if r.status_code == 201:
            logging.info(f'Creating Product: {title}, Response: {r.status_code}')
        else:
            logging.info(f'Creating Product: {title}, Response: {r.status_code}, Error: {r.content.decode("utf-8")}')
        return r.json()

    @classmethod
    def get_all_products(self, domain='', app_key='', app_secret=''):
        url = f"https://{app_key}:{app_secret}@{domain}/admin/products.json"
        r = requests.get(url)
        return r.json()

    @classmethod
    def get_specific_product(self, domain='', app_key='', app_secret='', productId=''):
        url = f"https://{app_key}:{app_secret}@{domain}/admin/products/{productId}.json"
        r = requests.get(url)
        return r.json()

    @classmethod
    def get_specific_variant(self, domain='', app_key='', app_secret='', skuId=''):
        url = f"https://{app_key}:{app_secret}@{domain}/admin/variants/{skuId}.json"
        logging.info(url)
        r = requests.get(url)
        return r.json()

    @classmethod
    def get_specific_inventory(self, domain='', app_key='', app_secret='', inventoryId=''):
        url = f"https://{app_key}:{app_secret}@{domain}/admin/inventory_items/{inventoryId}.json"
        r = requests.get(url)
        return r.json()
    
    @classmethod
    def get_all_locations(self, domain='', app_key='', app_secret='', inventoryId=''):
        url = f"https://{app_key}:{app_secret}@{domain}/admin/locations.json"
        r = requests.get(url)
        return r.json()

    @classmethod
    def create_variant(self, domain='', app_key='', app_secret='', productId='', variant=''):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        
        url = f"https://{app_key}:{app_secret}@{domain}/admin/products/{productId}/variants.json"
        title = variant['variant']['sku']
        
        r = requests.post(url, json=variant,  headers=headers)
        msg = json.loads(r.content.decode("utf-8"))
        
        if r.status_code == 201:
            logging.info(f'Creating SKU: {title}, Response: {r.status_code}')
        else:
            logging.info(f'Creating SKU: {title}, Response: {r.status_code}, Error: {msg}')
        return msg

    @classmethod
    def update_variant(self, domain='', app_key='', app_secret='', productId='', product=''):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        url = f"https://{app_key}:{app_secret}@{domain}/admin/variants/{productId}.json"
        title = product['variant']['sku']
        r = requests.put(url, json=product,  headers=headers)
        if r.status_code == 200:
            logging.info(f'Updating SKU: {title}, Response: {r.status_code}')
        else:
            logging.info(f'Updating SKU: {title}, Response: {r.status_code}, Error: {r.content.decode("utf-8")}')
        return r.status_code

    @classmethod
    def update_inventory(self, domain='', app_key='', app_secret='', inventory=''):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        url = f"https://{app_key}:{app_secret}@{domain}/admin/inventory_levels/set.json"

        r = requests.post(url, json=inventory,  headers=headers)
        if r.status_code == 200:
            logging.info(f'Updating SKU inventory... Response: {r.status_code}')
        else:
            logging.info(f'Updating SKU inventory... Response: {r.status_code}, Error: {r.content.decode("utf-8")}')
        return r.status_code

    @classmethod
    def delete_product(self, domain='', app_key='', app_secret='', productId=''):
        url = f"https://{app_key}:{app_secret}@{domain}/admin/products/{productId}.json"
        r = requests.delete(url)
        logging.info(r.status_code)

    @classmethod
    def get_order_transactions(self, domain='', app_key='', app_secret='', orderId=''):
        auth_key = f'{app_key}:{app_secret}'.encode('ascii')
        base64_bytes = base64.b64encode(auth_key)
        base64_auth = f'Bearer {base64_bytes.decode("ascii")}'

        headers = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": base64_auth}
        url = f"https://{app_key}:{app_secret}@{domain}/admin/orders/{orderId}/transactions.json"

        r = requests.get(url, headers=headers)
        r = json.loads(r.content.decode('utf-8'))
        return r

    @classmethod
    def get_order_fulfillments(self, domain='', app_key='', app_secret='', orderId='', fulfillmentId=''):
        auth_key = f'{app_key}:{app_secret}'.encode('ascii')
        base64_bytes = base64.b64encode(auth_key)
        base64_auth = f'Bearer {base64_bytes.decode("ascii")}'

        headers = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": base64_auth}
        url = f"https://{app_key}:{app_secret}@{domain}/admin/orders/{orderId}/fulfillments/{fulfillmentId}/events.json"

        r = requests.get(url, headers=headers)
        r = json.loads(r.content.decode('utf-8'))
        return r

    def put_product_price(domain='', app_key='', app_secret='', price_data=''):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        variant_code = price_data['variant']['id']

        url = f"https://{app_key}:{app_secret}@{domain}/admin/variants/{variant_code}.json"
        r = requests.put(url, json=price_data,  headers=headers)
        if r.status_code == 200:
            logging.info(f'Updating SKU price... Response: {r.status_code}')
        else:
            logging.info(f'Updating SKU price... Response: {r.status_code}, Error: {r.content.decode("utf-8")}')
        return r