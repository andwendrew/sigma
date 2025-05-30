from typing import Dict, Any, Optional, Union
import sys
import os
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from calendar_bot.llm.mistral_local import get_mistral_llm
from calendar_bot.agent.components.prompts import CALENDAR_ANALYZER_PROMPT

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
MODEL_NAME = "mistral"
_llm_instance = None

def get_llm():
    """Get or create the LLM instance (singleton pattern)."""
    global _llm_instance
    if _llm_instance is None:
        logger.info("Initializing LLM with model: %s", MODEL_NAME)
        _llm_instance = get_mistral_llm()
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
        logger.info("CalendarAnalyzer initialized with default duration: %d minutes", default_duration)
        
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

        try:
            logger.debug("Analyzing message: %s", message)
            today = datetime.now()
            
            # Format the prompt with current date and message
            prompt = CALENDAR_ANALYZER_PROMPT.format(
                today=today.strftime("%A, %B %d, %Y"),
                day_of_week=today.strftime("%A"),
                message=message,
                conversation_history=conversation_history or "No previous conversation."
            )
            
            # Get response from Mistral
            response = self.llm(prompt).strip()
            
            if response.startswith("CALENDAR"):
                return self.extract_event_details(response)
                    
            logger.debug("Message is not a calendar event, returning natural response")
            return response
            
        except Exception as e:
            logger.error("Error analyzing message: %s", str(e), exc_info=True)
            return "I'm sorry, I encountered an error processing your message."
        
    def extract_event_details(self, response: str) -> Dict[str, Any]:
        """
        Extract event details from a CALENDAR formatted response.
        
        Args:
            response: The LLM's response in CALENDAR format
            
        Returns:
            Dictionary with the event details
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not response.startswith("CALENDAR"):
            raise ValueError("Response must start with 'CALENDAR'")

        lines = response.split('\n')
        event_details = {}
        
        for line in lines[1:]:  # Skip the CALENDAR line
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if value and value != "none":  # Skip empty or "none" values
                    if key == "duration_minutes":
                        try:
                            event_details["duration_minutes"] = int(value)
                        except ValueError:
                            logger.warning("Invalid duration value: %s, using default", value)
                            event_details["duration_minutes"] = self.default_duration
                    elif key == "attendees":
                        event_details["attendees"] = [email.strip() for email in value.split(',')]
                    else:
                        event_details[key] = value
        
        # Validate required fields
        required_fields = ['title', 'date', 'time']
        missing_fields = [field for field in required_fields if field not in event_details]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
        return event_details

def test_analyzer():
    """Test the CalendarAnalyzer with various inputs."""
    analyzer = CalendarAnalyzer()
    
    test_cases = [
        "Dinner with Belinda next Friday at 6pm",
        "When is next Friday?"
    ]
    
    print("\nTesting Calendar Analyzer")
    print("-" * 50)
    
    for message in test_cases:
        print(f"\nTest message: {message}")
        try:
            result = analyzer.analyze_message(message)
            if isinstance(result, dict):
                print("Calendar Event detected:")
                print(f"- Title: {result['title']}")
                print(f"- Date: {result['date']}")
                print(f"- Time: {result['time']}")
                print(f"- Duration: {result.get('duration_minutes', 60)} minutes")
                if 'description' in result:
                    print(f"- Description: {result['description']}")
                if 'location' in result:
                    print(f"- Location: {result['location']}")
                if 'attendees' in result:
                    print(f"- Attendees: {', '.join(result['attendees'])}")
            else:
                print("Natural response:", result)
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    test_analyzer()