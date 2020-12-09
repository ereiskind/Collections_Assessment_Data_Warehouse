#API repository: https://app.swaggerhub.com/apis/COUNTER/counter-sushi_5_0_api/1.0.0

import requests
import json
import csv
import requests
from requests import HTTPError, Timeout
import time
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

    #Subsection: Confirm Returned Data Means OK to Continue
    if "Exception" in Status_Check.json():
        #ToDo: Add platform and error to Platforms_Not_Collected
        print(f"Reports from {SUSHI_Call_Data['URL']} not available because {Status_Check.json()['Exception']['Message']} (error code {Status_Check.json()['Exception']['Code']}).")
        # https://www.projectcounter.org/appendix-f-handling-errors-exceptions/ has list of COUNTER error codes
        continue

    #Alert: Silverchair, which uses both Requestor ID and API Key, generates a download when the SUSHI URL is entered rather than returning the data on the page itself--believed this meant requests couldn't find the data, needs to be confirmed
    #ToDo: Possibly handle above by checking if Status_Check.json() is empty

    #Subsection: Get List of R5 Reports Available
    Reports_URL = SUSHI_Call_Data["URL"] + "reports" # This API returns a list of the available SUSHI reports
    time.sleep(1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this spaces out the API calls
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
    if Available_Master_Reports == []:
        #ToDo: Add platform and error to Platforms_Not_Collected
        # If the master reports aren't offered, should the standard views be retrieved with this script?
        print(f"{SUSHI_Call_Data['URL']} doesn't offer any master reports.")
        continue
    
    #Subsection: Collect Individual Master Reports
    #ToDo: Allow system or user to change dates
    Credentials["begin_date"] = "2020-01-01"
    Credentials["end_date"] = "2020-01-31"

    for Master_Report in Available_Master_Reports: 
        Master_Report_Type = Master_Report["Report_ID"]
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
            # If either of the below isn't used, it's presence will add a 3050 warning to the JSON; since there's no good way to tell which IRs use which parameter, using both and letting the warning pass silently is the best option
            Credentials["include_parent_details"] = "True"
            #Alert: PQ IR had {"Name": "Include_Component_Details", "Value": "No"} as Report_Attributes item
            Credentials["include_component_details"] = "True"
        else:
            print("Invalid Master Report Type: " + Master_Report["Report_Name"])
            continue
        
        Master_Report_URL = SUSHI_Call_Data["URL"] + "reports/" + Master_Report_Type.lower()
        time.sleep(1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this spaces out the API calls
        try:
            Master_Report_Response = requests.get(Master_Report_URL, params=Credentials, timeout=90)
            # Larger reports seem to take longer to respond, so the initial timeout interval is long
        except Timeout as error:
            try: # Timeout errors seem to be random, so going to try get request again with more time
                time.sleep(1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this spaces out the API calls
                Master_Report_Response = requests.get(Master_Report_URL, params=Credentials, timeout=120)
            except Timeout as error:
                #ToDo: Get info for loading into sushierrorreports table--note that SUSHI JSONs for this resource don't have Report_Header sections, so data needs to come from elsewhere
                #ToDo: Load above data into a record in SUSHIErrorReports
                print(f"Server didn't respond to request for {Master_Report_Type} after second request of 120 seconds [{format(error)}].")
                continue
            except:
                print(f"An error occurred while requesting {Master_Report_Type} [{format(error)}].")
                #ToDo: Get same data as above and load into SUSHIErrorReports
                continue

            if Master_Report_Response.text == "":
                #ToDo: If Master_Report_Response.json() is empty, get above data and load into record in SUSHIErrorReports
                print(f"{Master_Report_URL} returned no data.")
                continue

        #ToDo: Error handling for JSON decoding errors--is there a way to take the text and transform it to valid JSON-like Python data structures? The rest of the code relies on Report_JSON being a dictionary.
        Report_JSON = Master_Report_Response.json()
        #Alert: Confirm that empty report is no usage
        

        #Section: Handle Reports Returning Errors
        #Subsection: Determine if Report is an Error Report
        #ToDo: Change this to looking for "Report_Items" in top level of keys in Report_JSON  and to checking that its value isn't an empty list
        #Alert: An empty Report_Header means no usage to report, and a number of platforms with no databases offer DR. How should the program distinguish between valid no usage, erroneous empty reports, and reports that aren't appropriate for the platform?
        # In error responses, no data is being reported, so Report_Header is the only top-level key; when data is returned, it's joined by Report_Items
        Top_Level_Keys = 0
        for value in Report_JSON.values():
            Top_Level_Keys += 1

        #Subsection: Clean Data for Error Reports
        #ToDo: Change below to if "Report_Items" isn't found in top level of Report_JSON keys
        if Top_Level_Keys == 1:
            #ToDo: Institution_ID for COUNTER namespace (collected from report_path), Created_By don't contain helpful data
            #ToDo: Wrap below in try block with except KeyError that redoes the function without the Report_Header
            Error_Reports_Dataframe = pandas.json_normalize(Report_JSON, ['Report_Header', 'Institution_ID'], sep=":", meta=[
                ['Report_Header', 'Created'],
                ['Report_Header', 'Created_By'],
                ['Report_Header', 'Institution_ID'],
                ['Report_Header', 'Report_ID'],
                ['Report_Header', 'Report_Name'] #ToDo: Should this be kept, or should info on which report always use ID and be stored in Char(2)?
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
        #Alert: Thought (also in Visio)--Alma interfaces, nested under vendors in one-to-many relationship but only able to store a single SUSHI credential, can be used as backends and connected to frontends here, be used to represent both backends and frontends individually, or should one platform among those that share a SUSHI setup be designated as location for SUSHI data?
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

        if Master_Report_Type == "DR":
            Dataframe_Fields.append(['Report_Items', 'Database'])
            Dataframe_Fields.append(['Report_Items', 'Publisher']) # Should we use Publisher or Publisher_ID and match the IDs in the database?
        elif Master_Report_Type == "TR":
            Dataframe_Fields.append(['Report_Items', 'Publisher']) # Should we use Publisher or Publisher_ID and match the IDs in the database?
            Dataframe_Fields.append(['Report_Items', 'Item_ID'])
            Dataframe_Fields.append(['Report_Items', 'Section_Type'])
            Dataframe_Fields.append(['Report_Items', 'Access_Type'])
            Dataframe_Fields.append(['Report_Items', 'YOP'])
            Dataframe_Fields.append(['Report_Items', 'Title'])
        elif Master_Report_Type == "IR":
            Dataframe_Fields.append(['Report_Items', 'Publisher']) # Should we use Publisher or Publisher_ID and match the IDs in the database?
            Dataframe_Fields.append(['Report_Items', 'Item_ID'])
            Dataframe_Fields.append(['Report_Items', 'Access_Type'])
            Dataframe_Fields.append(['Report_Items', 'YOP'])
            Dataframe_Fields.append(['Report_Items', 'Item'])
            # Excluded attributes: Authors, Publication_Date, Article_Version, Parent_Authors, Parent_Publication_Date, Parent_Article_Version, Component_Authors, Component_Publication_Date
            # About Parent Info
                # Optional fields containing info that can provide useful information: Parent_Title, Parent_Data_Type, Parent_DOI, Parent_Proprietary_ID, Parent_ISBN, Parent_Print_ISSN, Parent_Online_ISSN, Parent_URI, Component_Title, Component_Data_Type, Component_DOI, Component_Proprietary_ID, Component_ISBN, Component_Print_ISSN, Component_Online_ISSN, Component_URI
                # Unable to find item report containing this information, thus unsure how it's nested
                # list all attributes marked with ‘O’ in tables 4.b, 4.f, 4.k and 4.p except the Parent and Component elements in attributes_to_show, separated by ‘|’. For including the Parent and Component elements in IR add include_parent_details=True and include_component_details=True. This is explained in section 3.3.8.
            #ToDo: Map paths for Parent_Title, Parent_Data_Type, Parent_DOI, Parent_Proprietary_ID, Parent_ISBN, Parent_Print_ISSN, Parent_Online_ISSN, Parent_URI, Component_Title, Component_Data_Type, Component_DOI, Component_Proprietary_ID, Component_ISBN, Component_Print_ISSN, Component_Online_ISSN, Component_URI
        else:
            pass # This represents Platform Master Reports; the if-elif-else above filters out other reports before they reach this point
        
        #Subsection: Create Initial Dataframe
        #ToDo: Possibly put in try block if missing keys are causing problems despite setting 'ignore'
        Report_Dataframe = pandas.json_normalize(Report_JSON, meta=Dataframe_Fields, sep=":", errors='ignore')
        Report_Dataframe.to_csv('Check_Dataframe.csv', mode='a', index=False) # Using to more clearly investigate contents
        print("Break to look at CSV")

        #Subsection: Create Single Time Field
        #ToDo: Confirm that fields for beginning and end of each time interval are for the beginning and end of a single month
        #ToDo: Create a field for that month and/or change name of beginning date field (as ISO for first date of that month)
        #ToDo: Remove unneeded date fields

        #Subsection: Other Possible Changes to Dataframe
        # Should Access_Method be manipulated into a Boolean that would allow for exclusion of TDM, or should potential of other Access_Method options be kept?
        # Resource identifiers (DOI, ISBN, ect.) come as a list of dictionaries where all the dictionaries have the keys "Type" for the type of identifier and "Value" for the identifier itself; putting the whole list in the dataframe will be simpler and will more readily convert to a relational system where data about individual resources is in a separate relation
        # IR records largely lack elements indicating parent titles (thus far, none found)--do we want to try using the DOI API to connect items to titles?
            # Not all TR contain DOI for journals--is there an API that takes in ISSNs and returns DOIs?
            # Can that same API handle ISBNs?
        # YOP of 0001 means unknown, YOP of 9999 means articles in press--need way to indicate this in outputting results


        #Section: Export Dataframe to MySQL


#Section: Retrieve List of Failed Reports
#ToDo: SELECT COUNTER_Namespace, Report_Source, Report_Type FROM sushierrorreports WHERE Time_Report_Run > Script_Start_Time (aka created after the script started running)
#ToDo: Output the results of the above to an Excel file

Connection.close()