# data_classifier.py
# Process and classify data

### Imports ###

# Built-ins
import logging
import threading
from time import sleep

# Third party imports
import bluetooth
import numpy as np
from scipy import fft,signal



### Globals ###
LOGGER = logging.getLogger("classifier")

class DataClassifier():
    def __init__(self, controller):
        self.controller = controller
        
    def find_packet(self):
        # While in receiving state look for new raw packet
        while self.controller.receive_data:
            if self.controller.ecg_data != None:
                LOGGER.info("find_packet (DataClassifier) recieved packet.")
                # Spawn thread to handle new packet
                handler = threading.Thread(target=self.data_stream, args=(self.controller.mic_data,self.controller.ecg_data))
                handler.start()
                self.controller.ecg_data = None 

            sleep(0.2)

    def data_stream(self,raw_mic,raw_ecg):

        print('Hi')

        # Filter data... 
        # ...
        # Find ECG peaks 
        # pk_locs = ecg_peaks(raw_ecg)
        # Average PCG waveform (based on ECG peaks)
        # ...
        # Extract features
        # ...
        # Classify
        # ... 
        # Update self.controller variables
        # ...

    # def ecg_peaks(self,raw_ecg):
        # Johnny's class/functions...




