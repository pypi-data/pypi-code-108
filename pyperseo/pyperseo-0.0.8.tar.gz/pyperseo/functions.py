
from rdflib import Graph, URIRef, Literal, XSD
from os import listdir
from os.path import isfile, join
from datetime import datetime
import pandas as pd
import sys
import re


def get_files(path,format):
    """
    Obtain all files from current directory with certain format
    """
    files = [f for f in listdir(path) if isfile(join(path, f))]
    format_files = [ff for ff in files if ff.endswith(str("." + format))]
    if len(format_files) == 0:
        print("No resources are present at {} path with .{} format.".format(path,format))
    else:
        return format_files


def nt2ttl(path_file):
    """
    Data transformation from .nt file to .ttl
    """

    g = Graph()
    g.parse(str(path_file), format="turtle")

    g.namespace_manager.bind('this', URIRef("http://example.org/data/"))
    g.namespace_manager.bind('sio', URIRef("http://semanticscience.org/resource/"))
    g.namespace_manager.bind('obo', URIRef("http://purl.obolibrary.org/obo/"))
    #all_ns = [n for n in g.namespace_manager.namespaces()]
    #print(all_ns)

    splited = path_file.split(sep=".")
    filename = splited[0]
    ttl_path_file = filename + "." + "ttl"

    g.serialize(destination = str(ttl_path_file), format="turtle")


def milisec():
    """
    Creates a milisecond timestamp.
    """
    now = datetime.now()
    now = now.strftime('%Y%m%d%H%M%S%f')
    return now


def uniqid(path_file):
    """
    Creates unique identifier column based on milisecond timestamp.
    """
    data = pd.read_csv(path_file)

    data['uniqid'] = ""
    for i in data.index:
        data.at[i, "uniqid"] = milisec()

    print(data['uniqid'])
    data.to_csv(path_file, sep="," , index=False)


def triplipy(s,p,o,g):

    """
    RDFlib custom triplets serializer

    Test:

    from rdflib import Graph,URIRef, Literal,Namespace
    import sys
    import re

    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    trial = URIRef("https://github.com/pabloalarconm/PERSEO")

    g = Graph()

    triplipy(trial,rdfs.label,"This is a label",g)
    g.serialize(format='turtle')
    """
    
    #Subject:
    s.strip()
    ss=s.split()
    m_http=re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',s)
    #Check if its a rdflib object:
    if str(type(s))== "<class 'rdflib.term.URIRef'>":
        pass
    #Check if its a URI or a Multiple words string:
    elif len(ss) == 1 and m_http:
        s=URIRef(str(s))
    elif len(ss) >1 and m_http:
        sys.exit("Multiple word string cant be a Subject")
    else:
        sys.exit("Not matchable Subject")
        
    #Predicate:
    p.strip()
    pp=p.split()
    m_http=re.match('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',p)
    #Check if its a rdflib object:
    if str(type(p))== "<class 'rdflib.term.URIRef'>":
        pass
    #Check if its a URI or a Multiple words string:
    elif len(pp) == 1 and m_http:
        p=URIRef(str(p))
    elif len(pp) >1 and m_http:
        sys.exit("Multiple word string cant be a Predicate")
    else:
        sys.exit("Not matchable Predicate")
        
        
    #Object:
    m_http=re.match('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',o)
    m_date=re.match(r"[\d]{1,2}-[\d]{1,2}-[\d]{2}",o)
    m_float=re.match(r"[-+]?\d*\.\d+|\d+",o)
    m_init=re.match(r"[+-]?[0-9]+$",o)
    oo=o.split()
    #Check if its a rdflib object:
    if str(type(o))=="<class 'rdflib.term.URIRef'>":
        pass
    #Check if its a URI or a Multiple words string:
    elif len(oo) == 1 and m_http:
        o= URIRef(str(o))
    elif len(oo) > 1 and m_http:
        o = Literal(str(o),lang='en')
    elif m_date:
        o = Literal(str(o),datatype=XSD.date)
    elif m_float:
        o = Literal(str(o),datatype=XSD.float)
    elif m_init:
        o = Literal(str(o),datatype=XSD.init)
    else:
        o = Literal(str(o),lang='en')
        
    g.add([s,p,o])



