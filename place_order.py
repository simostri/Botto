#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 17:28:27 2023

@author: simonestriani
"""

import requests
import json
import urllib3

# Ignore insecure error messages
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def orderRequest():
  
    base_url = "https://localhost:5000/v1/api/"
    endpoint = "iserver/account/DU7561652/orders"

    json_body = {
        "orders": [
            {
            "conid": 265598,
            "orderType": "MKT",
            "side": "BUY",
            "tif": "DAY",
            "quantity":1,
            }
        ]
    }
    order_req = requests.post(url = base_url+endpoint, verify=False, json=json_body)
    order_json = json.dumps(order_req.json(), indent=2)

    print(order_req.status_code)
    print(order_json)

if __name__ == "__main__":
    orderRequest()