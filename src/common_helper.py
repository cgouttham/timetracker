from datetime import timedelta, datetime, timezone

def item_exists_in_report_interval_list(report_intervals, gcal_interval):
    return any(is_gcalInterval_and_reportInterval_equal(report_interval, gcal_interval) for report_interval in report_intervals);

def item_exists_in_gcal_interval_list(report_interval, gcal_intervals):
    return any(is_gcalInterval_and_reportInterval_equal(report_interval, gcal_interval) for gcal_interval in gcal_intervals);

def item_exists_in_report_interval_list_2(report_intervals, gcal_interval):
    return any(is_gcalInterval_and_reportInterval_equal(report_interval, gcal_interval) for report_interval in report_intervals);

def is_gcalInterval_and_reportInterval_equal(report_interval, gcal_interval):
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

    equal_when_source_is_timelogger_entry = __is_equal_when_source_is_timelogger_entry(report_interval, gcal_interval)
    equal_when_source_is_gcal_entry = __is_equal_when_source_is_gcal_entry(report_interval, gcal_interval)

    return equal_when_source_is_timelogger_entry or equal_when_source_is_gcal_entry

def __is_equal_when_source_is_timelogger_entry(report_interval, gcal_interval):
    if (gcal_interval["summary"] != report_interval.type):
        return False

    if (f"Group: {report_interval.group}" not in gcal_interval["description"]):
        return False

    if (f"Comment: {report_interval.comment}" not in gcal_interval["description"]):
        return False
    
    return True 

def __is_equal_when_source_is_gcal_entry(report_interval, gcal_interval):
    return gcal_interval["summary"] in report_interval.comment

def roundToNearestSec(datetimeVal):
    return datetimeVal - timedelta(microseconds=datetimeVal.microsecond)