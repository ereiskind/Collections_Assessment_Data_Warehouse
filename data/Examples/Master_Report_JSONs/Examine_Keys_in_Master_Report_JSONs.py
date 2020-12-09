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
    with open(File_Path) as JSON_File:
        JSON_Dictionary = json.load(JSON_File)


        #Section: Read Data from JSON Dictionary
        CSV_Record = {}
        # CSV_Record['Report_Creator'] contains the Created_By value
        # CSV_Record['Report'] contains the master report ID
        # CSV_Record['ID'] contains the COUNTER namespace for the source of the report
        # CSV_Record['Platform'] contains the platform

        #Subsection: Read Data from Header
        CSV_Record['Report_Creator'] = JSON_Dictionary['Report_Header']['Created_By']
        CSV_Record['Report'] = JSON_Dictionary['Report_Header']['Report_ID']

        try:
            for ID in JSON_Dictionary['Report_Header']['Institution_ID']:
                if ID['Type'] == "Proprietary":
                    CSV_Record['ID'] = ID['Value'].split(":")[0]
        except KeyError:
            if ":" in JSON_Dictionary['Report_Header']['Customer_ID']:
                CSV_Record['ID'] = JSON_Dictionary['Report_Header']['Customer_ID'].split(":")[0]
            else:
                CSV_Record['ID'] = "No COUNTER Namespace"

        #Subsection: Get List of Platforms
        if len(JSON_Dictionary['Report_Items']) == 0: # If the Report_Items section is empty
            CSV_Record['Platform'] = "Empty report"
            continue
        
        for Platforms in JSON_Dictionary['Report_Items']:
            List_of_Platforms = []
            for Key, Value in Platforms.items():
                print(CSV_Record)
                if Key == "Platform":
                    List_of_Platforms.append(Value)
                print(List_of_Platforms)
        #ToDo: Dedupe list (use list comprehension?)--all the List_of_Platform values for the samples contain a single platform--inspect SAGE/CQ and Oxford, get a mix of types of master reports

#Section: Create CSV
#ToDo: Create CSV using CSV_Records