#!/usr/local/bin/python3

'''
    This script finds the images in dir: 
        ' /Users/jakepencharz/Documents/Isazi/Data Labeller/BeerImages/ '
    and adds them to the DB.
'''

from flask import Flask
import psycopg2
from config import config
from os import listdir
from os.path import isfile, join


''' Connect to the PostgreSQL database server '''
try:
    # read connection parameters from the .ini file
    params = config()
    # connect to the PostgreSQL server
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)
except (Exception, psycopg2.DatabaseError) as error:
    print(error)

''' Find all images in directory '''
path = '/Users/jakepencharz/Documents/Isazi/Data Labeller/BeerImages/'
image_list = [f for f in listdir(path) if isfile(join(path, f))]
print('Number of images in dir: {}'.format(len(image_list)) )

'''Put images into the DB '''
for i in range(0, len(image_list)):
    image = image_list[i]
    print(image)
    print('Opening {} in {}'.format( image, path ))
    mypic=open('{}{}'.format( path, image ),'rb').read() 

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


