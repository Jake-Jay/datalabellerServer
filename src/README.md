# Data Labelling Server
Server used to serve the data labelling app. Connects to a Postgres database. This is intended to be used with an 
[android application](https://github.com/Jake-Jay/dataLabellerPrototype).


## Instructions to set up:

1. Make sure that the DB is up and running
2. Change the database.ini file to allow flask to connect to the DB
3. Run labellingServer.py


## About the files:


```
labellingServer.py 
```

- This is where the API is defined for the server

- Relies on __database.ini__ and __config.py__ to connect to the DB


```
populateImages.py
```

- Connects to the DB to insert some sample images. 
  - Change the path (line 27) where the program looks for images to add your own images to the DB.


```
populateDevices.sh
```

- bash script which runs a series of curl commands to insert valid IMEIs into the DB for testing. 