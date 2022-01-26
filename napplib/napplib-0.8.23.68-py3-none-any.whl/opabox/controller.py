import requests, json, datetime, logging, sys
from napplib.hub.controller import HubController

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

class OpaBoxController:
    @classmethod
    def check_parents(self, products, token, hub_store_id):
        parent_products = {}
        for pd in products:
            product = HubController.get_store_product_by_id(server_url='https://opabox.nappsolutions.com', token=token, id=pd['storeProductId'], store_id=hub_store_id)
            product.update({"mkp": pd})
            if product['parentProductId']['Int64']:
                if not product['parentProductId']['Int64'] in parent_products:
                    parent_products[product['parentProductId']['Int64']] = {"child": [], "main": []}
                parent_products[product['parentProductId']['Int64']]['child'].append(product)
            else:
                if not product['productId']['Int64'] in parent_products:
                    parent_products[product['productId']['Int64']] = {"child": [], "main": []}
                parent_products[product['productId']['Int64']]['main'].append(product)
        
        return parent_products

    @classmethod
    def make_new_product(self, product='', categ_id='', categ='', token='', parents=False, promotional_price=False, active=False):
        # verifica se existe relação pai x filho e cria o payload
        if parents:
            main_product = product['child'][0]
            parent = HubController.get_product_by_id(server_url='https://opabox.nappsolutions.com', token=token, product_id=main_product['parentProductId']['Int64'])

            image_url = None

            if main_product['imageURL']['String']:
                image_url = [{
                    "url": main_product['imageURL']['String'],
                    "order": 0
                }]

            payload = {
                "active": active,  #owner chose active or inactive
                "external_id": str(parent["id"]),
                "name": str(parent["name"]),
                "description": str(parent["description"]), #Optional
                "order": 0, # em casos de variantes de produto seguir uma ordem.
                "updated_at": int(datetime.datetime.now().timestamp()),
                "photos": image_url,
                "presentations": [],
                "product_views": []
            }

            presentations = {}

            product_sequence = 0

            for pd in product['child']:
                detail = HubController.get_product_by_id(server_url='https://opabox.nappsolutions.com', token=token, product_id=pd['productId']['Int64'])
                # coleta os atributos do produto filho
                if detail.get('attributes'):
                    product_sequence += 1

                    # --- set promotional price of product --- #
                    price_of = None

                    if promotional_price:
                        price_of = pd["listPrice"]
                
                    product_view = {
                        "active": True,
                        "id": str(pd["id"]),
                        "name": str(pd["productName"]["String"]),
                        "order": 0,
                        "photos": image_url,
                        "price": pd["salePrice"],
                        "price_cost": pd["listPrice"],
                        "promotional_price": price_of,
                        "stock_quantity": pd["stockQuantity"],
                        "unit_label": pd["measurementUnit"]["String"] if pd["measurementUnit"]["String"] else "UN",
                        "unit_quantity": 1,
                        "view": [],
                    }

                    if pd['eanProduct']['String']:
                        product_view.update({
                            "ean": str(pd['eanProduct']['String'])
                        })
                        product_view.update({
                            "sku": str(pd['productCode']['String'])
                        })
                    else:
                        # product_view.update({
                        #     "ean": str(product['productCode']['String'])
                        # })
                        product_view.update({
                            "sku": str(pd['productCode']['String'])
                        })

                    for attribute in detail['attributes']:
                        if attribute['name'].lower() == "cor":
                            if not "cor" in presentations:
                                presentations['cor'] = {
                                    "id": str(attribute['id']),
                                    "name": "Cor",
                                    "options": []
                                }
                            if not str(attribute['values'][0]['id']) in [c['id'] for c in presentations['cor']['options']]:
                                option = {
                                    "id": str(attribute['values'][0]['id']),
                                    "label": attribute['values'][0]['value']
                                }
                                presentations['cor']['options'].append(option)
                                product_view['view'].append({"option_id": option['id'], 'presentation_id': presentations['cor']['id']})
                            else:
                                option = {}

                                for op in presentations['cor']['options']:
                                    if str(attribute['values'][0]['id']) == str(op['id']):
                                        option = op

                                product_view['view'].append({"option_id": option['id'], 'presentation_id': presentations['cor']['id']})

                        if attribute['name'].lower() == 'tamanho':
                            size = attribute['values'][0]['value']
                            if not "tamanho" in presentations:
                                presentations['tamanho'] = {
                                    "id": str(attribute['id']),
                                    "name": "tamanho",
                                    "options": []
                                }

                            if not str(attribute['values'][0]['id']) in [c['id'] for c in presentations['tamanho']['options']]:
                                option = {
                                    "id": str(attribute['values'][0]['id']),
                                    "label": str(attribute['values'][0]['value'])
                                }
                                presentations['tamanho']['options'].append(option)
                                product_view['view'].append({"option_id": str(option['id']), 'presentation_id': str(presentations['tamanho']['id'])})
                            else:
                                option = {}

                                for op in presentations['tamanho']['options']:
                                    if str(attribute['values'][0]['id']) == op['id']:
                                        option = op
                                product_view['view'].append({"option_id": str(option['id']), 'presentation_id': str(presentations['tamanho']['id'])})

                    payload['product_views'].append(product_view)

            for key, presentation in presentations.items():
                payload['presentations'].append(presentation)
                
            if categ:
                payload.update({
                    "category_id": str(categ_id),
                    "category_label": str(categ)
                })

        # caso não haja relação de pai e filho
        else:
            presentations = {}
            store_product = product

            image_url = None

            if store_product['imageURL']['String']:
                image_url = [{
                    "url": store_product['imageURL']['String'],
                    "order": 0
                }]

            payload = {
                "active": active,  #owner chose active or inactive
                "external_id": str(store_product['id']),
                "name": str(store_product["productName"]["String"]),
                "description": str(store_product["productDescription"]["String"]), #Optional
                "order": 0, # em casos de variantes de produto seguir uma ordem.
                "updated_at": int(datetime.datetime.now().timestamp()),
                "photos": image_url,
                "presentations": [],
                "product_views": []
            }

            detail = HubController.get_product_by_id(server_url='https://opabox.nappsolutions.com', token=token, product_id=store_product['productId']['Int64'])
            
            if detail.get('attributes'):
                # --- set promotional price of product --- #
                price_of = None

                if promotional_price:
                    price_of = store_product["listPrice"]

                product_view = {
                    "active": True,
                    "id": str(store_product["id"]),
                    "name": str(store_product["productName"]["String"]),
                    "order": 0,
                    "photos": image_url,
                    "price": store_product["salePrice"],
                    "price_cost": store_product["listPrice"],
                    "promotional_price": price_of,
                    "stock_quantity": store_product["stockQuantity"],
                    "unit_label": store_product["measurementUnit"]["String"] if store_product["measurementUnit"]["String"] else "UN",
                    "unit_quantity": 1,
                    "view": [],
                }

                for attribute in detail['attributes']:
                    # create attributes of cor for opabox
                    if attribute['name'].lower() == "cor":
                        if not "cor" in presentations:
                            presentations['cor'] = {
                                "id": str(attribute['id']),
                                "name": "Cor",
                                "options": []
                            }
                    
                        if not str(attribute['values'][0]['id']) in [c['id'] for c in presentations['cor']['options']]:
                            option = {
                                "id": str(attribute['values'][0]['id']),
                                "label": attribute['values'][0]['value']
                            }
                            presentations['cor']['options'].append(option)
                            product_view['view'].append({"option_id": option['id'], 'presentation_id': presentations['cor']['id']})
                        else:
                            option = {}

                            for op in presentations['cor']['options']:
                                if str(attribute['values'][0]['id']) == str(op['id']):
                                    option = op

                            product_view['view'].append({"option_id": option['id'], 'presentation_id': presentations['cor']['id']})

                    # create attributes of size for opabox
                    if attribute['name'].lower() == "tamanho":
                        size = attribute['values'][0]['value']
                        if not "tamanho" in presentations:
                            presentations['tamanho'] = {
                                "id": str(attribute['id']),
                                "name": "tamanho",
                                "options": []
                            }

                        if not str(attribute['values'][0]['id']) in [c['id'] for c in presentations['tamanho']['options']]:
                            option = {
                                "id": str(attribute['values'][0]['id']),
                                "label": str(attribute['values'][0]['value'])
                            }
                            presentations['tamanho']['options'].append(option)
                            product_view['view'].append({"option_id": str(option['id']), 'presentation_id': str(presentations['tamanho']['id'])})
                        else:
                            option = {}

                            for op in presentations['tamanho']['options']:
                                if str(attribute['values'][0]['id']) == op['id']:
                                    option = op
                            product_view['view'].append({"option_id": str(option['id']), 'presentation_id': str(presentations['tamanho']['id'])})

                payload['product_views'].append(product_view)

            else:
                # --- set promotional price of product --- #
                price_of = None

                if promotional_price:
                    price_of = store_product["listPrice"]

                product_view = {
                        "active": True,
                        "id": str(store_product["id"]),
                        "name": str(store_product["productName"]["String"]),
                        "order": 0,
                        "photos": image_url,
                        "price": store_product["salePrice"],
                        "price_cost": store_product["listPrice"],
                        "promotional_price": price_of,
                        "stock_quantity": store_product["stockQuantity"],
                        "unit_label": store_product["measurementUnit"]["String"] if store_product["measurementUnit"]["String"] else "UN",
                        "unit_quantity": 1,
                        "view": [],
                    }

                payload['product_views'].append(product_view)

            if store_product['eanProduct']['String']:
                product_view.update({
                    "ean": str(store_product['eanProduct']['String'])
                })
                product_view.update({
                    "sku": str(store_product['productCode']['String'])
                })
            else:
                # product_view.update({
                #     "ean": str(a['productCode']['String'])
                # })
                product_view.update({
                    "sku": str(store_product['productCode']['String'])
                })

            if categ and categ_id:
                payload.update({
                    "category_id": str(categ_id),
                    "category_label": str(categ)
                })

        return payload

    @classmethod
    def make_update_product(self, product, promotional_price=False, parents=False):
        external_id = str(product["id"])
        price_of = None

        if promotional_price:
            price_of = float(product["listPrice"])

        if parents:
            external_id = str(product['parentProductId']['Int64'])

        payload = {
            "external_id": external_id,
            "price": float(product["salePrice"]),
            "price_cost": float(product["listPrice"]),
            "stock": int(product["stockQuantity"]),
            "promotional_price": price_of
        }

        if parents:
            payload.update({'product_view_id': str(product["id"])})

        return payload

    @classmethod
    def create_products(self, server_url, company, api_token='', products=[]):
        # create headers
        headers = {'Content-Type': 'Application/json'}

        # create url
        url = f'{server_url}/prod/v2/company/{company}/products?api_token={api_token}'

        for product in products:
            # do request to create a product
            logging.info(f'Criando produto na opabox...')
            r = requests.put(url, headers=headers, data=json.dumps([product]))

            if r.status_code == 200:
                logging.info('Sucessfull create product in opabox')
            else:
                logging.error(f'Error at created product in opabox {r.status_code} - {r.text}')

        return r.status_code

    @classmethod
    def update_product(self, server_url, company, api_token='', products=[], pagination=50):
        # create headers
        headers = {'Content-Type': 'Application/json'}
        
        for i in range(0, len(products), pagination):
            # create url
            url = f'{server_url}/prod/v2/company/{company}/products_price_stock?api_token={api_token}'

            # create product payload
            payload_product = json.dumps(products[i:i+pagination], ensure_ascii=False)

            # do request to create a product
            r = requests.post(url, headers=headers, data=payload_product)

            # # log
            logging.info(f'OpaBox update products {r.status_code}:{r.content} - from {i} to {i+pagination if i+pagination<len(products) else len(products)}')
