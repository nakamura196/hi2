import yaml
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

result = {}

f = open("config.yml", "r+")
config = yaml.load(f)

image_map = {}

df = pd.read_excel("../"+config["image_path"], sheet_name=0, header=None, index_col=None)

r_count = len(df.index)
c_count = len(df.columns)

for j in range(1, r_count):
    id = df.iloc[j, 0]
    url = df.iloc[j, 1]
    thumbnail = df.iloc[j, 2]
    if id not in image_map:
        image_map[id] = []
    image_map[id].append(
        {
            "original": url,
            "thumbnail": thumbnail
        }
    )

df = pd.read_excel("../"+config["metadata_path"], sheet_name=0,
                   header=None, index_col=None)

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

    print(str(j+1)+"/"+str(r_count)+"="+subject)

    obj2 = {}
    for i in map:
        value = df.iloc[j, i]
        field = map[i]["uri"]
        if field not in obj2:
            obj2[field] = []
        obj2[field].append(value)

    manifest_id = subject.split("/")[-2]

    dir = "../"+config["manifest_path"]+"/manifest/"+manifest_id
    os.makedirs(dir, exist_ok=True)

    file = dir+"/manifest.json"

    obj = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@type": "sc:Manifest",
        "sequences": [
            {
                "@type": "sc:Sequence",
                "label": "Current Page Order",
                "viewingHint": "non-paged",
                "canvases": []
            }
        ]
    }

    if "http://iiif.io/api/presentation/2#viewingDirection" in obj2:
        value = obj2["http://iiif.io/api/presentation/2#viewingDirection"][0]
        if value == "http://iiif.io/api/presentation/2#rightToLeftDirection":
            obj["viewingDirection"] = "right-to-left"

    if "http://purl.org/dc/terms/title" in obj2:
        obj["label"] = obj2["http://purl.org/dc/terms/title"][0].split("@")[0]

    if "http://purl.org/dc/terms/description" in obj2:
        obj["description"] = obj2["http://purl.org/dc/terms/description"][0]

    obj["@id"] = subject

    obj["metadata"] = []

    for i in map:
        value = df.iloc[j, i]

        if not pd.isnull(value) and value != 0:

            field = map[i]["uri"]

            if field in config["fields"]:
                obj["metadata"].append({
                    "label": map[i]["label"],
                    "value": value
                })

    prefix = obj["@id"].replace("/manifest.json", "")

    obj["sequences"][0]["@id"] = prefix+"/sequence/normal"

    canvases = obj["sequences"][0]["canvases"]

    if subject in image_map:
        images = image_map[subject]

        width = -1
        height = -1

        for i in range(len(images)):
            img2 = images[i]
            tmp = {
                "@type": "sc:Canvas",
                "thumbnail": {},
                "images": [
                    {
                        "@type": "oa:Annotation",
                        "motivation": "sc:painting",
                        "resource": {
                            "@type": "dctypes:Image",
                            "format": "image/jpeg",
                        }
                    }
                ]
            }
            tmp["@id"] = prefix+"/canvas/p"+str(i+1)
            tmp["label"] = "["+str(i+1)+"]"

            tmp["thumbnail"]["@id"] = img2["thumbnail"]#img_url.replace(".jpg", "_r25.jpg")

            if i == 0:
                obj["thumbnail"] = tmp["thumbnail"]["@id"]
                img = Image.open(urllib.request.urlopen(img2["original"]))
                width, height = img.size

            tmp["images"][0]["resource"]["width"] = width
            tmp["images"][0]["resource"]["height"] = height

            tmp["width"] = width
            tmp["height"] = height

            tmp["images"][0]["@id"] = prefix + \
                "/annotation/p"+str(i+1)+"-image"

            tmp["images"][0]["resource"]["@id"] = img2["original"]

            tmp["images"][0]["on"] = tmp["@id"]

            canvases.append(tmp)

    f2 = open(file, 'w')
    json.dump(obj, f2, ensure_ascii=False, indent=4,
                sort_keys=True, separators=(',', ': '))
