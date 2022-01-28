import sys
import pandas as pd

import requests
import rauth
from rauth import OAuth2Service
import json

class MailchimpREST:
    
    def __init__(self, access_token = None, client_id = '725681533252', client_secret = '68e3936817108f1e9ce8fe7c4021a05a8d0cffddb5e3d82c0a'):
        
        self.access_token = access_token
        
        self.oauth_base_uri = 'https://login.mailchimp.com/oauth2/'
        self.authorize_uri = 'https://login.mailchimp.com/oauth2/authorize'
        self.access_token_uri = 'https://login.mailchimp.com/oauth2/token'
        self.base_uri = ''

        self.client_id=client_id
        self.client_secret=client_secret
        self.redirect_uri='http://127.0.0.1'
        
        
    def get_auth_url(self, client_id = None, client_secret = None):
        
        if client_id is not None:
            self.client_id = client_id
            
        if client_secret is not None:
            self.client_secret = client_secret
        
        oauth2 = OAuth2Service(
            client_id=self.client_id,
            client_secret=self.client_secret,
            name='Mailchimp',
            authorize_url=self.authorize_uri,
            access_token_url=self.access_token_uri,
            base_url=self.base_uri)

        params = {
            'response_type': 'code',
            'redirect_uri': self.redirect_uri
        }

        url = oauth2.get_authorize_url(**params)
        return url
    
    def get_access_token(self, code):
        
        data={
            'grant_type':'authorization_code',
            'client_id' : client_id,
            'client_secret' : client_secret,
            'redirect_uri' : redirect_uri,
            'code' : code
        }
        
        response = requests.post(access_token_uri, data=data)
        if response.status_code == 200:
            
            self.access_token = response.json()['access_token']
            print("[get_access_token] Success. Token = '{}'".format(self.access_token))
            
        else:
            print("[get_access_token] Failed.")
            print(response.json())
            
        return self.access_token
            
        #print(response.json())
        
    def _request(self, request_func, endpoint, params={}, data={}, json={}, verbose=False):
        
        if self.access_token == None or self.access_token == '':
            print("[_request] Access token '{}' is not valid.".format(self.access_token))
            return None
        
        if self.base_uri == '':
            response = requests.get(self.oauth_base_uri + 'metadata', headers={
                'Authorization':'OAuth {}'.format(self.access_token)
            })
            if response.status_code == 200:
                #print(response.json())
                self.base_uri = response.json()['api_endpoint'] + '/3.0/'                
            else:
                print("[_request] Could not retrieve metadata.")
                return None
        
        url = self.base_uri + endpoint
        response = request_func(url, params=params, data=data, json=json, headers={
            'Authorization':'OAuth {}'.format(self.access_token)
        })

        if verbose:
            print("REST URI: {}".format(url))
            print("Response code: {0}".format(response.status_code))
            print("Response: " + response.text)

        return response, response.json()
            
        
    def post(self, endpoint, params={}, data={}, json={}, verbose=False):

        return self._request(requests.post, endpoint, params=params, data=data, json=json, verbose=verbose)

    
    def delete(self, endpoint, verbose=False):
        
        return self._request(requests.delete, endpoint, verbose=verbose)


    def put(self, endpoint, params={}, data={}, json={}, verbose=False):
        
        return self._request(requests.put, endpoint, params=params, data=data, json=json, verbose=verbose)

    
    def patch(self, endpoint, params={}, data={}, json={}, verbose=False):
        
        return self._request(requests.patch, endpoint, params=params, data=data, json=json, verbose=verbose)

    
    def get(self, endpoint, params={}, verbose=False):
        
        return self._request(requests.get, endpoint, params=params, verbose=verbose)


class MailchimpCustomersExtract():
    
    """
    Wrapper class for extracting customers from a Mailchimp audience.
    """
    
    def __init__(self, access_token = '1976af7eb0470a7d844ec590697f37d5'):
        
        self.api = MailchimpREST(access_token)
        self.df_customers = None
        self.list_id = ''
        
    def _extract_field(self, customer, field_name):
        
        return customer[field_name] if field_name in customer else ''
    
    def _extract_array(self, customer, field_name):
        
        return customer[field_name] if field_name in customer else ['']
    
    def _extract_dict(self, customer, field_name):
        
        return customer[field_name] if field_name in customer else {}
    
    def _get_audience_list_id(self, audience='HUMAI'):
        
        response, data = self.api.get('lists', verbose=False)
        for l in data['lists']:
            if l['name'] == audience:
                self.list_id = l['id']
                return True
                
        return False
    
    def extract(self, audience='HUMAI', page_size = 1000, verbose=False):
        
        if not self._get_audience_list_id(audience=audience):
            print("[extract] Could not find list ''".format(audience))
            return None
    
        offset = 0
        total_members = 1
        page_size = 1000
        customers = []
        while offset < total_members:

            try:
                response, data = self.api.get('lists/{}/members'.format(self.list_id), params={
                    'count' : page_size,
                    'offset' : offset,

                    'fields' : 'merge_fields,total_items,members'
                })

                total_members = data['total_items']
                if offset % 5000 == 0:
                    print("{:,}/{:,} ({:.2f}%)".format(offset, total_members, 100.0*offset/total_members))

                if response.status_code == 200:

                    for member in data['members']:

                        fields = self._extract_dict(member, 'merge_fields')
                        address = self._extract_dict(fields, 'ADDRESS')
                        if isinstance(address, str):
                            address = {}
                            
                        customers.append( 
                            (
                                self._extract_field(member, 'id'),
                                (self._extract_field(fields,'FNAME') + ' ' + self._extract_field(fields,'LNAME')).strip(),
                                self._extract_field(member, 'email_address').strip(),
                                self._extract_field(fields, 'BIRTHDAY'),
                                self._extract_field(address, 'addr1').strip().upper(),
                                self._extract_field(address, 'city').strip().upper(),
                                self._extract_field(address, 'zip').strip().upper(),
                                self._extract_field(address, 'country').strip().upper()
                            )
                        )
                else:
                    print("[extract] Got response status {} ({}), skipping to next offset {:,}".format(response.status_code, response.text, offset+page_size))
            except:
                print("[extract] Unexpected error: " + sys.exc_info()[0])


            offset = page_size + offset

        print("{:,}/{:,} ({:.2f}%)".format(total_members, total_members, 100.0))
        
        self.df_customers = pd.DataFrame(customers, columns=[
            'Customer_ID', 'Name', 'Email', 'Birthday', 'Address', 'City', 'Zip', 'Country' 
        ])

        return self.df_customers


        
class MailchimpPredictionsLoader:
    
    """
    Helper class for pushing predictions to Mailchimp.
    
    TODO: Finish implementation.
    """
    
    def __init__(self, audience='HUMAI', access_token = '1976af7eb0470a7d844ec590697f37d5'):
        
        self.api = MailchimpREST(access_token)
        self.ready = False
        self.audience = audience
        self.list_id = ''
        self.field_to_tag = {}
        
    def create_or_init(self, audience='HUMAI'):
        
        self.audience = audience
        self.field_to_tag = {}
        self.list_id = ''
        self.ready = False
        self._create_fields(audience)
        
        
    def _get_audience_list_id(self, audience='HUMAI'):
        
        response, data = self.api.get('lists', verbose=False)
        for l in data['lists']:
            if l['name'] == audience:
                self.list_id = l['id']
                return True
                
        return False
    
        
    def _create_fields(self, audience):
        
        try:
        
            self.ready = False
            if not self._get_audience_list_id(audience):
                print("[_create_fields] Could not find audience ''".format(audience))
                return self.ready

            required_fields = [
                ('Date to email', 'date', True, ''),
                ('Time of day', 'text', True, ''),
                ('Propensity to Open', 'number', True, 0.0),
                ('Propensity to Buy', 'number', True, 0.0),
                ('Num Transactions', 'number', True, 0),
                ('Discount Sensitivity', 'number', True, 0),
                ('Life Cycle Stage', 'text', True, ''),
                ('Last Transaction Date', 'date', True, ''),
                ('Last Email Activity Date', 'date', True, '')
            ]

            response, data = self.api.get('lists/{}/merge-fields'.format(self.list_id))

            self.field_to_tag = {e['name']:e['tag'] for e in data['merge_fields'] }
            print(self.field_to_tag.keys())
                  
            for field in required_fields:
                if field[0] not in self.field_to_tag:
                    
                    print("Creating field '{}'".format(field[0]))
                    
                    response, data = self.api.post('lists/{}/merge-fields'.format(self.list_id), json={
                    #response, data = self.api.patch('lists/{}/merge-fields'.format(self.list_id), json={
                        'name' : field[0],
                        'type' : field[1],
                        'public' : field[2]
                    }, verbose=False)
                    
                    #data = response
                    #print(data)
                    
                    self.field_to_tag[field[0]] = data['tag']
        
            self.ready = True
            
            #print(self.field_to_tag)
            
        except:
            
            print("[extract] Unexpected error: " + sys.exc_info()[0])
            
        return self.ready
        
    
    def push(
        self, 
        df,
        mappings,
        verbose=False):

        if not self.ready:
            print("[push] Not ready, call create_or_init()")
            return False
        
        nn = len(df)
        ii = 0

        dfg = df.groupby(by='Customer_ID')
        for cid, df_predictions in dfg:
            
            if ii % 500 == 0:
                print("{:,}/{:,} ({:.2f} %)".format(ii, nn, 100.0*ii/nn))
            
            if cid == '':
                print("  Skipping invalid Customer ID: {} with predictions {}".format(copernica_id, df_predictions))
                ii = len(df_predictions) + ii
            else:
                
                for index, row in df_predictions.iterrows():
                    
                    #print(row)
                    
                    merge_fields = {
                        self.field_to_tag[field] : row[mappings[field]] for field in mappings.keys()
                    }
                    
                    response = self.api.patch('lists/{}/members/{}'.format(self.list_id, cid), json={
                        'merge_fields' : merge_fields
                    }, verbose=False)


            ii = 1 + ii
            
        print("{:,}/{:,} ({:.2f} %)".format(nn, nn, 100.0))
        
        return True
        

    def remove(self, df, pred_type = 'PersonalizedMailFlow', verbose=False):

        if not self.ready:
            print("[push_predictions_to_copernica] Not ready, call create_or_init()")
            return False
        
        assert False, "Implement."
        
        return False 