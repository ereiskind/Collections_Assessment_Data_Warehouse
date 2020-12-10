# This serves as the library for the API calls and the ensuing status checks

import time
from pathlib import Path
import json
import os
import requests
from requests import HTTPError, Timeout
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#Subsection: Helper Functions
def Retrieve_Downloaded_JSON_File(WebDriver, URL):
    """Reads a JSON downloaded by an API call into memory.
    
    Some of the SUSHI API calls, most notable Silverchair, generate a JSON file download, which requests returns as a 403 error. This function captures the downloaded file and reads its contents into memory so the function can be used. Functionality related to downloading the file taken from https://medium.com/@moungpeter/how-to-automate-downloading-files-using-python-selenium-and-headless-chrome-9014f0cdd196.

    Arguments:
        browser {WebDriver} -- Selenium WebDriver used to access internet
        download_dir {File path} -- location the file should be downloaded to
        WebDriver {WebDriver} -- Selenium WebDriver used to access internet
        URL {string} -- the URL for performing the API call
    
    Returns:
        dictionary -- the API response JSON file transformed into Python data types
    """
    # The function requires a string containing the absolute path to the location where the file should be saved; this allows for a folder "API_Download" within the repo to hold the file
    API_Download_Folder = str(Path.cwd()) + r"\API_Download"

    # From source: "function to handle setting up headless download"
    WebDriver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': API_Download_Folder}}
    WebDriver.execute("send_command", params)
    WebDriver.get(URL) # From source: "get request to target the site selenium is active on"

    time.sleep(0.1) # This delay allows the downloaded JSON to be in the folder for long enough that the walk method can detect it
    for Folder, Subfolder, Files in os.walk(API_Download_Folder):
        if Files == []: # This means the 403 error was the result of something other than the data being downloaded as a JSON file
            return Files
        for File in Files: # There is actually only one file, but the iterator is needed to extract it from the list data structure
            Download_File_Path = str(Path('.', 'API_Download', File))
            with open(Download_File_Path) as JSONfile:
                JSON_File_Data = json.load(JSONfile)
            os.unlink(Download_File_Path)

    return JSON_File_Data


def JSON_to_Python_Data_Types(JSON):
    """Returns a JSON-like object that uses Python data types from multiple different forms of input that include JSON formatted data.
    This function takes a JSON-like Python dictionary, JSON-like Python list, requests object with JSON data, or <insert other objects here> and returns the same data using native Python data types.
    Arguments:
        JSON {varies} -- an object containing a JSON or JSON-like data
    Returns:
        dictionary or list -- the data in JSON using Python data types
    """
    if str(type(JSON)) == "<class 'dict'>":
        return JSON
    elif str(type(JSON)) == "<class 'list'>": #Alert: Not yet tested
        return JSON
    elif str(type(JSON)) == "<class 'requests.models.Response'>":
        try:
            return JSON.json()
        except:
            return False

#Section: API Calls
def Single_Element_API_Call(Path_Addition, URL, Parameters, WebDriver):
    """Performs the SUSHI R5 API call with a URL that contains a single extra element between the base URL and the parameters.
    
    Arguments:
        Path_Addition {string} -- the last element of the URL path before the parameters, also what is being requested by the API call
        URL {string} -- the root URL for the SUSHI API
        Parameters {string} -- the parameters that need to be passed as part of the API call
        WebDriver {WebDriver} -- Selenium WebDriver object
    
    Returns:
        dictionary or list -- the data in JSON returned by API using Python data types
        string -- the root URL for the SUSHI API, a pipe, what was being requested, a pipe, and the reason for the failure
    """
    API_Call_URL = URL + Path_Addition
    time.sleep(0.1) # Some platforms return a 1020 error if SUSHI requests aren't spaced out; this provides spacing
    try: # Makes the initial API call
        API_Response = requests.get(API_Call_URL, params=Parameters, timeout=15)
        API_Response.raise_for_status()
        #Alert: MathSciNet doesn't have a status report, but does have the other reports with the needed data--how should this be handled so that it can pass through?
    except Timeout as error: # If the API request times out
        return f"{URL}|{Path_Addition}|{format(error)}"
    except HTTPError as error: # If the API request returns a 4XX HTTP code
        if format(error.response) == "<Response [403]>":
            # This response could be because of an actual issue, or because the API prompts a JSON file download rather than making the JSON data the page content; the function below handles the latter case
            API_Response = Retrieve_Downloaded_JSON_File(WebDriver, API_Call_URL + "?" + Parameters)
            if API_Response == []:
                return f"{URL}|{Path_Addition}|{format(error)}"
        else:
            return f"{URL}|{Path_Addition}|{format(error)}"
    except: # If there's some other problem with the API request
        return f"{URL}|{Path_Addition}|Some other error"

    if JSON_to_Python_Data_Types(API_Response):
        return JSON_to_Python_Data_Types(API_Response)
    else:
        return f"{URL}|{Path_Addition}|Return not JSON: {API_Response.text}"
