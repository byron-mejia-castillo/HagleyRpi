
# airtable_push.py

from datetime import datetime  # Used to get current timestamp
import pytz  # For timezone-aware timestamps
from pyairtable import Api  # Airtable Python wrapper for API interaction

# Airtable access credentials (PAT should be stored securely in production)
BASE_ID = "app69VOY1oNDOWhHl"  # ID of the Airtable base
TABLE_NAME = "Guest Tracking"  # Name of the table where guest data will be stored

# Function to push total entered/exited counts to Airtable
def push_to_airtable(total_entered, total_exited):
    # Generate a timestamp in US Eastern Time
    eastern = pytz.timezone('America/New_York')
    timestamp = datetime.now(eastern).isoformat()

    # Debug logging of what is being pushed
    print(f"[INFO] Attempting to push to Airtable at {timestamp}")
    print(f"[INFO] Counts - Entered: {total_entered}, Exited: {total_exited}")

    try:
        # Connect to Airtable using the Personal Access Token (PAT)
        api = Api(PAT)
        table = api.table(BASE_ID, TABLE_NAME)

        # Create a new record using a dictionary of field names and values
        new_record = {
            "Timestamp": timestamp,
            "Exhibit Name": "Machine Workshop",  # Static value, can be made dynamic per exhibit
            "Total Entered": total_entered,
            "Total Exited": total_exited
        }

        # Send the new record to Airtable
        response = table.create(new_record)
        print("[INFO] Airtable push successful:", response)

    except Exception as e:
        # Error handling if the push fails
        print("[ERROR] Airtable push failed:", e)
