#API repository: https://app.swaggerhub.com/apis/COUNTER/counter-sushi_5_0_api/1.0.0

import requests
import json
import csv

#Section: Collect Information Needed for SUSHI Call
SUSHI_Credentials_File = open('SUSHI_R5_Credentials.csv','r')
SUSHI_Credentials = []
for Set in [SUSHI_Credential_Set.rstrip().split(",") for SUSHI_Credential_Set in SUSHI_Credentials_File]: # This turns each line oc the CSV into a dictionary within a list
    if Set[1] == "":
        Credentials = dict(URL = Set[0], APIKey = Set[2], CustomerID = Set[3])
    elif Set[2] == "":
        Credentials = dict(URL = Set[0], RequestorID = Set[1], CustomerID = Set[3])
    else:
        Credentials = dict(URL = Set[0], RequestorID = Set[1], APIKey = Set[2], CustomerID = Set[3])
    SUSHI_Credentials.append(Credentials)

# print(SUSHI_Creds_File.readline())
# print("something")
# print(SUSHI_Creds_File.readline())

#ToDo: Save SUSHI creds for use in multiple API calls
# Methiod for saving creds should also handle if call needs requestor ID and/or API key


#Section: Determine Reports Available
#Subsection: Determine SUSHI Availability
#ToDo: Run API call for status
#ToDo: If return value not 200, break and return error message to user

#Subsection: Get List of R5 Reports Available
#ToDo: Run API call for list of available R5 reports
#ToDo: Save results into a tuple


#Section: Collect Reports
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