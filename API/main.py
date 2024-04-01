from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import psycopg2
from datetime import datetime
from quickchart import QuickChart
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode
import pandas as pd

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
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



def get_quote():
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
def get_days_into_goal(username):
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


def get_day_2_goal_chart(days_into_goal, total_days):
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


def get_month_overview_chart(username):
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
        print(data_dict)
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
        # userdb_data['targetdate'] = int days to targetdate
        userdb_data['targetdate'] = (userdb_data['targetdate'] - datetime.now()).days

        userdb_data['isAvailable'] = 200

        if userdb_data['program'] == 'Weight Loss':
            userdb_data['goal'] = f"Loose {userdb_data['goal']} kg"
        else:
            userdb_data['goal'] = f"Run {userdb_data['goal']} km"
        cursor.close()
        conn.close()
        return userdb_data

    except Exception as e:
        print("error is in get_user_goal")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    


def generate_run_graph(df: pd.DataFrame):
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

def get_history_day_chart(username, date):
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
            short_url = generate_run_graph(df)
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

def get_run_stats(username, date):
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

def get_unique_dates(username, date):
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
        unique_dates = get_unique_dates(data_dict['userName'], data_dict['date'])
        graph_url, slected_date = get_history_day_chart(data_dict['userName'], data_dict['date'])
        distance, volume, duration = get_run_stats(data_dict['userName'], data_dict['date'])
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
    
def get_best_run(username):
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
        return data[0][1]
    except Exception as e:
        print("error is in get_best_run")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def get_last_run(username):
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
        return data[0][1]
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
        
        quote = get_quote()
        days_into_goal, total_days = get_days_into_goal(data_dict['userName'])
        pie_chart_url = get_day_2_goal_chart(days_into_goal=days_into_goal, total_days=total_days)
        bar_chart_url = get_month_overview_chart(data_dict['userName'])
        best_run = get_best_run(data_dict['userName'])
        last_run = get_last_run(data_dict['userName'])

        # return data as json
        data = {"quote": quote, "pie_chart_url": pie_chart_url, "bar_chart_url": bar_chart_url, "best_run": best_run, "last_run": last_run}
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
