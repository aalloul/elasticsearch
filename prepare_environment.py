#!/usr/bin/env python
import requests
import json

##########
# Cluster settings

ip = "http://192.168.178.206:9200"

#########

print "Create logging template"
infile = open("logging_template.json","r")
content = json.dumps(json.loads(infile.read()))
r = requests.put(ip+"/_template/logging_template", data=content)
if (r.status_code > 300):
    print "status is %s, reason is %s" % (r.status_code, r.reason)
else:
    print "  -> OK"
infile.close()

print "Create userbase template"
infile = open("userbase_template.json", "r")
content = json.dumps(json.loads(infile.read()))
r = requests.put(ip+"/_template/userbase_template", data=content)
if (r.status_code > 300):
    print "status is %s, reason is %s" % (r.status_code, r.reason)
else:
    print "  -> OK"

infile.close()
