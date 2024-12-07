from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import re

def parse_time_with_offset(date_str, time_str):
    """
    Parse time with timezone offset and convert to UTC
    
    :param date_str: Date in format DD.MM.YYYY
    :param time_str: Time in format HH:MM GMT+X
    :return: Datetime in UTC
    """
    # Parse date
    flight_date = datetime.strptime(date_str, "%d.%m.%Y")
    
    # Parse time and timezone
    time_match = re.search(r'(\d{2}:\d{2})\s*GMT([+-]\d+)', time_str)
    if not time_match:
        raise ValueError(f"Could not parse time from: {time_str}")
    
    time_part, gmt_part = time_match.groups()
    local_time = datetime.strptime(time_part.strip(), "%H:%M")
    
    # Combine date and time
    local_datetime = flight_date.replace(hour=local_time.hour, minute=local_time.minute)
    
    # Determine timezone
    offset_hours = int(gmt_part.strip())
    local_tz = pytz.FixedOffset(offset_hours * 60)
    local_datetime = local_tz.localize(local_datetime)
    
    # Convert to UTC
    return local_datetime.astimezone(pytz.UTC)

def create_flight_calendar_event(text_file_path):
    """
    Create an iCalendar event from flight details in a text file
    
    :param text_file_path: Path to the text file with flight details
    :return: iCalendar event
    """
    try:
        # Read file contents
        with open(text_file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Extract flight details
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        
        # First line: Flight name and date
        flight_info_match = re.match(r'(.*)\s+on\s+(\d{2}\.\d{2}\.\d{4})', lines[0])
        if not flight_info_match:
            raise ValueError("Could not parse flight name and date")
        
        flight_name = flight_info_match.group(1).strip()
        flight_date = flight_info_match.group(2).strip()
        
        # Find route line
        route_line = next((line for line in lines[1:] if ' to ' in line), None)
        if not route_line:
            raise ValueError("Could not find route line")
        
        route_match = re.match(r'(.*)\s+to\s+(.*)$', route_line)
        if not route_match:
            raise ValueError("Could not parse route")
        
        departure_city = route_match.group(1).strip()
        arrival_city = route_match.group(2).strip()
        
        # Find departure and arrival times
        departure_time_match = re.search(r'↗\s*(\d{2}:\d{2}\s*GMT[+-]\d+)', content)
        arrival_time_match = re.search(r'↘\s*(\d{2}:\d{2}\s*GMT[+-]\d+)', content)
        
        if not departure_time_match or not arrival_time_match:
            raise ValueError("Could not parse departure or arrival times")
        
        departure_time = departure_time_match.group(1).strip()
        arrival_time = arrival_time_match.group(1).strip()
        
        # Collect description
        description_lines = [line for line in lines if line not in [flight_name + " on " + flight_date, route_line, departure_time, arrival_time]]
        description = "\n".join(description_lines)

        # Convert times to UTC
        departure_time_utc = parse_time_with_offset(flight_date, departure_time)
        arrival_time_utc = parse_time_with_offset(flight_date, arrival_time)

        # Create iCal event
        cal = Calendar()
        event = Event()
        event.add('summary', f'Flight {flight_name}')
        event.add('description', description)
        event.add('dtstart', departure_time_utc)
        event.add('dtend', arrival_time_utc)
        event.add('location', f'{departure_city} to {arrival_city}')

        cal.add_component(event)

        # Save to .ics file
        ics_filename = f'flight_{flight_date.replace(".", "_")}.ics'
        with open(ics_filename, 'wb') as f:
            f.write(cal.to_ical())

        print(f"Calendar event created: {ics_filename}")
        return cal

    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return None

# Run the script
if __name__ == "__main__":
    create_flight_calendar_event("text.txt")