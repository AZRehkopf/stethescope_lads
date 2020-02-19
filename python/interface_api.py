# interface_api.py
# Communicates with the user interface

### Imports ###

# Built-ins
import logging
import os
import socket
import sys

### Globals ###
LOGGER = logging.getLogger("interface_api")

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)])

### Classes ###

class Interface_API():
    def __init__(self, controller):
        self.controller = controller

        self.host = "127.0.0.1"
        self.port = 65535
        self.conn = None
        self.addr = None 

    def connect_to_interface(self):
        LOGGER.info(f"Waiting for connection on port {self.port}")
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            try:
                tcp_socket.bind((self.host, self.port))
            except OSError:
                LOGGER.error("Could not connect ")    
                sys.exit()
            tcp_socket.listen()
            self.conn, self.addr = tcp_socket.accept()

        LOGGER.info(f"Listening for requests from the interface on port {self.port}")
        while True:
                try:
                    data = self.conn.recv(1024)
                    data_string = data.decode("utf-8")
                    
                    print(data_string)
                except ConnectionResetError:
                    LOGGER.info("Lost connection with the interface exiting")
                    sys.exit()

### Main ###
if __name__ == "__main__":
    # Code for testing the interface apis
    api = Interface_API(None)
    api.connect_to_interface()
    