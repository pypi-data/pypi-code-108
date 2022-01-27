from datetime import datetime
import requests
import json
import math
import pandas as pd
from typing import List, Optional, Union
import aiohttp
import asyncio
import numpy as np
import logging


class RkdClient:
    token = None
    base_url ='https://api.rkd.refinitiv.com/api/'

    def __init__(self, appid:str,username:str,password:str):
        self.appid = appid
        self.username = username
        self.password = password
        self.headers = {"content-type": "application/json;charset=utf-8"}
        self.timeout = 10
        self.validate_token()

    async def snapshot_gather_request(self, endpoint, payload, headers):
        url = f"{self.base_url}{endpoint}"
        
        async with aiohttp.ClientSession(headers=headers) as session:

            responses = []
            for data in payload:
                responses.append(
                    asyncio.ensure_future(
                        self.async_send_request_snapsot(session, url, data)
                    )
                )

            original_responses = await asyncio.gather(*responses)
            return original_responses

    async def async_send_request_snapsot(self, session, endpoint, payload):
        url = f"{self.base_url}{endpoint}"
        async with session.post(url, data=json.dumps(payload)) as resp:
            response = await resp.json()
            status = resp.status

            if status == 200:
                return response
            else:
                response = {
                    "ticker": payload["GetRatiosReports_Request_1"][
                        "companyId"
                    ],
                    "Error": response,
                    "AREV": None,
                    "MKTCAP": None,
                    "PEEXCLXOR": None,
                    "ProjPE": None,
                    "APRICE2BK": None,
                    "AEBITD": None,
                    "NHIG": None,
                    "NLOW": None,
                    "ACFSHR": None,
                }
                return response

    def validate_token(self):
        if self.is_valid_token:
            logging.info("valid token")
            logging.info("using existing token")
            self.token = self.token
        else:
            self.token = self.get_token()

    def send_request(self, endpoint:str, payload:dict, headers:dict)->dict:
        result = None
        url = f"{self.base_url}{endpoint}"
        try:
            result = requests.post(
                url,
                data=json.dumps(payload),
                headers=headers,
                timeout=self.timeout,
            )
            if result.status_code != 200:

                logging.warning("Request fail")
                logging.warning(f"request url :  {url}")
                logging.warning(f"request header :  {headers}")
                logging.warning(f"response status {result.status_code}")
                if (
                    result.status_code == 500
                ):  # if username or password or appid is wrong
                    logging.warning(
                        "Error: %s" % (json.dumps(result.json(), indent=2))
                    )
                    return None
        except requests.exceptions.RequestException as e:
            logging.error(f"error : {str(e)}")
            raise Exception("request error")
        except requests.Timeout:
            raise Exception("cannot get price data, waited to loong")
        return result.json()

    def get_token(self)-> str:
        authenMsg = {
            "CreateServiceToken_Request_1": {
                "ApplicationID": self.appid,
                "Username": self.username,
                "Password": self.password,
            }
        }
        authenURL = "TokenManagement/TokenManagement.svc/REST/Anonymous/TokenManagement_1/CreateServiceToken_1"
        logging.info("logged you in")
        logging.info("requesting new token")
        response = self.send_request(authenURL, authenMsg, self.headers)
        if response:
            self.token = response["CreateServiceToken_Response_1"][
                "Token"
            ]
            return self.token

    @property
    def is_valid_token(self)->bool:
        if not self.token:
            return False
        payload = {
            "ValidateToken_Request_1": {
                "ApplicationID": self.appid,
                "Token": self.token,
            }
        }
        headers = self.auth_headers()
        validate_url = "TokenManagement/TokenManagement.svc/REST/TokenManagement_1/ValidateToken_1"
        retry = 0
        while True:
            response = self.send_request(validate_url, payload, headers)
            if response:
                break
            else:
                retry += 1
                self.get_token()
                payload["ValidateToken_Request_1"][
                    "Token"
                ] = self.token
                headers["X-Trkd-Auth-Token"] = self.token
                response = self.send_request(validate_url, payload, headers)
            if retry >= 3:
                raise ConnectionError(f"failed after, retry {retry} times")

        return response["ValidateToken_Response_1"]["Valid"]

    def auth_headers(self)->dict:
        headers = self.headers
        headers["X-Trkd-Auth-ApplicationID"] = self.appid
        headers["X-Trkd-Auth-Token"] = self.token
        return headers

    def parse_response(self, response:dict)->dict:
        if response:
            json_data = response.get("RetrieveItem_Response_3", {}).get(
                "ItemResponse", []
            )
            if json_data:
                data = json_data[0].get("Item", None)
                if not data:
                    logging.error(response)
                    raise Exception(response)
                formated_json_data = []
                for index, item in enumerate(data):
                    ticker = item["RequestKey"]["Name"]
                    formated_json_data.append({"ticker": ticker})
                    if item["Status"]["StatusMsg"] == "OK":
                        for f in item["Fields"]["F"]:
                            field = f["n"]
                            val = f.get("Value", 0)
                            formated_json_data[index].update({field: val})
                    else:
                        logging.warning(
                            f"error status message {item['Status']['StatusMsg']} for {ticker}, there is no response data"
                        )
            return formated_json_data
        logging.error(response)
        raise Exception(response)


    def retrive_template(self, ticker:Union[list,str], scope="List", fields=""):

        if scope == "List":
            if not fields or fields == "":
                raise ValueError(
                    "fields keyword argument must set if scope is list"
                )
            field = (",").join(fields)
            fields = field.replace(",", ":")
        payload = {
            "RetrieveItem_Request_3": {
                "ItemRequest": [
                    {"Fields": fields, "RequestKey": [], "Scope": scope}
                ],
                "TrimResponse": True,
                "IncludeChildItemQoS": False,
            }
        }
        if isinstance(ticker, str):
            payload["RetrieveItem_Request_3"]["ItemRequest"][0][
                "RequestKey"
            ].append({"Name": ticker, "NameType": "RIC"})

        elif isinstance(ticker, list):
            for tic in ticker:
                payload["RetrieveItem_Request_3"]["ItemRequest"][0][
                    "RequestKey"
                ].append({"Name": tic, "NameType": "RIC"})

        return payload

    def get_snapshot(self, ticker:Union[list,str], df:bool=False)-> Optional[Union[pd.DataFrame, List[dict]]]:
        snapshot_url = "Fundamentals/Fundamentals.svc/REST/Fundamentals_1/GetRatiosReports_1"
        list_formated_json = []
        if isinstance(ticker, list):
            list_payload = []
            for tic in ticker:
                payload = {
                    "GetRatiosReports_Request_1": {
                        "companyId": tic,
                        "companyIdType": "RIC",
                    }
                }
                list_payload.append(payload)
            responses = asyncio.run(
                self.snapshot_gather_request(
                    snapshot_url, list_payload, self.auth_headers()
                )
            )

            for response in responses:
                if not "Error" in response:
                    base_response = response["GetRatiosReports_Response_1"][
                        "FundamentalReports"
                    ]["ReportRatios"]

                    formated_json = {}
                    formated_json["ticker"] = base_response["Issues"]["Issue"][
                        0
                    ]["IssueID"][2]["Value"]
                    fields = [
                        "AREV",
                        "MKTCAP",
                        "PEEXCLXOR",
                        "ProjPE",
                        "APRICE2BK",
                        "AEBITD",
                        "NHIG",
                        "NLOW",
                        "ACFSHR",
                    ]
                    for group_item in base_response["Ratios"]["Group"]:
                        for item in group_item["Ratio"]:
                            if item["FieldName"] in fields:
                                formated_json[item["FieldName"]] = item["Value"]
                    for group_item in base_response["ForecastData"]["Ratio"]:
                        if group_item["FieldName"] in fields:
                            formated_json[group_item["FieldName"]] = group_item[
                                "Value"
                            ][0]["Value"]
                    list_formated_json.append(formated_json)
                elif "Error" in response:
                    list_formated_json.append(response)
                else:
                    print(response)
        else:
            payload = {
                "GetRatiosReports_Request_1": {
                    "companyId": ticker,
                    "companyIdType": "RIC",
                }
            }
            response = self.send_request(
                snapshot_url, payload, self.auth_headers()
            )
            base_response = response["GetRatiosReports_Response_1"][
                "FundamentalReports"
            ]["ReportRatios"]

            formated_json = {}
            formated_json["ticker"] = base_response["Issues"]["Issue"][0][
                "IssueID"
            ][2]["Value"]
            fields = [
                "AREV",
                "MKTCAP",
                "PEEXCLXOR",
                "ProjPE",
                "APRICE2BK",
                "AEBITD",
                "NHIG",
                "NLOW",
                "ACFSHR",
            ]
            for group_item in base_response["Ratios"]["Group"]:
                for item in group_item["Ratio"]:
                    if item["FieldName"] in fields:
                        formated_json[item["FieldName"]] = item["Value"]
            for group_item in base_response["ForecastData"]["Ratio"]:
                if group_item["FieldName"] in fields:
                    formated_json[group_item["FieldName"]] = group_item[
                        "Value"
                    ][0]["Value"]
            list_formated_json.append(formated_json)
        df_data = pd.DataFrame(list_formated_json).rename(
            columns={
                "AREV": "revenue_per_share",
                "MKTCAP": "market_cap",
                "PEEXCLXOR": "pe_ratio",
                "ProjPE": "pe_forecast",
                "APRICE2BK": "pb",
                "AEBITD": "ebitda",
                "NHIG": "wk52_high",
                "NLOW": "wk52_low",
                "ACFSHR": "free_cash_flow",
            }
        )
        if df:
            return df_data
        return formated_json

    def get_data_from_rkd(self, identifier, field):
        quote_url = "Quotes/Quotes.svc/REST/Quotes_1/RetrieveItem_3"
        split = round(len(identifier) / min(50, len(identifier)))
        collected_data = []
        splitting_df = np.array_split(identifier, max(split, 1))
        for universe in splitting_df:
            tick = universe.tolist()
            payload = self.retrive_template(tick, fields=field)
            response = self.send_request(
                quote_url, payload, self.auth_headers()
            )
            formated_json_data = self.parse_response(response)
            result = pd.DataFrame(formated_json_data)
            collected_data.append(result)
        collected_data = pd.concat(collected_data)
        return result

    def get_index_price(self, index: str) -> float:
        quote_url = "Quotes/Quotes.svc/REST/Quotes_1/RetrieveItem_3"
        payload = self.retrive_template(
            index, fields=["CF_CLOSE"]
        )
        response = self.send_request(quote_url, payload, self.auth_headers())

        formated_json_data = self.parse_response(response)
        price = formated_json_data[0].get("CF_CLOSE",None)
        if not price:
            raise Exception("No price found")
        return float(price)

    def response_to_df(self, response: dict) -> pd.DataFrame:
        formated_json_data = self.parse_response(response)
        # jsonprint(formated_json_data)
        float_fields = [
            "CF_ASK",
            "CF_CLOSE",
            "CF_BID",
            "CF_HIGH",
            "CF_LOW",
            "PCTCHNG",
            "CF_VOLUME",
            "CF_LAST",
            "CF_NETCHNG",
            "CF_OPEN",
            "YIELD",
        ]
        parser_data = {
            "CF_ASK": "intraday_ask",
            "CF_OPEN": "open",
            "CF_CLOSE": "close",
            "CF_BID": "intraday_bid",
            "CF_HIGH": "high",
            "CF_LOW": "low",
            "PCTCHNG": "latest_price_change",
            "TRADE_DATE": "last_date",
            "CF_VOLUME": "volume",
            "CF_LAST": "latest_price",
            "CF_NETCHNG": "latest_net_change",
            "YIELD": "dividen_yield",
        }
        float_data = {
            "intraday_ask": "float",
            "close": "float",
            "open": "float",
            "intraday_bid": "float",
            "high": "float",
            "low": "float",
            "latest_price_change": "float",
            "volume": "float",
            "latest_price": "float",
            "latest_net_change": "float",
            "dividen_yield": "float",
        }

        for parsed_data in formated_json_data:
            for field in float_fields:
                values = parsed_data.get(field, 0)
                if field == "CF_LAST" and float(values) == 0:
                    values = parsed_data.get("CF_CLOSE", 0)
                if field == "CF_OPEN" and float(values) == 0:
                    values = parsed_data.get("CF_LAST", 0)
                if float(values) != 0:
                    parsed_data[field] = values
        df_data = pd.DataFrame(formated_json_data)
        df_data = df_data.rename(
            columns={k: v for k, v in parser_data.items() if k in df_data}
        )
        # print(df_data)
        df_data["last_date"] = str(datetime.now().date())
        df_data["intraday_date"] = str(datetime.now().date())

        df_data["intraday_time"] = str(datetime.now())
        df_data = df_data.astype(
            {k: v for k, v in float_data.items() if k in df_data}
        )
        return df_data

    async def quote_gather_request(
        self, url: str, payload: list, headers: dict
    ) -> List[pd.DataFrame]:
        async with aiohttp.ClientSession(headers=headers) as session:

            responses = []
            for data in payload:
                responses.append(
                    asyncio.ensure_future(
                        self.async_send_request_quote(session, url, data)
                    )
                )

            original_responses = await asyncio.gather(*responses)
            return original_responses

    async def async_send_request_quote(
        self, session, url, payload
    ) -> pd.DataFrame:
        async with session.post(url, data=json.dumps(payload)) as resp:
            response = await resp.json()
            status = resp.status

            if status == 200:
                return self.response_to_df(response)
            else:
                raise Exception(response)

    def bulk_get_quote(
        self, ticker: list, df=False
    ) -> Optional[Union[pd.DataFrame, List[dict]]]:
        quote_url = "Quotes/Quotes.svc/REST/Quotes_1/RetrieveItem_3"
        split = len(ticker) / 50
        if split < 2:
            split = math.ceil(split)
        splitting_df = np.array_split(ticker, split)
        bulk_payload = []
        for universe in splitting_df:
            ticker = universe.tolist()
            payload = self.retrive_template(
                ticker,
                fields=[
                    "CF_ASK",
                    "CF_OPEN",
                    "CF_CLOSE",
                    "CF_BID",
                    "PCTCHNG",
                    "CF_HIGH",
                    "CF_LOW",
                    "CF_LAST",
                    "CF_VOLUME",
                    "TRADE_DATE",
                    "CF_NETCHNG",
                    "YIELD",
                ],
            )
            bulk_payload.append(payload)

        self.validate_token()

        response: List[pd.DataFrame] = asyncio.run(
            self.quote_gather_request(
                quote_url, bulk_payload, self.auth_headers()
            )
        )
        data: pd.DataFrame = pd.concat(response, ignore_index=True)
        if df:
            return data
        return data.to_dict("records")

    def get_quote(self, ticker:Union[list,str], df:bool=False)-> Optional[Union[pd.DataFrame, List[dict]]]:
        """
        get quote for a ticker can be a list or str
        run syncrhonously
        """
        import math

        if isinstance(ticker, str):
            ticker = [ticker]
        quote_url = "Quotes/Quotes.svc/REST/Quotes_1/RetrieveItem_3"
        split = len(ticker) / 50
        collected_data = []
        if split < 2:
            split = math.ceil(split)
        splitting_df = np.array_split(ticker, split)
        for universe in splitting_df:
            ticker = universe.tolist()
            # print(len(ticker))
            payload = self.retrive_template(
                ticker,
                fields=[
                    "CF_ASK",
                    "CF_OPEN",
                    "CF_CLOSE",
                    "CF_BID",
                    "PCTCHNG",
                    "CF_HIGH",
                    "CF_LOW",
                    "CF_LAST",
                    "CF_VOLUME",
                    "TRADE_DATE",
                    "CF_NETCHNG",
                    "YIELD",
                ],
            )
            response = self.send_request(
                quote_url, payload, self.auth_headers()
            )

            formated_json_data = self.parse_response(response)
            df_data = pd.DataFrame(formated_json_data).rename(
                columns={
                    "CF_ASK": "intraday_ask",
                    "CF_CLOSE": "close",
                    "CF_OPEN": "open",
                    "CF_BID": "intraday_bid",
                    "CF_HIGH": "high",
                    "CF_LOW": "low",
                    "PCTCHNG": "latest_price_change",
                    "TRADE_DATE": "last_date",
                    "CF_VOLUME": "volume",
                    "CF_LAST": "latest_price",
                    "CF_NETCHNG": "latest_net_change",
                    "YIELD": "dividen_yield",
                }
            )
            df_data["last_date"] = str(datetime.now().date())
            df_data["intraday_date"] = str(datetime.now().date())
            df_data["intraday_time"] = str(datetime.now())
            collected_data.append(df_data)
        collected_data = pd.concat(collected_data, ignore_index=True)
        if df:
            # rename column match in table
            return collected_data
        return collected_data.to_dict("records")

    def get_rkd_data(self, ticker):
        """getting all data from RKD and save,function has no return"""

        self.get_snapshot(ticker)
        self.bulk_get_quote(ticker)


