#API repository: https://app.swaggerhub.com/apis/COUNTER/counter-sushi_5_0_api/1.0.0

import requests
import json
import csv
import requests
from requests import HTTPError, Timeout
import re
import pandas
import pymysql
from sqlalchemy import create_engine
import Database_Credentials #Alert: From original repository with flat structure; this file is now located at Collections_Assessment_Data_Warehouse/data/Database_Credentials.py


#Section: Functions
def Load_Dataframe_into_MySQL(Dataframe, DBTable, DBEngine):
    """A pandas to_sql function call bracketed by the creation and destruction of a SQLAlchemy session object.
    
    This function loads the data contained in Dataframe into DBTable, which is in the MySQL database referenced by DBEngine. Dataframe's record index values aren't included.
    Arguments:
        Dataframe {pandas dataframe} -- dataframe to be loaded into MySQL
        DBTable {string} -- name of the MySQL table (relation) the data's being loaded into
        DBEngine {SQLAlchemy engine} -- engine object for MySQL database
    """
    Connection = DBEngine.connect()
    Dataframe.to_sql(
        DBTable,
        con=Connection,
        if_exists='append',
        index=False
    )
    Connection.close()


def Execute_SQL_Statement(SQLStatement, DBConnection):
    """Executes a SQL statement using a PyMySQL connection object.
    This function executes a SQL statement using PyMySQL, creating the cursor based off the connection object argument at the beginning and performing the commit method on that connection at the end.
    Arguments:
        SQLStatement {string} -- the SQL statement
        DBConnection {PyMySQL connection} -- connection object for MySQL database
    """
    Cursor = DBConnection.cursor()
    Cursor.execute(SQLStatement)
    DBConnection.commit()


#Section: Initialize Variables for Reports Not Captured
#ToDo: Save the current time to variable Script_Start_Time
#ToDo: Create variable (what data type?) Platforms_Not_Collected for saving data about the platforms where reports aren't collected and the specific missing master reports can't be identified


#Section: Collect Information Needed for SUSHI Call
# Later, this will be replaced with a call to the Alma API--see Credentials_Through_Alma_API.py
SUSHI_Data_File = open('SUSHI_R5_Credentials.csv','r', encoding='utf-8-sig') # Without encoding, characters added to front of first URL, causing API call to fail
SUSHI_Data = []
for Set in [SUSHI_Data_Set.rstrip().split(",") for SUSHI_Data_Set in SUSHI_Data_File]: # This turns the CSV into a list where each line is a dictionary
    if Set[1] == "":
        Data = dict(URL = Set[0], api_key = Set[2], customer_id = Set[3])
    elif Set[2] == "":
        Data = dict(URL = Set[0], requestor_id = Set[1], customer_id = Set[3])
    else:
        Data = dict(URL = Set[0], requestor_id = Set[1], api_key = Set[2], customer_id = Set[3])
    SUSHI_Data.append(Data)


#Section: Create the PyMySQL Connection and SQLAlchemy Engine
Database = 'testdatawarehouse'

Connection = pymysql.connect(
    host=Database_Credentials.Host,
    user=Database_Credentials.Username,
    password=Database_Credentials.Password,
    db=Database
)

Engine = create_engine(
    'mysql+pymysql://' +
    Database_Credentials.Username + ':' +
    Database_Credentials.Password + '@' +
    Database_Credentials.Host + ':' + str(Database_Credentials.Post) + '/' +
    Database,
    echo=False
)


#Section: Make API Calls
for SUSHI_Call_Data in SUSHI_Data:
    Credentials = {key: value for key, value in SUSHI_Call_Data.items() if key != "URL"} # This creates another dictionary without the URL to be used in the URL's query string
    #Subsection: Determine SUSHI Availability
    Status_URL = SUSHI_Call_Data["URL"] + "status"
    try:
        Status_Check = requests.get(Status_URL, params=Credentials, timeout=10)
        Status_Check.raise_for_status()
    except HTTPError as error: # If the API request returns a 4XX HTTP code
        print(f"HTTP Error: {format(error)}")
        #ToDo: Add platform and error to Platforms_Not_Collected
        continue
    except Timeout as error: # If the API request times out
        print(f"Server didn't respond after 10 seconds ({format(error)}).")
        #ToDo: Add platform and error to Platforms_Not_Collected
        continue
    except: # If there's some other problem with the API request
        print(f"Some error other than a status error or timout occurred when trying to access {Status_URL}.")
        #ToDo: Add platform and error to Platforms_Not_Collected
        continue
    #Alert: Silverchair, which uses both Requestor ID and API Key, generates a download when the SUSHI URL is entered rather than returning the data on the page itself; as a result, requests can't find the data
    #ToDo: Possibly handle above by checking if Status_Check.json() is empty

    #Subsection: Get List of R5 Reports Available
    Reports_URL = SUSHI_Call_Data["URL"] + "reports" # This API returns a list of the available SUSHI reports
    try:
        Available_Reports = requests.get(Reports_URL, params=Credentials, timeout=10)
    except Timeout as error:
        print(f"Server didn't respond to request for {Master_Report_Type} after 10 seconds [{format(error)}].")
            #ToDo: Add platform and error to Platforms_Not_Collected
        continue
    
    Available_Master_Reports = [] # This list will contain the dictionaries from the JSON for the master reports available on the platform, which will be the only reports pulled
    for Report in Available_Reports.json():
        if "Master Report" in Report["Report_Name"]:
            Available_Master_Reports.append(Report)
    
    #Subsection: Collect Reports
    URL_Report_Path = re.compile(r'reports/\w{2}$') #ToDo: Handle trailing slash by adding it with a ? here, then creating a variable that removes it if it exists
    #ToDo: Allow system or user to change dates
    Credentials["begin_date"] = "2020-01-01"
    Credentials["end_date"] = "2020-01-31"
    for Master_Report in Available_Master_Reports: # This cycles through each of the master reports offered by the platform
        Master_Report_Type = Master_Report["Report_Name"] # This adds all of the possible attributes for a given master report to the URL used to request that master report
        if Master_Report_Type == "Platform Master Report":
            Credentials["attributes_to_show"] = "Data_Type|Access_Method"
        elif Master_Report_Type == "Database Master Report":
            Credentials["attributes_to_show"] = "Data_Type|Access_Method"
        elif Master_Report_Type == "Title Master Report":
            Credentials["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type|Section_Type"
        elif Master_Report_Type == "Item Master Report":
            Credentials["attributes_to_show"] = "Data_Type|Access_Method|YOP|Access_Type"
        else:
            print("Invalid Master Report Type: "+Master_Report_Type)
            continue
        
        Master_Report_URL = SUSHI_Call_Data["URL"] + URL_Report_Path.findall(Master_Report["Path"])[0]
        # This uses a regex to construct the API URL so only the piece of the path related to the report requested is included (some platforms have a "Path" attribute that include the domain as well)
        try:
            Master_Report_Response = requests.get(Master_Report_URL, params=Credentials, timeout=90)
            # Larger reports seem to take longer to respond, so the initial timeout interval is long
        except Timeout as error:
            try: # Timeout errors seem to be random, so going to try get request again with more time
                Master_Report_Response = requests.get(Master_Report_URL, params=Credentials, timeout=120)
            except Timeout as error:
                #ToDo: Get following info
                    # COUNTER namespace for the provider of the report: COUNTER_Namespace [extracted from Report_Header:Institution_ID]--derived by matching to URL
                    # Time the attempt to run the report was made: Time_Report_Run [Report_Header:Created]--timestamp?
                    # Platform that created the report: Report_Source [Report_Header:Created_By]--derived by matching to URL
                    # Full name of the master report: Report_Type [Report_Header:Report_Name] = Master_Report_Type
                #ToDo: Load above data into a record in SUSHIErrorReports
                print(f"Server didn't respond to request for {Master_Report_Type} after second request of 120 seconds [{format(error)}].")
                #ToDo: except: 
                    #ToDo: Get same data as above and load into SUSHIErrorReports
                #ToDo: If Master_Report_Response.json() is empty, get above data and load into record in SUSHIErrorReports
                continue

        Report_JSON = Master_Report_Response.json()
        

        #Section: Handle Reports Returning Errors
        #Subsection: Determine if Report is an Error Report
        #ToDo: Change this to looking for "Report_Items" in top level of keys in Report_JSON  and to checking that its value isn't an empty list
        # In error responses, no data is being reported, so Report_Header is the only top-level key; when data is returned, it's joined by Report_Items
        Top_Level_Keys = 0
        for value in Report_JSON.values():
            Top_Level_Keys += 1

        #Subsection: Clean Data for Error Reports
        #ToDo: Change below to if "Report_Items" isn't found in top level of Report_JSON keys
        if Top_Level_Keys == 1:
        #ToDo: Wrap below in try block with except KeyError that redoes the function without the Report_Header
            Error_Reports_Dataframe = pandas.json_normalize(Report_JSON, ['Report_Header', 'Institution_ID'], sep=":", meta=[
                ['Report_Header', 'Created'],
                ['Report_Header', 'Created_By'],
                ['Report_Header', 'Institution_ID'],
                ['Report_Header', 'Report_ID'],
                ['Report_Header', 'Report_Name']
            ]) #ToDo: Potentially move all fields to save to meta keyword argument
            Error_Reports_Dataframe.drop(Error_Reports_Dataframe[Error_Reports_Dataframe.Type != "Proprietary"].index, inplace=True)
            Error_Reports_Dataframe.drop(columns='Type', inplace=True)
            # The to_string operation seems to be truncating the value in Error_Reports_Dataframe['Report_Header:Institution_ID'] and leaving an ellipse at the end; since the content of the key-value pair with the key "Type" is not needed for the matching, it's being removed
            for i in range(len(Error_Reports_Dataframe['Report_Header:Institution_ID'])):
                del Error_Reports_Dataframe['Report_Header:Institution_ID'].iloc[i]["Type"]
            # One-at-a-time record handling not needed as these dataframes by design only have a single record so the overall error log is in 2NF
            Error_Reports_Dataframe['Report_Matching_Index'] = Error_Reports_Dataframe['Report_Header:Institution_ID'].to_string()
            Error_Reports_Dataframe['Report_Matching_Index'] = Error_Reports_Dataframe.Report_Matching_Index.str.slice(start=1) + Error_Reports_Dataframe['Report_Header:Report_ID']
            Error_Reports_Dataframe['Report_Matching_Index'] = Error_Reports_Dataframe.Report_Matching_Index.str.strip()
            Error_Reports_Dataframe.drop(columns='Report_Header:Institution_ID', inplace=True)
            Error_Reports_Dataframe.drop(columns='Report_Header:Report_ID', inplace=True)
            Error_Reports_Dataframe['COUNTER_Namespace'] = Error_Reports_Dataframe.Value.str.split(":").str[0]
            Error_Reports_Dataframe.drop(columns='Value', inplace=True)
            
            #Subsection: Load Error Reports into MySQL
            Error_Reports_Dataframe.rename(columns={
                'Report_Matching_Index': 'Matching',
                'Report_Header:Created_By': 'Report_Source',
                'Report_Header:Report_Name': 'Report_Type'
            }, inplace=True)
            # Import requires explicit conversion to datetime format here and timestamp data type in table
            Error_Reports_Dataframe['Time_Report_Run'] = pandas.to_datetime(Error_Reports_Dataframe['Report_Header:Created'], infer_datetime_format=True)
            # MySQL import relies on fields being in specific order, but not all providers order the fields in the same way, so fields are put in specific order for loading here
            Error_Reports_Dataframe = Error_Reports_Dataframe[[
                'COUNTER_Namespace',
                'Matching',
                'Time_Report_Run',
                'Report_Source',
                'Report_Type'
            ]]
            Load_Dataframe_into_MySQL(Error_Reports_Dataframe, 'sushierrorreports', Engine)

            #Subsection: Get New Error Reports Primary Keys from MySQL
            # The sushierrorreports table contains all the API calls for master reports that returned errors. Those records that haven't been connected to items in the sushierrorlog table contain the information needed to make this connection in the "Matching" field; reports that have been connected have a null "Matching" field.
            Query_for_Foreign_Keys = "SELECT SUSHIErrorReports_ID, Matching FROM sushierrorreports WHERE Matching IS NOT null;"
            Foreign_Key_Dataframe = pandas.read_sql(
                Query_for_Foreign_Keys,
                con=Engine,
                index_col='Matching',
                columns='SUSHIErrorReports_ID'
            )

            #Subsection: Clean Data for Error Log
            #ToDo: Wrap below in try block with except KeyError that redoes the function without the Report_Header
            Error_Log_Dataframe = pandas.json_normalize(Report_JSON, ['Report_Header', 'Exceptions'], sep=":", meta=[
                ['Report_Header', 'Institution_ID'],
                ['Report_Header', 'Report_ID'],
            ]) #ToDo: Potentially move all fields to save to meta keyword argument
            Error_Log_Dataframe['Report_Matching_Index'] = None
            for i in range(len(Error_Log_Dataframe['Report_Header:Institution_ID'])):
                Error_Log_Dataframe['Report_Matching_Index'].iloc[i] = str(Error_Log_Dataframe['Report_Header:Institution_ID'].iloc[i])
                Error_Log_Dataframe['Report_Matching_Index'].iloc[i] = Error_Log_Dataframe['Report_Matching_Index'].iloc[i] + Error_Log_Dataframe['Report_Header:Report_ID'].iloc[i]
            Error_Log_Dataframe['Report_Matching_Index'] = Error_Log_Dataframe['Report_Matching_Index'].str.strip()
            Error_Log_Dataframe.drop(columns='Report_Header:Institution_ID', inplace=True)
            Error_Log_Dataframe.drop(columns='Report_Header:Report_ID', inplace=True)
            
            Error_Log_Dataframe = Error_Log_Dataframe.join(
                Foreign_Key_Dataframe,
                on='Report_Matching_Index',
                how='inner'
            )
            
            #Subsection: Load Error Log into MySQL
            Error_Log_Dataframe.rename(columns={
                'Code': 'Error_Code',
                'Data': 'Error_Details',
                'Message': 'Error_Name',
                'SUSHIErrorReports_ID': 'Report_ID'
            }, inplace=True)
            # MySQL import relies on fields being in specific order, but not all providers order the fields in the same way, so fields are put in specific order for loading here
            Error_Log_Dataframe = Error_Log_Dataframe[[
                'Report_ID',
                'Error_Code',
                'Error_Details',
                'Error_Name',
                'Severity'
            ]]
            Load_Dataframe_into_MySQL(Error_Log_Dataframe, 'sushierrorlog', Engine)

            #Subsection: Null Values Used to Designate New Primary Keys in Error Report
            Query_for_Clearing = f"UPDATE sushierrorreports SET Matching = null WHERE SUSHIErrorReports_ID = {Foreign_Key_Dataframe.SUSHIErrorReports_ID.iloc[0]};"
            Execute_SQL_Statement(Query_for_Clearing, Connection)

            print("The report returned an error. See the SUSHI error reports log in the data warehouse for more details.")
            continue
        
        
        #Section: Read Master Report into Dataframe
        #Alert: Alma structure so one-to-many between vendors and platforms and each platform has own SUSHI--how is that handled in relation to the model where a single SUSHI can cover multiple platforms? --issue of database schema
        #Subsection: Determine Fields to Import
        Dataframe_Fields = [
            ['Report_Header', 'Created'],
            ['Report_Items', 'Platform'],
            ['Report_Items', 'Performance', 'Period', 'Begin_Date'],
            ['Report_Items', 'Performance', 'Period', 'End_Date'],
            ['Report_Items', 'Performance', 'Instance', 'Metric_Type'],
            ['Report_Items', 'Performance', 'Instance', 'Count'],
            ['Report_Items', 'Access_Method'],
            ['Report_Items', 'Data_Type'] #ToDo: Determine if issues with some of the reports returning errors are actually issues with missing keys and json_normalize (which shouldn't be happening since errors='ignore')
        ]

        if Master_Report_Type == "Database Master Report":
            Dataframe_Fields.append(['Report_Items', 'Database'])
            Dataframe_Fields.append(['Report_Items', 'Publisher']) # Should we use Publisher or Publisher_ID and match the IDs in the database?
        elif Master_Report_Type == "Title Master Report":
            Dataframe_Fields.append(['Report_Items', 'Publisher']) # Should we use Publisher or Publisher_ID and match the IDs in the database?
            Dataframe_Fields.append(['Report_Items', 'Item_ID'])
            Dataframe_Fields.append(['Report_Items', 'Section_Type'])
            Dataframe_Fields.append(['Report_Items', 'Access_Type'])
            Dataframe_Fields.append(['Report_Items', 'YOP'])
            Dataframe_Fields.append(['Report_Items', 'Title'])
        elif Master_Report_Type == "Item Master Report":
            Dataframe_Fields.append(['Report_Items', 'Publisher']) # Should we use Publisher or Publisher_ID and match the IDs in the database?
            Dataframe_Fields.append(['Report_Items', 'Item_ID'])
            Dataframe_Fields.append(['Report_Items', 'Access_Type'])
            Dataframe_Fields.append(['Report_Items', 'YOP'])
            Dataframe_Fields.append(['Report_Items', 'Item'])
            # Excluded attributes: Authors, Publication_Date, Article_Version, Parent_Authors, Parent_Publication_Date, Parent_Article_Version, Component_Authors, Component_Publication_Date
            # Can include parent info--how is this nested???
            # Desired parent info: Parent_Title, Parent_Data_Type, Parent_DOI, Parent_Proprietary_ID, Parent_ISBN, Parent_Print_ISSN, Parent_Online_ISSN, Parent_URI, Component_Title, Component_Data_Type, Component_DOI, Component_Proprietary_ID, Component_ISBN, Component_Print_ISSN, Component_Online_ISSN, Component_URI
        else:
            pass # This represents Platform Master Reports; the if-elif-else above filters out other reports before they reach this point
        
        #Subsection: Create Initial Dataframe
        #ToDo: Use only meta argument, no record_path
        Report_Dataframe = pandas.json_normalize(Report_JSON, ['Report_Header', 'Institution_ID'], sep=":", meta=Dataframe_Fields, errors='ignore')
        #ToDo: Above is outputting dataframe where only keys under Report_Header have values--why???
        Report_Dataframe.to_csv('Check_Dataframe.csv', mode='a', index=False) # Using to more clearly investigate contents
        print("Break to look at CSV")

        #Subsection: Create Single Time Field
        #ToDo: Confirm that fields for beginning and end of each time interval are for the beginning and end of a single month
        #ToDo: Create a field for that month and/or change name of beginning date field (as ISO for first date of that month)
        #ToDo: Remove unneeded date fields

        #Subsection: Other Possible Changes to Dataframe
        # Should Access_Method be manipulated into a Boolean that would allow for exclusion of TDM, or should potential of other Access_Method options be kept?
        # Resource identifiers (DOI, ISBN, ect.) come as a list of dictionaries where all the dictionaries have the keys "Type" for the type of identifier and "Value" for the identifier itself; putting the whole list in the dataframe will be simpler and will more readily convert to a relational system where data about individual resources is in a separate relation
        # IR records might not have parent item elements--if that's the case, can DOI be fed to API to get info needed to establish relation to its parent item?
        # YOP of 0001 means unknown, YOP of 9999 means articles in press--need way to indicate this in outputting results


        #Section: Export Dataframe to MySQL


#Section: Retrieve List of Failed Reports
#ToDo: SELECT COUNTER_Namespace, Report_Source, Report_Type FROM sushierrorreports WHERE Time_Report_Run > Script_Start_Time (aka created after the script started running)
#ToDo: Output the results of the above to an Excel file

Connection.close()