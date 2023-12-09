import subprocess
import sys


def get_base_prefix_compat():
    """Get base/real prefix, or sys.prefix if there is none."""
    return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix


if sys.prefix == get_base_prefix_compat():
    print("Please run this script using the virtual environment")
    sys.exit()

args = [
    "pyinstaller",
    "main.py",
    "--name=Cresliant",
    "--add-data=assets/icon.ico;.",
    "--add-data=assets/Roboto-Regular.ttf;.",
    "--onefile",
    "--noconsole",
    "--noconfirm",
]

if sys.platform == "win32":
    args.append("--icon=assets/icon.ico")

subprocess.call(args)
