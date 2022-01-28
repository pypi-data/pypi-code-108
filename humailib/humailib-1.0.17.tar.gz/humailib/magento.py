from abc import abstractmethod
import requests
import rauth
from rauth import OAuth1Service
import json
import datetime
import sys

import numpy as np
import pandas as pd

import humailib.utils as hu

class MagentoREST:
    
    def __init__(self, access_token, base_url):
        
        self.access_token = access_token
        #self.base_url = 'https://24fashion.nl/rest/default/V1/'
        self.base_url = base_url
                 
    def _get_uri(self, endpoint):
        
        return self.base_url + endpoint
  
    def post(self, endpoint, params, verbose=False):

        url = self._get_uri(endpoint)
        response = requests.post(url, params=params, headers={'Authorization':'Bearer {}'.format(self.access_token)})
        if verbose:
            print("REST URI: {}".format(url))
            print("Response code: {}".format(response.status_code))
            print("Response: {}".format(response.text))

        return response
    
    def put(self, endpoint, params, verbose=False):
        
        url = self._get_uri(endpoint)
        response = requests.put(url, params=params, headers={'Authorization':'Bearer {}'.format(self.access_token)})
        if verbose:
            print("REST URI: {}".format(url))
            print("Response code: {}".format(response.status_code))
            print("Response: {}".format(response.text))

        return response
    
    def get(self, endpoint, params=None, verbose=False):
        
        url = self._get_uri(endpoint)
        response = requests.get(url, params=params, headers={'Authorization':'Bearer {}'.format(self.access_token)})
        if verbose:
            print("REST URI: {}".format(url))
            print("Response code: {}".format(response.status_code))
            print("Response: {}".format(response.text))

        return response, response.json()
    
class MagentoOrdersExtract:
    
    def __init__(self, access_token, base_url):
        
        self.api = MagentoREST(access_token, base_url)
        
    def _extract_field(self, order, field_name):
        
        return order.get(field_name,'') # order[field_name] if field_name in order else ''
        
    def _extract_float(self, order, field_name):
        
        return order.get(field_name,np.nan)#order[field_name] if field_name in order else np.nan

    def _extract_array(self, customer, field_name):
        
        return customer.get(field_name,[''])#customer[field_name] if field_name in customer else ['']
    
    def extract(self, from_date, to_date, page_size = 1000, verbose=False):
        
        """
        Extract all orders between the dates [from_date, to_date)
        """
        
        order_rows = []
        item_rows = []
        
        try:
            params = {
                'searchCriteria[currentPage]':str(1), 
                'searchCriteria[pageSize]':str(1),
                'searchCriteria[filter_groups][0][filters][0][field]':'created_at',
                'searchCriteria[filter_groups][0][filters][0][value]':from_date.strftime('%Y-%m-%d %H:%M:%S'),
                'searchCriteria[filter_groups][0][filters][0][condition_type]':'gteq',
                'searchCriteria[filter_groups][1][filters][0][field]':'created_at',
                'searchCriteria[filter_groups][1][filters][0][value]':to_date.strftime('%Y-%m-%d %H:%M:%S'),
                'searchCriteria[filter_groups][1][filters][0][condition_type]':'lt'
            }
            response, orders = self.api.get('orders', params=params, verbose=False)
            to_id = orders['total_count']
            
            if verbose:
                print("Total number of orders {:,}".format(orders['total_count']))
        except:
            print("Unexpected error: " + sys.exc_info()[0])
        
        order_id = 1
        while order_id <= to_id:
                
            try:
                
                page = int(np.floor((order_id-1)/float(page_size))) + 1
                if verbose:
                    print("Requesting page {:,} of (orders from {:,} to {:,}, total={:,})".format(page, (page-1)*page_size, (page-1)*page_size + page_size, to_id))
                    
                params = {
                    'searchCriteria[currentPage]':str(page), 
                    'searchCriteria[pageSize]':str(page_size),
                    'searchCriteria[filter_groups][0][filters][0][field]':'created_at',
                    'searchCriteria[filter_groups][0][filters][0][value]':from_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'searchCriteria[filter_groups][0][filters][0][condition_type]':'gteq',
                    'searchCriteria[filter_groups][1][filters][0][field]':'created_at',
                    'searchCriteria[filter_groups][1][filters][0][value]':to_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'searchCriteria[filter_groups][1][filters][0][condition_type]':'lt'
                }
                order_id = page_size + order_id
                response, orders = self.api.get('orders', params=params, verbose=False)

                if (200 <= response.status_code <= 299) and 'items' in orders:
                  
                    for order in orders['items']:
                        
                        if 'items' in order and 'entity_id' in order and 'billing_address' in order:
                        
                            items = order['items']
                            billing = order['billing_address']
                            shipping = None
                            shipping_city = ''
                            shipping_country_id = ''
                            shipping_zip = ''
                            shipping_address = ''
                            if 'extension_attributes' in order:
                                if 'shipping_assignments' in order['extension_attributes']:
                                    shipping_data = order['extension_attributes']['shipping_assignments']
                                    if len(shipping_data) > 0:
                                        shipping_data = shipping_data[0]
                                        if 'shipping' in shipping_data:#
                                            if 'address' in shipping_data['shipping']:
                                                shipping = shipping_data['shipping']['address']
                            
                            entity_id = int( self._extract_field(order, 'entity_id') )
                            transaction_id = 'T'+str(entity_id)#hu.force_string(entity_id) # Force it to be a string

                            if True:
                                
                                #if verbose:
                                #    print("  Extracting order {}".format(transaction_id))

                                email = self._extract_field(order, 'customer_email')
                                firstname = self._extract_field(order, 'customer_firstname')
                                lastname = self._extract_field(order, 'customer_lastname')

                                billing_city = self._extract_field(billing, 'city')
                                billing_country_id = self._extract_field(billing, 'country_id')
                                billing_zip = self._extract_field(billing, 'postcode')
                                billing_address = ' '.join(self._extract_array(billing, 'street'))
                                if shipping is not None:
                                    shipping_city = self._extract_field(shipping, 'city')
                                    shipping_country_id = self._extract_field(shipping, 'country_id')
                                    shipping_zip = self._extract_field(shipping, 'postcode')
                                    shipping_address = ' '.join(self._extract_array(shipping, 'street'))

                                order_rows.append(tuple([
                                    transaction_id, 
                                    'I'+self._extract_field(order,'increment_id'),
                                    self._extract_float(order,'base_currency_code'),
                                    self._extract_float(order,'base_grand_total'), 
                                    self._extract_float(order,'discount_amount'), 
                                    self._extract_float(order,'subtotal'), 
                                    self._extract_float(order,'tax_amount'), 
                                    self._extract_float(order,'total_paid'),
                                    self._extract_float(order,'total_item_count'),
                                    self._extract_field(order,'customer_is_guest'),
                                    email, 
                                    self._extract_field(billing,'entity_id'), 
                                    firstname, lastname,
                                    billing_address,
                                    billing_zip,
                                    billing_city, billing_country_id, 
                                    shipping_address,
                                    shipping_zip,
                                    shipping_city, shipping_country_id, 
                                    self._extract_field(order,'created_at'), 
                                    self._extract_field(order,'status'),
                                    self._extract_field(order,'store_name'), 
                                    self._extract_field(order,'store_id'),
                                    'product',
                                    False,
                                    0.0,
                                    '',
                                ]))

                                for item in items:
                                    item_rows.append(tuple([
                                        transaction_id,
                                        self._extract_field(item,'created_at'),
                                        self._extract_field(item,'name'), 
                                        self._extract_field(item,'sku'), 
                                        self._extract_field(item,'product_id'),
                                        self._extract_float(item,'discount_amount'),
                                        self._extract_float(item,'discount_percent'),
                                        self._extract_float(item,'original_price'), 
                                        self._extract_float(item,'price'),
                                        self._extract_float(item,'price_incl_tax'),
                                        self._extract_float(item,'qty_ordered'),
                                        self._extract_float(item,'tax_amount'), 
                                        self._extract_float(item,'row_total'), 
                                        self._extract_float(item,'row_total_incl_tax'),
                                        self._extract_field(item,'item_id'),
                                        'product',
                                    ]))    
            except:
                print("Unexpected error: " + sys.exc_info()[0])
                
        df_trans = pd.DataFrame(order_rows, columns=[
            'Transaction_ID', 
            'Increment_ID',
            'Base_Currency','Total_Gross','Discount','Sub_Total','Tax_Amount','Amount_Paid',
            'Total_Num_Items_Purchased', 'Customer_Is_Guest',
            'Email', 
            'Billing_Entity_ID', 
            'Firstname', 'Lastname', 
            'Billing_Address', 'Billing_Zip','Billing_City','Billing_Country_ID',
            'Address_Line_1','Zip','City','Country',
            'Datetime', 
            'Status', 
            'Branch_Name', 
            'Branch_ID',
            'Item_Types',
            'Voucher_Used',
            'Voucher_Amount',
            'Single_Item_Product_ID',
        ])

        df_items = pd.DataFrame(item_rows, columns=[ 
            'Transaction_ID', 'Datetime', 
            'Name', 'SKU', 'Product_ID', 
            'Discount','Discount_Percent',
            'Original_Price', 'Price', 'Price_Incl_Tax', 
            'Quantity',
            'Tax_Amount', 'Total_Minus_Tax', 'Total',
            'Item_ID',
            'Item_Type',
        ])

        return df_trans, df_items
        
        
class MagentoCustomersExtract():
    
    def __init__(self, access_token, base_url):
        
        self.api = MagentoREST(access_token, base_url)
        self.df_customers = None
        
    def _extract_field(self, customer, field_name):
        
        return customer[field_name] if field_name in customer else ''
    
    def _extract_array(self, customer, field_name):
        
        return customer[field_name] if field_name in customer else ['']
    
    def extract(self, page_size = 1000, verbose=False):
        
        customer_rows = []
        
        today = datetime.datetime.today()
        
        try:
            params = {'searchCriteria[currentPage]':str(1), 
                      'searchCriteria[pageSize]':str(1),
                      'searchCriteria[filter_groups][0][filters][0][field]':'created_at',
                      'searchCriteria[filter_groups][0][filters][0][value]':today.strftime('%Y-%m-%d %H:%M:%S'),
                      'searchCriteria[filter_groups][0][filters][0][condition_type]':'lteq'
                     }
            response, customers = self.api.get('customers/search', params=params, verbose=False)
            to_id = customers['total_count']
            
            if verbose:
                print("Total number of customers: {:,}".format(customers['total_count']))
        except:
            print("Unexpected error: " + sys.exc_info()[0])
        
        cid = 1
        while cid <= to_id:
                
            try:
                
                page = int(np.floor((cid-1)/float(page_size))) + 1
                if verbose:
                    print("Requesting page {} of (customers from {} to {})".format(page, (page-1)*page_size, (page-1)*page_size + page_size))
                    
                params = {'searchCriteria[currentPage]':str(page), 
                          'searchCriteria[pageSize]':str(page_size),
                          'searchCriteria[filter_groups][0][filters][0][field]':'created_at',
                          'searchCriteria[filter_groups][0][filters][0][value]':today.strftime('%Y-%m-%d %H:%M:%S'),
                          'searchCriteria[filter_groups][0][filters][0][condition_type]':'lteq'
                         }
                cid = page_size + cid
                response, customers = self.api.get('customers/search', params=params, verbose=False)

                if (200 <= response.status_code <= 299) and 'items' in customers:
                  
                    for customer in customers['items']:
                  
                        city = ''
                        country_id = ''
                        postcode = ''
                        street = ''
                        telephone = ''
                        magento_id  = self._extract_field(customer, 'id')
                        dob = self._extract_field(customer, 'dob')
                        gender = self._extract_field(customer, 'gender')
                        email = self._extract_field(customer, 'email')
                        firstname = self._extract_field(customer, 'firstname')
                        lastname = self._extract_field(customer, 'lastname')
                        group_id = self._extract_field(customer, 'group_id')
                        if 'addresses' in customer and len(customer['addresses']) > 0:
                            for addr in customer['addresses']:
                                city = self._extract_field(addr, 'city')
                                country_id = self._extract_field(addr, 'country_id')
                                postcode = self._extract_field(addr, 'postcode')
                                street = self._extract_array(addr, 'street')[0]
                                telephone = self._extract_field(addr, 'telephone')

                                customer_rows.append(tuple([
                                    magento_id,
                                    firstname, lastname,# name.strip().upper(),
                                    gender, dob, email.strip().upper(),
                                    group_id,
                                    street, postcode, city, country_id, telephone
                                ]))
                        else:
                            customer_rows.append(tuple([
                                magento_id,
                                firstname, lastname, #name.strip().upper(),
                                gender, dob, email.strip().upper(),
                                group_id,
                                street, postcode, city, country_id, telephone
                            ]))
                    
            except:
                print("Unexpected error: " + sys.exc_info()[0])

        self.df_customers = pd.DataFrame(customer_rows, columns=[
            'Magento_ID',
            'Firstname', 'Lastname', #'Name', 
            'Gender', 'DOB', 'Email',
            'Group_ID', 
            'Address_Line_1', 'Zip', 'City', 'Country', 'Telephone'
        ])
        
        return self.df_customers
        
class MagentoProductsExtract():
    
    def __init__(self, access_token, base_url):
        
        self.api = MagentoREST(access_token, base_url)
        
    def _extract_field(self, product, field_name):
        
        return product[field_name] if field_name in product else ''
    
    def _extract_array(self, product, field_name):
        
        return product[field_name] if field_name in product else []
    
    def get_additional_fields(self, product):
        
        return []
    
    def define_additional_columns(self):
        
        return []

    def extract(self, page_size = 1000, verbose=False):
        
        product_rows = []
        
        today = datetime.datetime.today()
        
        try:
            params = {'searchCriteria[currentPage]':str(1), 
                      'searchCriteria[pageSize]':str(1),
                      'searchCriteria[filter_groups][0][filters][0][field]':'created_at',
                      'searchCriteria[filter_groups][0][filters][0][value]':today.strftime('%Y-%m-%d %H:%M:%S'),
                      'searchCriteria[filter_groups][0][filters][0][condition_type]':'lteq'
                     }
            response, customers = self.api.get('products', params=params, verbose=False)
            to_id = customers['total_count']
            
            if verbose:
                print("Total number of products: {:,}".format(customers['total_count']))
        except:
            print("Unexpected error: " + sys.exc_info()[0])
        
        cid = 1
        while cid <= to_id:
                
            try:
                
                page = int(np.floor((cid-1)/float(page_size))) + 1
                if verbose:
                    print("Requesting page {} of (products from {} to {})".format(page, (page-1)*page_size, (page-1)*page_size + page_size))
                    
                params = {'searchCriteria[currentPage]':str(page), 
                          'searchCriteria[pageSize]':str(page_size),
                          'searchCriteria[filter_groups][0][filters][0][field]':'created_at',
                          'searchCriteria[filter_groups][0][filters][0][value]':today.strftime('%Y-%m-%d %H:%M:%S'),
                          'searchCriteria[filter_groups][0][filters][0][condition_type]':'lteq'
                         }
                cid = page_size + cid
                response, products = self.api.get('products', params=params, verbose=False)

                if (200 <= response.status_code <= 299) and 'items' in products:
                  
                    for product in products['items']:
        
                        #if 'product_links' in product and len(product['product_links']) > 0:
                        #    print(product['id'])
                        #    print(product['product_links'])
                        
                        prod_id = self._extract_field(product, 'id')
                        prod_type_id = self._extract_field(product, 'type_id')
                        name = self._extract_field(product, 'name')
                        sku = self._extract_field(product, 'sku')
                        price = self._extract_field(product, 'price')
                        created_at = self._extract_field(product, 'created_at')
                        updated_at = self._extract_field(product, 'updated_at')

                        #options = ','.join(self._extract_array(product, 'options'))
                        #product_links = ','.join(self._extract_array(product, 'product_links'))
                        #tier_prices = ','.join(self._extract_array(product, 'tier_prices'))
                        
                        fields = [
                            prod_id, prod_type_id, name, sku, 
                            price, 
                            created_at, updated_at
                        ]
                        
                        fields = fields + self.get_additional_fields(product)

                        product_rows.append(tuple(fields))
                            
            except:
                print("Unexpected error: " + sys.exc_info()[0])
                
        columns = [
            'Product_ID', 'Product_Type_ID', 'Name', 'SKU', 
            'Price', 
            'Created_At', 'Updated_At'
        ]
        
        columns = columns + self.define_additional_columns()
            
        df_products = pd.DataFrame(product_rows, columns=columns)
        
        return df_products
    
