# data_controller.py
# Seperates and saves received data. Provides access to clean data for analysis

### Imports ###

# Built-ins
import logging
import os
import sys
import threading
from time import sleep

### Globals ###
LOGGER = logging.getLogger(__name__)

class DataController():
    def __init__(self, controller):
        self.controller = controller

        self.synced = False
        self.ecg_first = True
        self.hanging_ecg = None

        self.ecg_data = []
        self.mic_data = []

    def wait_for_raw_data(self):
        while self.controller.receive_data:
            if self.controller.raw_data_stream != None:
                handler = threading.Thread(target=self.process_data, 
                    args=(self.controller.raw_data_stream))
                handler.start()
                self.controller.raw_data_stream = None

            sleep(0.2)

    def process_data(self, raw_data):
        if not self.synced:
            if raw_data[0] != 65535:
                raise Exception("Sync bytes were not received")
            else:
                self.synced = True
                raw_data.pop(0)

        if not self.ecg_first:
            self.mic_data.append(raw_data.pop(0))

        if len(raw_data) % 2 != 0:
            self.ecg_first = False
            self.hanging_ecg = raw_data.pop()

        for index in range(len(raw_data)/2):
            self.ecg_data.append(raw_data[index*2])
            self.mic_data.append(raw_data[(index*2)+1])

        if self.hanging_ecg != None:
            self.ecg_data.append(self.hanging_ecg)
            self.hanging_ecg = None