import requests
from datetime import datetime
import pytz

API_KEY = '806dcbbf856919ac491f51e788a82ec9'
CITY = 'Wilmington'

url = f'http://api.openweathermap.org/data/2.5/weather?q=Wilmington,DE,US&appid={API_KEY}&units=imperial'


def get_weather():
  try:
      print("fetching weather data...")
      response = requests.get(url)
      if response.status_code == 200:
         print("API response recieved")
         data = response.json()
         print("data fetched from API:", data)

         temperature = data['main']['temp']
         humidity = data['main']['humidity']
         weather =  data['weather'][0]['description']
         timestamp = data['dt']

         degree_symbol = "\u00b0"
         formatted_temp = f"{int(temperature)}{degree_symbol}F"

         formatted_humidity = f"{int(humidity)}%"

         est = pytz.timezone('US/Eastern')
         time = datetime.fromtimestamp(timestamp, tz=pytz.utc).astimezone(est)
         time_str = time.strftime('%Y-%m-%d %H:%M:%S')
         date_str = time.strftime('%Y-%m-%d')
         time_only_str = time.strftime('%H:%M:%S')
         weather_data = {
           'temperature': formatted_temp,
           'weather': weather,
           'humidity': formatted_humidity,
           'date': date_str,
           'time': time_only_str
         }
         print(f"Weather data returned: {weather_data}")
         return weather_data

#         print(f"weather in {CITY} (at {time_str} EST):")
#         print(f"Temperature: {temperature}°F")
#         print(f"Weather: {weather}")
#         print(f"Humidity: {humidity}%")
      else:
        print(f"Error fetching weather data. status code: {response.status_code}")
  except Exception as e:
    print(f"An error occurred: {e}")

if __name__ == "__main__":
  get_weather()