# File Structure Information
This file structure tree is generated with the File Tree to Text Generator; it's the ASCII version. File/folder names in bold are files/folders brought into the container via the file overlay process and saved to the GitHub repository; file/folder names in italics are those brought in through the overlay process and included in the .gitignore file.
*For the program to work, the directory must have properly formatted Collections_Assessment_Data_Warehouse/data/Database_Credentials.py and Collections_Assessment_Data_Warehouse/data/SUSHI_R5_Credentials.json files. See Runtime_Environment.md and SUSHI_R5_Credentials_Template.json respectively for more information.*

Collections_Assessment_Data_Warehouse/
┣ data/
┃ ┣ *DML_CSVs/* (the CSVs containing the raw data for inclusion in the data warehouse entities other than "R5_Usage")
┃ ┣ Examples/
┃ ┃ ┣ *Master_Report_JSONs/* (sample DR, IR, PR, and TR from a selection of vendors)
┃ ┃ ┣ *Alma_Vendor_API_Call_Sample.json* (response to Vendor GET request to Alma API sandbox)
┃ ┃ ┣ *Alma_Vendor_Common_Keys.json** (JSON elements common to Alma_Vendor_API_Call_Sample and Alma_Vendor_Sample)
┃ ┃ ┣ **Alma_Vendor_Sample.json* (example response to Vendor GET request on Alma website)
┃ ┃ ┣ *Error_Sample.json* (COUNTER report with Exceptions in Report_Header and no Report_Items)
┃ ┃ ┣ *Exceptions_Sample.json* (COUNTER report with Exceptions in Report_Header and Report_Items)
┃ ┃ ┣ *Report_List_Sample.json* (COUNTER response to /reports GET request)
┃ ┃ ┣ *Status_Check_Alert_Sample.json* (COUNTER response to /status GET request with an alert value)
┃ ┃ ┣ *Status_Check_Error_Sample.json* (COUNTER response to /status GET request containing Exception)
┃ ┃ ┗ *Status_Check_Sample.json* (COUNTER response to /status GET request)
┃ ┣ SQL_Output/
┃ ┣ Create_Insert_Statements_for_Non-SUSHI_Data.py
┃ ┣ Create_Table_from_SUSHI_Credentials_JSON.py
┃ ┣ *Database_Credentials.py* (the credentials for the MySQL database)
┃ ┣ *SUSHI_R5_Credentials.json* (a list of the SUSHI credentials for all available resources formatted according to SUSHI_R5_Credentials_Template.json)
┃ ┗ Useful_SQL_Statements.sql
┣ docs/
┃ ┣ Runtime_Environment/
┃ ┃ ┣ **Data_Warehouse_DDL_Statements.sql** (the DDL statements used to create the connected database)
┃ ┃ ┣ **Docker_Compose.txt** (the contents of the docker-compose.yml creating the runtime environment)
┃ ┃ ┣ **MySQL_Dockerfile.txt** (the contents of the Dockerfile creating the MySQL container)
┃ ┃ ┣ **Python_Dockerfile.txt** (the contents of the Dockerfile creating the Python container)
┃ ┃ ┗ Runtime_Environment.md
┃ ┣ About_COUNTER.md
┃ ┣ Data_Saved_in_Warehouse.md
┃ ┣ Non-COUNTER_Resources.md
┃ ┣ Repository_Contents.md
┃ ┣ Resources.md
┃ ┣ SUSHI_R5_Credentials_Template.json
┃ ┣ User_Stories.md
┃ ┗ **requirements.txt** (Python dependencies)
┣ helpers/
┃ ┣ Authentication_Log_Collection.py
┃ ┣ Create_Master_Report_Dataframes.py
┃ ┣ Credentials_Through_Alma_API.py
┃ ┣ Get_Downloading_JSONs.py
┃ ┣ SUSHI_Call_Upon_Email_Alert_that_Stats_Are_Ready.py
┃ ┗ SUSHI_R5_API_Calls.py
┣ .gitignore
┣ README.md
┣ app.py
┣ SQL_Query_to_CSV.py
┗ SUSHI_R5_Interfaces_and_Credentials.py

To turn app.py into a script for downloading the JSON files, with only one interface in SUSHI_R5_Credentials.json, add the below to the end of "Subsection: Return Notice for Empty Reports" (~ line 486) and comment out the remainder of the program with three double quotes

with open(f'{Master_Report_Type}.json', 'w') as WriteJSON:
    json.dump(Master_Report_Response, WriteJSON)