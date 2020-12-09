-- This file exists to record the SQL created for the idea of tracking problems that emerged in report harvesting in MySQL, which was moved away from before the this repository became the host of the source code.

CREATE SCHEMA `testdatawarehouse`;

CREATE TABLE SUSHIErrorLog (
    SUSHIErrorLog_ID SERIAL,
    Report_ID BIGINT UNSIGNED,
    Error_Code VARCHAR(4),
    Error_Details VARCHAR(75),
    Error_Name VARCHAR(65),
    Severity VARCHAR(10),
    INDEX Report_ID_index (Report_ID),
    CONSTRAINT Report_ID_FK FOREIGN KEY Report_ID_index (Report_ID)
        REFERENCES SUSHIErrorReports(SUSHIErrorReports_ID)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
); 

CREATE TABLE SUSHIErrorReports (
    SUSHIErrorReports_ID SERIAL,
    COUNTER_Namespace VARCHAR(10),-- If ability to query to see what SUSHI APIs are returning errors is desired, Alma interface ID of credentials would be better here
    Matching VARCHAR(100) UNIQUE,
    Time_Report_Run TIMESTAMP,
    Report_Source VARCHAR(50),-- For platforms using third-party backends (e.g. Atypon), backend company name shows as provider, so field is of limited usefulness
    Report_Type VARCHAR(45)
); 