# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from flask import Flask, jsonify




#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Users/mattzavala/Documents/Data Science Bootcamp/sqlalchemy-challenge/SurfsUp/Resources/Starter_Code-4/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "api/v1.0/tobs<br/>"
        "api/v1.0/start_date/YYYY-MM-DD<br/>"
        "api/v1.0/start_date/YYYY-MM-DD/end_date/YYYY-MM-DD<br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session_instance = Session()
    try:
        result = session_instance.query(Measurement.date, Measurement.prcp).all()
        precipitation_data = {date: prcp for date, prcp in result}
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        session_instance.close()

    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations<br/>')
def stations():
    session_instance = Session()
    try:
        station_data = session_instance.query(Station.station, Station.name).all()
        result = [{'station': station, 'name': name} for station, name in station_data]
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        session_instance.close()
    
    return jsonify(result)

@app.route('api/v1.0/tobs<br/>')
def tobs():
    session_instance = Session()
    try:
        most_active = session_instance.query(Measurement.station)\
            .group_by(Measurement.station)\
            .order_by(func.count(Measurement.id).desc()).first()[0]
        
        latest_date = dt.datetime.strptime('2017-08-18', '%Y-%m-%d')
        one_year_ago = latest_date - dt.timedelta(days=366)

        result = session_instance.query(Measurement.date, Measurement.tobs)\
            .filter(Measurement.station == most_active)\
            .filter(Measurement.date >= one_year_ago).all()
        
        tobs_data = {str(date): tobs for date, tobs in result}

    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        session_instance.close()
        
    return jsonify(tobs_data)

@app.route('/api/v1.0/start_date/<string:start_date>')
def temp_stats_start(start_date):
    session_instance = Session()
    try:
        start_obj = dt.datetime.strptime(start_date, '%Y-%m-%d')
 
        results = session_instance.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start_obj).all()

        temp_stats = {
            'start_date': start_date,
            'min_temperature': results[0][0],
            'avg_temperature': results[0][1],
            'max_temperature': results[0][2]
        }
 
        return jsonify(temp_stats)
 
    except Exception as e:
        return jsonify({'error': str(e)})
 
    finally:
        session_instance.close()

@app.route('/api/v1.0/start_date/<start_date>/end_date/<end_date>')
def temp_stats_start_end(start_date, end_date):
    session_instance = Session()
    try:
        start_obj = dt.datetime.strptime(start_date, '%Y-%m-%d')
        end_obj = dt.datetime.strptime(end_date, '%Y-%m-%d')
 
        # Query temperature stats from Measurements table
        results = session_instance.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start_obj, Measurement.date <= end_obj).all()
 
        # Create a dictionary with temperature stats
        temp_stats = {
            'start_date': start_date,
            'end_date': end_date,
            'min_temperature': results[0][0],
            'avg_temperature': results[0][1],
            'max_temperature': results[0][2]
        }
 
        return jsonify(temp_stats)
 
    except Exception as e:
        return jsonify({'error': str(e)})
 
    finally:
        session_instance.close()
 
# Run the Flask application if executed as the main script
if __name__ == '__main__':
    app.run(debug=True)