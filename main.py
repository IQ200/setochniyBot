import ccxt
import time
import logging

import config

from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from binance.lib.utils import config_logging


# config_logging(logging, logging.DEBUG)


symbol = 'EPTUSDT'

setOrders = {a: 0 for a in range(21)}


client = UMFutures(key=config.apiKey, secret=config.secretKey)

# link = 'wss://fstream.binance.com/ws/'+symbol.lower()+'@trade'


def message_handler(_, message):
    print(message)



ccxtBinance = ccxt.binance({
            'apiKey': config.apiKey,
            'secret': config.secretKey,
            'enableRateLimit': True,

            'options': {
                'defaultType': 'future',
                'urls': {
                    'api': 'fapiPublic',
                    'test': 'https://testnet.binancefuture.com',
                },
            },
        })


while True:
    # Получить цену
    trades = ccxtBinance.fetch_trades(symbol, limit=1)
    lastPrice = trades[0]['price']
    print(lastPrice)
    # Составить сетку ордеров
    setOrders[11] = int(lastPrice)
    lenDrobChast = len(str(lastPrice).split(".")[1])
    zeroFiveProcent = round(lastPrice * 0.005, lenDrobChast)

    setOrders = {a: round(a * zeroFiveProcent + (lastPrice-zeroFiveProcent*10), lenDrobChast) for a in range(21)}
    # try:

    time.sleep(100)



    trades = ccxtBinance.fetch_trades(symbol, limit=1)
    print(trades)




logging.debug("closing ws connection")
# webSocketClient.stop()




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

while True:
    print('.')


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
