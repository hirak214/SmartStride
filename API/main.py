from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import psycopg2
from datetime import datetime
from quickchart import QuickChart
import json
from urllib.parse import urlencode

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
        print(data_dict)
    
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        if not cursor:
            raise HTTPException(status_code=500, detail="Could not connect to the database")

        # add to userDB : userName, email, password
        cursor.execute('''INSERT INTO userDB (userName, email, password) VALUES (%s, %s, %s)''',
                       (data_dict['userName'], data_dict['email'], data_dict['password']))

        conn.commit()
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
        UPDATE userData
        SET fullName = %s, dob = %s, height = %s, weight = %s, med = %s, gender = %s, blood = %s
        WHERE userName = %s
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
        # # Connect to the PostgreSQL database
        # conn = psycopg2.connect(**db_params)
        # cursor = conn.cursor()
        # if not cursor:
        #     raise HTTPException(status_code=500, detail="Could not connect to the database")
        # # get all data from runData
        # cursor.execute("SELECT * FROM runData WHERE uid = 123")
        # data = cursor.fetchall()
        # cursor.close()
        # conn.close()

        # # convert data to a list with sublists only keep speed and inclination values and add an index
        # data = [[i, row[2], row[3]] for i, row in enumerate(data)]

        # # return data as json
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
