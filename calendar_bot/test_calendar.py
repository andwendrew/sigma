from calendar_bot.tools.google_calendar import list_calendars

def test_calendar_listing():
    print("\nListing calendars:")
    print(list_calendars())


if __name__ == "__main__":
    test_calendar_listing() 