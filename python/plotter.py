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

### File Checks ###
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOGGING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
if not os.path.isdir(LOGGING_DIR):
    os.mkdir(LOGGING_DIR)

if not os.path.isdir(DATA_DIR):
    os.mkdir(DATA_DIR)

### Globals ###
LOGGER = logging.getLogger("plotter")
ECG_FILE_NAME = "/Users/zachariah/Documents/GitHub/stethescope_lads/data/20200330_153911_raw_ecg_data.csv"
MIC_FILE_NAME = "/Users/zachariah/Documents/GitHub/stethescope_lads/data/20200330_153911_raw_ecg_data_copy.csv"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOGGING_DIR, 'python.log')),
        logging.StreamHandler(sys.stdout)
    ])

LOGGER = logging.getLogger("data_collection")

class Plotter():
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 65534
        self.conn = None
        self.addr = None

    def start_plotter(self):
        LOGGER.info(f"Waiting for plotting connection")
        self.connect_to_data_socket()

        LOGGER.info(f"Connections established, sending data")
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
        ecg_file = open(ECG_FILE_NAME,'r')
        mic_file = open(MIC_FILE_NAME, 'r')
        ecg_reader = csv.reader(ecg_file)
        mic_reader = csv.reader(mic_file)
        
        sleep(5)
        
        for ecg_row, mic_row in zip(ecg_reader, mic_reader):
            count = 0
            mic_lst = []
            ecg_lst = []
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