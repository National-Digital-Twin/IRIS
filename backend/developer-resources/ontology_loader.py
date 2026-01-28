import requests

TURTLE_CONTENT_TYPE = "text/turtle;charset=utf-8"
ONTOLOGY_URL = "http://localhost:3030/ontology/data?default"

with open("ies4.ttl") as file:
    data = file.read()
    headers = {"Content-Type": TURTLE_CONTENT_TYPE}
    r = requests.post(
        ONTOLOGY_URL, data=data, headers=headers
    )
print("IES loaded")

with open("iesExtensions.ttl") as file:
    data = file.read()
    headers = {"Content-Type": TURTLE_CONTENT_TYPE}
    r = requests.post(
        ONTOLOGY_URL, data=data, headers=headers
    )
print("IES Extensions loaded")

with open("ndt_retrofit_buildings_extensions.ttl") as file:
    data = file.read()
    headers = {"Content-Type": TURTLE_CONTENT_TYPE}
    r = requests.post(
        ONTOLOGY_URL, data=data, headers=headers
    )
print("NDT ontology Extensions loaded")
