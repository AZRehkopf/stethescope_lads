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
from scipy import signal

# For testing
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg') # for plotting...

### Globals ###
LOGGER = logging.getLogger("classifier")

class DataClassifier():
    def __init__(self, controller):
        self.controller = controller

        # Filter specs
        self.fc = 50 # Cutoff frequency
        self.filt_order = 12
        self.FS = 4000
        self.filt_coeffs = signal.butter(self.filt_order,self.fc,fs=self.FS,output='sos')
        
        # For test (plotting 'real-time')
        self.itr = 0
        
    def find_packet(self):
        # While in receiving state look for new raw packet
        while self.controller.receive_data:
            if self.controller.mic_data_slow != None:
                LOGGER.info("find_packet (DataClassifier) recieved packet.")
                # Spawn thread to handle new packet
                handler = threading.Thread(target=self.data_stream, args=(self.controller.mic_data_slow,self.controller.ecg_data_slow))
                handler.start()
                self.controller.mic_data_slow = None 

            sleep(0.2)

    def data_stream(self,raw_mic,raw_ecg):
        
        
        # print('Hi')
        # self.plotter_fn(raw_ecg) # testing purposes
        
        # Filter data... 
        mic_filt = signal.sosfiltfilt(self.filt_coeffs,raw_mic)

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

    def plotter_fn(self,data):
        # Plot
        dir_name = '/Users/joshbierbrier/Desktop/Fourth_Year/Capstone/test_plot_slow/'
        ax = []
        fig=plt.figure()
        ax.append(fig.add_subplot(1, 1, 1))
        ax[0].plot(data)
        plt.savefig(dir_name+'test'+str(self.itr),bbox_inches='tight',dpi=50)
        plt.close(fig)
        self.itr += 1
