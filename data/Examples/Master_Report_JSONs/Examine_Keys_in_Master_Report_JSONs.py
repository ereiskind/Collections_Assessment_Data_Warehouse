# Loops through all of the JSONs in the folder; for each one, pulls "Report_Header:Created_By" and "Report_Header:Institution_ID:Value" for Institution_ID Type=Proprietary, then creates a CSV row for each instance of "Report_Items:Platform" with the above data points included

import os
import json

#Section: Initialize Lists
JSON_File_Names = []
CSV_Records = []


#Section: Open JSON
Current_Folder = os.path.dirname(os.path.realpath(__file__)) # Goes down to this specific subfolder--getcwd pulls all folders, including git
for Folder, Subfolders, Files in os.walk(Current_Folder):
    for File in Files:
        if File.endswith(".json"):
            JSON_File_Names.append(File)

for File in JSON_File_Names:
    File_Path = os.path.dirname(os.path.realpath(__file__)) + "\\" + File
    with open(File_Path) as JSON_File:
        JSON_Dictionary = json.load(JSON_File)


#Section: Read Data from JSON Dictionary
#Subsection: Read Data from Header
#ToDo: Get JSON_Dictionary['Report_Header']['Created_By'], a string, and save as the report creator
#ToDo: Get JSON_Dictionary['Institution_ID'], a list of dictionaries, and save the dictionary where "Type": "Proprietary" to a variable
#ToDo: From the above variable, get the value for the key 'Value'

#Subsection: Get List of Platforms
#ToDo: Get JSON_Dictionary['Report_Items'], a list of dictionaries, and save to an iterable
#ToDo: Iterate through the above, pulling the value for the key 'Platform' and saving it to a list
#ToDo: Dedupe list (use list comprehension?)


#Section: Create CSV Record
#ToDo: Create dictionaries representing rows of CSV with report creator, report proprietary ID, and platform by looping through list of platforms and making a record/dictionary for each platform 