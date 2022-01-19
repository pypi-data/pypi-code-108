from WhaleWisdom.Common.py_whale_wisdom import *
import pandas as pd

def get_prospect_holding_data(tickers, quarter_id):

    stock_data = pd.DataFrame()
    stock_ids = [int(x) for x in list(tickers["stock_id"])]
    if len(stock_ids) % 10 == 0:
        num_reqs = len(stock_ids) / 10
    else:
        num_reqs = (len(stock_ids) // 10) + 1
    for x in range(num_reqs):
        these_ids = stock_ids[x*10:(x+1)*10]
        api_input = '{"command":"holders","quarter_ids":[%d], "stock_ids":%s, "columns":[1,5,10,12,16], "hedge_funds_only":1}' % (quarter_id, these_ids)
        a = call_api(api_input)
        for stock_res in a["results"]:
            for holder in stock_res["records"]:
                for holding in holder["holdings"]:
                    data_dict = holding
                    data_dict["stock_id"] = stock_res["stock_id"]
                    stock_data = stock_data.append(data_dict, ignore_index=True)
    stock_data = stock_data.merge(tickers, on=["stock_id"])
    stock_data = filter_data(stock_data)
    return stock_data

def get_client_holding_data(clients, quarter_id):

    client_holdings = pd.DataFrame()
    if clients.shape[0] % 10 == 0:
        num_reqs = int(clients.shape[0] / 10)
    else:
        num_reqs = int((clients.shape[0] // 10) + 1)
    for x in range(num_reqs):
        these_ids = list(clients.iloc[x*10:(x+1)*10,:]["filer_id"])
        api_input = '{"command":"holdings","quarter_ids":[%d], "filer_ids":%s, "columns":[2,4,5,6,7,10,12,16,25]}' % (quarter_id, these_ids)
        a = call_api(api_input)
        for holder in a["results"]:
            holder_info = {"filer_id":holder["filer_id"]}
            for record in holder["records"]:
                for holding in record["holdings"]:
                    holding.update(holder_info)
                    client_holdings = client_holdings.append(holding, ignore_index=True)
    client_holdings = client_holdings.merge(clients[["filer_name","filer_id"]], on=["filer_id"])
    client_holdings = filter_data(client_holdings)
    return client_holdings

def filter_data(df):
    
    df = df[(~pd.isnull(df["current_percent_of_portfolio"])) & (~pd.isnull(df["current_mv"]))]
    return df[(df["current_percent_of_portfolio"] > 0) & (df["current_mv"] > 0)].drop_duplicates()
    