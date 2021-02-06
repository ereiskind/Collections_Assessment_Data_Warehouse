/*
This is a repository of SQL statements for use in querying the accopanying database.

To query the database in the mysql-container Docker container,
1. Open the host command line interface
2. `docker exec -it mysql-container mysql --user=root --password`
3. enter the password for root set in the MySQL Dockerfile
4. SQL shell: `USE Collections_Assessment_Warehouse_0.1;`
*/

-- Find all the interfaces and platforms for a specific vendor based on a match to part of a vendor's name.
SELECT
    Vendors.Vendor_ID,
    Vendors.Vendor_Name,
    Interfaces.Interface_ID,
    Interfaces.Interface_Name,
    Platforms.Platform_ID,
    Platforms.Platform_Name
FROM
    Vendors
    JOIN Interfaces ON Vendors.Vendor_ID = Interfaces.Vendor
    JOIN Platforms ON Interfaces.Interface_ID = Platforms.Interface
WHERE
    Vendors.Vendor_Name LIKE '%';

-- Interfaces and Stats Used for Reporting
/*
Interfaces.Interface_Name
Fiscal_Years.Fiscal_Year
Stats_Collection_Info.Collection_Required
Stats_Collection_Info.Manual_Collection_Required
Stats_Collection_Info.Manual_Collection_Completed
Stats_Collection_Info.Note
Stats_Collection_Info.In_eBooks_Report
Stats_Collection_Info.In_eJournals_Report
Stats_Collection_Info.In_Databases_Report
Stats_Collection_Info.In_Multimedia_Report

Interfaces.Interface_ID = Stats_Collection_Info.Interface
Fiscal_Years.Fiscal_Year_ID = Stats_Collection_Info.Fiscal_Year
*/

-- Usage for Resources by Interface (based on text matching to interface name)
SELECT
    Interfaces.Interface_Name,
    R5_Usage.Report,
    R5_Usage.Resource_Name,
    R5_Usage.Platform,
    R5_Usage.Proprietary_ID,
    R5_Usage.Metric_Type,
    R5_Usage.R5_Month,
    R5_Usage.R5_Count,
FROM
    Interfaces
    JOIN R5_Usage ON Interfaces.Interface_ID = R5_Usage.Interface
WHERE
    Interfaces.Interface_Name LIKE '%'
GROUP BY
    R5_Usage.Proprietary_ID;

-- Get the YOP and frequency of those YOP for a given Interface and Report
SELECT
    DISTINCT YOP,
    COUNT(YOP)
FROM
    R5_Usage
WHERE
    Interface=144
    AND Report='TR'
GROUP BY
    YOP;

-- Searching for a resource by name
SELECT
    DISTINCT Resource_Name,
    Platform,
    Proprietary_ID,
    Report
FROM
    R5_Usage
WHERE
    Resource_Name LIKE '%';

-- Getting a count for a given metric for all of the databases on a given platform
SELECT
    Resource_Name,
    SUM(R5_Count)
FROM
    R5_Usage
WHERE
    Report='DR'
    AND Metric_Type='Total_Item_Requests'
    AND Platform='NewsBank'
GROUP BY
    Resource_Name;