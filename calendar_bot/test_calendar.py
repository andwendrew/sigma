from calendar_bot.tools.google_calendar import (
    list_calendars,
    create_calendar,
    create_calendar_event,
    delete_calendar
)

def test_calendar_management():
    # 1. List existing calendars
    print("\n1. Listing existing calendars:")
    calendars = list_calendars()
    for cal in calendars:
        print(f"- {cal['summary']} (ID: {cal['id']})")
        if cal.get('primary'):
            print("  (This is your primary calendar)")

    # 2. Create a new test calendar
    print("\n2. Creating a new test calendar:")
    new_calendar = create_calendar(
        calendar_name="Test Calendar",
        description="This is a test calendar for demonstration"
    )
    if new_calendar['status'] == 'success':
        print(f"Created calendar: {new_calendar['summary']}")
        print(f"Calendar ID: {new_calendar['calendar_id']}")
        test_calendar_id = new_calendar['calendar_id']
    else:
        print(f"Error creating calendar: {new_calendar['error']}")
        return

    # 3. Create an event in the new calendar
    print("\n3. Creating a test event in the new calendar:")
    event = create_calendar_event(
        title="Test Event",
        date="2024-03-25",
        time="2:30 PM",
        description="This is a test event",
        location="Virtual Meeting",
        calendar_id=test_calendar_id
    )
    if event['status'] == 'success':
        print(f"Created event: {event['summary']}")
        print(f"Event link: {event['html_link']}")
    else:
        print(f"Error creating event: {event['error']}")

    # 4. Create an event in the primary calendar
    print("\n4. Creating a test event in the primary calendar:")
    primary_event = create_calendar_event(
        title="Primary Calendar Test",
        date="2024-03-26",
        time="3:00 PM",
        description="This is a test event in the primary calendar"
    )
    if primary_event['status'] == 'success':
        print(f"Created event: {primary_event['summary']}")
        print(f"Event link: {primary_event['html_link']}")
    else:
        print(f"Error creating event: {primary_event['error']}")

    # 5. List calendars again to see the new one
    print("\n5. Listing calendars after creating new one:")
    updated_calendars = list_calendars()
    for cal in updated_calendars:
        print(f"- {cal['summary']} (ID: {cal['id']})")

    # 6. Delete the test calendar
    print("\n6. Deleting the test calendar:")
    delete_result = delete_calendar(test_calendar_id)
    if delete_result['status'] == 'success':
        print(f"Successfully deleted calendar: {test_calendar_id}")
    else:
        print(f"Error deleting calendar: {delete_result['error']}")

    # 7. Final calendar list
    print("\n7. Final list of calendars:")
    final_calendars = list_calendars()
    for cal in final_calendars:
        print(f"- {cal['summary']} (ID: {cal['id']})")

if __name__ == "__main__":
    test_calendar_management() 