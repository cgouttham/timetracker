import os.path
from os import chdir, environ as env, makedirs
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from shutil import copyfile
import subprocess


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar']

def get_creds():
    tmp_dir = "/tmp"
    token_file = "token.json"
    original_token_path = 'assets/token.json'
    token_path = os.path.join(tmp_dir, token_file)

    try:
        creds = get_creds_logic(original_token_path, token_path, tmp_dir)
    except:
        remove_tmp_token_file(token_path)
        creds = get_creds_logic(original_token_path, token_path, tmp_dir) 

    return creds 

def get_creds_logic(original_token_path, token_path, tmp_dir):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if (os.path.exists(original_token_path) and not os.path.exists(token_path)):
        copy_creds_from_original_token_path(original_token_path, token_path, tmp_dir)

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'assets/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        try:
            with open(original_token_path, 'w') as original_token_path:
                original_token_path.write(creds.to_json())
        except:
            pass

    return creds

def copy_creds_from_original_token_path(original_token_path, token_path, tmp_dir):
    try:
        makedirs(tmp_dir)
        subprocess.run(["chmod", "775", str(tmp_dir)])
    except:
        pass
    copyfile(original_token_path, token_path)
    print("Created directory / copied file")

def remove_tmp_token_file(token_path):
    if os.path.exists(token_path):
        os.remove(token_path)
        print("Removed the file %s" % token_path)     
    else:
        print("Sorry, file %s does not exist." % token_path)