import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

from napplib.b2w.models.product import Product
from napplib.b2w.models.order import BillingAddress
from napplib.b2w.models.order import Payment
from napplib.b2w.models.order import Customer
from napplib.b2w.models.order import Status
from napplib.b2w.models.order import ShippingAddress
from napplib.b2w.models.order import Item
from napplib.b2w.models.order import Invoice
from napplib.b2w.models.order import Order

class B2WController:
	@classmethod
	def find_products(self, x_user_email='', x_api_key='', x_accountmanager_key='', hub_products=''):
		# create headers
		headers = {
			'x-user-email': x_user_email,
			'x-api-key': x_api_key,
			'x-accountmanager-key': x_accountmanager_key,
			'accept': "application/json;charset=UTF-8",
			'content-type': "application/json"
		}

		# loop in all napp hub products
		for product in hub_products:
			# get ean from napp hub
			ean = product.codeEan['String']

			# do request on skyhub to find this ean
			r = requests.get(f'https://api.skyhub.com.br/products?filters%5Bsku%5D={ean}', headers=headers)

			# in skyhub GET ean return a total itens, we check this number to determinate if exists or not
			total = int(json.loads(r.content.decode('utf-8'))['total'])

			# create variations
			#TODO

			# create specifications
			specifications = []
			variation_attributes = []
			if product.attributes:
				for hub_attribute in product.attributes:
					attribute = dict(
						key=str(hub_attribute['name']),
						value=hub_attribute['values'][0]['value']
					)
					variation_attributes.append(hub_attribute['name'])
					specifications.append(attribute)

			# create categories
			categories = []
			if product.categories:
				for hub_categorie in product.categories:
					categorie = dict(
						code=str(hub_categorie['id']),
						name=hub_categorie['name']
					)
					categories.append(categorie)

			# create b2w product object based on napphub
			b2w_product = Product(
				sku=product.skuErp,
				name=product.name,
				description=product.description,
				status=product.active,
				removed=False,
				qty=product.storeProduct.stockQuantity,
				price=product.storeProduct.salePrice,
				promotional_price=product.storeProduct.listPrice,
				cost=None,
				weight=product.storeProduct.weight['Float64'],
				height=product.storeProduct.height['Float64'],
				width=product.storeProduct.width['Float64'],
				length=product.storeProduct.length['Float64'],
				brand=product.productBrandName['String'],
				ean=ean,
				nbm=product.NBMOrigin,
				categories=categories,
				images=[product.mainImageURL['String']],
				specifications=specifications,
				variations=[],
				variation_attributes=variation_attributes
			)

			# check total
			if total != 0:
				# Product exists we need to update only stock and price
				payload = dict(
					product = dict(
						qty = b2w_product.qty,
						price = b2w_product.price
					)
				)

				# create payload
				payload = json.dumps(payload, ensure_ascii=False)

				# do request on b2w products
				r = requests.put(f'https://api.skyhub.com.br/products/{ean}', headers=headers, data=payload)

				# log and check request status
				if r.status_code == 204:
					logging.info(f'[HubController] EAN <{ean}> já existe no SkyHUB. [Atualizando Estoque/Preço]: Success!')
				else:
					logging.info(f'[HubController] Falha ao atualizar EAN <{ean}>. [Status]: {r.status_code}:{r.content}')
			else:
				# create payload with products
				payload = dict(product = b2w_product.__dict__)
				payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')

				# do request on products
				r = requests.post('https://api.skyhub.com.br/products', headers=headers, data=payload)
				logging.info(f'[HubController] EAN <{ean}> não existe no SkyHUB. [Criando]: {r.status_code}')

				# check response
				if r.status_code != 201:
					logging.info(f'[HubController] Falha ao criar EAN <{ean}>. [Status]: {r.status_code}:{r.content.decode("utf-8")}')

	@classmethod
	def delete_queue_orders(self, x_user_email='', x_api_key='', x_accountmanager_key='', mapped_orders=''):
		# create headers
		headers = dict()
		headers['Accept'] = 'application/json;charset=UTF-8'
		headers['Content-Type'] = 'application/json'
		headers['X-User-Email'] = x_user_email
		headers['x-Api-Key'] = x_api_key
		headers['x-accountmanager-key'] = x_accountmanager_key

		# do request on queue
		for order in mapped_orders:
			# get order id
			orderId = order['orderForeignId']['String']

			# delete order from queue
			r = requests.delete(f'https://api.skyhub.com.br/queues/orders/{orderId}', headers=headers)

			if r.status_code == 204:
				# log
				logging.info(f'[HubController] Deletando Ordem <{orderId}> da fila do SkyHUB. [Status]: {r.status_code}:{r.content}')

	@classmethod
	def get_queue_orders(self, x_user_email='', x_api_key='', x_accountmanager_key=''):
		# create headers
		headers = dict()
		headers['Accept'] = 'application/json;charset=UTF-8'
		headers['Content-Type'] = 'application/json'
		headers['X-User-Email'] = x_user_email
		headers['x-Api-Key'] = x_api_key
		headers['x-accountmanager-key'] = x_accountmanager_key

		# do request on queue
		r = requests.get('https://api.skyhub.com.br/queues/orders', headers=headers)

		# queue empty
		if not r.content:
			logging.info('[HubController] Fila do SkyHUB de Ordens vazia.')
			return None

		# get orders on queue
		b2w_orders = []
		b2w_order = b2w_orders.append(json.loads(r.content.decode('utf-8')))

		# check total
		if len(b2w_orders) == 0:
			logging.info('[HubController] SkyHUB sem Ordens de Venda.')
			return None

		# create orders array
		orders = []

		# loop in all b2w orders on queue
		for b2w_order in b2w_orders:
			# create varuables
			billing_address = dict()
			payments = []
			customer = dict()
			status = dict()
			shipping_address = dict()
			items = []
			invoices = []

			# create billing address
			if b2w_order['billing_address']:
				billing_address = BillingAddress(
					street=b2w_order['billing_address']['street'],
					region=b2w_order['billing_address']['region'],
					reference=b2w_order['billing_address']['reference'],
					detail=b2w_order['billing_address']['detail'],
					postcode=b2w_order['billing_address']['postcode'],
					phone=b2w_order['billing_address']['phone'],
					number=b2w_order['billing_address']['number'],
					neighborhood=b2w_order['billing_address']['neighborhood'],
					full_name=b2w_order['billing_address']['full_name'],
					country=b2w_order['billing_address']['country'],
					city=b2w_order['billing_address']['city'])
				billing_address = billing_address.__dict__

			# create payments
			if b2w_order['payments'] and len(b2w_order['payments']) > 0:
				for pay in b2w_order['payments']:
					payment = Payment(
						value=pay['value'],
						transaction_date=pay['transaction_date'],
						status=pay['status'],
						type_integration=pay['sefaz']['type_integration'],
						payment_indicator=pay['sefaz']['payment_indicator'],
						name_payment=pay['sefaz']['name_payment'],
						name_card_issuer=pay['sefaz']['name_card_issuer'],
						id_payment=pay['sefaz']['id_payment'],
						id_card_issuer=pay['sefaz']['id_card_issuer'],
						parcels=pay['parcels'],
						method=pay['method'],
						description=pay['description'],
						card_issuer=pay['card_issuer'],
						autorization_id=pay['autorization_id'])
					payment = payment.__dict__
					payments.append(payment)

			# create customer
			if b2w_order['customer']:
				customer = Customer(
					vat_number=b2w_order['customer']['vat_number'],
					phones=b2w_order['customer']['phones'],
					name=b2w_order['customer']['name'],
					gender=b2w_order['customer']['gender'],
					email=b2w_order['customer']['email'],
					date_of_birth=b2w_order['customer']['date_of_birth'])
				customer = customer.__dict__

			# create status
			if b2w_order['status']:
				status = Status(
					_type=b2w_order['status']['type'],
					label=b2w_order['status']['label'],
					code=b2w_order['status']['code'])
				status = status.__dict__

			# create shipping address
			if b2w_order['shipping_address']:
				shipping_address = ShippingAddress(
					street=b2w_order['shipping_address']['street'],
					region=b2w_order['shipping_address']['region'],
					reference=b2w_order['shipping_address']['reference'],
					detail= b2w_order['shipping_address']['detail'],
					postcode=b2w_order['shipping_address']['postcode'],
					phone=b2w_order['shipping_address']['phone'],
					number=b2w_order['shipping_address']['number'],
					neighborhood=b2w_order['shipping_address']['neighborhood'],
					full_name=b2w_order['shipping_address']['full_name'],
					country=b2w_order['shipping_address']['country'],
					city=b2w_order['shipping_address']['city'])
				shipping_address = shipping_address.__dict__

			# create items
			if b2w_order['items'] and len(b2w_order['items']) > 0:
				for b2w_item in  b2w_order['items']:
					item = Item(
						special_price=b2w_item['special_price'],
						shipping_cost=b2w_item['shipping_cost'],
						qty=b2w_item['qty'],
						product_id=b2w_item['product_id'],
						original_price=b2w_item['original_price'],
						name=b2w_item['name'],
						gift_wrap=b2w_item['gift_wrap'])
					item = item.__dict__
					items.append(item)

			# create invoices
			if b2w_order['invoices'] and len(b2w_order['invoices']) > 0:
				for b2w_invoice in  b2w_order['invoices']:
					invoice = Invoice(
						number=b2w_invoice['number'],
						key=b2w_invoice['key'],
						line=b2w_invoice['line'],
						issue_date=b2w_invoice['issue_date'],
						volume_qty=b2w_invoice['volume_qty'])
					invoice = invoice.__dict__
					invoices.append(invoice)

			# create order
			order = Order(
				code=b2w_order['code'],
				billing_address=billing_address,
				invoices=invoices,
				payments=payments,
				seller_shipping_cost=b2w_order['seller_shipping_cost'],
				updated_at=b2w_order['updated_at'],
				customer=customer,
				status=status,
				placed_at=b2w_order['placed_at'],
				channel=b2w_order['channel'],
				shipments=b2w_order['shipments'],
				approved_date=b2w_order['approved_date'],
				shipping_address=shipping_address,
				shipping_cost=b2w_order['shipping_cost'],
				estimated_delivery=b2w_order['estimated_delivery'],
				discount=b2w_order['discount'],
				shipping_method=b2w_order['shipping_method'],
				delivered_date=b2w_order['delivered_date'],
				items=items,
				shipping_carrier=b2w_order['shipping_carrier'],
				shipped_date=b2w_order['shipped_date'],
				total_ordered=b2w_order['total_ordered'])
			order = json.dumps(order.__dict__, ensure_ascii=False)

			# append to orders
			orders.append(order)

		# return
		return orders