# This code is used to load turtle data files from folders (listed in the folders list) into Jena for local testing.
# For the IoW housing data, this may take a while as they're lots of little files

import os
import requests

jena_host = "http://localhost:3030"
dataset = "knowledge"
path = "data?default"
jena_update = jena_host + "/" + dataset + "/" + path

folders = ["address-epcs", "uprn-latlon-toids"]

for folder in folders:
    directory = os.fsencode(folder)

    for file in os.listdir(directory):
        filename = os.path.join(folder, os.fsdecode(file))
        if filename.endswith(".ttl"):
            with open(filename) as f:
                data = f.read()
                headers = {"Content-Type": "text/turtle;charset=utf-8"}
                r = requests.post(jena_update, data=data, headers=headers)
                print(filename)
