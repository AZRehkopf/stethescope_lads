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
from data_collection import BluetoothController
from data_controller import DataController
from data_preproc import DataPreproc
from interface_api import Interface_API
from peak_detector import PeakDetector
from plotter import Plotter

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
        LOGGER.info("Creating modules...")
        self.data_collection_module = BluetoothController(self) 
        self.data_preproc = DataPreproc(self)
        self.interface = Interface_API(self)
        self.peak_detector_module = PeakDetector(self)
        self.plot = Plotter(self)
        
        # General class variables
        self.child_threads = []
        self.data_dir = DATA_DIR
        self.ecg_file_name = None
        self.mic_file_name = None

        self.ecg_save_file_name = None
        self.mic_save_file_name = None
        self.target_save_data_dir = None

        # Control signals
        self.start_analysis = False
        self.enable_bt_search = False
        self.collect_bt_data = False
        
        # Data structures for shared information
        self.raw_data_stream = None
        self.ecg_data = None
        self.mic_data = None

    def start_listening(self):
        LOGGER.info("Spawning child threads...")
        interface_api_thread = threading.Thread(target=self.interface.connect_to_interface, daemon=True)
        interface_api_thread.start()

        plotting_thread = threading.Thread(target=self.plot.start_plotter, daemon=True) 
        plotting_thread.start()
        
        while True:
            while not self.enable_bt_search:
                sleep(2)
            result = self.data_collection_module.search_for_device()
            self.enable_bt_search = False

            if result:
                LOGGER.info("Connected to BT")
                self.interface.send_bt_status(result, DATA_DIR)
            else:
                LOGGER.info("Failed to connect to BT")
                self.interface.send_bt_status(result, DATA_DIR)
                continue

            while not self.collect_bt_data:
                if self.enable_bt_search: break
                sleep(2)

            if self.collect_bt_data:
                LOGGER.info("Collecting BT data now...")
                self.data_collection_module.connect_and_listen()
        
        LOGGER.info("Data pipe closed")

### Main ###

if __name__ == "__main__":
    # Code for testing the entire system
    stethescope = StethescopeController()
    
    try:
        stethescope.start_listening() 
    except KeyboardInterrupt:
        LOGGER.info("Listening stopped by user.")