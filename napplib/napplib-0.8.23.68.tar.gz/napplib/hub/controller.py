import requests, json, datetime, sys, logging
from .utils import Utils
from .models.product import Product
from .models.product import ProductBrand
from .models.product import ProductCategorie
from .models.product import Attribute
from .models.product import AttributeValue
from .models.product import StoreProduct
from .models.product import Categorie
from .models.product import CategorieChild
from .models.product import MarketplaceCategory
from .models.product import StoreProductMarketplace
from .models.order import OrderProductPackageDimensions
from .models.order import OrderProduct
from .models.order import OrderAddress
from .models.order import OrderPayment
from .models.order import OrderCustomerAddress
from .models.order import OrderCustomer
from .models.order import OrderShippingAddress
from .models.order import OrderShippingItem
from .models.order import OrderShipping
from .models.order import InvoiceItem
from .models.order import Invoice
from .models.order import Order

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

class HubController:
	@classmethod
	def authenticate(self, server_url='', user='', passwd=''):
		# create headers
		headers = dict()
		headers['Content-Type'] = 'application/json'

		# authenticate payload
		payload = dict()
		payload['username'] = user
		payload['password'] = passwd

		# do login request
		r = requests.post(f'{server_url}/signin/', headers=headers, data=json.dumps(payload))

		# catch error
		if r.status_code != 200:
			raise Exception(f'Failed to login on NappHUB...try again... {r.content.decode("utf-8")}')

		# get and return token
		token = json.loads(r.content.decode('utf8'))['token']
		return token

	@classmethod
	def get_all_attributes(self, server_url='', token=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# do request
		r = requests.get(f'{server_url}/attributes/', headers=headers, timeout=60)
		r = r.content.decode('utf-8')

		# create products object
		attributes = None

		# check if exists products on this server
		if r and r != 'null':
			attributes = json.loads(r)

		# return
		return attributes

	@classmethod
	def get_marketplace_categories_by_mkt(self, server_url='', token='', marketplace_id=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# do request
		r = requests.get(f'{server_url}/marketplaceCategoriesByMarketplace/{marketplace_id}', headers=headers)
		r = r.content.decode('utf-8')

		# create products object
		product = None

		# check if exists marketplaceCategories on this server
		if r and r != 'null':
			product = json.loads(r)

		# return
		return product

	@classmethod
	def get_product_by_id(self, server_url='', token='', product_id=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# do request
		r = requests.get(f'{server_url}/products/{product_id}', headers=headers, timeout=60)
		r = r.content.decode('utf-8')

		# create products object
		product = None

		# check if exists products on this server
		if r and r != 'null':
			product = json.loads(r)

		# return
		return product

	@classmethod
	def get_products_pagination(self, server_url='', token=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		products = []
		url = "/products/"

		count = 0
		LIMIT = 150
		params = {
			"offset": count,
			"limit": LIMIT
		}

		response = requests.get(
			f"{server_url}{url}",
			headers=headers,
			params=params
		)

		total = json.loads(response.content)['total']
		if total == 0:
			logging.info("/products/ is empty.")
			return []

		products.extend(json.loads(response.content)['data'])

		pages = int(total / LIMIT)
		if pages == 0:
			return products

		for i in range(0, pages, 1):
			count += LIMIT

			params["offset"] = count

			response = requests.get(
				f"{server_url}{url}",
				headers=headers,
				params=params
			)

			products.extend(json.loads(response.content)['data'])

		return products

	@classmethod
	def get_all_products(self, server_url='', token='', offset=0, limit=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		if limit != '':
			r = requests.get(f'{server_url}/products/', headers=headers, params={'offset': offset , 'limit': limit}, timeout=180)
			r = r.content.decode('utf-8')

		else:
			r = requests.get(f'{server_url}/products/', headers=headers, timeout=180)
			r = r.content.decode('utf-8')

		# create products object
		products = None

		# check if exists products on this server
		if r and r != 'null':
			products = json.loads(r)

		# return
		return products

	@classmethod
	def check_store_products_marketplace_status(self, server_url='', token='', status='', marketplaceId=0, storeId=0):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		response = None

		if status == 'pending_register_product':
			r = requests.get(f'{server_url}/storeProductsMarketplace/?marketplaceId={marketplaceId}&storeId={storeId}&statusProcessing={status}', headers=headers)
			r = r.json()

			response = r['data']

		elif status == 'done':
			r = requests.get(f'{server_url}/storeProductsMarketplace/?marketplaceId={marketplaceId}&storeId={storeId}&statusProcessing={status}', headers=headers)
			r = r.json()

			response = r['data']

		return response

	@classmethod
	def check_store_products_marketplace_status_pagination(self, server_url='', token='', status='', marketplaceId=0, storeId=0):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		store_products_marketplace_all = []

		offset = 0
		limit = 500

		response = None
		if status == 'pending_register_product':
			response = requests.get(
				f'{server_url}/storeProductsMarketplace/?marketplaceId={marketplaceId}&storeId={storeId}&statusProcessing={status}&offset={offset}&limit={limit}',
				headers=headers)

		elif status == 'done':
			response = requests.get(
				f'{server_url}/storeProductsMarketplace/?marketplaceId={marketplaceId}&storeId={storeId}&statusProcessing={status}&offset={offset}&limit={limit}',
				headers=headers)

		if not response:
			raise Exception(f"Erro ao retornar os storeProductMarketplace | status: {status}")
		if response.status_code != 200 and response.status_code != 201:
			raise Exception(f"Erro ao retornar os storeProductMarketplace: {response.status_code}")

		total = json.loads(response.content)['total']
		if total == 0:
			logging.info(f"/storeProductsMarketplace/ status: {status} is empty.")
			return []

		store_products_marketplace_all.extend(json.loads(response.content)['data'])

		pages = int(total / limit)
		if pages == 0:
			return store_products_marketplace_all

		for i in range(pages):
			offset += limit

			response = None
			if status == 'pending_register_product':
				response = requests.get(
					f'{server_url}/storeProductsMarketplace/?marketplaceId={marketplaceId}&storeId={storeId}&statusProcessing={status}&offset={offset}&limit={limit}',
					headers=headers)
			elif status == 'done':
				response = requests.get(
					f'{server_url}/storeProductsMarketplace/?marketplaceId={marketplaceId}&storeId={storeId}&statusProcessing={status}&offset={offset}&limit={limit}',
					headers=headers)

			if not response:
				raise Exception(f"Erro ao retornar os storeProductMarketplace | status: {status}")
			if response.status_code != 200 and response.status_code != 201:
				raise Exception(f"Erro ao retornar os storeProductMarketplace: {response.status_code}")

			store_products_marketplace_all.extend(json.loads(response.content)['data'])

		return store_products_marketplace_all


	@classmethod
	def get_store_products_pagination(self, server_url='', token='', store_id=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		store_products_all = []
		url = "/storeProducts/"

		if store_id:
			url = f'/storeProductsByStore/{store_id}'

		count = 0
		LIMIT = 200
		params = {
			"start": count,
			"end": LIMIT
		}

		response = requests.get(
			f"{server_url}{url}",
			headers=headers,
			params=params
		)
		total = json.loads(response.content)['total']
		if total == 0:
			logging.info("/storeProducts/ is empty.")
			return []

		store_products_all.extend(json.loads(response.content)['data'])

		pages = int(total / LIMIT)
		if pages == 0:
			return store_products_all

		for i in range(0, pages, 1):
			count += LIMIT

			params["start"] = count

			response = requests.get(
				f"{server_url}{url}",
				headers=headers,
				params=params
			)

			store_products_all.extend(json.loads(response.content)['data'])

		return store_products_all

	@classmethod
	def get_all_store_products(self, server_url='', token='', store_id=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# do request
		r = requests.get(f'{server_url}/storeProductsByStore/{store_id}', headers=headers, timeout=180)
		r = r.content.decode('utf-8')

		# create products object
		store_products = None

		# check if exists products on this server
		if r and r != 'null':
			store_products = json.loads(r)

		# return
		return store_products

	@classmethod
	def get_product_by_ean(self, server_url='', token='', ean=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# do request
		r = requests.get(f'{server_url}/productsByEan/?ean={ean}', headers=headers, timeout=60)
		r = r.content.decode('utf-8')

		# create id object
		product = None

		# find store product
		if r and r != 'null':
			product = json.loads(r)

		# return
		return product

	@classmethod
	def get_store_product_by_id(self, server_url='', token='', id='', store_id=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# do request
		r = requests.get(f'{server_url}/storeProducts/{id}', headers=headers)
		r = r.content.decode('utf-8')

		# create id object
		store_product = None

		# find store product
		if r and r != 'null':
			store_product = json.loads(r)

		# return
		return store_product

	@classmethod
	def get_store_product_by_erpCode(self, server_url='', token='', erp_code='', store_id=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# do request
		r = requests.get(f'{server_url}/storeProductsByErpCodeAndStore/{erp_code}/{store_id}', headers=headers, timeout=60)
		r = r.content.decode('utf-8')

		# create id object
		store_product = None

		# find store product
		if r and r != 'null':
			store_product = json.loads(r)

		# return
		return store_product

	@classmethod
	def get_store_product_by_productCodeOrEan(self, server_url='', token='', store_id='', product_code='', ean=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# do request
		r = None
		if product_code != '':
			r = requests.get(f'{server_url}/storeProducts/', headers=headers, params={'storeId': store_id, 'productCode': product_code})
		elif ean != '':
			r = requests.get(f'{server_url}/storeProducts/', headers=headers, params={'storeId': store_id, 'ean': ean})
		r = r.content.decode('utf-8')

		# create object
		store_product = None

		# find store product
		if r and json.loads(r)['data'] != 'null':
			store_product = json.loads(r)['data']

		# return
		return store_product

	@classmethod
	def get_store_product_marketplace(self, server_url='', token='', marketplace_id='', store_id='', store_product_id=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		r = requests.get(f'{server_url}/storeProductsMarketplace/?marketplaceId={marketplace_id}&storeId={store_id}&storeProductId={store_product_id}', headers=headers, timeout=60)
		r = r.content.decode('utf-8')

		store_product_marketplace = None

		# find store product marketplace
		if r != None and r != 'null':
			store_product_marketplace = json.loads(r)['data']

		# return
		return store_product_marketplace

	@classmethod
	def create_store_product_marketplace(self, server_url, token, store_product_marketplace=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# create 'store product marketplace' payload
		payload_store_product_marketplace = json.dumps(store_product_marketplace.__dict__, ensure_ascii=True)

		# do request on POST/storeProductsMarketplace
		r = requests.post(f'{server_url}/storeProductsMarketplace/', headers=headers, data=payload_store_product_marketplace)
		logging.info(f'Criando o inventário de marketplace... [{"sucesso ao registrar o inventário (200)" if r.status_code == 200 else r.status_code}] - {r.content.decode("utf-8")}')

		return r.status_code

	@classmethod
	def update_store_product_marketplace(self, server_url, token, store_product_marketplace=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# create 'store product marketplace' payload
		payload_store_product_marketplace = json.dumps(store_product_marketplace.__dict__, ensure_ascii=True)

		# do request on POST/storeProductsMarketplace
		r = requests.put(f'{server_url}/storeProductsMarketplace/', headers=headers, data=payload_store_product_marketplace)
		logging.info(f'Atualizando o inventário de marketplace... [{"sucesso ao atualizar o inventário (200)" if r.status_code == 200 else r.status_code}] - {r.content.decode("utf-8")}')

		return r.status_code

	@classmethod
	def update_store_product(self, server_url, token, inventory, store_product_id, product_id):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# set hub product ID on object store product
		inventory.id = store_product_id
		inventory.productId = Utils.create_values(product_id, 'Int64')

		# create store product update payload
		payload_store_product = json.dumps(inventory.__dict__, ensure_ascii=True)

		# do request on PUT/storeProducts
		r = requests.put(f'{server_url}/storeProducts/', headers=headers, data=payload_store_product)

		# log
		logging.info(f'Atualizando o inventário da loja... [{"sucesso ao atualizar o inventário (200)" if r.status_code == 200 else r.status_code}] - {r.text}')

	@classmethod
	def create_store_product(self, server_url, token, inventory):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# create store product payload
		payload_store_product = inventory.__dict__

		# create 'store product' payload
		payload_store_product = json.dumps(payload_store_product, ensure_ascii=True)

		try:
			# do request on POST/storeProducts
			r = requests.post(f'{server_url}/storeProducts/', headers=headers, data=payload_store_product)
			logging.info(f'Criando o inventário da loja... [{"sucesso ao registrar o inventário (200)" if r.status_code == 200 else r.status_code}] - {r.content.decode("utf-8")}')

			r = r.json()
		except Exception as e:
			logging.info(f'Failed to create a store_product... {e}')

			r = None
			pass

		return r

	@classmethod
	def update_product(self, server_url, token, id_product, product):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# create product update payload
		product = product.__dict__
		product.update({"id": int(id_product)})

		payload_product = json.dumps(product, ensure_ascii=True)

		# do request on PUT/storeProducts
		r = requests.put(f'{server_url}/products/', headers=headers, data=payload_product)

		# log
		logging.info(f'Updating Products... ID <{product["id"]}>... {r.status_code}:{r.content.decode("utf-8").strip()}')

		return r

	@classmethod
	def create_category(self, server_url, token, categories=[]):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# Create request object
		r = None

		# Create payload_category
		payload_category = json.dumps(categories.__dict__, ensure_ascii=True)

		response = requests.post(f'{server_url}/categories/', headers=headers, data=payload_category)

		return response

	@classmethod
	def create_category_child(self, server_url, token, child_categories=[]):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# Create request object
		r = None

		# Create payload_category
		payload_child_category = json.dumps(child_categories.__dict__, ensure_ascii=True)

		r = requests.post(f'{server_url}/categories/', headers=headers, data=payload_child_category)

		r.status_code

	@classmethod
	def create_marketplace_category(self, server_url, token, marketplace_categories=[]):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# Create request object
		r = None

		# Create payload_category
		payload_marketpace_category = json.dumps(marketplace_categories.__dict__, ensure_ascii=True)

		r = requests.post(f'{server_url}/marketplaceCategories/', headers=headers, data=payload_marketpace_category)

		return r.status_code

	@classmethod
	def create_attribute(self, server_url, token, attribute=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload_attribute = json.dumps(attribute.__dict__, ensure_ascii=True)

		response = requests.post(f'{server_url}/attributes/', headers=headers, data=payload_attribute)

		return response

	@classmethod
	def create_attribute_value(self, server_url, token, attribute_value=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload_attribute_value = json.dumps(attribute_value.__dict__, ensure_ascii=True)

		response = requests.post(f'{server_url}/attributeValues/', headers=headers, data=payload_attribute_value)

		return response

	@classmethod
	def product_attribute(self, server_url, token, attributeName='', attributeValue='', eanProduct='', productCode='', storeId=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		if attributeName:
			response = requests.get(f'{server_url}/attributesByName/?name={attributeName}', headers=headers)
			response = response.json()

			if response:
				logging.info(f"attributeName alredy exists: [{attributeName}]")
			else:
				logging.info(f"attributeName not exists: [{attributeName}], uploading...")

				attribute = Attribute(name=attributeName)

				response_attr = self.create_attribute(
					server_url=server_url,
					token=token,
					attribute=attribute
				)

				if response_attr.status_code == 200:
					logging.info(f"sucessfull create attribute name: [{attributeName}] - {response_attr.text}")

		if attributeValue:
			response = requests.get(f'{server_url}/attributesByNameAndValue/?name={attributeName}&value={attributeValue}', headers=headers)
			response = response.json()

			if response:
				logging.info(f"attributeValue already exists: [{attributeName} - {attributeValue}]")
			else:
				logging.info(f"attributeValue not exists: [{attributeName} - {attributeValue}], uploading...")

				attribute_val = AttributeValue(
					name=attributeName,
					value=attributeValue
				)

				response_attr_vlr = self.create_attribute_value(
					server_url=server_url,
					token=token,
					attribute_value=attribute_val
				)

				if response_attr_vlr.status_code == 200:
					logging.info(f"sucessfull create attribute value: [{attributeName} - {attributeValue}] - {response_attr_vlr.text}")

		if eanProduct:
			codEan = dict()
			codEan['String'] = str(eanProduct)
			codEan['Valid'] = True

			prod = dict()
			prod['eanProduct'] = codEan

			attr = dict()
			attr['attributeName'] = str(attributeName)
			attr['attributeValue'] = str(attributeValue)

			body = dict()
			body['attribute'] = attr
			body['produto'] = prod

			r = requests.post(f'{server_url}/productAttributes/', headers=headers, data=json.dumps(body))

			if r.status_code == 200:
				logging.info(f"sucessfull create product attribute: [{eanProduct} - {attributeName} - {attributeValue}] - {r.text}")
			else:
				logging.error('error: [{}]'.format("attribute already exists in that product" if "uk_idx_product_attribute" in r.text.strip() else r.text.strip()))
				# logging.error(f"error: {r.status_code} - {r.text} -  at create product attribute: [{eanProduct} - {attributeName} - {attributeValue}]")

		if productCode and storeId:
			code = dict()
			code['String'] = str(productCode)
			code['Valid'] = True

			store = dict()
			store['Int64'] = int(storeId)
			store['Valid'] = True

			prod = dict()
			prod['productCode'] = code
			prod['storeId'] = store

			attr = dict()
			attr['attributeName'] = str(attributeName)
			attr['attributeValue'] = str(attributeValue)

			body = dict()
			body['attribute'] = attr
			body['produto'] = prod

			r = requests.post(f'{server_url}/productAttributes/', headers=headers, data=json.dumps(body))

			if r.status_code == 200:
				logging.info(f"sucessfull create product attribute: [{productCode} - {attributeName} - {attributeValue}] - {r.text}")
			else:
				logging.error('error: [{}]'.format("attribute already exists in that product" if "uk_idx_product_attribute" in r.text.strip() else r.text.strip()))
				# logging.error(f"error: {r.status_code} - {r.text} -  at create product attribute: [{productCode} - {attributeName} - {attributeValue}]")

	@classmethod
	def check_category(self, server_url, token, category='', child=False):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		logging.info('checando a categoria - [{}]'.format(category))

		# baixa as marcas de produtos já cadastradas no NappHub
		r = requests.get(f'{server_url}/categoriesByName/?name={category}', headers=headers)
		categ_hub = r.json()

		if categ_hub and str(categ_hub[0]['name']).strip() == str(category).strip():
			logging.info("categoria já está registrada no NappHub")
		else:
			logging.info("categoria não existe no hub, enviando...")

			categ_up = Categorie(name=category)

			response_categ = self.create_category(
				server_url=server_url,
				token=token,
				categories=categ_up
			)

			if response_categ.status_code == 200:
				logging.info(f"sucessfull create category: [{category}] - {response_categ.text}")
			else:
				logging.error(f"error: {response_categ.status_code} - {response_categ.text} create category: [{category}]")

	@classmethod
	def product_category(self, server_url, token, productCateg=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		category = productCateg.categoryName['String']

		if category:
			self.check_category(
				server_url=server_url,
				token=token,
				category=category
			)

			eanProduct = productCateg.eanProduct['String']
			productCode = productCateg.productCode['String']

			payload_product_categ = json.dumps(productCateg.__dict__, ensure_ascii=True)

			response = requests.post(f'{server_url}/productCategories/', headers=headers, data=payload_product_categ)

			if response.status_code == 200:
				logging.info(f"sucessfull create product categorie: [{category} - {eanProduct}/{productCode}]")
			else:
				logging.error(f"error {response.status_code} - {response.text} at created product categorie: [{category} - {eanProduct}/{productCode}]")

	@classmethod
	def check_brand(self, server_url, token, brand=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		logging.info('checando a marca - [{}]'.format(brand))

		# baixa as marcas de produtos já cadastradas no NappHub
		r = requests.get(f'{server_url}/productsBrandByName/?name={brand}', headers=headers)
		brand_hub = r.json()

		if brand_hub['description'] == str(brand).strip():
			logging.info("marca já está registrada no NappHub")

		else:
			logging.info("marca não existe no NappHub, enviando...")

			product_brand = ProductBrand(description=brand)
			payload_product_brand = json.dumps(product_brand.__dict__, ensure_ascii=True)

			response = requests.post(f'{server_url}/productsBrand/', headers=headers, data=payload_product_brand)

			if response.status_code == 200:
				logging.info('a marca: [{}] foi registrada com sucesso'.format(brand))
			else:
				logging.error('Erro ao registrar a marca [{} - code: {} - text: {}]'.format(brand, response.status_code, response.text))

	@classmethod
	def check_marketplace_inventory(self, server_url, token, inventory, marketplace_id=0, store_id=0, store_product_id=0, mkt_category=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		price_up = inventory.salePrice
		stock_up = inventory.stockQuantity

		if store_product_id:
			r = requests.get(f'{server_url}/storeProductsMarketplace/?marketplaceId={marketplace_id}&storeId={store_id}&storeProductId={store_product_id}', headers=headers)
			r = r.json()

			if r['data']:
				for x in r['data']:
					if x['storeProductId'] == store_product_id:
						logging.info("inventário de marketplace já existe")

						id_hub = r['data'][0]['id']
						status = r['data'][0]['statusProcessing']['String']
						price_hub = r['data'][0]['salePrice']['Float64']
						stock_hub = r['data'][0]['stockQuantity']['Float64']
						mktForeingid = r['data'][0]['marketplaceForeignId']['String']
						mktPartnerId = r['data'][0]['mktPartnerProductId']['Int64']

						if float(round(price_up,2)) != float(round(price_hub,2)) or int(stock_up) != int(stock_hub):

							logging.info("inventário de marketplace foi modificado, atualizando...")

							product_mkt = StoreProductMarketplace(
								id=id_hub,
								marketplaceId=marketplace_id,
								storeProductId=store_product_id,
								marketplaceForeignId=mktForeingid,
								mktPartnerProductId=mktPartnerId,
								active=True,
								listPrice=inventory.listPrice,
								salePrice=inventory.salePrice,
								stockQuantity=inventory.stockQuantity,
								marketplaceCategory=mkt_category,
								statusProcessing=status
							)

							self.update_store_product_marketplace(
								server_url=server_url,
								token=token,
								store_product_marketplace=product_mkt
							)

					else:
						logging.info("inventário de marketplace não existe, enviando...")

						product_mkt = StoreProductMarketplace(
							marketplaceId=marketplace_id,
							storeProductId=store_product_id,
							active=True,
							listPrice=inventory.listPrice,
							salePrice=inventory.salePrice,
							stockQuantity=inventory.stockQuantity,
							marketplaceCategory=mkt_category,
							statusProcessing='pending_register_product'
						)

						self.create_store_product_marketplace(
							server_url=server_url,
							token=token,
							store_product_marketplace=product_mkt
						)

	@classmethod
	def check_inventory(self, server_url, token, store_products=[], store_id=0, marketplace_id=0, mkt_category='', use_ean=False, use_sku=False, use_mkt=False):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# create arrays
		hub_products = []
		hub_products_not_found = []

		response = None

		for store_product in store_products:
			invetaryEan = store_product.eanProduct['String']
			invetaryCode = store_product.productCode['String']
			price_up = store_product.salePrice
			list_up = store_product.listPrice
			stock_up = store_product.stockQuantity

			# Check if use ean or sku to find product
			if use_ean:
				r = requests.get(f'{server_url}/storeProducts/?ean={invetaryEan}&storeId={store_id}', headers=headers)
				r = r.json()
			elif use_sku:
				r = requests.get(f'{server_url}/storeProducts/?productCode={invetaryCode}&storeId={store_id}', headers=headers)
				r = r.json()

			if r['data']:
				store_product_hub = r['data'][0]
				logging.info('inventário já existe')

				stock_hub = store_product_hub['stockQuantity']
				price_hub = store_product_hub['salePrice']
				list_hub = store_product_hub['listPrice']

				if int(stock_up) != int(stock_hub) or float(round(price_up,2)) != float(round(price_hub,2)) or float(round(list_up,2)) != float(round(list_hub,2)):

					logging.info('inventário foi modificado, atualizando...')

					self.update_store_product(
						server_url=server_url,
						token=token,
						inventory=store_product,
						store_product_id=store_product_hub['id'],
						product_id=store_product_hub['productId']['Int64']
					)

					store_product_id = store_product_hub['id']
				else:
					# não deixa atualizar store_products_marketplace
					store_product_id = 0

					# pra atualizar o marketplace, mesmo sem atualizar o store_product, use:
					# store_product_id = store_product_hub['id']
			else:
				logging.info('inventário não existe, enviando...')

				response = self.create_store_product(
					server_url=server_url,
					token=token,
					inventory=store_product
				)

				store_product_id = response

			if use_mkt:
				self.check_marketplace_inventory(
					server_url=server_url,
					token=token,
					store_product_id=store_product_id,
					marketplace_id=marketplace_id,
					store_id=store_id,
					mkt_category=mkt_category,
					inventory=store_product
				)

	@classmethod
	def create_product(self, server_url='', token='', store_id='', products=[], use_ean=False, use_sku=False):
		  # create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# create arrays
		hub_products = []
		hub_products_not_found = []

		response = None

		# loop in all integration produtcs
		for product in products:
			# create request object
			r = None

			# get product ids string,
			productEan = product.codeEan['String']
			productCode = product.productCode['String']

			# Check if use ean or sku to find product
			if use_ean:
				r = requests.get(f'{server_url}/productsByEan/?ean={productEan}', headers=headers)
			if use_sku:
				r = requests.get(f'{server_url}/productsByProductCode/?code={productCode}&storeId={store_id}', headers=headers)

			if r:
				# find hub product id based on integration product
				hub_product = json.loads(r.content.decode('utf-8'))
				hub_product_id = hub_product['id']
				hub_product_name = hub_product['name'] if 'name' in hub_product else ''
				hub_product_desc = hub_product['description'] if 'description' in hub_product else ''
				hub_product_parent = hub_product['parentId']['Int64']

				# check if product id exists on napp hub
				if hub_product_id != 0:
					# log
					logging.warning(f'Produto já existe no NappHub [<{productEan}>/<{productCode}>]')

					response = r

					# valida se mudou algo no produto, antes de chamar a função de update
					if str(hub_product_name) != str(product.name) or str(hub_product_desc) != str(product.description):

						product_update = Product(
							id=hub_product_id,
							parentId=hub_product_parent,
							productBrandName=hub_product['productBrandName']['String'],
							skuErp=hub_product['skuErp'] if 'skuErp' in hub_product else '',
							name=product.name,
							description=product.description,
							NBMOrigin=hub_product['NBMOrigin']['Int64'],
							warrantyTime=hub_product['warrantyTime']['Int64'],
							active=True,
							productCode=hub_product['productCode']['String'],
							storeId=hub_product['storeId']['Int64']
						)

						response = self.update_product(
							server_url=server_url,
							token=token,
							id_product=hub_product_id,
							product=product_update)

						logging.info(f"Produto foi modificado: <{productEan}>/<{productCode}>")
				else:
					# clear 'store products' from 'products' and create a new payload
					product = product.__dict__
					product.pop('storeProduct')

					# check exist's brand
					self.check_brand(server_url=server_url, token=token, brand=product['productBrandName']['String'])
					payload_product = json.dumps(product, ensure_ascii=True)

					# do request on POST products
					response = requests.post(f'{server_url}/products/', headers=headers, data=payload_product)
					logging.info(f'Criando o produto... [{"sucesso ao registrar o produto (200)" if response.status_code == 200 else response.status_code}] - {response.text}')

		return response

	@classmethod
	def create_products_and_store_products(self, server_url='', token='', store_id='', products=[], use_ean=False, use_sku=False, update_product=False, update_store_product=False):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# create arrays
		hub_products = []
		hub_products_not_found = []

		# loop in all integration produtcs
		for product in products:
			# create request object
			r = None

			# get product ids string
			productEan = product.productEan['String']
			productCode = product.productCode['String']

			# Check if use ean or sku to find product
			if use_ean:
				r = requests.get(f'{server_url}/productsByEan/?ean={productEan}', headers=headers)
			elif use_sku:
				r = requests.get(f'{server_url}/productsByProductCode/?code={productCode}&storeId={store_id}', headers=headers)

			# check if request exists
			if r:
				# find hub product id based on integration product
				hub_product = json.loads(r.content.decode('utf-8'))
				hub_product_id = hub_product['id']

				# check if product id exists on napp hub
				if hub_product_id != 0:
					# log
					logging.info(f'Code <{productEan}>/<{productCode}> exists on Napp HUB')

					# check update enabled
					if update_store_product:
						# find store product id
						store_product = self.get_store_product_by_erpCode(
							server_url=server_url,
							token=token,
							erpCode=productCode,
							store_id=store_id)

						# update if exists or create
						if store_product:
							self.update_store_product(
								server_url=server_url,
								token=token,
								product=product,
								store_product_id=store_product['id'],
								product_id=hub_product_id)
						else:
							self.create_store_product(
								server_url=server_url,
								token=token,
								product=product,
								product_id=hub_product_id)

					# update product
					if update_product:
						# set hub product id on object product
						product.id = hub_product_id

						# call
						self.update_product(
							server_url=server_url,
							token=token,
							product=product)
				else:
					# create store product payload
					payload_store_product = product.storeProduct.__dict__

					# clear 'store products' from 'products' and create a new payload
					product = product.__dict__
					product['storeProduct'] = None
					payload_product = json.dumps(product, ensure_ascii=True)

					# do request on POST products
					r = requests.post(f'{server_url}/products/', headers=headers, data=payload_product)
					logging.info(f'Creating product...{r.status_code} - {r.content.decode("utf-8")}')

					if r.status_code == 200:
						# get created product id
						product_id = int(r.content.decode('utf-8'))

						# call function
						self.create_store_product(
							server_url=server_url,
							token=token,
							product=product,
							product_id=product_id)

	@classmethod
	def find_parent_child_by_id(self, server_url='', token='', store_product=''):
		parent = None
		product = None

		product_id = store_product['productId']['Int64']
		product = self.get_product_by_id(server_url=server_url, token=token, product_id=product_id)

		if product and product['parentId']['Int64']:
			parent_id = product['parentId']['Int64']

			# get product parent object and append to list
			response_product = self.get_product_by_id(server_url=server_url, token=token, product_id=parent_id)

			if response_product:
				parent = response_product

		return parent, product

	@classmethod
	def find_parents_childs(self, server_url='', token='', store_products=''):
		# create arrays and tmp last parent id
		parents = []
		products = []
		count = 1
		qty = len(store_products)
		last_parent = 0

		# loop in all store products
		for store_product in store_products:
			try:
				logging.info(f'Identify parent and child from store product: {count}/{qty}')
				# get product ID and product object
				product_id = store_product['productId']
				product = self.get_product_by_id(server_url=server_url, token=token, product_id=product_id)

				if product:
					# append products to list and get parent ID
					products.append({'storeProduct': store_product, 'product': product})
					parent_id = product['parentId']['Int64']

					# check if parent id is different from last parent id check
					if parent_id != last_parent:
						# get product parent object and append to list
						parent = self.get_product_by_id(server_url=server_url, token=token, product_id=product['parentId']['Int64'])
						if parent:
							parents.append({'storeProduct': store_product, 'product': parent})
							# set latest parent id
							last_parent = parent_id
			except Exception as e:
				logging.info(f'Failed to identify parent and child... {e}')
				pass

			# count
			count += 1
		return parents, products

	@classmethod
	def get_order_by_foreign_id(self, server_url='', token='', orderForeignId='', storeId='', purchasedAt=''):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'
		params = {
			"foreignId": orderForeignId,
			"storeId": storeId,
			"purchasedAt": datetime.datetime.strftime(Utils.normalize_date(purchasedAt), "%Y-%m-%d")
		}

		url = f'{server_url}/orderByForeignId/'
		r = requests.get(url, headers=headers, params=params)
		r = r.content.decode('utf-8')
		r = json.loads(r)

		return r

	@classmethod
	def create_order(self, server_url='', token='', order=''):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload = json.dumps(order)
		r = requests.post(f'{server_url}/orders/', headers=headers, data=payload)
		msg = r.content.decode('utf-8')

		logging.info(f'Creating order {order.get("orderForeignId")["String"]}...{r.status_code} {msg}')

		return msg

	@classmethod
	def create_orders_list(self, server_url='', token='', orders_list=[]):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload = json.dumps(orders_list, ensure_ascii=True)
		r = requests.post(f'{server_url}/orders/?type=list', headers=headers, data=payload)
		count = 1
		while r.status_code != 200 and count < 3:
			logging.info(f" - Attempt {count}")
			r = requests.post(f'{server_url}/orders/?type=list', headers=headers, data=payload)
			logging.info(f'Creating order list - (attempt {count}) - {r.status_code}')
			count += 1

		logging.info(f'Creating order list...{r.status_code}')

		if r.status_code != 200:
			logging.info(f'Failed to send order list. Message: {r.content} - Payload: {payload}')

		r = r.content.decode('utf-8')
		return r

	@classmethod
	def update_order(self, server_url='', token='', order=''):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload = json.dumps(order)
		r = requests.put(f'{server_url}/orders/', headers=headers, data=payload)
		logging.info(f'Updating order {order.get("orderForeignId")["String"]}...{r.status_code}')

		r = r.content.decode('utf-8')
		return r

	@classmethod
	def get_order_invoices_pagination(self, server_url='', token=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		invoices = []
		url = "/invoices/"

		count = 0
		LIMIT = 500
		params = {
			"offset": count,
			"limit": LIMIT
		}

		response = requests.get(
			f"{server_url}{url}",
			headers=headers,
			params=params
		)

		total = json.loads(response.content)['total']
		if total == 0:
			logging.info("/invoices/ is empty.")
			return []

		invoices.extend(json.loads(response.content)['data'])

		pages = int(total / LIMIT)
		if pages == 0:
			return invoices

		for i in range(0, pages, 1):
			count += LIMIT

			params["offset"] = count

			response = requests.get(
				f"{server_url}{url}",
				headers=headers,
				params=params
			)

			invoices.extend(json.loads(response.content)['data'])

		return invoices

	@classmethod
	def create_order_invoice(self, server_url='', token='', invoice=''):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload = json.dumps(invoice)
		r = requests.post(f'{server_url}/invoices/', headers=headers, data=payload)
		response = r.content.decode('utf-8')
		logging.info(f'Creating invoice {invoice.get("orderId")}...{response}')
		return r

	@classmethod
	def get_order_shipping(self, server_url='', token=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		# do request
		r = requests.get(f'{server_url}/shippings/', headers=headers, timeout=180)
		r = r.content.decode('utf-8')

		# create shippings object
		shippings = None

		# check if exists shippings on this server
		if r and r != 'null':
			shippings = json.loads(r)

		# return
		return shippings

	@classmethod
	def create_order_shipping(self, server_url='', token='', shipping=''):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload = json.dumps(shipping)
		r = requests.post(f'{server_url}/shippings/', headers=headers, data=payload)
		response = r.content.decode('utf-8')
		logging.info(f'Creating shipping {shipping.get("orderId")}...{response}')
		return r

	@classmethod
	def update_order_shipping(self, server_url='', token='', shipping=''):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload = json.dumps(shipping)
		r = requests.put(f'{server_url}/orders/', headers=headers, data=payload)
		logging.info(f'Updating order {shipping.get("orderId")}...{r.status_code}')

		r = r.content.decode('utf-8')
		return r

	@classmethod
	def update_order_payment(self, server_url='', token='', payment=''):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload = json.dumps(payment)
		r = requests.put(f'{server_url}/payments/', headers=headers, data=payload)
		logging.info(f'Updating order {payment.get("orderId")}...{r.status_code}')

		# r = r.content.decode('utf-8')
		return r

	@classmethod
	def get_order_payments_pagination(self, server_url='', token=''):
		# create headers
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payments = []
		url = "/payments/"

		# count = 0
		# LIMIT = 500
		# params = {
		# 	"offset": count,
		# 	"limit": LIMIT
		# }

		response = requests.get(
			f"{server_url}{url}",
			headers=headers,
			#params=params
		)

		# total = json.loads(response.content)['total']
		# if total == 0:
		# 	logging.info("/payments/ is empty.")
		# 	return []

		payments.extend(json.loads(response.content)['data'])

		# pages = int(total / LIMIT)
		# if pages == 0:
		# 	return payments

		# for i in range(0, pages, 1):
		# 	count += LIMIT

		# 	params["offset"] = count

		# 	response = requests.get(
		# 		f"{server_url}{url}",
		# 		headers=headers,
		# 		params=params
		# 	)

		# 	payments.extend(json.loads(response.content)['data'])

		return payments

	@classmethod
	def create_order_payment(self, server_url='', token='', payment=''):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload = json.dumps(payment)
		r = requests.post(f'{server_url}/payments/', headers=headers, data=payload)
		response = r.content.decode('utf-8')
		logging.info(f'Creating payment {payment.get("orderId")}...{response}')

		return r

	@classmethod
	def get_customer_by_document(self, server_url='', token='', document=''):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		r = requests.get(f'{server_url}/customersByDocument/?document={document}', headers=headers)
		r = r.content.decode('utf-8')

		customer = None
		if r != 'null':
			customer = json.loads(r)

		return customer

	@classmethod
	def create_customer(self, server_url='', token='', customer=''):
		headers = dict()
		headers['Authorization'] = f'Bearer {token}'

		payload = json.dumps(customer)

		r = requests.post(f'{server_url}/customers/', headers=headers, data=payload)
		r = r.content.decode('utf-8')

		logging.info(f'Creating customer {customer.get("document")}...{r}')

		return r
