# The Runtime Environment Repository
Instead of using a standard virtual environment, this repository runs in a series of Docker containers, where the Python container serves the functions of the virtual environment. A second Git repository on a local machine or in a shared folder contains the Dockerfiles and Docker Compose file and files with private information used by the programs in this repository.

## The File Overlay Process
The complete contents of the Collections_Assessment_Data_Warehouse folder, described in Repository_Contents.md, are created by cloning the GitHub repository of the same name at https://github.com/ereiskind/Collections_Assessment_Data_Warehouse.git into this Docker container and then copying files from the runtime environment into this container at paths that coincide with the file structure of the above repository. For example, if the GitHub repository contains a directory ./root/repo/foo with no subdirectories, and the Python container Dockerfile contains instructions to copy files into a directory ./root/repo/foo/bar, when the contents of the container are viewed, ./root/repo/foo will have a subdirectory bar with files from the host machine. Including the files added to the container though that process to the .gitignore keeps them from being added to the GitHub repository.

### Creating "Database_Credentials.py"
One of the files added to the GitHub repository's file structure in the container through the above process is "Database_Credentials.py". It sets four variables:
- `Username`: the username for the account being used to access the database; with the Dockerfile provided, the database's only user is "root"
- `Password`: the password assigned to the username; in the sample Dockerfile provided, the user "root" was given the password "root"
- `Host`: the host name of the MySQL container given in the Docker Compose file; in the sample, this is "database"
- `Post`: the external port assigned to the MySQL container in the Docker Compose file; in the sample, this is "3306"

## The Runtime Environment Repository File Structure
Note: Italics represent snips

Collections_Assessment_Data_Warehouse_Runtime/
┣ Example_Data/
┃ ┣ Master_Report_JSONs/
┃ ┃ ┗ *sample DR, IR, PR, and TR from a selection of vendors*
┃ ┗ Samples/
┃   ┣ Alma_Vendor_API_Call_Sample.json (response to Vendor GET request to Alma API sandbox)
┃   ┣ Alma_Vendor_Common_Keys.json (JSON elements common to Alma_Vendor_API_Call_Sample and Alma_Vendor_Sample)
┃   ┣ Alma_Vendor_Sample.json (example response to Vendor GET request on Alma website)
┃   ┣ Error_Sample.json (COUNTER report with Exceptions in Report_Header and no Report_Items)
┃   ┣ Exceptions_Sample.json (COUNTER report with Exceptions in Report_Header and Report_Items)
┃   ┣ Report_List_Sample.json (COUNTER response to /reports GET request)
┃   ┣ Status_Check_Alert_Sample.json (COUNTER response to /status GET request with an alert value)
┃   ┣ Status_Check_Error_Sample.json  (COUNTER response to /status GET request containing Exception)
┃   ┗ Status_Check_Sample.json (COUNTER response to /status GET request)
┣ mysql/
┃ ┣ Dockerfile (the Dockerfile to create the MySQL container)
┃ ┗ Version_0.1_DDL.sql (the SQL statements to create the schema for the database and load in any information wanted in the database at initialization)
┣ Private_Info/
┃ ┣ Data_Warehouse_Data/
┃ ┃ ┗ *the CSVs containing the raw data for inclusion in the data warehouse entities other than "R5_Usage"*
┃ ┣ Database_Credentials.py (see "Creating Database_Credentials.py" above)
┃ ┗ SUSHI_R5_Credentials.json (a list of the SUSHI credentials for all available resources formatted according to SUSHI_R5_Credentials_Template.json)
┣ docker-compose.yml (the Docker Compose file)
┣ Dockerfile (the Dockerfile to create the Python container)
┣ README.md
┗ requirements.txt (the list of Python packages)

The copy statements at the end of docs/Runtime_Environment/Python_Dockerfile.txt can serve as a complete mapping of what files from the above structure are available in this repository and where those files are located.

## Alternate Methods for Accessing Containers
Below are alternate methods for accessing the contents of the runtime environment containers other than through VSCode.

### Accessing the MySQL Container via CLI
1. Open the host CLI
2. `docker exec -it mysql-container mysql --user=root --password`
3. Enter the password for the root user set in the MySQL Dockerfile

### Accessing the MySQL Container via MySQL Workbench
1. Open the MySQL container in the CLI
2. SQL prompt: `CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';` where "user" and "password" are the desired username and password
3. SQL prompt: `GRANT ALL PRIVILEGES ON * . * TO 'user'@'localhost';`
4. SQL prompt: `UPDATE mysql.user SET host = '%' WHERE user = 'user';`
5. SQL prompt: `exit`
6. `docker restart mysql-container`
7. Open MySQL Workbench and click the plus icon
8. Add a Connection Name
9.  Change the Hostname to "localhost"
10. Change the Username to the value of "user" created in step four
11. Add the password created in step two to the vault

### Accessing the Python Container via CLI
1. Open the host CLI
2. `docker exec -it python-container bash`
3. Bash prompt: `python`