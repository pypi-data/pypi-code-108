from WhaleWisdom.FundHoldings.report_builder import create_client_report, create_prospect_report_v1, create_prospect_report_v2
import pandas as pd
from WhaleWisdom.Common.npd_data import *
from WhaleWisdom.FundHoldings.report_data import *
import datetime
import os
import logging

def main(report_type, quarter, npd_tickers, npd_clients, manual, output_path, create_charts):

    if manual:
        logging.basicConfig(level=logging.INFO)
        logging.info("Cross referencing ticker data...")
    covered_tickers = get_covered_tickers(npd_tickers)
    if manual:
        logging.info("Consolidated NPD and WW stock data...")
    quarter_id = get_quarter(quarter)
    if report_type == "ProspectV1":
        if manual:
            logging.info("Getting prospect report data...")
        data = get_prospect_holding_data(covered_tickers, quarter_id)
        if manual:
            logging.info("Prospect report data retrieved...")
            logging.info("Building Prospect Report V1...")
        create_prospect_report_v1(data, quarter, output_path)
        if manual:
            logging.info("Prospect report V1 finished...")
    elif report_type == "ProspectV2":
        if manual:
            logging.info("Getting prospect report data...")
        data = get_prospect_holding_data(covered_tickers, quarter_id)
        if manual:
            logging.info("Prospect report data retrieved...")
            logging.info("Building Prospect Report V2...")
        create_prospect_report_v2(data, quarter, output_path)
        if manual:
            logging.info("Prospect report V2 finished...")
    elif report_type == "Client":
        if manual:
            logging.info("Cross referencing Client data...")
        covered_clients = get_covered_clients(npd_clients)
        if manual:
            logging.info("Consolidated NPD and WW filer data...")
            logging.info("Getting client report data...")
        data = get_client_holding_data(covered_clients, quarter_id)
        if manual:
            logging.info("Client report data retrieved...")
            logging.info("Building Client Report...")
        create_client_report(data, covered_tickers, covered_clients, quarter, output_path, create_charts)
        if manual:
            logging.info("Client report finished...")

if __name__ == '__main__':
    
    while True:
        report_type = input("Enter Report Type (Prospect/Client): ").strip()
        if report_type in ["Prospect","Client"]:
            break
        print("Invalid Response...")
    
    while True:
        quarter = input("Enter end date for desired quarter (format: 03/31/2021): ")
        try:
            given_date = datetime.datetime.strptime(quarter, "%m/%d/%Y")
        except:
            print("Incorrect Date format...")
            continue
        if (given_date.month, given_date.day) not in [(3,31),(6,30),(9,30),(12,31)]:
            print("Date is not end of quarter...")
            continue
        break
    while True:
        npd_tickers_path = input("Enter path to NPD tickers CSV (ex: c:/Users/Max Leonard/Documents/npd_tickers.csv) ")
        try:
            npd_tickers = pd.read_csv(npd_tickers_path)
        except:
            print("Incorrect file format or path...")
            continue
        if "stock_name" not in npd_tickers.columns:
            print("stock_name column not found in file...")
            continue
        if "stock_ticker" not in npd_tickers.columns:
            print("stock_ticker column not found in file...")
            continue
        break
    if report_type == "Client":
        while True:
            npd_clients_path = input("Enter path to NPD Client Groups CSV (ex: c:/Users/Max Leonard/Documents/fund_client_groups.csv): ")
            try:
                npd_clients = pd.read_csv(npd_clients_path)
            except:
                print("Incorrect file format or path...")
                continue
            if "filer_name" not in npd_clients.columns:
                print("filer_name column not found in file...")
                continue
            if "group" not in npd_clients.columns:
                print("group column not found in file...")
                continue
            break
        while True:
            output_path = input("Enter path to output Excel file: ")
            if not os.path.isdir(output_path):
                print("Provided output path is not directory...")
                continue
            break
        while True:
            create_charts = input("Include Client Holdings Charts? (y/n) ")
            if create_charts.lower() == "y":
                create_charts = True
                break
            elif create_charts.lower() == "n":
                create_charts = False
                break
            else:
                print("Invalid repsonse...")
        main(report_type, quarter, npd_tickers, npd_clients, True, output_path, create_charts)
    else:
        while True:
            output_path = input("Enter path to output Excel file: ")
            if not os.path.isdir(output_path):
                print("Provided output path is not directory...")
                continue
            break
        main(report_type, quarter, npd_tickers, None, True, output_path, False)