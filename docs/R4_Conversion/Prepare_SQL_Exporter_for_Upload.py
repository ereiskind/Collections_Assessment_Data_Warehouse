#! /usr/local/bin/python

#ToDo: Ask for Interface_ID
#ToDo: Open the original SQL file
#ToDo: Create a SQL file


#Section: Redo First Line
#ToDo: Read in first line
    # Example: "INSERT INTO EBSCO_JR1_FY_2016_2017 (Resource,Publisher,Platform,DOI,Proprietary_ID,Print_ISSN,Online_ISSN,Metric_Type,Data_Type,R4_Month,R4_Count) VALUES"
    #ToDo: Add "Interface" at beginning of list in parentheses
    #ToDo: Get number of fields
    #ToDo: Write line to new SQL file

#Section: Rework Each Insert Line
# Asterisk are repeats--make function
#ToDo: For each line after the first line ending with a comma
    #ToDo: Remove "( '" from the beginning and " )," from the end
    #ToDo: Split line at each "','"
    #ToDo*: For each item in list created by split but last two, enclose in parentheses, then single quotes, and append to a list
    #ToDo*: For penultimate item in list created by split, remove "T00:00:00Z" from end, surround in single quotes, and append to new list
    #ToDo*: Append final item in list created by split to new list
    #ToDo*: Join new list with comma as seperator
    #ToDo: Enclose newly created string in parentheses and end with a comma
    #ToDo: Write the above string to the new SQL file
#ToDo: For the line tht doesn't end with a comma (final line)
    #ToDo: Remove "( '" from the beginning and " )" from the end
    #ToDo: Split line at each "','"
    #ToDo*: For each item in list created by split but last two, enclose in parentheses, then single quotes, and append to a list
    #ToDo*: For penultimate item in list created by split, remove "T00:00:00Z" from end, surround in single quotes, and append to new list
    #ToDo*: Append final item in list created by split to new list
    #ToDo*: Join new list with comma as seperator
    #ToDo: Enclose newly created string in parentheses and end with semicolon
    #ToDo: Write the newly created string to the new SQL file
    #ToDo: Close and save the new SQL file