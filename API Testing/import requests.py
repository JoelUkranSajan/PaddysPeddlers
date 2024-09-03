import requests
import json

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