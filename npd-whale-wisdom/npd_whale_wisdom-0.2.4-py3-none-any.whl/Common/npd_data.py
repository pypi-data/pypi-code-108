from WhaleWisdom.Common.py_whale_wisdom import *
import pandas as pd
import bs4

def get_covered_tickers(npd_tickers):
    '''
    Takes dataframe with NPD Tickers as input.
    Must have stock_name and stock_ticker columns.
    Searches WW database for matching stocks and retrieves their ID's
    '''
    npd_tickers = npd_tickers.rename(columns={"stock_name":"npd_stock_name"})
    ww_tickers = get_ww_tickers()
    npd_ww = npd_tickers.merge(ww_tickers, on=["stock_ticker"])
    valid_stocks = []
    for ticker in npd_ww["stock_ticker"].unique():
        stock_lookup = call_api('{"command":"stock_lookup","symbol":"%s"}' % ticker)
        for stock in stock_lookup["stocks"]:
            if stock["status"] == "Active":
                valid_stocks.append(stock["id"])
    npd_ww = npd_ww[npd_ww["stock_id"].isin(valid_stocks)]
    #some stock names will return multiple results
    #pick the best result based on similarity of names
    dups = list(npd_ww[npd_ww.duplicated("stock_ticker")]["stock_ticker"].unique())
    to_remove = []
    for dup_ticker in dups:
        dup_rows = npd_ww[npd_ww["stock_ticker"] == dup_ticker]
        best_id = None
        best_score = 0
        for ind, row in dup_rows.iterrows():
            correct_words = row["npd_stock_name"].lower().replace(",","").replace(".","").split()
            test_words = row["stock_name"].lower().replace(",","").replace(".","").split()
            score = len([x for x in test_words if x in correct_words]) / len(test_words)
            if score > best_score:
                best_score = score
                best_id = row["stock_id"]
        to_remove += [x for x in dup_rows["stock_id"] if x != best_id]
    return npd_ww[~npd_ww["stock_id"].isin(to_remove)]

def get_covered_clients(npd_clients):
    '''
    Takes NPD Financial Clients as DataFrame
    DataFrame must have filer_name and group as columns
    '''
    npd_clients["filer_name"] = npd_clients["filer_name"].apply(lambda x: x.replace(",",""))
    filers = get_ww_filers()
    npd_clients = npd_clients.merge(filers[["filer_id","filer_name","city","state"]], on=["filer_name"])
    npd_clients["Account_Manager"] = npd_clients["group"].apply(lambda x: "NA" if x == "Enterprise" else x)
    npd_clients["Enterprise_client"] = npd_clients["group"].apply(lambda x: "Enterprise" if x == "Enterprise" else "No")
    npd_clients["Client_Type"] = npd_clients["group"].apply(lambda x: "Enterprise" if x == "Enterprise" else "TIR or Other")
    return npd_clients[["filer_id","filer_name","city","state","Enterprise_client","Client_Type","Account_Manager"]]

def get_ww_tickers():
    #retrieves current stock list from WhaleWisdom
    df = pd.read_csv("https://whalewisdom.com/stocks.csv")
    df = df.rename(columns={"id":"stock_id","name":"stock_name","symbol":"stock_ticker"})
    return df

def get_ww_filers():
    #retrieves current filer list from WhaleWisdom
    filers = pd.read_csv("https://whalewisdom.com/filers.csv")
    filers = filers.rename(columns={"id":"filer_id", "name":"filer_name"})
    return filers


def parse_groups_page(path):
    '''
    Helper function to parse HTML file from Whale Wisdom account page.
    Save the browser page as HTML, and use the downloaded file to create
    DataFrame with NPD financial clients and their client groups.
    '''
    with open(path) as f:
        soup = bs4.BeautifulSoup(f, "html.parser")
    clients = pd.DataFrame()
    client_table = soup.find("div", class_="v-data-table__wrapper").find("table")
    groups = client_table.find_all("tr")[1:]
    for group in groups:
        group_name = group.find("td").text.replace("\n","").strip()
        for fund in group.find_all("a"):
            fund_name = fund.find("strong").text
            clients = clients.append({"filer_name":fund_name, "group":group_name}, ignore_index=True)
    clients = clients.drop_duplicates("filer_name")
    return clients