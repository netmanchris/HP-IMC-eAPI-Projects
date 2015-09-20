'''Copyright 2015 Chris Young

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.'''
# This section imports required libraries
import requests
import json
import sys
import time
import subprocess
import csv
import os
import ipaddress
import pysnmp
from requests.auth import HTTPDigestAuth
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
cmdGen = cmdgen.CommandGenerator()





test_result = []




def get_dev_model_list():
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_model_list_url = "/imcrs/plat/res/model?category=0&start=0&size=10000"
    f_url = url + get_dev_model_list_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        test = {'TestName':'get_dev_model_list','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        dev_model_list = (json.loads(r.text))
        return dev_model_list['deviceModel']
    else:
        test = {'TestName':'get_dev_model_list','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return "get_dev_model_list: An Error has occured"


# url header to preprend on all IMC eAPI calls
url = None

# auth handler for eAPI calls
auth = None

# headers forcing IMC to respond with JSON content. XML content return is
# the default
headers = {'Accept': 'application/json', 'Content-Type':
           'application/json', 'Accept-encoding': 'application/json'}


def imc_creds(imc_protocol=None,imc_user=None, imc_pw=None, imc_server=None, imc_port=None):
    ''' This function prompts user for IMC server information and credentuials and stores
    values in url and auth global variables'''
    global url, auth, r
    if imc_protocol == None:
        imc_protocol = input("What protocol would you like to use to connect to the IMC server: \n Press 1 for HTTP: \n Press 2 for HTTPS:")
    if imc_protocol == "1":
        h_url = 'http://'
    else:
        h_url = 'https://'
    if imc_server == None:
        imc_server = input("What is the ip address of the IMC server?")
    if imc_pw == None:
        imc_port = input("What is the port number of the IMC server?")
    if imc_user == None:
        imc_user = input("What is the username of the IMC eAPI user?")
    if imc_pw == None:
        imc_pw = input('''What is the password of the IMC eAPI user?''')
    url = h_url + imc_server + ":" + imc_port
    auth = requests.auth.HTTPDigestAuth(imc_user, imc_pw)
    test_url = '/imcrs'
    f_url = url + test_url
    try:
        r = requests.get(f_url, auth=auth, headers=headers, verify=False)
    # checks for reqeusts exceptions
    except requests.exceptions.RequestException as e:
        print("Error:\n" + str(e))
        print("\n\nThe IMC server address is invalid. Please try again\n\n")
        imc_creds()
    if r.status_code != 200:  # checks for valid IMC credentials
        print("Error: \n You're credentials are invalid. Please try again\n\n")
        #imc_creds()
        test = {'TestName':'imc_creds','TestResult':'Fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return 'fail'

    else:
        print("You've successfully access the IMC eAPI")
        test = {'TestName':'imc_creds','TestResult':'Pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return 'pass'
