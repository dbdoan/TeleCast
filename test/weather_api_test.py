import json
import os
import requests
import sys

from clear import clean
from dotenv import load_dotenv

clean()

# ------------------------------------ #
# Load environment variables
load_dotenv()

API_KEY = os.getenv('WEATHER_API_KEY')
if API_KEY:
    print('API Key is set.')
else:
    print("API Key is not set.")
    sys.exit(1)

url = f'https://api.tomorrow.io/v4/weather/realtime?location=12345]&apikey={API_KEY}'

# ------------------------------------ #
try:
    response = requests.get(url, timeout=10)
    # Raise an HTTPError for bad responses
    response.raise_for_status()
    data = response.json()

    print(data['location'])

    # print(data['timelines'].items())
    
    # Extract specific attributes from the JSON response
    # For example, let's extract temperature, humidity, and wind speed from the data
    # if 'timelines' in data and 'daily' in data['timelines']:
    #     for day in data['timelines']['daily']:
    #         date = day['time']
    #         temperature = day['values'].get('temperature', 'N/A')
    #         humidity = day['values'].get('humidity', 'N/A')
    #         wind_speed = day['values'].get('windSpeed', 'N/A')
    #         print(f"Date: {date}")
    #         print(f"Temperature: {temperature}")
    #         print(f"Humidity: {humidity}")
    #         print(f"Wind Speed: {wind_speed}")
    #         print("---------------")
    # else:
    #     print("Unexpected JSON structure")

except requests.exceptions.HTTPError as errh:
    print("HTTP Error:", errh)
except requests.exceptions.ConnectionError as errc:
    print("Error Connecting:", errc)
except requests.exceptions.Timeout as errt:
    print("Timeout Error:", errt)
except requests.exceptions.RequestException as err:
    print("Something went wrong:", err)
