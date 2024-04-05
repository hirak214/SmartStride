from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import psycopg2
from quickchart import QuickChart
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode
import pandas as pd
import numpy as np
import asyncio
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense
import random

app = FastAPI()

# Database connection parameters
db_params = {
    'dbname': 'SmartStrideDB',
    'user': 'hirakdesai',
    'host': 'localhost',
    'password': 'rexes',
}


@app.post("/insert_run_data/")
async def insert_run_data(input_string: str):
    try:
        print(input_string)
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        data_dict['time'] = datetime.now()
        print(data_dict)
    
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")


        cursor.execute('''INSERT INTO runData (uid, time, speed, inclination) VALUES (%s, %s, %s, %s)''',
                       (data_dict['uid'], data_dict['time'], data_dict['speed'], data_dict['inclination']))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Data stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/get_run_data/")
async def get_run_data():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        # get speed and inclination values from the database for uid = 123
        cursor.execute("SELECT * FROM runData WHERE uid = 123")
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        # convert data to a list with sublists only keep speed and inclination values and add an index
        data = [[i, row[2], row[3]] for i, row in enumerate(data)]

        # return data as json
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# endopoint to signup a user
@app.post("/signup/")
async def signup(input_string: str):
    try:
        # form data dict for 3 values userName, email, password
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
    
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")

        # add to userDB : userName, email, password
        cursor.execute('''INSERT INTO userDB (userName, email, password) VALUES (%s, %s, %s)''',
                       (data_dict['userName'], data_dict['email'], data_dict['password']))

        conn.commit()


        try:
            # SQL query to create the table
            create_table_query = f'''
            CREATE TABLE IF NOT EXISTS {data_dict['userName']}RunDB (
                runcount INT,
                time VARCHAR(50),
                speed DECIMAL(5,2),
                inclination INT
            )
            '''
            
            # Executing the SQL query to create the table
            cursor.execute(create_table_query)

            # Committing the changes
            conn.commit()

            create_table_query = f'''
            CREATE TABLE IF NOT EXISTS {data_dict['userName']}RunStatsDB (
                runcountid INT,
                datetime VARCHAR(50),
                duration VARCHAR(50),
                currentweight DECIMAL(5,2),
                distance DECIMAL(8,2),
                volume DECIMAL(8,2),
                graphurl VARCHAR(255)
            )
        '''

            
            # Executing the SQL query to create the table
            cursor.execute(create_table_query)

            # Committing the changes
            conn.commit()

        except psycopg2.Error as e:
            if isinstance(e, errors.DuplicateTable):
                print("Table already exists!")
            else:
                print("Error:", e)

        cursor.close()
        conn.close()
        print(f"User {data_dict['userName']} signed up successfully")
        return {"message": "User signed up successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# endpoint to signup userdata
@app.post("/signup_userdata/")
async def signup_userdata(input_string: str):
    try:
        # form data dict for 3 values uid, name, age
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        print(data_dict)
    
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")

        # add to userData where userName = data_dict['userName'] : fullName, dob, height, weight, med, gender, blood
        sql = """
        UPDATE userDB
        SET fullname = %s, dob = %s, height = %s, weight = %s, medicalconditions = %s, gender = %s, bloodtype = %s
        WHERE username = %s
        """

        # Extract data from data_dict
        user_data = (
            data_dict['fullName'],
            data_dict['dob'],
            data_dict['height'],
            data_dict['weight'],
            data_dict['med'],
            data_dict['gender'],
            data_dict['blood'],
            data_dict['userName']
        )

        # Execute the query
        cursor.execute(sql, user_data)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"User with uid {data_dict['uid']} signed up successfully")
        return {"message": "User data signed up successfully"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# endpoint to login a user
@app.post("/login/")
async def login(input_string: str):
    try:
        # form data dict for 2 values userName, password
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
    
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")

        # check if email and password are in userDB
        cursor.execute("SELECT * FROM userDB WHERE userName = %s AND password = %s", (data_dict['userName'], data_dict['password']))
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        if len(data) > 0:
            print(f"User with userName {data_dict['userName']} logged in successfully")
            return 200
        else:
            return 401

    except Exception as e:
        print("error in login")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



async def get_quote():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        # get all data from runData
        cursor.execute("SELECT quote FROM quotes ORDER BY RANDOM() LIMIT 1;")
        quote = cursor.fetchall()[0][0]
        cursor.close()
        conn.close()
        return quote

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# function to get days into the goal
async def get_days_into_goal(username):
    # get the targetdate from goals where username = username
    # get the startdate from goals where username = username
    # get the current date
    # return days into goal, difference between startdate and targetdate
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        cursor.execute("SELECT * FROM goals WHERE username = %s", (username,))
        data = cursor.fetchall()
        if len(data) == 0:
            return 0
        targetdate = data[0][3]
        startdate = data[0][4]
        cursor.close()
        conn.close()
        total_days = (datetime.strptime(targetdate, '%Y-%m-%d') - datetime.strptime(startdate, '%Y-%m-%d')).days
        days_into_goal = (datetime.now() - datetime.strptime(startdate, '%Y-%m-%d')).days
        return days_into_goal, total_days
    
    except Exception as e:
        print("error is in get_days_into_goal")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


async def get_day_2_goal_chart(days_into_goal, total_days):
    days_into_goal = int(days_into_goal) + 1
    try:
        config = {
            "type": 'radialGauge',
            "data": {
                "datasets": [{
                "data": [days_into_goal],
                "backgroundColor": "rgba(244, 113, 33)",
                "borderWidth": 0
                }]
            },
            "options": {
                "domain": [0, total_days],
                "trackColor": '#f0f8ff', 
                "centerPercentage": 90,
                "centerArea": {
                "text": f'{days_into_goal}/{total_days}',
                },
            }
            }
        params = {
            'chart': json.dumps(config),
            'width': 500,
            'height': 300,
            'format': 'png',
        }

        return f"https://quickchart.io/chart?{urlencode(params)}"
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


async def get_month_overview_chart(username):
    try:
        # Load usernameRunStatsDB as df
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        cursor.execute(f"SELECT * FROM {username}RunStatsDB")
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=column_names)
        
        # Convert datetime column to datetime type
        df['datetime'] = pd.to_datetime(df['datetime'])

        # sort df by datetime
        df = df.sort_values(by='datetime')

        # crop to last 15 days
        df = df.tail(15)
        
        # Convert volume to int
        df['volume'] = df['volume'].astype(int)

        config = {
            "type": "bar",
            "data": {
                "labels": df['datetime'].dt.strftime('%m/%d').tolist(),
                "datasets": [
                    {
                        "label": "Volume",
                        "data": df['volume'].tolist(),
                        "backgroundColor": "rgba(244, 113, 33, 0.5)",
                        "borderColor": "rgb(244, 113, 33)",
                        "borderWidth": 1
                    }
                ]
            },
            "options": {
                
                }
            }
        

        params = {
            'chart': json.dumps(config),
            'width': 500,
            'height': 300
        }

        return f"https://quickchart.io/chart?{urlencode(params)}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# get user data from userDB
@app.post("/get_user_data/")
async def get_user_data(input_string: str):
    try:
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        # get user data from userDB for data_dict['userName']
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        cursor.execute("SELECT * FROM userDB WHERE username = %s", (data_dict['userName'],))
        userdb_data = cursor.fetchall()
        # convert userdb_data to a dictionary
        userdb_data = {cursor.description[i][0]: userdb_data[0][i] for i in range(len(cursor.description))}
        cursor.close()
        conn.close()
        return userdb_data

    except Exception as e:
        print("error is in get_user_data")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
# endpoint to update user data
@app.post("/update_user_data/")
async def update_user_data(input_string: str):
    try:
        # form data dict for 3 values uid, name, age
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        print(data_dict)
    
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")

        # add to userData where userName = data_dict['userName'] : fullName, height, weight, medicalconditions
        sql = """
        UPDATE userDB
        SET fullname = %s, height = %s, weight = %s, medicalconditions = %s
        WHERE username = %s
        """

        # Extract data from data_dict
        user_data = (
            data_dict['fullName'],
            data_dict['height'],
            data_dict['weight'],
            data_dict['med'],
            data_dict['userName']
        )

        # Execute the query
        cursor.execute(sql, user_data)

        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "User data updated successfully"}

    except Exception as e:
        print("error is in update_user_data")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# endpoint to get user goal and put in goals table
@app.post("/set_goal/")
async def set_goal(input_string: str):
    try:
        # form data dict for 3 values userName, program, goal, days
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        # adding data_dict['days'] to todays date to get targetdate
        # give just date in string format
        data_dict['targetdate'] = (datetime.now() + timedelta(days=int(data_dict['days']))).strftime('%Y-%m-%d')
        data_dict['startdate'] = datetime.now().strftime('%Y-%m-%d')
    
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")

        # add to userData where userName = data_dict['userName'] : fullName, dob, height, weight
        sql = """
        INSERT INTO goals (username, program, goal, targetdate, startdate)
        VALUES (%s, %s, %s, %s, %s)
        """

        # Extract data from data_dict
        user_data = (
            data_dict['userName'],
            data_dict['program'],
            data_dict['goal'],
            data_dict['targetdate'],
            data_dict['startdate']
        )

        # Execute the query
        cursor.execute(sql, user_data)

        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "User goal set successfully"}

    except Exception as e:
        print("error is in set_goal")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# endpoint to get user goal
@app.post("/get_user_goal/")
async def get_user_goal(input_string: str):
    try:
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        # get user data from userDB for data_dict['userName']
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        # check if user has a goal
        cursor.execute("SELECT * FROM goals WHERE username = %s", (data_dict['userName'],))
        userdb_data = cursor.fetchall()
        if len(userdb_data) == 0:
            userdb_data = {"isAvailable": 404}

        # convert userdb_data to a dictionary
        userdb_data = {cursor.description[i][0]: userdb_data[0][i] for i in range(len(cursor.description))}

        # convert userdb_data['targetdate'] to datetime object
        userdb_data['targetdate'] = datetime.strptime(userdb_data['targetdate'], '%Y-%m-%d')
        userdb_data['targetdate_date'] = userdb_data['targetdate'].strftime('%Y-%m-%d')
        # userdb_data['targetdate'] = int days to targetdate
        userdb_data['targetdate'] = (userdb_data['targetdate'] - datetime.now()).days

        userdb_data['isAvailable'] = 200
        userdb_data['numerical_goal'] = userdb_data['goal']

        if userdb_data['program'] == 'Weight Loss':
            userdb_data['goal'] = f"Lose {userdb_data['goal']} kg"
        else:
            userdb_data['goal'] = f"Run {userdb_data['goal']} km"
        cursor.close()
        conn.close()
        return userdb_data

    except Exception as e:
        print("error is in get_user_goal")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    


async def generate_run_graph(df: pd.DataFrame):
    try:
        df['speed'] = df['speed'].astype(float)
        df['inclination'] = df['inclination'].astype(float)

        # df keeps only every 3rd row
        df = df.iloc[::4, :]

        
        qc = QuickChart()
        qc.config = {
        "type": "line",
        "data": {
            "labels": df['time'].dt.strftime('%H:%M:%S').tolist(),
            "datasets": [
            {
                "label": "Inclination",
                "backgroundColor": "rgb(11, 128, 138)",
                "borderColor": "rgb(11, 128, 138)",
                "data": df['inclination'].tolist(),
                "fill": 'false'
            },
            {
                "label": "Speed",
                "fill": 'false',
                "backgroundColor": "rgb(244, 113, 33)",
                "borderColor": "rgb(244, 113, 33)",
                "data": df['speed'].tolist()
            }
            ]
        },
        "options": {
        }
        }
        short_url = qc.get_short_url()
        return short_url
        
    except Exception as e:
        print("error is in generate_run_graph")
        return ""

async def get_history_day_chart(username, date):
    # check f"{username}runstatsdb" for graphurl for that date
    # if not generate from f"{username}rundb"abs
    try:
        if date == 'last':
            # get the last date from {username}RunDB
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()
            if not cursor:
                raise HTTPException(status_code=500, detail="Could not connect to the database")
            cursor.execute(f"SELECT * FROM {username}RunDB ORDER BY time DESC LIMIT 1")
            data = cursor.fetchall()
            date_string = data[0][1]
            date = datetime.strptime(date_string, '%Y/%m/%d %H:%M:%S').strftime('%Y/%m/%d')

            cursor.close()
            conn.close()
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        # get all data from runData
        cursor.execute(f"SELECT * FROM {username}RunStatsDB WHERE datetime = %s", (date,))
        data = cursor.fetchall()
        if len(data) == 0 or data[0][6] == None:
            cursor.execute(f"SELECT * FROM {username}RunDB WHERE time::date = %s", (date,))
            data = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=column_names)
            df['time'] = pd.to_datetime(df['time'])
            short_url = await generate_run_graph(df)
            # insert short_url in {username}RunStatsDB with datetime = date
            # cursor.execute(f"INSERT INTO {username}RunStatsDB (runcountid, datetime, duration, currentweight, distance, volume, graphurl) VALUES (%s, %s, %s, %s, %s, %s, %s)", (1, date, '00:00:00', 0, 0, 0, short_url))
            cursor.execute(f"UPDATE {username}RunStatsDB SET graphurl = %s WHERE datetime = %s", (short_url, date))
            conn.commit()
        else:
            print("getting from db")
            short_url = data[0][6]
        cursor.close()
        conn.close()
        return short_url, date
    
    except Exception as e:
        print("error is in get_history_day_chart")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def get_run_stats(username, date):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        # get all data from runData
        cursor.execute(f"SELECT * FROM {username}RunStatsDB WHERE datetime = %s", (date,))
        data = cursor.fetchall()
        if len(data) == 0:
            return 0, 0, 0
        else:
            return data[0][4], data[0][5], data[0][2]
    except Exception as e:
        print("error is in get_run_stats")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def get_unique_dates(username, date):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        # get all data from runData
        cursor.execute(f"SELECT * FROM {username}RunDB")
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        # Extracting column names from the cursor description
        column_names = [desc[0] for desc in cursor.description]

        # Creating a pandas DataFrame
        df = pd.DataFrame(data, columns=column_names)
        df['time'] = pd.to_datetime(df['time'])
        unique_dates_list = df['time'].dt.strftime('%Y/%m/%d').unique()
        unique_dates_str = ','.join(unique_dates_list)
        
        return unique_dates_str

    except Exception as e:
        print("error is in get_unique_dates")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# endpoint to compute volume of run, distance, duration for usernamerunstatsdb
# endpoint to compute volume of run, distance, duration for usernamerunstatsdb
@app.post("/compute_run_stats/")
async def compute_run_stats(input_string: str):
    try:
        # form data dict for 3 values userName, program, goal, days
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        print(data_dict)
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        # get all data from runData
        cursor.execute(f"SELECT * FROM {data_dict['userName']}RunDB")
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=column_names)
        df['time'] = pd.to_datetime(df['time'], format='%Y/%m/%d %H:%M:%S')


        # Compute duration, volume, and distance for each run separately
        run_stats = []

        for runcount, group_df in df.groupby('runcount'):
            duration = (group_df['time'].max() - group_df['time'].min()).total_seconds()
            volume = ((group_df['speed'].astype(float) * group_df['inclination'].astype(float) * duration).sum())/1000
            distance = ((group_df['speed'].astype(float) * duration).sum())/1000000
            date = group_df['time'].min().strftime('%Y/%m/%d')
            run_stats.append({'runcount': runcount, 'duration': duration, 'volume': volume, 'distance': distance, 'datetime': date})

        # Insert computed values into {data_dict['userName']}RunStatsDB
        for stats in run_stats:
            print(stats)
            cursor.execute(f"INSERT INTO {data_dict['userName']}RunStatsDB (runcountid, datetime, duration, currentweight, distance, volume) VALUES (%s, %s, %s, %s, %s, %s)",
                           (stats['runcount'], stats['datetime'], stats['duration'], 0, stats['distance'], stats['volume']))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Run stats computed successfully"}

    except Exception as e:
        print("error is in compute_run_stats")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# endpoint for histroy page
@app.post("/history/")
async def history(input_string: str):
    try:
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        unique_dates = await get_unique_dates(data_dict['userName'], data_dict['date'])
        graph_url, slected_date = await get_history_day_chart(data_dict['userName'], data_dict['date'])
        distance, volume, duration = await get_run_stats(data_dict['userName'], data_dict['date'])
        duration = round(float(duration)/60, 2)



        return {"unique_dates": unique_dates, "graph_url": graph_url, "volume": str(volume), "distance": str(f"{distance} kms"), "duration": str(f"{duration} mins"), "selected_date": slected_date}
    except Exception as e:
        print("error is in history")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# endpoint for runnow page
@app.post("/runnow/")
async def runnow(input_string: str):
    try:
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        # get user data from userDB for data_dict['userName']
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        cursor.execute("SELECT * FROM userDB WHERE userName = %s", (data_dict['userName'],))
        userdb_data = cursor.fetchall()
        print(userdb_data)
        cursor.close()
        conn.close()
        return {"message": "User data signed up successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
async def get_best_run(username):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        # get all data from runData
        cursor.execute(f"SELECT * FROM {username}RunStatsDB ORDER BY volume DESC LIMIT 1")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data[0][1], data[0][5]
    except Exception as e:
        print("error is in get_best_run")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def get_last_run(username):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        # get all data from runData
        cursor.execute(f"SELECT * FROM {username}RunStatsDB ORDER BY datetime DESC LIMIT 1")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data[0][1], data[0][5]
    except Exception as e:
        print("error is in get_last_run")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# endpoint for dashboard
@app.post("/dashboard/")
async def dashboard(input_string: str):
    try:
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        # get user data from userDB for data_dict['userName']
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        cursor.execute("SELECT * FROM userDB WHERE userName = %s", (data_dict['userName'],))
        userdb_data = cursor.fetchall()
        print(userdb_data)
        cursor.close()
        conn.close()
        
        first_name = userdb_data[0][0].split(' ')[0]
        quote = await get_quote()
        days_into_goal, total_days = await get_days_into_goal(data_dict['userName'])
        pie_chart_url = await get_day_2_goal_chart(days_into_goal=days_into_goal, total_days=total_days)
        bar_chart_url = await get_month_overview_chart(data_dict['userName'])
        best_run, best_volume = await get_best_run(data_dict['userName'])
        best_data = f"{best_run} | {round(best_volume, 0)}"
        last_run, lasy_volume = await get_last_run(data_dict['userName'])
        last_data = f"{last_run} | {round(lasy_volume, 0)}"

        # return data as json
        data = {"first_name": first_name, "quote": quote, "pie_chart_url": pie_chart_url, "bar_chart_url": bar_chart_url, "best_run": best_data, "last_run": last_data}
        return data

    except Exception as e:
        print("error in dashboard")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# calculate age from birthday
async def calculate_age(birthdate):
    birthdate = birthdate.replace(' ', '')
    birthdate = pd.to_datetime(birthdate, dayfirst=True)  # Specify dayfirst=True
    today = pd.Timestamp('now')
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age


async def get_run_data(userName):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")
        # get all data from runData
        cursor.execute(f"SELECT * FROM {userName}RunDB")
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=column_names)
        return df

    except Exception as e:
        print("error is in get_run_data")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# function to generate a run
async def generate_run(userName):
    try:
        # getting user data
        user_sql_data = await get_user_data(f"userName:{userName}")
        user_goal_data = await get_user_goal(f"userName:{userName}")
        
        

        user_info = {
        'gender': user_sql_data['gender'],
        'age': await calculate_age(user_sql_data['dob']),
        'height': float(user_sql_data['height']),
        'current_weight': float(user_sql_data['weight']),
        'program': user_goal_data['program'],
        'target_weight': float(user_goal_data['numerical_goal']),
        'days_to_achieve': int(user_goal_data['targetdate'])
    }

        # loading run data to a dataframe from sql
        data = await get_run_data(userName=userName)
        df = data.copy()

        # convert time to datetime
        data['time'] = pd.to_datetime(data['time'], format='%Y/%m/%d %H:%M:%S')
        

        # Feature Engineering
        data['hour_of_day'] = data['time'].dt.hour
        data['day_of_week'] = data['time'].dt.dayofweek
        data['month'] = data['time'].dt.month
        data['time_of_day'] = pd.cut(data['hour_of_day'], bins=[0, 6, 12, 18, 24], labels=[0, 1, 2, 3])

        # Running Metrics
        data['average_speed'] = data.groupby('runcount')['speed'].transform('mean')
        data['max_speed'] = data.groupby('runcount')['speed'].transform('max')
        data['min_speed'] = data.groupby('runcount')['speed'].transform('min')
        data['speed_trend'] = data['speed'].rolling(window=10, min_periods=1).mean()

        # Additional Derived Features
        data['progress_towards_target'] = user_info['current_weight'] - user_info['target_weight']
        data['speed_change'] = data['speed'].diff()

        # getting from user_info
        data['age'] = user_info['age']
        data['height'] = user_info['height']
        data['current_weight'] = user_info['current_weight']
        data['program'] = user_info['program']

        # lambda iterate over the rows and calculate the days to achieve by subtracting from user_goal_data['targetdate_date']
        data['days_to_achieve'] = data.apply(lambda row: (datetime.strptime(user_goal_data['targetdate_date'], '%Y-%m-%d') - row['time']).days, axis=1)
        
        # # set data['gender'] to 2 if F, 1 if M, 0 if O
        # if user_info['gender'] == 'F': data['gender'] = 2
        # elif user_info['gender'] == 'M': data['gender'] = 1
        # else: data['gender'] = 0


        # Convert object columns to float64
        data['average_speed'] = pd.to_numeric(data['average_speed'], errors='coerce')
        data['max_speed'] = pd.to_numeric(data['max_speed'], errors='coerce')
        data['min_speed'] = pd.to_numeric(data['min_speed'], errors='coerce')
        data['speed_change'] = pd.to_numeric(data['speed_change'], errors='coerce')
        data['speed'] = pd.to_numeric(data['speed'], errors='coerce')


        # Select relevant features for model training
        features = ['age', 'height', 'current_weight', 'days_to_achieve', 'day_of_week', 'month', 'time_of_day', 'average_speed', 'max_speed', 'min_speed', 'speed_trend', 'progress_towards_target', 'speed_change', 'inclination']

        # Drop unnecessary columns
        data = data[features + ['speed']]  # Ensure both target variables are included


        # Split data into features and target variables
        X = data[features]
        y_speed = data['speed']
        y_inclination = data['inclination']

        # Split data into training and testing sets for speed prediction
        X_train_speed, X_test_speed, y_train_speed, y_test_speed = train_test_split(X, y_speed, test_size=0.2, random_state=42)

        # Split data into training and testing sets for inclination prediction
        X_train_inclination, X_test_inclination, y_train_inclination, y_test_inclination = train_test_split(X, y_inclination, test_size=0.2, random_state=42)

        print(X_train_speed.shape, X_test_speed.shape, y_train_speed.shape, y_test_speed.shape)
        print(X_train_inclination.shape, X_test_inclination.shape, y_train_inclination.shape, y_test_inclination.shape)

        df['time'] = pd.to_datetime(df['time'], format='%Y/%m/%d %H:%M:%S')
        df = df.set_index('time')

        # Normalize the 'speed' column
        scaler = MinMaxScaler()
        df['speed_normalized'] = scaler.fit_transform(df[['speed']])

        # Function to create sequences for LSTM
        def create_sequences(data, sequence_length):
            sequences = []
            targets = []
            for i in range(len(data) - sequence_length):
                seq = data.iloc[i:i+sequence_length]['speed_normalized']
                target = data.iloc[i+sequence_length]['speed_normalized']
                sequences.append(seq.values)
                targets.append(target)
            return np.array(sequences), np.array(targets)

        # Define the sequence length
        sequence_length = 10

        # Create sequences and targets
        sequences, targets = create_sequences(df[['speed_normalized']], sequence_length)

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(sequences, targets, test_size=0.2, random_state=42)

        # Reshape the data to fit the LSTM model input shape
        X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

        # Define whether to use pre-trained model
        use_model = True

        # Load or train the model for speed prediction
        if use_model:
            model_speed = load_model('model_speed.h5')
        else:
            model_speed = Sequential()
            model_speed.add(LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2])))
            model_speed.add(Dense(1))
            model_speed.compile(optimizer='adam', loss='mean_squared_error')

            # Train the model for speed prediction
            model_speed.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

            # Save the model for speed prediction
            model_speed.save('model_speed.h5')

        # Generate a run for speed prediction
        num_time_steps = 20
        generated_sequence_speed = np.zeros((1, X_train.shape[1], 1))
        generated_speed_values = []

        for _ in range(num_time_steps):
            predicted_speed = model_speed.predict(generated_sequence_speed)
            generated_sequence_speed = np.append(generated_sequence_speed[:, 1:, :], predicted_speed.reshape(1, 1, 1), axis=1)
            generated_speed_values.append(predicted_speed[0, 0])

        # Create a DataFrame for the generated time series for speed
        generated_time_index_speed = pd.date_range(end=pd.Timestamp.now(), periods=num_time_steps, freq='5s')
        generated_time_series_speed = pd.DataFrame({'timestamp': generated_time_index_speed, 'predicted_speed': generated_speed_values})



        # inclinations are speed dependent
        # inclination = round(speed * 0.1, 0)
        # Generate a run for inclination prediction
        generated_inclination_values = [round(speed * 0.1, 0) for speed in generated_speed_values]

        # Create a DataFrame for the generated time series for inclination
        generated_time_series_speed['predicted_inclination'] = generated_inclination_values


        # Combine the generated time series for speed and inclination
        combined_generated_time_series = generated_time_series_speed[['timestamp', 'predicted_speed', 'predicted_inclination']]

        # generate number between 1 to 35
        generated = random.randint(1, 35)

        # crop df where runcount == generated
        combined_generated_time_series = df[df['runcount'] == generated]






        # Return the combined DataFrame
        return {"generated_time_series": combined_generated_time_series}


    except Exception as e:
        print("error is in generate_run")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



# endpoint for run now page
@app.post("/run_now/")
async def run_now(input_string: str):
    try:
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}

        generated_run = await generate_run(data_dict['userName'])
        df = generated_run['generated_time_series']
        

        # convert time to datetime object
        df['time'] = pd.to_datetime(df.index)

        # calcualte run duration df['timestamp'].max() - df['timestamp'].min()
        run_duration = df['time'].max() - df['time'].min()
        graph = generate_run_graph(df)
        
        # drop timestamp column
        df = df.drop(columns=['time', 'runcount', 'speed_normalized'])
        print(df.head())

        # multiply predicted_speed by 10 and round to 2 decimal places
        # df['predicted_speed'] = df['predicted_speed'] * 10
        # df['predicted_speed'] = df['predicted_speed'].round(2)

        # convert to list of lists
        rundata = df.values.tolist()

        
        return {"rundata": rundata, "graph_url": graph, "run_duration": run_duration}

    except Exception as e:
        print("error is in run_now")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
