from datetime import datetime, timedelta
from copy_gcal_to_timelogger import sync_gc_entries_to_timelogger
from copy_timelogger_to_gcal import tl_to_gc_sync_history_for_last_x_days

def main():
    from_endtime =  datetime.now() - timedelta(days=2)
    to_endtime = datetime.now() - timedelta(hours=3)
    sync_gc_entries_to_timelogger(from_endtime, to_endtime)

    tl_to_gc_sync_history_for_last_x_days(2)

def lambda_handler(event, context):
    main()

if __name__ == "__main__":
    main()

