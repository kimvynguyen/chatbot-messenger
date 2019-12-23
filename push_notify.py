from __future__ import print_function
import pickle
import os.path
#from table import EmployeeData
from sqlalchemy import create_engine
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.oauth2.credentials
import google_auth_oauthlib.flow
import string
from app import *

def push_notification(recipient_id, message_text):
    params = {
        "access_token": "EAAFvTbGl9ccBAPzRAtItBSsIo7YCgeg5M5IXzrBZBas3lw8tWXbum6AWsNI9lkmzBoQhd2F9Jz5iAC7NDYcdZCWqlShqBeBf1ssvD5ORw8wzMxrMeG1ZB21ZARvnNoZCUEZBmoGceA3zoLI7RSyaMC0uzne0Nt3tAHEbVhsGxuz0aoZAaZBBqJqrIiLuZCP0F56sZD"
    } 
    headers = {
        "Content-Type": "application/json",
        "charset": "utf-8"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": { 
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v4.0/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

engine = create_engine('sqlite:///SaveData.db')
conn = engine.connect()

flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    ['https://www.googleapis.com/auth/youtube.force-ssl'])

# Indicate where the API server will redirect the user after the user completes
# the authorization flow. The redirect URI is required. The value must exactly
# match one of the authorized redirect URIs for the OAuth 2.0 client, which you
# configured in the API Console. If this value doesn't match an authorized URI,
# you will get a 'redirect_uri_mismatch' error.
flow.redirect_uri = 'https://www.example.com/oauth2callback'
authorization_url, state = flow.authorization_url(
    access_type='offline', include_granted_scopes='true')
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1Q9aYCh0QFbGBHrGQjty40UF_1-IPiikDhBfNftxqAGI'

def get_employee():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    SAMPLE_RANGE_NAME = 'TT_NhanVien!A2:E'
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    if values:
        res = values[0]
        push_notification(res[1],'Co khach hang de lai thong tin tu van. Vui long truy cap he thong')

get_employee()