from __future__ import print_function
import csv
import pandas as pd
from datetime import timedelta
from datetime import datetime, timezone
import credential_manager
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.Report import Report, Time_Entry
from clients.CalendarClient import CalendarClient, EventClient

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

def get_google_calendar_events(service, calendar, min_endtime, max_endtime):
    # Add and subtract a minute because event filter below is exclusive filter.
    min_endtime = min_endtime - timedelta(minutes=1)
    max_endtime = max_endtime + timedelta(minutes=1)
    events_result = service.events().list(calendarId=calendar['id'],
                                          maxResults=250, singleEvents=True,
                                          timeMin= min_endtime.astimezone().isoformat(),
                                          timeMax= max_endtime.astimezone().isoformat(),
                                          orderBy='startTime').execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return

    return events

def sync_report_events_to_google_calendar(service, calendar, report_intervals, gcal_intervals):
    remove_intervals_from_gcal_that_dont_exist_in_report(service, calendar, report_intervals, gcal_intervals)
    add_intervals_in_report_that_dont_exist_in_gcal(service, calendar, report_intervals, gcal_intervals)

def remove_intervals_from_gcal_that_dont_exist_in_report(service, calendar, report_intervals, gcal_intervals):
    for gcal_interval in gcal_intervals:
        if (item_exists_in_report_interval_list(report_intervals, gcal_interval)):
            continue
        else:
            service.events().delete(calendarId=calendar['id'], eventId=gcal_interval['id']).execute()
            print('Event deleted: %s' % (gcal_interval.get('htmlLink')))

def add_intervals_in_report_that_dont_exist_in_gcal(service, calendar, report_intervals, gcal_intervals):
    for report_interval in report_intervals:
        if (item_exists_in_gcal_interval_list(report_interval, gcal_intervals)):
            continue
        else:
            EventClient.create_event(service, calendar, report_interval)

def item_exists_in_report_interval_list(report_intervals, gcal_interval):
    return any(is_gcalInterval_and_reportInterval_equal(report_interval, gcal_interval) for report_interval in report_intervals);

def item_exists_in_gcal_interval_list(report_interval, gcal_intervals): 
    return any(is_gcalInterval_and_reportInterval_equal(report_interval, gcal_interval) for gcal_interval in gcal_intervals);

def is_gcalInterval_and_reportInterval_equal(report_interval, gcal_interval):
    if (f"Group: {report_interval.group}" not in gcal_interval["description"]):
        return False

    if (not gcal_interval["summary"] == report_interval.type):
        return False

    if (not roundToNearestSec(datetime.strptime(gcal_interval["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z").utcnow()) == roundToNearestSec(report_interval.starttime.utcnow())):
        return False

    if (not roundToNearestSec(datetime.strptime(gcal_interval["end"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z").utcnow()) == roundToNearestSec(report_interval.endtime.utcnow())):
        return False

    if (f"Comment: {report_interval.comment}" not in gcal_interval["description"]):
        return False

    return True

def roundToNearestSec(datetimeVal):
    return datetimeVal - timedelta(microseconds=datetimeVal.microsecond)

if __name__ == '__main__':
    main()
