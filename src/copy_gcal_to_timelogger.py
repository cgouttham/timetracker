import json
from clients.TimeLoggerClient import TimeLoggerClient
from credential_manager import GoogleCredentialManager

from datetime import timedelta, datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from models.Time_Entry import Time_Entry
from copy_gcal_to_timelogger_impl import sync_report_events_to_google_calendar 
from clients.CalendarClient import CalendarClient
from clients.EventClient import EventClient

def gc_to_tl_sync_history_for_last_x_days(num_of_days):
    min_endtime =  datetime.now() - timedelta(days=num_of_days)
    max_endtime = datetime.now()
    sync_gc_entries_to_timelogger(min_endtime, max_endtime)

def sync_gc_entries_to_timelogger(from_endtime, to_endtime):
    try:
        creds = GoogleCredentialManager.get_creds()
        service = build('calendar', 'v3', credentials=creds)
        
        timetracker_intervals = TimeLoggerClient.get_time_entries_from_api(from_endtime, to_endtime)
        # tt_calendar = CalendarClient.get_or_create_calendar(service, 'aTimeLogger Writeback')
        main_calendar = CalendarClient.get_or_create_calendar(service, 'cgouttham@gmail.com')
        logger_calendar = CalendarClient.get_or_create_calendar(service, 'TimeTracker Calendar')
        gcal_intervals = EventClient.get_google_calendar_events(service, main_calendar, from_endtime, to_endtime)
        
        print("Num of Intervals in Time Range", "\nTime Tracker Intervals: ", len(timetracker_intervals), "\nGoogle Calendar Intervals", len(gcal_intervals)) 
        types_by_name = TimeLoggerClient.get_types_by_name()
        sync_report_events_to_google_calendar(service, main_calendar, logger_calendar, timetracker_intervals, gcal_intervals, types_by_name)

        return len(timetracker_intervals) 

    except HttpError as error:
        print('An error occurred: %s' % error)