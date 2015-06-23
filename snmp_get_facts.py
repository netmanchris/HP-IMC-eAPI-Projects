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


from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
import json

cmdGen = cmdgen.CommandGenerator()

class snmp_dev():
  def __init__(self, rostring, ip_address):
      self.rostring = rostring
      self.ip_address = ip_address
      self.description = (get_sysdescr(self.rostring, self.ip_address))
      self.syscontact = (get_sysContact(self.rostring, self.ip_address))
      self.systemname = (get_systemName(self.rostring, self.ip_address))
      self.syslocation = (get_systemLocation(self.rostring, self.ip_address))
      self.interfacelist = (get_sys_ints(self.rostring, self.ip_address))  #works for first 100 interfaces only based on range command
      self.numinterfaces = len(self.interfacelist)


def get_sysdescr(rostring, ip_address):
       description = cmdGen.getCmd(cmdgen.CommunityData(rostring),
                          cmdgen.UdpTransportTarget((ip_address, 161)),
                          '.1.3.6.1.2.1.1.1.0')
       return str(description[3][0][1])

def get_sysContact(rostring, ip_address):
       syscontact = cmdGen.getCmd(cmdgen.CommunityData(rostring),
                          cmdgen.UdpTransportTarget((ip_address, 161)),
                          '.1.3.6.1.2.1.1.4.0')
       return str(syscontact[3][0][1])

def get_systemName(rostring, ip_address):
    systemname = cmdGen.getCmd(cmdgen.CommunityData(rostring),
                          cmdgen.UdpTransportTarget((ip_address, 161)),
                          '.1.3.6.1.2.1.1.5.0')
    return str(systemname[3][0][1])

def get_systemLocation(rostring, ip_address):
    location = cmdGen.getCmd(cmdgen.CommunityData(rostring),
                          cmdgen.UdpTransportTarget((ip_address, 161)),
                          '.1.3.6.1.2.1.1.6.0')
    return str(location[3][0][1])

def get_sys_ints(rostring, ip_address):
    int_range = range(1,1000)
    iflist = []
    for i in int_range:
        ifindex = i
        interface = cmdGen.getCmd(cmdgen.CommunityData(rostring),
                          cmdgen.UdpTransportTarget((ip_address, 161)),
                          '.1.3.6.1.2.1.2.2.1.2.'+str(ifindex))
        interface = str(interface[3][0][1])
        if len(interface) > 0:
            interface = {'Description':interface, 'ifIndex': ifindex}
            iflist.append(interface)
        else:
            return iflist


    
 
    



    
    




    
