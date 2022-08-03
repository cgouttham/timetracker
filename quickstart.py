from __future__ import print_function
import csv
import pandas as pd
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar']

def main():
    creds = get_creds()

    try:
        service = build('calendar', 'v3', credentials=creds)
        tt_calendar = get_or_create_calendar(service, 'TimeTracker Calendar')
        write_events_from_report(service, tt_calendar)
        get_next_10_events(service, tt_calendar)

    except HttpError as error:
        print('An error occurred: %s' % error)

def write_events_from_report(service, tt_calendar):
    df = pd.read_csv("report.csv")
    print(df.head())
    for index, row in df.iterrows():
        create_event(service, tt_calendar, row)

def create_event(service, tt_calendar, row):
    from_datetime = datetime.datetime.strptime(row['from'], '%d-%b-%Y %I:%M:%S %p')
    to_datetime = datetime.datetime.strptime(row['to'], '%d-%b-%Y %I:%M:%S %p')

    event = {
      'summary': row['type'],
      'description': f"Group: {row['group']} \nComment: {row['comment']}",
      'start': {
        'dateTime': from_datetime.isoformat(),
        'timeZone': 'US/Eastern',
      },
      'end': {
        'dateTime': to_datetime.isoformat(),
        'timeZone': 'US/Eastern',
      },
    }

    event = service.events().insert(calendarId=tt_calendar['id'], body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def get_creds():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def get_or_create_calendar(service, name):
    tt_calendar = get_calendar(service, name)
    if (tt_calendar == None):
        return create_calendar(service, name)
    else:
        return tt_calendar

def get_calendar(service, name):
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            if (calendar_list_entry['summary'] == name):
                print("match!!!!!")
                return calendar_list_entry
            print(calendar_list_entry['summary'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    return None

def create_calendar(service, name):
    calendar = {
        'summary': name,
        'timeZone': 'America/Los_Angeles'
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar

def get_next_10_events(service, tt_calendar):
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    print(tt_calendar['id'])

    events_result = service.events().list(calendarId=tt_calendar['id'], timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return

    # Prints the start and name of the next 10 events
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

if __name__ == '__main__':
    main()
