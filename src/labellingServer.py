#!/usr/local/bin/python3

from flask import Flask, jsonify, request, make_response, Response
import psycopg2
from psycopg2.extras import RealDictCursor
from config import config
import base64

app = Flask(__name__)

# ---- Not important (test function) - returns all labels for each of the training sets grouped by training set
@app.route('/', methods=['GET'])
def index():
    with connect() as conn:
        stmt = '''
            SELECT DISTINCT training_set.training_set_id, training_set."name" as Training_Set, "label" 
            FROM labels, training_set 
            WHERE labels.training_set_id = training_set.training_set_id
            ORDER BY training_set.training_set_id;
            '''
        result = jsonify( query( conn, stmt ) )
    return result

# ---- User recieves an unlabelled image with associated possible labels.
@app.route('/api/pattern/unlabelled', methods=['GET'])
def unlabelled():
    with connect() as conn:
        stmt = '''
            WITH counts AS (
                SELECT pattern_id as p_id, count(1) as occurrences
                FROM phone_pattern_label
                GROUP BY pattern_id
            )
            SELECT *
            FROM pattern AS pp
            LEFT OUTER JOIN counts as cc
            ON pp.pattern_id = cc.p_id
            WHERE cc.occurrences < 3 or cc.occurrences IS NULL
			OFFSET floor(random()* (SELECT count(*)FROM pattern))
			LIMIT 1;
            '''
        pattern_result =  query(conn, stmt)
        if pattern_result == []:
            return( jsonify({'error':'pattern not found'}))

        training_set_id =int( pattern_result[0]["training_set_id"] )
        stmt = '''
            SELECT label FROM labels
            WHERE training_set_id = {}
            '''.format(training_set_id)
        label_result = query(conn, stmt)
        if label_result == []:
            return( jsonify({'error':'no labels found'}))
        else:            
            return( jsonify({
                'pattern_id': pattern_result[0]['pattern_id'],
                'data': base64.encodebytes(pattern_result[0]['data']).decode("utf-8"),
                'mime_type': pattern_result[0]['mime_type'],
                'labels': list(l['label'] for l in label_result)
             }) )

# ---- User sends back proposed label. 
# * Should send back the users imei, label. 
# * Requires knowing the image ID and the potential labels
@app.route('/api/pattern/<int:pattern_id>/label', methods=['POST'])
def label(pattern_id):
    
    with connect() as conn:
        # Perform data quality check
        dev_num = request.json['device_number']
        if( recordExists(conn, 'phones', 'device_number', dev_num) == False ):
            return make_response('Device is not registered \n', 400)  
        
        label = request.json['label']
        if ( recordExists(conn, 'labels', 'label', label) == False ):
            return make_response('Record is  not found \n', 400 )

        stmt = '''
            INSERT INTO phone_pattern_label (pattern_id, phone_id, label_id)
            SELECT pp.pattern_id, ph.phone_id, ll.label_id
            FROM pattern as pp
            INNER JOIN phones as ph
            ON pp.pattern_id = {}
            AND ph.device_number = \'{}\'
            INNER JOIN labels as ll
            ON ll.label = \'{}\'
            '''.format(pattern_id, dev_num, label)
        insert(conn, stmt)
    return make_response('', 200)


# ---- Function to add phones into the phone table
@app.route('/api/register', methods=['POST'])
def register():
    imei = request.json['device_number']    

    if( validateDevice(imei) ):
        with connect() as conn:
            if( recordExists(conn, 'phones', 'device_number', imei)):
                return make_response('Phone is already registered \n', 400)
            stmt = '''
                INSERT INTO phones(device_number)
                VALUES({})
                '''.format(imei)
            insert(conn, stmt)
            return make_response('Valid and unique imei - device registered succesfully \n', 200)         
    else:
        return make_response('Invalid imei \n', 500)
    


# ---- Add a potential label to a training set
# * Probably shouldnt be part of the API. Good way to test the server's communication with a database
@app.route('/management/add_label/<int:training_set>', methods=['POST', 'GET'])
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
    

# ------------------------------------------------------------------------------------
# Functions not bound to routes:
# ------------------------------------------------------------------------------------

# ---- Query function for a general SELECT  (also closes cursor connection)
def query(conn, stmt):
    # create a cursor which is used for select statements
    with conn.cursor(cursor_factory = RealDictCursor) as cur:
        cur.execute(stmt)
        result = cur.fetchall()
        return( result )        

# ---- For general insert statements
def insert(conn, stmt):
    with conn.cursor(cursor_factory = RealDictCursor) as cur:
        try:
            cur.execute(stmt)    
        except Exception as e:
            print('Insertion unsuccesful \n{}'.format(e))

# ---- Check if a record exists in the DB
def recordExists(conn, table, key, value):
    with conn.cursor() as cur:
        stmt = '''
            SELECT 1
            FROM {}
            WHERE {} = '{}'
            '''.format(table, key, value)
        cur.execute(stmt) 
        ans = cur.fetchone()       
        print(stmt)
        if(ans == None):
            return False
        else:
            return True

    
# ---- Validate imei - should contain 15 charachters (other rules?)
def validateDevice(imei):
    if (len(imei) == 15):
        return True
    else:
        return False

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
