import os
import platform

# Clear console

def clean():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")