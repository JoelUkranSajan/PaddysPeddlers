import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import json
import csv
import datetime
import matplotlib.pyplot as plt
import os
import time
import sys
from scipy.interpolate import make_interp_spline, BSpline
import numpy as np
import pickle
from ML.weather_forecast_api_test import weather_api_request_forecast
pd.set_option('display.max_colwidth', None)
current_directory = os.getcwd()
print('Current directory is:' + current_directory)


####    IMPORT AND TRAIN    ####

def epoch_to_localtime(epoch):
    return datetime.datetime.fromtimestamp(int(epoch))

pickle_all_models = True

def data_clean_and_separation():
    df = pd.read_csv('ML/ML_Raw_Input.csv')
    Selected_Columns = df[['number', 'scrape_time', 'temperature', 'humidity', 'visibility', 'windspeed', 'available_bikes', 'available_bike_stands']].copy()

    Selected_Columns['scrape_time'] = Selected_Columns['scrape_time'].apply(epoch_to_localtime)
    Selected_Columns['month'] = Selected_Columns['scrape_time'].dt.month
    Selected_Columns['hour'] = Selected_Columns['scrape_time'].dt.strftime('%H').astype(float)
    Selected_Columns['day_of_week'] = Selected_Columns['scrape_time'].dt.weekday
    Selected_Columns = Selected_Columns.drop(['scrape_time'], axis = 1)
    Station_numbers = Selected_Columns['number'].unique()
    Stations_ML_Dict = {}
    for Station_number in Station_numbers:
        filter_cond = (Selected_Columns['number']==Station_number)
        Station_specific_rows = Selected_Columns.loc[filter_cond]
        Stations_ML_Dict[Station_number] = Station_specific_rows
        print('Seperated data for station:' + str(Station_number))

    return Stations_ML_Dict

models_dict = {}

def create_models():
    models_dict = {}
    Stations_ML_Dict = data_clean_and_separation()
    for i in range(1, len(Stations_ML_Dict)+1):

        StationData = Stations_ML_Dict.get(i)
        
        try:
            X = StationData[['month', 'hour', 'day_of_week', 'windspeed', 'temperature', 'humidity', 'visibility']]
            Y = StationData['available_bikes']
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
            rf_model = RandomForestRegressor(n_estimators=5, random_state=42)
            rf_model.fit(X_train, Y_train)
            Y_pred = rf_model.predict(X_test)
            models_dict[i] = rf_model
            mse = mean_squared_error(Y_test, Y_pred)
            print('Mean Squared Error:', mse, f'\033[1mStation: {i}\033[0m')

        except Exception as e:
            print("\033[91m", 'Error processing station ', i, ': ', e,  "\033[0m")

        if pickle_all_models:
            modelPickler(models_dict)


def create_models_stands():
    models_dict = {}
    Stations_ML_Dict = data_clean_and_separation()
    for i in range(1, len(Stations_ML_Dict)+1):

        StationData = Stations_ML_Dict.get(i)
        
        try:
            X = StationData[['month', 'hour', 'day_of_week', 'windspeed', 'temperature', 'humidity', 'visibility']]
            Y = StationData['available_bike_stands']
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
            rf_model = RandomForestRegressor(n_estimators=5, random_state=42)
            rf_model.fit(X_train, Y_train)
            Y_pred = rf_model.predict(X_test)
            models_dict[i] = rf_model
            mse = mean_squared_error(Y_test, Y_pred)
            print('Mean Squared Error:', mse, f'\033[1mStation: {i}\033[0m')

        except Exception as e:
            print("\033[91m", 'Error processing station ', i, ': ', e,  "\033[0m")

        if pickle_all_models:
            modelPickler_stands(models_dict)


def modelPickler(models_dict):
    for i in range(1, len(models_dict)+1):
        try:
            print('It\'s Picklin\' Time')
            rf_model = models_dict[i]
            modelFileName = 'ML/rf_model'+ str(i) +'.pkl'
            with open(modelFileName, 'wb') as handle:
                pickle.dump(rf_model, handle, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
                print("\033[91m", 'Error pickling', i, ': ', e,  "\033[0m")

def modelPickler_stands(models_dict):
    for i in range(1, len(models_dict)+1):
        try:
            print('It\'s Picklin\' Time')
            rf_model = models_dict[i]
            modelFileName = 'ML/rf_model_stands'+ str(i) +'.pkl'
            with open(modelFileName, 'wb') as handle:
                pickle.dump(rf_model, handle, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
                print("\033[91m", 'Error pickling', i, ': ', e,  "\033[0m")

####    PREDICT    ####

def data_clean_for_predict(stationNumber, weatherForecast):

    predictionDataframe = pd.DataFrame()
    predictionDataframe['number'] = [stationNumber] * len(weatherForecast['Timestamp'])
    predictionDataframe['scrape_time'] = weatherForecast['Timestamp']
    predictionDataframe['temperature'] = (weatherForecast['Temperature']) - 273.15 #Conversion to Celsius
    predictionDataframe['humidity'] = weatherForecast['Humidity']
    predictionDataframe['visibility'] = weatherForecast['visibility']
    predictionDataframe['windspeed'] = weatherForecast['Wind_Speed']
    Selected_ColumnsPred = predictionDataframe[['number', 'scrape_time', 'temperature', 'humidity', 'visibility', 'windspeed']].copy()
    Selected_ColumnsPred['scrape_time'] = Selected_ColumnsPred['scrape_time'].apply(epoch_to_localtime)
    Selected_ColumnsPred['month'] = Selected_ColumnsPred['scrape_time'].dt.month
    Selected_ColumnsPred['hour'] = Selected_ColumnsPred['scrape_time'].dt.strftime('%H').astype(float)
    Selected_ColumnsPred['day_of_week'] = Selected_ColumnsPred['scrape_time'].dt.weekday
    Selected_ColumnsPred = Selected_ColumnsPred.drop(['scrape_time'], axis = 1)
    Selected_ColumnsPred = Selected_ColumnsPred.drop(['number'], axis = 1)

    return Selected_ColumnsPred




forecastInterval = 60*0.25
def predict(stationNumber):

    weatherForecast = weather_api_request_forecast()
    currentTime = time.time()
    data_clean_for_predict(stationNumber, weatherForecast)
    Yout = models_dict[stationNumber].predict(Selected_ColumnsPred[['month', 'hour', 'day_of_week', 'windspeed', 'temperature', 'humidity', 'visibility']])
    return Yout



###     SINGLE MODEL PREDICT     ###

def predict_with_single_model(model, stationNumber):

    weatherForecast = weather_api_request_forecast()
    currentTime = time.time()
    Selected_ColumnsPred = data_clean_for_predict(stationNumber, weatherForecast)
    Yout = model.predict(Selected_ColumnsPred[['month', 'hour', 'day_of_week', 'windspeed', 'temperature', 'humidity', 'visibility']])
    return Yout


def predict_with_single_model_high_hours_res(model, stationNumber):

    weatherForecast = weather_api_request_forecast()
    currentTime = time.time()
    Selected_ColumnsPred = data_clean_for_predict(stationNumber, weatherForecast)
    duplicated_rows = []
    repeated_df = pd.DataFrame()

    for index, row in Selected_ColumnsPred.iterrows():
        duplicated_rows.extend([row] * 11)
        repeated_df = pd.concat([repeated_df, pd.DataFrame([row] * 11)], ignore_index=True)

    df_copy = repeated_df.copy()
    df_copy['hour'] = pd.to_numeric(df_copy['hour'])
    distance_from_last_multiple_of_12 = (df_copy.index % 12)[0:len(df_copy.index)]
    minutes_to_add = (distance_from_last_multiple_of_12)*(0.25)

    for i in range(len(df_copy)):
    
        if i % 12 != 0:
            df_copy.at[i, 'hour'] += minutes_to_add[i]

    Yout = model.predict(df_copy[['month', 'hour', 'day_of_week', 'windspeed', 'temperature', 'humidity', 'visibility']])
    return Yout






###     SINGLE MODEL CREATION ON STNUM INPUT     ###

def model_creation_single(stationNumber):
    for Station in Stations_ML_Dict.keys():
        if Station == stationNumber:
            try:
                StationData = Stations_ML_Dict[Station]
                X = StationData[['month', 'hour', 'day_of_week', 'windspeed', 'temperature', 'humidity', 'visibility']]
                Y = StationData[['available_bikes']]
                X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
                rf_model = RandomForestRegressor(n_estimators=5, random_state=42)
                rf_model.fit(X_train, Y_train)
                print("Model created successfully for station:", stationNumber)
                return rf_model
                
            except Exception as e:
                print("\033[91m", 'Error processing station ', StationData, ': ', e,  "\033[0m")




            
###     GENERATE PREDICTION FROM FUNCTION CONTAINING MODELS_DICT     ###

def generateCoordinates(stationNumber):
    result = predict(stationNumber)
    xValues = []
    yValues = []
    for i in result:
        yValues.append(i)
    for i in range(len(result)):
        xValues.append(i*forecastInterval/60)
    coordsTuple = (xValues, yValues)

    return coordsTuple

###     GENERATE A SINGLE MODEL AND PREDICT     ###

def generate_model_and_coords(stationNumber):
    # This function actually gets the saved model and uses it to predict

    #model = model_creation_single(stationNumber)
    i = stationNumber
    modelFileName = 'ML/rf_model'+ str(i) +'.pkl'
    with open(modelFileName, 'rb') as handle:
        model = pickle.load(handle)
    

    print('MODEL LOADED!')
    #result = predict_with_single_model(model, stationNumber)
    result = predict_with_single_model_high_hours_res(model, stationNumber)
    xValues = []
    yValues = []
    for i in result:
        yValues.append(i)
    for i in range(len(result)):
        xValues.append(i*forecastInterval/60)
    coordsTuple = (xValues, yValues)
    return coordsTuple


def generate_model_and_coords_stands(stationNumber):
    # This function actually gets the saved model and uses it to predict

    #model = model_creation_single(stationNumber)
    i = stationNumber
    modelFileName = 'ML/rf_model_stands'+ str(i) +'.pkl'
    with open(modelFileName, 'rb') as handle:
        model = pickle.load(handle)
    

    print('MODEL LOADED!')
    #result = predict_with_single_model(model, stationNumber)
    result = predict_with_single_model_high_hours_res(model, stationNumber)
    xValues = []
    yValues = []
    for i in result:
        yValues.append(i)
    for i in range(len(result)):
        xValues.append(i*forecastInterval/60)
    coordsTuple = (xValues, yValues)
    return coordsTuple


#create_models_stands()

# print(generate_model_and_coords(11))
# print(generate_model_and_coords_stands(11))

def trip_predict(FrontendJSON):

    Input = FrontendJSON
    flattened_input = []
    for feature in Input:
        finput = {
                    'startHour': Input['startHour']+Input['startMinute']/60,
                    'startMinute': Input['startMinute'],
                    'startMonth': Input['startMonth'],
                    'endHour': Input['endHour'],
                    'endMinute': Input['endMinute'],
                    'endMonth': Input['endMonth'],
                    'startDayOfWeek': Input['startDayOfWeek'],
                    'endDayOfWeek': Input['endDayOfWeek'],
                    'startStationNumber': Input['startStationNumber'],
                    'endStationNumber': Input['endStationNumber'],
                    'startUnixTimestamp': Input['startUnixTimestamp'],
                    'endUnixTimestamp': Input['endUnixTimestamp'],
                    }

    forecast_df = weather_api_request_forecast()

    differenceStart = (forecast_df['Timestamp'] - finput['startUnixTimestamp']).abs()
    closestEpochColumnIndexStart = differenceStart.idxmin()
    forecastRowStart = forecast_df.loc[closestEpochColumnIndexStart]

    differenceEnd = (forecast_df['Timestamp'] - finput['endUnixTimestamp']).abs()
    closestEpochColumnIndexEnd = differenceEnd.idxmin()
    forecastRowEnd = forecast_df.loc[closestEpochColumnIndexEnd]
    
    toPredictStart = pd.DataFrame()
    toPredictEnd = pd.DataFrame()

    toPredictStart[['month', 'hour', 'day_of_week', 'windspeed', 'temperature', 'humidity', 'visibility']] = [[finput['startMonth'], finput['startHour'], finput['startDayOfWeek'], forecastRowStart['Wind_Speed'], forecastRowStart['Temperature'], forecastRowStart['Humidity'], forecastRowStart['visibility']]]
    toPredictEnd[['month', 'hour', 'day_of_week', 'windspeed', 'temperature', 'humidity', 'visibility']] = [[finput['endMonth'], finput['endHour'], finput['endDayOfWeek'], forecastRowEnd['Wind_Speed'], forecastRowEnd['Temperature'], forecastRowEnd['Humidity'], forecastRowEnd['visibility']]]

    modelFileNameStart = 'ML/rf_model'+ str(finput['startStationNumber']) +'.pkl'
    with open(modelFileNameStart, 'rb') as handle:
        modelStart = pickle.load(handle)

    modelFileNameEnd = 'ML/rf_model'+ str(finput['endStationNumber']) +'.pkl'
    with open(modelFileNameEnd, 'rb') as handle:
        modelEnd = pickle.load(handle)

    return (modelStart.predict(toPredictStart), modelEnd.predict(toPredictEnd))



def trip_predict_stands(FrontendJSON):

    Input = FrontendJSON
    flattened_input = []
    for feature in Input:
        finput = {
                    'startHour': Input['startHour']+Input['startMinute']/60,
                    'startMinute': Input['startMinute'],
                    'startMonth': Input['startMonth'],
                    'endHour': Input['endHour'],
                    'endMinute': Input['endMinute'],
                    'endMonth': Input['endMonth'],
                    'startDayOfWeek': Input['startDayOfWeek'],
                    'endDayOfWeek': Input['endDayOfWeek'],
                    'startStationNumber': Input['startStationNumber'],
                    'endStationNumber': Input['endStationNumber'],
                    'startUnixTimestamp': Input['startUnixTimestamp'],
                    'endUnixTimestamp': Input['endUnixTimestamp'],
                    }

    forecast_df = weather_api_request_forecast()

    differenceStart = (forecast_df['Timestamp'] - finput['startUnixTimestamp']).abs()
    closestEpochColumnIndexStart = differenceStart.idxmin()
    forecastRowStart = forecast_df.loc[closestEpochColumnIndexStart]

    differenceEnd = (forecast_df['Timestamp'] - finput['endUnixTimestamp']).abs()
    closestEpochColumnIndexEnd = differenceEnd.idxmin()
    forecastRowEnd = forecast_df.loc[closestEpochColumnIndexEnd]
    
    toPredictStart = pd.DataFrame()
    toPredictEnd = pd.DataFrame()

    toPredictStart[['month', 'hour', 'day_of_week', 'windspeed', 'temperature', 'humidity', 'visibility']] = [[finput['startMonth'], finput['startHour'], finput['startDayOfWeek'], forecastRowStart['Wind_Speed'], forecastRowStart['Temperature'], forecastRowStart['Humidity'], forecastRowStart['visibility']]]
    toPredictEnd[['month', 'hour', 'day_of_week', 'windspeed', 'temperature', 'humidity', 'visibility']] = [[finput['endMonth'], finput['endHour'], finput['endDayOfWeek'], forecastRowEnd['Wind_Speed'], forecastRowEnd['Temperature'], forecastRowEnd['Humidity'], forecastRowEnd['visibility']]]

    modelFileNameStart = 'ML/rf_model_stands'+ str(finput['startStationNumber']) +'.pkl'
    with open(modelFileNameStart, 'rb') as handle:
        modelStart = pickle.load(handle)

    modelFileNameEnd = 'ML/rf_model_stands'+ str(finput['endStationNumber']) +'.pkl'
    with open(modelFileNameEnd, 'rb') as handle:
        modelEnd = pickle.load(handle)

    return (modelStart.predict(toPredictStart), modelEnd.predict(toPredictEnd))
