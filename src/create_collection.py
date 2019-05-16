import urllib.request
from bs4 import BeautifulSoup
import csv
from time import sleep
import pandas as pd
import json
import urllib.request
import os
from PIL import Image
import json
import yaml
import glob

result = {}

f = open("config.yml", "r+")
config = yaml.load(f)


manifests = []

collection = {
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": config["prefix"]+"/data/collection.json",
    "@type": "sc:Collection",
    "vhint": "use-thumb",
    "label": config["title"],
    "manifests": manifests
}

files = glob.glob("../"+config["manifest_path"]+'/**/*.json', recursive=True)

files.sort()

for file in files:
    f = open(file, 'r')
    json_dict = json.load(f)

    m = {
        "@id": json_dict["@id"],
        "@type": "sc:Manifest",
        "label": json_dict["label"],
        "description": json_dict["description"],
        "thumbnail": json_dict["thumbnail"]
    }
    manifests.append(m)

f1 = open("../"+config["dump_path"]+"/collection.json", 'w')
json.dump(collection, f1, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
