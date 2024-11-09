import os
import socket

from sys import platform


def check_internet_connection():
    # return False  # debug
    # offline mini game coming soon!

    try:
        socket.create_connection(("github.com", 80), timeout=5)
        return True
    except OSError:
        pass

    try:
        socket.create_connection(("1.1.1.1", 53), timeout=5)
        return True
    except OSError:
        pass

    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        pass

    return False

def clear_screen() -> None:
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")