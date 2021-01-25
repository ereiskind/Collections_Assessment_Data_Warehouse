#! /usr/local/bin/python
import logging
from pathlib import Path
import json
import csv
import os
import mysql.connector
from sqlalchemy import create_engine
import pandas
from pandas._testing import assert_frame_equal
import data.Database_Credentials as Database_Credentials
from helpers.Create_Master_Report_Dataframes import Create_Dataframe


#Section: Establish Prerequisites for Script Execution
#Subsection: Set Up Logging
# Status/progress checks are set to output at INFO level, activities performed by requests module output without logging statement at DEBUG level
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
# logging.disable(logging.DEBUG) # Uncomment to hide logging output for actions performed by requests module
# logging.disable(logging.CRITICAL) # Uncomment to hide all logging output

#Subsection: Create Error_Log
# This is a log for all of the reports that couldn't be loaded into the database for some reason
Error_Log_Location = Path('.', 'data', 'Error_Log.csv')
Error_Log_Headers = [
    "Interface", # Interface ID
    "Report", # The report that provided the data with the error--"status", "reports", and the master report abbreviations
    "Error", # The fixed-text description of the problem
        # HTTP error
        # COUNTER error
        # No reports available
        # Data already loaded into database
        # No data available
         # Unable to load into database
    "Description", # The free-text description of the problem, often with program error data
    "Dates", # The date range of the SUSHI harvest
]

if not Path.exists(Error_Log_Location):
    Write_Header = open(str(Error_Log_Location), 'a', newline='')
    CSV_Header_Writer = csv.DictWriter(Write_Header, Error_Log_Headers)
    CSV_Header_Writer.writeheader()
    Write_Header.close()

#Subsection: Create the SQLAlchemy Engine
Database = 'Collections_Assessment_Warehouse_0.1'
#ToDo: Investigate if this can be parsed from the first line of the SQL file referenced by the MySQL Dockerfile

Engine = create_engine(
    'mysql+mysqlconnector://' +
    Database_Credentials.Username + ':' +
    Database_Credentials.Password + '@' +
    Database_Credentials.Host + ':' + str(Database_Credentials.Post) + '/' +
    Database,
    echo=False # Should logging output be silenced?
)


#Section: Load JSON Files into MySQL
#Subsection: Read in Data
JSON_Files = Path('.', 'data', 'Load_to_Database')
for Folders, Subfolders, Files in os.walk(JSON_Files):
    for File in Files:
        # Files must be named {Interface_ID}.{Master_Report_Type}.json
        Interface_ID = File.split(".")[0]
        Master_Report_Type = File.split(".")[1]
        FileIO = open(JSON_Files / File) # The "/" can be used to concatenate parts of a file path provided the first item is a path object
        R5_Report = json.load(FileIO)
        FileIO.close()
        Master_Report_Dataframe = Create_Dataframe(Interface_ID, Master_Report_Type, R5_Report)
        if str(type(Master_Report_Dataframe)) == "<class 'str'>": # Meaning the dataframe couldn't be created
            Master_Report_Dataframe_Problem = dict(
                Interface = Interface_ID,
                Report = Master_Report_Dataframe.split("|")[0],
                Error = Master_Report_Dataframe.split("|")[1],
                Description = Master_Report_Dataframe.split("|")[2],
            )
            with open(str(Error_Log_Location), 'a', newline='') as Write_Row:
                Master_Report_Dataframe_Problem["Dates"] = "Taken from JSON file"
                CSV_Row_Writer = csv.DictWriter(Write_Row, Error_Log_Headers)
                CSV_Row_Writer.writerow(Master_Report_Dataframe_Problem)
            logging.info(f"Added to Error_Log: {Interface_ID}|" + Master_Report_Dataframe)
            continue
        logging.info(Master_Report_Dataframe.tail())
        Number_of_Records = Master_Report_Dataframe.shape[0]

        #Subsection: Load Dataframe into MySQL
        try:
            with Engine.connect() as Connection:
                with Connection.begin(): # This creates a SQL transaction
                    Master_Report_Dataframe.to_sql(
                        name='R5_Usage',
                        con=Engine,
                        if_exists='append',
                        chunksize=1000,
                        index=False
                    )
            
            Check_Loading = pandas.read_sql(
                sql=f'''
                    SELECT *
                    FROM (
                        SELECT * FROM R5_Usage
                        ORDER BY R5_Usage_ID DESC
                        LIMIT {Number_of_Records}
                    ) subquery
                    ORDER BY R5_Usage_ID ASC;
                ''',
                con=Engine
            ) # Reads the same number of records that were just loaded into the database from the database
            Check_Loading_Sans_PK = Check_Loading.drop(columns='R5_Usage_ID')
            # Below raises an error if the data for the last number of records equaling the number of records in Master_Report_Dataframe doesn't match that of Master_Report_Dataframe
            assert_frame_equal(Master_Report_Dataframe, Check_Loading_Sans_PK, check_dtype=False)
            logging.info(f"Successfully loaded {Master_Report_Type} for {Interface_ID} into database:\n{Check_Loading.tail()}")
        except Exception as Error_Message:
            Master_Report_Loading_Problem = dict(
                Interface = Interface_ID,
                Report = Master_Report_Type,
                Error = "Unable to load into database",
                Description = f"Dataframe didn't load into MySQL ({Error_Message})",
            )
            with open(str(Error_Log_Location), 'a', newline='') as Write_Row:
                Master_Report_Loading_Problem["Dates"] = "Taken from JSON file"
                CSV_Row_Writer = csv.DictWriter(Write_Row, Error_Log_Headers)
                CSV_Row_Writer.writerow(Master_Report_Loading_Problem)
            logging.info(f"Added to Error_Log: {Interface_ID}|{Master_Report_Type}|Unable to load into dataframe|Dataframe didn't load into MySQL ({Error_Message})")