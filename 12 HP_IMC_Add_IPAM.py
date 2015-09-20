



'''
import ipaddress
>>> a = ipaddress.ip_network('172.16.0.0/24')
>>> list(a.hosts())


list(a.subnets(new_prefix=30))


>>> b = list(a.subnets(new_prefix=30))
>>> len(b)
64
>>> type(b)
<class 'list'>
>>> b


>>> b[0].network_address
IPv4Address('172.16.0.0')

>>> c = list(b[0].hosts())
>>> c
[IPv4Address('172.16.0.1'), IPv4Address('172.16.0.2')]
>>> for i in b:
	hosts = list(i.hosts())
	print (hosts)

>>> test = []
>>> for i in b:
	hosts = list(i.hosts())
	test.append((hosts))


>>> for i in test:
	for b in i:
		print (str(b))	
>>> for i in test:
	print (str(i[0]))
	print (str(i[-1]))
	


#lists hosts
for i in test:
	for b in i:
		print (str(b))

def get_mask_length(ip1, ip2):
	ip1_int = int(ipaddress.ip_address(ip1))
	ip2_int = int(ipaddress.ip_address(ip2))
	unique_bits_int = abs(ip1_int - ip2_int)
	
	return ipaddress.ip_address(ip1).max_prefixlen - len('{:b}'.format(unique_bits_int))

		
>>> test = select_parent_segment()
>>> for i in test:
	print (i['id'] + ' ' + i['ip'])

	
-299 The system default IP segment
1 10.10.10.1-10.10.10.254
41 10.11.0.1-10.11.254.254
42 10.101.0.1-10.101.0.254
61 172.16.0.1-172.16.31.254

a = test[0]['ip']


        
new_ip_segment('10.10.10.0/24')
new_ip_segment('10.11.0.0/16')
new_ip_segment('10.101.0.0/24')
new_ip_segment('172.16.0.0/19')
new_ip_segment('192.168.0.1/24')


10.10.10.0/24
10.11.0.0/16
10.101.0.0/24
172.16.0.0/19



def new_ip_segment(ip_segment):
    parent_segments = select_parent_segment()
    for segment in parent_segments:
        if len(segment) > 6:
            start_ip = segment['startIp']
            end_ip = segment['endIp']
            netrange = ip_in_network(start_ip,end_ip)
            try:
                ip_segment = ipaddress.ip_network(ip_segment, strict = False)
                if ip_segment == netrange:
                    print ("Found it")
                else:
                    continue
            except:
                print ("There was an error")
                break



def ip_in_network(startIp, endIp):
    mask = 32
    startIp = ipaddress.ip_address(startIp)
    endIp = ipaddress.ip_address(endIp)
    netrange = ipaddress.ip_network(str(startIp)+'/'+str(mask), strict=False)
    while ((endIp in netrange) == False):
        mask -= 1
        netrange = ipaddress.ip_network(str(startIp)+'/'+str(mask), strict=False)
    return netrange
    
        
        
    

		
'''

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








def select_parent_segment():
    # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    global r
    get_root_ip_segment_url = "/imcrs/res/access/assignedIpScope/"
    f_url = url + get_root_ip_segment_url
    payload = None
    # creates the URL using the payload variable as the contents
    r = requests.get(f_url, auth=auth, headers=headers)
    r.status_code
    if r.status_code == 200:
        ip_segments = (json.loads(r.text))
        return ip_segments['assignedIpScope']
    
		


def add_ip_segment(parent_segment=None, ip_segment=None):
    if ip_segment == None:
        ip_segment = input('Please input the IP segment (ex.192.168.0.0/24): ')
    try:
        ip_segment = ipaddress.ip_network(ip_segment)
    except:
        print ('There was an error')
    networks = list(a.subnets(new_prefix=30))
    for network in networks:
        hosts = list(network.hosts())
        payload = '''{
        "startIp": "'''+str(hosts[0])+'''",
        "endIp": "'''+str(hosts[-1])+'''",
        "name": "'''+network.with_netmask+'''",
        "description": "'''+str(hosts[0])+''' to '''+str(hosts[-1])+'''"}'''
        print (json.dumps(json.loads(payload), indent=4))


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
