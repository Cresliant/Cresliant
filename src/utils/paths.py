import os
import sys


def resource(relative_path):
    return os.path.join(os.path.dirname(__file__), "../../assets", relative_path)


def general_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), "../../", relative_path)
