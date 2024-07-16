import os 
import json
import logging
from flask import Flask, request, Response
import psycopg2
from psycopg2.extras import execute_values


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def connect_to_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

@app.route('/', methods=['POST'])
def webhook_recibe_data():
    data = request.get_json()
    logging.debug(data)
    
   
    values = [(data['orderbook_timestamp'], data['book'], data['bids'], data['asks'], data['spread'])]
    logging.debug(values)
    
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO spread_books (orderbook_timestamp, book, bid, ask, spread) VALUES %s
        """
        
        execute_values(cursor, insert_query, values)
        conn.commit()
        
        logging.debug("Data inserted successfully into the database")
    except Exception as e:
        logging.error(f"Error inserting data into the database: {e}")
        return Response(json.dumps({"message":"error"}), mimetype='application/json',status=500)
    
    
    finally:
        cursor.close()
        conn.close()
    return Response(json.dumps({"message":"Ok"}), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
