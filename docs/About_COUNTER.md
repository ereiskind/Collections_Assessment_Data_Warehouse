# COUNTER Usage Statistics

## From the COUNTER Director in an Email List
"advice that we at COUNTER gave on 6 August 2019 about using an additional custom metric in the Master Reports to report the total number of chapters downloaded. This is not an amendment to the Code of Practice, but an extension as defined in section 11.4 of the Code of Practice. Clients like ERM and usage consolidation systems should be prepared to handle such custom values. Note that extensions are only allowed in Master Reports and custom reports"

## ACRL/IPEDS Instructions

### 60b. Initial Circulation: Digital/Electronic
Report usage of digital/electronic titles whether viewed, downloaded, or streamed. **Include usage for e-books, e-serials, and e-media titles** even if they were purchased as part of a collection or database.

Exclude: 
- E-serials and institutional repository documents, which are reported separately. 
- Usage of titles in demand-driven acquisition (DDA) or patron-driven acquisition (PDA) collections until they have been purchased or leased by the library. 
- Transactions of VHS, CDs, or DVDs, as the transactions of these materials are reported under "physical circulation." 

Most vendors will provide usage statistics in COUNTER reports. As of January 2019, Release 5 became the current Code of Practice (see Project COUNTER Release 5 Code of Practice [https://www.projectcounter.org/wpcontent/uploads/2019/11/Release_5_for_Providers_20191030.pdf]). Relevant COUNTER Release 5 reports for e-books are: **TR_B1**: Book Requests (Excluding OA_Gold). As to the COUNTER 5 metric type for e-books, **report "unique title requests."** For e-media, use **IR_M1**: Multimedia Item Requests, **report metric type for "total_item_requests"** is the most relevant. **If you have access to COUNTER Release 5 reports and can provide an answer for 60 Column B, skip questions 61 and 62 and leave them blank.** 

If you have access to COUNTER Release 5 reports and can provide an answer for 60 Column B, skip questions 61 and 62 and leave them blank. 

If COUNTER Release 5 reports are unavailable but COUNTER Release 4 reports are available, skip 60 Column B and leave it blank. Follow the instructions for questions 61 and 62 and provide answers accordingly.

Additional guidance: 
- Libraries may need to ask vendors for usage reports; reports may not be delivered automatically or in easily understood formats by the vendor to the library. 
- Viewing documents is defined as having the full text of a digital document or electronic resource downloaded. [NISO Z39.7-2013, section 7.7] 
- An electronic resource management system (ERMS) and/or a usage consolidation service may be helpful for collecting e-book usage statistics.
- Add notes as appropriate.

#### Calculating 60b
60b = TR_B1 + IR_M1 + TR_J1

##### TR_B1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE R5_Month>='2019-07-01' AND R5_Month<='2020-06-30' AND Metric_Type='Unique_Title_Requests' AND Data_Type='Book' AND Access_Type='Controlled' AND Access_Method='Regular' AND Report='TR';`
(Value was same with and without "Report='TR'")

##### IR_M1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE R5_Month>='2019-07-01' AND R5_Month<='2020-06-30' AND Metric_Type='Total_Item_Requests' AND Data_Type='Multimedia' AND Access_Method='Regular' AND Report='IR';`

##### TR_J1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE R5_Month>='2019-07-01' AND R5_Month<='2020-06-30' AND Metric_Type='Unique_Item_Requests' AND Data_Type='Journal' AND Access_Type='Controlled' AND Access_Method='Regular' AND Report='TR';`


### 63. E-Serials Usage: Digital/Electronic
Please note that the ACRL Academic Library Trend and Statistics Survey is not collecting use of print serial titles separately from other physical initial circulation.
Report usage of e-serial titles whether viewed, downloaded, or streamed. Include usage for e-serial titles only, even if the title was purchased as part of a database. Viewing a document is defined as having the full text of a digital document or electronic resource downloaded. [NISO Z39.7-2013, section 7.7] If available, include the count for open access e-journal usage if the title is accessible through the library’s catalog or discovery system. Libraries may need to ask vendors for e-serial usage reports; reports may not be delivered automatically or in easily understood formats by the vendor to the library. Most vendors will provide usage statistics in COUNTER Release 5 reports. The most relevant COUNTER Release 5 report for e-serial usage is **TR_J1**: Journal Requests (Excluding OA_Gold). For the metric type, **report "unique item requests."** If COUNTER Release 5 reports are unavailable, the most relevant COUNTER Release 4 report is JR1 (defined as the "Number of Successful Full-Text Article Requests by Month and Journal").

Applicable COUNTER Release 5 definitions:
- Article: "An item of original written work published in a journal, other serial publication, or in a book."
- Database: "A collection of electronically stored data or unit records (facts, bibliographic data, texts) with a common user interface and software for the retrieval and manipulation of data (NISO)"
- Full-Text Article: "The complete text, including all references, figures and tables, of an article, plus links to any supplementary material published with it."
- Open access: "Online research outputs that are free of all restrictions on access (e.g. access tolls) and free of many restrictions on use (e.g. certain copyright and license restrictions). Open access can be applied to all forms of published research output, including peer-reviewed and non-peer-reviewed academic journal articles, conference papers, theses, book chapters, and monographs.

In cases where vendors do not provide COUNTER reports, libraries may report using other means for monitoring digital/electronic circulation/usage (downloads, session views, transaction logs, etc.), or report zero. An electronic resource management system (ERMS) and/or a usage consolidation service may be helpful for collecting eserial usage statistics. Do not include usage of titles in demand-driven acquisition (DDA) or patron-driven acquisition (PDA) collections until they have been purchased or leased by the library.

Additional guidelines:
- When possible record usage at the article level.
- In cases where vendors do not provide COUNTER reports, libraries may report using other means for monitoring digital/electronic circulation/usage (downloads, session views, transaction logs, etc.) and make a note, or report zero.
- Viewing a document is defined as having the full text of a digital document or electronic resource downloaded. [NISO Z39.7-2013, section 7.7]
- An electronic resource management system (ERMS) and/or a usage consolidation service may be helpful for collecting e-serial usage statistics.
- Add notes as appropriate.

#### Calculating 63
63 = TR_J1

##### TR_J1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE R5_Month>='2019-07-01' AND R5_Month<='2020-06-30' AND Metric_Type='Unique_Item_Requests' AND Data_Type='Journal' AND Access_Type='Controlled' AND Access_Method='Regular' AND Report='TR';`


## ARL Instructions

### 18. Number of successful full-text article requests (journals)
Items reported should follow definitions as defined in the COUNTER 5 Code of Practice (https://www.projectcounter.org/release-5-code-practice/). The COUNTER 5 report that corresponds to Question 18 is **TR_J3** Journal Usage by Access Type. The metric from this COUNTER 5 report is **Unique Item Requests**. In a footnote, please *include the types of resources for which you are reporting* data.

#### Calculating 18
18 = TR_J3

##### TR_J3
`SELECT SUM(R5_Count) FROM R5_Usage WHERE R5_Month>='2019-07-01' AND R5_Month<='2020-06-30' AND Metric_Type='Unique_Item_Requests' AND Data_Type='Journal' AND Access_Method='Regular' AND Report='TR';`


### 19. Number of regular searches (databases)
Items reported should follow definitions as defined in the COUNTER 5 Code of Practice (https://www.projectcounter.org/release-5-codepractice/). The COUNTER 5 report that corresponds to Question 19 is **DR_D1** Database Search and Item Usage. The metric from this COUNTER 5 report is **Searches_Regular**. If this report is unavailable, the **PR_P1** report can be used as an alternative, with the PR_P1 **Searches Platform** metric. In a footnote, please *include the types of resources for which you are reporting* data. Please be sure to indicate whether you **used DR_D1 or PR_P1**. It is recommended that ONLY data that follow the COUNTER definitions be reported. Any exceptions should be documented in a footnote.

#### Calculating 19
19 = DR_D1

##### DR_D1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE R5_Month>='2019-07-01' AND R5_Month<='2020-06-30' AND Report='DR' AND Access_Method='Regular' AND Metric_Type='Searches_Regular';`


### 20. Number of federated searches (databases)
Items reported should follow definitions as defined in the COUNTER 5 Code of Practice (https://www.projectcounter.org/release-5-code-practice/). The COUNTER 5 report that corresponds to Question 20 is **DR_D1** Searches_Federated. Metric options include **"Searches_Federated", "Total_Item_Requests for full text databases", and "Total_Item_Investigations for non-full text databases"**. If a *combination of these metrics must be used to capture all the federated search data at your institution, please sum the numbers* accordingly, provided the information is not duplicative, and *indicate in a footnote*. The goal is to capture the totality of federated searches. In a footnote, please *include the types of resources for which you are reporting* data, and please **specify the COUNTER 5 metric used** to report this value. It is recommended that ONLY data that follow the COUNTER definitions be reported. Any exceptions should be documented in a footnote.

#### Calculating 20
20 = DR_D1

##### DR_D1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE R5_Month>='2019-07-01' AND R5_Month<='2020-06-30' AND Report='DR' AND Access_Method='Regular' AND Metric_Type='Searches_Federated';`


## Other COUNTER Reports

### PR_P1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='PR' AND Access_Method='Regular'`
- Metric_Type = Searches_Platform; Total_Item_Requests; Unique_Item_Requests; Unique_Title_Requests

### DR_D1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='DR' AND Access_Method='Regular'`
- Metric_Type=Searches_Automated; Searches_Federated; Searches_Regular; Total_Item_Investigations; Total_Item_Requests

### DR_D2
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='DR' AND Access_Method='Regular'`
- Metric_Type=Limit_Exceeded; No_License

### TR_B1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='TR' AND Data_Type='Book' AND Access_Type='Controlled' AND Access_Method='Regular'`
- Metric_Type=Total_Item_Requests; Unique_Title_Requests

### TR_B2
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='TR' AND Data_Type='Book' AND Access_Method='Regular'`
- Metric_Type=Limit_Exceeded; No_License

### TR_B3
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='TR' AND Data_Type='Book' AND Access_Method='Regular'`
- Metric_Type=Total_Item_Investigations; Total_Item_Requests; Unique_Item_Investigations; Unique_Item_Requests; Unique_Title_Investigations; Unique_Title_Requests

### TR_J1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='TR' AND Data_Type='Journal' AND Access_Type='Controlled' AND Access_Method='Regular'`
- Metric_Type=Total_Item_Requests; Unique_Item_Requests

### TR_J2
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='TR' AND Data_Type='Journal' AND Access_Method='Regular'`
- Metric_Type=Limit_Exceeded; No_License

### TR_J3
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='TR' AND Data_Type='Journal' AND Access_Method='Regular'`
- Metric_Type=Total_Item_Investigations; Total_Item_Requests; Unique_Item_Investigations; Unique_Item_Requests

### TR_J4
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='TR' AND Data_Type='Journal' AND Access_Type='Controlled' AND Access_Method='Regular'`
- Metric_Type=Total_Item_Requests; Unique_Item_Requests

### IR_A1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='IR' AND Data_Type='Article' AND Parent_Data_Type='Journal' AND Access_Method='Regular'`
- Metric_Type=Total_Item_Requests; Unique_Items_Requests

### IR_M1
`SELECT SUM(R5_Count) FROM R5_Usage WHERE Report='IR' AND Data_Type='Multimedia' AND Access_Method='Regular' AND Metric_Type='Total_Item_Requests';`
