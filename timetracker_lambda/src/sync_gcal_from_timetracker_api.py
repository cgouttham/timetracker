import json
from clients.TimeLoggerClient import TimeLoggerClient
from credential_manager import GoogleCredentialManager

from datetime import timedelta, datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from models.Time_Entry import Time_Entry
from google_calender_sync_helper import get_google_calendar_events, sync_report_events_to_google_calendar
from clients.CalendarClient import CalendarClient
from clients.EventClient import EventClient 

def sync_history_for_last_x_days(num_of_days):
    min_endtime =  datetime.now() - timedelta(days=num_of_days)
    max_endtime = datetime.now()
    sync_timelogger_entries_to_gc(min_endtime, max_endtime)

def sync_timelogger_entries_to_gc(from_endtime, to_endtime):
    try:
        creds = GoogleCredentialManager.get_creds()
        service = build('calendar', 'v3', credentials=creds)
        print("Syncing Reports in time-range {} - {}".format(from_endtime, to_endtime))
        
        timetracker_intervals = TimeLoggerClient.get_time_entries_from_api(from_endtime, to_endtime)
        tt_calendar = CalendarClient.get_or_create_calendar(service, 'TimeTracker Calendar')
        gcal_intervals = get_google_calendar_events(service, tt_calendar, from_endtime, to_endtime)
        
        print("Num of Intervals in Time Range", "\nTime Tracker Intervals: ", len(timetracker_intervals), "\nGoogle Calendar Intervals", len(gcal_intervals)) 
        sync_report_events_to_google_calendar(service, tt_calendar, timetracker_intervals, gcal_intervals)

        return len(timetracker_intervals) 

    except HttpError as error:
        print('An error occurred: %s' % error)

def sync_all_of_history():
    i = 0
    more_items_to_sync = True
    while (more_items_to_sync):
        min_endtime =  datetime.now() - timedelta(days=(i + 10))
        max_endtime = datetime.now() - timedelta(days=i)
        num_items_synced = sync_timelogger_entries_to_gc(min_endtime, max_endtime)
        more_items_to_sync = num_items_synced > 0
        i += 10
    print("completed");

if __name__ == '__main__':
    sync_history_for_last_x_days(10)
