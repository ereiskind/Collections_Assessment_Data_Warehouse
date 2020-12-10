-- -----------------------------------------------------
-- Create Table "Vendors"
-- -----------------------------------------------------
CREATE TABLE Vendors (
    Vendor_ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,-- With move to Alma, should Alma IDs be used here?
    CORAL_ID INT,-- Once information in CORAL has completely been transfered to Alma, this field may no longer be needed
    Vendor_Name VARCHAR(80) NOT NULL
); 

-- -----------------------------------------------------
-- Create Table "Interfaces"
-- -----------------------------------------------------
CREATE TABLE Interfaces (
    Interface_ID INT PRIMARY KEY NOT NULL, -- With Alma, these will be pre-supplied as the Alma ID numbers
    Interface_Name VARCHAR(75) NOT NULL,
    COUNTER_R4_Compliant BOOLEAN NOT NULL,
    SUSHI_R5_Compliant BOOLEAN NOT NULL,
    Has_Usage_Portal BOOLEAN NOT NULL,-- Need to establish rule about what value this should be for interfaces we're no longer getting stats from since access to resources on corresponding platform(s) has been discontinued
    Email_for_Usage VARCHAR(50),
    -- How should discontinued interfaces (interfaces for which we no longer have access to resources and thus don't need to gather stats from) be indicated?
    Vendor INT,
    INDEX INDX_Vendor (Vendor),
    CONSTRAINT FK_Interfaces_Vendor FOREIGN KEY INDX_Vendor (Vendor)
        REFERENCES Vendors(Vendor_ID)
        ON UPDATE cascade
        ON DELETE restrict
);

-- -----------------------------------------------------
-- Create Table "Fiscal_Years"
-- -----------------------------------------------------
CREATE TABLE Fiscal_Years (
    Fiscal_Year_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Fiscal_Year CHAR(9) NOT NULL
);

-- -----------------------------------------------------
-- Create Table "Stats_Collection_Info"
-- -----------------------------------------------------
CREATE TABLE Stats_Collection_Info (
    Interface INT NOT NULL,
    Fiscal_Year INT NOT NULL,
    Collection_Required BOOLEAN NOT NULL,-- This Bool is if stats need to be collected
    Manual_Collection_Required BOOLEAN,-- This Bool is if stats need to be collected manually; if stats don't need to be collected, value is null
    Manual_Collection_Completed BOOLEAN,-- This Bool is if stats requiring manual collection have been collected; if stats don't need manual collection, value is null
    Note TEXT,
    In_eBooks_Report VARCHAR(50),-- If included, value is report and metric used; if not, value is null
    In_eJournals_Report VARCHAR(50),-- If included, value is report and metric used; if not, value is null
    In_Databases_Report VARCHAR(50),-- If included, value is report and metric used; if not, value is null
    In_Multimedia_Report VARCHAR(50),-- If included, value is report and metric used; if not, value is null
    CHECK (
        (Collection_Required=false AND Manual_Collection_Required=null AND Manual_Collection_Completed=null)-- Stats collection not required
        OR (Collection_Required=true AND Manual_Collection_Required=false AND Manual_Collection_Completed=null)-- Stats collection not manual
        OR (Collection_Required=true AND Manual_Collection_Required=true AND Manual_Collection_Completed=false)-- Stats collection manual, not completed
        OR (Collection_Required=true AND Manual_Collection_Required=true AND Manual_Collection_Completed=true)-- Stats collection manual, completed
    ),
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

-- -----------------------------------------------------
-- Create Table "Platforms"
-- -----------------------------------------------------
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

-- -----------------------------------------------------
-- Create Table "Platform_Notes"
-- -----------------------------------------------------
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

-- -----------------------------------------------------
-- Create Table "Historical_Aleph"
-- -----------------------------------------------------
CREATE TABLE Historical_Aleph (
    Historical_Aleph_ID INT PRIMARY KEY NOT NULL,
    Platform INT NOT NULL,
    Aleph_Order_Number VARCHAR(25),
    ERS_Spreadsheet_Year VARCHAR(9),
    INDEX INDX_Platform (Platform),
    CONSTRAINT FK_HistoricalAleph_Platform FOREIGN KEY INDX_Platform (Platform)
        REFERENCES Platforms(Platform_ID)
        ON UPDATE restrict
        ON DELETE restrict
);

-- -----------------------------------------------------
-- Create Table "R5_Usage"
-- -----------------------------------------------------
CREATE TABLE R5_Usage (
    R5_Usage_ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    Interface INT NOT NULL,
    Report CHAR(2) NOT NULL,-- If adding standard views without master reports as standard views, this will need to change
    Resource_Name VARCHAR(150),
    Publisher VARCHAR(100),
    Publisher_ID VARCHAR(50),
    Platform VARCHAR(75) NOT NULL,
    DOI VARCHAR(50),
    Proprietary_ID VARCHAR(50),
    ISBN CHAR(17),
    Print_ISSN CHAR(9),
    Online_ISSN CHAR(9),
    URI VARCHAR(50),
    Data_Type VARCHAR(25) NOT NULL,
    Section_Type VARCHAR(10),
    Parent_Data_Type VARCHAR(25),
    Parent_DOI VARCHAR(50),
    Parent_Proprietary_ID VARCHAR(50),
    YOP SMALLINT,-- YOP unknown is "0001" and articles-in-press is "9999", so data type YEAR can't be used
    Access_Type VARCHAR(20),
    Access_Method VARCHAR(10) NOT NULL,
    Metric_Type VARCHAR(30) NOT NULL,
    R5_Month DATE NOT NULL,
    R5_Count MEDIUMINT UNSIGNED NOT NULL,
    Report_Creation_Date DATE NOT NULL,
    INDEX INDX_Interface (Interface),
    CONSTRAINT FK_R5Usage_Interface FOREIGN KEY INDX_Interface (Interface)
        REFERENCES Interfaces(Interface_ID)
        ON UPDATE cascade
        ON DELETE restrict
);