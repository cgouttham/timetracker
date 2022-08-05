import pandas as pd
from datetime import datetime

class Report:
    def __init__(self, filepath):
        self.intervals = []
        self.parse_report(filepath)

    def parse_report(self, filepath):
        df = pd.read_csv(filepath)
        for index, row in df.iterrows():
            self.intervals.append(Time_Entry(row["group"], row["type"], row["duration"], datetime.strptime(row['from'], '%d-%b-%Y %I:%M:%S %p'), datetime.strptime(row['to'], '%d-%b-%Y %I:%M:%S %p'), row["comment"]))

    def get_min_endtime(self):
        return min(self.intervals, key=lambda a : a.endtime).endtime

    def get_max_endtime(self):
        return max(self.intervals, key=lambda a : a.endtime).endtime
        
class Time_Entry:
    def __init__(self, group, task_type, duration, starttime, endtime, comment):
        self.group = group
        self.type = task_type
        self.duration = duration
        self.starttime = starttime
        self.endtime = endtime
        self.comment = comment