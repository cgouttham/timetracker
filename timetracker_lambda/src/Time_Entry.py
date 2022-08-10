from datetime import datetime
        
class Time_Entry:
    def __init__(self, group, task_type, duration, starttime, endtime, comment):
        self.group = group
        self.type = task_type
        self.duration = duration
        self.starttime = starttime
        self.endtime = endtime
        self.comment = comment

    def to_string(self):
        print(f"type: {self.type}, \t comment: {self.comment} \t starttime: {self.starttime}")