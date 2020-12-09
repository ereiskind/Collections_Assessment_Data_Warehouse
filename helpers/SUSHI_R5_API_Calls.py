# This serves as the library for the API calls and the ensuing status checks

#Section: API Calls
def Status(URL, Parameters):
    """Performs the SUSHI R5 API call to check for SUSHI server status and performs error checking on the response to ensure that it's valid.
    Arguments:
        URL {string} -- the root URL for the SUSHI API
        Parameters {string} -- the parameters that need to be passed as part of the API call
    
    
    Returns:
        dictionary or list -- the data in JSON using Python data types
        string -- the root URL for the SUSHI API, a pipe, and the reason for the failure
    """
    Status_URL = URL + "status"
    try: # Makes the initial API call
        Status_Check = requests.get(Status_URL, params=Parameters, timeout=10)
        Status_Check.raise_for_status()
    #Alert: MathSciNet doesn't have a status report, but does have the other reports with the needed data--how should this be handled so that it can pass through?
    except Timeout as error: # If the API request times out
        print(f"Server didn't respond after 10 seconds ({format(error)}).")
        return "URL"+"|Status Check Timeout"
    except HTTPError as error: # If the API request returns a 4XX HTTP code
        if format(error.response) == "<Response [403]>": # Handles the JSON file downloads 
            Status_Check = Retrieve_Downloaded_JSON_File(Chrome_Browser_Driver, Status_URL + "?" + Credentials_String)
        else:
            print(f"HTTP Error: {format(error)}")
            return "URL"+"|HTTP Error"
    except: # If there's some other problem with the API request
        print(f"Some error other than a status error or timout occurred when trying to access {Status_URL}.")
        return "URL"+"|Something Else")    

    Status_Check = JSON_to_Python_Data_Types(Status_Check)