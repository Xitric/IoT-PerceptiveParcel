from rdflib import Literal

from wrapper import *

g = model()

Package = IOTPP['/package/1']
temperaturSetPoint = IOTPP['/setpoint/temperaturSetPoint/1']
humititySetPoint = IOTPP['/setpoint/humititySetPoint/1']
motionSetPoint = IOTPP['/setpoint/motionSetPoint/1']

eventTemperatureViolation = IOTPP['/event/temperatureViolation/1']
eventHumitityViolation = IOTPP['/event/humitityViolation/1']
eventMotionViolation = IOTPP['/event/MotionViolation/1']
event1 =IOTPP['/event/1']
eventValue1 = IOTPP['/eventvalue/1']
topic1 = IOTPP['/topic/1']


g.add((Package, RDF.type, IOTPP.Package))
g.add((Package, IOTPP.hasSetPoint, temperaturSetPoint))
g.add((Package, IOTPP.hasSetPoint, humititySetPoint))
g.add((Package, IOTPP.hasSetPoint, motionSetPoint))
g.add((Package, IOTPP.packageId, Literal('ab3dm23jhl43bfj',datatype=XSD.ID)))

g.add((temperaturSetPoint,RDF.type, IOTPP.TemperaturSetPoint))
g.add((humititySetPoint,RDF.type, IOTPP.HumititySetPoint))
g.add((motionSetPoint,RDF.type, IOTPP.MotionSetPoint))

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

q_packageid = '''
    SELECT DISTINCT ?packageid 
    WHERE {
        ?package        rdf:type           iotPP:Package .
        ?package        iotPP:packageId    ?packageid
    }
    '''

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

q_Setpoint_TemperaturSetPoint = '''
    SELECT DISTINCT ?setpoint
    WHERE {
        ?package        rdf:type            iotPP:Package .
        ?setpoint       rdf:type            iotPP:TemperaturSetPoint .
        ?package        iotPP:hasSetPoint   ?setpoint 
    }
    '''

q_Setpoint_HumititySetPoint = '''
    SELECT DISTINCT  ?setpoint
    WHERE {
        ?package        rdf:type            iotPP:Package .
        ?setpoint       rdf:type            iotPP:HumititySetPoint .
        ?package        iotPP:hasSetPoint   ?setpoint
    }
    '''

q_Setpoint_MotionSetPoint = '''
    SELECT DISTINCT  ?setpoint
    WHERE {
        ?package        rdf:type            iotPP:Package .
        ?setpoint       rdf:type            iotPP:MotionSetPoint .
        ?package        iotPP:hasSetPoint   ?setpoint
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

print(query(g, q_topic_event))







