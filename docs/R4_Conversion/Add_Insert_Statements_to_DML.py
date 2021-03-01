#! /usr/local/bin/python

import logging
import os
from pathlib import Path
import sys


#Section: Function
def Prepare_Record_for_Database(Record, Interface_ID, Number_of_Fields):
    """Prepares the content of a record from an OpenRefine SQL Exporter file for upload to the R4_Usage table of the data warehouse.
    
    Arguments:
        Record {bytes} -- the content of the record from OpenRefine
        Interface_ID {int} -- the primary key for the source interface in the database
        Number_of_Fields {int} -- the number of records in the insert statement from OpenRefine
    
    Returns:
        bytes -- the content of the record ready for the insert statement
    """
    New_Record = [Interface_ID.encode('utf8')]
    Fields = Record.split(b"','")

    for i in range(0, Number_of_Fields-2):
        if Fields[i] == b"NULL":
            New_Record.append(b"NULL")
        else:
            New_Record.append(b"('" + Fields[i] + b"')")
    
    # The date and count are combined in Fields[Number_of_Fields-2] because the count value, as an int, doesn't have surrounding single quotes
    Date_and_Count = Fields[Number_of_Fields-2].split(b"',")
    New_Record.append(b"'" + Date_and_Count[0][:10] + b"'") # The slice takes only the ISO date
    New_Record.append(Date_and_Count[1]) # Integer doesn't need to be wrapped in single quotes

    return b", ".join(New_Record)


#Section: Set Up Logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s: %(message)s")

#Section: Open Files as Binary Files
#subsection: Open Main DML File
Main_DML_File = open(f'.\\mysql\\Version_0.1_DML.sql', 'ab')

#Subsection: Open the OpenRefine SQL Exporter Files, Collecting the Interface_ID Along the Way
for Folder in os.listdir('.\\Private_Info\\R4_Data'):
    if Path(f'.\\Private_Info\\R4_Data\\{Folder}').is_dir():
        logging.debug(f"Checking folder {Folder} for SQL files.")
        Interface_ID = Folder.split("--")[0]
        for File in os.listdir(f'.\\Private_Info\\R4_Data\\{Folder}'):
            if File.endswith(".sql"):
                try:
                    Insert_Statement = open(f'.\\Private_Info\\R4_Data\\{Folder}\\{File}', 'rb')
                    logging.debug(f"Adding insert statement {File} to DML file.")
                except: # Sometimes, a "OSError: [Errno 22] Invalid argument" error is raised despite the file names coming from a read of folder contents
                    logging.debug(f"The insert statement {File} couldn't be added to the database. To avoid having a missing insert statement, the program is ending.")
                    #toDo: Find a more elegant way to handle an insert statement tht can't be added to the main DML file because of a problem with opening it
                    Main_DML_File.close()
                    sys.exit()


                #Section: Reformat Insert Statement and Write to Main DML File
                #Subsection: Update and Write Start of Insert Statement
                try:
                    First_Line = Insert_Statement.readline().decode('utf8')
                    First_Line = First_Line.split("(")
                    First_Line[1] = First_Line[1].replace(",", ", ")
                    First_Line = "(Interface, ".join(First_Line)
                    Main_DML_File.write(First_Line.encode('utf8'))
                    Number_of_Fields = len(First_Line.split(", "))-1
                except:
                    logging.debug(f"Unable to write section of INSERT statement {Line} to main DML file. To avoid having a non-functional INSERT statement, the program is ending.")
                    Insert_Statement.close()
                    Main_DML_File.close()
                    sys.exit()

                #Subsection: Update and Write Records from Insert Statement
                for Line in Insert_Statement:
                    if Line.endswith(b",\n"): # The line is read as ending in a newline
                        Line = Line[3:-4] # Take from the fourth character to the third-from-last character
                        Line = Prepare_Record_for_Database(Line, Interface_ID, Number_of_Fields)
                        try:
                            Main_DML_File.write(b"(" + Line + b"),\n")
                        except:
                            logging.debug(f"Unable to write section of INSERT statement {Line} to main DML file. To avoid having a non-functional INSERT statement, the program is ending.")
                            Insert_Statement.close()
                            Main_DML_File.close()
                            sys.exit()
                    else: # The last record in the insert statement
                        Line = Line[3:-2] # Take from the fourth character to the second-from-last character
                        Line = Prepare_Record_for_Database(Line, Interface_ID, Number_of_Fields)
                        try:
                            Main_DML_File.write(b"(" + Line + b");")
                        except:
                            logging.debug(f"Unable to write section of INSERT statement {Line} to main DML file. To avoid having a non-functional INSERT statement, the program is ending.")
                            Insert_Statement.close()
                            Main_DML_File.close()
                            sys.exit()
                
                Main_DML_File.write(b"\n\n")
                logging.debug(f"Insert statement {File} in main DML file.")

Main_DML_File.close()