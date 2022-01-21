import json
from websocket import create_connection
import requests
import urllib
import logging

logger = logging.getLogger(__name__)

SYMBOL_SWITCHER = {
    "BTCUSDT": "BTC/USDT"
}

POSITION_TYPES = {
    "long": 1,
    "short": 2
}

ORDER_TYPES = {
    "stop_order": 0,
    "target_order": 1,
    "limit_order": 2,
}

REVERTED_POSITION_TYPES = {v: k for k, v in POSITION_TYPES.items()}
REVERTED_ORDER_TYPES = {v: k for k, v in ORDER_TYPES.items()}

DOMAIN = 'e1.quantfury.com'
WEBSOCKET_DOMAIN = 'a1.quantfury.com'
VERSION = 'v7'
NEGOTIATE_URL = "https://{}/signalr/negotiate?clientProtocol=2.1&_=1626042979667".format(WEBSOCKET_DOMAIN)
WEBSOCKET_URL = 'wss://{domain}/signalr/connect'\
                '?transport=webSockets&clientProtocol=2.1&connectionToken={{}}&tid=0'.format(domain=WEBSOCKET_DOMAIN)

common_headers = {
    "Host": "e1.quantfury.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json;charset=utf-8",
    "Origin": "https://trading.quantfury.com",
    "Connection": "keep-alive",
    "Referer": "https://trading.quantfury.com/"
}


class Utils:

    @classmethod
    def reformat_symbol(cls, symbol):
        if type(symbol) is not str:
            raise ValueError('Invalid symbol Type')
        if symbol in SYMBOL_SWITCHER:
            return SYMBOL_SWITCHER[symbol]
        elif symbol.find('/') < 0:
            logger.warning('func=Utils.reformat_symbol, symbol={}, msg=Symbol should have Slash'.format(symbol, ))
        return symbol

    @classmethod
    def get_connection_token(cls):
        status_code, reason = None, None
        payload = {}
        headers = {}
        try:
            raw_response = requests.request("GET", NEGOTIATE_URL, headers=headers, data=payload)

            status_code, reason = raw_response.status_code, raw_response.reason
            response = raw_response.json()

            connection_token = response['ConnectionToken']
            connection_token = urllib.parse.quote(connection_token)

            return connection_token
        except Exception as e:
            logger.critical('func=Utils.get_connection_token, status_code={}, reason={}, msg={}'.format(
                status_code, reason, e))
            raise e

    @classmethod
    def get_price_id(cls, symbol):
        return cls.get_latest_price_and_id(symbol)[1]

    @classmethod
    def get_latest_price(cls, symbol):
        return cls.get_latest_price_and_id(symbol)[0]

    @classmethod
    def get_latest_price_and_id(cls, symbol):
        try:
            symbol = cls.reformat_symbol(symbol)
            connection_token = cls.get_connection_token()

            headers = json.dumps({

            })
            ws = create_connection(
                WEBSOCKET_URL.format(
                    connection_token), headers=headers)

            ws.send(json.dumps({"H": "priceshub", "M": "SubscribeToPriceStreams", "A": [[symbol]], "I": 0}))

            for _ in range(10000):
                result = ws.recv()
                if result.find('"shortName":"{}"'.format(symbol)) > 0 and result.find('"id":"') > 0:
                    price_data = json.loads(result)
                    return price_data['M'][0]['A'][0]['price'], price_data['M'][0]['A'][0]['id']
        except Exception as e:
            logger.critical('func=Utils.get_latest_price_and_id, symbol={}, msg={}'.format(symbol, e))
            raise e

    @classmethod
    def get_test_limit_stop_target_prices(cls, symbol):
        buy_price = Utils.get_latest_price(symbol)
        buy_price = buy_price - (buy_price % 100) - 50
        stop_price, target_price = buy_price - 1000, buy_price + 1000
        return buy_price, stop_price, target_price

    @classmethod
    def get_device_id(cls):
        return "ead2ce58-63e1-414d-bda7-104f0069edd0"


class Quantfury:
    def __init__(self, token):
        self.token = token

    def create_OCO_long_order(self, symbol, quote_order_quantity, buy_price, stop_price, target_price, position_type):
        """
        Create OCO long order
        Parameters
        ----------
        symbol
        quote_order_quantity
        buy_price
        stop_price
        target_price
        position_type

        Returns
        -------

        """
        url = 'https://{domain}/{version}/limitOrder/create'.format(domain=DOMAIN, version=VERSION)
        status_code, reason, error_code, error_message, stage = None, None, None, None, 'API.first_attempt'
        try:
            latest_price, price_id = Utils.get_latest_price_and_id(symbol)
            body = {
                "priceId": price_id,
                "price": buy_price,
                "value": {
                    "amountSystem": quote_order_quantity
                },
                "stopOrder": stop_price,
                "targetOrder": target_price,
                "positionType": POSITION_TYPES[position_type],
                "executionType": 0,
                "shortName": symbol
            }
            headers = self.get_headers()
            raw_response = requests.post(url, json=body, headers=headers)

            status_code, reason = raw_response.status_code, raw_response.reason or None
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)

            if error_code == 'InvalidLimitOrderPrice':
                stage = 'API.second_attempt'
                body['price'] = latest_price
                raw_response = requests.post(url, json=body, headers=headers)

                status_code, reason = raw_response.status_code, raw_response.reason or None
                json_result = raw_response.json()
                error_code, error_message = json_result.get('code', None), json_result.get('error', None)

            return json_result
        except Exception as e:
            logger.critical(
                'func=Quantfury.create_OCO_long_order, symbol={}, quote_order_quantity={}, buy_price={}, '
                'stop_price={}, target_price={}, position_type={}, status_code={}, reason={}, error_code={}, '
                'error_message={}, stage={}, msg={}'.format(
                    symbol, quote_order_quantity, buy_price, stop_price, target_price, position_type, status_code,
                    reason, error_code, error_message, stage, e))
            raise e

    def create_limit_long_order(self, symbol, quote_order_quantity, buy_price, position_type):
        """
        Create long limit order
        Parameters
        ----------
        symbol
        quote_order_quantity
        buy_price
        position_type

        Returns
        -------

        """
        url = 'https://{domain}/{version}/limitOrder/create'.format(domain=DOMAIN, version=VERSION)
        status_code, reason, error_code, error_message = None, None, None, None
        try:
            body = {
                "priceId": Utils.get_price_id(symbol),
                "price": buy_price,
                "executionType": 0,
                "value": {
                    "amountSystem": quote_order_quantity
                },
                "positionType": POSITION_TYPES[position_type],
                "shortName": symbol
            }
            headers = self.get_headers()
            raw_response = requests.post(url, json=body, headers=headers)

            status_code, reason = raw_response.status_code, raw_response.reason
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)


            return json_result
        except Exception as e:
            logger.critical(
                'func=Quantfury.create_limit_long_order, symbol={}, '
                'status_code={}, reason={}, error_code={}, error_message={}, msg={}'.format(
                    symbol, status_code, reason, error_code, error_message, e))
            raise e

    def create_market_order(self, symbol, quote_order_quantity, position_type):
        """
        Create market order
        Parameters
        ----------
        symbol
        quote_order_quantity
        position_type

        Returns
        -------

        """
        url = 'https://{domain}/{version}/positions/open'.format(domain=DOMAIN, version=VERSION)
        status_code, reason, error_code, error_message = None, None, None, None
        try:
            body = {
                "shortName": symbol,
                "positionType": POSITION_TYPES[position_type],
                "priceId": Utils.get_price_id(symbol),
                "targetOrders": [],
                "stopOrders": [],
                "value": {
                    "amountSystem": quote_order_quantity
                }
            }
            headers = self.get_headers()
            raw_response = requests.post(url, json=body, headers=headers)

            status_code, reason = raw_response.status_code, raw_response.reason
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)


            return json_result
        except Exception as e:
            logger.critical(
                'func=Quantfury.create_market_order, symbol={}, '
                'status_code={}, reason={}, error_code={}, error_message={}, msg={}'.format(
                    symbol, status_code, reason, error_code, error_message, e))
            raise e

    def update_position(self, api_order_id, symbol, price_value, quote_order_quantity, order_type):
        """
        Update a position
        Parameters
        ----------
        position_id : str
            Position ID
        symbol : str
            Asset symbol
        price_value : float
        quote_order_quantity : int
            Quantity in usdt
        order_type : str
            Order type stop_order: 0, target_order: 1, limit_order: 2

        Returns
        -------
        dict
            Data of the position
        """
        url = 'https://{domain}/{version}/reduceOrders/update'.format(domain=DOMAIN, version=VERSION)
        status_code, reason, error_code, error_message = None, None, None, None
        try:
            if order_type not in ORDER_TYPES:
                raise ValueError('Invalid order_type <{}> must be {}'.format(order_type, ';'.join(ORDER_TYPES.keys())))
            body = {
                "price": price_value,
                "id": api_order_id,
                "value": {
                    "amountSystem": quote_order_quantity
                }
            }
            headers = self.get_headers()
            raw_response = requests.post(url, json=body, headers=headers)

            status_code, reason = raw_response.status_code, raw_response.reason
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)

            return json_result
        except Exception as e:
            logger.critical(
                'func=Quantfury.update_position, symbol={}, '
                'status_code={}, reason={}, error_code={}, error_message={}, msg={}'.format(
                    symbol, status_code, reason, error_code, error_message, e))
            raise e

    def create_position(self, position_id, symbol, price_value, quote_order_quantity, order_type):
        """
        Update a position
        Parameters
        ----------
        position_id : str
            Position ID
        symbol : str
            Asset symbol
        price_value : float
        quote_order_quantity : int
            Quantity in usdt
        order_type : str
            Order type stop_order: 0, target_order: 1, limit_order: 2

        Returns
        -------
        dict
            Data of the position
        """
        url = 'https://{domain}/{version}/reduceOrders/create'.format(domain=DOMAIN, version=VERSION)
        status_code, reason, error_code, error_message = None, None, None, None
        try:
            if order_type not in ORDER_TYPES:
                raise ValueError('Invalid order_type <{}> must be {}'.format(order_type, ';'.join(ORDER_TYPES.keys())))
            body = {
                "price": price_value,
                "tradingPositionId": position_id,
                "orderType": ORDER_TYPES[order_type],
                "value": {
                    "amountSystem": quote_order_quantity
                }
            }
            headers = self.get_headers()
            raw_response = requests.post(url, json=body, headers=headers)

            status_code, reason = raw_response.status_code, raw_response.reason
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)

            return json_result
        except Exception as e:
            logger.critical(
                'func=Quantfury.create_position, symbol={}, '
                'status_code={}, reason={}, error_code={}, error_message={}, msg={}'.format(
                    symbol, status_code, reason, error_code, error_message, e))
            raise e

    def update_order(self, order_id, symbol, buy_price, stop_price, target_price, quote_order_quantity, order_type):
        """
        Update an order
        Parameters
        ----------
        order_id : str
            Order id
        symbol : str
            Asset symbol
        buy_price : float
            Buy price
        stop_price : float
            Stop price
        target_price : float
            target price
        quote_order_quantity : int
            Quantity in Dollars
        order_type : str
            Order type stop_order: 0, target_order: 1, limit_order: 2
        Returns
        -------
        dict
            Data of order

        """
        url = 'https://{domain}/{version}/limitOrder/update'.format(domain=DOMAIN, version=VERSION)
        status_code, reason, error_code, error_message = None, None, None, None
        try:
            if order_type not in ORDER_TYPES:
                raise ValueError('Invalid order_type <{}> must be {}'.format(order_type, ';'.join(ORDER_TYPES.keys())))
            body = {
                "priceId": Utils.get_price_id(symbol),
                "price": buy_price,
                "executionType": 0,
                "value": {
                    "amountSystem": quote_order_quantity
                },
                "stopOrder": stop_price,
                "targetOrder": target_price,
                "id": order_id
            }
            headers = self.get_headers()
            raw_response = requests.post(url, json=body, headers=headers)

            status_code, reason = raw_response.status_code, raw_response.reason
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)

            return json_result
        except Exception as e:
            logger.critical(
                'func=Quantfury.update_order, order_id={}, symbol={}, '
                'status_code={}, reason={}, error_code={}, error_message={}, msg={}'.format(
                    order_id, symbol, status_code, reason, error_code, error_message, e))
            raise e

    @classmethod
    def login(cls, username, password):
        """

        Parameters
        ----------
        username : str
            Username of a Quantfury Account
        password : str
            Password of a Quantfury Account
        Returns
        -------
        dict
            Dict with token field
        """
        status_code, reason, error_code, error_message = None, None, None, None
        try:
            url = 'https://{domain}/{version}/auth/login'.format(domain=DOMAIN, version=VERSION)
            country_code = 52
            country_code_iso = 'MX'
            device_id = Utils.get_device_id()
            body = {
                "password": password,
                "phoneNumber": username,
                "countryCode": country_code,
                "countryCodeIso": country_code_iso,
                "deviceId": device_id
            }
            raw_response = requests.post(url, data=json.dumps(body), headers=common_headers)

            status_code, reason = raw_response.status_code, raw_response.reason
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)

            return json_result
        except Exception as e:
            n = len(username)//2
            masked_username = ("*"*n)+username[n:]
            logger.critical(
                'func=Quantfury.login, user={}, '
                'status_code={}, reason={}, error_code={}, error_message={}, msg={}'.format(
                    masked_username, status_code, reason, error_code, error_message, e))
            raise e

    def check_credentials(self):
        """
        Check if token is valid
        Returns
        -------
        dict
            True if token works, False otherwise
        """
        try:
            orders = self.list_orders()
            return 'data' in orders
        except Exception as _:
            return False

    def close_order(self, order_id):
        """
        Close order
        Parameters
        ----------
        order_id

        Returns
        -------

        """
        status_code, reason, error_code, error_message = None, None, None, None
        try:
            url = 'https://{domain}/{version}/limitOrder/cancel'.format(domain=DOMAIN, version=VERSION)
            body = {
                "tradingPositionId": order_id,
                "priceId": Utils.get_price_id(symbol)
            }
            headers = self.get_headers()
            raw_response = requests.post(url, json=body, headers=headers)

            status_code, reason = raw_response.status_code, raw_response.reason
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)

            return json_result
        except Exception as e:
            logger.critical(
                'func=Quantfury.cancel, order_id={}, '
                'status_code={}, reason={}, error_code={}, error_message={}, msg={}'.format(
                    order_id, status_code, reason, error_code, error_message, e))
            raise e

    def cancel(self, order_id):
        """
        Cancel order
        Parameters
        ----------
        order_id : str
            Order ID to cancel
        Returns
        -------
        dict
            Dict with code of success or fail

        """
        status_code, reason, error_code, error_message = None, None, None, None
        try:
            url = 'https://{domain}/{version}/limitOrder/cancel'.format(domain=DOMAIN, version=VERSION)
            body = {
                "id": order_id
            }
            headers = self.get_headers()
            raw_response = requests.post(url, json=body, headers=headers)

            status_code, reason = raw_response.status_code, raw_response.reason
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)

            return json_result
        except Exception as e:
            logger.critical(
                'func=Quantfury.cancel, order_id={}, '
                'status_code={}, reason={}, error_code={}, error_message={}, msg={}'.format(
                    order_id, status_code, reason, error_code, error_message, e))
            raise e

    def list_orders(self):
        """
        List open positions, active limit orders in the account
        Returns
        -------
        dict
            Dict with fields: open_positions and active_limit_orders

        """
        status_code, reason, error_code, error_message = None, None, None, None
        try:
            url = 'https://{domain}/{version}/session'.format(domain=DOMAIN, version=VERSION)

            headers = self.get_headers()
            raw_response = requests.get(url, headers=headers)

            status_code, reason = raw_response.status_code, raw_response.reason
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)

            return json_result
        except Exception as e:
            logger.critical(
                'func=Quantfury.list_orders, '
                'status_code={}, reason={}, error_code={}, error_message={}, msg={}'.format(
                    status_code, reason, error_code, error_message, e))
            raise e

    def active_trade(self, symbol):
        """
        Check if there is an open trade
        Parameters
        ----------
        symbol : str
            Asset symbol

        Returns
        -------
        bool
            True if there is an open position for the symbol

        """
        orders = self.list_orders()
        active_limit_orders = orders['data']['activeLimitOrders']
        open_positions = orders['data']['openPositions']
        if len([i for i in active_limit_orders if i['shortName'] == symbol]) > 0:
            return active_limit_orders[0]['id']
        elif len([i for i in open_positions if i['shortName'] == symbol]) > 0:
            return open_positions[0]['id']
        return None

    def active_order_in_position(self, symbol, order_type):
        """
        Check if there is an active order in an open position
        Parameters
        ----------
        symbol : str
            Asset symbol
        order_type : str
            Order type

        Returns
        -------
        bool
            order_api_id

        """
        try:
            if order_type in ORDER_TYPES.keys():
                order_type = ORDER_TYPES[order_type]
            elif order_type not in ORDER_TYPES.values():
                raise ValueError('Invalid order type')

            orders = self.list_orders()
            open_positions = orders['data']['openPositions']
            for open_position in open_positions:
                if open_position['shortName'] == symbol and open_position['stopOrders']:
                    if len(open_position['stopOrders']) > 1:
                        logger.warning('func=Quantfury.active_order_in_position, symbol={}, order_type={}, '
                                       'msg=Many declared stop orders'.format(symbol, order_type))
                    for order in open_position['stopOrders']:
                        if order['orderType'] == order_type:
                            return order['id']
                if open_position['shortName'] == symbol and open_position['targetOrders']:
                    if len(open_position['targetOrders']) > 1:
                        logger.warning('func=Quantfury.active_order_in_position, symbol={}, order_type={}, '
                                       'msg=Many declared target orders'.format(symbol, order_type))
                    for order in open_position['targetOrders']:
                        if order['orderType'] == order_type:
                            return order['id']
            return None
        except Exception as e:
            logger.critical('func=Quantfury.active_order_in_position, symbol={}, order_type={}, msg={}'.format(
                symbol, order_type, e))

    def upsert_position(self, api_position_id, symbol, order_type, target_price, limit_amount_system):
        api_order_id = self.active_order_in_position(symbol, order_type)
        if api_order_id:
            order_json_result = self.update_position(
                api_order_id, symbol, target_price,
                limit_amount_system, order_type)
        else:
            order_json_result = self.create_position(
                api_position_id, symbol, target_price,
                limit_amount_system, order_type)
        return order_json_result

    def list_closed_positions(self):
        """
        List close position in the account
        Returns
        -------
        list
            List with one dict peer close position
        """
        status_code, reason, error_code, error_message = None, None, None, None
        try:
            url = 'https://{domain}/{version}/tradingHistory/closedAndReducedPositions'.format(
                domain=DOMAIN, version=VERSION)

            headers = self.get_headers()
            raw_response = requests.post(url, json={}, headers=headers)

            status_code, reason = raw_response.status_code, raw_response.reason
            json_result = raw_response.json()
            error_code, error_message = json_result.get('code', None), json_result.get('error', None)

            return json_result
        except Exception as e:
            logger.critical(
                'func=Quantfury.list_orders, '
                'status_code={}, reason={}, error_code={}, error_message={}, msg={}'.format(
                    status_code, reason, error_code, error_message, e))
            raise e

    def get_account_balance(self):
        session_data = self.list_orders()
        account_info = session_data['data']
        return account_info['balanceAccount'] + account_info['pnlAccountClosePositions'] + \
            account_info['pnlAccountDividends']

    def get_headers(self):
        return {**common_headers, **{
            "Authorization": "Bearer {}".format(self.token)}}

    @classmethod
    def filter_order(cls, list_orders_response, order_id):
        orders = [i for i in list_orders_response['data']['activeLimitOrders'] if order_id == i['id']]
        if orders:
            return orders[0]

    @classmethod
    def calculate_open_position_profits(cls, orders):
        profits = {}
        if not ('data' in orders and 'openPositions' in orders['data']):
            return {}
        for position in orders["data"]["openPositions"]:
            current_price = Utils.get_latest_price(symbol)
            min_price_tmp = min(position["openPrice"], current_price)
            profits[position['shortName']] = min_price_tmp / max(position["openPrice"], current_price)
        return profits

    def get_open_position_profits(self):
        orders = self.list_orders()
        return self.calculate_open_position_profits(orders)


def test_oco_order(username, password, symbol, token):
    quote_order_quantity = 10
    position_type = 'long'
    buy_price = Utils.get_latest_price(symbol)
    buy_price = buy_price - buy_price % 100

    stop_price, target_price = buy_price - 1000, buy_price + 1000
    if token:
        quantfury = Quantfury(token)
    else:
        login_result = Quantfury.login(username, password)
        quantfury = Quantfury(login_result['data']['token'])

    oco_response = quantfury.create_OCO_long_order(
        symbol, quote_order_quantity, buy_price, stop_price, target_price, position_type)
    order_id = oco_response['data']['id']
    logger.info(
        'func=test_oco_order, stage=open_order, order_id={}, buy_price={}, stop_price={}, target_price={}'.format(
            order_id, buy_price, stop_price, target_price))
    print(order_id)
    list_orders_response = quantfury.list_orders()
    if len(list_orders_response['data']['activeLimitOrders']) == 0:
        raise ValueError('No active orders')

    order_id_listed = list_orders_response['data']['activeLimitOrders'][0]['id']
    assert order_id == order_id_listed

    price_value = buy_price - 200
    order_type = 'LIMIT_ORDER'
    update_order_response = quantfury.update_order(
        order_id, symbol, price_value, stop_price, target_price, quote_order_quantity, order_type)

    assert 'data' in update_order_response

    response_buy_price = update_order_response['data']['price']
    response_stop_price = update_order_response['data']['stopOrder']
    response_target_price = update_order_response['data']['targetOrder']
    update_order_response_id = update_order_response['data']['id']
    logger.info(
        'func=test_oco_order, msg=update_order, order_id={}, buy_price={}, stop_price={}, target_price={}'.format(
            update_order_response_id, response_buy_price, response_stop_price, response_target_price))
    assert price_value == response_buy_price
    assert stop_price == response_stop_price
    assert target_price == response_target_price
    assert order_id == update_order_response_id

    quantfury.cancel(order_id_listed)

    list_orders_response = quantfury.list_orders()
    order = quantfury.filter_order(list_orders_response, order_id)
    assert order is None
    logger.info('func=test_oco_order, msg=cancel_order, order_id={}'.format(update_order_response_id))


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    load_dotenv()

    username = os.getenv("QUANTFURY_USERNAME")
    password = os.getenv("QUANTFURY_PASSWORD")
    token = os.getenv("QUANTFURY_TOKEN")
    symbol = 'BTC/USDT'

    test_oco_order(username, password, symbol, token)


