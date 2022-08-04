from __future__ import print_function
import csv
import pandas as pd
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def main():
    sample_items = []
    sample_items.append(SampleItem(1, 2))
    sample_items.append(SampleItem(2, -9))
    sample_items.append(SampleItem(-1, 9))
    print(min(sample_items, key=lambda a : a.p1))

class SampleItem():
    def __init__(self, p1, p2):
        self.p1 = p1;
        self.p2 = p2;


if __name__ == '__main__':
    main()