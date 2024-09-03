import requests
import json

data = requests.get('https://api.openweathermap.org/data/2.5/weather?q=Dublin,uk&APPID=0bfe5ce5741894169eae4f47182af766')
response_json = data.json()  

Weather = open('Weather.json', 'w')
json.dump(response_json, Weather, indent=4)
       
print(Weather)