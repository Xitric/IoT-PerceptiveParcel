from rdflib import Literal
from wrapper import *

# TODO: methods for querying and inserting into the ontology ttl file
# TODO: host on local server?

# Might contain:
#   Devices and their ids
#   Mapping of current package ids to devices
#   Device types and the data they generate
#       Where this data is published (the topics)
#   Setpoint values for package types

# Kasper's ESP has machine id:
#   30aea4ddc98c
g = model()

def _init():
    packageId = 'ab3dm23jhl43bfj'
    Package = IOTPP['/package/'+packageId]

    PackageType = IOTPP['/packagetype']
    package_identifier = "letter"

    temperaturSetPoint = IOTPP['/temperatur']
    humititySetPoint = IOTPP['/humitity']
    motionSetPoint = IOTPP['/motion']

    temperaturValue = 23
    humitityValue = 60
    motionValue = 100

    g.add((Package, RDF.type, IOTPP.Package))
    g.add((Package, IOTPP.hasPackageType, PackageType))
    g.add((Package, IOTPP.packageId, Literal(packageId,datatype=XSD.ID)))

    g.add((PackageType, RDF.type, IOTPP.PackageType))
    g.add((PackageType, IOTPP.identifier, Literal(package_identifier,datatype=XSD.string)))
    g.add((PackageType, IOTPP.hasSetPoint, temperaturSetPoint))
    g.add((PackageType, IOTPP.hasSetPoint, humititySetPoint))
    g.add((PackageType, IOTPP.hasSetPoint, motionSetPoint))

    g.add((temperaturSetPoint,RDF.type, IOTPP.TemperaturSetPoint))
    g.add((temperaturSetPoint, IOTPP.value, Literal(temperaturValue, datatype=XSD.int)))
    g.add((humititySetPoint,RDF.type, IOTPP.HumititySetPoint))
    g.add((humititySetPoint, IOTPP.value, Literal(humitityValue, datatype=XSD.int)))
    g.add((motionSetPoint,RDF.type, IOTPP.MotionSetPoint))
    g.add((motionSetPoint,IOTPP.value, Literal(motionValue, datatype=XSD.int)))

def insert_device(deviceid):
    deviceId = deviceid
    Device = IOTPP['/device/'+deviceId]
    
    g.add((Device, RDF.type, IOTPP.Device))
    g.add((Device, IOTPP.deviceId,Literal(deviceId,datatype=XSD.ID)))
    
def insert_package_to_device(deviceid, packageid, packagetype_identifier):
    deviceId = deviceid
    packageId = packageid   
    package_identifier = packagetype_identifier
    
    PackageType = IOTPP['/packagetype/'+package_identifier]
    Device = IOTPP['/device/'+deviceId]
    Package = IOTPP['/package/'+packageId]

    g.add((Device, RDF.type, IOTPP.Device))
    g.add((Device, IOTPP.deviceId,Literal(deviceId,datatype=XSD.ID)))
    g.add((Device, IOTPP.hasAPackage, Package))

    g.add((Package, RDF.type, IOTPP.Package))
    g.add((Package, IOTPP.hasPackageType, PackageType))
    g.add((Package, IOTPP.packageId, Literal(packageId,datatype=XSD.ID)))

    g.add((PackageType, RDF.type, IOTPP.PackageType))
    g.add((PackageType, IOTPP.identifier, Literal(package_identifier,datatype=XSD.string)))

def get_all_deviceIds():
    ids = _query_device_Ids()
    deviceids_result = [str(ids[i][0]) for i in range(len(ids))]
    return deviceids_result

def get_package_on_device(deviceid):
    packages = _query_packages_on_deviceid(deviceid)
    packages_result = [(str(packageid),str(packagetype)) for packageid,packagetype in packages]
    return packages_result

def get_setpoints_on_packagetype(package_identifier):
    setpoints = _query_setpoints_for_packagetype(package_identifier)
    setpoints_result = [int(setpoints[i][0]) for i in range(len(setpoints))]
    return setpoints_result

def _query_device_Ids():
    q_deviceIds = '''
    SELECT DISTINCT ?deviceid
    WHERE {
        ?device         rdf:type                iotPP:Device .
        ?device         iotPP:deviceId          ?deviceid 
    }
    '''
    return query(g, q_deviceIds)

def _query_packages_on_deviceid(deviceid):
    q_package_on_device = '''
    SELECT DISTINCT ?packageid ?identifier
    WHERE {{
        ?device         rdf:type                iotPP:Device .
        ?device         iotPP:deviceId          "{}"^^xsd:ID .
        ?device         iotPP:hasAPackage       ?package .
        ?package        iotPP:packageId         ?packageid . 
        ?package        iotPP:hasPackageType    ?packagetype .
        ?packagetype    iotPP:identifier        ?identifier
    }}
    '''.format(deviceid)
    return query(g,q_package_on_device)

def _query_setpoints_for_packagetype(package_identifier):
    q_setpoints = '''
    SELECT DISTINCT ?value
    WHERE {{
        ?Package         rdf:type                iotPP:Package .
        ?package         iotPP:hasPackageType    ?packagetype .
        ?packagetype     iotPP:identifier        "{}"^^xsd:string . 
        ?packagetype     iotPP:hasSetPoint       ?setpoint .
        ?setpoint        iotPP:value             ?value  
    }} ORDER BY ?setpoint
    '''.format(package_identifier)
    return query(g,q_setpoints)


#Code for testing 
_init()

insert_device('30aea4ddc98c')
insert_device('50aefjiejf')
insert_package_to_device('30aea4ddc98c','sde445jfdivbds','box')
insert_package_to_device('30aea4ddc98c','leteerf34fere','letter')

print(get_all_deviceIds())
print(get_package_on_device('30aea4ddc98c'))
print(get_setpoints_on_packagetype('letter'))


