# The Runtime Environment Repository
Instead of using a standard virtual environment, this repository runs in a series of Docker containers, where the Python container serves the functions of the virtual environment. A second Git repository on a local machine or in a shared folder contains the Dockerfiles and Docker Compose file and files with private information used by the programs in this repository.

## The File Overlay Process
While the programming functionality and documentation for the data warehouse are stored in a public Git repo, the runtime folder--the folder from which the Docker containers are launched--contains the following prerequisite data:

- The Dockerfiles for the Python and MySQL containers, and the Docker Compose file for building them together
- The SQL files for creating and loading the database
- The list of Python dependencies
- The JSON with the SUSHI credentials
- The Python file with the credentials for accessing the database

The above files, as well as other documentation and examples containing private information, are combined with the files in the public repo through a file overlay process where files in the runtime folder are copied into the Docker containers through "copy" commands in the Dockerfiles. For example, if the container contains a directory ./root/repo/foo with no subdirectories, and a Dockerfile contains instructions to copy files into a directory ./root/repo/foo/bar, when the contents of the container are viewed, ./root/repo/foo will have a subdirectory bar with files from the host machine.

For a complete list of the runtime folder's content, see "The Runtime Environment Repository File Structure."

### Creating the Application
The functionality of the data warehouse is in the Python container's Collections_Assessment_Data_Warehouse folder, described in Repository_Contents.md, which is created by cloning the GitHub repository of the same name at https://github.com/ereiskind/Collections_Assessment_Data_Warehouse.git into the container and then copying files saved in the runtime folder for privacy reasons into that container at paths that coincide with the file structure of the above repository. All files in the Collections_Assessment_Data_Warehouse folder, including those added through the file overlay process, will be committed to the public repo unless added to the .gitignore file.

#### Creating "Database_Credentials.py"
One of the files added to the GitHub repository's file structure in the container through the above process is "Database_Credentials.py". It sets four variables:
- `Username`: the username for the account being used to access the database; with the Dockerfile provided, the database's only user is "root"
- `Password`: the password assigned to the username; in the sample Dockerfile provided, the user "root" was given the password "root"
- `Host`: the host name of the MySQL container given in the Docker Compose file; in the sample, this is "database"
- `Post`: the external port assigned to the MySQL container in the Docker Compose file; in the sample, this is "3306"

### Creating the Database
The database can be constructed and pre-populated through the file overlay process. Copying SQL files to the `/docker-entrypoint-initdb.d/` folder has the same effect as running all the statements in the file in the MySQL instance at build time. Multiple files can be used, but data definition language files need to go before data manipulation language files.


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
┃ ┣ Version_0.1_DDL.sql (the SQL statements to create the schema for the database)
┃ ┗ Version_0.1_DML.sql (the SQL statements to load in any information wanted in the database at initialization)
┣ Private_Info/
┃ ┣ Data_Warehouse_Data/
┃ ┃ ┗ *the CSVs containing the raw data for inclusion in the data warehouse entities other than "R5_Usage"*
┃ ┣ JSON_to_Upload/
┃ ┃ ┗ *the JSONs containing the COUNTER usage that can't be pulled through the SUSHI API*
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

### Create a Copy of the MySQL Container Contents in DDL and DML
(The first three steps are about accessing the bash shell for the MySQL container)
1. Attach a VS Code window to a running container (this process needs )
2. Select "mysql-container" as the running container
3. Open the integrated terminal
4. `mysqldump --password database > filename.sql` where "database" is the name of the database the data is coming from and "filename" is the name of the file the data is being saved to 
5. Enter the password for the root user set in the MySQL Dockerfile
6. In the left-hand menu, right click the new file and select "Download..."
7. Download the SQL text file to the local machine

### Accessing the Python Container via CLI
1. Open the host CLI
2. `docker exec -it python-container bash`
3. Bash prompt: `python`