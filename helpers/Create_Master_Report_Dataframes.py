import pandas

#Section: Main Function
def Create_Dataframe(Interface, Master_Report_Type, Master_Report_JSON):
    """This creates a pandas dataframe based on the result of a SUSHI API call for a COUNTER R5 master report.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_Type {string} -- the ID for the master report type
        Master_Report_JSON {dict} -- the SUSHI API response in native Python data types
    
    Returns:
        dataframe -- the SUSHI API response data in a dataframe
        string -- the Master_Report_Type wasn't for a master report
    """
    if  Master_Report_Type == "PR":
        Create_PR_Dataframe(Interface, Master_Report_JSON)
    elif Master_Report_Type == "DR":
        Create_DR_Dataframe(Interface, Master_Report_JSON)
    elif Master_Report_Type == "TR":
        Create_TR_Dataframe(Interface, Master_Report_JSON)
    elif Master_Report_Type == "IR":
        Create_IR_Dataframe(Interface, Master_Report_JSON)
    else:
        #ToDo: If saving data from reports where no master report is available, determine where to send the JSON here
        # Currently, the function should never get here
        return "ERROR: Master_Report_Type"
    #ToDo: Send inputs to appropriate function for master report type
    #ToDo: Make other adjustments
    
    #Subsection: Create Single Time Field
        #ToDo: Confirm that fields for beginning and end of each time interval are for the beginning and end of a single month
        #ToDo: Create a field for that month and/or change name of beginning date field (as ISO for first date of that month)
        #ToDo: Remove unneeded date fields


#Section: Dataframe Creation Functions
def Create_PR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from a platform master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
    """
    #Subsection: Check Field Length Constraints
    #ToDo: Do these need to use loop constructs to get to all values at the dictionary key path?
    if len(Master_Report_JSON['Report_Items', 'Platform']) > Platform_Length:
        #ToDo: Create new variable holding largest found value of len(Master_Report_JSON['Report_Items', 'Platform'])
        pass

    #Subsection: Create Dataframe
    Dataframe = pandas.json_normalize(Master_Report_JSON, sep=":", meta=[
        Interface, # Interface
        Master_Report_JSON['Report_Header']['Report_ID'], # Report
        Master_Report_JSON['Report_Items', 'Platform'], # Platform
        Master_Report_JSON['Report_Items', 'Data_Type'], # Data_Type
        Master_Report_JSON['Report_Items', 'Access_Method'], # Access_Method
        Master_Report_JSON['Report_Items', 'Performance', 'Instance', 'Metric_Type'], # Metric_Type
        Master_Report_JSON['Report_Items', 'Performance', 'Period', 'Begin_Date'], # R5_Month
        Master_Report_JSON['Report_Items', 'Performance', 'Instance', 'Count'], # R5_Count
        Master_Report_JSON['Report_Header', 'Created'], # Report_Creation_Date
    ])

    #ToDo: If any new largest found values were created, create messagebox indicating what the max length for a given field was and presenting the option to not load the dataframe (adding info on report to Platforms_Not_Collected instead by returning string from these functions)

    return Dataframe


def Create_DR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from a database master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
    """
    #Subsection: Check Field Length Constraints
    #ToDo: Do these need to use loop constructs to get to all values at the dictionary key path?
    if len(Master_Report_JSON['Report_Items', 'Database']) > Resource_Name_Length:
        #ToDo: Create new variable holding largest found value of len(Master_Report_JSON['Report_Items', 'Database'])
        pass
    if len(Master_Report_JSON['Report_Items', 'Publisher']) > Publisher_Length:
        #ToDo: Create new variable holding largest found value of len(Master_Report_JSON['Report_Items', 'Publisher'])
        pass
    if len(Master_Report_JSON['Report_Items', 'Platform']) > Platform_Length:
        #ToDo: Create new variable holding largest found value of len(Master_Report_JSON['Report_Items', 'Platform'])
        pass

    #Subsection: Create Dataframe
    Dataframe = pandas.json_normalize(Master_Report_JSON, sep=":", meta=[
        Interface, # Interface
        Master_Report_JSON['Report_Header']['Report_ID'], # Report
        Master_Report_JSON['Report_Items', 'Database'], # Resource_Name
        Master_Report_JSON['Report_Items', 'Publisher'], # Publisher
        #ToDo: Should "Publisher_ID (len=50)" be kept in addition to or in favor of "Publisher"?
        Master_Report_JSON['Report_Items', 'Platform'], # Platform
        Master_Report_JSON['Report_Items', 'Item_ID'], # Proprietary_ID
        Master_Report_JSON['Report_Items', 'Data_Type'], # Data_Type
        Master_Report_JSON['Report_Items', 'Access_Method'], # Access_Method
        Master_Report_JSON['Report_Items', 'Performance', 'Instance', 'Metric_Type'], # Metric_Type
        Master_Report_JSON['Report_Items', 'Performance', 'Period', 'Begin_Date'], # R5_Month
        Master_Report_JSON['Report_Items', 'Performance', 'Instance', 'Count'], # R5_Count
        Master_Report_JSON['Report_Header', 'Created'], # Report_Creation_Date
    ])

    #ToDo: If any new largest found values were created, create messagebox indicating what the max length for a given field was and presenting the option to not load the dataframe (adding info on report to Platforms_Not_Collected instead by returning string from these functions)

    return Dataframe


def Create_TR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from a title master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
    """
    #Subsection: Check Field Length Constraints
    #ToDo: Do these need to use loop constructs to get to all values at the dictionary key path?
    if len(Master_Report_JSON['Report_Items', 'Title']) > Resource_Name_Length:
        #ToDo: Create new variable holding largest found value of len(Master_Report_JSON['Report_Items', 'Title'])
        pass
    if len(Master_Report_JSON['Report_Items', 'Publisher']) > Publisher_Length:
        #ToDo: Create new variable holding largest found value of len(Master_Report_JSON['Report_Items', 'Publisher'])
        pass
    if len(Master_Report_JSON['Report_Items', 'Platform']) > Platform_Length:
        #ToDo: Create new variable holding largest found value of len(Master_Report_JSON['Report_Items', 'Platform'])
        pass
    #if len(insert how to isolate DOI here) > DOI_Length:
        #ToDo: Create new variable holding largest found value
    #if len(insert how to isolate Proprietary_ID here) > Proprietary_ID_Length:
        #ToDo: Create new variable holding largest found value
    #if len(insert how to isolate URI here) > URI_Length:
        #ToDo: Create new variable holding largest found value

    #Subsection: Create Dataframe
    Dataframe = pandas.json_normalize(Master_Report_JSON, sep=":", meta=[
        Interface, # Interface
        Master_Report_JSON['Report_Header']['Report_ID'], # Report
        Master_Report_JSON['Report_Items', 'Title'], # Resource_Name
        Master_Report_JSON['Report_Items', 'Publisher'], # Publisher
        #ToDo: Should "Publisher_ID (len=50)" be kept in addition to or in favor of "Publisher"?
        Master_Report_JSON['Report_Items', 'Platform'], # Platform
        Master_Report_JSON['Report_Items', 'Item_ID'], # Proprietary_ID, DOI, ISBN, Print_ISSN, Online_ISSN, URI
        Master_Report_JSON['Report_Items', 'Data_Type'], # Data_Type
        Master_Report_JSON['Report_Items', 'Section_Type'], # `Section_Type
        Master_Report_JSON['Report_Items', 'YOP'], # YOP
        Master_Report_JSON['Report_Items', 'Access_Type'], # Access_Type
        Master_Report_JSON['Report_Items', 'Access_Method'], # Access_Method
        Master_Report_JSON['Report_Items', 'Performance', 'Instance', 'Metric_Type'], # Metric_Type
        Master_Report_JSON['Report_Items', 'Performance', 'Period', 'Begin_Date'], # R5_Month
        Master_Report_JSON['Report_Items', 'Performance', 'Instance', 'Count'], # R5_Count
        Master_Report_JSON['Report_Header', 'Created'], # Report_Creation_Date
    ])

    #ToDo: If any new largest found values were created, create messagebox indicating what the max length for a given field was and presenting the option to not load the dataframe (adding info on report to Platforms_Not_Collected instead by returning string from these functions)

    return Dataframe


def Create_IR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from an item master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
    """
    #Subsection: Check Field Length Constraints
    #ToDo: Do these need to use loop constructs to get to all values at the dictionary key path?
    if len(Master_Report_JSON['Report_Items', 'Item']) > Resource_Name_Length:
        #ToDo: Create new variable holding largest found value of len(Master_Report_JSON['Report_Items', 'Item'])
        pass
    if len(Master_Report_JSON['Report_Items', 'Publisher']) > Publisher_Length:
        #ToDo: Create new variable holding largest found value of len(Master_Report_JSON['Report_Items', 'Publisher'])
        pass
    if len(Master_Report_JSON['Report_Items', 'Platform']) > Platform_Length:
        #ToDo: Create new variable holding largest found value of len(Master_Report_JSON['Report_Items', 'Platform'])
        pass
    #if len(insert how to isolate DOI here) > DOI_Length:
        #ToDo: Create new variable holding largest found value
    #if len(insert how to isolate Proprietary_ID here) > Proprietary_ID_Length:
        #ToDo: Create new variable holding largest found value
    #if len(insert how to isolate URI here) > URI_Length:
        #ToDo: Create new variable holding largest found value
    #if len(insert how to isolate Parent_DOI here) > Parent_DOI_Length:
        #ToDo: Create new variable holding largest found value
    #if len(insert how to isolate Parent_Proprietary_ID here) > Parent_Proprietary_ID_Length:
        #ToDo: Create new variable holding largest found value

    #Subsection: Create Dataframe
    Dataframe = pandas.json_normalize(Master_Report_JSON, sep=":", meta=[
        Interface, # Interface
        Master_Report_JSON['Report_Header']['Report_ID'], # Report
        Master_Report_JSON['Report_Items', 'Item'], # Resource_Name
        Master_Report_JSON['Report_Items', 'Publisher'], # Publisher
        #ToDo: Should "Publisher_ID (len=50)" be kept in addition to or in favor of "Publisher"?
        Master_Report_JSON['Report_Items', 'Platform'], # Platform
        Master_Report_JSON['Report_Items', 'Item_ID'], # Proprietary_ID, DOI, ISBN, Print_ISSN, Online_ISSN, URI
        Master_Report_JSON['Report_Items', 'Data_Type'], # Data_Type
        Master_Report_JSON['Report_Items', 'Item_Parent', 'Data_Type'], # Parent_Data_Type
        Master_Report_JSON['Report_Items', 'Item_Parent', 'Item_ID'], # Parent_DOI, Parent_Proprietary_ID
        Master_Report_JSON['Report_Items', 'YOP'], # YOP
        Master_Report_JSON['Report_Items', 'Access_Type'], # Access_Type

        Master_Report_JSON['Report_Items', 'Access_Method'], # Access_Method
        Master_Report_JSON['Report_Items', 'Performance', 'Instance', 'Metric_Type'], # Metric_Type
        Master_Report_JSON['Report_Items', 'Performance', 'Period', 'Begin_Date'], # R5_Month
        Master_Report_JSON['Report_Items', 'Performance', 'Instance', 'Count'], # R5_Count
        Master_Report_JSON['Report_Header', 'Created'], # Report_Creation_Date
    ])

    #ToDo: If any new largest found values were created, create messagebox indicating what the max length for a given field was and presenting the option to not load the dataframe (adding info on report to Platforms_Not_Collected instead by returning string from these functions)

    return Dataframe


#Section: Field Length Constants
#ToDo: Is there a way to read metadata from MySQL into Python?
Resource_Name_Length = 150
Publisher_Length = 100
Platform_Length = 75
DOI_Length = 50
Proprietary_ID_Length = 50
URI_Length = 50
Parent_DOI_Length = 50
Parent_Proprietary_ID_Length = 50