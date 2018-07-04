#!/usr/local/bin/python3

from flask import Flask
import psycopg2
from config import config

""" Connect to the PostgreSQL database server """
try:
    # read connection parameters from the .ini file
    params = config()
    # connect to the PostgreSQL server
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)
except (Exception, psycopg2.DatabaseError) as error:
    print(error)

''' Put an image in '''
path = '/Users/jakepencharz/Documents/Isazi/Data Labeller/BeerImages/'
print('Opening an Image in {}'.format(path))
mypic=open('{}amstel-light.jpg'.format(path),'rb').read() 

''' Put the image into the DB '''
print('Placing into the DB')
cursor = conn.cursor()
stmt = '''
    INSERT INTO pattern("data", mime_type, training_set_id)
    SELECT {}, 'jpg', training_set_id
    FROM training_set
    where "name" = 'bottles';
    '''.format(psycopg2.Binary(mypic))
try:
    cursor.execute(stmt)
except Exception as e:
    print('Insertion unsuccesful: {}'.format(e))



conn.commit()
cursor.close()
conn.close()


