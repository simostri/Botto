#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 22:06:30 2023

@author: simonestriani
"""

import requests

# Disable SSL Warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# reauthenticate
def confirmStatus():
    base_url = "https://localhost:5000/v1/api/"
    endpoint = "iserver/auth/status"
    
    auth_req = requests.get(url=base_url+endpoint,verify=False)
    print(auth_req)
    print(auth_req.text)

if __name__ == "__main__":
    confirmStatus()