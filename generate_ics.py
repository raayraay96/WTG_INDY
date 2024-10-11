import os
import re
import json
import markdown
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime

# Directory containing your Markdown event files
EVENTS_DIR = 'events'  # Adjust this path based on your repo structure

# Initialize a calendar
calendar = Calendar()
events_list = []

# Regular expressions to extract event details
date_regex = re.compile(r'Date:\s*(\d{4}-\d{2}-\d{2})')
time_regex = re.compile(r'Time:\s*([\d:APMapm\s]+)')
location_regex = re.compile(r'Location:\s*(.+)')
description_regex = re.compile(r'Description:\s*(.+)')
link_regex = re.compile(r'\[Event Link\]\((http[s]?://[^)]+)\)')

def extract_event_details(content):
    # Convert Markdown to HTML
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract text based on labels
    date_text = soup.find(text=re.compile(r'Date:')).strip()
    time_text = soup.find(text=re.compile(r'Time:')).strip()
    location_text = soup.find(text=re.compile(r'Location:')).strip()
    description_text = soup.find(text=re.compile(r'Description:')).strip()
    link_tag = soup.find('a', text='Event Link')
    
    date_match = date_regex.search(date_text)
    time_match = time_regex.search(time_text)
    location_match = location_regex.search(location_text)
    description_match = description_regex.search(description_text)
    link = link_tag['href'] if link_tag else ''
    
    event_date = date_match.group(1) if date_match else None
    event_time = time_match.group(1) if time_match else '00:00 AM'
    event_location = location_match.group(1) if location_match else 'N/A'
    event_description = description_match.group(1) if description_match else ''
    
    # Combine date and time
    event_datetime_str = f"{event_date} {event_time}"
    event_datetime = datetime.strptime(event_datetime_str, '%Y-%m-%d %I:%M %p')
    
    return {
        'name': soup.find('h3').get_text().strip(),
        'begin': event_datetime,
        'location': event_location,
        'description': event_description,
        'url': link
    }

# Iterate over all Markdown files in the EVENTS_DIR
for filename in os.listdir(EVENTS_DIR):
    if filename.endswith('.md'):
        filepath = os.path.join(EVENTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            # Split content by event delimiter (e.g., '---')
            events = content.split('---')
            for event_content in events:
                event_content = event_content.strip()
                if event_content:
                    try:
                        details = extract_event_details(event_content)
                        event = Event()
                        event.name = details['name']
                        event.begin = details['begin']
                        event.location = details['location']
                        event.description = f"{details['description']} \nMore info: {details['url']}"
                        calendar.events.add(event)
                        events_list.append({
                            "title": details['name'],
                            "date": details['begin'].date().isoformat(),
                            "time": details['begin'].time().strftime('%I:%M %p'),
                            "location": details['location'],
                            "description": details['description'],
                            "link": details['url'],
                            "category": 'General'  # Adjust category as needed
                        })
                    except Exception as e:
                        print(f"Error parsing event in {filename}: {e}")

# Write the calendar to an .ics file
os.makedirs('calendar', exist_ok=True)
with open('calendar/events_calendar.ics', 'w', encoding='utf-8') as ics_file:
    ics_file.writelines(calendar)

# Write the events.json for FullCalendar
with open('docs/events.json', 'w', encoding='utf-8') as json_file:
    json.dump(events_list, json_file, indent=2)
