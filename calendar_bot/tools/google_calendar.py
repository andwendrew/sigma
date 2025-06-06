from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import json
from datetime import datetime, timedelta
import time
import tzlocal
from typing import Dict, Any, Optional, List, Union

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Get an authorized Google Calendar API service instance."""
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_info(
            json.loads(open('calendar_bot/token.json').read()), SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'calendar_bot/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def parse_datetime(date_str: str, time_str: str) -> datetime:
    """Parse date and time strings into a datetime object."""
    # Try different date formats
    date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y', '%d %B %Y']
    time_formats = ['%H:%M', '%I:%M %p', '%I:%M%p']
    
    date_obj = None
    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue
    
    if not date_obj:
        raise ValueError(f"Could not parse date: {date_str}")
    
    time_obj = None
    for fmt in time_formats:
        try:
            time_obj = datetime.strptime(time_str, fmt)
            break
        except ValueError:
            continue
    
    if not time_obj:
        raise ValueError(f"Could not parse time: {time_str}")
    
    # Combine date and time
    return datetime.combine(date_obj.date(), time_obj.time())

def get_system_timezone() -> str:
    """Get the system's local timezone."""
    local_timezone = tzlocal.get_localzone()
    return str(local_timezone)

def create_calendar(calendar_name: str, description: Optional[str] = None, timezone: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new calendar.
    
    Args:
        calendar_name: Name of the calendar
        description: Optional description of the calendar
        timezone: Optional timezone (defaults to system timezone)
    
    Returns:
        Dict containing the created calendar details
    """
    try:
        service = get_calendar_service()
        
        if timezone is None:
            timezone = get_system_timezone()
            
        calendar = {
            'summary': calendar_name,
            'timeZone': timezone
        }
        
        if description:
            calendar['description'] = description
            
        created_calendar = service.calendars().insert(body=calendar).execute()
        
        return {
            'status': 'success',
            'calendar_id': created_calendar['id'],
            'summary': created_calendar['summary'],
            'timezone': created_calendar['timeZone'],
            'description': created_calendar.get('description', '')
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def list_calendars(active_only: bool = True, cleaned: bool = False) -> Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """
    List calendars the user has access to.
    
    Args:
        active_only: If True, only return calendars that are currently selected/visible.
                    If False, return all calendars regardless of visibility.
        cleaned: If True, return a dictionary mapping calendar IDs to their details.
                If False, return a list of full calendar details.
    
    Returns:
        If cleaned=True: Dictionary mapping calendar IDs to their details
        If cleaned=False: List of dictionaries containing full calendar details
    """
    try:
        service = get_calendar_service()
        calendar_list = service.calendarList().list().execute()
        
        if cleaned:
            # Return dictionary mapping IDs to calendar details
            calendars = {}
            for calendar in calendar_list['items']:
                if not active_only or calendar.get('selected', False):
                    calendars[calendar['id']] = {
                        'title': calendar['summary'],
                        'description': calendar.get('description', 'No description'),
                        'timezone': calendar.get('timeZone', 'Not specified'),
                        'is_primary': calendar.get('primary', False)
                    }
            return calendars
        else:
            # Return list of full calendar details
            calendars = []
            for calendar in calendar_list['items']:
                if not active_only or calendar.get('selected', False):
                    calendars.append({
                        'id': calendar['id'],
                        'summary': calendar['summary'],
                        'description': calendar.get('description', ''),
                        'timezone': calendar.get('timeZone', ''),
                        'primary': calendar.get('primary', False),
                        'selected': calendar.get('selected', False),
                        'access_role': calendar.get('accessRole', '')
                    })
            return calendars
        
    except Exception as e:
        if cleaned:
            return {'error': {'error': str(e)}}
        else:
            return [{
                'status': 'error',
                'error': str(e)
            }]

def create_calendar_event(
    title: str,
    date: str,
    time: str,
    duration_minutes: int = 60,
    notification_minutes: int = 10,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[list] = None,
    calendar_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a Google Calendar event.
    
    Args:
        title: Event title
        date: Event date (various formats supported)
        time: Event time (various formats supported)
        duration_minutes: Event duration in minutes (default: 60)
        notification_minutes: Minutes before event to send notification (default: 10)
        description: Optional event description
        location: Optional event location
        attendees: Optional list of attendee email addresses
        calendar_id: Optional calendar ID (defaults to primary calendar)
    
    Returns:
        Dict containing the created event details
    """
    try:
        service = get_calendar_service()
        
        # Parse the date and time
        start_datetime = parse_datetime(date, time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Get system timezone
        timezone = get_system_timezone()
        
        # Create the event
        event = {
            'summary': title,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': timezone,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': notification_minutes}
                ]
            }
        }
        
        # Add optional fields
        if description:
            event['description'] = description
        if location:
            event['location'] = location
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        # Use specified calendar_id or default to primary calendar
        calendar_id = calendar_id or 'primary'
        
        # Create the event
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        
        return {
            'status': 'success',
            'event_id': event['id'],
            'html_link': event['htmlLink'],
            'summary': event['summary'],
            'start': event['start']['dateTime'],
            'end': event['end']['dateTime'],
            'calendar_id': calendar_id,
            'notification_minutes': notification_minutes
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def delete_calendar(calendar_id: str) -> Dict[str, Any]:
    """
    Delete a calendar.
    
    Args:
        calendar_id: ID of the calendar to delete
    
    Returns:
        Dict containing the operation status
    """
    try:
        service = get_calendar_service()
        service.calendars().delete(calendarId=calendar_id).execute()
        
        return {
            'status': 'success',
            'message': f'Calendar {calendar_id} deleted successfully'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
