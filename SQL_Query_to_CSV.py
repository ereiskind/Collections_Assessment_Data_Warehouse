#! /usr/local/bin/python

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


#Section: Run SQL Query
SQL_Query = input("Enter the SQL statement to run (without newlines): ")

Query_Results = pandas.read_sql(
    sql=SQL_Query,
    con=Engine
)


#Section: Save Query Results to CSV
File_Name = input("Enter the name of the file (not including path or file extension info); don't use spaces or slashes. ")
File = str(Path('.', 'data', 'SQL_Output', File_Name + '.csv'))

Query_Results.to_csv(
    path_or_buf=File,
    index=False
)