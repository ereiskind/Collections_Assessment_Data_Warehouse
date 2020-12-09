# Loops through all of the JSONs in the folder; for each one, pulls "Report_Header:Created_By" and "Report_Header:Institution_ID:Value" for Institution_ID Type=Proprietary, then creates a CSV row for each instance of "Report_Items:Platform" with the above data points included

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

        #Subsection: Read Data from Header
        CSV_Record['Report_Creator'] = JSON_Dictionary['Report_Header']['Created_By']
        try:
            for ID in JSON_Dictionary['Report_Header']['Institution_ID']:
                if ID['Type'] == "Proprietary":
                    CSV_Record['ID'] = ID['Value'].split(":")[0]
        except KeyError:
            CSV_Record['ID'] = None

        #Subsection: Get List of Platforms
        for Platforms in JSON_Dictionary['Report_Items']:
            for Platform in Platforms:
                print(CSV_Record)
                print(Platform['Platform']) #Got "indices must be interger" error
        #ToDo: Get , a list of dictionaries, and save to an iterable
        #ToDo: Iterate through the above, pulling the value for the key 'Platform' and saving it to a list
        #ToDo: Dedupe list (use list comprehension?)


#Section: Create CSV
#ToDo: Create CSV using CSV_Records