from datetime import datetime, timedelta, timezone

class EventClient:
	def get_google_calendar_events(service, calendar, min_endtime, max_endtime):
		# Add and subtract a minute because event filter below is exclusive filter.
		min_endtime = min_endtime - timedelta(minutes=1)
		max_endtime = max_endtime + timedelta(minutes=1)
		events_result = service.events().list(calendarId=calendar['id'],
											maxResults=250, singleEvents=True,
											timeMin= min_endtime.astimezone().isoformat(),
											timeMax= max_endtime.astimezone().isoformat(),
											orderBy='startTime').execute()

		events = events_result.get('items', [])

		if not events:
			print('No upcoming events found.')
			return []

		return events
		
	def create_event(service, tt_calendar, time_entry):
		start_time_in_utc = datetime.fromtimestamp(datetime.timestamp(time_entry.starttime), tz=timezone.utc)
		end_time_in_utc = datetime.fromtimestamp(datetime.timestamp(time_entry.endtime), tz=timezone.utc)

		if (end_time_in_utc < start_time_in_utc):
			print("Skipping corrupted event")
			return

		event = {
			'summary': time_entry.type,
			'description': f"Group: {time_entry.group} \nComment: {time_entry.comment}",
			'start': {
				'dateTime': start_time_in_utc.isoformat(),
				'timeZone': 'UTC',
			},
			'end': {
				'dateTime': end_time_in_utc.isoformat(),
				'timeZone': 'UTC',
			},
		}

		event = service.events().insert(calendarId=tt_calendar['id'], body=event).execute()
		print('Event created: %s' % (event.get('htmlLink')))