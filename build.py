import configparser
import subprocess
import sys


def get_base_prefix_compat():
    """Get base/real prefix, or sys.prefix if there is none."""
    return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix


if sys.prefix == get_base_prefix_compat():
    print("Please run this script using the virtual environment")
    sys.exit()

version = sys.version_info
if version.major != 3 or version.minor != 10:
    print(
        f"Warning: Use python 3.10 for the best optimization, you are currently using {version.major}.{version.minor}"
    )

args = [
    "pyinstaller",
    "main.py",
    "--name=Cresliant",
    "--add-data=assets;assets",
    "--add-data=pyproject.toml;.",
    "--add-data=src/utils/FileDialog/images;src/utils/FileDialog/images",
    "--onefile",
    "--noconsole",
    "--noconfirm",
]

# Find and remove all dev dependencies from the build incase they are accidentally included
config = configparser.ConfigParser()
config.read("pyproject.toml")
if "tool.poetry.group.dev.dependencies" in config.sections():
    for dependency in config.options("tool.poetry.group.dev.dependencies"):
        args.append("--exclude-module=" + dependency.replace("-", "_"))

if sys.platform == "win32":
    args.append("--icon=assets/icon.ico")

subprocess.call(args)
