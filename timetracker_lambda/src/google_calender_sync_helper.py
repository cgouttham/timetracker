from datetime import timedelta, datetime, timezone
import json
from clients.EventClient import EventClient

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
        return []

    return events

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

def item_exists_in_report_interval_list(report_intervals, gcal_interval):
    return any(is_gcalInterval_and_reportInterval_equal(report_interval, gcal_interval) for report_interval in report_intervals);

def item_exists_in_gcal_interval_list(report_interval, gcal_intervals):
    return any(is_gcalInterval_and_reportInterval_equal(report_interval, gcal_interval) for gcal_interval in gcal_intervals);

def is_gcalInterval_and_reportInterval_equal(report_interval, gcal_interval):
    if (f"Group: {report_interval.group}" not in gcal_interval["description"]):
        return False

    if (gcal_interval["summary"] != report_interval.type):
        return False

    start_time_in_time_entry_utc = roundToNearestSec(datetime.fromtimestamp(datetime.timestamp(report_interval.starttime), tz=timezone.utc))
    start_time_gcal = roundToNearestSec(datetime.strptime(gcal_interval["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z"))
    start_time_gcal_utc = datetime.fromtimestamp(datetime.timestamp(start_time_gcal), tz=timezone.utc)
    if (start_time_in_time_entry_utc != start_time_gcal_utc):
        return False

    end_time_in_time_entry_utc = roundToNearestSec(datetime.fromtimestamp(datetime.timestamp(report_interval.endtime), tz=timezone.utc))
    end_time_gcal = roundToNearestSec(datetime.strptime(gcal_interval["end"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z"))
    end_time_gcal_utc = datetime.fromtimestamp(datetime.timestamp(end_time_gcal), tz=timezone.utc)
    if (end_time_in_time_entry_utc != end_time_gcal_utc):
        return False

    if (f"Comment: {report_interval.comment}" not in gcal_interval["description"]):
        return False

    return True

def roundToNearestSec(datetimeVal):
    return datetimeVal - timedelta(microseconds=datetimeVal.microsecond)