
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
import requests, json, sys, time, subprocess, csv
from requests.auth import HTTPDigestAuth


#url header to preprend on all IMC eAPI calls
url = None

#auth handler for eAPI calls
auth = None

#headers forcing IMC to respond with JSON content. XML content return is the default
headers = {'Accept': 'application/json', 'Content-Type': 'application/json','Accept-encoding': 'application/json'}

def create_operator():
    if auth == None or url == None:     #checks to see if the imc credentials are already available
        imc_creds()
    create_operator_url = '/imcrs/plat/operator'
    f_url = url+create_operator_url
    with open ('imc_operator_list.csv') as csvfile:      #opens imc_operator_list.csv file
        reader = csv.DictReader(csvfile)        #decodes file as csv as a python dictionary
        for operator in reader:
            payload = json.dumps(operator, indent=4)      #loads each row of the CSV as a JSON string
            r = requests.post(f_url, data=payload, auth=auth, headers=headers)   #creates the URL using the payload variable as the contents 
            if r.status_code == 409:        
                print ("Operator Already Exists")
            elif r.status_code == 201:
                print ("Operator Successfully Created")


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
    imc_pw = input("What is the password of the IMC eAPI user?")
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
    createoperator = input("Do you wish to create IMC Operators? Y/N:")
    if createoperator == "Y" or createoperator == "y":
        create_operator()

    
    


if __name__ == "__main__":
    main()

