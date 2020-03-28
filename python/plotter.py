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
        while True:
            payload = {
                'ecg': self.controller.latest_ecg_value, 
                'mic': self.controller.latest_mic_value
            }
            
            try:
                self.conn.send(json.dumps(payload).encode())
            except BrokenPipeError:
                LOGGER.info("User closed the interface")
                return
            sleep(0.25)