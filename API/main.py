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
                volume DECIMAL(8,2)
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

def get_day_2_goal_chart():
    try:
        config = {
            "type": 'radialGauge',
            "data": {
                "datasets": [{
                "data": [80],
                "backgroundColor": "orange",
                }]
            },
            "options": {
                "domain": [0, 100],
                "trackColor": '#f0f8ff', 
                "centerPercentage": 90,
                "centerArea": {
                "text": '80%',
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

def get_month_overview_chart():
    try:
        config = {
            "type": "bar",
            "data": {
                "labels": ["Hello world", "Test"],
                "datasets": [{
                    "label": "Foo",
                    "data": [1, 2]
                }]
            }
        }

        params = {
            'chart': json.dumps(config),
            'width': 500,
            'height': 300,
            'backgroundColor': 'white',
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
    
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")

        # add to userData where userName = data_dict['userName'] : fullName, dob, height, weight
        sql = """
        INSERT INTO goals (username, program, targetdate, goal)
        VALUES (%s, %s, %s, %s)
        """

        # Extract data from data_dict
        user_data = (
            data_dict['userName'],
            data_dict['program'],
            data_dict['targetdate'],
            data_dict['goal']
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
        df = df.iloc[::3, :]
        
        qc = QuickChart()
        qc.config = {
        "type": "line",
        "data": {
            "labels": df['datetime'].dt.strftime('%H:%M:%S').tolist(),
            "datasets": [
            {
                "label": "Inclination",
                "backgroundColor": "rgb(255, 99, 132)",
                "borderColor": "rgb(255, 99, 132)",
                "data": df['inclination'].tolist(),
                "fill": 'false'
            },
            {
                "label": "Speed",
                "fill": 'false',
                "backgroundColor": "rgb(54, 162, 235)",
                "borderColor": "rgb(54, 162, 235)",
                "data": df['speed'].tolist()
            }
            ]
        },
        "options": {
        }
        }
        short_url = qc.get_short_url()
        print(short_url)
        return short_url
        
    except Exception as e:
        print("error is in generate_run_graph")
        print(e)
        return ""

def get_history_data(username, date):
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

        df['datetime'] = pd.to_datetime(df['datetime'])

        unique_dates_list = df['datetime'].dt.strftime('%Y/%m/%d').unique()
        unique_dates_str = ','.join(unique_dates_list)

        if date == "last":
            date = unique_dates_list[-1]

        short_df = df[df['datetime'].dt.strftime('%Y/%m/%d') == date]

        url = generate_run_graph(short_df)

        
        return {"unique_dates": unique_dates_str, "graph_url": url}
    
    except Exception as e:
        print("error is in get_history_data")
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# endpoint for histroy page
@app.post("/history/")
async def history(input_string: str):
    try:
        data_dict = {pair.split(':')[0].strip(): pair.split(':')[1].strip() for pair in input_string.split(',')}
        print(data_dict)
        data = get_history_data(data_dict['userName'], data_dict['date'])
        return data
    except Exception as e:
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
        pie_chart_url = get_day_2_goal_chart()
        bar_chart_url = get_month_overview_chart()
        # return data as json
        data = {"quote": quote, "pie_chart_url": pie_chart_url, "bar_chart_url": bar_chart_url}
        print(data)
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
