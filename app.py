#API repository: https://app.swaggerhub.com/apis/COUNTER/counter-sushi_5_0_api/1.0.0

import logging
from pathlib import Path
import json
import csv
import time
import os
import sys
import requests
from requests import HTTPError, Timeout
from tkinter import messagebox
import pandas
import pymysql
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#Alert: FROM ORIGINAL REPOSITORY with flat structure; these files are now at different locations
import Database_Credentials # Loaded in from runtime environment repository at Collections_Assessment_Data_Warehouse/data/Database_Credentials.py
import SUSHI_R5_API_Calls # In this repository at Collections_Assessment_Data_Warehouse/helpers/SUSHI_R5_API_Calls.py


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
    Response_to_Problem = messagebox.askyesno(title="Status Check Problem", message=f"The status check for {Source} contained the following {Type}:\n\n{Message}\n\nShould the usage for this platform be collected?")
    if not Response_to_Problem: # This code block needs to run if the answer to the above is no, which produces the Boolean False
        Problem_Message = f"Canceled collection from interface with {Type}: {Message}"
        Capture_Problem = dict(
            Interface = Source,
            Type = "status",
            Details = Problem_Message,
        )
        Platforms_Not_Collected.append(Capture_Problem)
        logging.info(f"Added to Platforms_Not_Collected: {Source}|{Report}|{Problem_Message}")
        return True
    return False


def Handle_Exception_Master_Report(Source, Report, Exception_List, Load_Report_Items = False):
    """Handles results of a SUSHI API call for a master report that is or contains exceptions.
    
    The function parses the list of exceptions, remaking each exception into a string. Then, if the response contained a Report_Items section, it asks if the usage should be loaded into the database. Finally, if the usage isn't to be loaded into the database, the report is added to Platforms_Not_Collected and the corresponding log statement is output to the terminal. Note that because there are two different possible parmeters for including parent details, "include_parent_details" and "include_component_details", which an item report might use, most item reports will require handling through this function.
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
        #ToDo: Check how the messagebox formatting works and adjust if necessary
        Load_Report_Items = messagebox.askyesno(title="Exception Raised", message=f"The {Report} for {Source} contained the following exception(s):\n\n{List_of_Exceptions}\n\nShould this report be added to the database?")
    if not Load_Report_Items: # This code block needs to run if the answer to the above is no, which produces the Boolean False
        Problem_Message = f"Cancelled collection because of exception(s) {'|'.join(List_of_Exceptions)}"
        Capture_Problem = dict(
            Interface = Source,
            Type = Report,
            Details = Problem_Message,
        )
        Platforms_Not_Collected.append(Capture_Problem)
        logging.info(f"Added to Platforms_Not_Collected: {Source}|{Report}|{Problem_Message}")
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
def Load_Dataframe_into_MySQL(Dataframe, DBTable, DBEngine):
    """A pandas to_sql function call bracketed by the creation and destruction of a SQLAlchemy session object.
    
    This function loads the data contained in Dataframe into DBTable, which is in the MySQL database referenced by DBEngine. Dataframe's record index values aren't included.
    
    Arguments:
        Dataframe {pandas dataframe} -- dataframe to be loaded into MySQL
        DBTable {string} -- name of the MySQL table (relation) the data's being loaded into
        DBEngine {SQLAlchemy engine} -- engine object for MySQL database
    
    Returns:
        None
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
    
    Returns:
        None
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
Platforms_Not_Collected = []
    # This will contain the URLs for failed API calls that prevented any reports from being collected
    # Format: SUSHI base URL|Source of problem|Error that caused failure

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
with open('SUSHI_R5_Credentials.json') as JSON_File:
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


#Section: Make API Calls for Status and Reports
for SUSHI_Call_Data in SUSHI_Data:
    # These list comprehensions create another dictionary with just the content needed for the URL's query string--two are used because combining the Boolean expressions wasn't working
    #ToDo: Try to combine Boolean expressions at end for a single list comprehension
    Credentials = {key: value for key, value in SUSHI_Call_Data.items() if key != "URL"}
    Credentials = {key: value for key, value in Credentials.items() if key != "JSON_Name"}
    logging.info(f"Making API calls starting with {SUSHI_Call_Data['URL']}")

    #Subsection: Determine SUSHI Availability
    Credentials_String = "&".join("%s=%s" % (k,v) for k,v in Credentials.items())
    Status_Check = SUSHI_R5_API_Calls.Single_Element_API_Call("status", SUSHI_Call_Data["URL"], Credentials_String, Chrome_Browser_Driver)
    if str(type(Status_Check)) == "<class 'str'>": # Meaning the API call returned an error
        Platforms_Not_Collected.append(Status_Check)
        logging.info("Added to Platforms_Not_Collected: " + Status_Check)
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
    Available_Reports = SUSHI_R5_API_Calls.Single_Element_API_Call("reports", SUSHI_Call_Data["URL"], Credentials_String, Chrome_Browser_Driver)
    if str(type(Available_Reports)) == "<class 'str'>": # Meaning the API call returned an error
        Platforms_Not_Collected.append(Available_Reports)
        logging.info("Added to Platforms_Not_Collected: " + Available_Reports)
        continue
    # This creates a list of all the reports offered by a platform excluding the consortium reports offered by Silverchair, which have a Report_ID value of "Silverchair:CR_??"
    Available_Reports_List = []
    for Report in Available_Reports:
        #ToDo: This is raising a KeyError in a small number of interfaces--figure out reason and how to handle the error
        if "Silverchair:CR" not in Report["Report_ID"]:
            Available_Reports_List.append(Report["Report_ID"])
    
    Available_Master_Reports = [] # This list will contain the dictionaries from the JSON for the master reports available on the platform, which will be the only reports pulled
    for Report in Available_Reports:
        if "_" not in Report["Report_ID"]:
            Available_Master_Reports.append(Report)
    if Available_Master_Reports == []:
        Platforms_Not_Collected.append(SUSHI_Call_Data["URL"] + "|reports|No master reports available")
        logging.info("Added to Platforms_Not_Collected: " + SUSHI_Call_Data["URL"] + "|reports|No master reports available")
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
            Platforms_Not_Collected.append(Extra_Report_Problem) 
        logging.info(f"Added to Platforms_Not_Collected: {SUSHI_Call_Data['JSON_Name']}|{Report}|Standard report based on master report not offered")
    
    logging.info(f"Master report list collection successful: {len(Available_Master_Reports)} reports")

    #Section: Make API Calls for Individual Master Reports
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
            # If either of the below is in the parameters but isn't used by the platform, it's presence will add a 3050 warning to the JSON; since there's no good way to tell which IRs use which parameter, using both and handling the error in Handle_Exception_Master_Report is the best option
            Credentials["include_parent_details"] = "True"
            Credentials["include_component_details"] = "True"
        else:
            messagebox.showwarning(title="Invalid Master Report Type", message=f"{SUSHI_Call_Data['JSON_Name']} contained a {Master_Report['Report_Name']}. Work out further report type handling.") # This message shouldn't ever appear
            continue
        logging.info(f"Ready to call {SUSHI_Call_Data['URL']} for {Master_Report_Type}.")

        Credentials_String = "&".join("%s=%s" % (k,v) for k,v in Credentials.items())
        Master_Report_Response = SUSHI_R5_API_Calls.Master_Report_API_Call(Master_Report_Type, SUSHI_Call_Data["URL"], Credentials_String, Chrome_Browser_Driver)
        if str(type(Master_Report_Response)) == "<class 'str'>": # Meaning the API call returned an error
            Master_Report_Response_Problem = dict(
                Interface = SUSHI_Call_Data["JSON_Name"],
                Type = Master_Report_Response.split("|")[0],
                Details = Master_Report_Response.split("|")[1],
            )
            Platforms_Not_Collected.append(Master_Report_Response_Problem)
            logging.info(f"Added to Platforms_Not_Collected: {SUSHI_Call_Data['JSON_Name']}|" + Master_Report_Response)
            continue

        #Subsection: Handle Master Reports with Exceptions
        try: # Master_Report_Response is JSON-like dictionary with top-level key of "Report_Header" that includes the key "Exceptions"
            Master_Report_Exception = Master_Report_Response["Report_Header"]["Exceptions"]
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
                # Based on observed close-to-standard behavior, an interface could return a list of multiple Exception dictionaries, which JSON_to_Python_Data_Types would handle as an error, directing it to the Platforms_Not_Collected list. If that happens, error handling for that situation may be better handled within the JSON_to_Python_Data_Types function.
                pass # A SUSHI JSON without an "Exceptions" key will return a KeyError for the above

        #ToDo: If len(Master_Report_Response["Report_Items"]) == 0 (aka no usage reported), possible sanity check on that?

        logging.info(f"API call to {SUSHI_Call_Data['URL']} for {Master_Report_Type} successful: {len(Master_Report_Response['Report_Items'])} resources")

        #Subsection: Save Individual Reports as JSON
        File_Name = Path('Examples', 'Example_JSONs', f"{Master_Report_Response['Report_Header']['Report_ID']}_{SUSHI_Call_Data['JSON_Name']}.json")
        with open(File_Name, 'w') as writeJSON:
            json.dump(Master_Report_Response, writeJSON)
            logging.info(f"{File_Name} created.")
        
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

Connection.close()

#Section: Output Platforms_Not_Collected
#Alert: The CSV below needs to be written to the data folder
FileIO = open('Platforms_Not_Collected.csv', 'w', newline='')
CSV_Writer = csv.DictWriter(FileIO, [
    #ToDo: Decide if there are better column names to use and/or if more columns are needed
    "Interface", # The interface where there was a problem
    "Type", # The type of error
    #ToDo: Develop fixed vocabulary for "Type"
    "Details", # the details of the error
    #ToDo: Determine what should and shouldn't go in details, and make other columns if necessary
])
CSV_Writer.writeheader()

for Platform in Platforms_Not_Collected:
    CSV_Writer.writerow(Platform)

FileIO.close()
#ToDo: Figure out how to open CSV so it stays open when program exits--os.startfile closes file at program exit