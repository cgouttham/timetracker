import csv
import json
import os
import requests
import psycopg2

from datetime import timedelta, datetime
from requests.auth import HTTPBasicAuth


class CredentialStore():
    def get_timeloggerapi_credentials():
        return json.load(open('assets/timeloggercredentials.json'))
    
    def get_timelogger_api_username():
        return CredentialStore.get_timeloggerapi_credentials()["username"]
    
    def get_timelogger_api_password():
        return CredentialStore.get_timeloggerapi_credentials()["password"]
 
    def get_postgres_password():
        return CredentialStore.get_timeloggerapi_credentials()["postgres_password"]



class DBConnectionClient():
    def get_sql_db_connection():
        return psycopg2.connect(
            host="time-tracker-db.cfvlptn5awxs.us-east-2.rds.amazonaws.com",
            database="postgres",
            user="cgouttham",
            password=CredentialStore.get_postgres_password())

class TypesTableCreator():
    def create():
        json_object = TypesTableCreator.get_types()

        conn = DBConnectionClient.get_sql_db_connection()
        cur = conn.cursor()

        TypesTableCreator.drop_and_recreate_types_table()

        for type_obj in json_object:
            type_name = type_obj['name']
            type_is_activity_group = type_obj['group']
            type_deleted = type_obj['deleted']
            type_guid = type_obj['guid']

            if (type_obj['parent']):
                type_parent = "'" + type_obj['parent'] + "'"
            else:
                type_parent = "null"

            sql = f"""INSERT INTO type(Name, IsActivityGroup, Deleted, Guid, ParentGuid)
                    VALUES('{type_name}', {type_is_activity_group}, {type_deleted}, '{type_guid}', {type_parent}) RETURNING guid;"""
            cur.execute(sql)
            # get the generated id back
            typeid = cur.fetchone()[0]
            print(typeid)
            # commit the changes to the database
            conn.commit()

    def get_types():
        url = "https://app.atimelogger.com/api/v2/types"
        response = requests.get(url, auth=HTTPBasicAuth(CredentialStore.get_timelogger_api_username(), CredentialStore.get_timelogger_api_password()))

        types = json.loads(response.content.decode())["types"]
        with open("json_data/types.json", "w") as outfile:
            json.dump(types, outfile, indent=4)

        return types

    def drop_and_recreate_types_table():
        conn = DBConnectionClient.get_sql_db_connection()
        cur = conn.cursor()
        cur.execute("".join(open('drop_and_create_types.sql').readlines()))
        conn.commit()

class IntervalsTableCreator():
    def get_intervals():
        url = "https://app.atimelogger.com/api/v2/intervals?limit=8000"
        response = requests.get(url, auth=HTTPBasicAuth(CredentialStore.get_timelogger_api_username(), CredentialStore.get_timelogger_api_password()))
        intervals = json.loads(response.content.decode())["intervals"]
        with open("json_data/intervals.json", "w") as outfile:
            json.dump(intervals, outfile, indent=4)

if __name__ == '__main__':
    TypesTableCreator.create()
