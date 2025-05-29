from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field

# Import the real LLM and tool
from .llm.mistral_local import get_mistral_llm
from .tools.google_calendar import create_calendar_event

class CalendarTool:
    def __init__(self):
        self.name = "create_calendar_event"
        self.description = """Creates a Google Calendar event. 
        Required parameters:
        - title: The event title
        - date: The event date (supports formats like YYYY-MM-DD, MM/DD/YYYY, Month DD, YYYY)
        - time: The event time (supports formats like HH:MM, HH:MM AM/PM)
        
        Optional parameters:
        - duration_minutes: Event duration in minutes (default: 60)
        - description: Event description
        - location: Event location
        - attendees: List of attendee email addresses"""

    def run(self, title: str, date: str, time: str, **kwargs: Any) -> str:
        result = create_calendar_event(title, date, time, **kwargs)
        if result['status'] == 'success':
            return f"Successfully created event '{result['summary']}' on {result['start']}. You can view it here: {result['html_link']}"
        else:
            return f"Failed to create event: {result['error']}"

def format_conversation_history(history: List[Dict[str, str]]) -> str:
    """Format conversation history for the LLM."""
    formatted = ""
    for msg in history:
        formatted += f"User: {msg['user']}\n"
        if 'assistant' in msg:
            formatted += f"Assistant: {msg['assistant']}\n"
    return formatted

def process_command(command: str, history: Optional[List[Dict[str, str]]] = None) -> str:
    llm = get_mistral_llm()
    tools = [CalendarTool()]
    
    # Format the conversation history
    context = ""
    if history:
        context = format_conversation_history(history)
        context += "\nUser: " + command
    else:
        context = command
    
    # For now, just return LLM output (no tool use yet)
    return llm(context)

def test_calendar():
    """Test function to create a simple calendar event."""
    tool = CalendarTool()
    result = tool.run(
        title="Test Meeting",
        date="2024-03-15",  # Tomorrow's date
        time="14:00",
        duration_minutes=30,
        description="This is a test meeting",
        location="Virtual Meeting"
    )
    print(result)

if __name__ == "__main__":
    test_calendar()
