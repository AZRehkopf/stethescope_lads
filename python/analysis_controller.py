# plotter.py
# Sends data to be plotted by the interface

### Imports ###

# Built-ins
import csv
import json
import logging
import os
import random
import socket
import sys
from time import sleep
import threading

# Third Party
import numpy
from scipy import fft, signal
import scipy.signal

### Globals ###

LOGGER = logging.getLogger("analysis")

class AnalysisController():
    def __init__(self, controller):
        self.controller = controller

        # Socket Parameters
        self.host = "127.0.0.1"
        self.port = 65534
        self.conn = None
        self.addr = None

        LOGGER.info("Analysis controller class initialized")

    def start_controller(self):
        LOGGER.info(f"Waiting for plotting connection")
        self.connect_to_data_socket()
        LOGGER.info(f"Connections established, waiting for interface signal to send data")
        
        while not self.controller.start_analysis:
            sleep(5)
        
        LOGGER.info(f"Sending data now")
        self.send_data()

    def connect_to_data_socket(self):
         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            try:
                tcp_socket.bind((self.host, self.port))
            except OSError:
                LOGGER.error("Could not connect")    
                sys.exit()
            tcp_socket.listen()
            self.conn, self.addr = tcp_socket.accept()

    def send_data(self):
        # Varaibles for opening the CSV files
        ecg_file = open(self.controller.ecg_file_name,'r')
        mic_file = open(self.controller.mic_file_name, 'r')
        ecg_reader = csv.reader(ecg_file)
        mic_reader = csv.reader(mic_file)
        
        # Variables for transmitting data to the interface to be graphed
        transmit_count = 0
        transmit_ecg_lst = []
        transmit_mic_lst = []

        # Variables for finding heart rate
        analysis_detect_count = 0
        analysis_detect_ecg_lst = []
        analysis_detect_mic_lst = []
        
        for ecg_row, mic_row in zip(ecg_reader, mic_reader):
            for ecg_value, mic_value in zip(ecg_row, mic_row):
                if ecg_value != '' and mic_value != '':
                    ecg_num = int(ecg_value)
                    mic_num = int(mic_value)
                    
                    transmit_ecg_lst.append(ecg_num)
                    transmit_mic_lst.append(mic_num)
                    transmit_count += 1
                    
                    analysis_detect_ecg_lst.append(ecg_num)
                    analysis_detect_mic_lst.append(mic_num)
                    analysis_detect_count += 1

                    if transmit_count == 400:
                        dec_ecg_list = numpy.rint(scipy.signal.decimate(transmit_ecg_lst, 20)).tolist()
                        dec_mic_list = numpy.rint(scipy.signal.decimate(transmit_mic_lst, 20)).tolist()
                        
                        payload = {
                        'ecg': dec_ecg_list, 
                        'mic': dec_mic_list
                        }

                        try:
                            self.conn.send(json.dumps(payload).encode())
                            sleep(0.11)
                        except KeyboardInterrupt:
                            LOGGER.info("User cancelled data transmission")
                            return
                        except BrokenPipeError:
                            LOGGER.info("User closed the interface")
                            return
                        
                        transmit_count = 0
                        transmit_mic_lst = []
                        transmit_ecg_lst = []

                    if analysis_detect_count == 20000:
                        analysis_raw_ecg_data = analysis_detect_ecg_lst.copy() 
                        analysis_raw_pcg_data = analysis_detect_mic_lst.copy() 
                        analysis_thread = threading.Thread(
                            target=self.controller.data_classifier_module.run_heart_sound_analysis, 
                            args=(
                                analysis_raw_ecg_data,
                                analysis_raw_pcg_data), 
                            daemon=True)
                        analysis_thread.start()

                        fft_thread = threading.Thread(
                            target=self.compute_fft, 
                            args=(
                                analysis_raw_pcg_data,), 
                            daemon=True)
                        fft_thread.start()
                        
                        analysis_detect_count = 0
                        analysis_detect_ecg_lst = []
                        analysis_detect_mic_lst = []

    def compute_fft(self, raw_mic_data):
        sleep(0.5)
        mic_np = numpy.array(raw_mic_data) # numpy variable
        
        # Compute FFT 
        mic_fft = fft.rfft(mic_np - mic_np.mean()) # remove mean before computing FFT
        mic_fft = 20 * numpy.log10(abs(mic_fft))
        mic_fft = mic_fft[0:4999]
        lst_mic_fft = mic_fft.tolist()
        lst_mic_fft.pop()
        dec_filt_fft_lst = numpy.rint(scipy.signal.decimate(lst_mic_fft, 5)).tolist()
        
        #print(dec_filt_fft_lst)
        #print(len(dec_filt_fft_lst))
        self.controller.interface.send_fft_graph(dec_filt_fft_lst)
        

if __name__ == "__main__":
    plotter = AnalysisController()
    plotter.start_controller()
    #plotter.send_data()