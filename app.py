#API repository: https://app.swaggerhub.com/apis/COUNTER/counter-sushi_5_0_api/1.0.0

import requests
import json
import csv
import requests
from requests import HTTPError, Timeout

#Section: Collect Information Needed for SUSHI Call
SUSHI_Data_File = open('SUSHI_R5_Credentials.csv','r')
SUSHI_Data = []
for Set in [SUSHI_Data_Set.rstrip().split(",") for SUSHI_Data_Set in SUSHI_Data_File]: # This turns each line oc the CSV into a dictionary within a list
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
    except HTTPError as error:
        print(f"HTTP Error: {format(error)}")
        #ToDo: 403 error seems to be invalid credentials--perhaps create specific error message for that?
        continue
    except Timeout as error:
        print(f"Server didn't respond after 10 seconds ({format(error)}).")
        continue
    except:
        print(f"Some error other than a status error or timout occurred when trying to access {Status_URL}.")
        continue
    #Alert: Silverchair, which uses both Requestor ID and API Key, generates a download when the SUSHI URL is entered rather than returning the data on the page itself; as a result, requests can't find the data

    #Subsection: Get List of R5 Reports Available
    Reports_URL = SUSHI_Call_Data["URL"] + "reports"
    try:
        Available_Reports = requests.get(Reports_URL, params=Credentials, timeout=10)
    except Timeout as error:
        print(f"Server didn't respond to request for list of available reports after 10 seconds ({format(error)}).")
        continue
    
    Available_Master_Reports = [] # This list will contain the dictionaries for the master reports available on the platform, which will be the only reports pulled
    for Report in json.loads(Available_Reports.text):
        if "Master Report" in Report["Report_Name"]:
            Available_Master_Reports.append(Report)
    
    #Subsection: Collect Reports
    for Master_Report in Available_Master_Reports:
        try:
            Master_Report_Response = requests.get(Master_Report["Path"], params=Credentials, timeout=10)
        except Timeout as error:
            print(f"Server didn't respond to request for {Master_Report["Report_Name"]} after 10 seconds ({format(error)}).")
            continue
        print(Master_Report_Response)
    #ToDo: For each item in available reports tuple, request report with as much detail as possible
    #ToDo: Save reports





















"""
#Section: Class "Collection Category"
#This class assumes all are SUSHI R5 compliant--actual dashboard backend will have master class and subclasses for each type of collection
class Collection_Category:
    #Subsection: attributes with constructor and getter methods
    def __init__(self, **kwargs): #This will initialize all arguments with variables assigned to them when the instance of the class is created
        self._BaseURL = kwargs['BaseURL']
        self._CustomerID = kwargs['CustomerID'] #In the CORAL password field
        self._RequestorID = kwargs['RequestorID'] if 'RequestorID' in kwargs else None #In the CORAL username field
        self._APIKey = kwargs['APIKey'] if 'APIKey' in kwargs else None #In the CORAL username field unless requestor ID also required, then in notes section

    def BaseURL(self):
        return self._BaseURL

    def CustomerID(self):
        return self._CustomerID

    def RequestorID(self):
        return self._RequestorID

    def APIKey(self):
        return self._APIKey

    #Subsection: methods
    #Todo: determine if having some different params in same CORAL field would be more easily handled by creation of subclasses for each use case instance
    def Call_Parameters_without_Dates(self):
        #Pairs where value is null seem to be ignored as params in requests.get
        Parameters = {
            'customer_id': self._CustomerID,
            'requestor_id': self._RequestorID,
            'api_key': self._APIKey
        }
        return Parameters

#Section: Write Returned JSON to CSV
#Todo: need to update so file title will have report name in it
def Write_JSON_to_CSV(ReturnedJSON, ReportType, CollectionCategory):
    #ReturnedJSON: what was returned by API call after json.dumps
    #ReportType: the R5 report type
    #CollectionCategory: the resource(s) the stats in the JSON are for
    with open("filename.csv", mode='w') as CSV: #Context manager automatically closes file when code block ends
        #Todo: add ReportType and CollectionCategory to name of CSV created
        CSVWriter = csv.writer(CSV)
        CSVWriter.writerow(ReturnedJSON)

#Section: Initialize
#Todo: determine if the call is automated or manual; if latter, present report filters
#Todo: determine what source is being collected
Collection_Category_Name = input("What category is being called? ")

#Section: SUSHI Information
#Todo: initialize instance of "Collection Category" with information from CORAL
BURL = input("Base URL: ")
CID = input("Customer ID: ")
VerificationType = input("Enter \"1\" if there's a requestor ID, \"2\" if there's an API key, or \"3\" if both are used. ")
VerificationType = int(VerificationType) #No user input error check beyond this
if VerificationType == 1:
    RID = input("Requestor ID: ")
    Collection_Category_Name = Collection_Category(BaseURL = BURL, CustomerID = CID, RequestorID = RID)
elif VerificationType == 2:
    APIK = input("API Key: ")
    Collection_Category_Name = Collection_Category(BaseURL = BURL, CustomerID = CID, APIKey = APIK)
elif VerificationType == 3:
    RID = input("Requestor ID: ")
    APIK = input("API Key: ")
    Collection_Category_Name = Collection_Category(BaseURL = BURL, CustomerID = CID, RequestorID = RID, APIKey = APIK)

#Section: Status(?)
StatusURL = Collection_Category_Name.BaseURL() + '/status'
StatusResult = requests.get(StatusURL, params=Collection_Category_Name.Call_Parameters_without_Dates())
print(StatusResult) #Returns status code--checks if everthing's OK
StatusResult = json.dumps(StatusResult.json(), indent=4) #Returns JSON result of API call and transforms it into JSON; indent argument formats output"""