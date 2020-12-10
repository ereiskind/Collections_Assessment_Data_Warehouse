import pandas

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


def Create_PR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from a platform master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
    """


def Create_DR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from a database master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
    """


def Create_TR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from a title master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
    """


def Create_IR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from an item master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
    """


#Section: JSON Locations
#Subsection: Interface 
    # SUSHI_Call_Data['JSON_Name']
#Subsection: Report
    # Master_Report_Response['Report_Header']['Report_ID']
#Subsection: Resource_Name (len=150)
    # Warning if longer than 150 characters
    # DR: ['Report_Items', 'Database']
    # IR: ['Report_Items', 'Item']
    # TR: ['Report_Items', 'Title']
#Subsection: Publisher (len=100)
    # Warning if longer than 100 characters
    # DR, TR, IR: ['Report_Items', 'Publisher']
#Subsection: Publisher_ID (len=50)
    # Should this be kept in addition to or in favor of "Publisher"?
#Subsection: Platform (not null) (len=75)
    # Warning if longer than 75 characters
    # ['Report_Items', 'Platform']
#Subsection: DOI (len=50)
    # Warning if longer than 50 characters
    # TR, IR: See ['Report_Items', 'Item_ID']
#Subsection: Proprietary_ID (len=50)
    # Warning if longer than 50 characters
    # DR, TR, IR: See ['Report_Items', 'Item_ID']
#Subsection: ISBN
    # TR, IR: See ['Report_Items', 'Item_ID']
#Subsection: Print_ISSN
    # TR, IR: See ['Report_Items', 'Item_ID']
#Subsection: Online_ISSN
    # TR, IR: See ['Report_Items', 'Item_ID']
#Subsection: URI (len=50)
    # Warning if longer than 50 characters
    # TR, IR: See ['Report_Items', 'Item_ID']
#Subsection: Data_Type (not null)
    # ['Report_Items', 'Data_Type']
#Subsection: `Section_Type
    # TR: ['Report_Items', 'Section_Type']
#Subsection: Parent_Data_Type
    # IR: ['Report_Items', 'Item_Parent', 'Data_Type']
#Subsection: Parent_DOI (len=50)
    # Warning if longer than 50 characters
    # IR: See ['Report_Items', 'Item_Parent', 'Item_ID']
#Subsection: Parent_Proprietary_ID (len=50)
    # Warning if longer than 50 characters
    # IR: See ['Report_Items', 'Item_Parent', 'Item_ID']
#Subsection: YOP (YOP unknown is "0001" and articles-in-press is "9999", so data type YEAR can't be used)
    # TR, IR: ['Report_Items', 'YOP']
#Subsection: Access_Type
    # TR, IR: ['Report_Items', 'Access_Type']
#Subsection: Access_Method (not null)
    # ['Report_Items', 'Access_Method']
#Subsection: Metric_Type (not null)
    # ['Report_Items', 'Performance', 'Instance', 'Metric_Type']
#Subsection: R5_Month (not null)
    # ['Report_Items', 'Performance', 'Period', 'Begin_Date']
#Subsection: R5_Count (not null)
    #  ['Report_Items', 'Performance', 'Instance', 'Count']
#Subsection: Report_Creation_Date
    # ['Report_Header', 'Created']