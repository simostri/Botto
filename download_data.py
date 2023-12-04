#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 19:09:46 2023

@author: simonestriani
"""

import requests
import json
# Disable SSL Warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def historicalData():
    base_url = "https://localhost:5000/v1/api/"
    endpoint = "hmds/history"

    conid = "conid=265598"
    period = "period=1y"  # Time period
    bar = "bar=1d"        # Bar time interval
    outsideRth = "outsideRth=true"
    barType = "barType=midpoint"

    params = "&".join([conid, period, bar, outsideRth, barType])
    request_url = "".join([base_url, endpoint, "?", params])

    hd_req = requests.get(url=request_url, verify=False)
    hd_json = hd_req.json()

    # Extract time period and bar interval for filename
    time_period = period.split('=')[1]
    bar_interval = bar.split('=')[1]

    filename = f'historical_data_{time_period}_{bar_interval}.json'

    # Save JSON data to a file
    with open(filename, 'w') as file:
        json.dump(hd_json, file, indent=2)

    print(hd_req)
    print(json.dumps(hd_json, indent=2))

    return hd_json

historicalData()