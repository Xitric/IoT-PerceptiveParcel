from rdflib import Graph, Namespace

# Standard namespaces that we can refer to
# See: https://www.w3.org/TR/rdf-schema/
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')

# See: https://www.w3.org/TR/2004/REC-owl-guide-20040210/
OWL = Namespace('http://www.w3.org/2002/07/owl#')

# See: https://brickschema.org/ontology
BRICK = Namespace('https://brickschema.org/schema/1.0.3/Brick#')
FRAME = Namespace('https://brickschema.org/schema/1.0.3/BrickFrame#')

IOTPP = Namespace('https://github.com/Xitric/IoT-PerceptiveParcel#')
XSD = Namespace('http://www.w3.org/2001/XMLSchema#')

def model():
    g = Graph()

    # Read file describing our data types and relationships for build information
    g.parse('PackageSchema.ttl', format='turtle')

    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)
    g.bind('owl', OWL)
    g.bind('brick', BRICK)
    g.bind('iotpp', IOTPP)
    g.bind('xsd', XSD)
    g.bind('frame', FRAME)

    return g


def query(g, q):
    r = g.query(q)
    return list(map(lambda row: list(row), r))