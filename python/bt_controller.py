# bt_controller.py
# Receives data from the ESP32 board

### Imports ###

# Built-ins
import logging
import os
import sys
from time import sleep

# Third party imports
import bluetooth

### Globals ###
LOGGER = logging.getLogger(__name__)

class BluetoothController():
    def __init__(self, controller):
        self.controller = controller
        
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
        LOGGER.info("Opening connection with the ESP32 device.")
        
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.socket.connect((self.mac_address, self.port))
        LOGGER.info("Ready to receive data.")

        # Sending byte commands transmitter to begin
        self.socket.send(b'1')

        byte_buffer = []
        carry = None 

        while self.controller.receive_data:
            # Get Data from bluetooth buffer
            try:
                data = self.socket.recv(1024)
            except ConnectionResetError:
                LOGGER.error("Lost connection with ESP32 device.")
                self.socket.close()
                self.controller.receive_data = False
                return

            parsed_data = bytes.hex(bytes(data))

            # Check if there was a carry over from the last set of values
            if carry != None:
                byte_buffer.append(int(carry+parsed_data[:4-len(carry)], 16))
                parsed_data = parsed_data[4-len(carry):]
                carry = None
            
            # Process received data
            for block in range(4,len(parsed_data)+1,4):
	            byte_buffer.append(int(parsed_data[block-4:block], 16))

            # Check if there are any incomplete sets of 4 bytes
            remainder = len(parsed_data) % 4
            if (remainder) != 0:
                carry = parsed_data[-remainder:]

            # Print every 10000 samples
            # Add code to save data to file here if necessary
            if len(byte_buffer) >= 10000:
                self.controller.raw_data_stream = byte_buffer
                byte_buffer = []

        # Command transmitter to stop transmitting         
        self.socket.send(b'0')
        self.socket.close()

if __name__ == "__main__":
    # Code for debugging this module
    test_controller = BluetoothController()
    test_controller.search_for_device()
    test_controller.connect_and_listen()