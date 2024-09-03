#THIS SCRIPT IS AN ATTEMPT TO INTEGRATE THE SCRAPER AND DATABASE MODIFIER SCRIPTS

import requests
import json
from sqlalchemy.orm import sessionmaker
from database_creation import Station, Availability, Weather, engine
from database_access import json_to_list, extract_stations, extract_availability, extract_weather, latest_availability_data

def JCD_API_REQ():

    try:
        r = requests.get('https://api.jcdecaux.com/vls/v1/stations?contract=Dublin&apiKey=283268b098299ec2e15661dbd2854f9bc4691238')

        # Check if the request was successful (status code 200)
        if r.status_code == 200:
            response_json = r.json()
            print(response_json)
            result = open('result.json', 'w')
            json.dump(response_json, result, indent=4)
            result.close()
        else:
            print("Error:", r.status_code)
            
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)


def weather_api_request():
    try:
        r = requests.get('https://api.openweathermap.org/data/2.5/weather?q=London,uk&APPID=0bfe5ce5741894169eae4f47182af766')

        # Check if the request was successful (status code 200)
        if r.status_code == 200:
            response_json = r.json()
            print(response_json)
            result = open('Weather.json', 'w')
            json.dump(response_json, result, indent=4)
            result.close()
        else:
            print("Error:", r.status_code)
        
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
    
    
JCD_API_REQ()
data_list = json_to_list("result.json")
extract_availability(data_list)
extract_stations(data_list)

weather_api_request()
extract_weather("Weather.json")
latest_availability_data()

