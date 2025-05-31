"""Utility functions for date handling."""

from datetime import datetime, timedelta

def get_next_two_weeks_dates(today: str, day_of_week: str) -> str:
    """
    Generate a string mapping of dates to days of the week for the next two weeks.
    
    Args:
        today: Date string in YYYY-MM-DD format
        day_of_week: Current day of the week
        
    Returns:
        String containing the date-to-day mapping for the next two weeks
    """
    # Parse the input date
    current_date = datetime.strptime(today, "%Y-%m-%d")
    
    # Generate the mapping for the next 14 days
    date_mapping = []
    for i in range(14):
        date = current_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        day = date.strftime("%A")
        date_mapping.append(f"{date_str}: {day}")
    
    return "\n".join(date_mapping) 
