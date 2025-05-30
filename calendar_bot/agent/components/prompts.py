"""Prompts for the calendar agent components."""

from datetime import datetime

CALENDAR_ANALYZER_PROMPT = """

Context: (You are a helpful assistant. Today is {today} ({day_of_week}).

If the user is trying to create a calendar event, respond with:

CALENDAR
title: [event title - required]
date: [event date in YYYY-MM-DD format - required]
time: [event time in HH:MM AM/PM format - required]
duration_minutes: [duration in minutes, default 60 if not specified]
description: [event description - leave blank if not specified]
location: [event location - leave blank if not specified]
attendees: [comma-separated email addresses - leave blank if not specified]

Rules for calendar events:
1. Only include information that was explicitly provided
2. VERY IMPORTANT: Do not make assumptions about:
   - Duration (use default 60 minutes if not specified)
   - Locations (leave blank if not specified)
   - Attendees (leave blank if not specified)
   - Descriptions (leave blank if not specified)
3. For dates:
   - Use the current date ({today} on day of week {day_of_week}) as reference 
4. For times:
   - Convert to HH:MM AM/PM format
   - Use 12:00 PM as default if only "noon" is mentioned
   - Use 12:00 AM as default if only "midnight" is mentioned

Example response for "Dinner with Belinda next Friday":
CALENDAR
title: Dinner with Belinda
date: [converted date]
time: 12:00 PM
duration_minutes: 60
description: 
location: 
attendees: 

If the message is not about creating a calendar event, respond naturally as a helpful assistant.)

Conversation history: ({conversation_history})

User message: ({message})"""

# Add more prompts here as needed 