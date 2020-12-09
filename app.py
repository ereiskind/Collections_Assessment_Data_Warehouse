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
    
    This function loads the data contained in Dataframe, a pandas dataframe, into DBTable, a table (relation) in the MySQL database which is being called by DBEngine, a SQLAlchemy engine object. Dataframe's record index values aren't included.
    """
    Connection = DBEngine.connect()
    Dataframe.to_sql(
        DBTable,
        con=Connection,
        if_exists='append',
        index=False
    )
    Connection.close()


#Section: Collect Information Needed for SUSHI Call
SUSHI_Data_File = open('SUSHI_R5_Credentials.csv','r')
SUSHI_Data = []
for Set in [SUSHI_Data_Set.rstrip().split(",") for SUSHI_Data_Set in SUSHI_Data_File]: # This turns the CSV into a list where each line is a dictionary
    if Set[1] == "":
        Data = dict(URL = Set[0], api_key = Set[2], customer_id = Set[3])
    elif Set[2] == "":
        Data = dict(URL = Set[0], requestor_id = Set[1], customer_id = Set[3])
    else:
        Data = dict(URL = Set[0], requestor_id = Set[1], api_key = Set[2], customer_id = Set[3])
    SUSHI_Data.append(Data)


#Section: Create the SQLAlchemy Engine
Engine = create_engine(
    'mysql+pymysql://' +
    Database_Credentials.Username + ':' +
    Database_Credentials.Password + '@' +
    Database_Credentials.Host + ':' + str(Database_Credentials.Post) + '/' +
    'testdatawarehouse',
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
        #ToDo: 403 error seems to be invalid credentials--perhaps create specific error message for that?
        continue
    except Timeout as error: # If the API request times out
        print(f"Server didn't respond after 10 seconds ({format(error)}).")
        continue
    except: # If there's some other problem with the API request
        print(f"Some error other than a status error or timout occurred when trying to access {Status_URL}.")
        continue
    #Alert: Silverchair, which uses both Requestor ID and API Key, generates a download when the SUSHI URL is entered rather than returning the data on the page itself; as a result, requests can't find the data
    #ToDo: Determine way to output platforms that aren't checked for reports

    #Subsection: Get List of R5 Reports Available
    Reports_URL = SUSHI_Call_Data["URL"] + "reports" # This API returns a list of the available SUSHI reports
    try:
        Available_Reports = requests.get(Reports_URL, params=Credentials, timeout=90)
    except Timeout as error:
        print(f"Server didn't respond to request for {Master_Report_Type} after 90 seconds [{format(error)}].")
            # Larger reports seem to take longer to respond, so the timeout interval is long
        continue
    
    Available_Master_Reports = [] # This list will contain the dictionaries from the JSON for the master reports available on the platform, which will be the only reports pulled
    for Report in json.loads(Available_Reports.text):
        if "Master Report" in Report["Report_Name"]:
            Available_Master_Reports.append(Report)
    
    #Subsection: Collect Reports
    URL_Report_Path = re.compile(r'reports/\w{2}$')
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
            print("Invalid Master Report Type")
            #ToDo: Determine if "continue" is appropriate keyword to move on to next Master_Report in Available_Master_Reports
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
                continue

        Report_JSON = json.loads(Master_Report_Response.text)
        

        #Section: Handle Reports Returning Errors
        #Subsection: Determine if Report is an Error Report
        # In error responses, no data is being reported, so Report_Header is the only top-level key; when data is returned, it's joined by Report_Items
        Top_Level_Keys = 0
        for value in Report_JSON.values():
            Top_Level_Keys += 1

        #Subsection: Clean Data for Error Reports
        if Top_Level_Keys == 1:
            Error_Reports_Dataframe = pandas.json_normalize(Report_JSON, ['Report_Header', 'Institution_ID'], sep=":", meta=[
                ['Report_Header', 'Created'],
                ['Report_Header', 'Created_By'],
                ['Report_Header', 'Institution_ID'],
                ['Report_Header', 'Report_ID'],
                ['Report_Header', 'Report_Name']
            ])
            Error_Reports_Dataframe.drop(Error_Reports_Dataframe[Error_Reports_Dataframe.Type != "Proprietary"].index, inplace=True)
            Error_Reports_Dataframe.drop(columns='Type', inplace=True)
            Error_Reports_Dataframe['Report_Matching_Index'] = Error_Reports_Dataframe['Report_Header:Institution_ID'].to_string()
            Error_Reports_Dataframe['Report_Matching_Index'] = Error_Reports_Dataframe.Report_Matching_Index.str.slice(start=1) + Error_Reports_Dataframe['Report_Header:Report_ID']
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
            Error_Reports_Dataframe.to_csv('Check_Dataframe_1.csv', mode='a', index=False)
            Load_Dataframe_into_MySQL(Error_Reports_Dataframe, 'sushierrorreports', Engine)

            #Subsection: Get New Error Reports Primary Keys from MySQL
            #ToDo: Read PK and index back from MySQL

            #Subsection: Clean Data for Error Log
            Error_Log_Dataframe = pandas.json_normalize(Report_JSON, ['Report_Header', 'Exceptions'], sep=":", meta=[
                ['Report_Header', 'Institution_ID'],
                ['Report_Header', 'Report_ID'],
            ])
            Error_Log_Dataframe['Report_Matching_Index'] = Error_Log_Dataframe['Report_Header:Institution_ID'].to_string()
            Error_Log_Dataframe['Report_Matching_Index'] = Error_Log_Dataframe.Report_Matching_Index.str.slice(start=1) + Error_Log_Dataframe['Report_Header:Report_ID']
            # Above assumes that there won't be more than 10 rows (error codes) returned for a given report
            Error_Log_Dataframe.drop(columns='Report_Header:Institution_ID', inplace=True)
            Error_Log_Dataframe.drop(columns='Report_Header:Report_ID', inplace=True)
            #ToDo: Add reports PK to log dataframe as field named "Report_ID" by matching on field Report_Matching_Index
            #ToDo: Remove Report_Matching_Index column from dataframe
            
            #Subsection: Load Error Log into MySQL
            Error_Log_Dataframe.rename(columns={
                'Code': 'Error_Code',
                'Data': 'Error_Details',
                'Message': 'Error_Name'
            }, inplace=True)
            # MySQL import relies on fields being in specific order, but not all providers order the fields in the same way, so fields are put in specific order for loading here
            Error_Log_Dataframe = Error_Log_Dataframe[[
                'Report_ID',
                'Error_Code',
                'Error_Details',
                'Error_Name',
                'Severity'
            ]]
            Error_Log_Dataframe.to_csv('Check_Dataframe_2.csv', mode='a', index=False)

            #Subsection: Null Values Used to Designate New Primary Keys in Error Report
            #ToDo: Null values in "Match" column of SUSHIErrorReports table for those reports just loaded

            print("The report returned an error. See the SUSHI error reports log in the data warehouse for more details.")
            continue
        
        
        #Section: Read Master Report into Dataframe
        #Subsection: Determine Fields to Import
        Dataframe_Fields = [
            ['Report_Header', 'Created'],
            ['Report_Items', 'Platform'],
            ['Report_Items', 'Performance', 'Period', 'Begin_Date'],
            ['Report_Items', 'Performance', 'Period', 'End_Date'],
            ['Report_Items', 'Performance', 'Instance', 'Metric_Type'],
            ['Report_Items', 'Performance', 'Instance', 'Count'],
            ['Report_Items', 'Access_Method'],
            ['Report_Items', 'Data_Type']
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
            # Desired parent info: Parent_Title, Parent_Data_Type, Parent_DOI, Parent_Propriatary_ID, Parent_ISBN, Parent_Print_ISSN, Parent_Online_ISSN, Parent_URI, Component_Title, Component_Data_Type, Component_DOI, Component_Propriatary_ID, Component_ISBN, Component_Print_ISSN, Component_Online_ISSN, Component_URI
        else:
            pass # This represents Platform Master Reports; the if-elif-else above filters out other reports before they reach this point
        
        #Subsection: Create Initial Dataframe
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
        # Resource identifiers (DOI, ISBN, ect.) come as a list of dictionaries where all the dictionaries have the keys "Type" for the type of identifier and "Value" for the identifier itself; putting the whole list in the dataframe will be simpler and will more readily convert to a relational system where data about individual resources is in a seperate relation
        # IR records might not have parent item elements--if that's the case, can DOI be fed to API to get info needed to establish relation to its parent item?
        # YOP of 0001 means unknown, YOP of 9999 means articles in press--need way to indicate this in outputting results


        #Section: Export Dataframe to MySQL