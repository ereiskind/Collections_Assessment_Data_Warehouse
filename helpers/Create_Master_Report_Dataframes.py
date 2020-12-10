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
    
    #ToDo: Make any other adjustments
    
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
        Platform = Item['Platform']
        if len(Platform) > Platform_Length:
            Update_Max_Platform_Length = True
            Platform_Length = len(Platform)
        #ToDo: Key Data_Type not always available (KeyError)
        Data_Type = Item['Data_Type']
        #ToDo: Key Access_Method not always available (KeyError)
        Access_Method = Item['Access_Method']
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
        Resource_Name = Item['Database']
        if len(Resource_Name) > Resource_Name_Length:
            Update_Max_Resource_Name_Length = True
            Resource_Name_Length = len(Resource_Name)
        Publisher = Item['Publisher']
        if len(Publisher) > Publisher_Length:
            Update_Max_Publisher_Length = True
            Publisher_Length = len(Publisher)
        Platform = Item['Platform']
        if len(Platform) > Platform_Length:
            Update_Max_Platform_Length = True
            Platform_Length = len(Platform)
        try: # This handles situations where data types aren't included
            Data_Type = Item['Data_Type']
        except KeyError:
            Data_Type = None #ToDo: Confirm this is registering as a null value
        Access_Method = Item['Access_Method']
        try: # This handles situations where proprietary IDs aren't included
            for ID in Item['Item_ID']:
                if ID['Type'] == "Proprietary":
                    Proprietary_ID = ID['Value']
        except KeyError:
            Proprietary_ID = None #ToDo: Confirm this is registering as a null value
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
        Resource_Name = Item['Title']
        if len(Resource_Name) > Resource_Name_Length:
            Update_Max_Resource_Name_Length = True
            Resource_Name_Length = len(Resource_Name)
        Publisher = Item['Publisher']
        if len(Publisher) > Publisher_Length:
            Update_Max_Publisher_Length = True
            Publisher_Length = len(Publisher)
        Platform = Item['Platform']
        if len(Platform) > Platform_Length:
            Update_Max_Platform_Length = True
            Platform_Length = len(Platform)
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
            Section_Type = None #ToDo: Confirm this is registering as a null value
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
                    Record["Proprietary_ID"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["DOI"] = DOI
                except UnboundLocalError: # There wasn't a DOI
                    Record["DOI"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["ISBN"] = ISBN
                except UnboundLocalError: # There wasn't an ISBN
                    Record["ISBN"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["Print_ISSN"] = Print_ISSN
                except UnboundLocalError: # There wasn't a Print_ISSN
                    Record["Print_ISSN"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["Online_ISSN"] = Online_ISSN
                except UnboundLocalError: # There wasn't an Online_ISSN
                    Record["Online_ISSN"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["URI"] = URI
                except UnboundLocalError: # There wasn't an URI
                    Record["URI"] = None #ToDo: Confirm this is registering as a null value

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
        Resource_Name = Item['Item']
        if len(Resource_Name) > Resource_Name_Length:
            Update_Max_Resource_Name_Length = True
            Resource_Name_Length = len(Resource_Name)
        try: # This handles situations where publishers aren't included
            Publisher = Item['Publisher']
            if len(Publisher) > Publisher_Length:
                Update_Max_Publisher_Length = True
                Publisher_Length = len(Publisher)
        except KeyError:
            Publisher = None #ToDo: Confirm this is registering as a null value
        Platform = Item['Platform']
        if len(Platform) > Platform_Length:
            Update_Max_Platform_Length = True
            Platform_Length = len(Platform)
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
                    Record["Proprietary_ID"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["DOI"] = DOI
                except UnboundLocalError: # There wasn't a DOI
                    Record["DOI"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["ISBN"] = ISBN
                except UnboundLocalError: # There wasn't an ISBN
                    Record["ISBN"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["Print_ISSN"] = Print_ISSN
                except UnboundLocalError: # There wasn't a Print_ISSN
                    Record["Print_ISSN"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["Online_ISSN"] = Online_ISSN
                except UnboundLocalError: # There wasn't an Online_ISSN
                    Record["Online_ISSN"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["URI"] = URI
                except UnboundLocalError: # There wasn't an URI
                    Record["URI"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["Parent_DOI"] = Parent_DOI
                except UnboundLocalError: # There wasn't a Parent_DOI
                    Record["Parent_DOI"] = None #ToDo: Confirm this is registering as a null value

                try:
                    Record["Parent_Proprietary_ID"] = Parent_Proprietary_ID
                except UnboundLocalError: # There wasn't a Parent_Proprietary_ID
                    Record["Parent_Proprietary_ID"] = None #ToDo: Confirm this is registering as a null value

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