from __future__ import print_function
import csv
from datetime import timedelta
from datetime import datetime, timezone
import credential_manager
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.Report import Report, Time_Entry
from clients.CalendarClient import CalendarClient, EventClient
from google_calender_sync_helper import get_google_calendar_events, sync_report_events_to_google_calendar

def main():
    creds = credential_manager.get_creds()

    try:
        service = build('calendar', 'v3', credentials=creds)
        report = Report('report.csv');

        min_endtime = report.get_min_endtime()
        max_endtime = report.get_max_endtime()

        tt_calendar = CalendarClient.get_or_create_calendar(service, 'TimeTracker Calendar')
        gcal_intervals = get_google_calendar_events(service, tt_calendar, min_endtime, max_endtime)
        sync_report_events_to_google_calendar(service, tt_calendar, report.intervals, gcal_intervals)

    except HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
    main()
