import json
from copy_gcal_to_timelogger import gc_to_tl_sync_history_for_last_x_days
from copy_timelogger_to_gcal import tl_to_gc_sync_history_for_last_x_days

def lambda_handler(event, context):
    gc_to_tl_sync_history_for_last_x_days(2)
    tl_to_gc_sync_history_for_last_x_days(2)

