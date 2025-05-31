"""Utility functions for date handling."""

from datetime import datetime, timedelta
from collections import defaultdict

def get_next_two_weeks_dates(today: str, day_of_week: str) -> str:
    """
    Generate a string mapping of dates to days of the week for the next two weeks.
    
    Args:
        today: Date string in YYYY-MM-DD format
        day_of_week: Current day of the week
        
    Returns:
        String containing the date-to-day mapping organized by day of week
    """
    # Parse the input date
    current_date = datetime.strptime(today, "%Y-%m-%d")
    
    # Find the Monday of the current week
    days_since_monday = current_date.weekday()
    monday_of_current_week = current_date - timedelta(days=days_since_monday)
    
    # Create a dictionary to store dates by day of week
    dates_by_day = defaultdict(dict)
    
    # Generate dates for the next 21 days (to cover this week, next week, and next next week)
    for i in range(21):
        date = current_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        day = date.strftime("%A")
        
        # Calculate days since Monday of current week
        days_since_monday = (date - monday_of_current_week).days
        
        # Determine which week this date belongs to
        if days_since_monday < 7:
            week_label = "this"
        elif days_since_monday < 14:
            week_label = "next"
        else:
            week_label = "next_next"
            
        # Only store the date if we haven't seen this day+week combination yet
        if week_label not in dates_by_day[day]:
            dates_by_day[day][week_label] = date_str
    
    # Format the output as a string
    output = []
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        if day in dates_by_day:
            dates = dates_by_day[day]
            output.append(f"{day}:")
            if "this" in dates:
                output.append(f"  this {day}: {dates['this']}")
            if "next" in dates:
                output.append(f"  next {day}: {dates['next']}")
            if "next_next" in dates:
                output.append(f"  next next {day}: {dates['next_next']}")
            output.append("")  # Add blank line between days
    
    return "\n".join(output) 
    