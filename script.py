from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import re

def parse_time_with_offset(date_str, departure_time_str, arrival_time_str):
    """
    Parse departure and arrival times with timezone offset and convert to UTC
    
    :param date_str: Date in format DD.MM.YYYY
    :param departure_time_str: Departure time in format HH:MM GMT+X
    :param arrival_time_str: Arrival time in format HH:MM GMT+X
    :return: Tuple of departure and arrival times in UTC
    """
    # Parse date
    flight_date = datetime.strptime(date_str, "%d.%m.%Y")
    
    # Parse departure time and timezone
    departure_match = re.search(r'(\d{2}:\d{2})\s*GMT([+-]\d+)', departure_time_str)
    arrival_match = re.search(r'(\d{2}:\d{2})\s*GMT([+-]\d+)', arrival_time_str)
    
    if not departure_match or not arrival_match:
        raise ValueError(f"Could not parse times from: {departure_time_str}, {arrival_time_str}")
    
    departure_time_part, departure_gmt_part = departure_match.groups()
    arrival_time_part, arrival_gmt_part = arrival_match.groups()
    
    departure_local_time = datetime.strptime(departure_time_part.strip(), "%H:%M")
    arrival_local_time = datetime.strptime(arrival_time_part.strip(), "%H:%M")
    
    # Determine timezones
    departure_offset_hours = int(departure_gmt_part.strip())
    arrival_offset_hours = int(arrival_gmt_part.strip())
    
    # Combine date and times
    departure_local_datetime = flight_date.replace(
        hour=departure_local_time.hour, 
        minute=departure_local_time.minute
    )
    
    # Adjust arrival date if needed
    arrival_date = flight_date
    if arrival_local_time.hour < departure_local_time.hour:
        arrival_date += timedelta(days=1)
    
    arrival_local_datetime = arrival_date.replace(
        hour=arrival_local_time.hour, 
        minute=arrival_local_time.minute
    )
    
    # Create timezone-aware datetime
    departure_local_tz = pytz.FixedOffset(departure_offset_hours * 60)
    arrival_local_tz = pytz.FixedOffset(arrival_offset_hours * 60)
    
    departure_local_datetime = departure_local_tz.localize(departure_local_datetime)
    arrival_local_datetime = arrival_local_tz.localize(arrival_local_datetime)
    
    # Convert to UTC
    departure_time_utc = departure_local_datetime.astimezone(pytz.UTC)
    arrival_time_utc = arrival_local_datetime.astimezone(pytz.UTC)
    
    return departure_time_utc, arrival_time_utc
    """
    Parse time with timezone offset and convert to UTC, handling cross-midnight flights
    
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
    
    # Adjust date if time crosses midnight
    if local_time.hour < 12:  # Assume cross-midnight if time is before noon
        flight_date += timedelta(days=1)
    
    # Combine date and time
    local_datetime = flight_date.replace(hour=local_time.hour, minute=local_time.minute)
    
    # Determine timezone
    offset_hours = int(gmt_part.strip())
    local_tz = pytz.FixedOffset(offset_hours * 60)
    local_datetime = local_tz.localize(local_datetime)
    
    # Convert to UTC
    return local_datetime.astimezone(pytz.UTC)
    
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
        departure_time_utc, arrival_time_utc = parse_time_with_offset(
    flight_date, 
    departure_time, 
    arrival_time
)

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