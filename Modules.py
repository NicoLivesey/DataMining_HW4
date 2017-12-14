import json

json_data = open("reduced_dblp.json").read()

data = json.loads(json_data)
print(data[0])