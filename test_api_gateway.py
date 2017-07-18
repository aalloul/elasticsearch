#!/usr/bin/env python
from requests import post
from json import dumps

body = [{"sessID": "1492719093000","activity_start": "1492719093000","class_name": "postUsage","stack_trace": "postUsageRequestError","time": "1492531797401","method_name": "postUsage"},{"stack_trace": "postUsageRequestError","class_name": "postUsage","time": "1492531567560","method_name": "postUsage"}]


headers = {'Content-Type': 'application/json'}
headers['deviceType'] = "test_device_type_lambda_1"
headers["deviceID"] = "test_device_id_lambda_1"
headers["networkRequestTime"] = "1492796228000"
headers["x-api-key"] = "vmXvcob4V33NpNVXKsDll8nAQAcmHGZZ87Fl4HF6"

url = "https://2ewwhcff9d.execute-api.eu-west-1.amazonaws.com/production/shippy-logging"
res = post(url, data=dumps(body),headers=headers)
print(res.json())
