# plotter.py
# Sends data to be plotted by the interface

### Imports ###

# Built-ins
import csv
import json
import logging
import numpy
import scipy.signal
import os
import random
import socket
import sys
from time import sleep

### Globals ###
LOGGER = logging.getLogger("plotter")

class Plotter():
    def __init__(self, controller):
        self.controller = controller

        self.host = "127.0.0.1"
        self.port = 65534
        self.conn = None
        self.addr = None

    def start_plotter(self):
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
        ecg_file = open(self.controller.ecg_file_name,'r')
        mic_file = open(self.controller.mic_file_name, 'r')
        ecg_reader = csv.reader(ecg_file)
        mic_reader = csv.reader(mic_file)
        
        count = 0
        mic_lst = []
        ecg_lst = []
        
        for ecg_row, mic_row in zip(ecg_reader, mic_reader):
            for ecg_value, mic_value in zip(ecg_row, mic_row):
                if ecg_value != '' and mic_value != '':
                    ecg_lst.append(int(ecg_value))
                    mic_lst.append(int(mic_value))
                    count += 1

                    if count == 400:
                        dec_ecg_list = numpy.rint(scipy.signal.decimate(ecg_lst, 20)).tolist()
                        dec_mic_list = numpy.rint(scipy.signal.decimate(mic_lst, 20)).tolist()
                        
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
                        
                        count = 0
                        mic_lst = []
                        ecg_lst = []

            
if __name__ == "__main__":
    plotter = Plotter()
    plotter.start_plotter()
    #plotter.send_data()