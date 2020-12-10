CREATE TABLE LIB_Vendors (
    CORAL_ID INT PRIMARY KEY,
    Vendor_Name VARCHAR(75)
); 

CREATE TABLE LIB_Interfaces (
    Interfaces_ID INT PRIMARY KEY, -- Should this be pre-supplied to ensure matching with JSON and mimic production, where values from Alma will likely be used?
    Interface_Name VARCHAR(75),
    COUNTER_R4_Compliant BOOLEAN,
    SUSHI_R5_Compliant BOOLEAN,
    Has_Usage_Portal BOOLEAN,
    Email_for_Usage VARCHAR(50),
    Vendor INT,
    INDEX INDX_Vendor (Vendor),
    CONSTRAINT FK_Interfaces_Vendor FOREIGN KEY INDX_Vendor (Vendor)
        REFERENCES LIB_Vendors(CORAL_ID)
        ON UPDATE cascade
        ON DELETE restrict
);