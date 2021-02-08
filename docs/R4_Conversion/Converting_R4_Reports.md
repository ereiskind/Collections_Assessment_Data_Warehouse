# Converting R4 Reports for Upload
To allow for the preservation of historical usage statistics, data from COUNTER Release 4 reports can be uploaded into the "R4_Usage" table in the database, but only after it has been converted to match with the table's schema. Contained within this folder are JSONs containing steps that can be applied to a tabular R4 report uploaded to OpenRefine to convert it into a format appropriate for upload.

When uploading to OpenRefine, skip the first seven rows and use the next row as header.