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
        self.ip = dev_details(ip_address)['ip']
        self.description = dev_details(ip_address)['sysDescription']
        self.location = dev_details(ip_address)['location']
        self.contact = dev_details(ip_address)['contact']
        self.type = dev_details(ip_address)['typeName']
        self.name = dev_details(ip_address)['sysName']
        self.status = dev_details(ip_address)['statusDesc']
        self.devid = dev_details(ip_address)['id']

        self.interfacelist = dev_interface(self.devid)
        self.numinterface = len(dev_interface(self.devid))
        self.vlans = dev_vlans(self.devid)['vlan']
        self.accessinterfaces = get_device_access_interfaces(self.devid)['accessIf']
        self.trunkinterfaces = get_trunk_interfaces(self.devid)['trunkIf']
        self.alarm = dev_alarms(self.devid)['alarm']
        self.numalarm = len(dev_alarms(self.devid)['alarm'])
        self.serial = get_serial_numbers(get_dev_asset_details(self.ip)['netAsset'])
        self.runconfig = dev_run_config(self.devid)
        self.startconfig = dev_start_config(self.devid)

class imc_interface():
    def __init__(self, ip_address, ifIndex):
        self.ip = dev_details(ip_address)['ip']
        self.devid = dev_details(ip_address)['id']
        self.ifIndex = get_interface_details(self.devid, ifIndex)['ifIndex']
        self.macaddress = get_interface_details(self.devid, ifIndex)['phyAddress']
        self.status = get_interface_details(self.devid, ifIndex)['statusDesc']
        self.adminstatus = get_interface_details(self.devid, ifIndex)['adminStatusDesc']
        self.name = get_interface_details(self.devid, ifIndex)['ifDescription']
        self.description = get_interface_details(self.devid, ifIndex)['ifAlias']
        self.mtu = get_interface_details(self.devid, ifIndex)['mtu']
        self.speed = get_interface_details(self.devid, ifIndex)['ifspeed']
        self.accessinterfaces = get_device_access_interfaces(self.devid)['accessIf']
        self.pvid = get_access_interface_vlan(self.ifIndex, self.accessinterfaces)

class host(imc_dev):
    def __init__(self, ip_address):
        self.hostip = real_time_locate(ip_address)['locateIp']
        self.deviceip = real_time_locate(ip_address)['deviceIp']
        self.ifIndex = real_time_locate(ip_address)['ifIndex']
        self.devid = real_time_locate(ip_address)['deviceId']
        self.accessinterfaces = get_device_access_interfaces(self.devid)['accessIf']
        self.pvid = get_access_interface_vlan(self.ifIndex, self.accessinterfaces)
        self.devstatus = dev_details(self.deviceip)['statusDesc']
        self.status = get_interface_details(self.devid, self.ifIndex)['statusDesc']


        
def get_dev_asset_details(ipAddress):
       # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_asset_url = "/imcrs/netasset/asset?assetDevice.ip="+ipAddress
    f_url = url + get_dev_asset_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        dev_asset_info = (json.loads(r.text))
        return dev_asset_info
    else:
        print("get_dev_asset_details:  An Error has occured")    

def get_serial_numbers(assetList):
    serial_list = []
    if type(assetList) == list:
        for i in assetList:
            if len(i['serialNum']) > 0:
                serial_list.append(i)
    return serial_list

def get_trunk_interfaces(devId):
       # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_trunk_interfaces_url = "/imcrs/vlan/trunk?devId="+devId+"&start=1&size=5000&total=false"
    f_url = url + get_trunk_interfaces_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        dev_trunk_interfaces = (json.loads(r.text))
        if len(dev_trunk_interfaces) == 2:
            return dev_trunk_interfaces
        else:
            dev_trunk_interfaces['trunkIf'] = "No trunk inteface"
            return dev_trunk_interfaces
        dev_trunk_interfaces = (json.loads(r.text))['trunkIf']
    
def get_access_interface_vlan(ifIndex, accessinterfacelist):
    for i in accessinterfacelist:
        if i['ifIndex'] == ifIndex:
            return i['pvid']
        else:
            return "Not an Access Port"

def get_device_access_interfaces(devId):
       # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_access_interface_vlan_url = "/imcrs/vlan/access?devId="+devId+"&start=1&size=500&total=false"
    f_url = url + get_access_interface_vlan_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        dev_access_interfaces = (json.loads(r.text))
        if len(dev_access_interfaces) == 2:
            return dev_access_interfaces
        else:
            dev_access_interfaces['accessIf'] = "No access inteface"
            return dev_access_interfaces
    else:
        print("get_device_access_interfaces: An Error has occured")
        





def get_interface_details(devId, ifIndex):
       # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_interface_details_url = "/imcrs/plat/res/device/"+devId+"/interface/"+ifIndex
    f_url = url + get_interface_details_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        dev_details = (json.loads(r.text))
        return dev_details
    else:
        print("get_interface_details: An Error has occured")

    
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
        if type(dev_details['device']) == list:
            for i in dev_details['device']:
                if i['ip'] == ip_address:
                    dev_details = i
                    return dev_details
        elif type(dev_details['device']) == dict:
            return dev_details['device']
    else:
        print("dev_details: An Error has occured")


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
    elif r.status_code == 409:
        return {'vlan':'no vlans'}
    else:
        print("dev_vlans: An Error has occured")
        


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

def real_time_locate(ipAddress):
    if auth == None or url == None:  # checks to see if the imc credentials are already available
        imc_creds()
    real_time_locate_url = "/imcrs/res/access/realtimeLocate?type=2&value="+ipAddress+"&total=false"
    f_url = url + real_time_locate_url
    r = requests.get(f_url, auth=auth, headers=headers)   #creates the URL using the payload variable as the contents
    if r.status_code == 200:
        return (json.loads(r.text)['realtimeLocation'])
          
    else:
     print (r.status_code)
     print ("An Error has occured")


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
