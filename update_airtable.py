import requests


pat = "patletzoLLi7ce7xL.0db2bf92647a7435f3d8c952f7d48577d715f9c0cddd3dc0db2825f4e7b088b9"  
base_id = "appWkXrNpjVQgVEJw"  
table_name = "weather"  


def update_airtable(weather_data):
    if not weather_data:
        print("No weather data to send to Airtable.")
        return


    airtable_url = f"https://api.airtable.com/v0/appWkXrNpjVQgVEJw/weather"

    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json"
    }

 
    data = {
        "fields": {
            "temperature": weather_data['temperature'],
            "weather": weather_data['weather'],
            "humidity": weather_data['humidity'],
            "date": weather_data['date'],
            "time": weather_data['time'],
        }
    }

    try:
        print("Sending data to Airtable...")
        response = requests.post(airtable_url, json=data, headers=headers)

        if response.status_code == 200:
            print("Data successfully sent to Airtable!")
        else:
            print(f"Failed to send data to Airtable: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"An error occurred while sending data to Airtable: {e}")


if __name__ == "__main__":
    update_airtable(weather_data=None)  # Placeholder call, you'll pass real data when using it