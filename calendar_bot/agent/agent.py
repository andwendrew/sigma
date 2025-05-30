"""Main agent that handles all calendar-related operations and user interactions."""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from calendar_bot.agent.components.calendar_analyzer import CalendarAnalyzer
from calendar_bot.tools.google_calendar import create_calendar_event

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalendarTool:
    """Tool for creating calendar events with detailed parameter handling."""
    
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

    def run(self, title: str, date: str, time: str, **kwargs: Any) -> Dict[str, Any]:
        """Run the calendar event creation tool."""
        return create_calendar_event(title, date, time, **kwargs)

class Agent:
    """Main agent that handles all calendar operations and user interactions."""
    
    def __init__(self):
        """Initialize the Agent with required components."""
        self.analyzer = CalendarAnalyzer()
        self.calendar_tool = CalendarTool()
        self.conversation_history = []  # Initialize conversation history
        logger.info("Agent initialized")
    
    def format_conversation_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history for context."""
        if not history:
            return "No previous conversation."
            
        formatted = []
        for msg in history:
            formatted.append(f"User: {msg['user']}")
            if 'assistant' in msg:
                formatted.append(f"Assistant: {msg['assistant']}")
        return "\n".join(formatted)
        
    def process_message(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Process a user message and perform appropriate operations.
        
        Args:
            message: The user's message to process
            conversation_history: Optional list of previous messages in the conversation
            
        Returns:
            A response string indicating the result of the operation
        """
        try:
            # Format conversation history
            formatted_history = self.format_conversation_history(conversation_history if conversation_history else self.conversation_history)
            
            # Analyze the message with conversation history
            result = self.analyzer.analyze_message(message, conversation_history=formatted_history)
            
            # If it's a calendar event, create it
            if isinstance(result, dict):
                event = self._create_calendar_event(result)
                response = self._format_event_response(event)
            else:
                response = result
            
            # Update conversation history
            self.conversation_history.append({
                'user': message,
                'assistant': response
            })
            
            return response
            
        except Exception as e:
            logger.error("Error processing message: %s", str(e), exc_info=True)
            error_response = f"I'm sorry, I encountered an error: {str(e)}"
            # Add error to conversation history
            self.conversation_history.append({
                'user': message,
                'assistant': error_response
            })
            return error_response
    
    def _create_calendar_event(self, event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a calendar event with the given details.
        
        Args:
            event_details: Dictionary containing event details
            
        Returns:
            Dictionary containing the created event information
        """
        try:
            # Create the event using the calendar tool
            event = self.calendar_tool.run(
                title=event_details['title'],
                date=event_details['date'],
                time=event_details['time'],
                description=event_details.get('description', ''),
                location=event_details.get('location', ''),
                duration_minutes=event_details.get('duration_minutes', 60),
                attendees=event_details.get('attendees', [])
            )
            
            if event['status'] == 'success':
                logger.info("Successfully created calendar event: %s", event['summary'])
            else:
                logger.error("Failed to create calendar event: %s", event.get('error', 'Unknown error'))
                
            return event
            
        except Exception as e:
            logger.error("Error creating calendar event: %s", str(e), exc_info=True)
            raise
    
    def _format_event_response(self, event: Dict[str, Any]) -> str:
        """
        Format a response message for a calendar event operation.
        
        Args:
            event: Dictionary containing event information
            
        Returns:
            Formatted response string
        """
        if event['status'] == 'success':
            return (
                f"I've created a calendar event for you:\n"
                f"📅 {event['summary']}\n"
                f"🕒 {event['start_time']}\n"
                f"📍 {event.get('location', 'No location specified')}\n"
                f"🔗 {event['html_link']}"
            )
        else:
            return f"I'm sorry, I couldn't create the calendar event: {event.get('error', 'Unknown error')}"

def test_agent():
    """Test the Agent with various inputs."""
    agent = Agent()
    
    # Test with conversation history
    conversation_history = [
        {"user": "Hi there!", "assistant": "Hello! How can I help you today?"},
        {"user": "I need to schedule some meetings", "assistant": "I'd be happy to help you schedule meetings. What would you like to schedule?"}
    ]
    
    test_cases = [
        # Calendar events
        "Schedule a meeting with John tomorrow at 2pm to discuss the project",
        "Create a team lunch on Friday at noon at the Italian restaurant",
        "Add a reminder for my dentist appointment on March 25th at 3:30pm",
        
        # General messages
        "What's the weather like today?",
        "How are you doing?",
        "Tell me a joke",
        
        # Edge cases
        "Schedule a meeting",  # Missing time
        "Create an event called 'Meeting'",  # Missing date and time
        "Set up a call with John",  # Missing all details
    ]
    
    print("\nTesting Agent")
    print("-" * 50)
    
    # Test without conversation history
    print("\nTesting without conversation history:")
    for message in test_cases:
        print(f"\nTest message: {message}")
        try:
            response = agent.process_message(message)
            print("Response:", response)
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 50)
    
    # Test with conversation history
    print("\nTesting with conversation history:")
    for message in test_cases:
        print(f"\nTest message: {message}")
        try:
            response = agent.process_message(message, conversation_history)
            print("Response:", response)
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    test_agent() 