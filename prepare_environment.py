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

r = requests.delete(ip+"/_template/logging_template")
if (r.status_code > 300):
    print "delete status is %s, reason is %s" % (r.status_code, r.reason)

r = requests.put(ip+"/_template/logging_template", data=content)
if (r.status_code > 300):
    print "status is %s, reason is %s" % (r.status_code, r.reason)
else:
    print "  -> OK"
infile.close()


print "Create userbase template"
r = requests.delete(ip+"/_template/userbase_template")
if (r.status_code > 300):
    print "delete status is %s, reason is %s" % (r.status_code, r.reason)

infile = open("template_userbase.json", "r")
content = json.dumps(json.loads(infile.read()))
r = requests.put(ip+"/_template/userbase_template", data=content)
if (r.status_code > 300):
    print "status is %s, reason is %s" % (r.status_code, r.reason)
else:
    print "  -> OK"

infile.close()

print "Create offerdata template"
r = requests.delete(ip+"/_template/offerdata_userbase")
if (r.status_code > 300):
    print "delete status is %s, reason is %s" % (r.status_code, r.reason)

infile = open("template_offerdata.json", "r")
content = json.dumps(json.loads(infile.read()))
r = requests.put(ip+"/_template/offerdata_userbase", data=content)
if (r.status_code > 300):
    print "status is %s, reason is %s" % (r.status_code, r.reason)
else:
    print "  -> OK"

infile.close()
