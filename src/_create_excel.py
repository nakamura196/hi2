import urllib.request
from bs4 import BeautifulSoup
import csv
from time import sleep
import pandas as pd
import json
import urllib.request
import os
from PIL import Image

ex = []
result = []
result.append(["Title", "Description", "Link"])

with open('data/data_all.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # ヘッダーを読み飛ばしたい時

    for row in reader:

        # print(row)

        title1 = row[0]
        id1 = row[1]

        title2 = row[2]
        id2 = row[3]

        no = row[4]
        desc = row[5]

        manifest = "https://nakamura196.github.io/hi/data/" + \
            str(id1)+"/"+str(id2)+"/"+str(no).zfill(4) + ".json"

        if manifest in ex:
            continue
        
        ex.append(manifest)

        url = "http://da.dl.itc.u-tokyo.ac.jp/uv/?manifest="+manifest

        result.append([title1+"・"+title2+"・"+no, desc, url])

df = pd.DataFrame(result)

df.to_excel("../docs/data/metadata.xlsx", index=False, header=False)
