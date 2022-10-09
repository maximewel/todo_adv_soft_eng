# todo_adv_soft_eng
Todo app, simple introduction project required to pass in order to take the advanced software engineering class

# Project

## Technology
The goal of this project is to iterate over a basic todo API built with aiohttp. A testing module is provided. This testing module attacks the API and provides the results of the test.
* The API is iterated over the simple aiohttp project (minimal)
* The database is a mysql local instance (no sqlite)
* The ORM used in the middle is sqlAlchemy

## Structure
This is a first try at aiohttp. Having worked with frameworks such as Laravel or the Django Rest Framework (DRF), this project is made with the separation (MVC-oriented) in mind:
* The main configuration / routers setup is all done in the *app.py* module
* The controllers (respectively *tags.py* and *todo.py*) implement the functions that conntrol the request from the view
* The models (Tag and Todo in *models.py*, with the intermediate relationship table *todo_tag*) act as light data classes

# Utilisation
This section explains how to setup the project to get it to work

## Python
This project uses a virtual environment to install the (Few) dependencies required.\
To work in a virtual environment and reduce conflicts with your python installation, prepare a python v-env:\
```python -m venv .venv```\
Activate the venv (Optional, can be different depending on your OS, adapt the venv filename - here it's .venv):\
```. ./.venv/bin/activate```\
Install the dependancies:\
```pip install -r requirements.txt```

## Database
The project requires a reachable mysql database ready to be populated.\
The tables are always checked and re-created at the start of the project. The database itself and the configuration associated with it is the only information that the app needs to know.

First, a mysql server needs to run. The easier is to have any kind of local SQL server easily accessible. This sql can also live in a docker.

If a mysql server is available, the *app.py* module has a database configuration where the information must be adapted:
```
databaseConfig = {
        "username": "root",
        "password": "root",
        "dbLocation": "localhost",
        "dbName": "todo_db"
    }
```
The minimal connection information is the username, passowrd, dblocation, and the name of the database schema where the tables will be created.\
\
**Note: If MySQL is a no-no**: This project uses the sqlAlchemy engine. Thus, by slightly adapting the code, it is possible to change the engine connection.\
The connection is initialized only once in the *app.py* module on the *create_connection* function:\
```engine = create_engine(f"mysql+pymysql://{databaseConfig['username']}:{databaseConfig['password']}@{databaseConfig['dbLocation']}/{databaseConfig['dbName']}?charset=utf8mb4")```
sqlAlchemy is compatible with a lot of different databases and the project is not built specifically for mysql, therefore it should be possible to change it to a close and more favorable database engine (mariaDb, sqlite...)

## Start !
With the python dependancies ready and the database schema open, simply start the app: ```python app.py``` and run the test. Enjoy !

# Contact
The test pass with a 100% success rate locally: 
> passes: 38    failures: 0     duration: 2.09s

But deploying without dockers (for the back-end and the database) is always tricky and can generate configuration errors. If any problem arise or you don't have the same results, don't hesitate to contact me at my unine email address.