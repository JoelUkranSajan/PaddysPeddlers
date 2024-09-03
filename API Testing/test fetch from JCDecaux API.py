import requests
import json
r = requests.get('https://api.jcdecaux.com/vls/v1/stations?contract=Dublin&apiKey=283268b098299ec2e15661dbd2854f9bc4691238')
response_json = r.json()
#print(response_json)

result = open('result.json', 'w')

json.dump(response_json, result, indent=4)
# '''
# station_dict = {station["number"]: station for station in response_json}

# result.close()

# #response_dict = json.loads(response_json)

# #print(response_json)
# print(station_dict)

# dict = json.load(response_json)

# print(type(response_json))
# '''
# #print(dict)



