# steth_controller.py
# Coordinates all the digital stethescope components

### Imports ###

# Built-ins
import logging
import os
import sys

# Local imports
from bt_controller import BluetoothController

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
        self.receive_data = True
        self.bluetooth_module = BluetoothController(self)

    def start_listening(self):
        LOGGER.info("Beginning listening session...")
        self.bluetooth_module.search_for_device()
        self.bluetooth_module.connect_and_listen()

if __name__ == "__main__":
    stethescope = StethescopeController()
    stethescope.start_listening()