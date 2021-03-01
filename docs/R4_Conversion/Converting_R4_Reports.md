# Converting R4 Reports for Upload
To allow for the preservation of historical usage statistics, data from COUNTER Release 4 reports can be uploaded into the "R4_Usage" table in the database, but only after it has been converted to match with the table's schema. That conversion requires changing tabular data into a matching SQL insert statement, done through the following process:

1. The tabular R4 report is uploaded into OpenRefine.
2. An OpenRefine project is created from the uploaded worksheet by skipping the first seven rows and using the next row as the header. The project is named `{origin workbook name}_{report name}_FY {fiscal year}` where the curly braces are placeholders for the content described inside them.
3. The JSON in this folder named for the report type is applied to the project.
4. The SQL Exporter is chosen as the export option.
5. The R4_Month and R4_Count types are changed to "Date" and "Int" respectively.
6. The table name is changed to "R4_Usage" and the "Include Schema" box is deselected.
7. The SQL file is downloaded via the SQL Exporter.
8. The downloaded file is run through Prepare_SQL_Exporter_for_Upload.py.

### Notes
- The journal reports use the Data_type value "serial" because some content falls into other R5 data types; book reports are just about always books or parts of books
- JR5 reports are by FY, so they'll need a normalized resources table to serve as a foreign key; as a result, they haven't been converted
