CREATE TABLE LIB_Vendors (
    CORAL_ID INT PRIMARY KEY NOT NULL,
    Vendor_Name VARCHAR(75) NOT NULL
); 

CREATE TABLE LIB_Interfaces (
    Interface_ID INT PRIMARY KEY NOT NULL, -- Should this be pre-supplied to ensure matching with JSON and mimic production, where values from Alma will likely be used?
    Interface_Name VARCHAR(75) NOT NULL,
    COUNTER_R4_Compliant BOOLEAN NOT NULL,
    SUSHI_R5_Compliant BOOLEAN NOT NULL,
    Has_Usage_Portal BOOLEAN NOT NULL,
    Email_for_Usage VARCHAR(50),
    Vendor INT NOT NULL,
    INDEX INDX_Vendor (Vendor),
    CONSTRAINT FK_Interfaces_Vendor FOREIGN KEY INDX_Vendor (Vendor)
        REFERENCES LIB_Vendors(CORAL_ID)
        ON UPDATE cascade
        ON DELETE restrict
);

CREATE TABLE LIB_Fiscal_Year (
    Fiscal_Year_ID INT PRIMARY KEY NOT NULL,
    Fiscal_Year CHAR(9) NOT NULL
);

CREATE TABLE LIB_Stats_Collection_Info (
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
        REFERENCES LIB_Interfaces(Interface_ID)
        ON UPDATE restrict
        ON DELETE restrict,
    INDEX INDX_FY (Fiscal_Year),
    CONSTRAINT FK_SCInfo_FY FOREIGN KEY INDX_FY (Fiscal_Year)
        REFERENCES LIB_Fiscal_Year(Fiscal_Year_ID)
        ON UPDATE restrict
        ON DELETE restrict
);