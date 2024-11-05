#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 22:45:24 2024

@author: simone
"""
from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.common import MarketDataTypeEnum
import threading
import time

#if tickType == 2 and reqId == 1:
class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
	def tickPrice(self, reqId, tickType, price, attrib):
		print('The current ask price is: ', price,n)

def run_loop():
	app.run()
    
    
n=0
app = IBapi()
app.connect('127.0.0.1', 4002, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server
app.reqMarketDataType(MarketDataTypeEnum.DELAYED)
#Create contract object
apple_contract = Contract()
apple_contract.symbol = 'AAPL'
apple_contract.secType = 'STK'
apple_contract.exchange = 'SMART'
apple_contract.currency = 'USD'

#Request Market Data
app.reqMktData(1, apple_contract, '', False, False, [])

try:
    while True:
        #time.sleep(5)  # Keep the script running
        n=n+1    
except KeyboardInterrupt:
    print("Disconnecting...")
    app.disconnect()
    api_thread.join()