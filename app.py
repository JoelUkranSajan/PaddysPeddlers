from flask import Flask, render_template, url_for , jsonify, request
import json
from ML.RFModel import generate_model_and_coords, generate_model_and_coords_stands, trip_predict, trip_predict_stands


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stations")
def get_stations():
    # get_station_data_from_db("./DB/Data/stations.json");
    data = []
    with open('./Data/stations.json', 'r') as file:
       data = json.load(file)
    return data

@app.route("/weather")
def get_weather():
    # latest_weather("./DB/Data/weather.json")
    with open('./DB/Data/weather_raw.json') as file:
        data = json.load(file)
    return data

@app.route('/get_images')
def get_image_url():
    image_url = url_for('static', filename='images/pressure.jpg')
    return jsonify({'image_url': image_url})

@app.route('/getStationInfo', methods=['POST'])
def get_station():
    if request.is_json:
        try:
            data = request.get_json()
            station_number = data['stationNumber']
        except KeyError:
            return jsonify({"error": "Missing stationNumber in the request"}), 400

        try:
            bike_data = generate_model_and_coords(station_number)
            stand_data = generate_model_and_coords_stands(station_number)
            processed_data = {"bikes": bike_data, "stands": stand_data, "status": "Processed"}
            return jsonify(processed_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Request must be JSON"}), 400


@app.route('/getBikeAndStandInfo', methods=['POST'])
def upload():
    # Takes JSON data we're getting from planning a trip.
    data = request.json
    print(data)
   
    with open('request_data.json', 'w') as f:
        json.dump(data, f)
    
    # Test values to return to front end
    #available_bikes = 2
    #available_stands = 3
    
    # Think will need to call ML function here and return data to frontend.
    # Call trip predict functions here 
    # Unpack tuples.
    # Update jsonify statement to return values.
    trip_predict_bike_results = round(trip_predict(data)[0][0])
    trip_predict_stand_results = round(trip_predict_stands(data)[1][0])
    print("Predicted Values:")
    print(trip_predict_stand_results)
    print(trip_predict_bike_results)
    
    # Return message to console
    return jsonify({
        'message': 'upload() method complete.',
        'availableBikesStart': trip_predict_bike_results,
        'availableStandsEnd': trip_predict_stand_results
    })
    

if __name__ == "__main__":
    app.run(debug=True);


    