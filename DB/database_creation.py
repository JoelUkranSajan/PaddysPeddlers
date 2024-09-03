from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
#import pymysql


# Database access details.
# See Reference 1.
URL = "dublinbikesdb.c1aeqwowc1uf.eu-north-1.rds.amazonaws.com"
PORT = "3306"
DB = "DBProject_InitName"
USER = "admin"
PASSWORD = "COMP30830"

# This line creates a SQLAlchemy engine using the database connection URL (DB_URL). 
# The echo=True parameter enables logging of SQL statements that are executed.
engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URL, PORT, DB), echo=True)

#This line invokes the declarative_base function to create a base class (Base). 
# The Base class serves as a parent class for all the SQLAlchemy models (mapped classes) that you define in
# your application. When you create a model, you typically inherit from this base class, and it provides some 
# common functionality, such as automatically generating table names and managing the mapping of attributes to columns.

Base = declarative_base()    

# The following classes define the tables to be created within the database. See to Reference 2.

class Station(Base):
    
    __tablename__ = "station"
    
    number = Column(Integer, primary_key = True, nullable = False)
    address = Column(String(128))
    banking = Column(Integer)
    bikestands = Column(Integer)
    name = Column(String(128))
    positionlat = Column(Float)
    positionlong = Column(Float)
    
    def __init__(self, number, address, banking, bikestands, name, latitude, longtitude):
        self.number = number
        self.address = address
        self.banking = banking
        self.bikestands = bikestands
        self.name = name
        self.positionlat = latitude
        self.positionlong = longtitude

class Availability(Base):
    
    __tablename__ = "availability"
    
    number = Column(Integer, ForeignKey('station.number'), nullable = False, primary_key = True)
    last_update = Column(BigInteger, nullable = False, primary_key = True)
    available_bikes = Column(Integer)
    available_bike_stands = Column(Integer)
    status = Column(String(128))
    scrape_time = Column(BigInteger, nullable = False)
    
    def __init__(self, number, update, available_bikes, available_stands, status, scrape_time):
        self.number = number
        self.available_bikes = available_bikes
        self.available_bike_stands = available_stands
        self.last_update = update
        self.status = status
        self.scrape_time = scrape_time

class Weather(Base):
    
    __tablename__ = "weather"
    
    station_id = Column(Integer, nullable = False, primary_key = True)
    weather_main = Column(String(128))
    weather_description = Column(String(128))
    temperature = Column(Float)
    feels_like = Column(Float)
    pressure = Column(Integer)
    humidity = Column(Integer)
    visibility = Column(Integer)
    windspeed = Column(Float)
    clouds = Column(Integer)
    time = Column(BigInteger, nullable = False, primary_key = True)
    sunrise = Column(BigInteger)
    sunset = Column(BigInteger)
    scrape_time = Column(BigInteger, nullable = False)
    
    def __init__(self, station, main, description, temperature, feels_like, pressure, 
                 humidity, visibility, windspeed, clouds, time, sunrise, sunset, scrape_time):
        self.station_id = station
        self.weather_main = main
        self. weather_description = description
        self.temperature = temperature
        self.feels_like = feels_like
        self.pressure = pressure
        self.humidity = humidity
        self.visibility = visibility
        self.windspeed = windspeed
        self.clouds = clouds
        self.time = time
        self.sunrise = sunrise 
        self.sunset = sunset
        self.scrape_time = scrape_time    
    
# Database has already been created. The following code is for troubleshooting only.
# Drop existing tables.
#Base.metadata.drop_all(engine)

# Recreate tables with the updated model
#Base.metadata.create_all(engine)

# References:
# 1) COMP30830 Sofware Engineering (Conversion) - API Requests, Scraping, RDS Lecture.
# 2) Python SQLAlchemy ORM Introduction: https://www.youtube.com/watch?v=Z2zD3EdjpNo&t=428s&ab_channel=ZeqTech


