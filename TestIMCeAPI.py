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

''' Purpose of this script is to automate the testing of the IMC eAPI RESTful calls.
The actual response is not tested at this time. Only the precence of a valid
HTTP Status Codes.  Test name, Test result (Pass/Fail), and HTTP response code
will be captured and written as output to CSV file for validation. '''

test_result = []

def write_test_result(test_result):
    '''Writes list of dictionaries test_result to test_result.csv using the
    key values of the first dictionary in the list as the headers for the columns'''
    keys = test_result[0].keys()
    with open('test_result.csv', 'w') as f:
        dict_writer = csv.DictWriter(f,keys)
        dict_writer.writeheader()
        dict_writer.writerows(test_result)

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
        self.startconfig = None

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
        test = {'TestName':'GetDevAssetDetails','TestResult':'Pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return dev_asset_info
    else:
        print("get_dev_asset_details:  An Error has occured")
        test = {'TestName':'GetDevAssetDetails','TestResult':'Fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)

def get_serial_numbers(assetList):
    serial_list = []
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
        test = {'TestName':'get_trunk_interfaces','TestResult':'Pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        if len(dev_trunk_interfaces) == 2:
            test = {'TestName':'get_trunk_interfaces','TestResult':'Pass','StatusCode':r.status_code, 'Content': r.content}
            test_result.append(test)
            return dev_trunk_interfaces
        
        else:
            dev_trunk_interfaces['trunkIf'] = "No trunk inteface"
            test = {'TestName':'get_trunk_interfaces','TestResult':'Pass','StatusCode':r.status_code, 'Content': r.content}
            test_result.append(test)
            return dev_trunk_interfaces
        dev_trunk_interfaces = (json.loads(r.text))['trunkIf']
    else:
        test = {'TestName':'get_trunk_interfaces','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        print ('get_trunk_interfaces: an error occurred')
    
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
        test = {'TestName':'get_device_access_interfaces','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        if len(dev_access_interfaces) == 2:
            test = {'TestName':'get_device_access_interfaces','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
            test_result.append(test)
            return dev_access_interfaces
        else:
            dev_access_interfaces['accessIf'] = "No access inteface"
            return dev_access_interfaces
    else:
        test = {'TestName':'get_device_access_interfaces','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
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
        test = {'TestName':'get_interface_details','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return dev_details
    else:
        test = {'TestName':'get_interface_details','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
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
        test = {'TestName':'Get_Dev_Details','TestResult':'Pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        if type(dev_details['device']) == list:
            for i in dev_details['device']:
                if i['ip'] == ip_address:
                    dev_details = i
                    test = {'TestName':'Get_Dev_Details','TestResult':'Pass','StatusCode':r.status_code, 'Content': r.content}
                    test_result.append(test)
                    return dev_details
        elif type(dev_details['device']) == dict:
            return dev_details['device']
    else:
        print("dev_details: An Error has occured")
        test = {'TestName':'Get_Dev_Details','TestResult':'Fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)


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
        test = {'TestName':'dev_vlans','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return dev_details
    elif r.status_code == 409:
        test = {'TestName':'dev_vlans','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return {'vlan':'no vlans'}
    else:
        test = {'TestName':'dev_vlans','TestResult':'Fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
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
        test = {'TestName':'dev_interfaces','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return int_list
    else:
        test = {'TestName':'dev_interfaces','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
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
        test = {'TestName':'dev_run_config','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return run_conf
    else:
        test = {'TestName':'dev_run_config','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)


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
        test = {'TestName':'dev_start_config','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return start_conf
    else:
        test = {'TestName':'dev_start_config','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)


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
        test = {'TestName':'dev_alarms','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return dev_alarm
    else:
        test = {'TestName':'dev_alarms','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)

def set_interface_up(devId, ifIndex):
    if auth == None or url == None:
        imc_creds()
    global r
    set_int_up_url = "/imcrs/plat/res/device/" + devId +"/interface/" + ifIndex + "/up"
    f_url = url + set_int_up_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.put(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 204:
        test = {'TestName':'set_interface_up','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return "up"
    else:
        test = {'TestName':'set_interface_up','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return "set_interface_up: An Error has occured"

def set_interface_down(devId, ifIndex):
    if auth == None or url == None:
        imc_creds()
    global r
    set_int_up_url = "/imcrs/plat/res/device/" + devId +"/interface/" + ifIndex + "/down"
    f_url = url + set_int_up_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.put(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 204:
        test = {'TestName':'set_interface_down','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return "down"
    else:
        test = {'TestName':'set_interface_down','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return "set_interface_up: An Error has occured"

def get_terminal_location(terminal_ip_address):
    if auth == None or url == None:
        imc_creds()
    global r
    get_terminal_location_url = "/imcrs/res/access/realtimeLocate?type=2&value="+ terminal_ip_address +"&total=false"
    f_url = url + get_terminal_location_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        test = {'TestName':'get_terminal_location','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        terminal_location = (json.loads(r.text))
        return terminal_location["realtimeLocation"]
    else:
        test = {'TestName':'get_terminal_location','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return "get_terminal_location: An Error has occured"

def get_dev_ip_mac_arp(devid):
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_ip_mac_arp_url = "/imcrs/res/access/ipMacArp/"+ devid +"?start=1&size=1000"
    f_url = url + get_dev_ip_mac_arp_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        test = {'TestName':'get_dev_ip_mac_arp','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        dev_ip_mac_arp = (json.loads(r.text))
        return dev_ip_mac_arp['ipMacArp']
    else:
        test = {'TestName':'get_dev_ip_mac_arp','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return "get_dev_ip_mac_arp: An Error has occured"

def get_dev_ip_mac_learning(devid):
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_ip_mac_learning_url = "/imcrs/res/access/ipMacLearn/"+devid+"?start=1&size=1000"
    f_url = url + get_dev_ip_mac_learning_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        test = {'TestName':'get_dev_ip_mac_learning','TestResult':'pass','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        dev_ip_mac_arp = (json.loads(r.text))
        return dev_ip_mac_arp['ipMacLearnResult']
    else:
        test = {'TestName':'get_dev_ip_mac_learning','TestResult':'fail','StatusCode':r.status_code, 'Content': r.content}
        test_result.append(test)
        return "get_dev_ip_mac_learning: An Error has occured"

def get_dev_model_list():
    if auth == None or url == None:
        imc_creds()
    global r
    get_dev_model_list_url = "/imcrs/plat/res/model?start=0&size=10000"
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


def main():
    creds = imc_creds('1','admin','#password#','10.101.0.202','8080')
    if creds == 'fail':
        sys.exit('Credentials Failure. Aborting test')
    dev_details('10.101.0.221')
    get_dev_asset_details('10.101.0.221')
    get_trunk_interfaces('2')
    get_device_access_interfaces('2')
    get_interface_details('2', '78')
    dev_vlans('2')
    dev_interface('2')
    dev_run_config('2')
    dev_start_config('2')
    dev_alarms('2')
    set_interface_down('2', '78')
    set_interface_down('2', '78')
    get_terminal_location('10.101.0.51')
    get_dev_ip_mac_arp('2')
    get_dev_ip_mac_learning('2')
    
    
    
    write_test_result(test_result)



