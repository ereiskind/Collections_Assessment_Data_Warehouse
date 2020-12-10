# This outputs the contents of SUSHI_R5_Credentials.json, a file in the same folder containing a list of JSON object with the same structure as the one shown in SUSHI_R5_Credentials_Template.json, in a tabular format

import json
import csv

fileIO = open('SUSHI_R5_Credentials.csv', 'w', newline='')
CSV_Writer = csv.DictWriter(fileIO, [
    "Platform/Stats Source",
    "JSON Name",
    "Vendor_Name",
    "Covered Platforms",
    "Collection Issues",
    "Ready Notice Email",
    "URL",
    "Customer ID",
    "Requestor ID",
    "API Key",
    "SUSHI Platform Code",
    "CORAL",
])
CSV_Writer.writeheader()

with open('SUSHI_R5_Credentials.json') as JSON_File:
    Data_File = json.load(JSON_File)
    Data = []
    for Vendor in Data_File:
        Stats_Source = dict(
            CORAL = Vendor["code"],
            Vendor_Name = Vendor["name"]
        )
        for Interface in Vendor["interface"]:
            Stats_Source["Platform/Stats Source"] = Interface["description"],
            Stats_Source["Covered Platforms"] = Interface["not from Alma"]["platforms"]
            if Interface["name"] != "":
                Stats_Source["JSON Name"] = Interface["name"]
            if Interface["statistics"]["user_id"] != "":
                Stats_Source["Customer ID"] = Interface["statistics"]["user_id"]
            if Interface["statistics"]["user_password"] != "":
                Stats_Source["Requestor ID"] = Interface["statistics"]["user_password"]
            if Interface["statistics"]["online_location"] != "":
                Stats_Source["URL"] = Interface["statistics"]["online_location"]
            if Interface["statistics"]["delivery_address"] != "":
                Stats_Source["API Key"] = Interface["statistics"]["delivery_address"]
            if Interface["statistics"]["locally_stored"] != "":
                Stats_Source["SUSHI Platform Code"] = Interface["statistics"]["locally_stored"]
            if Interface["not from Alma"]["issues"] != "":
                Stats_Source["Collection Issues"] = Interface["not from Alma"]["issues"]
            if Interface["not from Alma"]["notification"] != "":
                Stats_Source["Ready Notice Email"] = Interface["not from Alma"]["notification"]
            CSV_Writer.writerow(Stats_Source)