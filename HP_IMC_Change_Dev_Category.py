
#   IMC Server Build Project 1.0
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
headers = {'Accept': 'application/json', 'Content-Type': 'application/json','Accept-encoding': 'application/json'}

def change_dev_category():
    global dev_list
    dev_list = filter_dev_category()
    for dev in dev_list:
        print ("system name: "+ dev['sysName']+'\nCurrent Category: '+dev['devCategoryImgSrc']+
               '\nIP address: '+ dev['ip']+'\nSystem Description: '+dev['sysDescription']+ '\n\n')
    print_dev_category()
    cat_id = input("What is the category to which you want to move the selected device: ")
    for i in dev_list:
        dev_id = i["id"]
        change_dev_cat_url = "/imcrs/plat/res/device/"+dev_id+"/updateCategory"
        f_url = url + change_dev_cat_url
        payload = '''{ "categoryId" : "'''+cat_id+'''" }'''
        r = requests.put(f_url, data=payload, auth=auth, headers=headers)   #creates the URL using the payload variable as the contents
        if r.status_code == 204:
            continue  
        else:
         print (r.status_code)
         print ("An Error has occured")

def filter_dev_category():
    if auth == None or url == None:  # checks to see if the imc credentials are already available
        imc_creds()
    global r
    category = None
    ip_range = None
    get_dev_list_url = None
    filter_by_cat = input("Do you want to filter by device category?\nY/N: ")
    if filter_by_cat.lower() == "y":
        print_dev_category()
        category = input("Please select the device category: ")
        get_dev_list_url = ("/imcrs/plat/res/device?resPrivilegeFilter=false&category="+category+"&start=0&size=10000&orderBy=id&desc=false&total=false")
        #return get_dev_list_url
    filter_by_ip = input("Do you want to filter by IP address network range?\nY/N: ")
    if filter_by_ip.lower() == "y":
        ip_range = input("What is the ip network range?\n Example: 10.101.16.\nFuzzy search is acceptible: ")
        if category == None:
            get_dev_list_url = ("/imcrs/plat/res/device?resPrivilegeFilter=false&ip="+ip_range+"&start=0&size=5&orderBy=id&desc=false&total=false")
        else:
            get_dev_list_url = ("/imcrs/plat/res/device?resPrivilegeFilter=false&category="+category+"&ip="+ip_range+"&start=0&size=10000&orderBy=id&desc=false&total=false")
    f_url = url + get_dev_list_url
    
    payload = None
    r = requests.get(f_url, auth=auth, headers=headers)   #creates the URL using the payload variable as the contents
    r.status_code
    if r.status_code == 200:
         dev_list = (json.loads(r.text))["device"]
         return dev_list
    else:
         print ("An Error has occured")
        
                         
        
        

def print_dev_category():
    categories = [{"categoryId":"0", "dev_type":"router"},
              {"categoryId":"1", "dev_type":"switch"},
              {"categoryId":"2", "dev_type":"server"},
              {"categoryId":"3", "dev_type":"security"},
              {"categoryId":"4", "dev_type":'storage' },
              {"categoryId":"5", "dev_type":"wireless"},
              {"categoryId":"6", "dev_type": "voice"},
              {"categoryId":"7", "dev_type":'printer'},
              {"categoryId":"8", "dev_type":'ups'},
              {"categoryId":"9", "dev_type":"desktop"},
              {"categoryId":"10", "dev_type":"other"},
              {"categoryId":"11", "dev_type":"surveillance"},
              {"categoryId":"12", "dev_type":"video"},
              {"categoryId":"13", "dev_type":"module"},
              {"categoryId":"14", "dev_type":"virtualdev"},
	      {"categoryId":"15", "dev_type":"Load Balancer"},
              {"categoryId":"16", "dev_type":"sdn_ctrl"}
              ]
    for i in categories:
        print ("For "+i["dev_type"]+", Please press: "+i["categoryId"])
    





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
    add_device = input("Do you wish to change device categories now? Y/N:")
    if add_device.lower() == "y":
        change_dev_category()

    
    


if __name__ == "__main__":
    main()

