import json


with open("data.json") as json_file:
    json_data = json.load(json_file)

for key, value in json_data.iteritems():
    print key, value

json_data['saurabh'] = 1231214132412343
print json_data['saurabh']