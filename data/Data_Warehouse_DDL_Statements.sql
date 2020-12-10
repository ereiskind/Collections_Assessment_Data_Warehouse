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
    INDEX INDX_Interface (Interface),
    CONSTRAINT FK_R5Usage_Interface FOREIGN KEY INDX_Interface (Interface)
        REFERENCES Interfaces(Interface_ID)
        ON UPDATE cascade
        ON DELETE restrict
);