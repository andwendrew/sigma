"""Prompts for the calendar agent components."""

from datetime import datetime

DATE_REFERENCE_TRANSFORMER_PROMPT = """
Context: Today is {today}, {day_of_week}.

Transform the user's date/time references into a Python dictionary that can be reliably computed.
IMPORTANT: Return a raw Python dictionary, not a string representation of a dictionary.

Valid output formats (return these exact Python dictionaries):
1. For single dates:
dict(type="single", reference="TODAY", offset=0)
dict(type="single", reference="MONDAY", offset=7)

2. For date ranges:
dict(type="range", reference="TODAY", offset=0, end_reference="FRIDAY", end_offset=0)

3. For errors:
dict(error="no_date")
dict(error="ambiguous")

Valid reference values (use these EXACTLY):
TODAY
TOMORROW
MONDAY
TUESDAY
WEDNESDAY
THURSDAY
FRIDAY
SATURDAY
SUNDAY

Rules (return these exact Python dictionaries):
1. For single dates:
   - "today" -> dict(type="single", reference="TODAY", offset=0)
   - "tomorrow" -> dict(type="single", reference="TODAY", offset=1)
   - "next [day]" -> dict(type="single", reference="[day]", offset=7)
   - "this [day]" -> dict(type="single", reference="[day]", offset=0)
   - "in X days" -> dict(type="single", reference="TODAY", offset=X)
   - "X days from [day]" -> dict(type="single", reference="[day]", offset=X)

2. For date ranges:
   - "from [day] to [day]" -> dict(type="range", reference="[day]", offset=0, end_reference="[day]", end_offset=0)
   - "until [day]" -> dict(type="range", reference="TODAY", offset=0, end_reference="[day]", end_offset=0)
   - "next X days" -> dict(type="range", reference="TODAY", offset=0, end_reference="TODAY", end_offset=X)

3. For ambiguous cases:
   - If multiple interpretations possible, choose the closest future date
   - If unclear, return dict(error="ambiguous")
   - If no date reference found, return dict(error="no_date")

Examples (return these exact Python dictionaries):
1. Single dates:
   - "next Monday" -> dict(type="single", reference="MONDAY", offset=7)
   - "this Friday" -> dict(type="single", reference="FRIDAY", offset=0)
   - "in 3 days" -> dict(type="single", reference="TODAY", offset=3)
   - "2 days after next Tuesday" -> dict(type="single", reference="TUESDAY", offset=9)

2. Date ranges:
   - "from Monday to Friday" -> dict(type="range", reference="MONDAY", offset=0, end_reference="FRIDAY", end_offset=0)
   - "until next Wednesday" -> dict(type="range", reference="TODAY", offset=0, end_reference="WEDNESDAY", end_offset=7)
   - "next 5 days" -> dict(type="range", reference="TODAY", offset=0, end_reference="TODAY", end_offset=5)

3. Error cases:
   - "schedule a workout" -> dict(error="no_date")
   - "next week sometime" -> dict(error="ambiguous")

If the message contains no date references, return dict(error="no_date").
"""

CALENDAR_ANALYZER_PROMPT = """
Context: (You are a helpful assistant. Today is {today}, {day_of_week}.

For reference, here is a list of the next two weeks' from today's dates and days of the week:
{date_mapping}

If the user's message calls for the creation of a calendar event, respond in the exactly following format with
all the relevant fields correctly filled out: 

CALENDAR
title: [event title]
date: [YYYY-MM-DD]
time: [HH:MM]
duration_minutes: [default 60 if not specified]
description: [leave blank if not specified]
location: [leave blank if not specified]
attendees: [leave blank if not specified]

Specifically for location and attendees, it is crucial to not make up fake information or make assumptions, so to be 
safe, leave these blank unless the user explicitly provides them. 

If the message is NOT about creating a calendar event, respond naturally as a helpful assistant.

Rules:
1. For calendar events:
   - Convert relative dates to YYYY-MM-DD
   - Convert times to HH:MM in 24 hour format
   - Use 12:00 PM for "noon", 12:00 AM for "midnight"
   - Leave optional fields blank
   - Do not make up email addresses

2. For non-calendar related queries:
   - Give a natural, helpful response
   - Do not use the CALENDAR format

Please use the conversation history to understand the user's intent and context.

Conversation history: ({conversation_history})"""

# Add more prompts here as needed 