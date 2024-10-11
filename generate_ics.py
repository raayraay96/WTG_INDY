import os
import json
from ics import Calendar, Event
from datetime import datetime

EVENTS_JSON = 'events.json'
ICS_OUTPUT = 'calendar/events_calendar.ics'

# Ensure the 'calendar' directory exists
os.makedirs('calendar', exist_ok=True)

# Initialize a calendar
calendar = Calendar()
events_list = []

# Load events from JSON
with open(EVENTS_JSON, 'r', encoding='utf-8') as f:
    events = json.load(f)

for event in events:
    e = Event()
    e.name = event['title']
    e.begin = f"{event['date']} {event['time']}"
    e.location = event.get('location', 'N/A')
    e.description = f"{event.get('description', '')} \nMore info: {event.get('link', '')}"
    calendar.events.add(e)
    events_list.append({
        "title": event['title'],
        "date": event['date'],
        "time": event['time'],
        "location": event.get('location', 'N/A'),
        "description": event.get('description', ''),
        "link": event.get('link', ''),
        "category": event.get('category', 'General')  # Ensure category is present
    })

# Write the calendar to an .ics file
with open(ICS_OUTPUT, 'w', encoding='utf-8') as ics_file:
    ics_file.writelines(calendar)

# Optionally, write the events.json for FullCalendar
with open('docs/events.json', 'w', encoding='utf-8') as json_file:
    json.dump(events_list, json_file, indent=2)
