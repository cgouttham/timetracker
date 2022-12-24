from datetime import datetime, timezone
import json
from credential_manager import TimeLoggerCredentialsManager
import requests
from requests.auth import HTTPBasicAuth
from models.Time_Entry import Time_Entry

class TimeLoggerClient:
    def check_if_interval_exists_in_timelogger():
        print("Not Implemented")

    def create_event_and_interval():
        print("Not implemented")

    def get_types():
        url = "https://app.atimelogger.com/api/v2/types"
        response = requests.get(url, auth=HTTPBasicAuth(TimeLoggerCredentialsManager.get_creds()["username"], TimeLoggerCredentialsManager.get_creds()["password"]))
        types = json.loads(response.content.decode())["types"]
        types_dict = { x["guid"] : x for x in types }
        return types_dict

    def get_types_by_name():
        url = "https://app.atimelogger.com/api/v2/types"
        response = requests.get(url, auth=HTTPBasicAuth(TimeLoggerCredentialsManager.get_creds()["username"], TimeLoggerCredentialsManager.get_creds()["password"]))
        types = json.loads(response.content.decode())["types"]
        types_dict = { x["name"] : x for x in types if x["group"] == False }
        return types_dict

    def get_time_entries_from_api(min_endtime, max_endtime):
        types_by_guid = TimeLoggerClient.get_types()
        intervals = TimeLoggerClient.get_intervals(min_endtime, max_endtime)
        time_entries = []
        for interval in intervals:
            task_type = types_by_guid[interval["type"]["guid"]]
            task_type_name = task_type["name"]
            group_type_name = types_by_guid[task_type["parent"]]["name"] if task_type["parent"] != None else ""

            time_entries.append(Time_Entry(group_type_name, task_type_name, "mock_duration", datetime.fromtimestamp(interval["from"]), datetime.fromtimestamp(interval["to"]), interval["comment"]))

        return time_entries

    def get_intervals(min_endtime, max_endtime):
        min_endtime_epoch = min_endtime.strftime('%s')
        max_endtime_epoch = max_endtime.strftime('%s')
        url = f"https://app.atimelogger.com/api/v2/intervals?from={min_endtime_epoch}&to={max_endtime_epoch}&limit=500"
        response = requests.get(url, auth=HTTPBasicAuth(TimeLoggerCredentialsManager.get_creds()["username"], TimeLoggerCredentialsManager.get_creds()["password"]))
        return json.loads(response.content.decode())["intervals"] or []
