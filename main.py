# from datetime import datetime
# from binance.error import ClientError
# from binance.spot import Spot
# import ccxt
# import logging
# import os
# import sys
# from binance import client
# from binance import depthcache
# from binance import enums
# from binance import exceptions
# from binance import websockets

# from binance import *

import time
import datetime
import ssl
import websocket
import pandas as pd
from pandas import DataFrame
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.exceptions import BinanceAPIException
import re
import config

# from binance.um_futures import UMFutures
# from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
# from binance.lib.utils import config_logging

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# config_logging(logging, logging.DEBUG)


def on_msg(_, msg):
    print(msg)


def on_err(_, err):
    print(err)


def main():
    global initProc, lastPrice, sizeOrder, lenDrobChast, gridPercent, zeroFiveProcent, setGridOrders, sizeOrderUSD, quantityOrders, lenSetGridOrders, orderClientId

    initProc = True
    sizeOrderUSD = 5.4
    gridPercent = 0.005  # НЕ ПРОЦЕНТЫ, А МНОЖИТЕЛЬ!!!!!!
    quantityOrders = 2

    quantityOrders = int(quantityOrders / 2) * 2  # Четное!!!

    setGridOrders = {a: 0 for a in range(quantityOrders + 1)}

    symbol = config.symbol

    lastPrice = sizeOrder = lenDrobChast = zeroFiveProcent = sizeOrder = orderClientId = 0

    # create futures order
    def create_futures_sell_limit_order(symbol, sizeOrder, price, newClientOrderId):
        order = client.futures_create_order(
            symbol=symbol,
            side="SELL",
            type="LIMIT",
            quantity=sizeOrder,
            price=price,
            # positionSide="SHORT",  # BOTH for One-way Mode ; LONG or SHORT for Hedge Mode
            newClientOrderId=newClientOrderId,
            recvWindow=5000,
            timeInForce="GTC",
            timestamp=time.time_ns()
        )
        return (order)

    def create_futures_buy_limit_order(symbol, sizeOrder, price, newClientOrderId):
        order = client.futures_create_order(
            symbol=symbol,
            side="BUY",
            type="LIMIT",
            quantity=sizeOrder,
            price=price,
            # positionSide="SHORT",  # BOTH for One-way Mode ; LONG or SHORT for Hedge Mode
            newClientOrderId=newClientOrderId,
            recvWindow=5000,
            timeInForce="GTC",
            timestamp=time.time_ns()
        )
        return (order)

    def _user_data(msg):

        global orderClientId

        if 'e' in msg and msg['e'] != 'ACCOUNT_UPDATE' and msg['e'] != 'TRADE_LITE' :
            print(f"message type: {msg['e']}", datetime.datetime.today())
            print(msg)
            print('-------------------')

            if 'e' in msg and msg['e'] == 'ORDER_TRADE_UPDATE':

                if msg['o'].get('X') == 'FILLED':
                    try:
                        orderClientId = msg['o']['c']
                        print('Исполнился ордер: ', orderClientId)
                        print('Отменяем ордера:  ', datetime.datetime.today())
                        print('-------------------')
                        order = client.futures_cancel_all_open_orders(symbol=symbol)
                    except BinanceAPIException as e:
                        date = datetime.datetime.today()
                        print('now ', date)
                        print(e.status_code)
                        print(e.message)
                        print('-------------------')

                elif msg['o'].get('X') == 'CANCELED':
                    try:
                        print('Отменился ордер: ', orderClientId)
                        # date = datetime.datetime.today()
                        print('now ', datetime.datetime.today())
                        print('-------------------')
                        lastPrice = orderClientId.replace("buy_", "")
                        lastPrice = lastPrice.replace("sell_", "")
                        lastPrice = float(lastPrice)
                        zeroFiveProcent = lastPrice * gridPercent
                        setGridOrders = {
                            a: round(a * zeroFiveProcent + (lastPrice - zeroFiveProcent * quantityOrders / 2), lenDrobChast)
                            for
                            a in range(quantityOrders + 1)}

                        priceBuyLimit = setGridOrders[int((len(setGridOrders) - 1) / 2) - 1]
                        priceSellLimit = setGridOrders[int((len(setGridOrders) - 1) / 2) + 1]
                        order = create_futures_buy_limit_order(symbol, sizeOrder,
                                                                   priceBuyLimit,
                                                                   'buy_' + str(priceBuyLimit))
                        order = create_futures_sell_limit_order(symbol, sizeOrder,
                                                                priceSellLimit,
                                                                'sell_' + str(priceSellLimit))
                    except BinanceAPIException as e:
                        date = datetime.datetime.today()
                        print('now ', date)
                        print(e.status_code)
                        print(e.message)
                        print('-------------------')

    # priceFilOdrer =

    # Филл?   msg['o']['x'] == 'FILLED'
    # Если да, то узнать цену msg['o']['p']
    # Сравнить с центральной
    # Выставить новый по центральной

    client = Client(config.apiKey, config.secretKey
                    # base_url="https://testnet.binance.vision"
                    # proxies={ 'https': creds.proxy }
                    )

    # Подписываемся на WebSocket ордеров для отслеживания изменения (филл)
    twm = ThreadedWebsocketManager(config.apiKey, config.secretKey)
    # start is required to initialise its internal loop
    twm.start()

    date = datetime.datetime.today()
    print('Start websocket now: ', date)

    twm.start_futures_user_socket(callback=_user_data)
    # twm.join()

    df = DataFrame(
        client.futures_recent_trades(**{'symbol': symbol, 'limit': 1})
    )

    while True:
        if initProc:
            initProc = False

            lastPrice = float(df.iloc[0]['price'])
            sizeOrder = int(sizeOrderUSD / float(df.iloc[0]['price']))

            # Составить сетку ордеров
            lenDrobChast = len(str(lastPrice).split(".")[1])
            zeroFiveProcent = lastPrice * gridPercent
            setGridOrders = {
                a: round(a * zeroFiveProcent + (lastPrice - zeroFiveProcent * quantityOrders / 2), lenDrobChast) for a
                in range(quantityOrders + 1)}

            # Выставляем лимитные ордера на покупку
            if 0 == 0:
                lenSetGridOrders = len(setGridOrders)
                for v in range(int((lenSetGridOrders - 1) / 2), 0, -1):
                    order = create_futures_buy_limit_order(symbol, sizeOrder, setGridOrders[v - 1],
                                                           'buy_' + str(setGridOrders[v - 1]))
                    # print(setGridOrders[v-1])
                    print(order)

            # Выставляем лимитные ордера на продажу
            if 0 == 0:
                lenSetGridOrders = len(setGridOrders)
                for v in range(int((lenSetGridOrders + 1) / 2), lenSetGridOrders):
                    order = create_futures_sell_limit_order(symbol, sizeOrder, setGridOrders[v],
                                                            'sell_' + str(setGridOrders[v]))
                    print(order)
        # else:

        # print("* TRADE *", df.tail(10), sep="\n")


if __name__ == "__main__":
    main()


def mainkms():
    # Получить цену
    #     x = {'symbol': symbol, 'limit': 1}
    df = DataFrame(
        client.futures_recent_trades(**{'symbol': symbol, 'limit': 1})
    )
    lastPrice = float(df.iloc[0]['price'])
    sizeOrder = int(sizeOrderUSD / float(df.iloc[0]['price']))

    # Составить сетку ордеров
    lenDrobChast = len(str(lastPrice).split(".")[1])
    zeroFiveProcent = lastPrice * gridPercent
    setGridOrders = {a: round(a * zeroFiveProcent + (lastPrice - zeroFiveProcent * quantityOrders / 2), lenDrobChast)
                     for a in range(quantityOrders + 1)}

    # sizeOrder = 280
    # symbol = "BROCCOLIF3BUSDT"
    # order = client.futures_create_order(
    #     symbol=symbol,
    #     side="BUY",
    #     type="LIMIT",
    #     quantity=sizeOrder,
    #     # price=setGridOrders[v],
    #     price=0.019500,
    #     # positionSide="LONG",  # BOTH for One-way Mode ; LONG or SHORT for Hedge Mode
    #     newClientOrderId=str('0.019'),
    #     recvWindow=5000,
    #     timeInForce="GTC",
    #     timestamp=time.time_ns()
    # )
    # # print(DataFrame(order))
    # print(order)

    # Выставляем лимитные ордера на покупку
    if 0 != 0:
        lenSetGridOrders = len(setGridOrders)
        for v in range(int((lenSetGridOrders - 1) / 2), 0, -1):
            order = client.futures_create_order(
                symbol=symbol,
                side="BUY",
                type="LIMIT",
                quantity=sizeOrder,
                price=setGridOrders[v - 1],
                # positionSide="SHORT",  # BOTH for One-way Mode ; LONG or SHORT for Hedge Mode
                newClientOrderId=str(setGridOrders[v]),
                recvWindow=5000,
                timeInForce="GTC",
                timestamp=time.time_ns()
            )
            # print(setGridOrders[v-1])
            print(order)

    print('--------------------')
    # Выставляем лимитные ордера на продажу
    if 0 != 0:
        lenSetGridOrders = len(setGridOrders)
        for v in range(int((lenSetGridOrders + 1) / 2), lenSetGridOrders):
            order = client.futures_create_order(
                symbol=symbol,
                side="SELL",
                type="LIMIT",
                quantity=sizeOrder,
                price=setGridOrders[v],
                # positionSide="LONG",  # BOTH for One-way Mode ; LONG or SHORT for Hedge Mode
                newClientOrderId=str(setGridOrders[v]),
                recvWindow=5000,
                timeInForce="GTC",
                timestamp=time.time_ns()
            )

            # print(setGridOrders[v])
            print(order)

    # Подписываемся на WebSocket ордеров для отслеживания изменения (филл)

    print("* TRADE *", df.tail(10), sep="\n")

# mainKMS()

# -----------------------------------------------------------------
#     try:
#
#         # print(f"* exchange_info {symbol}* ", cl.exchange_info(symbol), sep="\n")
#
#         # print(f"* best_price {symbol}* ", cl.book_ticker(symbol=symbol), sep="\n")
#         # buy_price = cl.book_ticker(symbol=symbol).get('askPrice')
#         # sell_price = cl.book_ticker(symbol=symbol).get('bidPrice')
#
#
#         print(cl.new_order(
#             symbol=symbol,
#             # newClientOrderId="sell_btcusdt_15",
#             side='SELL',
#             type='LIMIT',
#             quantity=0.7,
#
#             price=30000,
#             timeInForce='GTC'
#         ))
#
#         print(f"* account assets * ", cl.account(), sep="\n")
#
#         # order_id = 8214572
#         # print(f"* CANCEL order {order_id}", cl.cancel_order(symbol=symbol, orderId=order_id), sep="\n")
#
#         df = DataFrame(cl.get_orders(symbol, recvWindow=59000), columns=['price', 'origQty', 'executedQty', 'cummulativeQuoteQty', 'origQuoteOrderQty', 'status', 'type', 'side', 'orderId'])
#         print("* ORDERS *", df.tail(10), sep="\n")
#     except ClientError as e:
#         print(e.error_code, e.error_message)
#
# --------------------------------------
# client = UMFutures(key=config.apiKey, secret=config.secretKey)
#
# # link = 'wss://fstream.binance.com/ws/'+symbol.lower()+'@trade'
#
#
# def message_handler(_, message):
#     print(message)
#
#
#
# ccxtBinance = ccxt.binance({
#             'apiKey': config.apiKey,
#             'secret': config.secretKey,
#             'enableRateLimit': True,
#
#             'options': {
#                 'defaultType': 'future',
#                 'urls': {
#                     'api': 'fapiPublic',
#                     'test': 'https://testnet.binancefuture.com',
#                 },
#             },
#         })
#
#
# while True:
#     # Получить цену
#     trades = ccxtBinance.fetch_trades(symbol, limit=1)
#     lastPrice = trades[0]['price']
#     print(lastPrice)
#     # Составить сетку ордеров
#     setOrders[11] = int(lastPrice)
#     lenDrobChast = len(str(lastPrice).split(".")[1])
#     # zeroFiveProcent = round(lastPrice * 0.005, lenDrobChast)
#     zeroFiveProcent = lastPrice * 0.005
#
#     setOrders = {a: round(a * zeroFiveProcent + (lastPrice-zeroFiveProcent*10), lenDrobChast) for a in range(21)}
#     # setOrders01 = {a: a * zeroFiveProcent + (lastPrice - zeroFiveProcent * 10) for a in range(21)}
#     # try:
#
#     time.sleep(100)
#
#
#
#     trades = ccxtBinance.fetch_trades(symbol, limit=1)
#     print(trades)
#
#
#
#
# logging.debug("closing ws connection")
# # webSocketClient.stop()
#
# -----------------------------------------------------------------


# Проверять количество открытых ордеров
# Если открытые уменьшились, то выставлять ближний в нужную сторону


# webSocketClient = UMFuturesWebsocketClient(on_message=message_handler)
#
# webSocketClient.agg_trade(
#     symbol="zerebrousdt",
#     id=1,
#     callback=message_handler,
# )

# time.sleep(100)


# Subscribe to a single symbol stream
# print(webSocketClient.agg_trade(symbol="btcusdt")) #symbol.lower()))

# webSocketClient.agg_trade(symbol="btcusdt") #symbol.lower()))

# print("closing ws connection")
# webSocketClient.stop()

# while True:
#     print('.')


# print(client.exchange_info())
# print(client.balance())
# print(client.new_order(symbol=symbol, side='BUY', type='LIMIT', price=0.04, quantity=1000, timeInForce="GTC"))


#
#
# import requests
# import base64
# import json
# from cryptography.hazmat.primitives.serialization import load_pem_private_key
# from websocket import create_connection
# from binance.client import Client
#
# import websocket
# import json
#
# import websocket, json, threading
#
#
# class binance():
#     def __init__(self):
#         self.ticker_socket = []
#
#     # Выключение сокета
#     def on_error(self, _wsa, wsData):
#         _wsa.close()
#
#     # Данные от сокета
#     def on_message(self, _wsa, wsData):
#         mData = json.loads(wsData)
#         self.ticker_socket = mData
#
#     # Запуск сокета
#     def run_web_sock(self):
#         while True:
#             try:
#                 # wss ='wss://fstream.binance.com/ws/btcusdt@trade'
#                 # wss ='wss://testnet.binance.vision/ws/btcusdt@trade'
#                 # wss ='wss://ws-dapi.binance.vision/ws-dapi/v1/btcusdt@trade'
#                 # wss ='wss://fstream.testnet.binance.vision/ws/btcusdt@trade'
#                 # wss ='wss://stream.binancefuture.com/ws/btcusdt@trade' # Тестовый сервер фьючерсов бинанса
#                 wss = 'wss://stream.binance.com:9443/ws/btcusdt@trade' # User Data Streams for Binance
#                 wsa = websocket.WebSocketApp(wss,
#                                              on_message=self.on_message,
#                                              on_error=self.on_error)
#
#                 print(u'Установлено соединение Web Socket')
#
#                 wsa.run_forever()
#                 raise Exception(u'Разрыв соединения Web Socket')
#             except Exception as e:
#                 print(str(e))
#                 time.sleep(1)
#
#     # Старт
#     def start(self):
#         ws = threading.Thread(target=self.run_web_sock)
#         ws.setDaemon(True)
#         ws.start()
#
#
# # Проверка
# class main():
#     def __init__(self):
#         # Инициализация класса / запуск потока
#         wb = binance()
#         wb.start()
#
#         exchangeBinance = ccxt.binance({
#             'apiKey': config.API_KEY,
#             'secret': config.API_SECRET,
#             'enableRateLimit': True,
#
#             'options': {
#                 'defaultType': 'future',
#                 'urls': {
#                     'api': 'https://testnet.binancefuture.com',
#                     'test': 'https://testnet.binancefuture.com',
#                 },
#             },
#         })
#
#         # Переключаем ccxt на песочницу Бинанса
#         exchangeBinance.set_sandbox_mode(True)
#
#         symbol = 'BTCUSDT'  # выбираем торговую пару
#         # buyPrice = 0  # устанавливаем начальную цену покупки
#         # sellPrice = 0  # устанавливаем начальную цену покупки
#         amount = 0.01  # устанавливаем объем монет для покупки
#         # profit_percent = 1  # задаем процент прибыли
#
#         # myTtrades = dict(symbol=symbol, since=None, limit=None, params={})
#
#         symbols = ['BTCUSDT', 'ETHUSDT', 'DOGEUSDT']
#         while True:
#             trades = exchangeBinance.watch_trades_for_symbols(symbols)
#             print(trades)
#
#         # print(exchangeBinance.watch_trades(**myTtrades))
#
#         currentPrice = float(wb.ticker_socket['p'])
#         oldCurrentPrice = currentPrice
#         openOrders = exchangeBinance.fetch_open_orders(symbol)
#         sellPrice = round(currentPrice * 1.0001)
#         buyPrice = round(currentPrice / 1.0001)
#         orderBuy = dict(symbol=symbol, type='limit', side='buy', price=buyPrice, amount=amount)
#         orderSell = dict(symbol=symbol, type='limit', side='sell', price=sellPrice, amount=amount)
#
#         if len(openOrders) == 0:
#             if orderBuy:
#                 returnOrderBuy = exchangeBinance.create_order(**orderBuy)
#                 # clientOrderBuyId = returnOrderBuy['clientOrderId']
#                 lastPriceBuy = returnOrderBuy['price']
#
#             if orderSell:
#                 returnOrderSell = exchangeBinance.create_order(**orderSell)
#                 # clientOrderSellId = returnOrderSell['clientOrderId']
#                 lastPriceSell = returnOrderSell['price']
#
#         # Вывод данных
#         while True:
#             if float(wb.ticker_socket['p']) != oldCurrentPrice:
#                 currentPrice = float(wb.ticker_socket['p'])
#                 oldCurrentPrice = currentPrice
#                 openOrders = exchangeBinance.fetch_open_orders(symbol)
#
#                 if len(openOrders) != 2:
#                     currentPrice = float(wb.ticker_socket['p'])
#                     orders = exchangeBinance.cancel_all_orders(symbol)
#
#                     if orderBuy:
#                         buyPrice = round(currentPrice / 1.0001)
#                         orderBuy = dict(symbol=symbol, type='limit', side='buy', price=buyPrice, amount=amount)
#                         returnOrderBuy = exchangeBinance.create_order(**orderBuy)
#                         # clientOrderBuyId = returnOrderBuy['clientOrderId']
#                         # lastPriceBuy = returnOrderBuy['price']
#
#                     if orderSell:
#                         sellPrice = round(currentPrice * 1.0001)
#                         orderSell = dict(symbol=symbol, type='limit', side='sell', price=sellPrice, amount=amount)
#                         returnOrderSell = exchangeBinance.create_order(**orderSell)
#                         # clientOrderSellId = returnOrderSell['clientOrderId']
#                         # lastPriceSell = returnOrderSell['price']
#
#                 print(currentPrice)
#  # ---------------------
#
#
#                     # if openOrders[0]['side'] == 'buy':
#                     # sellPrice = round(currentPrice * 1.0001)
#                     # buyPrice = round(currentPrice / 1.0001)
#                     #
#                     # if orderSell:
#                     #     returnOrderSell = exchangeBinance.create_order(**orderSell)
#                     #     clientOrderSellId = returnOrderSell['clientOrderId']
#                     #     lastPriceSell = returnOrderSell['price']
#                     #
#                     # if orderBuy:
#                     #     returnOrderBuy = exchangeBinance.create_order(**orderBuy)
#                     #     clientOrderBuyId = returnOrderBuy['clientOrderId']
#                     #     lastPriceBuy = returnOrderSell['price']
#
#                 # if openOrders[0]['side'] == 'sell':
#                 #     sellPrice = round(lastPriceSell * 1.0001)
#                 #     buyPrice = round(lastPriceSell / 1.0001)
#                 #
#                 #     if orderSell:
#                 #         returnOrderSell = exchangeBinance.create_order(**orderSell)
#                 #         clientOrderSellId = returnOrderSell['clientOrderId']
#                 #         lastPriceSell = returnOrderSell['price']
#                 #
#                 #     if orderBuy:
#                 #         returnOrderBuy = exchangeBinance.create_order(**orderBuy)
#                 #         clientOrderBuyId = returnOrderBuy['clientOrderId']
#                 #         lastPriceBuy = returnOrderSell['price']
#
#
#
#
#
#
#
#                 #
#                 # if orderSell:
#                 #     returnOrderSell = exchangeBinance.create_order(**orderSell)
#                 #     clientOrderSellId = returnOrderSell['clientOrderId']
#
#
#
#
#
#             # balance = exchangeBinance.fetch_balance()
#             # openOrders = exchangeBinance.fetch_open_orders(symbol)
#             # closedOrders = exchangeBinance.fetch_closed_orders(symbol)
#             # lastPrices = exchange.fetch_last_prices(symbol)
#             # tickerData = exchangeBinance.fetch_ticker(symbol)
#             # currentPrice = tickerData['last']
#             # print(currentPrice, buyPrice, sellPrice)
#             # print('-----------------')
#
#
#
#
#
#
#
#
#
# if __name__ == "__main__":
#     main()
#
#
#
#
#
#
#
# # -----------------------------------------------------------
#
#
#
# # print(balance)
# # print('-----------------')
# # print(open_orders)
# # print('-----------------')
# # print(closed_orders)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# # wss://testnet.binancefuture.com/ws-fapi/v1
#
#
#
#
#
# # open_orders = exchange.fetch_open_orders()
# # closed_orders = exchange.fetch_closed_orders()
#
#
#
#
#
#
# # api_key = config.API_KEY
# # api_secret = config.API_SECRET
#
#
# # import websocket
# # import json
# #
# # def on_message(ws, message):
# #     data = json.loads(message)
# #     # Поле 'c' содержит текущую цену
# #     current_price = data['c']
# #     print(f"Текущая цена VINEUSDT: {current_price}")
# #
# # def on_error(ws, error):
# #     print(f"Ошибка: {error}")
# #
# # def on_close(ws):
# #     print("Закрытие соединения")
# #
# # def on_open(ws):
# #     print("Соединение установлено. Ожидание обновлений цен...")
# #
# # if __name__ == "__main__":
# #     # URL WebSocket для отслеживания тикеров по паре VINEUSDT
# #     # ws_url = "wss://fstream.binance.com:9443/ws/btcusdt@ticker"
# #
# #     ws_url = "wss://fstream.binance.com/stream?streams=bnbusdt@aggTrade/btcusdt@markPrice"
# #
# #     ws = websocket.WebSocketApp(ws_url,
# #                                 on_open=on_open,
# #                                 on_message=on_message,
# #                                 on_error=on_error,
# #                                 on_close=on_close)
# #
# #     # Запускаем WebSocket в основном потоке
# #     ws.run_forever()
#
#
# #
# # import asyncio
# # import websockets
# #
# # async def listen_btcusdt_price():
# #     url = "wss://fstream.binance.com/stream?streams=bnbusdt@aggTrade/btcusdt@markPrice"
# #
# #     async with websockets.connect(url) as websocket:
# #         print("Подключено к Binance WebSocket для BTCUSDT")
# #         while True:
# #             try:
# #                 message = await websocket.recv()
# #                 data = json.loads(message)
# #                 # В объекте data есть поле 'c' — текущая цена
# #                 current_price = data['c']
# #                 print(f"Новая цена BTCUSDT: {current_price}")
# #             except Exception as e:
# #                 print(f"Ошибка: {e}")
# #                 break
# #
# # if __name__ == "__main__":
# #     asyncio.get_event_loop().run_until_complete(listen_btcusdt_price())
#
#
#
#
#
#
#
#
#
#
#
# # # URL для получения данных о последних сделках (Trades)
# # symbol = "BTCUSDT"
# # url = f"https://testnet.binancefuture.com/fapi/v1/trades?symbol={symbol}&limit=1"
# #
# # try:
# #     response = requests.get(url)
# #     response.raise_for_status()
# #     trades = response.json()
# #
# #     if trades:
# #         last_trade = trades[0]
# #         price = last_trade['price']
# #         print(f"Последняя цена сделки по {symbol}: {price}")
# #     else:
# #         print("Нет данных о сделках.")
# # except requests.exceptions.RequestException as e:
# #     print(f"Ошибка запроса: {e}")
#
#
# #
# # api_key = config.API_KEY
# # api_secret = config.API_SECRET
# # client = Client(api_key, api_secret, testnet=True)
# # # client.API_URL = "https://testnet.binance.vision/api"
# #
# # try:
# #     balance = client.futures_account_balance()
# #     print(balance)
# # except Exception as e:
# #    print(e)
# #
#
#
#
#
#
#
# # try:
# #    account_info = client.get_account()
# #    print(account_info)
# # except Exception as e:
# #    print(e)
#
#
# # from binance.client import Client
# # import config
# #
# # client = Client(config.API_KEY, config.API_SECRET)
# #
# # # Получить баланс
# # balance = client.futures_account_balance()
# # print(balance)
#
