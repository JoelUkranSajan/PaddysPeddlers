import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, InvalidRequestError
from sqlalchemy import text
from DB.DatabaseCreation import Station, Availability, Weather, engine
from datetime import datetime
import pandas as pd
from DB.Common.common import log_error

# See Reference 1 for resource used for accessing and adding to database using SQLAlchemy.
# See Reference 2 for resource used for deciding which core SQLAlchemy exception types to import.
# See Reference 3 for resource used for sourcing Python error types related to dictionaries and file handling.

################################################################################################################

# START OF FUNCTION

def log_error(error_log_filename, error_message):
    """This function is used to log errors encountered during the execution of functions defined in this module. 

    Args:
        error_log_filename (str): Parameter for name of error file for the specified function.
        error_message (str): Error message to be logged in the error_log.txt file.

    Returns:
        The function does not return anything.
    """
    
    timestamp = datetime.now()
    
    try:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"{timestamp} - Error: {error_message}\n")
    except:
        print("Error occured during logging of error.\n")
        
# END OF FUNCTION

################################################################################################################

# START OF FUNCTION

def json_to_list(json_file):
    
    """The function opens the "results.json" file and reads the stations static data into the "jc_data" 
    (short for "JCDeveaux Data") variable. The json module "json.loads()" method is called with "jc_data" as 
    the argument and creates a list of dictionaries named "jc_data_list" (short for "JCDeveaux Data List").

    Args:
        json_file (json file): JSON file containing data scraped from JCDeveaux.
    
    Returns:
        List of dictionaries containinf the JSON data.
    """
    
    try:
        with open(json_file, 'r') as file:
            jc_data = file.read()

        jc_data_list = json.loads(jc_data)
        
        return jc_data_list
    
    except FileNotFoundError as e:
        log_error("error_log.txt", f"json_to_list() function error - FNF: {e}")
        return None
    except IOError as e:
        log_error("error_log.txt", f"json_to_list() function error - IO: {e}")
        return None
    except PermissionError as e:
        log_error("error_log.txt", f"json_to_list() function error - Permissions: {e}")
        return None
    except json.JSONDecodeError as e:
        log_error("error_log.txt", f"json_to_list() function error - JSON Decode: {e}")
        return None

# END OF FUNCTION

################################################################################################################
# START OF FUNCTION

def update_stations_to_db(jc_data_list):
    """
    This function accepts the "jc_data_list" list returned from json_to_list() as an argument. 
    The function creates a session with the database. It then loops through each dictionary entry in 
    "jc_data_list" and extracts the required data. The data is added to a station object which is the
    committed to the database. Finally, the session is closed and function execution terminates.
    The function does not return anything.

    Note that the "banking" dictionary entry in the JSON file is in boolean form. The function casts this to 
    "int" type in alignment with the sample SQL schema provided in the COMP30830 "API Requests, Scraping, RDS" 
    lecture.

    Args:
        jc_data_list (list): List of dictionaries containing information on Dublin Bikes stations.
    """  
    
    Session = sessionmaker(bind=engine) 
    session = Session()
    
    for entry in jc_data_list:
        existing_entry = session.query(Availability).filter_by(number=entry["number"]).first()
        # This line should check for an existing entry by means of the above query on the Availability table using the information
        # extracted from the "entry" dictionary from jc_data_list. first() should return None if it is not in the database which 
        # causes the following if statement to not be executed, adding "entry" to the database. See Reference 4.
        
        if existing_entry:  # Should the Stations table be updated on every fetch? Ask TA.
            continue
        else:
            try:
            
                number = entry["number"]
                address = entry["address"]      
                banking = int(entry["banking"])
                bikestands = entry["bike_stands"]
                name = entry["name"]
                positionlat = entry["position"]["lat"]
                positionlong = entry["position"]["lng"]
                
                station = Station(number, address, banking, bikestands, name, positionlat, positionlong)
                session.add(station)
                session.commit()
            
            except KeyError as e:
                log_error("error_log.txt", f"extract_stations() function error - Key Error on entry = {entry}: {e}")
            except ValueError as e:
                log_error("error_log.txt", f"extract_stations() function error - Value Error on entry = {entry}: {e}")
            except SQLAlchemyError as e:
                log_error("error_log.txt", f"extract_stations() function error - SQLAlchemy Error on entry = {entry}: {e}")
            except IntegrityError as e:
                log_error("error_log.txt", f"extract_stations() function error - Integrity Error on entry = {entry}: {e}")
            except InvalidRequestError as e:
                log_error("error_log.txt", f"extract_stations() function error - Invalid Request Error on entry = {entry}: {e}")
    session.close()

# END OF FUNCTION

################################################################################################################    

# START OF FUNCTION

def update_availability_to_db(jc_data_list, scraper_time_stamp):
    """
    This function loops through each dictionary entry in "jc_data_list" and extracts the availability data.
    The function also takes "scraper_time_stamp" as an argument and adds this to the database in the "scrape_time" column to allow
    the availability table to be joined with the weather table. The function does not return a value.
    Args:
    jc_data_list (list): List of dictionaries containing information on Dublin Bikes stations.
    """
    
    Session = sessionmaker(bind=engine) 
    session = Session()
    for entry in jc_data_list:
        
        existing_entry = session.query(Availability).filter_by(number=entry["number"], last_update=entry["last_update"]).first()
        if existing_entry:
            continue   
        # This line should check for an existing entry by means of the above query on the Availability table using the information
        # extracted from the "entry" dictionary from jc_data_list. first() should return None if it is not in the database which 
        # causes the following if statement to not be executed, adding "entry" to the database. See Reference 4.
            
        else:
            try:
                number = entry["number"]
                last_update = entry["last_update"]
                available_bikes = entry["available_bikes"]
                available_bike_stands = entry["available_bike_stands"]
                status = entry["status"]
                scrape_time = scraper_time_stamp
                
                availability = Availability(number, last_update, available_bikes, available_bike_stands, status, scrape_time)
                session.add(availability)
                session.commit()
                
            except KeyError as e:
                    log_error("error_log.txt", f"extract_availability() function error - Key Error on entry = {entry}: {e}")
            except ValueError as e:
                log_error("error_log.txt", f"extract_availability() function error - Value Error on entry = {entry}: {e}")
            except SQLAlchemyError as e:
                log_error("error_log.txt", f"extract_availability() function error - SQLAlchemy Error on entry = {entry}: {e}")
            except IntegrityError as e:
                log_error("error_log.txt", f"extract_availability() function error - Integrity Error on entry = {entry}: {e}")
            except InvalidRequestError as e:
                log_error("error_log.txt", f"extract_availability() function error - Invalid Request Error on entry = {entry}: {e}") 
    
    session.close()
    
# END OF FUNCTION

################################################################################################################

# START OF FUNCTION
def update_weather_to_db(json_file, scraper_time_stamp):
    """
    This function loops through each dictionary entry in "w_data_list" and extracts the weather data.
    The function also takes "scraper_time_stamp" as an argument and adds this to the database in the "scrape_time" column to allow
    the weather table to be joined with the availability table.
    The function does not return a value.
    Args:
        w_data_list (list): List of dictionaries containing weather information.
    """
    
    Session = sessionmaker(bind=engine) 
    session = Session()
    
    with open(json_file, 'r') as file:
        json_data = json.load(file)
        
    existing_entry = session.query(Weather).filter_by(time=json_data["dt"]).first()
        
    if not existing_entry:
        try:
            
            station_id = json_data["id"]
            weather_main = json_data["weather"][0]["main"]
            weather_description = json_data["weather"][0]["description"]
            temperature = json_data["main"]["temp"]
            feels_like = json_data["main"]["feels_like"]
            pressure = json_data["main"]["pressure"]
            humidity = json_data["main"]["humidity"]
            visibility = json_data["visibility"]
            windspeed = json_data["wind"]["speed"]
            clouds = json_data["clouds"]["all"]
            time = json_data["dt"]
            sunrise = json_data["sys"]["sunrise"]
            sunset = json_data["sys"]["sunset"]
            scrape_time = scraper_time_stamp
            
            weather = Weather(station_id, weather_main, weather_description, temperature, feels_like, pressure,
                        humidity, visibility, windspeed, clouds, time, sunrise, sunset, scrape_time)
            session.add(weather)
            session.commit()
            
        except KeyError as e:
                log_error("error_log.txt", f"extract_weather() function error - Key Error")
        except ValueError as e:
            log_error("error_log.txt", f"extract_weather() function error - Value Error")
        except SQLAlchemyError as e:
            log_error("error_log.txt", f"extract_weather() function error - SQLAlchemy Error")
        except IntegrityError as e:
            log_error("error_log.txt", f"extract_weather() function error - Integrity Error")
        except InvalidRequestError as e:
            log_error("error_log.txt", f"extract_weather() function error - Invalid Request Error") 

    session.close()
    
# END OF FUNCTION

################################################################################################################

# START OF FUNCTION

# Code adapted from Reference 5.

# SQ1 (Sub-Query 1) returns a table with each bike station and it's latest "last_update" value.
# SQ2 (Sub-Query 2) joins the result of SQ1 back with the Availbility table to return the latest availability data.
# The result of SQ2 is then joined with the Station table to provide an amalgamated table containing the most up-to-date composite data
# and the subsequent code exports this as a JSON file for use by the front end.

def get_station_data_from_db(file_name):
    df = pd.read_sql_table("station", engine)
    sql_query = text("""
    SELECT
        s.number,
        s.address,
        s.banking,
        s.bikestands,
        s.name,
        s.positionlat,
        s.positionlong,
        SQ2.last_update,
        SQ2.available_bikes,
        SQ2.available_bike_stands,
        SQ2.status
        
    FROM station s 
    JOIN (
        SELECT a.number, a.last_update, a.available_bikes, a.available_bike_stands, a.status 
        FROM availability a
        JOIN (
            SELECT number, MAX(last_update) as latest_update
            FROM availability
            GROUP BY number) SQ1
            ON a.number = SQ1.number AND a.last_update = SQ1.latest_update) SQ2
        ON s.number = SQ2.number;
    """)

    with engine.begin() as connection:
        result = pd.read_sql_query(sql = sql_query, con = connection)

    with open(file_name, 'w') as file:
        result.to_json(file_name, orient="records")

# END OF FUNCTION

################################################################################################################

# START OF FUNCTION

def availability_weather_join():
    """
    This function queries the data base and joins the "availability" and "weather" tables based on equality of the
    "scrape_time" attributes of both tables. The function returns a Pandas dataframe.
    """
    df = pd.read_sql_table("availability", engine)
    
    sql_query = text("""
    SELECT * FROM availability A
    JOIN weather W
    ON A.scrape_time = W.scrape_time;
    """)

    with engine.begin() as connection:
        result = pd.read_sql_query(sql = sql_query, con = connection)

    return result

# END OF FUNCTION

################################################################################################################

# START OF FUNCTION

def latest_weather(file_name):
    """This function returns the latest weather data from the weather table in the database.
    """

    df = pd.read_sql_table("weather", engine)
    
    sql_query = text("""
    SELECT * FROM weather
    WHERE scrape_time = (SELECT MAX(scrape_time) FROM weather);
    """)

    with engine.begin() as connection:
        result = pd.read_sql_query(sql = sql_query, con = connection)
    
    with open(file_name, 'w') as file:
        result.to_json(file_name, orient="records")

# END OF FUNCTION

################################################################################################################


# References:
# 1) Python SQLAlchemy ORM - CREATE, READ, UPDATE, DELETE Data - https://www.youtube.com/watch?v=f0-kEG37GE0&ab_channel=ZeqTech
# 2) SQLAlchemy Core Exceptions - https://docs.sqlalchemy.org/en/20/core/exceptions.html
# 3) Python Error Types - https://www.tutorialsteacher.com/python/error-types-in-python
# 4) Intro to Flask SQLAlchemy Queries - https://www.youtube.com/watch?v=JKoxrqis0Co&list=PLXmMXHVSvS-BlLA5beNJojJLlpE0PJgCW&index=3&ab_channel=PrettyPrinted
# 5) Proclus Academy, Pandas: How to Read and Write Data to a SQL Database - https://proclusacademy.com/blog/practical/pandas-read-write-sql-database/
# 6) SaturnCloud, Converting Pandas DataFrame to JSON Object Column: A Guide - https://saturncloud.io/blog/converting-pandas-dataframe-to-json-object-column-a-comprehensive-guide/
# 7) StackOverflow Convert Pandas DataFrame to JSON format - https://stackoverflow.com/questions/39257147/convert-pandas-dataframe-to-json-format
# 8) Pandas Documentation, - pandas.DataFrame.to_json https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html
