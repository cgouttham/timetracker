from datetime import datetime, timezone

class EventClient:
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