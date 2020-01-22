# steth_controller.py
# Coordinates all the digital stethescope components

### Imports ###

# Built-ins
import logging
import os
import sys
import threading

# Local imports
from bt_controller import BluetoothController
from data_controller import DataController

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
        self.bluetooth_module = BluetoothController(self)
        self.data_module = DataController(self)
        
        self.child_threads = []
        self.receive_data = True
        self.raw_data_stream = None

    def start_listening(self):
        LOGGER.info("Beginning listening session...")
        self.bluetooth_module.search_for_device()
        
        bt_listening_thread = threading.Thread(target=self.bluetooth_module.connect_and_listen, daemon=True)
        bt_listening_thread.start()
        self.child_threads.append(bt_listening_thread)

if __name__ == "__main__":
    stethescope = StethescopeController()
    try:
        stethescope.start_listening()
        for thread in stethescope.child_threads:
            thread.join()
            
    except KeyboardInterrupt:
        LOGGER.info("Listening stopped by user.")