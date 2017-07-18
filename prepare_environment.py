#!/usr/bin/env python

from elasticsearch import Elasticsearch, helpers, RequestsHttpConnection, client
from json import loads, dumps
from requests_aws4auth import AWS4Auth

##########
# Cluster settings

ip = "https://search-shippy-es-f5eynamiumiunz5mrdxxmodksu.eu-west-1.es.amazonaws.com"
theport = 80
ACCESS_KEY = "AKIAIAOZRRLDX37HKW4Q"
SECRET_KEY = "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"
REGION = "eu-west-1"
host = 'search-shippy-es-f5eynamiumiunz5mrdxxmodksu.eu-west-1.es.amazonaws.com'
awsauth = AWS4Auth(ACCESS_KEY, SECRET_KEY, REGION, 'es')
#########

# Establish the connection
es = Elasticsearch(
    hosts=[{'host': host, 'port': theport}],
    http_auth=awsauth,
    connection_class=RequestsHttpConnection
)

index_client = client.IndicesClient(es)
print ("Create logging template")

print ("1- Logging data template")
with open("logging_template.json","r") as infile:
    content = loads(infile.read())
    res = index_client.put_template(name = "logging-template", body = content)
    print (res)

print ("1- Offer data template")
with open("template_offerdata.json", "r") as infile:
    content = loads(infile.read())
    res = index_client.put_template(name = "offer-template", body = content)
    print (res)

infile.close()

print (" Done ")
