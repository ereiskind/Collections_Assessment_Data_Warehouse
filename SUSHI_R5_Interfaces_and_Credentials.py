#! /usr/local/bin/python

# This creates "SUSHI_R5_Interfaces_and_Credentials.csv", a table with all of the SUSHI R5 compliant interfaces listed in the database and their SUSHI credentials from "SUSHI_R5_Credentials.json".

import json
import csv
from pathlib import Path
import pandas
import mysql.connector
from sqlalchemy import create_engine
import data.Database_Credentials as Database_Credentials

#Section: Create SQLAlchemy Engine
Database = 'Collections_Assessment_Warehouse_0.1'

Engine = create_engine(
    'mysql+mysqlconnector://' +
    Database_Credentials.Username + ':' +
    Database_Credentials.Password + '@' +
    Database_Credentials.Host + ':' + str(Database_Credentials.Post) + '/' +
    Database,
    echo=False # Should logging output be silenced?
)


#Section: Create Dataframes
#Subsection: Get Data from Database
R5_SUSHI_Interfaces = pandas.read_sql(
    sql='''
        SELECT Interface_ID, Interface_Name
        FROM Interfaces
        WHERE SUSHI_R5_Compliant = 1;
    ''',
    con=Engine
)

#Subsection: Get Data from JSON
with open(str(Path('.', 'data', 'SUSHI_R5_Credentials.json'))) as JSON_File:
    Data_File = json.load(JSON_File)
    Data = []
    for Vendor in Data_File:
        for Interface in Vendor["interface"]:
            Record = dict(
                Interface_ID = Interface["name"]
            )
            if Interface["statistics"]["user_id"] != "":
                Record["Customer ID"] = Interface["statistics"]["user_id"]
            if Interface["statistics"]["user_password"] != "":
                Record["Requestor ID"] = Interface["statistics"]["user_password"]
            if Interface["statistics"]["online_location"] != "":
                Record["URL"] = Interface["statistics"]["online_location"]
            if Interface["statistics"]["delivery_address"] != "":
                Record["API Key"] = Interface["statistics"]["delivery_address"]
            if Interface["statistics"]["locally_stored"] != "":
                Record["SUSHI Platform Code"] = Interface["statistics"]["locally_stored"]
            
            Data.append(Record)
R5_SUSHI_Credentials = pandas.DataFrame(Data)


#Section: Join Dataframes
R5_Interfaces = R5_SUSHI_Interfaces.set_index('Interface_ID').join(R5_SUSHI_Credentials.set_index('Interface_ID'))
File = str(Path('.', 'data', 'SQL_Output', 'SUSHI_R5_Interfaces_with_Credentials.csv'))
R5_Interfaces.to_csv(
    path_or_buf=File,
    index=False
)