# COUNTER Usage Statistics

## From the COUNTER Director in an Email List
"advice that we at COUNTER gave on 6 August 2019 about using an additional custom metric in the Master Reports to report the total number of chapters downloaded. This is not an amendment to the Code of Practice, but an extension as defined in section 11.4 of the Code of Practice. Clients like ERM and usage consolidation systems should be prepared to handle such custom values. Note that extensions are only allowed in Master Reports and custom reports"

## ACRL/IPEDS Instructions

### 60b. Initial Circulation: Digital/Electronic
Report usage of digital/electronic titles whether viewed, downloaded, or streamed.

Include: 
- Usage for e-books and e-media titles only. 
- Titles even if they were purchased as part of a collection or database.

Exclude: 
- E-serials and institutional repository documents, which are reported separately. 
- Usage of titles in demand-driven acquisition (DDA) or patron-driven acquisition (PDA) collections until they have been purchased or leased by the library. 
- Transactions of VHS, CDs, or DVDs, as the transactions of these materials are reported under "physical circulation." 

Most vendors will provide usage statistics in COUNTER reports. As of January 2019, Release 5 became the current Code of Practice (see Project COUNTER Release 5 Code of Practice [https://www.projectcounter.org/wpcontent/uploads/2019/11/Release_5_for_Providers_20191030.pdf]). Relevant COUNTER Release 5 reports for e-books are: **TR_B1**: Book Requests (Excluding OA_Gold). As to the COUNTER 5 metric type for e-books, **report "unique title requests."** For e-media, use **IR_M1**: Multimedia Item Requests, **report metric type for "total_item_requests"** is the most relevant. **If you have access to COUNTER Release 5 reports and can provide an answer for 60 Column B, skip questions 61 and 62 and leave them blank.** If COUNTER Release 5 reports are unavailable but COUNTER Release 4 reports are available, skip 60 Column B and leave it blank. Follow the instructions for questions 61 and 62 and provide answers accordingly. 

Additional guidance: 
- Libraries may need to ask vendors for usage reports; reports may not be delivered automatically or in easily understood formats by the vendor to the library. 
- Viewing documents is defined as having the full text of a digital document or electronic resource downloaded. [NISO Z39.7-2013, section 7.7] 
- An electronic resource management system (ERMS) and/or a usage consolidation service may be helpful for collecting e-book usage statistics. 
- Add notes as appropriate.

#### TR_B1
Metric_Types: Unique_Title_Requests
Report_Filters: Data_Type=Book; Access_Type=Controlled; Access_Method=Regular*
#### IR_M1
Metric_Types: Total_Item_Requests
Report_Filters: Data_Type=Multimedia; Access_Method=Regular*


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

#### TR_J1
Metric_Types: Unique_Item_Requests
Report_Filters: Data_Type=Journal; Access_Type=Controlled; Access_Method=Regular*