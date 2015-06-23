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

#   IMC Server Build Project 1.0
#  Chris Young a.k.a Darth
#
# Hewlett Packard Company    Revision 1.0
#
# Change History.... 3/19/15
#

# This series of functions is intended to help automate the build of an IMC server using
# the eAPI function. The eAPI is available natively on the IMC enterprise edition
# and can be added to the standard edition through the purchase of the
# eAPI addon license.

# This section imports required libraries
import requests
import json
import sys
import time
import subprocess
import csv
from requests.auth import HTTPDigestAuth


# url header to preprend on all IMC eAPI calls
url = None

# auth handler for eAPI calls
auth = None

# headers forcing IMC to respond with JSON content. XML content return is
# the default
headers = {'Accept': 'application/json', 'Content-Type':
           'application/json', 'Accept-encoding': 'application/json'}


def create_operator():
    # checks to see if the imc credentials are already available
    if auth == None or url == None:
        imc_creds()
    create_operator_url = '/imcrs/plat/operator'
    f_url = url + create_operator_url
    # opens imc_operator_list.csv file
    with open('imc_operator_list.csv') as csvfile:
        # decodes file as csv as a python dictionary
        reader = csv.DictReader(csvfile)
        for operator in reader:
            # loads each row of the CSV as a JSON string
            payload = json.dumps(operator, indent=4)
            # creates the URL using the payload variable as the contents
            r = requests.post(f_url, data=payload, auth=auth, headers=headers)
            if r.status_code == 409:
                print("Operator Already Exists")
            elif r.status_code == 201:
                print("Operator Successfully Created")


# This sections contains helper functions leveraged by other other functions

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
        r = requests.get(f_url, auth=auth, headers=headers)
    # checks for requests exceptions
    except requests.exceptions.RequestException as e:
        print("Error:\n" + str(e))
        print("\n\nThe IMC server address is invalid. Please try again\n\n")
        imc_creds()
    if r.status_code != 200:  # checks for valid IMC credentials
        print("Error: \n You're credentials are invalid. Please try again\n\n")
        imc_creds()
    else:
        print("You've successfully access the IMC eAPI")


# Defines the program to be run

def main():
    createoperator = input("Do you wish to create IMC Operators? Y/N:")
    if createoperator == "Y" or createoperator == "y":
        create_operator()


if __name__ == "__main__":
    main()
