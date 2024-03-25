from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import psycopg2
from datetime import datetime


app = FastAPI()

# Database connection parameters
db_params = {
    'dbname': 'SmartStrideDB',
    'user': 'hirakdesai',
    'host': 'localhost',
    'password': '',
}


@app.post("/insert_run_data/")
async def insert_run_data(input_string: str):
    try:
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
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        quote = get_quote()
        # return data as json
        data = {"quote": quote}
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
