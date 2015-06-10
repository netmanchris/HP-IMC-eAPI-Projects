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

#  IMC Server Build Project 1.0
#  Chris Young a.k.a Darth
#
#Hewlett Packard Company    Revision 1.0
#
#Change History.... 3/19/15
#

#This series of functions is intended to help automate the build of an IMC server using
#the eAPI function. The eAPI is available natively on the IMC enterprise edition
#and can be added to the standard edition through the purchase of the eAPI addon license.

#This section imports required libraries
import requests, json, sys, time, subprocess, csv, os, ipaddress
from requests.auth import HTTPDigestAuth


#url header to preprend on all IMC eAPI calls
url = None

#auth handler for eAPI calls
auth = None

#headers forcing IMC to respond with JSON content. XML content return is the default
headers = {'Accept': 'application/json', 'Content-Type': 'application/json','Accept-encoding': 'application/json'}1    



#This sections deals with getting the topology id and links and capturing them in a dictionary

def get_links():
    topo_id = select_a_view()
    get_links_url = '''/imcrs/plat/res/link?topoId='''+topo_id+'''&total=false'''
    f_url = url + get_links_url
    r = requests.get(f_url, auth=auth, headers=headers)   #creates the URL using the payload variable as the contents 
    if r.status_code == 200:
         link_list = (json.loads(r.text))
         return link_list
  



def get_custom_views():
    if auth == None or url == None:  # checks to see if the imc credentials are already available
        imc_creds()
    get_custom_view_url = '/imcrs/plat/res/view/custom?resPrivilegeFilter=false&desc=false&total=false'
    f_url = url + get_custom_view_url
    r = requests.get(f_url, auth=auth, headers=headers)   #creates the URL using the payload variable as the contents 
    if r.status_code == 200:
         view_list = (json.loads(r.text))["customView"]
         return view_list
    else:
         print ("An Error has occured")

def find_a_view():
    view_name = input("Please input the name of the view you wish to add devices to: ")
    view_list = get_custom_views()
    for i in view_list:
        if i['name'].lower() == view_name.lower():
            return i['symbolId']
        
def select_a_view():
    view_list = get_custom_views()
    print ("Please Select from the Available Custom Views: ")
    for i in view_list:
        print ("View Name: "+i['name'])
    topo_id = find_a_view()
    return topo_id


#This section correlates the device label from the topology database to a specific device id. Then correlates the ifDesc to a specific ifIndex value

def filter_dev_category(dev_label):
    if auth == None or url == None:  # checks to see if the imc credentials are already available
        imc_creds()
    global r
    get_dev_list_url = ("/imcrs/plat/res/device?resPrivilegeFilter=false&label="+dev_label+"&start=0&size=10&orderBy=id&desc=false&total=false")
    f_url = url + get_dev_list_url
    
    payload = None
    r = requests.get(f_url, auth=auth, headers=headers)   #creates the URL using the payload variable as the contents
    r.status_code
    if r.status_code == 200:
         dev_list = (json.loads(r.text))["device"]
         return dev_list
    else:
         print ("An Error has occured")

def get_dev_interface(dev_id):
    if auth == None or url == None:  # checks to see if the imc credentials are already available
        imc_creds()
    global r
    get_dev_interface_url = "/imcrs/plat/res/device/"+dev_id+"/interface?start=0&size=1000&desc=false&total=false"
    f_url = url + get_dev_interface_url
    payload = None
    r = requests.get(f_url, auth=auth, headers=headers)   #creates the URL using the payload variable as the contents
    r.status_code
    if r.status_code == 200:
         int_list = (json.loads(r.text))['interface']
         return int_list
    else:
         print ("An Error has occured")

def find_int(ifDesc, int_list):
	for i in int_list:
		if i["ifDescription"] == ifDesc:
			return i["ifIndex"]         
         
#This sections contains helper functions leveraged by other other functions



def imc_creds():
    ''' This function prompts user for IMC server information and credentuials and stores
    values in url and auth global variables'''
    global url, auth, r
    imc_protocol = input("What protocol would you like to use to connect to the IMC server: \n Press 1 for HTTP: \n Press 2 for HTTPS:")
    if imc_protocol == "1":
        h_url = 'http://'
    else:
        h_url = 'https://'
    imc_server = input("What is the ip address of the IMC server?")
    imc_port = input("What is the port number of the IMC server?")
    imc_user = input("What is the username of the IMC eAPI user?")
    imc_pw = input('''What is the password of the IMC eAPI user?''')
    url = h_url+imc_server+":"+imc_port
    auth = requests.auth.HTTPDigestAuth(imc_user,imc_pw)
    test_url = '/imcrs'
    f_url = url+test_url
    try:
        r = requests.get(f_url, auth=auth, headers=headers)
    except requests.exceptions.RequestException as e:     #checks for reqeusts exceptions
            print ("Error:\n"+str(e))
            print ("\n\nThe IMC server address is invalid. Please try again\n\n")
            imc_creds()
    if r.status_code != 200:      #checks for valid IMC credentials
        print ("Error: \n You're credentials are invalid. Please try again\n\n")
        imc_creds()
    else:
        print ("You've successfully access the IMC eAPI")
    
    
#Defines the program to be run
        
def main():
    if auth == None or url == None:  # checks to see if the imc credentials are already available
        imc_creds()
    view_name = create_new_view()
    view_list = get_custom_views()
    view_id = get_view_id(view_name)
    dev_list = filter_dev_category()
    add_device_to_view(dev_list, view_id)


if __name__ == "__main__":
    main()
