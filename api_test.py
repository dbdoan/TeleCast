import json
import os
import requests
import sys

from dotenv import load_dotenv

# ------------------------------------ #
# ------------------------------------ #
def clear_console():
    """Clear the console based on the OS."""
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')

# Clear the console
clear_console()

# ------------------------------------ #
# ------------------------------------ #
# Load environment variables
load_dotenv()

API_KEY = os.getenv('WEATHER_API_KEY')
if API_KEY:
    print('API Key is set.')
else:
    print("API Key is not set.")
    sys.exit(1)

url = f'https://api.tomorrow.io/v4/weather/forecast?location=42.3478,-71.0466&apikey={API_KEY}'

# ------------------------------------ #
# ------------------------------------ #
try:
    response = requests.get(url,timeout=10)
    # Raise an HTTPError for bad responses
    response.raise_for_status()  
    data = response.json()
    pretty_data = json.dumps(data, indent=2)
    print(pretty_data)
except requests.exceptions.HTTPError as errh:
    print("HTTP Error:", errh)
except requests.exceptions.ConnectionError as errc:
    print("Error Connecting:", errc)
except requests.exceptions.Timeout as errt:
    print("Timeout Error:", errt)
except requests.exceptions.RequestException as err:
    print("Something went wrong:", err)