import requests
import pandas as pd

''' Function that call the Tableau Server REST API to perform a query '''
def query_tableau(query, site_id, username, password):
    # Set the request parameters
    url = 'https://tableau.server.url/api/2.6/sites/' + site_id + '/workbooks?filter=' + query
    # Set proper headers
    headers = {'content-type': 'application/json', 'accept': 'application/json'}
    # Do the HTTP request
    response = requests.get(url, auth=(username, password), headers=headers)
    # Check for HTTP codes other than 200
    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
        exit()
    # Decode the JSON response into a dictionary and use the data
    data = response.json()
    return data
    
''' Convert response in a dataframe '''
def get_dataframe(data):
    # Get the list of workbooks
    workbooks = data['workbooks']
    # Create a dataframe from the list
    df = pd.DataFrame(workbooks)
    return df

