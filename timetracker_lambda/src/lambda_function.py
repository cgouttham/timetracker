import json
from sync_gcal_from_timetracker_api import main, sync_history_for_last_x_days

def lambda_handler(event, context):
    sync_history_for_last_x_days(10)
