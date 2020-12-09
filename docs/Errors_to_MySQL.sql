-- This file exists to record the SQL created for the idea of tracking problems that emerged in report harvesting in MySQL, which was moved away from before the this repository became the host of the source code.

CREATE TABLE SUSHIErrorLog (
    SUSHIErrorLog_ID SERIAL,
    Report_ID BIGINT,-- Foreign key connected to SUSHIErrorReports.SUSHIErrorReports_ID
    Error_Code VARCHAR(4),
    Error_Details VARCHAR(75),
    Error_Name VARCHAR(65),
    Severity VARCHAR(10)
); 

CREATE TABLE SUSHIErrorReports (
    SUSHIErrorReports_ID SERIAL,
    COUNTER_Namespace VARCHAR(10),
    Match VARCHAR(100) UNIQUE,
    Time_Report_Run DATETIME,
    Report_Source VARCHAR(50),
    Report_Type VARCHAR(45)
); 