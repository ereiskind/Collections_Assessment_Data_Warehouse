# Converting R4 Reports for Upload
To allow for the preservation of historical usage statistics, data from COUNTER Release 4 reports can be uploaded into the "R4_Usage" table in the database, but only after it has been converted to match with the table's schema. That conversion requires changing tabular data into a matching SQL insert statement, done through the following process:

1. The tabular R4 report is uploaded into OpenRefine.
2. An OpenRefine project is created from the uploaded worksheet by skipping the first six or seven rows (depending on if row eight is blank or contains the headers as the standard dictates) and using the next row as the header. The project is named `{origin workbook name}_{report name}_FY {fiscal year}` where the curly braces are placeholders for the content described inside them. Spaces in the project name can be left as is--they'll be replaced with hyphens when the project is exported from OpenRefine.
3. The JSON in this folder named for the report type is applied to the project.
4. The SQL Exporter is chosen as the export option.
5. The R4_Month and R4_Count types are changed to "Date" and "Int" respectively.
6. The table name is changed to "R4_Usage" and the "Include Schema" box is deselected.
7. The SQL file is downloaded via the SQL Exporter.

Running Add_Insert_Statements_to_DML.py in the root directory of the runtime folder (see Collections_Assessment_Data_Warehouse/docs/Runtime_Environment/Runtime_Environment.md for more information on the runtime folder setup) will add all of the SQL files in the Collections_Assessment_Data_Warehouse_Runtime\Private_Info\R4_Data directory of the runtime folder to the DML file used on database creation.

### Notes
- The journal reports use the Data_type value "serial" because some content falls into other R5 data types; book reports are just about always books or parts of books
- JR5 reports are by FY, so they'll need a normalized resources table to serve as a foreign key; as a result, they haven't been converted
