#THIS SCRIPT IS AN ATTEMPT TO INTEGRATE THE SCRAPER AND DATABASE MODIFIER SCRIPTS
import requests
import json
import time
from DatabaseAccess import update_availability_to_db, update_stations_to_db, update_weather_to_db, get_station_data_from_db, latest_weather
from Common.common import json_to_list
import os

# Added to allow script to find required files in Data folder.
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

Bike_API_Key = "283268b098299ec2e15661dbd2854f9bc4691238"
Weather_API_Key = "0bfe5ce5741894169eae4f47182af766"

Bike_API_Link = "https://api.jcdecaux.com/vls/v1/stations?contract=Dublin&apiKey=" + Bike_API_Key
Weather_API_Link = "https://api.openweathermap.org/data/2.5/weather?lat=53.344603&lon=-6.263371&appid=" + Weather_API_Key +"&units=metric"

Bike_Json_File = "./Data/stations_raw.json"
Weather_Json_File = "./Data/weather_raw.json"

Final_Station_Json_File = "./DB/Data/stations.json"
Final_Weather_Json_File = "./DB/Data/weather.json"

def get_bike_station_info():

    try:
        response = requests.get(Bike_API_Link)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            response_json = response.json()
            result = open(Bike_Json_File, 'w')
            json.dump(response_json, result, indent=4)
            result.close()
        else:
            print("Error:", response.status_code)
            
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)


def get_weather_info():
    try:
        response = requests.get(Weather_API_Link)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            response_json = response.json()
            print(response_json)
            result = open(Weather_Json_File, 'w')
            json.dump(response_json, result, indent=4)
            result.close()
        else:
            print("Error:", response.status_code)
        
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
    

scraper_time_stamp = int(time.time())
print(scraper_time_stamp)
get_bike_station_info()
data_list = json_to_list(Bike_Json_File)
update_stations_to_db(data_list)
update_availability_to_db(data_list, scraper_time_stamp)

get_weather_info()
update_weather_to_db(Weather_Json_File, scraper_time_stamp)
get_station_data_from_db(Final_Station_Json_File)
latest_weather(Final_Weather_Json_File)

