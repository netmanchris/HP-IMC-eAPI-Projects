from pysnmp.entity import engine, config
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.entity.rfc3413 import cmdgen
from pysnmp.proto import rfc1902

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

#
# SNMPv2c setup
#

# SecurityName <-> CommunityName mapping
config.addV1System(snmpEngine, 'my-area', 'private')

# Specify security settings per SecurityName (SNMPv1 - 0, SNMPv2c - 1)
config.addTargetParams(snmpEngine, 'my-creds', 'my-area', 'noAuthNoPriv', 1)

#
# Setup transport endpoint and bind it with security settings yielding
# a target name (choose one entry depending of the transport needed).
#

# UDP/IPv4
config.addSocketTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpSocketTransport().openClientMode()
)
config.addTargetAddr(
    snmpEngine, 'my-router',
    udp.domainName, ('10.101.0.221', 161),
    'private'
)

# Error/response reciever
def cbFun(sendRequestHandle,
          errorIndication, errorStatus, errorIndex,
          varBindTable, cbCtx):
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
            )
        )
    else:
        for oid, val in varBindTable:
            print('%s = %s' % (oid.prettyPrint(), val.prettyPrint()))

# Prepare and send a request message
cmdgen.SetCommandGenerator().sendReq(
    snmpEngine,
    'my-router',
    ( ((1,3,6,1,2,1,31,1,1,1,18,1), rfc1902.OctetString('Check this out')), ),
    cbFun
)

# Run I/O dispatcher which would send pending queries and process responses
snmpEngine.transportDispatcher.runDispatcher()
