# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# create an engine to access the sqlite file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Create the inspector and connect it to the engine
inspector = inspect(engine)

# Collect the names of tables within the database
inspector.get_table_names()


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# find the keys for the respective classes; alternative method to confirm
# Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
##session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# 1) Start from Homepage and list all availabe API routes

@app.route("/")
def welcome():
    """Listing all available api routes."""
    return (
        f"Hawaii Climate API Analysis Guide<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (apply format as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (apply format as YYYY-MM-DD/YYYY-MM-DD)"

    )
     
# 2) Retrieve the last 12 months of data from the precipitation analysis to a dictionary, and use 'date' as the key and 'prcp' as the value

@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_date = dt.date(previous_year.year, previous_year.month, previous_year.day)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_date).order_by(Measurement.date.desc()).all()


    preci_dict = dict(results)

    print(f"Precipitation Results Below - {preci_dict}")
    return jsonify(preci_dict) 


# 3) Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    info = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    queryresult = session.query(*info).all()
    session.close()

    station_list = []
    for station,name,lat,lon,limit in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = limit
        station_list.append(station_dict)

    return jsonify(station_list)

# 4) Query the dates and temperature results of the most-active station for the previous year of data (i.e. Station ID: USC00519281).
#    Return a JSON list of temperature observations for the previous year. 

@app.route("/api/v1.0/tobs")
def tobs():
     session = Session(engine)
        
     
     queryresult_1 = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281').\
         filter(Measurement.date>='2016-08-23').all()
    
     tobs_list = []
     
     for date,tobs in queryresult_1:
         
         tobs_dict = {}
         
         tobs_dict["Date"] = date
         
         tobs_dict["Tobs"] = tobs
        
         tobs_list.append(tobs_dict)
   
            
     return jsonify(tobs_list)
    


# 5) Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#    For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#    For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.


@app.route("/api/v1.0/<start>")

def temps_start(start):
    session = Session(engine)
    queryresult_2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    session.close()

    temps_list_1 = []
    for min_temp, avg_temp, max_temp in queryresult_2:
        temps_dict_1 = {}
        temps_dict_1['Minimum Temperature'] = min_temp
        temps_dict_1['Average Temperature'] = avg_temp
        temps_dict_1['Maximum Temperature'] = max_temp
        temps_list_1.append(temps_dict_1)

    return jsonify(temps_list_1)


@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start, end):
    session = Session(engine)
    queryresult_3 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps_list_2 = []
    for min_temp, avg_temp, max_temp in queryresult_3:
        temps_dict_2 = {}
        temps_dict_2['Minimum Temperature'] = min_temp
        temps_dict_2['Average Temperature'] = avg_temp
        temps_dict_2['Maximum Temperature'] = max_temp
        temps_list_2.append(temps_dict_2)

    return jsonify(temps_list_2)


if __name__ == "__main__":
    app.run(debug=True)

