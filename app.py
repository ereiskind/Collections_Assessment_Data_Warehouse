#API repository: https://app.swaggerhub.com/apis/COUNTER/counter-sushi_5_0_api/1.0.0

from pathlib import Path
import json
import csv
import time
import os
import sys
import requests
from requests import HTTPError, Timeout
import pandas
import pymysql
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#Alert: FROM ORIGINAL REPOSITORY with flat structure; these files are now at different locations
import Database_Credentials # Loaded in from runtime environment repository at Collections_Assessment_Data_Warehouse/data/Database_Credentials.py
import SUSHI_R5_API_Calls # In this repository at Collections_Assessment_Data_Warehouse/helpers/SUSHI_R5_API_Calls.py


#Section: Functions
#Subsection: Messages
def Handle_Status_Check_Error(URL, Message, Code):
    #ToDo: Add platform and error to Platforms_Not_Collected
    print(f"Reports from {URL} not available because {Message} (error code {Code}).")


def API_Download_Not_Empty():
    """Prints a message indicating that the "API_Download" folder isn't empty and that it needs to be for the program to work properly, then exits the program.
    
    Returns:
        None
    """
    print("The \"API_Downloads\" folder has something in it; it must be empty for this program to work properly. Please remove everthing from that folder, then try to run this program again.")
    sys.exit()


#Subsection: Database Interactions
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


#Section: Establish Prerequisites for Script Execution
#Subsection: Confirm Folder "API_Download" is Empty
API_Download_Path = str(Path.cwd()) + r"\API_Download"
for Folder, Subfolder, Files in os.walk(API_Download_Path):
    if len(Files) > 0:
        API_Download_Not_Empty()
    elif len(Subfolder) > 0:
        API_Download_Not_Empty()

#Subsection: Initialize Variables for Reports Not Captured
#ToDo: Save the current time to variable Script_Start_Time
Platforms_Not_Collected = [] # This will contain the URLs for failed API calls

#Subsection: Create the PyMySQL Connection and SQLAlchemy Engine
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

#Subsection: Create Options Object for Chrome WebDriver
# From source: "instantiate a chrome options object so you can set the size and headless preference"
# Taken from https://medium.com/@moungpeter/how-to-automate-downloading-files-using-python-selenium-and-headless-chrome-9014f0cdd196
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--verbose')
chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "Downloads",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
})
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-software-rasterizer')

#Alert: FROM ORIGINAL REPOSITORY; path to chromedriver probably needs to be changed, probably to "../usr/local/bin/"
Path_to_ChromeDriver = Path('..', 'AppData', 'Local', 'chromedriver.exe') # For this path to work, the repo must be in the directory named for the user, and the "Local" directory must be in PATH
Chrome_Browser_Driver = webdriver.Chrome(options=chrome_options, executable_path=Path_to_ChromeDriver)


#Section: Collect Information Needed for SUSHI Call
# Later, this will be replaced with a call to the Alma API--see Credentials_Through_Alma_API.py
#ToDo: Use credential set containing comma in mock Alma API response
SUSHI_Data_File = open('SUSHI_R5_Credentials.csv','r', encoding='utf-8-sig') # Without encoding, characters added to front of first URL, causing API call to fail
SUSHI_Data = []
for Set in [SUSHI_Data_Set.rstrip().split(",") for SUSHI_Data_Set in SUSHI_Data_File]: # This turns the CSV into a list where each line is a dictionary
    try: # If none of the credential sets have a platform, the if statement below causes a key error
        if Set[4] != "":
            if Set[1] == "":
                Data = dict(URL = Set[0], api_key = Set[2], customer_id = Set[3], platform = Set[4])
            elif Set[2] == "":
                Data = dict(URL = Set[0], requestor_id = Set[1], customer_id = Set[3], platform = Set[4])
            else:
                Data = dict(URL = Set[0], requestor_id = Set[1], api_key = Set[2], customer_id = Set[3], platform = Set[4])
        else:
            if Set[1] == "":
                Data = dict(URL = Set[0], api_key = Set[2], customer_id = Set[3])
            elif Set[2] == "":
                Data = dict(URL = Set[0], requestor_id = Set[1], customer_id = Set[3])
            else:
                Data = dict(URL = Set[0], requestor_id = Set[1], api_key = Set[2], customer_id = Set[3])
    except:
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
    Credentials_String = "&".join("%s=%s" % (k,v) for k,v in Credentials.items())
    Status_Check = SUSHI_R5_API_Calls.Status(SUSHI_Call_Data["URL"], Credentials_String, Chrome_Browser_Driver)
    if str(type(Status_Check)) == "<class 'str'>": # Meaning the API call returned an error
        Platforms_Not_Collected.append(Status_Check)
        continue

    #Subsection: Check if Status_Check Returns COUNTER Error
    # https://www.projectcounter.org/appendix-f-handling-errors-exceptions/ has list of COUNTER error codes
    try: # Status_Check is JSON-like dictionary with Report_Header and information about the error
        Status_Check_Error = Status_Check["Exception"]["Severity"]
        if Status_Check_Error == "Error":
            Handle_Status_Check_Error(SUSHI_Call_Data["URL"], Status_Check["Exception"]["Message"], Status_Check["Exception"]["Code"])
            continue
        #ToDo: Potentially retry for == "Fatal" or block for == "Warning"?
    except:
        try: # Status_Check is JSON-like dictionary with nothing but information about the error
            Status_Check_Error = Status_Check["Severity"]
            if Status_Check_Error == "Error":
                Handle_Status_Check_Error(SUSHI_Call_Data["URL"], Status_Check["Message"], Status_Check["Code"])
                continue
            #ToDo: Potentially retry for == "Fatal" or block for == "Warning"?
        except:
            try: # Status_Check is a list containing a JSON-like dictionary with nothing but information about the error
                Status_Check_Error = Status_Check[0]["Severity"]
                if Status_Check_Error == "Error":
                    Handle_Status_Check_Error(SUSHI_Call_Data["URL"], Status_Check[0]["Message"], Status_Check[0]["Code"])
                    continue
                #ToDo: Potentially retry for == "Fatal" or block for == "Warning"?
            except:
                pass # If the status check passes, a KeyError is returned

    #Subsection: Get List of R5 Reports Available
    Reports_URL = SUSHI_Call_Data["URL"] + "reports" # This API returns a list of the available SUSHI reports
    Credentials_String = "&".join("%s=%s" % (k,v) for k,v in Credentials.items())
    time.sleep(0.1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this spaces out the API calls
    try:
        Available_Reports = requests.get(Reports_URL, params=Credentials_String, timeout=10)
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
        Master_Report_Type = Master_Report["Report_ID"].upper()
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
        Credentials_String = "&".join("%s=%s" % (k,v) for k,v in Credentials.items())
        time.sleep(0.1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this spaces out the API calls
        try:
            Master_Report_Response = requests.get(Master_Report_URL, params=Credentials_String, timeout=90)
            # Larger reports seem to take longer to respond, so the initial timeout interval is long
        except Timeout as error:
            try: # Timeout errors seem to be random, so going to try get request again with more time
                time.sleep(0.1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this spaces out the API calls
                Master_Report_Response = requests.get(Master_Report_URL, params=Credentials_String, timeout=120)
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
        #ToDo: Sanity check that no usage empty report makes sense here vs. empty report as indication of an issue?

        from pathlib import Path
        try:
            Namespace = str(Report_JSON['Report_Header']['Institution_ID'][0]['Value']).split(":")[0]
            File_Name = Path('Examples', 'Example_JSONs', f"{Report_JSON['Report_Header']['Report_ID']}_{Namespace}.json")
        except KeyError:
            try:
                Namespace = str(Report_JSON['Institution_ID'][0]['Value']).split(":")[0]
                File_Name = Path('Examples', 'Example_JSONs', f"{Report_JSON['Report_ID']}_{Namespace}.json")
            except KeyError:
                print(f"No Institution_ID key was found in the {Master_Report_Type} from {Master_Report_URL}.")
                continue
        with open(File_Name, 'w') as writeJSON:
            json.dump(Master_Report_Response.json(), writeJSON)
        
        """
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
        """


#Section: Retrieve List of Failed Reports
#ToDo: SELECT COUNTER_Namespace, Report_Source, Report_Type FROM sushierrorreports WHERE Time_Report_Run > Script_Start_Time (aka created after the script started running)
#ToDo: Output the results of the above to an Excel file

Connection.close()