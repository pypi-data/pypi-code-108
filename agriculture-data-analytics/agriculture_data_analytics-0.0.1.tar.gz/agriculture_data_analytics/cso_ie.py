from pandas import DataFrame
import io
import pandas
import requests


def download_cso_table_data(table_code: str, file_type: str = "CSV", version: str = "1.0") -> str:
    """
    This function downloads the data from the CSO website.
    :param table_code: str
    :param file_type: str
    :param version: str
    return: str
    """
    BASE_URL = "https://ws.cso.ie/public/api.jsonrpc"
    JSON_DATA = f'{{"jsonrpc":"2.0","method":"PxStat.Data.Cube_API.ReadDataset","params":{{"class":"query","id":[],"dimension":{{}},"extension":{{"pivot":null,"codes":false,"language":{{"code":"en"}},"format":{{"type":"{file_type}","version":"{version}"}},"matrix":"{table_code}"}},"version":"2.0"}}}}'

    url = f"{BASE_URL}?data={JSON_DATA}"
    response_json_rpc = requests.get(url).json()
    print(f"Downloaded https://data.cso.ie/table/{table_code}")
    return response_json_rpc['result']


def download_cso_table_dataframe(table_code: str) -> DataFrame:
    """
    This function downloads the data from the CSO website.
    :param table_code: str
    return: DataFrame
    """
    string_io = io.StringIO(download_cso_table_data(table_code))
    return pandas.read_csv(string_io, sep=",")
