from rdflib import Literal

from wrapper import *

g = model()

deviceId = 'dsjidjossd'
Device = IOTPP['/device/'+deviceId]

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

eventTemperatureViolation = IOTPP['/event/temperatureViolation/1']
eventHumitityViolation = IOTPP['/event/humitityViolation/1']
eventMotionViolation = IOTPP['/event/MotionViolation/1']
event1 =IOTPP['/event/1']
eventValue1 = IOTPP['/eventvalue/1']
topic1 = IOTPP['/topic/1']

g.add((Device, RDF.type, IOTPP.Device))
g.add((Device, IOTPP.deviceId,Literal(deviceId,datatype=XSD.ID)))
g.add((Device, IOTPP.hasAPackage, Package))

g.add((Package, RDF.type, IOTPP.Package))
g.add((Package, IOTPP.hasPackageType, PackageType))
g.add((Package, IOTPP.packageId, Literal(packageId,datatype=XSD.ID)))

g.add((temperaturSetPoint,RDF.type, IOTPP.TemperaturSetPoint))
g.add((temperaturSetPoint, IOTPP.value, Literal(temperaturValue, datatype=XSD.int)))
g.add((humititySetPoint,RDF.type, IOTPP.HumititySetPoint))
g.add((humititySetPoint, IOTPP.value, Literal(humitityValue, datatype=XSD.int)))
g.add((motionSetPoint,RDF.type, IOTPP.MotionSetPoint))
g.add((motionSetPoint,IOTPP.value, Literal(motionValue, datatype=XSD.int)))

g.add((PackageType, RDF.type, IOTPP.PackageType))
g.add((PackageType, IOTPP.identifier, Literal(package_identifier,datatype=XSD.string)))
g.add((PackageType, IOTPP.hasSetPoint, temperaturSetPoint))
g.add((PackageType, IOTPP.hasSetPoint, humititySetPoint))
g.add((PackageType, IOTPP.hasSetPoint, motionSetPoint))

g.add((eventTemperatureViolation, RDF.type, IOTPP.TemperatureViolation))
g.add((eventTemperatureViolation,IOTPP.hasValue, eventValue1))
g.add((eventTemperatureViolation,IOTPP.hasPackage, Package))
g.add((eventTemperatureViolation,IOTPP.timestamp,Literal('2002-11-26T21:32:52',datatype=XSD.dateTime)))

g.add((eventHumitityViolation, RDF.type, IOTPP.HumitityViolation))
g.add((eventHumitityViolation,IOTPP.hasValue, eventValue1))
g.add((eventHumitityViolation,IOTPP.hasPackage, Package))
g.add((eventHumitityViolation,IOTPP.timestamp,Literal('2003-12-26T21:32:52',datatype=XSD.dateTime)))

g.add((eventMotionViolation, RDF.type, IOTPP.MotionViolation))
g.add((eventMotionViolation,IOTPP.hasValue, eventValue1))
g.add((eventMotionViolation,IOTPP.hasPackage, Package))
g.add((eventMotionViolation,IOTPP.timestamp,Literal('2004-12-26T21:32:52',datatype=XSD.dateTime)))

g.add((event1, RDF.type, IOTPP.Event))
g.add((event1,IOTPP.hasValue, eventValue1))
g.add((event1,IOTPP.hasPackage, Package))
g.add((event1,IOTPP.timestamp,Literal('2001-10-26T21:32:52',datatype=XSD.dateTime)))

g.add((event1, RDF.type, IOTPP.EventValue))

g.add((topic1, RDF.type, IOTPP.Topic))
g.add((topic1, IOTPP.hasEvent, event1))
g.add((topic1, IOTPP.topicName, Literal('tempTooHigh',datatype=XSD.string)))


g.serialize("ontology.ttl", 'turtle')

#Used
q_packageInfo = '''
    SELECT DISTINCT ?packageid
    WHERE {
        ?package        rdf:type                iotPP:Package .
        ?package        iotPP:packageId         ?packageid .
        ?package        iotPP:hasPackageType    ?packagetype 
    }
    '''
#Used
q_deviceInfo = '''
    SELECT DISTINCT ?deviceid
    WHERE {
        ?device         rdf:type                iotPP:Device .
        ?device         iotPP:deviceId          ?deviceid 
    }
    '''
q_packageId = '''
    SELECT DISTINCT ?packageid
    WHERE {
        ?package         rdf:type                iotPP:Package .
        ?package         iotPP:packageId         ?packageid 
    }
    '''

#Used
q_package_on_device = '''
    SELECT DISTINCT ?packageid ?packagetype
    WHERE {
        ?device         rdf:type                iotPP:Device
        ?device         iotPP:hasAPackage       ?package .
        ?package        iotPP:packageId         ?packageid .
        ?package        iotPP:hasPackageType    ?packagetype 
    }
    '''
#Used
q_Setpoint_TemperaturSetPoint = '''
    SELECT DISTINCT ?value
    WHERE {
        ?device         rdf:type              iotPP:Device .
        ?device         iotPP:hasAPackage     ?package .
        ?package        iotPP:hasPackageType  ?packagetype .
        ?setpoint       rdf:type              iotPP:TemperaturSetPoint .
        ?packagetype    iotPP:hasSetPoint     ?setpoint .
        ?setpoint       iotPP:value           ?value
    }
    '''
#Used
q_Setpoint_HumititySetPoint = '''
    SELECT DISTINCT  ?value
    WHERE {

        ?device         rdf:type              iotPP:Device .
        ?device         iotPP:hasAPackage     ?package .
        ?package        iotPP:hasPackageType  ?packagetype .        
        ?setpoint       rdf:type              iotPP:HumititySetPoint .
        ?packagetype    iotPP:hasSetPoint     ?setpoint .
        ?setpoint       iotPP:value           ?value
    }
    '''
#Used
q_Setpoint_MotionSetPoint = '''
    SELECT DISTINCT  ?value
    WHERE {
        ?device         rdf:type              iotPP:Device .
        ?device         iotPP:hasAPackage     ?package .
        ?package        iotPP:hasPackageType  ?packagetype .        
        ?setpoint       rdf:type              iotPP:MotionSetPoint .
        ?packagetype    iotPP:hasSetPoint     ?setpoint .
        ?setpoint       iotPP:value           ?value        
    }
    '''
#_____________currently not used___________________________

q_event_TemperatureViolation = '''
    SELECT DISTINCT ?package ?eventvalue ?timestamp
    WHERE {
        ?event          rdf:type           iotPP:TemperatureViolation .
        ?event          iotPP:hasPackage   ?package .
        ?event          iotPP:hasValue     ?eventvalue .
        ?event          iotPP:timestamp    ?timestamp 
    }
    ''' 
q_event_HumitityViolation = '''
    SELECT DISTINCT ?package ?eventvalue ?timestamp
    WHERE {
        ?event          rdf:type           iotPP:HumitityViolation .
        ?event          iotPP:hasPackage   ?package .
        ?event          iotPP:hasValue     ?eventvalue .
        ?event          iotPP:timestamp    ?timestamp 
    }
    ''' 

q_event_MotionViolation = '''
    SELECT DISTINCT ?package ?eventvalue ?timestamp
    WHERE {
        ?event          rdf:type           iotPP:MotionViolation .
        ?event          iotPP:hasPackage   ?package .
        ?event          iotPP:hasValue     ?eventvalue .
        ?event          iotPP:timestamp    ?timestamp 
    }
    ''' 

q_topicName = '''
    SELECT DISTINCT  ?topicname
    WHERE {
        ?topic          rdf:type            iotPP:Topic .
        ?topic          iotPP:topicName     ?topicname
    }
    '''
q_topic_event = '''
    SELECT DISTINCT  ?event
    WHERE {
        ?topic          rdf:type            iotPP:Topic .
        ?topic          iotPP:hasEvent      ?event
    }
    '''
deviceid = 'dsjidjossd'
q_package_on_device = '''
    SELECT DISTINCT ?packageid ?packagetype
    WHERE {{
        ?device         rdf:type                iotPP:Device .
        ?device         iotPP:deviceId          "{}"^^xsd:ID .
        ?device         iotPP:hasAPackage       ?package .
        ?package        iotPP:packageId         ?packageid . 
        ?package        iotPP:hasPackageType    ?packagetype 
    }}
    '''.format(deviceid)

identifier = "letter"
q_setpoints = '''
    SELECT DISTINCT ?value
    WHERE {{
        ?Package         rdf:type                iotPP:Package .
        ?package         iotPP:hasPackageType    ?packagetype .
        ?packagetype     iotPP:identifier        "{}"^^xsd:string . 
        ?packagetype     iotPP:hasSetPoint       ?setpoint .
        ?setpoint        iotPP:value             ?value  
    }}
    '''.format(identifier)

queryModel = query(g,q_topic_event)

print(query(g, q_setpoints))







