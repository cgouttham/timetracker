import csv
import json
import os
import requests
import psycopg2

from datetime import timedelta, datetime
from requests.auth import HTTPBasicAuth

def main():
    get_types()
    get_intervals()

def get_types():
    url = "https://app.atimelogger.com/api/v2/types"
    response = requests.get(url, auth=HTTPBasicAuth(get_timeloggerapi_credentials()["username"], get_timeloggerapi_credentials()["password"]))

    types = json.loads(response.content.decode())["types"]
    with open("json_data/types.json", "w") as outfile:
        json.dump(types, outfile, indent=4)

def get_intervals():
    url = "https://app.atimelogger.com/api/v2/intervals?limit=8000"
    response = requests.get(url, auth=HTTPBasicAuth(get_timeloggerapi_credentials()["username"], get_timeloggerapi_credentials()["password"]))
    intervals = json.loads(response.content.decode())["intervals"]
    with open("json_data/intervals.json", "w") as outfile:
        json.dump(intervals, outfile, indent=4)

def get_timeloggerapi_credentials():
    return json.load(open('assets/timeloggercredentials.json'))

def add_ids_to_types():
    d = {}
    json_object  = json.load(open('json_data/types.json'))
    for i in range(len(json_object)):
        json_object[i]['id'] = i + 1
        d[json_object[i]["guid"]] = json_object[i]


    json_object = add_foreign_ids_to_types(json_object)

    with open("json_data/types_output.json", "w") as outfile:
        json.dump(json_object, outfile, indent=4)

def convert_to_sql_readable_json():
    input_json = json.load(open('json_data/types_output.json'))
    output_json = {}
    output_json['Types'] = []
    for json_item in input_json:
        output_json['Types'].append({ 'Type': json_item })

    with open("json_data/types_output_for_sql.json", "w") as outfile:
        json.dump(output_json, outfile, indent=4)

    return output_json


def add_foreign_ids_to_types(json_object):
    d = {}
    for json_item in json_object:
        d[json_item['guid']] = json_item['id']


    for json_item in json_object:
        if (json_item['parent'] != None):
            json_item['parent_id'] = d[json_item['parent']]
            json_item['parent_guid'] = d[json_item['parent']]
        else:
            json_item['parent_id'] = None

    return json_object

def write_to_sql_table(json_object):
    conn = psycopg2.connect(
        host="time-tracker-db.cfvlptn5awxs.us-east-2.rds.amazonaws.com",
        database="postgres",
        user="cgouttham",
        password=get_timeloggerapi_credentials()["postgres_password"])

    cur = conn.cursor()

    for json_item in json_object["Types"]:
        type_obj = json_item["Type"]

        type_id = type_obj['id']
        type_parent_id = type_obj['parent_id'] or 'null'
        type_name = type_obj['name']
        type_is_activity_group = type_obj['group']
        type_deleted = type_obj['deleted']
        type_guid = type_obj['guid']

        sql = f"""INSERT INTO type(Id, ParentId, Name, IsActivityGroup, Deleted, Guid, ParentGuid)
                VALUES({type_id}, {type_parent_id}, '{type_name}', {type_is_activity_group}, {type_deleted}, '{type_guid}', '{type_parent}') RETURNING id;"""
        cur.execute(sql)
        # get the generated id back
        typeid = cur.fetchone()[0]
        print(typeid)
        # commit the changes to the database
        conn.commit()

if __name__ == '__main__':
    json_output = convert_to_sql_readable_json()
    write_to_sql_table(json_output)

