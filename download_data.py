#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 19:09:46 2023

@author: simonestriani
"""

import requests
import json
import pandas as pd
import mplfinance as mpf
# Disable SSL Warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def historicalData():
    base_url = "https://localhost:5000/v1/api/"
    endpoint = "hmds/history"

    conid="conid=265598"
    period="period=1w"  # Changed to 2 months
    bar="bar=1min"      # Changed to 5-minute intervals
    outsideRth="outsideRth=true"
    barType="barType=midpoint"

    params = "&".join([conid, period, bar, outsideRth, barType])
    request_url = "".join([base_url, endpoint, "?", params])

    hd_req = requests.get(url=request_url, verify=False)
    hd_json = hd_req.json()

    # Save JSON data to a file
    with open('historical_data_2M_5min.json', 'w') as file:
        json.dump(hd_json, file, indent=2)

    print(hd_req)
    print(json.dumps(hd_json, indent=2))

    return hd_json