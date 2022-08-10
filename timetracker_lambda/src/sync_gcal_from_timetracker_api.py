import csv
import json
import os
import requests
import credential_manager

from datetime import timedelta, datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from requests.auth import HTTPBasicAuth

from Time_Entry import Time_Entry
from google_calender_sync_helper import get_google_calendar_events, sync_report_events_to_google_calendar
from clients.CalendarClient import CalendarClient, EventClient

def main():
    try:
        print("start")
        creds = credential_manager.get_creds()
        service = build('calendar', 'v3', credentials=creds)
        min_endtime =  datetime.now() - timedelta(days=20)
        max_endtime = datetime.now()
        timetracker_intervals = get_time_entries_from_api(min_endtime, max_endtime)
        print(len(timetracker_intervals))

        tt_calendar = CalendarClient.get_or_create_calendar(service, 'TimeTracker Calendar')
        gcal_intervals = get_google_calendar_events(service, tt_calendar, min_endtime, max_endtime)
        print(len(gcal_intervals))
        sync_report_events_to_google_calendar(service, tt_calendar, timetracker_intervals, gcal_intervals)

    except HttpError as error:
        print('An error occurred: %s' % error)

def remove_tmp_folder():
    if os.path.exists(tmp_file_path):
        os.remove(tmp_file_path)
        print("Removed the file %s" % tmp_file_path)     
    else:
        print("Sorry, file %s does not exist." % tmp_file_path)

def get_time_entries_from_api(min_endtime, max_endtime):
    types_by_guid = get_types()
    intervals = get_intervals(min_endtime, max_endtime)
    time_entries = []
    for interval in intervals:
        task_type = types_by_guid[interval["type"]["guid"]]
        task_type_name = task_type["name"]
        group_type_name = types_by_guid[task_type["parent"]]["name"] if task_type["parent"] != None else ""

        time_entries.append(Time_Entry(group_type_name, task_type_name, "mock_duration", datetime.fromtimestamp(interval["from"]), datetime.fromtimestamp(interval["to"]), interval["comment"]))

    return time_entries

def get_types():
    url = "https://app.atimelogger.com/api/v2/types"

    response = requests.get(url, auth=HTTPBasicAuth(get_timeloggerapi_credentials()["username"], get_timeloggerapi_credentials()["password"]))
    types = json.loads(response.content.decode())["types"]
    types_dict = { x["guid"] : x for x in types }
    return types_dict


def get_intervals(min_endtime, max_endtime):
    min_endtime_epoch = min_endtime.strftime('%s')
    max_endtime_epoch = max_endtime.strftime('%s')
    url = f"https://app.atimelogger.com/api/v2/intervals?from={min_endtime_epoch}&to={max_endtime_epoch}&limit=250"
    response = requests.get(url, auth=HTTPBasicAuth(get_timeloggerapi_credentials()["username"], get_timeloggerapi_credentials()["password"]))
    return json.loads(response.content.decode())["intervals"] or []

def get_timeloggerapi_credentials():
    return json.load(open('assets/timeloggercredentials.json'))

if __name__ == '__main__':
    main()
