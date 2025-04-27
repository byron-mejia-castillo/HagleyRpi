import requests
import time
from datetime import datetime
import pytz
import creds

AIRTABLE_API_URL = 'https://api.airtable.com/v0/app69VOY1oNDOWhHl/tblclQ6dJrZD55ORz'
AIRTABLE_PAT = creds.AIRTABLE_PAT

LAT = "39.77"
LON = "-75.58"
WEATHER_API_URL = f'https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&units=imperial&appid={creds.WEATHER_API}'

headers = {
    'Authorization': f'Bearer {AIRTABLE_PAT}',
    'Content-Type': 'application/json'
}

def get_weather():
    try:
        response = requests.get(WEATHER_API_URL)
        response.raise_for_status()
        weather_data = response.json()
        temperature = weather_data['main']['temp']
        weather_desc = weather_data['weather'][0]['description']
        return temperature, weather_desc
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch weather data: {e}")
        return None, None
def send_to_airtable(total_entered, total_exited):
    """
    Send data to Airtable.
    - total_entered: Incremental number of guests captured (new entries since last update)
    - total_exited: Incremental number of exits (new exits since last update)
    """
    # Get current time in EST
    eastern = pytz.timezone('America/New_York')
    timestamp = datetime.now(eastern).isoformat()
    temperature, weather_desc = get_weather()
  
    data = {
        "fields": {
#words in quotations need to be matching with the field names in the table
            "Timestamp": timestamp,
            "Total Entered": total_entered,
            "Total Exited": total_exited,
            "Exhibit Name": "The House", #edit this line for the single select options we have on our AirTable
            "Temperature": temperature,
            "Weather Description": weather_desc 
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


