# data_preproc.py
# Process data from data_controller

### Imports ###

# Built-ins
import logging
import threading
from time import sleep

# Third party imports
import bluetooth
import numpy as np
from scipy import fft,signal

# Third party imports for testing
import matplotlib.pyplot as plt
import time

### Globals ###
LOGGER = logging.getLogger("preproc")

class DataPreproc():
    def __init__(self, controller):
        self.controller = controller
        
        # Filter Setup  (!!! make this an input in controller (i.e. 'user' defined) !!!)
        # ------------
        filt_len = 111 # order + 1
        fc = 50 # Cutoff frequency
        self.FS = 4000 # Sampling rate
        # Create filter 
        self.filt_b = signal.firwin(filt_len,fc,fs=self.FS)
        self.filt_a = 1 # since FIR filter
        # Filter initial conditions
        self.init_cond = signal.lfilter_zi(self.filt_b,self.filt_a)
        
    def find_packet(self):
        # While in receiving state look for new raw packet
        while self.controller.receive_data:
            if self.controller.mic_data != None:
                LOGGER.info("find_packet (DataPreproc) recieved packet.")
                # Spawn thread to handle new packet
                handler = threading.Thread(target=self.mic_packet, args=(self.controller.mic_data,))
                handler.start()
                self.controller.mic_data = None 

            sleep(0.2)

    def mic_packet(self,packet):
        # This code to process data
        mic_np = np.array(packet) # numpy variable
        LOGGER.info("mic_packet recieved packet. Data size: " + str(mic_np.size))

        # Compute FFT 
        mic_fft = fft.rfft(mic_np - mic_np.mean()) # remove mean before computing FFT

        # Filter (& update filter initial conditions for next packet)
        mic_filt, self.init_cond = signal.lfilter(self.filt_b,self.filt_a,mic_np,zi = self.init_cond)

        # FFT of filtered data
        mic_filt_fft = fft.rfft(mic_filt - mic_filt.mean()) # remove mean before computing FFT

        # Update controller
        # self.controller. ... 
        self.mic_fft = mic_fft
        self.mic_filt = mic_filt
        self.mic_filt_fft = mic_filt_fft


if __name__ == "__main__":
    # Code for debugging this module

    # Import data from computer
    data = np.loadtxt('/Users/joshbierbrier/Desktop/Fourth_Year/Capstone/python practice/14_01_2020__16_57_40.csv',delimiter=",")

    # Create class
    s_init_time = time.time()
    data_proc = DataPreproc(5) # arbitrary input
    e_init_time = time.time() # time to initialize filter
    print("init time: " + str(e_init_time-s_init_time))

    # Call data processing function
    s_filter_time = time.time()
    data_proc.mic_packet(data[0:20000])
    e_filter_time = time.time()
    print("filter time: " + str(e_filter_time-s_filter_time))


    # Plotting...
    # Plot FFT before and after filtering
    plt.figure(1)
    plt.subplot(211)
    # plt.plot(range(0,data_proc.mic_fft.size),np.abs(data_proc.mic_fft))
    plt.plot(range(0,data_proc.mic_fft.size),20 * np.log10(abs(data_proc.mic_fft)))
    plt.title("Raw FFT [dB]")
    plt.subplot(212)
    # plt.plot(range(0,data_proc.mic_filt_fft.size),np.abs(data_proc.mic_filt_fft))
    plt.plot(range(0,data_proc.mic_filt_fft.size),20 * np.log10(abs(data_proc.mic_filt_fft)))
    plt.title("Filtered FFT [dB]")
    plt.tight_layout()

    # Plot signal before and after filtering
    plt.figure(2)
    plt.subplot(211)
    plt.plot(range(0,20000),data[0:20000])
    plt.title("Raw Data")
    plt.subplot(212)
    plt.plot(range(0,data_proc.mic_filt.size),np.abs(data_proc.mic_filt))
    plt.title("Filtered Data")
    plt.tight_layout()
   
    # Plot filter info
    w, h = signal.freqz(data_proc.filt_b,data_proc.filt_a,fs = data_proc.FS)

    # plt.figure(2)
    fig, ax1 = plt.subplots()
    ax1.set_title('Digital filter frequency response')

    ax1.plot(w, 20 * np.log10(abs(h)), 'b')
    ax1.set_ylabel('Amplitude [dB]', color='b')
    ax1.set_xlabel('Frequency [rad/sample]')

    ax2 = ax1.twinx()
    angles = np.unwrap(np.angle(h))
    ax2.plot(w, angles, 'g')
    ax2.set_ylabel('Angle (radians)', color='g')
    ax2.grid()
    ax2.axis('tight')
    
    # Group Delay
    w,g = signal.group_delay((data_proc.filt_b,data_proc.filt_a),fs = data_proc.FS)
    plt.figure(4)
    plt.plot(w,np.round(g))
    plt.title("Group Delay (rounded to nearest integer)")

    plt.show()