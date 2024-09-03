import requests
import pandas as pd
import json


def weather_api_request_forecast():
    try:
        r = requests.get('https://api.openweathermap.org/data/2.5/forecast?lat=53.7&lon=7.3&APPID=0bfe5ce5741894169eae4f47182af766')

        if r.status_code == 200:
            response_json = r.json()
            #print(response_json)
            forecasts = response_json['list']
            flattened_forecasts = []
            for forecast in forecasts:
                flattened_forecast = {
                    'Timestamp': forecast['dt'],
                    'Temperature': forecast['main']['temp'],
                    'Humidity': forecast['main']['humidity'],
                    'Wind_Speed': forecast['wind']['speed'],
                    'visibility': forecast['visibility']
                }
                flattened_forecasts.append(flattened_forecast)
            
            df_weather_forecast = pd.DataFrame(flattened_forecasts)
            return df_weather_forecast

        else:
            print("Error:", r.status_code)
        
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
    
print(weather_api_request_forecast())
