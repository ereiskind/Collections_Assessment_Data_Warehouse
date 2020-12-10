# This script can generate MySQL insert statements for the tables in Schema_Creation_Statements other than R5_Usage based on CSVs of the same name as the tables in the subfolder "data/DML_CSVs". The CSVs cannot contain a header row and the columns must be in the order in which the fields are listed in the insert statements.
# The columns must be listed in the same order as the field names are, where the ith column is represented by Record[i]. So, if the first field listed corresponds to the values in the third column of the CSV, the first item listed in the VALUES clause must be Record[3].
    # All string values are encapsulated in parentheses, then in single quotes, like ('Record[i]'), so that any commas within the values are retained.
# The script handles escaping all apostrophes in the CSV, replaces empty strings in the insert statements with null values, and condenses the INSERT statements, which are written across multiple lines here for clarity, into a single line.

# Reminder: cd into data before executing

from pathlib import Path
import csv

print("-- Table Vendors")

CSV_Path = Path('.', 'DML_CSVs', 'Vendors.csv')
with open(CSV_Path) as CSVfile:
    for Record in list(csv.reader(CSVfile)):
        for i in range(len(Record)):
            Record[i] = Record[i].replace("'", "''")
        Insert_Statement = f"""
            INSERT INTO Vendors (
                CORAL_ID,
                Vendor_Name
            )
            VALUES(
                {Record[0]},
                ('{Record[1]}')
            );
        """
        Insert_Statement = Insert_Statement.replace("('')", "NULL")

        Temp_List = Insert_Statement.split()
        Insert_Statement = " ".join(Temp_List)
        Temp_List = Insert_Statement.split("( ")
        Insert_Statement = "(".join(Temp_List)
        Temp_List = Insert_Statement.split(" )")
        Insert_Statement = ")".join(Temp_List)

        print(Insert_Statement)


print("-- Table Interfaces")

CSV_Path = Path('.', 'DML_CSVs', 'Interfaces.csv')
with open(CSV_Path) as CSVfile:
    for Record in list(csv.reader(CSVfile)):
        for i in range(len(Record)):
            Record[i] = Record[i].replace("'", "''")
        Insert_Statement = f"""
            INSERT INTO Interfaces (
                Interface_Name,
                COUNTER_R4_Compliant,
                SUSHI_R5_Compliant,
                Has_Usage_Portal,
                Email_for_Usage,
                Vendor,
            )
            VALUES(
                ('{Record[0]}'),
                {Record[1]},
                {Record[2]},
                {Record[3]},
                ('{Record[4]}'),
                {Record[5]}
            );
        """
        Insert_Statement = Insert_Statement.replace("('')", "NULL")

        Temp_List = Insert_Statement.split()
        Insert_Statement = " ".join(Temp_List)
        Temp_List = Insert_Statement.split("( ")
        Insert_Statement = "(".join(Temp_List)
        Temp_List = Insert_Statement.split(" )")
        Insert_Statement = ")".join(Temp_List)

        print(Insert_Statement)


print("-- Table Fiscal_Years")

CSV_Path = Path('.', 'DML_CSVs', 'Fiscal_Years.csv')
with open(CSV_Path) as CSVfile:
    for Record in list(csv.reader(CSVfile)):
        for i in range(len(Record)):
            Record[i] = Record[i].replace("'", "''")
        Insert_Statement = f"""
            INSERT INTO Fiscal_Years (
                Fiscal_Year
            )
            VALUES(
                ('{Record[0]}')
            );
        """
        Insert_Statement = Insert_Statement.replace("('')", "NULL")

        Temp_List = Insert_Statement.split()
        Insert_Statement = " ".join(Temp_List)
        Temp_List = Insert_Statement.split("( ")
        Insert_Statement = "(".join(Temp_List)
        Temp_List = Insert_Statement.split(" )")
        Insert_Statement = ")".join(Temp_List)

        print(Insert_Statement)

#Alert: Stats_Collection_Info needs PK from Interfaces, which is an auto-increment field

print("-- Table Stats_Collection_Info")

CSV_Path = Path('.', 'DML_CSVs', 'Stats_Collection_Info.csv')
with open(CSV_Path) as CSVfile:
    for Record in list(csv.reader(CSVfile)):
        for i in range(len(Record)):
            Record[i] = Record[i].replace("'", "''")
        Insert_Statement = f"""
            INSERT INTO Stats_Collection_Info (
                Interface,
                Fiscal_Year,
                Collection_Required,
                Manual_Collection_Required,
                Manual_Collection_Completed,
                Note,
                In_eBooks_Report,
                In_eJournals_Report,
                In_Databases_Report,
                In_Multimedia_Report
            )
            VALUES(
                {Record[0]},
                {Record[1]},
                {Record[2]},
                {Record[3]},
                {Record[4]},
                ('{Record[5]}'),
                ('{Record[6]}'),
                ('{Record[7]}'),
                ('{Record[8]}'),
                ('{Record[9]}')
            );
        """
        Insert_Statement = Insert_Statement.replace("('')", "NULL")
        
        Temp_List = Insert_Statement.split()
        Insert_Statement = " ".join(Temp_List)
        Temp_List = Insert_Statement.split("( ")
        Insert_Statement = "(".join(Temp_List)
        Temp_List = Insert_Statement.split(" )")
        Insert_Statement = ")".join(Temp_List)
        
        print(Insert_Statement)


print("-- Table Platforms")

CSV_Path = Path('.', 'DML_CSVs', 'Platforms.csv')
with open(CSV_Path) as CSVfile:
    for Record in list(csv.reader(CSVfile)):
        for i in range(len(Record)):
            Record[i] = Record[i].replace("'", "''")
        Insert_Statement = f"""
            INSERT INTO Platforms (
                Interface,
                Platform_Name,
                Platform_Homepage_Permalink
            )
            VALUES(
                {Record[0]},
                ('{Record[1]}'),
                ('{Record[2]}')
            );
        """
        Insert_Statement = Insert_Statement.replace("('')", "NULL")

        Temp_List = Insert_Statement.split()
        Insert_Statement = " ".join(Temp_List)
        Temp_List = Insert_Statement.split("( ")
        Insert_Statement = "(".join(Temp_List)
        Temp_List = Insert_Statement.split(" )")
        Insert_Statement = ")".join(Temp_List)

        print(Insert_Statement)


print("-- Table Platform_Notes")

CSV_Path = Path('.', 'DML_CSVs', 'Platform_Notes.csv')
with open(CSV_Path) as CSVfile:
    for Record in list(csv.reader(CSVfile)):
        for i in range(len(Record)):
            Record[i] = Record[i].replace("'", "''")
        Insert_Statement = f"""
            INSERT INTO Platform_Notes (
                Platform,
                Note
            )
            VALUES(
                {Record[0]},
                ('{Record[1]}')
            );
        """
        Insert_Statement = Insert_Statement.replace("('')", "NULL")

        Temp_List = Insert_Statement.split()
        Insert_Statement = " ".join(Temp_List)
        Temp_List = Insert_Statement.split("( ")
        Insert_Statement = "(".join(Temp_List)
        Temp_List = Insert_Statement.split(" )")
        Insert_Statement = ")".join(Temp_List)

        print(Insert_Statement)


print("-- Table Historical_Aleph")

CSV_Path = Path('.', 'DML_CSVs', 'Historical_Aleph.csv')
with open(CSV_Path) as CSVfile:
    for Record in list(csv.reader(CSVfile)):
        for i in range(len(Record)):
            Record[i] = Record[i].replace("'", "''")
        Insert_Statement = f"""
            INSERT INTO Historical_Aleph (
                Platform,
                Aleph_Order_Number,
                ERS_Spreadsheet_Year
            )
            VALUES(
                {Record[0]},
                ('{Record[1]}'),
                ('{Record[2]}')
            );
        """
        Insert_Statement = Insert_Statement.replace("('')", "NULL")

        Temp_List = Insert_Statement.split()
        Insert_Statement = " ".join(Temp_List)
        Temp_List = Insert_Statement.split("( ")
        Insert_Statement = "(".join(Temp_List)
        Temp_List = Insert_Statement.split(" )")
        Insert_Statement = ")".join(Temp_List)

        print(Insert_Statement)