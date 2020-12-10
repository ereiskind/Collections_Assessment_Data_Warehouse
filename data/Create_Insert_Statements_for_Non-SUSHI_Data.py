# This script can generate MySQL insert statements for the tables in Schema_Creation_Statements other than R5_Usage based on CSVs of the same name as the tables in the subfolder "data/DML_CSVs". The CSVs cannot contain a header row and the columns must be in the order in which the fields are listed in the insert statements.
# The columns must be listed in the same order as the field names are, where the ith column is represented by Record[i]. So, if the first field listed corresponds to the values in the third column of the CSV, the first item listed in the VALUES clause must be Record[3].
    # All non-numeric values are encapsulated in parentheses, then in single quotes, like ('Record[i]'), so that any commas within the values are retained.
# The script handles escaping all apostrophes in the CSV, replaces empty strings in the insert statements with null values, and condenses the INSERT statements, which are written across multiple lines here for clarity, into a single line.

from pathlib import Path
import csv

'''Example:
print("-- Table <table>")
CSV_Path = Path('.', 'DML_CSVs', '<table>.csv')
with open(CSV_Path) as CSVfile:
    for Record in list(csv.reader(CSVfile)):
        for i in range(len(Record)):
            Record[i] = Record[i].replace("'", "''")
        Insert_Statement = f"""
            INSERT INTO <table> (
                <list of table's fields here>
            )
            VALUES(
                ('{Record[0]}'),
                {Record[1]}
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
'''

"""
CREATE TABLE Vendors (
    CORAL_ID INT PRIMARY KEY NOT NULL,
    Vendor_Name VARCHAR(75) NOT NULL
);
CREATE TABLE Interfaces (
    Interface_ID INT PRIMARY KEY NOT NULL, -- Should this be pre-supplied to ensure matching with JSON and mimic production, where values from Alma will likely be used?
    Interface_Name VARCHAR(75) NOT NULL,
    COUNTER_R4_Compliant BOOLEAN NOT NULL,
    SUSHI_R5_Compliant BOOLEAN NOT NULL,
    Has_Usage_Portal BOOLEAN NOT NULL,
    Email_for_Usage VARCHAR(50),
    Vendor INT NOT NULL,
    INDEX INDX_Vendor (Vendor),
    CONSTRAINT FK_Interfaces_Vendor FOREIGN KEY INDX_Vendor (Vendor)
        REFERENCES Vendors(CORAL_ID)
        ON UPDATE cascade
        ON DELETE restrict
);
CREATE TABLE Fiscal_Year (
    Fiscal_Year_ID INT PRIMARY KEY NOT NULL,
    Fiscal_Year CHAR(9) NOT NULL
);
CREATE TABLE Stats_Collection_Info (
    Interface INT NOT NULL,
    Fiscal_Year INT NOT NULL,
    Manual_Collection_Required BOOLEAN NOT NULL,
    Manual_Collection_Completed BOOLEAN,
    Note TEXT,
    In_eBooks_Report BOOLEAN NOT NULL,
    In_eJournals_Report BOOLEAN NOT NULL,
    In_Databases_Report BOOLEAN NOT NULL,
    In_Multimedia_Report BOOLEAN NOT NULL,
    PRIMARY KEY (Interface, Fiscal_Year),
    INDEX INDX_Interface (Interface),
    CONSTRAINT FK_SCInfo_Interface FOREIGN KEY INDX_Interface (Interface)
        REFERENCES Interfaces(Interface_ID)
        ON UPDATE restrict
        ON DELETE restrict,
    INDEX INDX_FY (Fiscal_Year),
    CONSTRAINT FK_SCInfo_FY FOREIGN KEY INDX_FY (Fiscal_Year)
        REFERENCES Fiscal_Year(Fiscal_Year_ID)
        ON UPDATE restrict
        ON DELETE restrict
);
CREATE TABLE Platforms (
    Platform_ID INT PRIMARY KEY NOT NULL,
    Interface INT NOT NULL,
    Platform_Name VARCHAR(50) NOT NULL,
    Platform_Homepage_Permalink TINYTEXT,
    INDEX INDX_Interface (Interface),
    CONSTRAINT FK_Platforms_Interface FOREIGN KEY INDX_Interface (Interface)
        REFERENCES Interfaces(Interface_ID)
        ON UPDATE cascade
        ON DELETE restrict
);
CREATE TABLE Platform_Notes (
    Platform_Notes_ID INT PRIMARY KEY NOT NULL,
    Platform INT NOT NULL,
    Note TEXT,
    INDEX INDX_Platform (Platform),
    CONSTRAINT FK_PlatformNotes_Platform FOREIGN KEY INDX_Platform (Platform)
        REFERENCES Platforms(Platform_ID)
        ON UPDATE restrict
        ON DELETE restrict
);
CREATE TABLE Historical_Aleph (
    Historical_Aleph_ID INT PRIMARY KEY NOT NULL,
    Platform INT NOT NULL,
    Aleph_Order_Number VARCHAR(25),
    INDEX INDX_Platform (Platform),
    CONSTRAINT FK_HistoricalAleph_Platform FOREIGN KEY INDX_Platform (Platform)
        REFERENCES Platforms(Platform_ID)
        ON UPDATE restrict
        ON DELETE restrict
);
"""