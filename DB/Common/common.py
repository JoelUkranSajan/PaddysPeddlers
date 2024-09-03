import json
from datetime import datetime

"""
This function is used to log errors encountered during the execution of functions defined in this module. 
Args:
    error_log_filename (str): Parameter for name of error file for the specified function.
    error_message (str): Error message to be logged in the error_log.txt file.
Returns:
    The function does not return anything.
"""
def log_error(error_log_filename, error_message):
    timestamp = datetime.now()
    try:
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"File:{error_log_filename}:{timestamp} \nError: {error_message}\n")
    except:
        print("Error occured during logging of error.\n")
        


"""
The function opens the "results.json" file and reads the stations static data into the "jc_data" 
    (short for "JCDeveaux Data") variable. The json module "json.loads()" method is called with "jc_data" as 
    the argument and creates a list of dictionaries named "jc_data_list" (short for "JCDeveaux Data List").
    Args:
        json_file (json file): JSON file containing data scraped from JCDeveaux.
    Returns:
        List of dictionaries containinf the JSON data.
"""
def json_to_list(file_name):
    try:
        with open(file_name, 'r') as file:
            jc_data = file.read()

        jc_data_list = json.loads(jc_data)
        return jc_data_list
    
    except FileNotFoundError as e:
        log_error("error_log.txt", f"json_to_list() function error - FNF: {e}")
        return None
    except IOError as e:
        log_error("error_log.txt", f"json_to_list() function error - IO: {e}")
        return None
    except PermissionError as e:
        log_error("error_log.txt", f"json_to_list() function error - Permissions: {e}")
        return None
    except json.JSONDecodeError as e:
        log_error("error_log.txt", f"json_to_list() function error - JSON Decode: {e}")
        return None