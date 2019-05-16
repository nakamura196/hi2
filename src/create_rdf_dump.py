import urllib.request
from bs4 import BeautifulSoup
import csv
from time import sleep
import pandas as pd
import json
import urllib.request
import os
from PIL import Image
from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace
import yaml

f = open("config.yml", "r+")
config = yaml.load(f)

df = pd.read_excel("../"+config["metadata_path"],
                   sheet_name=0, header=None, index_col=None)

r_count = len(df.index)
c_count = len(df.columns)

map = {}

g = Graph()

for i in range(1, c_count):
    label = df.iloc[0, i]
    uri = df.iloc[1, i]
    type = df.iloc[2, i]

    if not pd.isnull(type):
        obj = {}
        map[i] = obj
        obj["label"] = label
        obj["uri"] = uri
        obj["type"] = type

for j in range(3, r_count):
    subject = df.iloc[j, 0]
    subject = URIRef(subject)
    for i in map:
        value = df.iloc[j, i]

        if not pd.isnull(value) and value != 0:

            obj = map[i]
            p = URIRef(obj["uri"])

            if obj["type"].upper() == "RESOURCE":
                g.add((subject, p, URIRef(value)))
            else:
                tmp = value.split("@")
                if len(tmp) == 2:
                    value = tmp[0]
                    lang = tmp[1]
                    g.add((subject, p, Literal(value,  lang=lang)))
                else:
                    g.add((subject, p, Literal(value)))

g.serialize(format='json-ld', destination="../"+config["dump_path"]+"/data.json", )
