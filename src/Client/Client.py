'''
@File     : Client.py
@Time     : 2025/01/02 17:57:16
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
import socket
from time import time
from src.PeerToPeerNetwork.Msg import Version
from hashlib import sha256
import threading
import logging
logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf8')

class CLIENT(object):
    def __init__(self,
        client_start_string: bytes | int, client_version: int, client_services: int,
        client_recv_IP_address: str, client_recv_port: int, client_trans_IP_address: str,
        client_trans_port: int, client_nonce: int, client_start_height: int, client_listen: int | tuple
    ) -> None:
        if not self.ready_log(name=str(client_nonce)):
            raise Exception('Failed to initialize the logger.')
        self.logger.info(f'Initializing the client with {client_nonce}...')
        if not self.ready_recv(
            recv_IP_address=client_recv_IP_address, 
            recv_port=client_recv_port, listen=client_listen
        ):
            raise Exception('Failed to initialize the receiver.')
        self.logger.info(f'Initializing the receiver with {client_nonce}...')
        if not self.ready_trans(
            trans_IP_address=client_trans_IP_address,
            trans_port=client_trans_port, listen=client_listen
        ):
            raise Exception('Failed to initialize the transmitter.')
        self.logger.info(f'Initializing the transmitter with {client_nonce}...')
        if not self.ready_version(
            start_string=client_start_string, version=client_version, services=client_services,
            timestamp=int(time()), addr_recv_services=client_services, addr_recv_IP_address=client_recv_IP_address,
            addr_recv_port=client_recv_port, addr_trans_services=client_services, addr_trans_IP_address=client_trans_IP_address,
            addr_trans_port=client_trans_port, nonce=client_nonce, start_height=client_start_height
        ):
            raise Exception('Failed to initialize the version.')
        self.logger.info(f'Initializing the version with {client_nonce}...')
        if not self.ready_state():
            raise Exception('Failed to initialize the state.')
        self.logger.info(f'Initializing the state with {client_nonce}...')
        self.receiver = threading.Thread(target=self.recving)
        self.receiver.start()
        
    
    def ready_log(self, name: str):
        self.logger = logging.getLogger(name=name)
        self.logger.info(f'Initializing the logger for {name}')

        self.recv_logger = logging.getLogger(name=f'{name}:recv')
        self.recv_logger.info(f'Initializing the logger for {name}:recv')
        
        self.trans_logger = logging.getLogger(name=f'{name}_trans')
        self.trans_logger.info(f'Initializing the logger for {name}_trans')
        
        return True

    def ready_recv(self,
        recv_IP_address: str,
        recv_port: int,
        listen: int | tuple[int, int]
    ):
        self.recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv.bind((recv_IP_address, recv_port))
        self.recv.listen(listen if isinstance(listen, int) else listen[0])
        self.recv_logger.info(f'Listening on {recv_IP_address}:{recv_port}')

        return True

    def ready_trans(self,
        trans_IP_address: str,
        trans_port: int,
        listen: int | tuple[int, int]                
    ):
        self.trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.trans.bind((trans_IP_address, trans_port))
        self.trans.listen(listen if isinstance(listen, int) else listen[-1])
        self.trans_logger.info(f'Listening on {trans_IP_address}:{trans_port}')
        return True
    
    def ready_version(self,
        start_string: bytes | int, version: int, services: int, 
        timestamp: int, addr_recv_services: int, addr_recv_IP_address: str,
        addr_recv_port: int, addr_trans_services: int, addr_trans_IP_address: str,
        addr_trans_port: int, nonce: int, start_height: int
    ):
        self.version = Version(
            start_string=start_string,
            version=version,
            services=services,
            timestamp=timestamp,
            addr_recv_services=addr_recv_services,
            addr_recv_IP_address=addr_recv_IP_address,
            addr_recv_port=addr_recv_port,
            addr_trans_services=addr_trans_services,
            addr_trans_IP_address=addr_trans_IP_address,
            addr_trans_port=addr_trans_port,
            nonce=nonce,
            start_height=start_height
        )
        self.logger.info(f'Version: {self.version}')
        return True
    
    def ready_state(self):
        self.messages = []
        return True

    def recving(self):
        while True:
            conn, addr = self.recv.accept()
            self.recv_logger.info(f'Connected by {addr}')
            data = b''
            while _:=conn.recv(1024):
                data += _
            else:
                self.messages.append(data)
            self.recv_logger.info(f'Received: {len(data)}_bytes')
            conn.close()
    
    def response(self):
        while True:
            while not len(self.messages):
                pass
            message = self.messages.pop()
            
            if self.messages:
                data = self.messages.pop(0)
        pass
