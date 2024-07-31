
import dotenv
import os
import requests

from clear import clean
from urllib.parse import quote


clean()

# # ------------------------------------ #
# Check if API_TOKEN is set
dotenv.load_dotenv()

def check_env_tokens():
    MAP_KEY = os.getenv("MAP_KEY")
    if MAP_KEY:
        print("MAP_KEY SECURED.")
    else:
        print("MAP_KEY NOT SET.")

check_env_tokens()

# # ------------------------------------ #
# Functions to set user's info and check
def set_address_line_1():
    user_address = str(input("Enter in your Address (line 1): ").title())
    return user_address

def set_city():
    user_city = str(input("Enter in your city: " ).capitalize())
    return user_city

def set_state():
    user_state = str(input("Enter in your state (ex: CA, TX, FL): ").upper())
    return user_state

def set_zipcode():
    user_zipcode = str(input("Enter in your zipcode: "))
    return user_zipcode

def set_user_info():
    user_info_dict = {
        "user_address_line_1": set_address_line_1(),
        "user_city": set_city(),
        "user_state": set_state(),
        "user_zipcode": set_zipcode()
    }
    return user_info_dict

def info_check(user_dict):
    user_correct = ""
    while user_correct != 'yes'.lower or user_correct != 'y'.lower():
        user_correct = str(input("\n"
                        f"Address Line 1: {user_dict['user_address_line_1']}\n"
                        f"City: {user_dict['user_city']}\n"
                        f"State: {user_dict['user_state']}\n"
                        f"Zipcode: {user_dict['user_zipcode']}\n"
                        "Here is the information you entered, is everything correct? (y/n): "))
        if user_correct == 'no'.lower() or user_correct == 'n'.lower():
            user_dict = set_user_info()
        elif user_correct == 'yes'.lower() or user_correct == 'y'.lower():
            break
# # ------------------------------------ #

# def encode_address(address):
#     encoded_address = quote(address)
#     return encoded_address


container = set_user_info()

info_check(container)

print(container)

# user_full_address = (f"{user_address_line_1} {user_city} {user_state} {user_zipcode} United States")
# formatted_address = quote(user_full_address)

# try:
#     url = f'https://api.mapbox.com/search/geocode/v6/forward?q={formatted_address}&country=us&proximity=ip&types=address&language=en&access_token={MAP_KEY}'
#     response = requests.get(url, timeout=10)
#     response.raise_for_status()
#     # Save the image
#     # with open('map_image.png', 'wb') as file:
#     #     file.write(response.content)
#     # print("Image saved as map_image.png.")
#     data = response.json()
#     print(data)

# except requests.exceptions.HTTPError as errh:
#     print("HTTP Error: ", errh)
# except requests.exceptions.ConnectionError as errc:
#     print("Connection Error: ", errc)
# except requests.exceptions.Timeout as errt:
#     print("Timeout Error: ", errt)
# except requests.exceptions.RequestException as err:
#     print("Something went wrong: ", err)