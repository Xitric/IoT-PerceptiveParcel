from rdflib import Literal
from repository.wrapper import model, query, IOTPP, RDF, XSD

g = model()

def _init():
    insert_package_type('letter', 70, 10000, 40)
    insert_package_type('clothing', 65, 20000, 40)
    insert_package_type('glass', 80, 1000, 550)
    insert_package_type('ceramics', 80, 2500, 600)
    insert_package_type('electronics', 30, 8000, 45)
    insert_package_type('food', 40, 3000, 5)
    insert_package_type('animal', 80, 10000, 30)
    insert_package_type('polar-animal', 80, 10000, 0)

    insert_device('30aea4ddc98c')  # Kasper
    insert_device('30aea4dd02a8')  # Emil
    g.serialize("repository/model.ttl", 'turtle')

def insert_package_type(package_type, humidity_value, motion_value, temperature_value):
    PackageType = IOTPP['/packagetype/'+package_type]

    humiditySetPoint = IOTPP[package_type+'/humidity']
    motionSetPoint = IOTPP[package_type+'/motion']
    temperatureSetPoint = IOTPP[package_type+'/temperature']

    g.add((PackageType, RDF.type, IOTPP.PackageType))
    g.add((PackageType, IOTPP.identifier, Literal(package_type,datatype=XSD.string)))
    g.add((PackageType, IOTPP.hasSetPoint, humiditySetPoint))
    g.add((PackageType, IOTPP.hasSetPoint, motionSetPoint))
    g.add((PackageType, IOTPP.hasSetPoint, temperatureSetPoint))

    g.add((humiditySetPoint,RDF.type, IOTPP.HumiditySetPoint))
    g.add((humiditySetPoint, IOTPP.value, Literal(humidity_value, datatype=XSD.int)))
    g.add((motionSetPoint,RDF.type, IOTPP.MotionSetPoint))
    g.add((motionSetPoint,IOTPP.value, Literal(motion_value, datatype=XSD.int)))
    g.add((temperatureSetPoint,RDF.type, IOTPP.TemperatureSetPoint))
    g.add((temperatureSetPoint, IOTPP.value, Literal(temperature_value, datatype=XSD.int)))

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

def get_package_types():
    package_types = _query_package_types()
    return [str(package_types[i][0]) for i in range(len(package_types))]

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

def _query_package_types():
    q_package_types = '''
    SELECT DISTINCT ?identifier
    WHERE {
        ?packagetype    rdf:type                iotPP:PackageType .
        ?packagetype    iotPP:identifier        ?identifier
    } ORDER BY ?identifier
    '''
    return query(g,q_package_types)

_init()
