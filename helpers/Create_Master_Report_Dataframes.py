#! /usr/local/bin/python
import pandas
from tkinter import messagebox

#Section: Main Function
def Create_Dataframe(Interface, Master_Report_Type, Master_Report_JSON):
    """This creates a pandas dataframe based on the result of a SUSHI API call for a COUNTER R5 master report.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_Type {string} -- the ID for the master report type
        Master_Report_JSON {dict} -- the SUSHI API response in native Python data types
    
    Returns:
        dataframe -- the SUSHI API response data in a dataframe
        string -- the type and details of the problem preventing the data from being made into a dataframe seperated by a pipe
    """
    #Subsection: Send to Subfunction to Extract Appropriate Fields from JSON
    if  Master_Report_Type == "PR":
        Dataframe = Create_PR_Dataframe(Interface, Master_Report_JSON)
    elif Master_Report_Type == "DR":
        Dataframe = Create_DR_Dataframe(Interface, Master_Report_JSON)
    elif Master_Report_Type == "TR":
        Dataframe = Create_TR_Dataframe(Interface, Master_Report_JSON)
    elif Master_Report_Type == "IR":
        Dataframe = Create_IR_Dataframe(Interface, Master_Report_JSON)
    else:
        #ToDo: If saving data from reports where no master report is available, determine where to send the JSON here
        # Currently, the function should never get here
        return f"Unable to create dataframe|Master report type {Master_Report_Type} not recognized for creating a dataframe"
    
    if str(type(Dataframe)) == "<class 'str'>": # Meaning one of the values exceeded the max length for the field
        return Dataframe
    
    #Subsection: Change Data Types and Add Missing Columns to Match Final Database
    # Dataframe to MySQL--two hashes means in all reports
        ## "Interface" int64 --> Interface INT
        ## "Report" string --> Report CHAR
        # "Resource_Name" string --> Resource_Name VARCHAR
        # "Publisher" string --> Publisher VARCHAR
        # Publisher_ID VARCHAR
        ## "Platform" string --> Platform VARCHAR
        # "DOI" string --> DOI VARCHAR
        # "Proprietary_ID" string --> Proprietary_ID VARCHAR
        # "ISBN" string --> ISBN CHAR
        # "Print_ISSN" string --> Print_ISSN CHAR
        # "Online_ISSN" string --> Online_ISSN CHAR
        # "URI" string --> URI VARCHAR
        ## "Data_Type" string --> Data_Type VARCHAR
        # "Section_Type" string --> Section_Type VARCHAR
        # "Parent_Data_Type" string --> Parent_Data_Type VARCHAR
        # "Parent_DOI" string --> Parent_DOI VARCHAR
        # "Parent_Proprietary_ID" string --> Parent_Proprietary_ID VARCHAR
        # "YOP" int64 --> YOP SMALLINT (YOP unknown is "0001" and articles-in-press is "9999", so data type YEAR can't be used)
        # "Access_Type" string --> Access_Type VARCHAR
        ## "Access_Method" string --> Access_Method VARCHAR
        ## "Metric_Type" string --> Metric_Type VARCHAR
        ## "R5_Month" datetime64 --> R5_Month DATE
        ## "R5_Count" int64 --> R5_Count MEDIUMINT
        ## "Report_Creation_Date" datetime64 --> Report_Creation_Date DATE
    
    Dataframe = Dataframe.astype({
        'Interface': 'int64',
        'Report': 'string',
        'Platform': 'string',
        'Data_Type': 'string',
        'Metric_Type': 'string',
        'R5_Count': 'int64'
    })

    Dataframe['R5_Month'] = pandas.to_datetime(
        Dataframe['R5_Month'],
        errors='raise', # If ‘raise’, then invalid parsing will raise an exception; If ‘coerce’, then invalid parsing will be set as NaT; If ‘ignore’, then invalid parsing will return the input
        format='%Y-%m-%d'
    )
   
    Dataframe['Report_Creation_Date'] = pandas.to_datetime(
        Dataframe['Report_Creation_Date'],
        errors='raise', # If ‘raise’, then invalid parsing will raise an exception; If ‘coerce’, then invalid parsing will be set as NaT; If ‘ignore’, then invalid parsing will return the input
        format='%Y-%m-%dT',
        exact=False # Some dates use the timezone (indicated by "Z") while others use UTC offset, so the format just has the ISO date format
    )

    try:
        Dataframe['Resource_Name'] = Dataframe['Resource_Name'].astype('string')
        # Should there be a sanity/data check here that all DR, TR, IR records have a Resource_Name value?
    except KeyError:
        Dataframe['Resource_Name'] = None
        Dataframe['Resource_Name'] = Dataframe['Resource_Name'].astype('string')

    try:
        Dataframe['Publisher'] = Dataframe['Publisher'].astype('string')
    except KeyError:
        Dataframe['Publisher'] = None
        Dataframe['Publisher'] = Dataframe['Publisher'].astype('string')
    
    try:
        Dataframe['Access_Method'] = Dataframe['Access_Method'].astype('string')
    except KeyError:
        Dataframe['Access_Method'] = None
        Dataframe['Access_Method'] = Dataframe['Access_Method'].astype('string')

    #ToDo: If adding Publisher_ID as data saved, change to add null value only if column not already present
    Dataframe['Publisher_ID'] = None
    Dataframe['Publisher_ID'] = Dataframe['Publisher_ID'].astype('string')

    try:
        Dataframe['DOI'] = Dataframe['DOI'].astype('string')
    except KeyError:
        Dataframe['DOI'] = None
        Dataframe['DOI'] = Dataframe['DOI'].astype('string')

    try:
        Dataframe['Proprietary_ID'] = Dataframe['Proprietary_ID'].astype('string')
    except KeyError:
        Dataframe['Proprietary_ID'] = None
        Dataframe['Proprietary_ID'] = Dataframe['Proprietary_ID'].astype('string')

    try:
        Dataframe['ISBN'] = Dataframe['ISBN'].astype('string')
    except KeyError:
        Dataframe['ISBN'] = None
        Dataframe['ISBN'] = Dataframe['ISBN'].astype('string')

    try:
        Dataframe['Print_ISSN'] = Dataframe['Print_ISSN'].astype('string')
    except KeyError:
        Dataframe['Print_ISSN'] = None
        Dataframe['Print_ISSN'] = Dataframe['Print_ISSN'].astype('string')

    try:
        Dataframe['Online_ISSN'] = Dataframe['Online_ISSN'].astype('string')
    except KeyError:
        Dataframe['Online_ISSN'] = None
        Dataframe['Online_ISSN'] = Dataframe['Online_ISSN'].astype('string')

    try:
        Dataframe['URI'] = Dataframe['URI'].astype('string')
    except KeyError:
        Dataframe['URI'] = None
        Dataframe['URI'] = Dataframe['URI'].astype('string')

    try:
        Dataframe['Section_Type'] = Dataframe['Section_Type'].astype('string')
    except KeyError:
        Dataframe['Section_Type'] = None
        Dataframe['Section_Type'] = Dataframe['Section_Type'].astype('string')

    try:
        Dataframe['Parent_Data_Type'] = Dataframe['Parent_Data_Type'].astype('string')
    except KeyError:
        Dataframe['Parent_Data_Type'] = None
        Dataframe['Parent_Data_Type'] = Dataframe['Parent_Data_Type'].astype('string')

    try:
        Dataframe['Parent_DOI'] = Dataframe['Parent_DOI'].astype('string')
    except KeyError:
        Dataframe['Parent_DOI'] = None
        Dataframe['Parent_DOI'] = Dataframe['Parent_DOI'].astype('string')

    try:
        Dataframe['Parent_Proprietary_ID'] = Dataframe['Parent_Proprietary_ID'].astype('string')
    except KeyError:
        Dataframe['Parent_Proprietary_ID'] = None
        Dataframe['Parent_Proprietary_ID'] = Dataframe['Parent_Proprietary_ID'].astype('string')

    try:
        Dataframe['YOP'] = Dataframe['YOP'].astype('int64')
    except KeyError:
        Dataframe['YOP'] = None
        Dataframe['YOP'] = Dataframe['YOP'].astype('Int64') # The capital "I" is a pandas data type that allows for nulls (https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html)

    try:
        Dataframe['Access_Type'] = Dataframe['Access_Type'].astype('string')
    except KeyError:
        Dataframe['Access_Type'] = None
        Dataframe['Access_Type'] = Dataframe['Access_Type'].astype('string')
    
    #Subsection: Reorder Columns for Import to MySQL
    Dataframe = Dataframe[[
        'Interface',
        'Report',
        'Resource_Name',
        'Publisher',
        'Publisher_ID',
        'Platform',
        'DOI',
        'Proprietary_ID',
        'ISBN',
        'Print_ISSN',
        'Online_ISSN',
        'URI',
        'Data_Type',
        'Section_Type',
        'Parent_Data_Type',
        'Parent_DOI',
        'Parent_Proprietary_ID',
        'YOP',
        'Access_Type',
        'Access_Method',
        'Metric_Type',
        'R5_Month',
        'R5_Count',
        'Report_Creation_Date'
    ]]
    
    return Dataframe


#Section: Dataframe Creation Functions
def Create_PR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from a platform master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
        string -- the type and details of the problem preventing the data from being made into a dataframe seperated by a pipe
    """
    global Platform_Length
    Update_Max_Platform_Length = False

    Dataframe_Records = []

    Report = Master_Report_JSON['Report_Header']['Report_ID']
    Report_Creation_Date = Master_Report_JSON['Report_Header']['Created']
    
    for Item in Master_Report_JSON['Report_Items']:
        
        try:
            Platform = Item['Platform']
            if len(Platform) > Platform_Length:
                Update_Max_Platform_Length = True
                Platform_Length = len(Platform)
        except TypeError: # The JSON contained a null value, so trying to find the length put up an error
            Platform = None
        
        try: # This handles situations where data types aren't included
            Data_Type = Item['Data_Type']
        except KeyError:
            Data_Type = None
        
        try: # This handles situations where access methods aren't included
            Access_Method = Item['Access_Method']
        except KeyError:
            Access_Method = None
        
        for Time_Period in Item['Performance']:
            R5_Month = Time_Period['Period']['Begin_Date']
            for Statstic in Time_Period['Instance']:
                Metric_Type = Statstic['Metric_Type']
                R5_Count = Statstic['Count']

                Dataframe_Records.append({
                    "Interface": Interface,
                    "Report": Report,
                    "Report_Creation_Date": Report_Creation_Date,
                    "Platform": Platform,
                    "Data_Type": Data_Type,
                    "Access_Method": Access_Method,
                    "R5_Month": R5_Month,
                    "Metric_Type": Metric_Type,
                    "R5_Count": R5_Count,
                })
    Dataframe = pandas.DataFrame(Dataframe_Records)

    if Update_Max_Platform_Length:
        messagebox.showwarning(title="Max Platform Length Exceeded", message=f"The platform report for interface {Interface} has values for the field \"Platform\" exceeding the field's max character length. Update the field to greater than {Platform_Length} characters.")
        return f"Unable to create PR dataframe|Values in \"Platform\" are {Platform_Length} characters long and would have been truncated on import to MySQL"

    return Dataframe


def Create_DR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from a database master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
        string -- the type and details of the problem preventing the data from being made into a dataframe seperated by a pipe
    """
    global Platform_Length
    global Resource_Name_Length
    global Publisher_Length
    Update_Max_Platform_Length = False
    Update_Max_Resource_Name_Length = False
    Update_Max_Publisher_Length = False

    Dataframe_Records = []

    Report = Master_Report_JSON['Report_Header']['Report_ID']
    Report_Creation_Date = Master_Report_JSON['Report_Header']['Created']
    
    for Item in Master_Report_JSON['Report_Items']:
        
        try:
            Resource_Name = Item['Database']
            if len(Resource_Name) > Resource_Name_Length:
                Update_Max_Resource_Name_Length = True
                Resource_Name_Length = len(Resource_Name)
        except TypeError: # The JSON contained a null value, so trying to find the length put up an error
            Resource_Name = None
        
        try:
            Publisher = Item['Publisher']
            if len(Publisher) > Publisher_Length:
                Update_Max_Publisher_Length = True
                Publisher_Length = len(Publisher)
        except TypeError: # The JSON contained a null value, so trying to find the length put up an error
            Publisher = None
        
        try:
            Platform = Item['Platform']
            if len(Platform) > Platform_Length:
                Update_Max_Platform_Length = True
                Platform_Length = len(Platform)
        except TypeError: # The JSON contained a null value, so trying to find the length put up an error
            Platform = None
        
        try: # This handles situations where data types aren't included
            Data_Type = Item['Data_Type']
        except KeyError:
            Data_Type = None
        
        try:  # This handles situations where access methods aren't included
            Access_Method = Item['Access_Method']
        except KeyError:
            Access_Method - None
        
        try: # This handles situations where proprietary IDs aren't included
            for ID in Item['Item_ID']:
                if ID['Type'] == "Proprietary":
                    Proprietary_ID = ID['Value']
        except KeyError:
            Proprietary_ID = None
        
        for Time_Period in Item['Performance']:
            R5_Month = Time_Period['Period']['Begin_Date']
            for Statstic in Time_Period['Instance']:
                Metric_Type = Statstic['Metric_Type']
                R5_Count = Statstic['Count']

                Record = {
                    "Interface": Interface,
                    "Report": Report,
                    "Report_Creation_Date": Report_Creation_Date,
                    "Resource_Name": Resource_Name,
                    "Publisher": Publisher,
                    #ToDo: Should "Publisher_ID (len=50)" be kept in addition to or in favor of "Publisher"?
                    "Platform": Platform,
                    "Data_Type": Data_Type,
                    "Access_Method": Access_Method,
                    "R5_Month": R5_Month,
                    "Metric_Type": Metric_Type,
                    "R5_Count": R5_Count,
                    "Proprietary_ID": Proprietary_ID,
                }
                Dataframe_Records.append(Record)
    Dataframe = pandas.DataFrame(Dataframe_Records)

    if Update_Max_Platform_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The database report for interface {Interface} has values for the field \"Platform\" exceeding the field's max character length. Update the field to greater than {Platform_Length} characters.")
        return f"Unable to create DR dataframe|Values in \"Platform\" are {Platform_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_Resource_Name_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The database report for interface {Interface} has values for the field \"Resource_Name\" exceeding the field's max character length. Update the field to greater than {Resource_Name_Length} characters.")
        return f"Unable to create DR dataframe|Values in \"Resource_Name\" are {Resource_Name_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_Publisher_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The database report for interface {Interface} has values for the field \"Publisher\" exceeding the field's max character length. Update the field to greater than {Publisher_Length} characters.")
        return f"Unable to create DR dataframe|Values in \"Publisher\" are {Publisher_Length} characters long and would have been truncated on import to MySQL"

    return Dataframe


def Create_TR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from a title master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
        string -- the type and details of the problem preventing the data from being made into a dataframe seperated by a pipe
    """
    global Platform_Length
    global Resource_Name_Length
    global Publisher_Length
    global DOI_Length
    global Proprietary_ID_Length
    global URI_Length
    Update_Max_Platform_Length = False
    Update_Max_Resource_Name_Length = False
    Update_Max_Publisher_Length = False
    Update_Max_DOI_Length = False
    Update_Max_Proprietary_ID_Length = False
    Update_Max_URI_Length = False

    Dataframe_Records = []

    Report = Master_Report_JSON['Report_Header']['Report_ID']
    Report_Creation_Date = Master_Report_JSON['Report_Header']['Created']
    
    for Item in Master_Report_JSON['Report_Items']:
        
        try:
            Resource_Name = Item['Title']
            if len(Resource_Name) > Resource_Name_Length:
                Update_Max_Resource_Name_Length = True
                Resource_Name_Length = len(Resource_Name)
        except TypeError: # The JSON contained a null value, so trying to find the length put up an error
            Resource_Name = None
        
        try:
            Publisher = Item['Publisher']
            if len(Publisher) > Publisher_Length:
                Update_Max_Publisher_Length = True
                Publisher_Length = len(Publisher)
        except TypeError: # The JSON contained a null value, so trying to find the length put up an error
            Publisher = None
        
        try:
            Platform = Item['Platform']
            if len(Platform) > Platform_Length:
                Update_Max_Platform_Length = True
                Platform_Length = len(Platform)
        except TypeError: # The JSON contained a null value, so trying to find the length put up an error
            Platform = None
        
        for ID in Item['Item_ID']:
            if ID['Type'] == "Proprietary":
                Proprietary_ID = ID['Value']
                if len(Proprietary_ID) > Proprietary_ID_Length:
                    Update_Max_Proprietary_ID_Length = True
                    Proprietary_ID_Length = len(Proprietary_ID)
            if ID['Type'] == "DOI":
                DOI = ID['Value']
                if len(DOI) > DOI_Length:
                    Update_Max_DOI_Length = True
                    DOI_Length = len(DOI)
            if ID['Type'] == "ISBN":
                ISBN = ID['Value']
            if ID['Type'] == "Print_ISSN":
                Print_ISSN = ID['Value']
            if ID['Type'] == "Online_ISSN":
                Online_ISSN = ID['Value']
            if ID['Type'] == "URI":
                URI = ID['Value']
                if len(URI) > URI_Length:
                    Update_Max_URI_Length = True
                    URI_Length = len(URI)
        
        Data_Type = Item['Data_Type']
        
        try: # This handles situations where section types aren't included
            Section_Type = Item['Section_Type']
        except KeyError:
            Section_Type = None
        
        YOP = Item['YOP']
        
        Access_Type = Item['Access_Type']
        
        Access_Method = Item['Access_Method']
        
        for Time_Period in Item['Performance']:
            R5_Month = Time_Period['Period']['Begin_Date']
            for Statstic in Time_Period['Instance']:
                Metric_Type = Statstic['Metric_Type']
                R5_Count = Statstic['Count']

                Record = {
                    "Interface": Interface,
                    "Report": Report,
                    "Report_Creation_Date": Report_Creation_Date,
                    "Resource_Name": Resource_Name,
                    "Publisher": Publisher,
                    #ToDo: Should "Publisher_ID (len=50)" be kept in addition to or in favor of "Publisher"?
                    "Platform": Platform,
                    "Data_Type": Data_Type,
                    "Section_Type": Section_Type,
                    "YOP": YOP,
                    "Access_Type": Access_Type,
                    "Access_Method": Access_Method,
                    "R5_Month": R5_Month,
                    "Metric_Type": Metric_Type,
                    "R5_Count": R5_Count,
                }

                try:
                    Record["Proprietary_ID"] = Proprietary_ID
                except UnboundLocalError: # There wasn't a Proprietary_ID
                    Record["Proprietary_ID"] = None

                try:
                    Record["DOI"] = DOI
                except UnboundLocalError: # There wasn't a DOI
                    Record["DOI"] = None

                try:
                    Record["ISBN"] = ISBN
                except UnboundLocalError: # There wasn't an ISBN
                    Record["ISBN"] = None

                try:
                    Record["Print_ISSN"] = Print_ISSN
                except UnboundLocalError: # There wasn't a Print_ISSN
                    Record["Print_ISSN"] = None

                try:
                    Record["Online_ISSN"] = Online_ISSN
                except UnboundLocalError: # There wasn't an Online_ISSN
                    Record["Online_ISSN"] = None

                try:
                    Record["URI"] = URI
                except UnboundLocalError: # There wasn't an URI
                    Record["URI"] = None

                Dataframe_Records.append(Record)
    Dataframe = pandas.DataFrame(Dataframe_Records)

    if Update_Max_Platform_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The title report for interface {Interface} has values for the field \"Platform\" exceeding the field's max character length. Update the field to greater than {Platform_Length} characters.")
        return f"Unable to create TR dataframe|Values in \"Platform\" are {Platform_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_Resource_Name_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The title report for interface {Interface} has values for the field \"Resource_Name\" exceeding the field's max character length. Update the field to greater than {Resource_Name_Length} characters.")
        return f"Unable to create TR dataframe|Values in \"Resource_Name\" are {Resource_Name_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_Publisher_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The title report for interface {Interface} has values for the field \"Publisher\" exceeding the field's max character length. Update the field to greater than {Publisher_Length} characters.")
        return f"Unable to create TR dataframe|Values in \"Publisher\" are {Publisher_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_DOI_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The title report for interface {Interface} has values for the field \"DOI\" exceeding the field's max character length. Update the field to greater than {DOI_Length} characters.")
        return f"Unable to create TR dataframe|Values in \"DOI\" are {DOI_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_Proprietary_ID_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The title report for interface {Interface} has values for the field \"Proprietary_ID\" exceeding the field's max character length. Update the field to greater than {Proprietary_ID_Length} characters.")
        return f"Unable to create TR dataframe|Values in \"Proprietary_ID\" are {Proprietary_ID_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_URI_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The title report for interface {Interface} has values for the field \"URI\" exceeding the field's max character length. Update the field to greater than {URI_Length} characters.")
        return f"Unable to create TR dataframe|Values in \"URI\" are {URI_Length} characters long and would have been truncated on import to MySQL"

    return Dataframe


def Create_IR_Dataframe(Interface, Master_Report_JSON):
    """This creates a pandas dataframe from an item master report JSON.
    
    Arguments:
        Interface {int} -- the ID for the interface
        Master_Report_JSON {dict} -- the master report JSON in native Python data types
    
    Returns:
        dataframe -- the master report data in a dataframe
        string -- the type and details of the problem preventing the data from being made into a dataframe seperated by a pipe
    """
    global Platform_Length
    global Resource_Name_Length
    global Publisher_Length
    global DOI_Length
    global Proprietary_ID_Length
    global URI_Length
    global Parent_DOI_Length
    global Parent_Proprietary_ID_Length
    Update_Max_Platform_Length = False
    Update_Max_Resource_Name_Length = False
    Update_Max_Publisher_Length = False
    Update_Max_DOI_Length = False
    Update_Max_Proprietary_ID_Length = False
    Update_Max_URI_Length = False
    Update_Max_Parent_DOI_Length = False
    Update_Max_Parent_Proprietary_ID_Length = False

    Dataframe_Records = []

    Report = Master_Report_JSON['Report_Header']['Report_ID']
    Report_Creation_Date = Master_Report_JSON['Report_Header']['Created']
    
    for Item in Master_Report_JSON['Report_Items']:
        
        try:
            Resource_Name = Item['Item']
            if len(Resource_Name) > Resource_Name_Length:
                Update_Max_Resource_Name_Length = True
                Resource_Name_Length = len(Resource_Name)
        except KeyError: # The key wasn't included in the JSON
            Resource_Name = None
        except TypeError: # The JSON contained a null value, so trying to find the length put up an error
            Resource_Name = None
        
        try:
            Publisher = Item['Publisher']
            if len(Publisher) > Publisher_Length:
                Update_Max_Publisher_Length = True
                Publisher_Length = len(Publisher)
        except KeyError: # the key wasn't included in the JSON
            Publisher = None
        except TypeError: # The JSON contained a null value, so trying to find the length put up an error
            Publisher = None
        
        try:
            Platform = Item['Platform']
            if len(Platform) > Platform_Length:
                Update_Max_Platform_Length = True
                Platform_Length = len(Platform)
        except TypeError: # The JSON contained a null value, so trying to find the length put up an error
            Platform = None
        
        try: # This handles situations where no item IDs are included
            for ID in Item['Item_ID']:
                if ID['Type'] == "Proprietary":
                    Proprietary_ID = ID['Value']
                    if len(Proprietary_ID) > Proprietary_ID_Length:
                        Update_Max_Proprietary_ID_Length = True
                        Proprietary_ID_Length = len(Proprietary_ID)
                if ID['Type'] == "DOI":
                    DOI = ID['Value']
                    if len(DOI) > DOI_Length:
                        Update_Max_DOI_Length = True
                        DOI_Length = len(DOI)
                if ID['Type'] == "ISBN": #ToDo: Check if ISBNs are ever used in item-level IDs
                    ISBN = ID['Value']
                if ID['Type'] == "Print_ISSN": #ToDo: Check if ISSNs are ever used in item-level IDs
                    Print_ISSN = ID['Value']
                if ID['Type'] == "Online_ISSN": #ToDo: Check if eISSNs are ever used in item-level IDs
                    Online_ISSN = ID['Value']
                if ID['Type'] == "URI":
                    URI = ID['Value']
                    if len(URI) > URI_Length:
                        Update_Max_URI_Length = True
                        URI_Length = len(URI)
        except KeyError:
            pass # The "try-except UnboundLocalError" blocks below will handle all of the variables from above
        
        Data_Type = Item['Data_Type']
        
        try:
            Parent_Data_Type = Item['Item_Parent']['Data_Type']
            for Parent_ID in Item['Item_Parent']['Item_ID']:
                if Parent_ID['Type'] == "DOI":
                    Parent_DOI = Parent_ID['Value']
                    if len(Parent_DOI) > Parent_DOI_Length:
                        Update_Max_Parent_DOI_Length = True
                        Parent_DOI_Length = len(Parent_DOI)
                if Parent_ID['Type'] == "Proprietary":
                    Parent_Proprietary_ID = Parent_ID['Value']
                    if len(Parent_Proprietary_ID) > Parent_Proprietary_ID_Length:
                        Update_Max_Parent_Proprietary_ID_Length = True
                        Parent_Proprietary_ID_Length = len(Parent_Proprietary_ID)
        except KeyError: # This handles situations where item parent info isn't included
            Parent_Data_Type = None # The "try-except UnboundLocalError" blocks below will handle the parent ID variables
        except TypeError: # This handles situations where the value for the key "Item_Parent" is a list containing a single dictionary
            for Parent in Item['Item_Parent']:
                Parent_Data_Type = Parent['Data_Type']
                for Parent_ID in Parent['Item_ID']:
                    if Parent_ID['Type'] == "DOI":
                        Parent_DOI = Parent_ID['Value']
                        if len(Parent_DOI) > Parent_DOI_Length:
                            Update_Max_Parent_DOI_Length = True
                            Parent_DOI_Length = len(Parent_DOI)
                    if Parent_ID['Type'] == "Proprietary":
                        Parent_Proprietary_ID = Parent_ID['Value']
                        if len(Parent_Proprietary_ID) > Parent_Proprietary_ID_Length:
                            Update_Max_Parent_Proprietary_ID_Length = True
                            Parent_Proprietary_ID_Length = len(Parent_Proprietary_ID)
        
        try:
            YOP = Item['YOP']
        except KeyError:
            YOP = None
        
        Access_Type = Item['Access_Type']
        
        Access_Method = Item['Access_Method']
        
        for Time_Period in Item['Performance']:
            R5_Month = Time_Period['Period']['Begin_Date']
            for Statstic in Time_Period['Instance']:
                Metric_Type = Statstic['Metric_Type']
                R5_Count = Statstic['Count']

                Record = {
                    "Interface": Interface,
                    "Report": Report,
                    "Report_Creation_Date": Report_Creation_Date,
                    "Resource_Name": Resource_Name,
                    "Publisher": Publisher,
                    #ToDo: Should "Publisher_ID (len=50)" be kept in addition to or in favor of "Publisher"?
                    "Platform": Platform,
                    "Data_Type": Data_Type,
                    "Parent_Data_Type": Parent_Data_Type,
                    "YOP": YOP,
                    "Access_Type": Access_Type,
                    "Access_Method": Access_Method,
                    "R5_Month": R5_Month,
                    "Metric_Type": Metric_Type,
                    "R5_Count": R5_Count,
                }

                try:
                    Record["Proprietary_ID"] = Proprietary_ID
                except UnboundLocalError: # There wasn't a Proprietary_ID
                    Record["Proprietary_ID"] = None

                try:
                    Record["DOI"] = DOI
                except UnboundLocalError: # There wasn't a DOI
                    Record["DOI"] = None

                try:
                    Record["ISBN"] = ISBN
                except UnboundLocalError: # There wasn't an ISBN
                    Record["ISBN"] = None

                try:
                    Record["Print_ISSN"] = Print_ISSN
                except UnboundLocalError: # There wasn't a Print_ISSN
                    Record["Print_ISSN"] = None

                try:
                    Record["Online_ISSN"] = Online_ISSN
                except UnboundLocalError: # There wasn't an Online_ISSN
                    Record["Online_ISSN"] = None

                try:
                    Record["URI"] = URI
                except UnboundLocalError: # There wasn't an URI
                    Record["URI"] = None

                try:
                    Record["Parent_DOI"] = Parent_DOI
                except UnboundLocalError: # There wasn't a Parent_DOI
                    Record["Parent_DOI"] = None

                try:
                    Record["Parent_Proprietary_ID"] = Parent_Proprietary_ID
                except UnboundLocalError: # There wasn't a Parent_Proprietary_ID
                    Record["Parent_Proprietary_ID"] = None

                Dataframe_Records.append(Record)
    Dataframe = pandas.DataFrame(Dataframe_Records)

    if Update_Max_Platform_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The item report for interface {Interface} has values for the field \"Platform\" exceeding the field's max character length. Update the field to greater than {Platform_Length} characters.")
        return f"Unable to create IR dataframe|Values in \"Platform\" are {Platform_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_Resource_Name_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The item report for interface {Interface} has values for the field \"Resource_Name\" exceeding the field's max character length. Update the field to greater than {Resource_Name_Length} characters.")
        return f"Unable to create IR dataframe|Values in \"Resource_Name\" are {Resource_Name_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_Publisher_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The item report for interface {Interface} has values for the field \"Publisher\" exceeding the field's max character length. Update the field to greater than {Publisher_Length} characters.")
        return f"Unable to create IR dataframe|Values in \"Publisher\" are {Publisher_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_DOI_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The item report for interface {Interface} has values for the field \"DOI\" exceeding the field's max character length. Update the field to greater than {DOI_Length} characters.")
        return f"Unable to create IR dataframe|Values in \"DOI\" are {DOI_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_Proprietary_ID_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The item report for interface {Interface} has values for the field \"Proprietary_ID\" exceeding the field's max character length. Update the field to greater than {Proprietary_ID_Length} characters.")
        return f"Unable to create IR dataframe|Values in \"Proprietary_ID\" are {Proprietary_ID_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_URI_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The item report for interface {Interface} has values for the field \"URI\" exceeding the field's max character length. Update the field to greater than {URI_Length} characters.")
        return f"Unable to create IR dataframe|Values in \"URI\" are {URI_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_Parent_DOI_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The item report for interface {Interface} has values for the field \"Parent_DOI\" exceeding the field's max character length. Update the field to greater than {Parent_DOI_Length} characters.")
        return f"Unable to create IR dataframe|Values in \"Parent_DOI\" are {Parent_DOI_Length} characters long and would have been truncated on import to MySQL"
    if Update_Max_Parent_Proprietary_ID_Length:
        messagebox.showwarning(title="Max Field Length Exceeded", message=f"The item report for interface {Interface} has values for the field \"Parent_Proprietary_ID\" exceeding the field's max character length. Update the field to greater than {Parent_Proprietary_ID_Length} characters.")
        return f"Unable to create IR dataframe|Values in \"Parent_Proprietary_ID\" are {Parent_Proprietary_ID_Length} characters long and would have been truncated on import to MySQL"

    return Dataframe


#Section: Field Length Constants
#ToDo: Is there a way to read metadata from MySQL into Python?
Resource_Name_Length = 1500
Publisher_Length = 100
Platform_Length = 75
DOI_Length = 50
Proprietary_ID_Length = 50
URI_Length = 200
Parent_DOI_Length = 50
Parent_Proprietary_ID_Length = 50