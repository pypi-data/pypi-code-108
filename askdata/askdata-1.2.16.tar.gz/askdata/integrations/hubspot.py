''' Get contacts from Hubspot via API '''

import requests
import json
import pandas as pd

def get_contacts(hapikey, offset=0):

    properties = ["firstname","lastname","email","company","jobtitle","phone","address","city","state","zip","country","twitter","facebook","linkedin"]

    params = {
        'hapikey': hapikey,
        'property': properties,
        'count': 100,
        'vidOffset': offset
    }

    r = requests.get("https://api.hubapi.com/contacts/v1/lists/all/contacts/all", params=params)

    if r.status_code == 200:
        return r.json()
    else:
        return None

''' Return the result of the Hubspot API to apandas Dataframe '''
def get_contacts_df(hapikey, offset=0):

    contacts = get_contacts(hapikey, offset)

    if contacts is not None:
        from pandas import json_normalize
        df = pd.DataFrame(json_normalize(contacts['contacts']))

        df.columns = df.columns.str.replace('properties.', '')
        df.columns = df.columns.str.replace('.value', '')

        df = df.drop(['identity-profiles','canonical-vid','merged-vids','vid','merge-audits','form-submissions'], axis=1)
        
        # Convert added at in YYYY-MM-DD format
        df['addedAt'] = pd.to_datetime(df['addedAt'], unit='ms')

        # Rename columns
        df.rename(columns={'portal-id': 'contact_id'}, inplace=True)

        return df

    else:

        return None
