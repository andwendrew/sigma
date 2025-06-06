from typing import Dict, Any, Optional, Union, List
import sys
import os
import logging
from datetime import datetime
from calendar_bot.agent.components.date_utils import get_next_two_weeks_dates
from calendar_bot.tools.google_calendar import list_calendars

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from calendar_bot.llm.llama_local import get_llama_llm
from calendar_bot.agent.components.prompts import CALENDAR_ANALYZER_PROMPT
from calendar_bot.llm.llama_local import MODEL_NAME

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress Google API client warnings
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

_llm_instance = None

def get_llm():
    """Get or create the LLM instance (singleton pattern)."""
    global _llm_instance
    if _llm_instance is None:
        logger.info("Initializing LLM with model: %s", MODEL_NAME)
        _llm_instance = get_llama_llm(
            temperature=0.2,  # Lower temperature for more deterministic responses
            top_p=0.3,       # Lower top_p for more focused responses
            top_k=20,        # Lower top_k for more precise token selection
            num_predict=512  # Reduced max tokens since calendar events are concise
        )
    return _llm_instance

class CalendarAnalyzer:
    """Analyzes messages to detect and extract calendar event details."""
    
    def __init__(self, default_duration: int = 60):
        """
        Initialize the CalendarAnalyzer.
        
        Args:
            default_duration: Default duration in minutes for events (default: 60)
        """
        self.llm = get_llm()
        self.default_duration = default_duration
        self.available_calendars = {}  # Cache for calendar lookups
        self.primary_calendar_id = None
        logger.info("CalendarAnalyzer initialized with default duration: %d minutes", default_duration)
    
    def _update_calendar_cache(self):
        """Update the cache of available calendars."""
        calendars = list_calendars()
        self.available_calendars = {
            cal['id']: cal for cal in calendars
        }
        # Store primary calendar ID
        primary_cal = next((cal for cal in calendars if cal.get('primary')), None)
        if primary_cal:
            self.primary_calendar_id = primary_cal['id']
        else:
            self.primary_calendar_id = None
    
    def _parse_calendar_id(self, calendar_id: str) -> str:
        """
        Parse and validate a calendar ID.
        
        Args:
            calendar_id: The calendar ID to validate
            
        Returns:
            The validated calendar ID or the primary calendar's ID if invalid/not found
        """
        if not calendar_id:
            return self.primary_calendar_id
            
        # Update calendar cache if empty
        if not self.available_calendars:
            self._update_calendar_cache()
            
        # Check if the ID exists in our calendars
        if calendar_id in self.available_calendars:
            return calendar_id
            
        # If not found, return primary calendar ID
        logger.warning(f"Calendar ID {calendar_id} not found, defaulting to primary calendar")
        return self.primary_calendar_id
    
    def _parse_attendees(self, attendees_str: str) -> List[str]:
        """
        Parse attendees string into a list of email addresses.
        Only includes strings that contain '@' as they are considered email addresses.
        
        Args:
            attendees_str: Comma-separated string of attendees
            
        Returns:
            List of email addresses
        """
        if not attendees_str or attendees_str.lower() == "none":
            return []
            
        # Split by comma and clean up each attendee
        attendees = [a.strip() for a in attendees_str.split(",")]
        
        # Only keep attendees that look like email addresses
        email_attendees = [a for a in attendees if "@" in a]
        
        if email_attendees:
            logger.info(f"Parsed attendees: {email_attendees}")
        else:
            logger.info("No valid email addresses found in attendees")
            
        return email_attendees
        
    def analyze_message(self, message: str, conversation_history: Optional[str] = None) -> Union[Dict[str, Any], str]:
        """
        Analyze a message and either extract calendar event details or return a natural response.
        
        Args:
            message: The user's message to analyze
            conversation_history: Optional formatted conversation history
            
        Returns:
            Either a dictionary with event details if it's a calendar event, or a string with the natural response
        """
        if not message or not isinstance(message, str):
            raise ValueError("Message must be a non-empty string")
            
        logger.info("Analyzing message: %s", message)
        
        # Update calendar cache
        self._update_calendar_cache()
        
        # Format the prompt with current date and conversation history
        today = datetime.now().strftime("%Y-%m-%d")
        day_of_week = datetime.now().strftime("%A")
        
        # Create the system prompt with calendar instructions
        system_prompt = CALENDAR_ANALYZER_PROMPT.format(
            today=today,
            day_of_week=day_of_week,
            conversation_history=conversation_history,
            date_mapping=get_next_two_weeks_dates(today, day_of_week),
            calendar_list=list_calendars()
        )

        try:
            # Get response from LLM with the calendar system prompt
            response = self.llm(prompt=message, system_prompt=system_prompt)
            logger.info("Received response from LLM")
            
            # Check if it's a calendar event
            if "CALENDAR-----" in response:
                # Get only the content after CALENDAR-----
                calendar_content = response.split("CALENDAR-----")[1].strip()
                
                # Parse the calendar event details
                event_details = {}
                for line in calendar_content.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if value:  # Only add non-empty values
                            # Convert duration_minutes to integer
                            if key == "duration_minutes":
                                try:
                                    value = int(value)
                                except ValueError:
                                    value = self.default_duration
                            # Parse calendar_id if present
                            elif key == "calendar_id":
                                value = self._parse_calendar_id(value)
                            # Convert notification_minutes to integer
                            elif key == "notification_minutes":
                                try:
                                    value = int(value)
                                except ValueError:
                                    value = 10  # Default notification time
                            # Parse attendees if present
                            elif key == "attendees":
                                value = self._parse_attendees(value)
                            event_details[key] = value
                
                # Validate required fields
                required_fields = ["title", "date", "time"]
                missing_fields = [field for field in required_fields if field not in event_details]
                if missing_fields:
                    raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
                
                # Add default duration if not specified
                if "duration_minutes" not in event_details:
                    event_details["duration_minutes"] = self.default_duration
                
                # Add default notification time if not specified
                if "notification_minutes" not in event_details:
                    event_details["notification_minutes"] = 10
                
                # Add default calendar_id if not specified
                if "calendar_id" not in event_details:
                    event_details["calendar_id"] = self.primary_calendar_id
                
                return event_details
            else:
                # Return the natural response
                return response.strip()
                
        except Exception as e:
            logger.error("Error analyzing message: %s", str(e))
            raise

def test_analyzer():
    """Test the calendar analyzer with some example messages."""
    analyzer = CalendarAnalyzer()
    
    test_messages = [
        "lunch with manager david tomorrow noon amazon intern"
    ]
    for message in test_messages:
        print(f"\nTesting message: {message}")
        try:
            result = analyzer.analyze_message(message)
            print(result)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_analyzer()