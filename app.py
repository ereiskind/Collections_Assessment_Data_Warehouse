#API repository: https://app.swaggerhub.com/apis/COUNTER/counter-sushi_5_0_api/1.0.0

import requests
import json
import csv
import requests
from requests import HTTPError, Timeout
import re
import pandas
import pymysql

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
        
        Master_Report_URL = SUSHI_Call_Data["URL"] + URL_Report_Path.findall(Master_Report["Path"])[0] # This uses a regex to construct the API URL so only the piece of the path related to the report requested is included (some platforms have a "Path" attribute that include the domain as well)
        try:
            Master_Report_Response = requests.get(Master_Report_URL, params=Credentials, timeout=10)
        except Timeout as error:
            print(f"Server didn't respond to request for master report after 10 seconds ({format(error)}).")
            #ToDo: Try to get type of master report in string--using Master_Report["Report_Name"] in curly brackets led to an error
            continue

        #Section: Read Master Report into Dataframe
        Report_JSON = json.loads(Master_Report_Response.text)
        #Subsection: If Report Contains Error Codes, Record Errors and Move to Next Report
        # In error responses, no data is being reported, so Report_Header is the only top-level key; when data is returned, it's joined by Report_Items
        Top_Level_Keys = 0
        for value in Report_JSON.values():
            Top_Level_Keys += 1

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
            # Columns (in order): Report_Header:Created, Report_Header:Created_By, Report_Header:Report_Name, Report_Matching_Index, COUNTER_Namespace
            Error_Reports_Dataframe.to_csv('Check_Dataframe_1.csv', mode='a', index=False)

            Error_Log_Dataframe = pandas.json_normalize(Report_JSON, ['Report_Header', 'Exceptions'], sep=":", meta=[
                ['Report_Header', 'Institution_ID'],
                ['Report_Header', 'Report_ID'],
            ])
            Error_Log_Dataframe['Report_Matching_Index'] = Error_Log_Dataframe['Report_Header:Institution_ID'].to_string()
            Error_Log_Dataframe['Report_Matching_Index'] = Error_Log_Dataframe.Report_Matching_Index.str.slice(start=1) + Error_Log_Dataframe['Report_Header:Report_ID']
            # Above assumes that there won't be more than 10 rows (error codes) returned for a given report
            Error_Log_Dataframe.drop(columns='Report_Header:Institution_ID', inplace=True)
            Error_Log_Dataframe.drop(columns='Report_Header:Report_ID', inplace=True)
            # Columns (in order): Code, Data, Message, Severity, Report_Matching_Index
            Error_Log_Dataframe.to_csv('Check_Dataframe_2.csv', mode='a', index=False)

            #ToDo: Load reports dataframe to MySQL, where PK is autogenenerated
            #ToDo: Read PK and index back from MySQL
            #ToDo: Add reports PK to log dataframe as another field
            #ToDo: Remove index column from dataframe
            #ToDo: Create transaction to load log dataframe to MySQL and null values in "Match" column of SUSHIErrorReports table

            print("The report returned an error. See the SUSHI error reports log in the data warehouse for more details.")
            continue
        
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
            pass # Because of if-elif-else with same Boolean Expressions above, this should never happen
        
        #Subsection: Create Initial Dataframe
        Report_Dataframe = pandas.json_normalize(Report_JSON, ['Report_Header', 'Institution_ID'], sep=":", meta=Dataframe_Fields)
        Report_Dataframe.to_csv('Check_Dataframe.csv') # Using to more clearly investigate contents
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

#Testing MySQL Export
connection = pymysql.connect(host='localhost', user='root', password='password', db='usage_test')
cursor = connection.cursor()
cursor.execute(
    """INSERT INTO usage_table (column1, column2) VALUES ("row 1, column 1", "row 1, column 2")"""
)
cursor.fetchall()
connection.commit()
connection.close()