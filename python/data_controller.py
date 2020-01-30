# data_controller.py
# Seperates and saves received data. Provides access to clean data for analysis

### Imports ###

# Built-ins
import csv
import logging
import os
import sys
import threading
from time import sleep

### Globals ###
LOGGER = logging.getLogger("data")

class DataController():
    def __init__(self, controller):
        self.controller = controller

        self.synced = False
        self.ecg_first = True
        self.hanging_ecg = None

        self.ecg_data = []
        self.mic_data = []

    def wait_for_raw_data(self):
        # While in receiving state look for new raw data
        while self.controller.receive_data:
            if self.controller.raw_data_stream != None:
                LOGGER.info("New raw data detected.")
                
                # Spawn thread to handle new raw data
                handler = threading.Thread(target=self.process_data, 
                                            args=(self.controller.raw_data_stream,))
                handler.start()
                self.controller.raw_data_stream = None

            sleep(0.2)

    def process_data(self, raw_data):
        # If this is the first stream of data received make sure sync bytes are present
        if not self.synced:
            if raw_data[0] != 65535:
                raise Exception("Sync bytes were not received")
            else:
                self.synced = True
                raw_data.pop(0)

        # Split the data streams 
        if not self.ecg_first:
            self.mic_data.append(raw_data.pop(0))

        if len(raw_data) % 2 != 0:
            self.ecg_first = False
            self.hanging_ecg = raw_data.pop()
        else:
            self.ecg_first = True

        for index in range(int(len(raw_data)/2)):
            self.ecg_data.append(raw_data[index*2])
            self.mic_data.append(raw_data[(index*2)+1])

        if self.hanging_ecg != None:
            self.ecg_data.append(self.hanging_ecg)
            self.hanging_ecg = None

        # Pass split data to the controller and reset
        self.controller.ecg_data = self.ecg_data
        self.controller.mic_data = self.mic_data

        self.save_data(self.mic_data,self.ecg_data)

        self.ecg_data = [] 
        self.mic_data = [] 

        LOGGER.info("Data processing complete")
    
    def save_data(self,mic,ecg): 
        with open(os.path.join(self.controller.data_dir, self.controller.ecg_file_name),'a') as ecg_file:
        	writer = csv.writer(ecg_file)
        	writer.writerow(ecg) 

        with open(os.path.join(self.controller.data_dir, self.controller.mic_file_name),'a') as mic_file:
        	writer = csv.writer(mic_file)
        	writer.writerow(mic) 