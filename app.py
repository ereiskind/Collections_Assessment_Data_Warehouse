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
        #ToDo: Need a way to capture when the response isn't usage stats (e.g. code 1011, "Report Queued for Processing"; code 1020, "Client has made too many requests")--JSON has fields "Code" with number, "Message" with problem description, "Data" with more details on problem
        # JSONs are truncated when output to terminal 
        Report_JSON = json.loads(Master_Report_Response.text)
        print(json.dumps(Report_JSON, indent=4))


        #Section: Read Master Report into Dataframe
        #Subsection: Create Initial Dataframe
        # Use json_normalize

        #Subsection: Create Single Time Field
        #ToDo: Confirm that fields for beginning and end of each time interval are for the beginning and end of a single month
        #ToDo: Create a field for that month and/or change name of beginning date field (as ISO for first date of that month)
        #ToDo: Remove unneeded date fields

        #Subsection: Other Possible Changes to Dataframe
        # Should Access_Method be manipulated into a Boolean that would allow for exclusion of TDM, or should potential of other Access_Method options be kept?
        # Resource identifiers (DOI, ISBN, ect.) come as a list of dictionaries where all the dictionaries have the keys "Type" for the type of identifier and "Value" for the identifier itself; putting the whole list in the dataframe will be simpler and will more readily convert to a relational system where data about individual resources is in a seperate relation
        # IR records might not have parent item elements--if that's the case, can DOI be fed to API to get info needed to establish relation to its parent item?


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