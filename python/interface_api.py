# interface_api.py
# Communicates with the user interface

### Imports ###

# Built-ins
import datetime
import json
import logging
import os
import socket
import sys

### Globals ###
LOGGER = logging.getLogger("interface_api")

### Classes ###

class Interface_API():
    def __init__(self, controller):
        self.controller = controller

        self.host = "127.0.0.1"
        self.port = 65535
        self.conn = None
        self.addr = None 

        LOGGER.info("Interface class initialized")

    def connect_to_interface(self):
        LOGGER.info(f"Waiting for connection on port {self.port}")
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            try:
                tcp_socket.bind((self.host, self.port))
            except OSError:
                LOGGER.error("Could not connect")    
                sys.exit()
            tcp_socket.listen()
            self.conn, self.addr = tcp_socket.accept()

        LOGGER.info(f"Interface connection extablished, listening for requests")
        while True:
                try:
                    data = self.conn.recv(1024)
                    data_string = data.decode("utf-8")
                    
                    try:
                        parsed_data = json.loads(data_string)
                    except json.JSONDecodeError:
                        LOGGER.info("User closed the interface")
                        sys.exit()
                    
                    if parsed_data['cmd'] == 'start':
                        LOGGER.info("Start command recieved")
                        self.controller.ecg_file_name = parsed_data['ecg_file']
                        self.controller.mic_file_name = parsed_data['mic_file']
                        self.controller.start_analysis = True
                    elif parsed_data['cmd'] == 'stop':
                        LOGGER.info("Stop command recieved")
                    elif parsed_data['cmd'] == 'find_bt':
                        LOGGER.info("Find BT command recieved")
                        self.controller.enable_bt_search = True
                    elif parsed_data['cmd'] == 'start_bt':
                        LOGGER.info("Start BT collection command recieved")
                        self.controller.ecg_save_file_name = parsed_data['ecg_file']
                        self.controller.mic_save_file_name = parsed_data['mic_file']
                        self.controller.target_save_data_dir = parsed_data['data_fp']
                        self.controller.collect_bt_data = True
                    elif parsed_data['cmd'] == 'stop_bt':
                        LOGGER.info("Stop BT collection command recieved")
                        self.controller.collect_bt_data = False
                        
                except ConnectionResetError:
                    LOGGER.info("Lost connection with the interface exiting")
                    sys.exit()

    def send_bt_status(self, status, data_fp):
        current_dt = datetime.datetime.now()
        ecg_file_name = current_dt.strftime("%Y%m%d_%H%M%S_raw_ecg_data")
        mic_file_name = current_dt.strftime("%Y%m%d_%H%M%S_raw_mic_data")
        
        payload = {"cmd": "bt_stat", "status": status, "data_fp": data_fp, "ecg": ecg_file_name, "mic": mic_file_name}
        self.conn.send(json.dumps(payload).encode())

    def send_heart_rate(self, heart_rate):
        payload = {"cmd": "updt_hr", "hr": heart_rate}
        self.conn.send(json.dumps(payload).encode())

    def send_heart_sounds_classification(self, classification):
        payload = {"cmd": "updt_cls", "cls": classification}
        self.conn.send(json.dumps(payload).encode())

    def send_fft_graph(self, data):
        payload = {"cmd": "updt_fft", "fft": data}
        self.conn.send(json.dumps(payload).encode())

### Main ###
if __name__ == "__main__":
    # Code for testing the interface apis
    api = Interface_API(None)
    api.connect_to_interface()