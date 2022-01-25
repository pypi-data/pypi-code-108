import json
from pandasql import sqldf
import pandas as pd

''' Integration abstract class '''
class Dataset():

	def discovery(self):
		pass

	def resultset_to_df(json_data):
		# Parse the JSON data
		json_data = json.loads(json_data)
		# Get the data from the JSON
		data = json_data['data']
		# Get the schema from the JSON
		schema = json_data['schema']
		# Create a list of column names
		column_names = [column['name'] for column in schema]
		# Create a list of data
		data_list = [row['cells'] for row in data]
		# Create a dataframe from the data
		df = pd.DataFrame(data_list, columns=column_names)
		# Return the dataframe
		return df

	def df_to_resultset(df):
		# Get the schema from the dataframe
		schema = df.columns
		# Create a list of dictionaries with the data
		data_list = df.to_dict('records')
		# Create a dictionary with the data
		data = {'data': data_list}
		# Create a dictionary with the schema
		schema_dict = {column: {'name': column} for column in schema}
		# Create a dictionary with the schema and data
		json_dict = {
			'schema': schema_dict,
			'data': data_list,
			'id': None,
			'dataset': {
				'id': '6512cf85-4f81-4fa0-a2b8-c51c6aad6cf9-BIGQUERY-a0fb8755-d50b-412b-9b86-0fd7d5529843',
				'name': 'Datacenters',
				'icon': 'https://storage.googleapis.com/askdata/datasets/icons/icoDataBigQuery.png'
			},
			'connection': '',
			'executedSQLQuery': 'SELECT AVG(`traffic`) AS `alias_0` FROM `askdata.Atlassian.atlassian_datacenter` ORDER BY `alias_0` DESC LIMIT 50',
			'schema': schema_dict,
			'data': data_list,
			'filters': None,
			'sortedBy': None,
			'page': None,
			'limit': 50,
			'totalRecords': 1,
			'queryId': ''
		}
		# Return the dictionary
		return json_dict

	def run_query(query, df):
		
		### Query is a SQLite3
		#query = """
		#SELECT *
		#FROM df
		#WHERE col_1 IS NOT NULL;
		#"""
		###

		# Run the query

		df_results = sqldf.run(query)
		return 	df_to_resultset(df_results)

	dataset_settings_example = """{
	    "payload": {
	        "page": 0,
	        "totalElements": 8,
	        "data": [
	            {
	                "datasetId": "f324ef9a-279b-4105-901b-c47c624edf7f-DATA_TABLE-0d129d26-58e5-441f-b9b3-8c80efdeb094",
	                "schemaMetaData": {
	                    "columnId": "area_geografica",
	                    "columnName": "area_geografica",
	                    "dataType": "VARCHAR",
	                    "dataExample": "Calabria",
	                    "internalDataType": "STRING",
	                    "indexedWith": null,
	                    "join": null,
	                    "details": {}
	                },
	                "parameterType": "ENTITY_TYPE",
	                "code": "AREA_GEOGRAFICA",
	                "name": "Area geografica",
	                "description": null,
	                "synonyms": [
	                    "area",
	                    "geografia",
	                    "area geografica",
	                    "area geograficas",
	                    "regione"
	                ],
	                "icon": "",
	                "sampleQueries": [],
	                "importValues": true,
	                "mandatory": false,
	                "enabled": true,
	                "advancedConfiguration": {},
	                "viewValues": "View",
	                "custom": false,
	                "dynamicParameterValues": [],
	                "searchable": false,
	                "nameTransformer": null,
	                "synonymTransformers": null
	            }
	        ]
	    }
	}"""

	### Convert string_json_object in a denormalized dataframe """
	def dataset_settings_to_dataframe(dataset_settings):
	    """
	    Convert string_json_object in a denormalized dataframe
	    """
	    # Convert string_json_object in a json object
	    json_object = json.loads(dataset_settings)
	    # Convert json_object in a dataframe
	    df = pd.DataFrame(json_object['payload']['data'])
	    # Return the dataframe
	    return df

### Convert string_json_object in a denormalized dataframe """
#df = dataset_settings_to_dataframe(dataset_settings_example)

### Show the dataframe
#df

	### Convert dataframe in a json similar to the string_json_object one """
	def dataset_settings_dataframe_to_json(df):
	    """
	    Convert dataframe in a json similar to the string_json_object one
	    """
	    # Convert dataframe in a json object
	    json_object = df.to_json(orient='records')
	    # Convert json_object in a string
	    string_json_object = json.dumps(json_object)
	    # Return the string
	    return string_json_object

### Convert dataframe in a json similar to the string_json_object one """
#dataset_settings = dataset_settings_dataframe_to_json(df)

### Show the string_json_object
#dataset_settings


