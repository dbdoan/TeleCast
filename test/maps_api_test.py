
import dotenv
import os
import requests

from clear import clean

clean()
# ------------------------------------ #
dotenv.load_dotenv()

MAP_KEY = os.getenv("MAP_KEY")
if MAP_KEY:
    print("MAP_KEY SECURED.")
else:
    print("MAP_KEY NOT SET.")



# ------------------------------------ #
try:
    url = f'https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/-122.103,37.8936,9.32,0/300x200?access_token={MAP_KEY}'
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    # Save the image
    with open('map_image.png', 'wb') as file:
        file.write(response.content)
    print("Image saved as map_image.png.")

except requests.exceptions.HTTPError as errh:
    print("HTTP Error: ", errh)
except requests.exceptions.ConnectionError as errc:
    print("Connection Error: ", errc)
except requests.exceptions.Timeout as errt:
    print("Timeout Error: ", errt)
except requests.exceptions.RequestException as err:
    print("Something went wrong: ", err)