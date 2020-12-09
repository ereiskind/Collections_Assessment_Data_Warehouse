# Loops through all of the JSONs in the folder; for each one, pulls "Report_Header:Created_By" and "Report_Header:Institution_ID:Value" for Institution_ID Type=Proprietary, then creates a CSV row for each instance of "Report_Items:Platform" with the above data points included

"""To obtain JSONs, the following goes at the very end of the "Make API Calls" section of app.py:

from pathlib import Path
print(type(Report_JSON))
Namespace = str(Report_JSON['Report_Header']['Institution_ID'][0]['Value']).split(":")[0]
File_Name = Path('Examples', 'Example_JSONs', f"{Report_JSON['Report_Header']['Report_ID']}_{Namespace}.json")
with open(File_Name, 'w') as writeJSON:
    json.dump(Master_Report_Response.json(), writeJSON)
"""

import os
import json
from pathlib import Path
import csv


#Section: Functions
def Move_Key_Value_Pairs(Old_Dict, New_Dict):
    """This function moves all key-value pairs in Old_Dict into New_Dict.
    Arguments:
        Old_Dict {dictionary} -- dictionary with key-value pairs to be moved
        newDict {dictionary} -- dictionary to receive new key-value pairs
    """
    for Key, Value in Old_Dict.items():
        New_Dict[Key] = Value


#Section: Initialize Lists
JSON_File_Names = []
CSV_Record_List = []


#Section: Open JSON
#Subsection: Get list of JSON Files in Folder
Current_Folder = os.path.dirname(os.path.realpath(__file__)) # Goes down to this specific subfolder--getcwd pulls all folders, including git
for Folder, Subfolders, Files in os.walk(Current_Folder):
    for File in Files:
        if File.endswith(".json"):
            JSON_File_Names.append(File)

#Subsection: Loop Through Opening JSON Files in Folder
for File in JSON_File_Names:
    File_Path = os.path.dirname(os.path.realpath(__file__)) + "\\" + File
    with open(File_Path, encoding='utf8') as JSON_File:
        JSON_Dictionary = json.load(JSON_File)


        #Section: Read Data from JSON Dictionary
        Header_Data = {}
        Header_Data['Source_JSON'] = File
        
        #Subsection: Read Data from Header
        Header_Data['Report_Creator'] = JSON_Dictionary['Report_Header']['Created_By']
        Header_Data['Report_Type'] = JSON_Dictionary['Report_Header']['Report_ID']

        try:
            for ID in JSON_Dictionary['Report_Header']['Institution_ID']:
                if ID['Type'] == "Proprietary":
                    Header_Data['Source_COUNTER_Namespace'] = ID['Value'].split(":")[0]
        except KeyError:
            if ":" in JSON_Dictionary['Report_Header']['Customer_ID']:
                Header_Data['Source_COUNTER_Namespace'] = JSON_Dictionary['Report_Header']['Customer_ID'].split(":")[0]
            else:
                Header_Data['Source_COUNTER_Namespace'] = "No COUNTER Namespace"

        #Subsection: Get List of Platforms
        if len(JSON_Dictionary['Report_Items']) == 0: # If the Report_Items section is empty
            CSV_Record = {}
            Move_Key_Value_Pairs(Header_Data, CSV_Record)
            CSV_Record['Resource_Platform'] = "Empty report"
            CSV_Record_List.append(CSV_Record)
            continue

        Platform_List = []
        for Platforms in JSON_Dictionary['Report_Items']:
            for Key, Value in Platforms.items():
                if Key == "Platform":
                    Platform_List.append(Value)
        
        CSV_Record = {}
        Move_Key_Value_Pairs(Header_Data, CSV_Record)
        for Found_Platform in Platform_List:
            CSV_Record['Resource_Platform'] = Found_Platform
            #ToDo: When the above step runs, the 'Resource_Platform' values within both CSV_Record and all the dictionaries within CSV_Record_List change--desired behavior is only the former changes

#Section: Create CSV
for Record in CSV_Record_List:
    print(Record)