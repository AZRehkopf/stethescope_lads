# bt_controller.py
# Receives data from the ESP32 board

### Imports ###

# Built-ins
import csv
import datetime
import logging
import os
import sys
from time import sleep

# Third party imports
import bluetooth

### File Checks ###
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOGGING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
if not os.path.isdir(LOGGING_DIR):
    os.mkdir(LOGGING_DIR)

if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)

### Globals ###

CONTROL_PACKET_SIZE = 1
DATA_PACKET_SIZE = 2

### Logging Configuration

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOGGING_DIR, 'python.log')),
        logging.StreamHandler(sys.stdout)
    ])

LOGGER = logging.getLogger("data_collection")


class BluetoothController():
    def __init__(self):
        self.mac_address = None
        self.name = None
        self.socket = None
        self.port = 1

        current_dt = datetime.datetime.now()
        self.ecg_file_name = current_dt.strftime("%Y%m%d_%H%M%S_raw_ecg_data.csv")
        self.mic_file_name = current_dt.strftime("%Y%m%d_%H%M%S_raw_mic_data.csv")

        self.ecg_list = []
        self.mic_list = []

    def search_for_device(self):
        LOGGER.info("Searching for bluetooth devices...")
        
        # Look for any nearby devices that are ready to pair
        detected_devices = bluetooth.discover_devices(lookup_names=True)

        # Look for the ESP32 device and connect if found
        if len(detected_devices) == 0:
            LOGGER.error("No devices were detected. Make sure the deivce is powered on.")
            sys.exit()
        else:
            count = 0
            target_device = None
            
            for device in detected_devices:
                if "ESP32" in device[1]:
                    count += 1
                    target_device = device
            
            if count == 0:
                LOGGER.error("No ESP32 devices were detected. Make sure the deivce is powered on.")
                sys.exit()
            elif count == 1:
                LOGGER.info("Device found.")
                self.mac_address = target_device[0].decode("utf-8")
                self.name = target_device[1]
                
                LOGGER.info("Opening connection with the ESP32 device.")
        
                self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.socket.connect((self.mac_address, self.port))
                LOGGER.info("Ready to receive data.")
            else:
                LOGGER.error("Multiple ESP32 devices were detected, no handling for this yet")
                sys.exit()

    def connect_and_listen(self):
        LOGGER.info("Starting data pipe...")

        # Sending byte commands transmitter to begin
        self.socket.send(b'1')
        
        self.aquire_lock()
        
        while True:
            try:
                self.get_samples()
                self.verify_locked()
                self.save_data()
            except KeyboardInterrupt:
                LOGGER.info("Data collection stopped by user")
                break

        LOGGER.info("Closing data pipe...")
        
        # Command transmitter to stop transmitting         
        self.socket.send(b'0')
        self.socket.close()

    def aquire_lock(self):
        LOGGER.info("Aquiring lock with ESP32 device...")
        while True:
            try:
                data = self.socket.recv(CONTROL_PACKET_SIZE)
            except ConnectionResetError:
                LOGGER.error("Unexepcted error while aquiring lock")
                self.socket.close()
                return 
            
            if data == bytearray(b'\xff'):
                LOGGER.info("Lock aquired")
                return

    def get_samples(self):
        parsed_ecg = None
        parsed_mic = None
        
        for _ in range(100):
            try:
                ecg_sample = self.socket.recv(DATA_PACKET_SIZE)
                if len(ecg_sample) < 2:
                    error = self.socket.recv(DATA_PACKET_SIZE - len(ecg_sample))
                    ecg_sample.extend(error)
                
                mic_sample = self.socket.recv(DATA_PACKET_SIZE)
                if len(mic_sample) < 2:
                    error = self.socket.recv(DATA_PACKET_SIZE - len(mic_sample))
                    mic_sample.extend(error)

            except ConnectionResetError:
                LOGGER.error("Unexepcted error while recieving data packets")
                self.socket.close()
                return 
            
            self.ecg_list.append(int(bytes.hex(bytes(ecg_sample)), base=16))
            self.mic_list.append(int(bytes.hex(bytes(mic_sample)), base=16))

    def verify_locked(self):
        try:
            data = self.socket.recv(CONTROL_PACKET_SIZE)
        except ConnectionResetError:
            LOGGER.error("Unexepcted error while aquiring lock")
            self.socket.close()
            return 
        
        if data != bytearray(b'\xff'):
            LOGGER.warning("Lock lost, reaquiring...")
            self.aquire_lock()

    def save_data(self): 
        with open(os.path.join(DATA_DIR, self.ecg_file_name),'a') as ecg_file:
        	writer = csv.writer(ecg_file)
        	writer.writerow(self.ecg_list) 

        with open(os.path.join(DATA_DIR, self.mic_file_name),'a') as mic_file:
        	writer = csv.writer(mic_file)
        	writer.writerow(self.mic_list)

        self.mic_list = []
        self.ecg_list = []

### Main ###

if __name__ == "__main__":
    bt_controller = BluetoothController()
    bt_controller.search_for_device()
    bt_controller.connect_and_listen()