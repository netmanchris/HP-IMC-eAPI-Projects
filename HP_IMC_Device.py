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


# IMC Device Class

class imc_dev():

    def __init__(self, ip_address):
        self.ip = dev_details(ip_address)['device']['ip']
        self.description = dev_details(ip_address)['device']['sysDescription']
        self.location = dev_details(ip_address)['device']['location']
        self.contact = dev_details(ip_address)['device']['contact']
        self.type = dev_details(ip_address)['device']['typeName']
        self.name = dev_details(ip_address)['device']['sysName']
        self.status = dev_details(ip_address)['device']['statusDesc']
        self.devid = dev_details(ip_address)['device']['id']

        self.interfacelist = dev_interface(self.devid)
        self.numinterface = len(dev_interface(self.devid))
        self.vlans = dev_vlans(self.devid)['vlan']
        self.alarm = dev_alarms(self.devid)['alarm']
        self.numalarm = len(dev_alarms(self.devid)['alarm'])
        #self.serial = None
        self.runconfig = dev_run_config(self.devid)
        self.startconfig = None


def dev_details(ip_address):
    # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_details_url = "/imcrs/plat/res/device?resPrivilegeFilter=false&ip=" + \
        ip_address + "&start=0&size=10&orderBy=id&desc=false&total=false"
    f_url = url + get_dev_details_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        dev_details = (json.loads(r.text))
        return dev_details
    else:
        print("An Error has occured")


def dev_vlans(devId):
    # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_vlans_url = "/imcrs/vlan?devId=" + \
        devId + "&start=0&size=10&total=false"
    f_url = url + get_dev_vlans_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        dev_details = (json.loads(r.text))
        return dev_details
    else:
        print("An Error has occured")


def dev_interface(dev_id):
    # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_interface_url = "/imcrs/plat/res/device/" + dev_id + \
        "/interface?start=0&size=1000&desc=false&total=false"
    f_url = url + get_dev_interface_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        int_list = (json.loads(r.text))['interface']
        return int_list
    else:
        print("An Error has occured")


def dev_run_config(devId):
    # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_run_url = "/imcrs/icc/deviceCfg/" + devId + "/currentRun"
    f_url = url + get_dev_run_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        run_conf = (json.loads(r.text))['content']
        return run_conf


def dev_start_config(devId):
    # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_run_url = "/imcrs/icc/deviceCfg/" + devId + "/currentStart"
    f_url = url + get_dev_run_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        start_conf = (json.loads(r.text))['content']
        return start_conf


def dev_alarms(devId):
    # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_alarm_url = "/imcrs/fault/alarm?operatorName=admin&deviceId=" + \
        devId + "&desc=false"
    f_url = url + get_dev_alarm_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        dev_alarm = (json.loads(r.text))
        return dev_alarm


# url header to preprend on all IMC eAPI calls
url = None

# auth handler for eAPI calls
auth = None

# headers forcing IMC to respond with JSON content. XML content return is
# the default
headers = {'Accept': 'application/json', 'Content-Type':
           'application/json', 'Accept-encoding': 'application/json'}


def imc_creds():
    ''' This function prompts user for IMC server information and credentuials and stores
    values in url and auth global variables'''
    global url, auth, r
    imc_protocol = input(
        "What protocol would you like to use to connect to the IMC server: \n Press 1 for HTTP: \n Press 2 for HTTPS:")
    if imc_protocol == "1":
        h_url = 'http://'
    else:
        h_url = 'https://'
    imc_server = input("What is the ip address of the IMC server?")
    imc_port = input("What is the port number of the IMC server?")
    imc_user = input("What is the username of the IMC eAPI user?")
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
        imc_creds()
    else:
        print("You've successfully access the IMC eAPI")
