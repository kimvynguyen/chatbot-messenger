from __future__ import print_function
from apiclient.discovery import build
from googleapiclient import discovery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "quickstart-1576060735118-cecb4a18398b.json"

#ham insert nhan vien vao sheet
def insert_employee(fb_name, FacebookID, name, SDT, email):
    credentials = None
    service = discovery.build('sheets', 'v4', credentials=credentials)
    # The ID of the spreadsheet to update.
    spreadsheet_id = '1Q9aYCh0QFbGBHrGQjty40UF_1-IPiikDhBfNftxqAGI'  # TODO: Update placeholder value.

    # The A1 notation of a range to search for a logical table of data.
    # Values will be appended after the last row of the table.
    range_ = 'TT_NhanVien!A2:D'  # TODO: Update placeholder value.

    # How the input data should be interpreted.
    value_input_option = 'USER_ENTERED'  # TODO: Update placeholder value.
    # How the input data should be inserted.
    insert_data_option = 'INSERT_ROWS'  # TODO: Update placeholder value.
    value_range_body = {
        "values":[[ fb_name, FacebookID,name,SDT,email]
                ]
        }
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()
