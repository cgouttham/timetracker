from datetime import timedelta, datetime, timezone
import json
from urllib import request
import requests
from clients.EventClient import EventClient 
from common_helper import item_exists_in_report_interval_list, item_exists_in_report_interval_list_2, roundToNearestSec
import uuid
from requests.auth import HTTPBasicAuth

from credential_manager import TimeLoggerCredentialsManager


def sync_report_events_to_google_calendar(service, main_calendar, logger_calendar, report_intervals, gcal_intervals, types_by_name):
    add_intervals_from_gcal_that_dont_exist_in_report(service, main_calendar, logger_calendar, report_intervals, gcal_intervals, types_by_name)

def get_type(gcal_details, types_by_name):
    if "Morning Routine" in gcal_details:
        return types_by_name["Morning Routine"]["guid"]

    for type_name in types_by_name:
        if type_name in json.dumps(gcal_details):
            return types_by_name[type_name]["guid"] 

    return types_by_name["General"]["guid"]

def add_intervals_from_gcal_that_dont_exist_in_report(service, main_calendar, logger_calendar, report_intervals, gcal_intervals, types_by_name):
    for gcal_interval in gcal_intervals:
        # Skip all gcal items that are full day.
        if ("dateTime" not in gcal_interval["start"]):
            continue;

        if (item_exists_in_report_interval_list_2(report_intervals, gcal_interval)):
            continue
        else:
            activity_id = str(uuid.uuid4())
            interval_id = str(uuid.uuid4())


            gcal_details = {
                "title": gcal_interval["summary"] if "summary" in gcal_interval else None,
                "description": gcal_interval["description"] if "description" in gcal_interval else None
            }

            activity_type = get_type(gcal_details, types_by_name)

            start_time_gcal = roundToNearestSec(datetime.strptime(gcal_interval["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z"))
            start_time_gcal_utc = datetime.fromtimestamp(datetime.timestamp(start_time_gcal), tz=timezone.utc) 
            end_time_gcal = roundToNearestSec(datetime.strptime(gcal_interval["end"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z"))
            end_time_gcal_utc = datetime.fromtimestamp(datetime.timestamp(end_time_gcal), tz=timezone.utc)

            event = {
                "activities": [
                    {
                        "guid": activity_id,
                        "type":{
                            "guid": activity_type
                        },
                        "comment": json.dumps(gcal_details),
                        "state":"stopped",
                        "start": None,
                        "revision":0,
                        "intervals":[
                            {
                                "guid": interval_id,
                                "from":int(start_time_gcal_utc.timestamp()),
                                "to":int(end_time_gcal_utc.timestamp()),
                                "comment": None,
                                "activityGuid": None,
                                "type": None,
                                "userGuid": None,
                                "revision": None,
                                "userEmail": None,
                                "firstName": None,
                                "lastName": None,
                                "tags": None,
                                "deleted": False,
                                "fields":{
                                }
                            }
                        ],
                        "tags":[
                        ],
                        "typeGuid": activity_type,
                        "innerGuid": activity_id
                    }
                ],
                "revision": 0
            }

            try:
                url = "https://app.timetrack.io/api/v2/activities"
                headers = {"Content-Type": "application/json", "Host": "app.timetrack.io" }
                response = requests.post(
                        url, 
                        data = json.dumps(event), 
                        headers= headers,
                        auth=HTTPBasicAuth(
                                TimeLoggerCredentialsManager.get_creds()["username"], 
                                TimeLoggerCredentialsManager.get_creds()["password"]
                            )
                        )
                event = service.events().insert(calendarId=logger_calendar['id'], body=gcal_interval).execute()
                print('Event created: %s' % (event.get('htmlLink'))) 

                service.events().delete(calendarId=main_calendar['id'], eventId=gcal_interval["id"]).execute()
            except:
                print('Event failed to create')
