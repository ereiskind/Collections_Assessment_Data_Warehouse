#! /usr/local/bin/python
#API repository: https://app.swaggerhub.com/apis/COUNTER/counter-sushi_5_0_api/1.0.0

import logging
from pathlib import Path
import json
import csv
import time
import os
import sys
from datetime import date
from datetime import datetime
import requests
from requests import HTTPError, Timeout
import pyinputplus
import pandas
import mysql.connector
from sqlalchemy import create_engine
from dateutil import parser
from dateutil.rrule import rrule, MONTHLY
import data.Database_Credentials as Database_Credentials
from helpers.SUSHI_R5_API_Calls import Single_Element_API_Call
from helpers.SUSHI_R5_API_Calls import Master_Report_API_Call
from helpers.Create_Master_Report_Dataframes import Create_Dataframe


#Section: Set Up Logging
# Status/progress checks are set to output at INFO level, activities performed by requests module output without logging statement at DEBUG level
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
# logging.disable(logging.DEBUG) # Uncomment to hide logging output for actions performed by requests module
# logging.disable(logging.CRITICAL) # Uncomment to hide all logging output


#Section: Functions
#Subsection: Error Handling
def Handle_Status_Check_Problem(Source, Message, Error = None, Type = "alert"):
    """Handles results of SUSHI API call for status that countain an error or alert by presenting the message and asking if the interface's stats should be collected.
    
    #ToDo: Potentially offer option to try again if message severity is "fatal"

    Arguments:
        Source {string} -- the JSON name for the current interface
        Message {string} -- the SUSHI error message or the SUSHI alert value
        Error {string} -- the SUSHI error severity; default None for SUSHI alerts
        Type {int or string} -- the SUSHI error code; default "Alert" for SUSHI alerts
    
    Returns:
        None
        Boolean -- if keyword continue is triggered
    """
    if len(Message) == 0: # Some interfaces always include the key for a status check problem, even if none exists; this keeps the messagebox from being triggered in those instances
        return False
    # Combined, below tests if "Type" is a series of digits, meaning that it's an error code
    if str(type(Type)) == "<class 'int'>":
        Type = "error " + str(Type)
    elif Type.isnumeric():
        Type = "error " + Type
    Response_to_Problem = pyinputplus.inputBool(f"The status check for {Source} contained the following {Type}:\n\n{Message}\n\nShould the usage for this platform be collected? Type \"True\" for yes or \"False\" for no to answer. ")
    if not Response_to_Problem: # This code block needs to run if the answer to the above is no, which produces the Boolean False
        Problem_Message = f"Canceled collection from interface with {Type}: {Message}"
        Capture_Problem = dict(
            Interface = Source,
            Type = "status",
            Details = Problem_Message,
        )
        Error_Log.append(Capture_Problem)
        logging.info(f"Added to Error_Log: {Source}|status|{Problem_Message}")
        return True
    return False


def Handle_Exception_Master_Report(Source, Report, Exception_List, Load_Report_Items = False):
    """Handles results of a SUSHI API call for a master report that is or contains exceptions.
    
    The function parses the list of exceptions, remaking each exception into a string. Then, if the response contained a Report_Items section, it asks if the usage should be loaded into the database. Finally, if the usage isn't to be loaded into the database, the report is added to Error_Log and the corresponding log statement is output to the terminal. Note that because there are two different possible parmeters for including parent details, "include_parent_details" and "include_component_details", which an item report might use, most item reports will require handling through this function.
    #ToDo: Skip over the messagebox if all of the exceptions are 3050 (parameter not available)
    
    Arguments:
        Source {string} -- the JSON name for the current interface
        Report {string} -- the abbreviation for the current master report
        Exception_List {list} -- the list of exception dictionaries
    
    Keyword Arguments:
        Load_Report_Items {bool} -- if the SUSHI API response contains the Report_Items key (default: {False})
    
    Returns:
        Boolean -- if keyword continue is triggered
    """
    List_of_Exceptions = []

    for SUSHI_Exception in Exception_List:
        # Combined, below confirms SUSHI_Exception["Code"] is a series of digits, meaning that it's an exception code
        if str(type(SUSHI_Exception["Code"])) == "<class 'int'>":
            Code = "exception " + str(SUSHI_Exception["Code"])
        elif SUSHI_Exception["Code"].isnumeric():
            Code = "exception " + SUSHI_Exception["Code"]

        try:
            List_of_Exceptions.append(f"{Code}: {SUSHI_Exception['Message']} ({SUSHI_Exception['Data']})")
        except:
            List_of_Exceptions.append(f"{Code}: {SUSHI_Exception['Message']}")

    if Load_Report_Items: # Meaning that there's data that could be loaded--messagebox changes Boolean to if that data should be loaded
        print(f"The {Report} for {Source} contained the following exception(s):\n\n")
        for Exception_Raised in List_of_Exceptions:
            print(Exception_Raised + "\n")
        Load_Report_Items = pyinputplus.inputBool("\nShould this report be added to the database? Type \"True\" for yes or \"False\" for no to answer. ")
    if not Load_Report_Items: # This code block needs to run if the answer to the above is no, which produces the Boolean False
        Problem_Message = f"Cancelled collection because of exception(s) {'|'.join(List_of_Exceptions)}"
        Capture_Problem = dict(
            Interface = Source,
            Type = Report,
            Details = Problem_Message,
        )
        Error_Log.append(Capture_Problem)
        logging.info(f"Added to Error_Log: {Source}|{Report}|{Problem_Message}")
        return True
    return False


def API_Download_Not_Empty():
    """Prints a message indicating that the "API_Download" folder isn't empty and that it needs to be for the program to work properly, then exits the program.
    
    Returns:
        None
    """
    print("The \"API_Downloads\" folder has something in it; it must be empty for this program to work properly. Please remove everthing from that folder, then try to run this program again.")
    sys.exit()


#Subsection: Database Interactions
'''
def Execute_SQL_Statement(SQLStatement, DB):
    """Executes a SQL statement using a PyMySQL connection object.
    
    This function fully encapsulates the execution of a SQL statement using PyMySQL, creating a connection object, creating a cursor based off the connection object, executing the statement, committing the changes, and closing the connection.
    #Alert: This function is currently not used; any adjustments that need to be made to accommodate manual manipulations or retrieval of the data through SQL should be done in the context of the Flask app that will serve as the UI.
    
    Arguments:
        SQLStatement {string} -- the SQL statement
        DB {string} -- name of the MySQL database the statement will be executed in
    
    Returns:
        None
    """
    Connection = pymysql.connect(
        host=Database_Credentials.Host,
        user=Database_Credentials.Username,
        password=Database_Credentials.Password,
        db=Database
    )
    
    Cursor = Connection.cursor()
    Cursor.execute(SQLStatement)
    Connection.commit()
    Connection.close()
'''


#Section: Establish Prerequisites for Script Execution
#Subsection: Confirm Folder "API_Download" is Empty
API_Download_Path = r"/root/Collections_Assessment_Data_Warehouse/data/API_Download"
#Alert: The above path is absolute because the deployment of the repository within a Docker container guarantees uniform placement in the overall file structure. To deploy using a method other than the one described in Runtime_Environment.md, change this file path.
for Folder, Subfolder, Files in os.walk(API_Download_Path):
    if len(Files) > 0:
        API_Download_Not_Empty()
    elif len(Subfolder) > 0:
        API_Download_Not_Empty()

#Subsection: Initialize List for Error_Log
Error_Log = []
# This is a log for all of the reports that couldn't be loaded into the database for some reason
# Columns:
    # Interface: interface ID
    # Report: the report that provided the data with the error--"status", "reports", and the master report abbreviations
    # Error: the fixed-text description of the problem
        # HTTP error
        # COUNTER error
        # No reports available
        # Data already loaded into database
        # No data available
        # Unable to load into database
    # Description: the free-text description of the problem, often with program error data

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


#Section: Collect Information Needed for SUSHI Call
# Later, this will be replaced with a call to the Alma API--see Credentials_Through_Alma_API.py
SUSHI_R5_Credentials_Path = str(Path('.', 'data', 'SUSHI_R5_Credentials.json'))
with open(SUSHI_R5_Credentials_Path) as JSON_File:
    SUSHI_Data_File = json.load(JSON_File)
    SUSHI_Data = []
    for Vendor in SUSHI_Data_File:
        for Interface in Vendor["interface"]:
            Set = dict(
                URL = Interface["statistics"]["online_location"],
                JSON_Name = Interface["name"],
                customer_id = Interface["statistics"]["user_id"]
            )
            if Interface["statistics"]["user_password"] != "":
                Set["requestor_id"] = Interface["statistics"]["user_password"]
            if Interface["statistics"]["delivery_address"] != "":
                Set["api_key"] = Interface["statistics"]["delivery_address"]
            if Interface["statistics"]["locally_stored"] != "":
                Set["platform"] = Interface["statistics"]["locally_stored"]
            SUSHI_Data.append(Set)
            logging.info(f"Credentials for {SUSHI_Data[-1]['JSON_Name']} added to SUSHI_Data")


#Subsection: Enter Date Range for Stats
Begin_Date = pyinputplus.inputDate(
    "Please enter the year and month for the first month of stats collection. The month must be two digits and the year must be four digits. ",
    formats=[
        '%Y%m', # yyyymm
        '%m-%Y', # mm-yyyy
        '%m/%Y', # mm/yyyy
        '%Y-%m', # yyyy-mm
        '%Y/%m', # yyyy/mm
    ]
)

End_Date = date.min # This ensures that the while loop letting the user set End_Date runs at least once
while End_Date < Begin_Date:
    End_Date = pyinputplus.inputDate(
        f"Please enter the year and month for the last month of stats collection; this must be after {Begin_Date.strftime('%Y-%m')}. The month must be two digits and the year must be four digits. ",
        formats=[
            '%Y%m', # yyyymm
            '%m-%Y', # mm-yyyy
            '%m/%Y', # mm/yyyy
            '%Y-%m', # yyyy-mm
            '%Y/%m', # yyyy/mm
        ]
    )


#Section: Make API Calls for Status and Reports
for SUSHI_Call_Data in SUSHI_Data:
    # These list comprehensions create another dictionary with just the content needed for the URL's query string--two are used because combining the Boolean expressions wasn't working
    #ToDo: Try to combine Boolean expressions at end for a single list comprehension
    Credentials = {key: value for key, value in SUSHI_Call_Data.items() if key != "URL"}
    Credentials = {key: value for key, value in Credentials.items() if key != "JSON_Name"}
    logging.info(f"Making API calls starting with {SUSHI_Call_Data['URL']}")

    #Subsection: Determine SUSHI Availability
    Credentials_String = "&".join("%s=%s" % (k,v) for k,v in Credentials.items())
    Status_Check = Single_Element_API_Call("status", SUSHI_Call_Data["URL"], Credentials_String)
    if str(type(Status_Check)) == "<class 'str'>": # Meaning the API call returned an error
        Status_Check_Problem = dict(
            Interface = SUSHI_Call_Data["JSON_Name"],
            Type = Status_Check.split("|")[0],
            Details = Status_Check.split("|")[1],
        )
        Error_Log.append(Status_Check_Problem)
        logging.info(f"Added to Error_Log: {SUSHI_Call_Data['JSON_Name']}|" + Status_Check)
        continue

    #Subsection: Check if Status_Check Returns COUNTER Error
    # https://www.projectcounter.org/appendix-f-handling-errors-exceptions/ has list of COUNTER error codes
    try: # Status_Check is JSON-like dictionary with Report_Header and information about the error
        Status_Check_Error = Status_Check["Exception"]["Severity"]
        if Handle_Status_Check_Problem(SUSHI_Call_Data["JSON_Name"], Status_Check["Exception"]["Message"], Status_Check_Error, Status_Check["Exception"]["Code"]):
            continue
    except:
        try: # Status_Check is JSON-like dictionary with nothing but information about the error
            Status_Check_Error = Status_Check["Severity"]
            if Handle_Status_Check_Problem(SUSHI_Call_Data["JSON_Name"], Status_Check["Message"], Status_Check_Error, Status_Check["Code"]):
                continue
        except: #Alert: Not known if functional
            try: # Status_Check is a list containing a JSON-like dictionary with nothing but information about the error
                Status_Check_Error = Status_Check[0]["Severity"]
                if Handle_Status_Check_Problem(SUSHI_Call_Data["JSON_Name"], Status_Check[0]["Message"], Status_Check_Error, Status_Check[0]["Code"]):
                    continue
            except: # If the status check passes, a KeyError is returned
                pass # Before the status check is declared a success, it needs to be checked for COUNTER Alerts as well
    
    #Subsection: Check if Status_Check Returns COUNTER Alert
    try:
        Status_Check_Alert = Status_Check["Alerts"]
        if Handle_Status_Check_Problem(SUSHI_Call_Data["JSON_Name"], Status_Check_Alert):
            continue
    except:
        logging.info(f"Status check successful: {Status_Check}")

    #Subsection: Get List of R5 Reports Available
    Credentials_String = "&".join("%s=%s" % (k,v) for k,v in Credentials.items())
    Available_Reports = Single_Element_API_Call("reports", SUSHI_Call_Data["URL"], Credentials_String)
    if str(type(Available_Reports)) == "<class 'str'>": # Meaning the API call returned an error
        Available_Reports_Problem = dict(
            Interface = SUSHI_Call_Data["JSON_Name"],
            Type = Status_Check.split("|")[0],
            Details = Status_Check.split("|")[1],
        )
        Error_Log.append(Available_Reports_Problem)
        logging.info(f"Added to Error_Log: {SUSHI_Call_Data['JSON_Name']}|" + Status_Check)
        continue
    # This creates a list of all the reports offered by a platform excluding the consortium reports offered by Silverchair, which have a Report_ID value of "Silverchair:CR_??"
    Available_Reports_List = []
    for Report in Available_Reports:
        if "Silverchair:CR" not in Report["Report_ID"]:
            Available_Reports_List.append(Report["Report_ID"])
    
    Available_Master_Reports = [] # This list will contain the dictionaries from the JSON for the master reports available on the platform, which will be the only reports pulled
    for Report in Available_Reports:
        if "_" not in Report["Report_ID"]:
            Available_Master_Reports.append(Report)
    if Available_Master_Reports == []:
        No_Reports_Problem = dict(
            Interface = SUSHI_Call_Data["JSON_Name"],
            Type = "reports",
            Details = "No master reports available",
        )
        Error_Log.append(No_Reports_Problem)
        logging.info("Added to Error_Log: " + SUSHI_Call_Data["JSON_Name"] + "|reports|No master reports available")
        continue

    Captured_By_Master_Reports = []
    Not_Captured_By_Master_Reports = []
    for Master_Report in Available_Master_Reports:
        [Captured_By_Master_Reports.append(Report) for Report in Available_Reports_List if Report[0:2] == Master_Report["Report_ID"]]
    [Not_Captured_By_Master_Reports.append(Report) for Report in Available_Reports_List if Report not in Captured_By_Master_Reports]
    if len(Not_Captured_By_Master_Reports) > 0:
        for Report in Not_Captured_By_Master_Reports:
            # The number of these is small, and custom reports will be included in this number, so the list will need to be reviewed manually
            Extra_Report_Problem = dict(
                Interface = SUSHI_Call_Data["JSON_Name"],
                Type = Report,
                Details = "Standard report based on master report not offered",
            )
            Error_Log.append(Extra_Report_Problem) 
        logging.info(f"Added to Error_Log: {SUSHI_Call_Data['JSON_Name']}|{Report}|Standard report based on master report not offered")
    
    logging.info(f"Master report list collection successful: {len(Available_Master_Reports)} reports")

    #Section: Make API Calls for Individual Master Reports
    #Subsection: Add Date Parameters
    Credentials["begin_date"] = Begin_Date.strftime('%Y-%m')
    Credentials["end_date"] = End_Date.strftime('%Y-%m')

    #Subsection: Add Parameters Specific to Type of Master Report
    for Master_Report in Available_Master_Reports:
        Master_Report_Type = Master_Report["Report_ID"].upper()
        
        #Subsection: Check If Statistics Have Already Been Collected for the Given Interface and Report for Any Months in the Given Range
        Months_in_Range = list(rrule(
            freq = MONTHLY,
            dtstart = parser.isoparse(Credentials["begin_date"]),
            until = parser.isoparse(Credentials["end_date"])
        )) # rrule generates a object that can be unpacked into a list of datetime objects representing dates and/or times occurring on a recurring schedule
        #Note: The list doesn't seem to overwrite itself at each iteration, which is fine as the values in it will be the same every time the Master_Reports loop is run
        
        Usage_in_DB = []
        for Month in Months_in_Range:
            Previous_Load_Check = pandas.read_sql(
                sql=f'''
                    SELECT COUNT(*) AS 'Value'
                    FROM R5_Usage
                    WHERE Interface = {SUSHI_Call_Data['JSON_Name']}
                    AND R5_Month = '{Month}'
                    AND Report = '{Master_Report_Type}';
                ''', #ToDo: Determine if "Month" needs type juggling and/or to be explicitly identified as the first of the month
                con=Engine
            )
            Previous_Load_Check = Previous_Load_Check.iloc[0]['Value'] # This changes the dataframe with a single value to a numpy.int64 data type
            if Previous_Load_Check > 0:
                Usage_in_DB.append(Month)
        
        if len(Usage_in_DB): # Triggers if list of month with usage already in database isn't empty
            #ToDo: Increase sophistication of parsing dates to make running partial date ranges possible
            Usage_in_DB_Months = []
            for Month_Present in Usage_in_DB:
                Usage_in_DB_Months.append(Month_Present.strftime('%Y-%m'))
            Usage_in_DB_Months = ", ".join(Usage_in_DB_Months)
            Load_Usage_Data = pyinputplus.inputBool(f"The {Master_Report_Type} for {SUSHI_Call_Data['JSON_Name']} for the month(s) of {Usage_in_DB_Months} are already in the database; should the loading of the usage just collected, which also includes those dates, be skipped? Type \"True\" for yes or \"False\" for no to answer. ")
            if Load_Usage_Data:
                Duplicated_Usage_Data_Problem = dict(
                    Interface = SUSHI_Call_Data['JSON_Name'],
                    Type = Master_Report_Type,
                    Details = f"Data for this report for the months {Usage_in_DB_Months} was already in the database",
                )
                Error_Log.append(Duplicated_Usage_Data_Problem)
                logging.info(f"Added to Error_Log: {SUSHI_Call_Data['JSON_Name']}|{Master_Report_Type}|Data for this report for the months {Usage_in_DB_Months} was already in the database")
                continue

        #Subsection: Add Parameters Specific to Type of Master Report
        # If the parameters for showing parent details in Item Master Report are in other master reports, an error message saying the parameter's been ignored is included in the report header; the below takes them out of the query
        if "include_parent_details" in Credentials:
            del Credentials["include_parent_details"]
            del Credentials["include_component_details"]

        # This cycles through each of the master reports offered by the platform, adding the URL query parameters needed to get the most granular version of the given master report
        if Master_Report_Type == "PR":
            Credentials["attributes_to_show"] = "Data_Type|Access_Method"
        elif Master_Report_Type == "DR":
            Credentials["attributes_to_show"] = "Data_Type|Access_Method"
        elif Master_Report_Type == "TR":
            Credentials["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type|Section_Type"
        elif Master_Report_Type == "IR":
            Credentials["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type"
            # If either of the below is in the parameters but isn't used by the platform, it's presence will add a 3050 warning to the JSON; since there's no good way to tell which IRs use which parameter, using both and handling the error in Handle_Exception_Master_Report is the best option
            Credentials["include_parent_details"] = "True"
            Credentials["include_component_details"] = "True"
        else:
            logging.info(f"{SUSHI_Call_Data['JSON_Name']} contained a {Master_Report['Report_Name']}. Work out further report type handling.") # This message shouldn't ever appear
            continue
        logging.info(f"Ready to call {SUSHI_Call_Data['URL']} for {Master_Report_Type}.")

        #Subsection: Make API Call for Master Report
        Credentials_String = "&".join("%s=%s" % (k,v) for k,v in Credentials.items())
        Master_Report_Response = Master_Report_API_Call(Master_Report_Type, SUSHI_Call_Data["URL"], Credentials_String)
        if str(type(Master_Report_Response)) == "<class 'str'>": # Meaning the API call returned an error
            Master_Report_Response_Problem = dict(
                Interface = SUSHI_Call_Data["JSON_Name"],
                Type = Master_Report_Response.split("|")[0],
                Details = Master_Report_Response.split("|")[1],
            )
            Error_Log.append(Master_Report_Response_Problem)
            logging.info(f"Added to Error_Log: {SUSHI_Call_Data['JSON_Name']}|" + Master_Report_Response)
            continue

        #Subsection: Handle Master Reports with Exceptions
        try: # Master_Report_Response is JSON-like dictionary with top-level key of "Report_Header" that includes the key "Exceptions"
            Master_Report_Exceptions = Master_Report_Response["Report_Header"]["Exceptions"]
            if "Report_Items" in Master_Report_Response:
                if Handle_Exception_Master_Report(SUSHI_Call_Data["JSON_Name"], Master_Report_Type, Master_Report_Exceptions, True):
                    continue
            else:
                if Handle_Exception_Master_Report(SUSHI_Call_Data["JSON_Name"], Master_Report_Type, Master_Report_Exceptions):
                    continue
        except:
            try: # Master_Report_Response is JSON-like dictionary containing only the content of a single Exception
                if "Code" in Master_Report_Response:
                    if Handle_Exception_Master_Report(SUSHI_Call_Data["JSON_Name"], Master_Report_Type, list(Master_Report_Response)):
                        continue
            except:
                # Based on observed close-to-standard behavior, an interface could return a list of multiple Exception dictionaries, which JSON_to_Python_Data_Types would handle as an error, directing it to the Error_Log list. If that happens, error handling for that situation may be better handled within the JSON_to_Python_Data_Types function.
                pass # A SUSHI JSON without an "Exceptions" key will return a KeyError for the above

        logging.info(f"API call to {SUSHI_Call_Data['URL']} for {Master_Report_Type} successful: {len(Master_Report_Response['Report_Items'])} resources")

        #Subsection: Return Notice for Empty Reports
        # These cause problems when passed into the dataframe creation functions, so they're handled here; more investigation is needed, however, as an empty report can be either correct behavior (some interfaces seem to offer DR even though there aren't any databases on the constituent platform(s)/user interface(s)) or a problem
        #ToDo: Build in some sort of checking to determine if the lack of Report_Items is problematic
        if len(Master_Report_Response["Report_Items"]) == 0:
            Master_Report_Items_Problem = dict(
                Interface = SUSHI_Call_Data["JSON_Name"],
                Type = Master_Report_Type,
                Details = f"{Master_Report_Type} empty",
            )
            Error_Log.append(Master_Report_Items_Problem)
            logging.info(f"Added to Error_Log: {SUSHI_Call_Data['JSON_Name']}|{Master_Report_Type}|{Master_Report_Type} empty")
            continue
        #Alert: Should DRs with a single database where the metrics are identical to the PR (see Project MUSE as example) be captured and silently disposed of here as well?


        #Section: Load Master Report into MySQL
        #Subsection: Read Master Report into Dataframe
        Master_Report_Dataframe = Create_Dataframe(SUSHI_Call_Data['JSON_Name'], Master_Report_Type, Master_Report_Response)
        if str(type(Master_Report_Dataframe)) == "<class 'str'>": # Meaning the dataframe couldn't be created
            Master_Report_Dataframe_Problem = dict(
                Interface = SUSHI_Call_Data["JSON_Name"],
                Type = Master_Report_Dataframe.split("|")[0],
                Details = Master_Report_Dataframe.split("|")[1],
            )
            Error_Log.append(Master_Report_Dataframe_Problem)
            logging.info(f"Added to Error_Log: {SUSHI_Call_Data['JSON_Name']}|" + Master_Report_Dataframe)
            continue
        logging.info(Master_Report_Dataframe.head())

        #Subsection: Load Dataframe into MySQL
        #Alert: This exception handling won't necessarily pick up on a failure to load data into MySQL, but that problem should be resolved
        try:
            with Engine.connect() as Connection:
                with Connection.begin(): # This creates a SQL transaction
                    Master_Report_Dataframe.to_sql(
                        name='R5_Usage',
                        con=Engine,
                        if_exists='append',
                        index=False
                    )
            
            Check_Loading = pandas.read_sql(
                sql='''SELECT * FROM R5_Usage;''',
                con=Engine
            )
            logging.info(f"Successfully loaded {Master_Report_Type} for {SUSHI_Call_Data['JSON_Name']} into database:\n{Check_Loading.tail()}")
        except Exception as Error_Message:
            #Alert: (mysql.connector.errors.OperationalError) 2055: Lost connection to MySQL server at 'database:3306', system error: 32 Broken pipe
            #ToDo: Above error occurred for some larger reports
            Master_Report_Loading_Problem = dict(
                Interface = SUSHI_Call_Data["JSON_Name"],
                Type = Master_Report_Type,
                Details = f"Unable to load {Master_Report_Type} dataframe to MySQL ({Error_Message})",
            )
            Error_Log.append(Master_Report_Loading_Problem)
            logging.info(f"Added to Error_Log: {SUSHI_Call_Data['JSON_Name']}|{Master_Report_Type}|Unable to load {Master_Report_Type} dataframe to MySQL ({Error_Message})")

#Section: Output Error_Log
Error_Log_Location = str(Path('.', 'data', 'Error_Log.csv'))
FileIO = open(Error_Log_Location, 'w', newline='')
CSV_Writer = csv.DictWriter(FileIO, [
    "Interface",
    "Report",
    "Error",
    "Description"
])
CSV_Writer.writeheader()

for Error in Error_Log:
    CSV_Writer.writerow(Error)

FileIO.close()
#ToDo: Figure out how to open CSV so it stays open when program exits--os.startfile closes file at program exit