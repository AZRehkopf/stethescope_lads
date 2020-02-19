# steth_controller.py
# Coordinates all the digital stethescope components

### Imports ###

# Built-ins
import datetime
import logging
import os
import sys
import threading
from time import sleep

# Local imports
from bt_controller import BluetoothController
from data_controller import DataController
from data_preproc import DataPreproc

### Globals ###

LOGGING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

### File Checks ###

if not os.path.isdir(LOGGING_DIR):
    os.mkdir(LOGGING_DIR)

if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)

### Logging Configuration ###

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOGGING_DIR, 'python.log')),
        logging.StreamHandler(sys.stdout)
    ])

LOGGER = logging.getLogger("controller")

### Classes ###

class StethescopeController():
    def __init__(self):
        # Child modules for handling various components
        self.bluetooth_module = BluetoothController(self)
        self.data_module = DataController(self)
        self.data_preproc = DataPreproc(self)
        
        # General class variables
        self.child_threads = []
        self.data_dir = DATA_DIR
        self.ecg_file_name = None
        self.mic_file_name = None

        # Control signals
        self.receive_data = False
        
        # Data structures for shared information
        self.raw_data_stream = None
        self.ecg_data = None
        self.mic_data = None

    def start_listening(self):
        LOGGER.info("Beginning listening session...")
        self.receive_data = True
        
        # Generate file names for raw data
        current_dt = datetime.datetime.now()
        self.ecg_file_name = current_dt.strftime("%Y%m%d_%H%M%S_raw_ecg_data.csv")
        self.mic_file_name = current_dt.strftime("%Y%m%d_%H%M%S_raw_mic_data.csv")

        # Spawn thread for handling received data
        data_handling_thread = threading.Thread(target=self.data_module.wait_for_raw_data, 
                                                    daemon=True)
        data_handling_thread.start()
        self.child_threads.append(data_handling_thread)
        
        data_processing_thread = threading.Thread(target=self.data_preproc.find_packet,
                                                    daemon=True)
        data_processing_thread.start()
        self.child_threads.append(data_processing_thread)

        # Start bluetooth conection and data transfer
        self.bluetooth_module.search_for_device()
        self.bluetooth_module.connect_and_listen()

### Main ###

if __name__ == "__main__":
    # Code for testing the entire system
    stethescope = StethescopeController()
    
    try:
        stethescope.start_listening() 
    except KeyboardInterrupt:
        LOGGER.info("Listening stopped by user.")