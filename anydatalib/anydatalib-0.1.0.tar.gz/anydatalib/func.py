import requests

def get_table_as_excel(table_name):
    try:
        result = requests.get(f"http://127.0.0.1:8000/tabletocsv/?table_name={table_name}")
        return result
    except:
        return "Something went wrong or no Data has been found!"