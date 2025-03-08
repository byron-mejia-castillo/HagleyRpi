from get_weather import get_weather
from update_airtable import update_airtable

def main():
  weather_data = get_weather()
  print("Weather data fetched:", weather_data)
  update_airtable(weather_data)

if __name__ == "__main__":
  main()


