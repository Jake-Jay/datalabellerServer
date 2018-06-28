#!/usr/local/bin/python3

from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
from config import config

app = Flask(__name__)

# ---- Not important (test function) - returns all 
@app.route('/', methods=['GET'])
def index():
    with connect() as conn:
        stmt = """SELECT DISTINCT training_set.training_set_id, "label" 
                FROM labels, training_set where labels.training_set_id = training_set.training_set_id;"""
        result = jsonify( query( conn, stmt ) )
    return result

# ---- Retreive an unlabelled image using its image ID
@app.route('/pattern/unlabelled/<int:pattern_id>', methods=['GET'])
def unlabelled(pattern_id):
    with connect() as conn:
        stmt = 'SELECT mime_type FROM pattern WHERE pattern_id=%d' %pattern_id
        result =  query(conn, stmt)
        print( result )
        if result == []:
            return( jsonify({'error':'pattern not found'}))
        else:            
            return( jsonify(result))


# ---- Add a potential label to a training set
@app.route('/label/add_label/<int:training_set>', methods=['POST', 'GET'])
def addPotentialLabel(training_set):
    if request.method == 'POST':
        if request.form: 
            newLabel = request.form.get('label')
            with connect() as conn:
                stmt = 'INSERT INTO labels("label", training_set_id) VALUES( \'{0}\', {1});'.format( newLabel, training_set )
                insert(conn, stmt)    
                print(stmt)
            return(jsonify({'Label': '%s' %newLabel}))
        else:
            return( jsonify({'error': 'invalis request'}))
    else:
        return( jsonify({'error': 'incorrect method'})) 
    

# @app.route('/pattern/<int:pattern_id>/label', methods=['POST'])
# def label(pattern_id):
    # { 'label': 'dog', 'imea': '7q26rimq4y' }
    #Request.data
    # pass

# ---- Query function (also closes cursor connection)
def query(conn, stmt):
    # create a cursor which is used for select statements
    with conn.cursor(cursor_factory = RealDictCursor) as cur:
        cur.execute(stmt)
        result = cur.fetchall()
        return(result)

def insert(conn, stmt):
    with conn.cursor(cursor_factory = RealDictCursor) as cur:
        cur.execute(stmt)        
    

# ---- Returns a conection object to the Postgress DB
def connect():
    """ Connect to the PostgreSQL database server """
    try:
        # read connection parameters from the .ini file
        params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        return(conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
 
if __name__ == '__main__':
    app.run(debug=True)
