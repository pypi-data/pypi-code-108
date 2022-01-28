import requests
import rauth
from rauth import OAuth2Service
import json

from timeit import default_timer as timer
import datetime

import numpy as np
import pandas as pd

from humailib.cloud_tools import GoogleBigQuery

import humailib.utils as hu
import humailib.hasher as hh


class CopernicaREST:
    
    def __init__(self, access_token):
        
        self.access_token = access_token
        self.base_url = 'https://api.copernica.com/v2/'
        # Just a random string
        self.state = 'sjDIEj39fkDSUo40'
        
    #Directondergoed: def get_auth_url(self, client_id = '352576017e08e77410efc978040b7e7d', client_secret = 'dc0ac7e6d01998f78a92850835004d3d'):
    def get_auth_url(self, client_id, client_secret):
        
        copernica = OAuth2Service(
            client_id=client_id,
            client_secret=client_secret,
            name='Copernica',
            authorize_url='https://www.copernica.com/nl/authorize',
            access_token_url='https://api.copernica.com/v2/token',
            base_url='https://www.copernica.com/nl/')

        redirect_uri = 'https://www.copernica.com/nl/'
        params = {'state': self.state,
                  'response_type': 'code',
                  'redirect_uri': redirect_uri}

        url = copernica.get_authorize_url(**params)
        return url
        
    def post(self, endpoint, params=None, data=None, verbose=False):

        url = self.base_url + endpoint + '?access_token={}'.format(self.access_token)
        response = requests.post(url, params=params, data=data)
        if verbose:
            print("REST URI: {}".format(url))
            print("Response code: {0}".format(response.status_code))
            print("Response: " + response.text)

        return response
    
    def delete(self, endpoint, verbose=False):
        
        url = self.base_url + endpoint + '?access_token={}'.format(self.access_token)
        response = requests.delete(url)
        if verbose:
            print("REST URI: {}".format(url))
            print("Response code: {0}".format(response.status_code))
            print("Response: " + response.text)

        return response
    
    def put(self, endpoint, params=None, data=None, verbose=False):
        
        url = self.base_url + endpoint + '?access_token={}'.format(self.access_token)
        response = requests.put(url, params=params, data=data)
        if verbose:
            print("REST URI: {}".format(url))
            print("Response code: {0}".format(response.status_code))
            print("Response: " + response.text)

        return response
    
    def get(self, endpoint, params=None, verbose=False):
        
        url = self.base_url + endpoint + '?access_token={}'.format(self.access_token)
        response = requests.get(url, params=params)
        if verbose:
            print("REST URI: {}".format(url))
            print("Response code: {0}".format(response.status_code))
            print("Response: " + response.text)

        return response, response.json()
        

class CopernicaEmailExtract:
    
    def __init__(self, access_token):
        
        self.api = CopernicaREST(access_token)
        
    def extract(
        self, from_date, to_date, 
        min_destinations = 3, page_size = 1000, verbose=False
    ):
        """
        Get all email events for the date range in the halt-open interval [from_date, to_date).
        """
        
        total = 1
        offset = 0

        mailings = []
        events = []
        
        ii = 1

        while offset < total:

            response, mm = self.api.get(
                'publisher/emailings', params={
                    'type': 'mass', 
                    'start': offset, 'count': page_size,
                    'fromdate': from_date.strftime('%Y-%m-%d'), 'todate': to_date.strftime('%Y-%m-%d')
                }, 
                verbose=False
            )
            total = mm['total']

            for m in mm['data']:
                mailing_id = m['id']
                mailing_datetime = m['timestamp']
                ndestinations = int(m['destinations'])
                if ndestinations >= min_destinations:

                    _, stats = self.api.get('publisher/emailing/{}'.format(mailing_id), verbose=False)
                    
                    broadcast_id = str(stats['id'])
                    #print(stats)
                    print("{}/{} emailing {} at {}, subject '{}', destinations: {:,}, clicks: {:,}, opens: {:,}".format(
                        ii, total,
                        broadcast_id, 
                        stats['timestamp'], 
                        stats['subject'], 
                        int(stats['destinations']),
                        int(stats['clicks']), 
                        int(stats['impressions'])
                    ))

                    mailings.append((broadcast_id, stats['timestamp'], str(stats['document']), 
                                     stats['subject'], int(stats['destinations']), 
                                     int(stats['impressions']), int(stats['clicks'])))

                    ## events
                    dd = self._get_events_by_type(
                        mailing_id, mailing_datetime, type='deliveries', event_name='DELIVERY', verbose=verbose
                    )
                    events.extend(dd)

                    ## OPENS ("impressions")
                    oo = self._get_events_by_type(
                        mailing_id, mailing_datetime, type='impressions', event_name='OPEN', verbose=verbose
                    )
                    events.extend(oo)

                    ## CLICKS
                    cc = self._get_events_by_type(
                        mailing_id, mailing_datetime, type='clicks', event_name='CLICK', verbose=verbose
                    )
                    events.extend(cc)

                    ## UNSUBSCRIBES 
                    uu = self._get_events_by_type(
                        mailing_id, mailing_datetime, type='unsubscribes', event_name='UNSUBSCRIBE', verbose=verbose
                    )
                    events.extend(uu)
                else:
                    print("{}/{} destinations: {:,}. Doesn't satisfy minimum {:,}".format(
                        ii, total,
                        ndestinations,
                        min_destinations
                    ))

                ii = 1 + ii
                
            offset = mm['count'] + offset

        df_mailings = pd.DataFrame(mailings, columns=['Broadcast_ID', 'Send_Datetime', 'Campaign_ID', 
                                                      'Campaign_Name', 'Num_Customers', 'Num_Opens', 'Num_Clicks'])
        df_mailings = df_mailings.sort_values(by=['Send_Datetime'])
        
        df_mailings_events = pd.DataFrame(events, columns=['Broadcast_ID', 'Copernica_ID', 'Send_Datetime', 
                                                          'Activity', 'Activity_Datetime', 'Description'])
        df_mailings_events = df_mailings_events.sort_values(by=['Activity_Datetime'])
        
        hu.columns_as_datetime(df_mailings, columns=['Send_Datetime'])
        hu.columns_as_datetime(df_mailings_events, columns=['Send_Datetime','Activity_Datetime'])

        return df_mailings, df_mailings_events
        
    
    def _get_events_by_type(self, mailing_id, mailing_datetime, type='events', event_name='DELIVERY', verbose=False):
        
        events = []
        
        if verbose:
            print("[CopernicaEmailExtract_get_events_by_type]... retrieving {} for {}".format(event_name, mailing_id))

        start = 0
        count = 1000
        total = 1
        while start < total:
            response, dd = self.api.get(
                'publisher/emailing/{}/{}'.format(mailing_id, type), 
                params={'start': start, 'count':count},
                verbose=False
            )
            
            if 200 <= response.status_code <= 299:
                
                total = dd['total']

                if verbose:
                    print("  Emailing: {}, found {} [{},{}) total {}".format(mailing_id, event_name, dd['start'], dd['start']+dd['count'], total))

                for d in dd['data']:

                    if d['emailing'] != mailing_id:
                        print("{} {}".format(d['emailing'], mailing_id))
                        
                    broadcast_id = str(mailing_id)
                    events.append((
                        # Broadcast_ID, Copernica_ID, Send_datetime, Activity, Activity_Datetime, Description
                        broadcast_id, d['profile'], mailing_datetime, event_name, d['timestamp'], ''
                    ))

                start = dd['count'] + start
            else:
                print("[CopernicaEmailExtract_get_events_by_type] {}".format(response.text))

        print("  Emailing {}, found {:,} events of type {}".format(mailing_id, len(events), event_name))

        return events     
     
    
class CopernicaPredictionsLoader:
    
    def __init__(self, access_token, database, humai_pred_collection = 'HumaiPredictions'):
        
        self.api = CopernicaREST(access_token)
        self.ready = False
        self.humai_database_id = -1
        self.humai_collection_id = -1
        
        self.profile_fields = [
            ('Humai_Customer_ID','text','',True),
            ('Humai_Group','text','',True)
        ]
        
        self.subprofile_fields = [
            ('Humai_Customer_ID','text','',True),
            ('Humai_Mail_ID','integer',-1,True),
            ('Type','text','PersonalizedMailFlow',True),
            ('Date','date','2020-01-01',True),
            ('DatetimeSlot','text','Midnightto12PM', True),
            ('Group','text','A',True)
        ]
        
        
    def create_or_init(
        self, 
        database,
        humai_pred_collection = 'Humai_Predictions',
        profile_fields = None,
        subprofile_fields = None
    ):
        if profile_fields is not None:
            self.profile_fields = profile_fields
            
        if subprofile_fields is not None:
            self.subprofile_fields = subprofile_fields
            
        self._create_fields_and_collection(database, humai_pred_collection)
        
        
    def _create_elements(self, endpoint, df):
    
        _, data = self.api.get(endpoint)

        existing_elements = {d['name']:True for d in data['data']}

        success = True
        for index, row in df.iterrows():

            if row['name'] in existing_elements:
                print("[_create_elements] Found {}".format(row['name']))
            else:
                print("[_create_elements] Creating {}...".format(row['name']))

                new_element = row.to_dict()
                response = self.api.post(endpoint, data=new_element, verbose=True)

                if response.status_code == 201:
                    print("  Created.")
                else:
                    print("  Failed to create.")
                    success = False
                    
        return success
        
    def _create_fields_and_collection(self, database, humai_pred_collection = 'Humai_Predictions'):
        
        ## Set data
        
        self.humai_database_id = -1
        self.humai_collection_id = -1
        self.ready = False
        
        df_fields = pd.DataFrame(self.profile_fields, columns=['name','type','value','displayed'])

        required_interests = [
        #    ('OS_1', 'Humai_Interests'),
        #    ('OS_2',' Humai_Interests'),
        #    ('SIX_MONTH', 'Humai_Interests')
        ]

        df_interests = pd.DataFrame(required_interests, columns=['name','group'])

        df_collection_fields = pd.DataFrame(self.subprofile_fields, columns=['name','type','value','displayed'])
        
        ## Creation logic
        
        response, data = self.api.get('databases')
        if response.status_code == 200:
            
            databases = {db['name']:db['ID'] for db in data['data']}
            self.humai_database_id = int(databases[database]) if database in databases else -1
                
        if self.humai_database_id >= 0:
            
            print("[_create_fields_and_collection] Found database '{}', ID: {}".format(database, self.humai_database_id))
            
            response, data = self.api.get('database/{}/collections'.format(self.humai_database_id))
            if response.status_code != 200:
                print("[_create_fields_and_collection] Could not retrieve collections for database {}".format(database))
                return
                
            collections = {c['name']:c['ID'] for c in data['data']}
            #print(collections)
            self.humai_collection_id = int(collections[humai_pred_collection]) if humai_pred_collection in collections else -1
            #print(self.humai_collection_id)
            
            if self.humai_collection_id == -1:
                
                response = self.api.post('database/{}/collections'.format(self.humai_database_id), data={'name':humai_pred_collection})
                if response.status_code != 201:
                    print("Could not create collection: {}".format(humai_pred_collection))
                    return
                
            if self.humai_collection_id >= 0:
                print("[_create_fields_and_collection] Found collection '{}', ID: {}".format(humai_pred_collection, self.humai_collection_id))
                                       
            success = self.humai_database_id >= 0 and self.humai_collection_id >= 0
            
            if success:
                
                print("Checking fields...")
                success = success & self._create_elements('database/{}/fields'.format(self.humai_database_id), df_fields)
                print("Checking interests...")
                success = success & self._create_elements('database/{}/interests'.format(self.humai_database_id), df_interests)
                print("Checking collection fields...")
                success = success & self._create_elements('collection/{}/fields'.format(self.humai_collection_id), df_collection_fields)

                self.ready = success
            
            print("[_create_fields_and_collection] Ready => {}".format(self.ready))
        else:
            
            print("[_create_fields_and_collection] Database {} does not exist.".format(database))
            
            
    def push_profile_data(self, df, mapping, interest_mapping=None, cid_column='Customer_ID', test=False):
        
        if not self.ready:
            print("[push_predictions_to_copernica] Not ready, call create_or_init()")
            return
        
        nn = len(df)
        ii = 0

        dfg = df.groupby(by='Copernica_ID')
        t0 = timer()
        for copernica_id, df_profile in dfg:
            
            copernica_id = int(copernica_id)
        
            if ii % 500 == 0:
                t1 = timer()
                print("{:,}/{:,} ({:.2f} %) elapsed: {}".format(ii, nn, 100.0*ii/nn, str(datetime.timedelta(seconds=(t1-t0)))))

            if copernica_id == -1:
                print("  Skipping invalid Copernica ID: {} with profile {}".format(copernica_id, df_profile))
                ii = len(df_profile) + ii
            else:
                profile = df_profile.iloc[0,:]

                #response, data = self.api.get('profile/{}'.format(copernica_id), verbose=False)
                #if response.status_code == 200:#requests.codes.ok:
                    
                fields_data = {
                    key : profile[ mapping[key] ] for key in mapping.keys()
                }

                interests_data = None
                if interest_mapping is not None:
                    interests_data = {
                        key : profile[ interest_mapping[key] ] for key in interest_mapping.keys()
                    }

                if test:
                    print("Copernica ID {}, push:".format(copernica_id))
                    for field in fields_data.keys():
                        print("  '{}' -> '{}'".format(field, fields_data[field]))

                    if interests_data is not None:
                        for interest in interests_data.keys():
                            print("  interest '{}' -> '{}'".format(interest, interests_data[interest]))
                else:
                    response = self.api.put('profile/{}/fields'.format(copernica_id), data=fields_data, verbose=False)
                    if interests_data is not None:
                        response = self.api.put('profile/{}/interests'.format(copernica_id), data=interests_data, verbose=False)

                #else:
                #    print("Could not retrieve Copernica ID {}".format(copernica_id))

            ii = len(df_profile) + ii
                      
        t1 = timer()
        print("{:,}/{:,} ({:.2f} %) elapsed: {}".format(
            nn, nn, 100.0, 
            str(datetime.timedelta(seconds=(t1-t0)))
        ))
        
        
    def push_subprofile_data(self, df, mapping, cid_column='Customer_ID', test=False):
    
        if not self.ready:
            print("[push_predictions_to_copernica] Not ready, call create_or_init()")
            return
    
        nn = len(df)
        ii = 0

        dfg = df.groupby(by='Copernica_ID')
        t0 = timer()
        for copernica_id, df_subprofiles in dfg:
            
            copernica_id = int(copernica_id)
            
            if copernica_id == -1:
                print("  Skipping invalid Copernica ID: {} with profile {}".format(copernica_id, df_subprofiles))
                ii = len(df_profile) + ii
            else:
                #response, data = self.api.get('profile/{}'.format(copernica_id), verbose=False)
                #if response.status_code == 200:#requests.codes.ok:

                #
                # Create predictions as subprofiles
                #

                for index, row in df_subprofiles.iterrows():

                    if ii % 500 == 0:
                        t1 = timer()
                        print("{:,}/{:,} ({:.2f} %) elapsed: {}".format(ii, nn, 100.0*ii/nn, str(datetime.timedelta(seconds=(t1-t0)))))

                    subprofile_data = {
                        key : row[ mapping[key] ] for key in mapping.keys()
                    }

                    if test:
                        print("Copernica ID {}:".format(copernica_id))
                        for field in subprofile_data.keys():
                            print('  {} -> {}'.format(field, subprofile_data[field]))
                    else:                            
                        response = self.api.post(
                            'profile/{}/subprofiles/{}'.format(copernica_id, self.humai_collection_id), 
                            data=subprofile_data, verbose=False
                        )

                    ii = 1 + ii

                    #response.status_code, response.text, response.reason
                #else:
                #    print("Could not retrieve Copernica ID {}".format(copernica_id))

                #    ii = len(df_predictions) + ii            

        t1 = timer()
        print("{:,}/{:,} ({:.2f} %) elapsed: {}".format(
            nn, nn, 100.0, 
            str(datetime.timedelta(seconds=(t1-t0)))
        ))

            
    def push(self, df, pred_type='PersonalizedMailFlow', segment_columns = None, segment_names = None, verbose=False):

        assert False, "Deprecated"
        
        if not self.ready:
            print("[push_predictions_to_copernica] Not ready, call create_or_init()")
            return
        
        nn = len(df)
        ii = 0

        dfg = df.groupby(by='Copernica_ID')
        for copernica_id, df_predictions in dfg:
            
            if copernica_id == -1:
                print("  Skipping invalid Copernica ID: {} with predictions {}".format(copernica_id, df_predictions))
                ii = len(df_predictions) + ii
            else:
                customer_id = df_predictions.iloc[0, :]['Customer_ID']

                response, data = self.api.get('profile/{}'.format(copernica_id), verbose=False)
                if response.status_code == 200:#requests.codes.ok:

                    if verbose:
                        print("Copernica ID {}, Humai Customer ID {} == {}".format(data['ID'], data['fields']['Humai_Customer_ID'], customer_id))
                        for field in data['fields']:
                            print("  {} -> {}".format(field, data['fields'][field]))

                    #
                    # Update existing profile fields
                    #

                    fields_data = {
                        'Humai_Customer_ID' : str(customer_id)
                    }
                    response = self.api.put('profile/{}/fields'.format(copernica_id), data=fields_data, verbose=False)

                    if segment_columns is not None:
                        interests_data = {}
                        row = df_predictions.iloc[0,:]
                        for col,name in zip(segment_columns, segment_names):
                            interests_data[name] = row[col]

                        # Update (PUT) existing interests
                        response = self.api.put('profile/{}/interests'.format(copernica_id), data=interests_data, verbose=False)

                    #
                    # Create predictions as subprofiles
                    #

                    for index, row in df_predictions.iterrows():

                        if ii % 500 == 0:
                            print("{:,}/{:,} ({:.2f} %)".format(ii, nn, 100.0*ii/nn))

                        subprofile = {
                            'Humai_Customer_ID' : str(customer_id),
                            'Humai_Mail_ID' : int(row['Email_ID']),
                            'Type' : pred_type,
                            'Date' : row['Date'].strftime('%Y-%m-%d'),
                            'DatetimeSlot' : row['Time_Of_Day'],
                            'Channel' : 'Email',
                            'Group' : 'B'
                        }

                        response = self.api.post(
                            'profile/{}/subprofiles/{}'.format(copernica_id, self.humai_collection_id), 
                            data=subprofile, verbose=False
                        )

                        ii = 1 + ii

                        #response.status_code, response.text, response.reason
                else:
                    print("Could not retrieve Copernica ID {}".format(copernica_id))

                    ii = len(df_predictions) + ii
            
            
        print("{:,}/{:,} ({:.2f} %)".format(nn, nn, 100.0))
        
    
    def remove_all_subprofiles(self, page_size=1000, verbose=False):
        
        if not self.ready:
            print("[remove_all_subprofiles] Not ready, call create_or_init()")
            return
        
        cur_profile = 0
        total_profiles = 1
        n_removed = 0
        while cur_profile < total_profiles:

            parameters = {
                'start' : cur_profile,
                'limit' : page_size
            }
            response, data = self.api.get(
                'database/{}/profiles'.format(self.humai_database_id), 
                params=parameters, 
                verbose=False
            )
            if 200 <= response.status_code <= 299:

                total_profiles = data['total']

                for profile in data['data']:

                    if cur_profile % 1000 == 0:
                        print("{:,}/{:,} ({:.2f}%). Removed {:,} subprofiles so far".format(
                            cur_profile, total_profiles, 
                            100.0*cur_profile / total_profiles, 
                            n_removed,
                        ))

                    copernica_id = int( profile['ID'] )

                    response, data = self.api.get('profile/{}/subprofiles/{}'.format(copernica_id, self.humai_collection_id), verbose=False)
                    if 200 <= response.status_code <= 299:#requests.codes.ok:

                        for subprofile in data['data']:
                            n_removed = 1 + n_removed
                            self.api.delete('subprofile/{}'.format(subprofile['ID']))
                            if verbose:
                                print("  Deleted subprofile ID {}, created {}, type {}".format(subprofile['ID'], subprofile['created'], subprofile['fields']['Type']))

                    cur_profile = 1 + cur_profile
                    
            else:
                print("[link_and_add_to_customers] Call to retrieve {} profiles starting from {} failed.".format(total_profiles, cur_profile))


    def remove(self, df, pred_type = 'PersonalizedMailFlow', verbose=False):

        #assert False, "Deprecated"
        
        if not self.ready:
            print("[push_predictions_to_copernica] Not ready, call create_or_init()")
            return
        
        cpids = df['Copernica_ID'].unique().tolist()
        nn = len(cpids)
        ii = 0
        
        for copernica_id in cpids:
            
            if copernica_id == -1:
                print("  Skipping invalid Copernica ID: {}".format(copernica_id))
            
            if ii % 500 == 0:
                print("{:,}/{:,} ({:.2f} %)".format(ii, nn, 100.0*ii/nn))
            
            if verbose:
                print("Copernica ID {}".format(copernica_id))

            response, data = self.api.get('profile/{}/subprofiles/{}'.format(copernica_id, self.humai_collection_id), verbose=False)
            if response.status_code == 200:#requests.codes.ok:

                for subprofile in data['data']:
                    if subprofile['fields']['Type'] == pred_type:
                        self.api.delete('subprofile/{}'.format(subprofile['ID']))
                        if verbose:
                            print("  Deleted subprofile ID {}, created {}, type {}".format(subprofile['ID'], subprofile['created'], subprofile['fields']['Type']))
                        
            ii = 1 + ii
            
        print("{:,}/{:,} ({:.2f} %)".format(nn, nn, 100.0))
        

def get_database_id(api, database):
    """
    Get the 'ID' field for database in Copernica.
    """
    
    response, data = api.get('databases')
    if response.status_code == 200:
            
        databases = {db['name']:db['ID'] for db in data['data']}
        return int(databases[database]) if database in databases else -1
                
    return -1


class CopernicaCustomersExtract:
    """
    Helper class for converting between Customer IDs and Copernica IDs, given a customers table.
    """
    
    def __init__(self, gbq, access_token):
        
        self.df_customers = None
        self.gbq = gbq
        self.api = CopernicaREST(access_token)
        self.fieldnames = {
            'firstname' : 'MFirstName',
            'lastname' : 'MLastName',
            'email' : 'MEmail',
            'gender' : 'MGender',
            'dob' : 'MDOB',
        }
        
        return
    
    def _extract_string(self, record, field_name):
        
        return record[field_name].strip().upper() if field_name in record else ''
    
    def _extract_int(self, record, field_name):
        
        return int(record[field_name]) if field_name in record else np.nan
    
    def _unsubscribed(self, fields):
        
        return self._extract_string(fields, 'MSubscriberRawState') != 'STATUS_SUBSCRIBED' or self._extract_string(fields, 'MNewsletter') != 'YES' or self._extract_string(fields, 'AfgemeldNieuwsbrief') == 'JA'

    def set_fieldnames(self, fieldnames):
        
        self.fieldnames = fieldnames        
    
    def extract(self, database='', page_size=1000, verbose=False):
        
        if self.api is None:
            print("[CopernicaCustomersExtract::extract] No API.")
            return None

        database_id = get_database_id(self.api, database)
        if database_id < 0:
            if verbose:
                print("[CopernicaCustomersExtract::extract] Failed to find database {}".format(database))
            return None
        
        customer_rows = []
        
        cur_profile = 0
        total_profiles = 1
        while cur_profile < total_profiles:

            parameters = {
                'start' : cur_profile,
                'limit' : page_size
            }
            response, data = self.api.get('database/{}/profiles'.format(database_id), params=parameters, verbose=False)
            if 200 <= response.status_code <= 299:

                total_profiles = data['total']
                #print(data)

                for profile in data['data']:

                    if cur_profile % 1000 == 0:
                        print("{:,}/{:,} ({:.2f}%)".format(
                            cur_profile, total_profiles, 100.0*float(cur_profile)/total_profiles
                        ))

                    copernica_id = -1
                    if 'fields' in profile:
                        fields = profile['fields']
                        #print("fields:\n============")
                        #print(fields)
                        cfirstname = self._extract_string(fields, self.fieldnames['firstname'])
                        clastname = self._extract_string(fields, self.fieldnames['lastname'])
                        cemail = self._extract_string(fields, self.fieldnames['email'])
                        copernica_id = int( profile['ID'] )

                        unsub = profile['removed'] or self._unsubscribed(fields)
                        
                        customer_rows.append((
                            copernica_id,cemail,
                            cfirstname,clastname,
                            self._extract_string(fields, self.fieldnames['dob']),
                            self._extract_string(fields, self.fieldnames['gender']),
                            not unsub
                        ))
                        
                        if verbose:
                            print(f"{copernica_id}, {cemail}, {cfirstname}, {clastname}")
                        
                    cur_profile = 1 + cur_profile
            else:
                cur_profile = page_size + cur_profile
                print("[link_and_add_to_customers] Call to retrieve {} profiles starting from {} failed.".format(total_profiles, cur_profile))

        print("{:,}/{:,} ({:.2f}%)".format(
            total_profiles, total_profiles, 100.0, 
        ))

        df_customers = pd.DataFrame(
            customer_rows,
            columns=['Copernica_ID','Email','Firstname','Lastname',
                     'Date_of_Birth',
                     'Gender',
                     'Subscribed']
        )

        return df_customers

class CopernicaSelectionExtract:
    """
    Helper class for converting between Customer IDs and Copernica IDs, given a customers table.
    """
    
    def __init__(self, gbq, access_token):
        
        self.df_customers = None
        self.gbq = gbq
        self.api = CopernicaREST(access_token)
        self.fieldnames = {
            'copernica_id' : 'ID',
            'email' : 'email',
            'Customer_ID' : 'Humai_Customer_ID',
            'Group' : 'Humai_Group',
        }
        
        return
    
    def _extract_string(self, record, field_name):
        
        return record[field_name].strip().upper() if field_name in record else ''
    
    def _extract_int(self, record, field_name):
        
        return int(record[field_name]) if field_name in record else np.nan
    
    def set_fieldnames(self, fieldnames):
        
        self.fieldnames = fieldnames        
    
    def extract(self, view_id='', page_size=1000, verbose=False):
        
        if self.api is None:
            print("[CopernicaCustomersExtract::extract] No API.")
            return None

        #database_id = get_database_id(self.api, database)
        #if database_id < 0:
        #    if verbose:
        #        print("[CopernicaCustomersExtract::extract] Failed to find database {}".format(database))
        #    return None
        
        customer_rows = []
        
        cur_profile = 0
        total_profiles = 1
        while cur_profile < total_profiles:

            parameters = {
                'start' : cur_profile,
                'limit' : page_size
            }
            response, data = self.api.get('view/{}/profiles'.format(view_id), params=parameters, verbose=False)
            if 200 <= response.status_code <= 299:

                total_profiles = data['total']
                #print(data)

                for profile in data['data']:

                    if cur_profile % 1000 == 0:
                        print("{:,}/{:,} ({:.2f}%)".format(
                            cur_profile, total_profiles, 100.0*float(cur_profile)/total_profiles
                        ))

                    copernica_id = -1
                    if 'fields' in profile:
                        fields = profile['fields']
                        
                        copernica_id = int( profile['ID'] )
                        cemail = self._extract_string(fields, self.fieldnames['email'])
                        customer_id = self._extract_string(fields, self.fieldnames['Customer_ID'])
                        cgroup = self._extract_string(fields, self.fieldnames['Group'])
                        
                        customer_rows.append((
                            copernica_id,cemail,
                            customer_id, cgroup
                        ))
                        
                        if verbose:
                            print(f"{copernica_id}, {cemail}, {customer_id}, {cgroup}")
                        
                    cur_profile = 1 + cur_profile
            else:
                cur_profile = page_size + cur_profile
                print("[link_and_add_to_customers] Call to retrieve {} profiles starting from {} failed.".format(total_profiles, cur_profile))

        print("{:,}/{:,} ({:.2f}%)".format(
            total_profiles, total_profiles, 100.0, 
        ))

        df_customers = pd.DataFrame(
            customer_rows,
            columns=['Copernica_ID','Email','Customer_ID','Group',]
        )
        
        print(f"Total profiles: {total_profiles:,}")

        return df_customers