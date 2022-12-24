from datetime import timedelta, datetime, timezone
import json
from clients.EventClient import EventClient
from common_helper import item_exists_in_gcal_interval_list, item_exists_in_report_interval_list

def sync_report_events_to_google_calendar(service, calendar, report_intervals, gcal_intervals):
    remove_intervals_from_gcal_that_dont_exist_in_report(service, calendar, report_intervals, gcal_intervals)
    add_intervals_from_report_that_dont_exist_in_gcal(service, calendar, report_intervals, gcal_intervals)

def remove_intervals_from_gcal_that_dont_exist_in_report(service, calendar, report_intervals, gcal_intervals):
    for gcal_interval in gcal_intervals:
        if (item_exists_in_report_interval_list(report_intervals, gcal_interval)):
            continue
        else:
            service.events().delete(calendarId=calendar['id'], eventId=gcal_interval['id']).execute()
            print('Event deleted: %s' % (gcal_interval.get('htmlLink')))

def add_intervals_from_report_that_dont_exist_in_gcal(service, calendar, report_intervals, gcal_intervals):
    for report_interval in report_intervals:
        if (item_exists_in_gcal_interval_list(report_interval, gcal_intervals)):
            continue
        else:
            EventClient.create_event(service, calendar, report_interval)

