# plotter.py
# Sends data to be plotted by the interface

### Imports ###

# Built-ins
import json
import logging
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

        self.mic_port = 65533
        self.mic_conn = None
        self.mic_addr = None

        self.ecg_port = 65534
        self.ecg_conn = None
        self.ecg_addr = None

    def start_plotter(self):
        LOGGER.info(f"Waiting for plotting connections")
        self.connect_to_ecg_socket()
        self.connect_to_mic_socket()

        LOGGER.info(f"Connections established, sending data")
        self.send_data()

    def connect_to_mic_socket(self):
         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            try:
                tcp_socket.bind((self.host, self.mic_port))
            except OSError:
                LOGGER.error("Could not connect")    
                sys.exit()
            tcp_socket.listen()
            self.mic_conn, self.mic_addr = tcp_socket.accept()

    def connect_to_ecg_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            try:
                tcp_socket.bind((self.host, self.ecg_port))
            except OSError:
                LOGGER.error("Could not connect")    
                sys.exit()
            tcp_socket.listen()
            self.ecg_conn, self.ecg_addr = tcp_socket.accept()

    def send_data(self):
        while True:
            self.mic_conn.send(str(random.randint(0,4094)).encode())
            self.ecg_conn.send(str(random.randint(0,4094)).encode())
            sleep(0.25)