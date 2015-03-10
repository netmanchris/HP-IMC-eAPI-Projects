__author__ "@netmanchris"
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

#This section contains global variables
imc_protocol = None
imc_server = None
imc_port = None
imc_user = None
imc_pw = None
imc_app =
headers = {'Accept': 'application/json', 'Content-Type': 'application/json','Accept-encoding': 'application/json'}
Def imc_creds():
    global imc_protocol, imc_ip,imc_port, imc_user, imc_pw
    imc_protocol = input("What is the protocol of the IMC server? http/https:)
    imc_server = input("What is the ip address of the IMC server?")
    imc_port = input("What is the port number of the IMC server?")
    imc_user = input("What is the username of the IMC eAPI user?")
    imc_pw = input("What is the password of the IMC eAPI user?")

Def main():            
    createoperator = input("Do you wish to create IMC Operators? Y/N:")
    if createoperator == "Y" or createoperator == "y":
        create_operator()

Def create_operator():
    if imc_protocol == None:
            imc_creds()
    
    




