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

#Section: Initialize Lists
JSON_File_Names = []
CSV_Records = []


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
            CSV_Record['Resource_Platform'] = "Empty report"
            CSV_Records.append(CSV_Record)
            continue

        for Platforms in JSON_Dictionary['Report_Items']:
            for Key, Value in Platforms.items():
                if Key == "Platform":
                    CSV_Record['Resource_Platform'] = Value
                    CSV_Records.append(CSV_Record)

#Section: Create CSV
CSV_File_Path = Path('Examples', 'Example_JSONs', 'JSON_Keys.csv')
CSV = open(CSV_File_Path, 'w', newline='')
CSV_Writer = csv.DictWriter(CSV, [
    'Source_JSON', # Contains the name of the JSON file the data came from
    'Report_Creator', # Contains the Created_By value
    'Report_Type', # Contains the master report ID
    'Source_COUNTER_Namespace', # Contains the COUNTER namespace for the source of the report
    'Resource_Platform' # Contains the platform
])
CSV_Writer.writeheader()
for Record in CSV_Records:
    CSV_Writer.writerow(Record)