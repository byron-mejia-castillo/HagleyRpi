import requests
import time
from datetime import datetime
import pytz

AIRTABLE_API_URL = 'https://api.airtable.com/v0/app69VOY1oNDOWhHl/tblclQ6dJrZD55ORz'
AIRTABLE_PAT = 'patgilkGDswzak9Ty.ae5c53eda53254abe5d1df62580ab750aad449c862892f41de141917420c27a7'

headers = {
    'Authorization': f'Bearer {AIRTABLE_PAT}',
    'Content-Type': 'application/json'
}

def send_to_airtable(total_entered, total_exited):
    """
    Send data to Airtable.
    - total_entered: Incremental number of guests captured (new entries since last update)
    - total_exited: Incremental number of exits (new exits since last update)
    """
    # Get current time in EST
    eastern = pytz.timezone('America/New_York')
    timestamp = datetime.now(eastern).isoformat()  
    data = {
        "fields": {
#words in quotations need to be matching with the field names in the table
            "Timestamp": timestamp,
            "Count": total_entered,
            "Total Exited": total_exited,
            "Exhibit Name": "Machine Workshop" #edit this line for the single select options we have on our AirTable 
        }
    }
    try:
        response = requests.post(AIRTABLE_API_URL, headers=headers, json=data)
        response.raise_for_status()
        print(f"[INFO] Sent to Airtable: Total Entered = {total_entered}, Total Exited = {total_exited}")
    except requests.exceptions.RequestException as e:
#error messages will be sent back for debugging
        print(f"[ERROR] Failed to send to Airtable: {e}")
        if e.response is not None:
            print(f"[DEBUG] Response: {e.response.text}")