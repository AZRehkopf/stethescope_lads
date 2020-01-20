# steth_controller.py
# Coordinates all the digital stethescope components

### Imports ###

# Built-ins
import logging
import os
import sys

# Local imports

# Third party imports

### Globals ###

LOGGING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')

if not os.path.isdir(LOGGING_DIR):
    os.mkdir(LOGGING_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOGGING_DIR, 'python.log')),
        logging.StreamHandler(sys.stdout)
    ])

LOGGER = logging.getLogger(__name__)

class StethescopeController():
    def __init__(self):
        pass

if __name__ == "__main__":
    pass