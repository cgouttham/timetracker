from datetime import datetime, timezone

class CalendarClient:
	def get_or_create_calendar(service, name):
		tt_calendar = CalendarClient.get_calendar(service, name)
		if (tt_calendar == None):
			return CalendarClient.create_calendar(service, name)
		else:
			return tt_calendar

	def get_calendar(service, name):
		page_token = None
		while True:
			calendar_list = service.calendarList().list(pageToken=page_token).execute()
			for calendar_list_entry in calendar_list['items']:
				if (calendar_list_entry['summary'] == name):
					return calendar_list_entry
			page_token = calendar_list.get('nextPageToken')
			if not page_token:
				break

		return None

	def create_calendar(service, name):
		calendar = {
			'summary': name,
			'timeZone': 'US/Eastern'
		}

		created_calendar = service.calendars().insert(body=calendar).execute()
		return created_calendar

