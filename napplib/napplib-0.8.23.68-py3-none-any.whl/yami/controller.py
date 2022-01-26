import json
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

class YamiController:
    """Controller da API Yami"""
    url = 'https://api.ymi.io'
    timeout = 30 * 60 # 30 minutos 

    @classmethod
    def create_brand(cls, token, account, brand):
        """Cria uma marca
        - Parametros:
        ---
            - token: str
            - account: str
            - brand: YamiBrand"""

        r = cls._request('POST', f'catalog/brand?an={account}', token=token, data=json.dumps(brand.__dict__))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Created Brand... [{r.status_code}] - {r.content.decode("utf-8")}')
            return json.loads(r.content.decode('utf8'))['brandId']

        logging.error(f'Failed to create Brand [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def create_category(cls, token, account, category):
        """Cria uma categoria
        - Parametros:
        ---
            - token: str
            - account: str
            - category: YamiCategory"""

        r = cls._request('POST', f'catalog/category?an={account}', token=token, data=json.dumps(category.__dict__))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Created Category... [{r.status_code}] - {r.content.decode("utf-8")}')
            return json.loads(r.content.decode('utf8'))['idCategory']

        logging.error(f'Failed to create Category [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def update_product(cls, token, account, productId, product):
        """Atualiza um produto
        - Parametros:
        ---
            - token: str
            - account: str
            - productId: str
            - product: YamiProduct"""

        r = cls._request('PUT', f'catalog/product/{productId}?an={account}', token=token, data=json.dumps(product.__dict__))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Updated Product... [{r.status_code}] - {r.content.decode("utf-8")}')
            return json.loads(r.content.decode('utf8'))['productId']

        logging.error(f'Failed to update Product [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def create_product(cls, token, account, product):
        """Cria um produto
        - Parametros:
        ---
            - token: str
            - account: str
            - product: YamiProduct"""
        
        r = cls._request('POST', f'catalog/product/?an={account}', token=token, data=json.dumps(product.__dict__))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Created Product... [{r.status_code}] - {r.content.decode("utf-8")}')
            return json.loads(r.content.decode('utf8'))['id']

        logging.error(f'Failed to create Product [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def update_variation(cls, token, account, skuId, variation):
        """Atualiza uma variação do produto pai
        - Parametros:
        ---
            - token: str
            - account: str
            - skuId:
            - variation: YamiSKUProduct"""
        
        r = cls._request('PUT', f'catalog/sku/{skuId}?an={account}', token=token, data=json.dumps(variation.__dict__))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Updated Product SKU Variation... [{r.status_code}] - {r.content.decode("utf-8")}')
            return json.loads(r.content.decode('utf8'))['skuId']

        logging.error(f'Failed to update Product SKU Variation [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def create_variation(cls, token, account, variation):
        """Cria uma variação do produto pai
        - Parametros:
        ---
            - token: str
            - account: str
            - variation: YamiSKUProduct"""
        
        r = cls._request('POST', f'catalog/sku?an={account}', token=token, data=json.dumps(variation.__dict__))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Created Product SKU... [{r.status_code}] - {r.content.decode("utf-8")}')
            return json.loads(r.content.decode('utf8'))['skuId']

        logging.error(f'Failed to create Product SKU [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def create_specification_group(cls, token, account, group):
        """Cria uma especificação para a variação
        - Parametros:
        ---
            - token: str
            - account: str
            - group: YamiSpecificationGroup"""
        
        r = cls._request('POST', f'catalog/specification_group?an={account}', token=token, data=json.dumps(group.__dict__))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Created Specification Group... [{r.status_code}] - {r.content.decode("utf-8")}')
            return json.loads(r.content.decode('utf8'))['specificationGroupId']

        logging.error(f'Failed to create Specification Group [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def create_specification_field(cls, token, account, field):
        """Cria uma especificação para a variação
        - Parametros:
        ---
            - token: str
            - account: str
            - field: YamiSpecificationField"""
        r = cls._request('POST', f'catalog/specification_field?an={account}', token=token, data=json.dumps(field.__dict__))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Created Specification Field... [{r.status_code}] - {r.content.decode("utf-8")}')
            return json.loads(r.content.decode('utf8'))['fieldId']

        logging.error(f'Failed to create Specification Field [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def create_variation_specification(cls, token, account, variationId, specification):
        """Cria uma especificação para a variação
        - Parametros:
        ---
            - token: str
            - account: str
            - variantionId: int
            - specification: YamiProductSpecification"""
        specs = []
        for i in specification:
            specs.append(i.__dict__)

        r = cls._request('PUT', f'catalog/sku_specification/{variationId}?an={account}', token=token, data=json.dumps(specs))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Created Product SKU Specification... [{r.status_code}] - {r.content.decode("utf-8")}')
            return

        logging.error(f'Failed to create Product SKU Specification [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def create_variation_image(cls, token, account, variationId, images):
        """Cria uma imagem para a variação
        - Parametros:
        ---
            - token: str
            - account: str
            - variantionId: int
            - specification: YamiProductSpecification"""
        dictImages = []
        for i in images:
            dictImages.append(i.__dict__)

        r = cls._request('PUT', f'catalog/sku_images/{variationId}?an={account}', token=token, data=json.dumps(dictImages))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Created Product SKU Image... [{r.status_code}] - {r.content.decode("utf-8")}')
            return

        logging.error(f'Failed to create Product SKU Image [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def create_variation_inventory(cls, token, account, warehouseId, variationId, inventory):
        """Atualiza o estoque da variação do produto
        - Parametros:
        ---
            - token: str
            - account: str
            - warehouseId: int
            - variationId: int
            - inventory: YamiInvetory"""
        
        r = cls._request('PUT', f'catalog/inventory/{variationId}/{warehouseId}?an={account}', token=token, data=json.dumps(inventory.__dict__))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Created Product SKU Inventory... [{r.status_code}] - {r.content.decode("utf-8")}')
            return json.loads(r.content.decode('utf8'))['skuId']

        logging.error(f'Failed to create Product SKU Inventory [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def create_variation_price(cls, token, account, variationId, price):
        """Atualiza o preço da variação do Produto
        - Parametros:
        ---
            - token: str
            - account: str
            - variationId: int
            - price: YamiPrice"""
        
        r = cls._request('PUT', f'catalog/price/{variationId}?an={account}', token=token, data=json.dumps(price.__dict__))

        if r.status_code in [ 200, 201 ]:
            logging.info(f'Created Product SKU Price... [{r.status_code}] - {r.content.decode("utf-8")}')
            return json.loads(r.content.decode('utf8'))['skuId']

        logging.error(f'Failed to create Product SKU Price [{r.status_code}] - {r.content.decode("utf-8")}')

    @classmethod
    def get_skus(cls, token, account):
        """Retorna todos os SKUs em um dicionário

        Ex.: print(YamiController.get_skus(yamiToken, account))
        - Parametros:
        ---
            - token: str
            - account: str"""
        
        page = 1
        skus = []
        yami_skus = None

        while yami_skus != []:
            r = cls._request('GET', f'catalog/skus?an={account}&page={page}', token=token)
            yami_skus = r.json()['skus']
            skus.extend(yami_skus)
            page += 1

            if r.status_code in [ 200, 201 ]:
                logging.info(f'Success to get all SKU [{r.status_code}]')
            else:
                logging.error(f'Failed to get all SKU [{r.status_code}]')
                
        return skus


    @classmethod
    def _request(cls,method: str , endpoint: str, token: str, data: str = None, extra_headers: dict = None):

        headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = f'Bearer {token}'
        
        if extra_headers:
            headers = { **headers, **extra_headers}

        return requests.request(method, f'{cls.url}/{endpoint}', headers=headers, data=data, timeout=cls.timeout)
