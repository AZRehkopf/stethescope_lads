# steth_controller.py
# Coordinates all the digital stethescope components

### Imports ###

# Built-ins
import logging
import os
import sys
from time import sleep

# Local imports

# Third party imports
import bluetooth

### Globals ###
LOGGER = logging.getLogger(__name__)

class BluetoothController():
    def __init__(self):
        self.mac_address = None
        self.name = None
        
        self.socket = None
        self.port = 1

    def search_for_device(self):
        LOGGER.info("Searching for bluetooth devices...")
        detected_devices = bluetooth.discover_devices(lookup_names=True)

        if len(detected_devices) == 0:
            LOGGER.error("No devices were detected. Make sure the deivce is powered on.")
        else:
            count = 0
            target_device = None
            
            for device in detected_devices:
                if "ESP32" in device[1]:
                    count += 1
                    target_device = device
            
            if count == 0:
                LOGGER.error("No ESP32 devices were detected. Make sure the deivce is powered on.")
            elif count == 1:
                LOGGER.info("Device found.")
                self.mac_address = target_device[0].decode("utf-8")
                self.name = target_device[1]
            else:
                LOGGER.error("Multiple ESP32 devices were detected, no handling for this yet")

    def connect_and_listen(self):
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.connect((self.mac_address, self.port))
        
        byte_buffer = []
        carry = None 

        while True:
            data = self.socket.recv(32)
            parsed_data = bytes.hex(bytes(data))
            
            for block in range(2,len(parsed_data)+1,2):
	            byte_buffer.append(parsed_data[block-2:block])

            if len(byte_buffer) >= 10000:
                print(byte_buffer)
                byte_buffer = []
        
        self.socket.close()

if __name__ == "__main__":
    test_controller = BluetoothController()
    test_controller.search_for_device()
    print("connected")
    test_controller.connect_and_listen()