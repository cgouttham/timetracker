from __future__ import print_function
import csv
import datetime
import os.path
from requests.auth import HTTPBasicAuth
import requests
from typing import List
import json
from datetime import timedelta
from datetime import datetime, timezone


if __name__ == '__main__':
    url = "https://app.atimelogger.com/api/v2/types"
    response = requests.get(url, auth=HTTPBasicAuth('cgouttham@gmail.com', 'samplepassword'))
    types = json.loads(response.content.decode())["types"]
    object_dict = { x["guid"] : x for x in types }
    print(object_dict)