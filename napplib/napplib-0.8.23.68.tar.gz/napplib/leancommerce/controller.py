import json
import logging
import requests

# Decorator to limit the number of requests by time
from .utils import requests_remaining, requests_remaining_config

# set logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

# * leancommerce APIs accept only 200 requests per minute.
requests_remaining_config['total_remaining'] = 200 # 200 requests
requests_remaining_config['time'] = 60  # 1 minute


class LeanCommerceController:
    """[
        This class is a compilation of calls for the integration of leancommerce.
        For more details on the leancommerce APIs access their documentation:
        https://integracao.leancommerce.com.br/swagger/index.html?urls.primaryName=v1
    ]
    """
    # create headers
    headers = dict()
    headers['Content-Type'] = 'application/json'

    # URL root
    url_root = 'https://integracao.leancommerce.com.br'

    @requests_remaining
    def authenticate(self, store_id, app_id, app_key):
        """[Function to authorize calls in leancommerce APIs, returning a token to use in other functions.]

        Args:
            store_id ([str]): [Store ID to identify store login]
            app_id ([str]): [App ID to authorize integration to leancommerce API]
            app_key ([str]): [App KEY to authorize integration to leancommerce API]

        Returns:
            [str]: [Return token to authorize others functions]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id

        # body authenticate
        body = dict()
        body['AppId'] = app_id
        body['AppKey'] = app_key

        # route to login
        route = f'/api/v1/login'
        r = requests.post(f'{self.url_root}{route}', data=json.dumps(body), headers=headers)

        token = ''
        if r.status_code == 200:
            logging.info(f'Authorization Success!! - {r.status_code}')
            # The response of this route when status == 200 is only the Authorization token "b'1234567 '",
            # it is necessary to give a decode to transform it into a string.
            token = r.content.decode()
        else:
            logging.error(f'Authorization Fail!! - {r.status_code} - {r.content}')

        return token

    @requests_remaining
    def get_grid_all(self, store_id, token):
        """[Function that collects all the grids of a store]

        Args:
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [json]: [a json with the grids of a store]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'
        # route to get grids
        route = f'/api/v1/catalogo/grades'
        r = requests.get(f'{self.url_root}{route}', headers=headers)

        grids = {}
        if r.status_code == 200:
            logging.info(f'Get Grid Success!! - {r.status_code}')
            # The response of this route when status == 200 is a json
            # containing the grids referring to the store
            grids = json.loads(r.content)
        else:
            logging.error(f'Get Grid Fail!! - {r.status_code} - {r.content}')
        
        return grids

    @requests_remaining
    def get_grid_by_id(self, grid_id, store_id, token):
        """[Function that collects a specific grid of a store through the ID.]

        Args:
            grid_id ([int, str]): [Grid ID to search]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [json]: [a json with a specific grid of a store]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to get specific grid
        route = f'/api/v1/catalogo/grades/{grid_id}'
        r = requests.get(f'{self.url_root}{route}', headers=headers)

        grid = {}
        if r.status_code == 200:
            logging.info(f'Get Grid({grid_id}) Success!! - {r.status_code}')
            # The response of this route when status == 200 is a json
            # containing the a specific grid referring to the store
            grid = json.loads(r.content)
        else:
            logging.error(f'Get Grid({grid_id}) Fail!! - {r.status_code} - {r.content}')
        
        return grid

    @requests_remaining
    def create_grid(self, grid, store_id, token):
        """[Function to create a store grid in leancommerce.]

        Args:
            grid ([dict]): [Grid Dict payload]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to create grid
        route = f'/api/v1/catalogo/grades'
        r = requests.post(f'{self.url_root}{route}', data=json.dumps(grid), headers=headers)

        if r.status_code == 200:
            logging.info(f'Create Grid Success!! - {r.status_code}')
        else:
            logging.error(f'Create Grid  Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def create_grid_value(self, grid_value, grid_id, store_id, token):
        """[Function to create a store grid value in leancommerce.]

        Args:
            grid_value ([dict]): [Grid Value Dict payload]
            grid_id ([int, str]): [grid ID to create a new value]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to create grid value
        route = f'/api/v1/catalogo/grades/{grid_id}/valores'
        r = requests.post(f'{self.url_root}{route}', data=json.dumps(grid_value), headers=headers)

        if r.status_code == 200:
            logging.info(f'Create Grid Value Success!! - {r.status_code}')
        else:
            logging.error(f'Create Grid Value Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def get_category_all(self, store_id, token):
        """[Function that collects all the categories of a store]

        Args:
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [json]: [a json with the categories of a store]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to get all categories
        route = f'/api/v1/catalogo/categorias'
        r = requests.get(f'{self.url_root}{route}', headers=headers)

        categories = {}
        if r.status_code == 200:
            logging.info(f'Get Category Success!! - {r.status_code}')
            # The response of this route when status == 200 is a json
            # containing the categories referring to the store
            categories = json.loads(r.content)
        else:
            logging.error(f'Get Category Fail!! - {r.status_code} - {r.content}')
        
        return categories

    @requests_remaining
    def get_category_by_id(self, category_id, store_id, token):
        """[Function that collects a specific category of a store through the ID.]

        Args:
            category_id ([int, str]): [Category ID to search]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [json]: [a json with the specific categories of a store]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to get specific categories
        route = f'/api/v1/catalogo/categorias/{category_id}'
        r = requests.get(f'{self.url_root}{route}', headers=headers)

        category = {}
        if r.status_code == 200:
            logging.info(f'Get Category({category_id}) Success!! - {r.status_code}')
            # The response of this route when status == 200 is a json
            # containing the a specific categories referring to the store
            category = json.loads(r.content)
        else:
            logging.error(f'Get Category({category_id}) Fail!! - {r.status_code} - {r.content}')
        
        return category

    @requests_remaining
    def create_category(self, category, store_id, token):
        """[Function to create a store category in leancommerce.]

        Args:
            category ([dict]): [Category Dict payload]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to create category
        route = f'/api/v1/catalogo/categorias'
        r = requests.post(f'{self.url_root}{route}', data=json.dumps(category), headers=headers)

        if r.status_code == 200:
            logging.info(f'Create Category Success!! - {r.status_code}')
        else:
            logging.error(f'Create Category Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def get_product_all(self, store_id, token):
        """[Function that collects all the products of a store]

        Args:
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [json]: [a json with the products of a store]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to get all products
        route = f'/api/v1/catalogo/produtos'
        r = requests.get(f'{self.url_root}{route}', headers=headers)

        products = {}
        if r.status_code == 200:
            logging.info(f'Get Product Success!! - {r.status_code}')
            # The response of this route when status == 200 is a json
            # containing the products referring to the store
            products = json.loads(r.content)
        else:
            logging.error(f'Get Product Fail!! - {r.status_code} - {r.content}')
        
        return products 

    @requests_remaining
    def get_product_by_id(self, product_id, store_id, token):
        """[Function that collects a specific product of a store]

        Args:
            store_id ([int, str]): [Product ID to search]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [json]: [a json with the specific product of a store]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to get specific product
        route = f'/api/v1/catalogo/produtos/{product_id}'
        r = requests.get(f'{self.url_root}{route}', headers=headers)

        products = {}
        if r.status_code == 200:
            logging.info(f'Get Product({product_id}) Success!! - {r.status_code}')
            # The response of this route when status == 200 is a json
            # containing the a specific product referring to the store
            products = json.loads(r.content)
        else:
            logging.error(f'Get Product({product_id}) Fail!! - {r.status_code} - {r.content}')
        
        return products

    @requests_remaining
    def create_product(self, product, store_id, token):
        """[Function to create a store product in leancommerce.]

        Args:
            product ([dict]): [Product Dict payload]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to create product
        route = f'/api/v1/catalogo/produtos'
        r = requests.post(f'{self.url_root}{route}', data=json.dumps(product), headers=headers)

        if r.status_code == 200:
            logging.info(f'Create Product Success!! - {r.status_code}')
        else:
            logging.error(f'Create Product Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def create_product_variation(self, product_variation, product_id, store_id, token):
        """[Function to create a store product variation in leancommerce.]

        Args:
            product_variation ([dict]): [Product Variation Dict payload]
            product_id ([int, str]): [Product ID to create a new variation]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to create product variation
        route = f'/api/v1/catalogo/produtos/{product_id}/variacoes'
        r = requests.post(f'{self.url_root}{route}', data=json.dumps(product_variation), headers=headers)

        if r.status_code == 200:
            logging.info(f'Create Product Variation Success!! - {r.status_code}')
        else:
            logging.error(f'Create Product Variation Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def update_product(self, product, product_id, store_id, token):
        """[Function to update store product]

        Args:
            product ([dict]): [Product Dict payload]
            product_id ([int, str]): [Product ID to update]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to update product
        route = f'/api/v1/catalogo/produtos/{product_id}'
        r = requests.put(f'{self.url_root}{route}', data=json.dumps(product), headers=headers)

        if r.status_code == 200:
            logging.info(f'Update Product Success!! - {r.status_code}')
        else:
            logging.error(f'Update Product Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def update_product_variation(self, product_variation, product_id, store_id, token):
        """[Function to update a store product variation.]

        Args:
            product_variation ([dict]): [Product Variation Dict payload]
            product_id ([int, str]): [Product ID to create a new variation]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to update product variation
        route = f'/api/v1/catalogo/produtos/{product_id}/variacoes'
        r = requests.put(f'{self.url_root}{route}', data=json.dumps(product_variation), headers=headers)

        if r.status_code == 200:
            logging.info(f'Update Product variation Success!! - {r.status_code}')
        else:
            logging.error(f'Update Product variation Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def update_prices(self, prices, store_id, token):
        """[Function to update a store product prices.]

        Args:
            prices ([dict]): [Prices Dict payload]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to update prices
        route = f'/api/v1/precos'
        r = requests.put(f'{self.url_root}{route}', data=json.dumps(prices), headers=headers)

        if r.status_code == 200:
            logging.info(f'Update Prices Success!! - {r.status_code}')
        else:
            logging.error(f'Update Prices Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def update_inventory(self, inventories, store_id, token):
        """[Function to update a store product inventory.]

        Args:
            inventories ([dict]): [Inventory Dict payload]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to update inventory
        route = f'/api/v1/estoque'
        r = requests.put(f'{self.url_root}{route}', data=json.dumps(inventories), headers=headers)

        if r.status_code == 200:
            logging.info(f'Update inventories Success!! - {r.status_code}')
        else:
            logging.error(f'Update inventories Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def create_image(self, product_images, product_id, store_id, token):
        """[Function to create a product image.]

        Args:
            product_images ([dict]): [Image Dict payload]
            product_id ([int, str]): [Product ID to create a new image]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to create image
        route = f'/api/v1/catalogo/produtos/{product_id}/imagens'
        r = requests.post(f'{self.url_root}{route}', data=json.dumps(product_images), headers=headers)

        if r.status_code == 200:
            logging.info(f'Create Product images Success!! - {r.status_code}')
        else:
            logging.error(f'Create Product images Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def get_order_all(self, store_id, token, page=0, result_per_page=25):
        """[Function that collects all the order of a store]

        Args:
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]
            page (int, optional): [Page number to search]. Defaults to 0.
            result_per_page (int, optional): [Total results per page]. Defaults to 25.

        Returns:
            [json]: [a json with the orders of a store]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        params = {
            "Pagina": page,
            "TotalRegistrosPorPagina": result_per_page
        }

        # route to get all orders
        route = f'/api/v1/pedidos'
        r = requests.get(f'{self.url_root}{route}', headers=headers, params=params)

        orders = {}
        if r.status_code == 200:
            logging.info(f'Get Orders Success!! - {r.status_code}')
            # The response of this route when status == 200 is a json
            # containing the orders referring to the store
            orders = json.loads(r.content)
        else:
            logging.error(f'Get Orders Fail!! - {r.status_code} - {r.content}')
        
        return orders 

    @requests_remaining
    def get_order_by_id(self, order_id, store_id, token):
        """[Function that collects a specific order of a store]

        Args:
            order_id ([int, str]): [Order ID to search]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [json]: [a json with the specific order of a store]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to get all orders
        route = f'/api/v1/pedidos/id/{order_id}'
        r = requests.get(f'{self.url_root}{route}', headers=headers)

        order = {}
        if r.status_code == 200:
            logging.info(f'Get Order({order_id}) Success!! - {r.status_code}')
            # The response of this route when status == 200 is a json
            # containing the a specific orders referring to the store
            order = json.loads(r.content)
        else:
            logging.error(f'Get Order({order_id}) Fail!! - {r.status_code} - {r.content}')
        
        return order 

    @requests_remaining
    def get_order_by_number(self, order_number, store_id, token):
        """[Function that collects a specific order of a store]

        Args:
            order_number ([str]): [Order Number to search]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [json]: [a json with the specific order of a store]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to get all orders
        route = f'/api/v1/pedidos/numero/{order_number}'
        r = requests.get(f'{self.url_root}{route}', headers=headers)

        order = {}
        if r.status_code == 200:
            logging.info(f'Get Order({order_number}) Success!! - {r.status_code}')
            # The response of this route when status == 200 is a json
            # containing the a specific orders referring to the store
            order = json.loads(r.content)
        else:
            logging.error(f'Get Order({order_number}) Fail!! - {r.status_code} - {r.content}')
        
        return order 

    @requests_remaining
    def update_order_tracking_by_number(self, order_tracking, order_number, store_id, token):
        """[Function to update a order tracking.]

        Args:
            order_tracking ([dict]): [Order Tracking Dict payload]
            order_number ([str]): [Order Number to update]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to update order tracking
        route = f'/api/v1/pedidos/numero/{order_number}/tracking'
        r = requests.post(f'{self.url_root}{route}', data=json.dumps(order_tracking), headers=headers)

        if r.status_code == 200:
            logging.info(f'Update order tracking Success!! - {r.status_code}')
        else:
            logging.error(f'Update order tracking Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def update_order_status_by_number(self, order_status, order_number, store_id, token):
        """[Function to update a order status.]

        Args:
            order_status ([dict]): [Order Tracking Dict payload]
            order_number ([str]): [Order Number to update]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to update order status
        route = f'/api/v1/pedidos/numero/{order_number}/tracking'
        r = requests.post(f'{self.url_root}{route}', data=json.dumps(order_status), headers=headers)

        if r.status_code == 200:
            logging.info(f'Update order status Success!! - {r.status_code}')
        else:
            logging.error(f'Update order status Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def create_invoice_by_number(self, invoice, order_number, store_id, token):
        """[Function to create a order invoice.]

        Args:
            invoice ([dict]): [Order Invoice Dict payload]
            order_number ([str]): [Order Number to update]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to create order invoice
        route = f'/api/v1/pedidos/{order_number}/nota-fiscal'
        r = requests.put(f'{self.url_root}{route}', data=json.dumps(invoice), headers=headers)

        if r.status_code == 200:
            logging.info(f'Create order invoice Success!! - {r.status_code}')
        else:
            logging.error(f'Create order invoice Fail!! - {r.status_code} - {r.content}')
        
        return r

    @requests_remaining
    def update_invoice_by_number(self, invoice, order_number, store_id, token):
        """[Function to update a order invoice.]

        Args:
            invoice ([dict]): [Order Invoice Dict payload]
            order_number ([str]): [Order Number to update]
            store_id ([str]): [Store ID to identify store]
            token ([str]): [Authorization token]

        Returns:
            [obj]: [Requests response Object]
        """
        headers = self.headers.copy()
        headers['x-loja-id'] = store_id
        headers['Authorization'] = f'Bearer {token}'

        # route to update order invoice
        route = f'/api/v1/pedidos/{order_number}/nota-fiscal'
        r = requests.put(f'{self.url_root}{route}', data=json.dumps(invoice), headers=headers)

        if r.status_code == 200:
            logging.info(f'Update order invoice Success!! - {r.status_code}')
        else:
            logging.error(f'Update order invoice Fail!! - {r.status_code} - {r.content}')
        
        return r

