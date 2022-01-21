from datetime import datetime
import os
import asyncio
from metaapi_cloud_sdk import MetaApi

from metaapi_cloud_sdk.clients.metaApi.tradeException import TradeException
# Note: for information on how to use this example code please read https://metaapi.cloud/docs/client/usingCodeExamples/

token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiIzYTI0YzMwYzFkNDRmZGFmZGI3NmVmYTUxZmQ2MDJmMCIsInBlcm1pc3Npb25zIjpbXSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaWF0IjoxNjM5NDkwMzEzLCJyZWFsVXNlcklkIjoiM2EyNGMzMGMxZDQ0ZmRhZmRiNzZlZmE1MWZkNjAyZjAifQ.DhA6Q-AlWNssi8ScOaWy2Bxo4Hebgw94BDE6PiT9J-TvsuF7OqvdYBQ1IWYEMtsYsg3Ij8p8Wpvn8ZdZeHRkR3vLcQnMH-GZj3DyYkeqovQKk6U3uOobV-GS3meJPZYfw2zItuTDBWxuHDZsVW1ZvF4sItBDmsWIe2svF0NmKE1nu-ephcYVzYo9grr93de_h-QwlP-yeZFeGEqrz3-q5gYWcARJsIR1BX63zePuDHkUK9k5W9Rm28WdB87MHEyMSWhcAZDf8si5MwsPYC3wpzNtzGqORF3UY-w5EmolCtSPMBqM7AI0LKc1n8GPS3ZhnvHkfGhWEdb5gKlCWwshk30tICN24C1bZG06zfs450oLm8ih9ls5oyshcg_xwawNvsA305D7Siz0Pzqr1xnUA8zMz8cVUFZtjdBWCfot05_ziVO0x_mApVyAVC2OA-Sh61RtkwNNpg4bTCzK30OpdiS9GO0HLgnepnuwWOO0T9DTzTAJUxyJcXOzcWcXGdMTWaGAp5ranytU97k8GxDHa5jOS_WvphL24C8QA6of0pYZwHM3Ul5Aw351H1SbJLIqs2AChDoUnpJb9OZb-27ESLZgM1mhU6rwzt8lRRbxUHaXSv5QpM29nPm3k5KrFSv-UTXiX6oU9c1nNh3qLb6FKV_B1CQarcvyx66iUg-1DcU'
# login = '2132970485'
# password = 'Marines791!'
# server_name = 'CBTLimited-Trading'
login = '3648098'
password = 'Marines791!'
server_name = 'OANDA-Demo-1'


async def meta_api_synchronization():
    api = MetaApi(token)
    try:
        # Add test MetaTrader account
        accounts = await api.metatrader_account_api.get_accounts()
        account = None
        for item in accounts:
            if item.login == login and item.type.startswith('cloud'):
                account = item
                break
        if not account:
            print('Adding MT4 account to MetaApi')
            account = await api.metatrader_account_api.create_account({
                'name': 'Test account',
                'type': 'cloud',
                'login': login,
                'password': password,
                'server': server_name,
                'platform': 'mt4',
                'application': 'MetaApi',
                'magic': 1000
            })
        else:
            print('MT4 account already added to MetaApi')

        #  wait until account is deployed and connected to broker
        print('Deploying account')
        await account.deploy()
        print('Waiting for API server to connect to broker (may take couple of minutes)')
        await account.wait_connected()

        new_data = await account.get_historical_candles('EURUSD','1d',datetime.now(),limit=1000)
        print(new_data)

        # connect to MetaApi API
        connection = account.get_streaming_connection()
        await connection.connect()

        # wait until terminal state synchronized to the local state
        print('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
        await connection.wait_synchronized()

        # access local copy of terminal state
        print('Testing terminal state access')
        terminal_state = connection.terminal_state
        print('connected:', terminal_state.connected)
        print('connected to broker:', terminal_state.connected_to_broker)
        print('account information:', terminal_state.account_information)
        print('positions:', terminal_state.positions)
        print('orders:', terminal_state.orders)
        print('specifications:', terminal_state.specifications)
        print('EURUSD specification:', terminal_state.specification('EURUSD'))

        # access history storage
        history_storage = connection.history_storage
        print('deals:', history_storage.deals[-5:])
        print('history orders:', history_storage.history_orders[-5:])

        await connection.subscribe_to_market_data('EURUSD')
        print('EURUSD price:', terminal_state.price('EURUSD'))

        # trade
        print('Submitting pending order')
        try:
            result = await connection.create_limit_buy_order('GBPUSD', 0.07, 1.0, 0.9, 2.0,
                                                             {'comment': 'comm', 'clientId': 'TE_GBPUSD_7hyINWqAlE'})
            print('Trade successful, result code is ' + result['stringCode'])
        except Exception as err:
            print('Trade failed with error:')
            print(api.format_error(err))

        # finally, undeploy account after the test
        print('Undeploying MT4 account so that it does not consume any unwanted resources')
        await account.undeploy()

    except Exception as err:
        # process errors
        if hasattr(err, 'details'):
            # returned if the server file for the specified server name has not been found
            # recommended to check the server name or create the account using a provisioning profile
            if err.details == 'E_SRV_NOT_FOUND':
                print(err)
            # returned if the server has failed to connect to the broker using your credentials
            # recommended to check your login and password
            elif err.details == 'E_AUTH':
                print(err)
            # returned if the server has failed to detect the broker settings
            # recommended to try again later or create the account using a provisioning profile
            elif err.details == 'E_SERVER_TIMEZONE':
                print(err)
        print(api.format_error(err))
    exit()

asyncio.run(meta_api_synchronization())