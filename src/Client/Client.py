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
from src.PeerToPeerNetwork.Msg import Version, PAYLOAD
from src.PeerToPeerNetwork.P2PNetwork import Peer, RecvPeer, TransPeer
from src.PeerToPeerNetwork.NetConf.Global import IDENTIFIER_SERIALIZE
from hashlib import sha256
from asyncio import LifoQueue, run
import logging
logging.basicConfig(filename='logs/logs.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf8')

class CLIENT(object):
    def __init__(self,
        start_string: bytes | int, version: int, client_services: int, 
        client_identifier: int, client_start_height: int, client_listen: int | tuple,
        recv_services: int, recv_IP_address: str, recv_port: int,
        trans_services: int, trans_IP_address: str, trans_port: int
    ) -> None:
        if not self.ready(
            start_string=start_string, version=version, client_services=client_services,
            client_identifier=client_identifier, client_start_height=client_start_height, client_listen=client_listen,
            recv_services=recv_services, recv_IP_address=recv_IP_address, recv_port=recv_port,
            trans_services=trans_services, trans_IP_address=trans_IP_address, trans_port=trans_port
        ):
            raise Exception('Failed to initialize the client.')
        self.logger.info('Client is ready.')
        run(self.act())

    def ready(self,
        start_string: bytes | int, version: int, client_services: int, 
        client_identifier: int, client_start_height: int, client_listen: int | tuple,
        recv_services: int, recv_IP_address: str, recv_port: int,
        trans_services: int, trans_IP_address: str, trans_port: int
    ) -> bool:
        if not self.ready_state(
            start_string=start_string, version=version, client_services=client_services,
            identifier=client_identifier, start_height=client_start_height, recv_services=recv_services,
            recv_IP_address=recv_IP_address, recv_port=recv_port, trans_services=trans_services,
            trans_IP_address=trans_IP_address, trans_port=trans_port
        ):
            return False
        
        if not self.ready_recv(
            listen=client_listen
        ):
            return False
        
        if not self.ready_trans(
            listen=client_listen
        ):
            return False

        return True

    async def act(self) -> None:
        while True:
            data: bytes = self.actSequence.get()
            payload = PAYLOAD.toPayload(data)
            payload, data = payload if not isinstance(payload, tuple) else (payload, b'')
            if data:
                self.logger.warning(f'Received a payload with more {len(data)}.L.bytes')
            payload.act(self)
            self.logger.info(f'Received a action: {data.hex()}')

    def ready_state(self,
        start_string: bytes | int, version: int, client_services: int,
        identifier: int, start_height: int, recv_services: int,
        recv_IP_address: str, recv_port: int, trans_services: int,
        trans_IP_address: str, trans_port: int
    ) -> bool:
        self.actSequence = LifoQueue()
        self.mesSequence = LifoQueue()
        self.logger = logging.getLogger(name=IDENTIFIER_SERIALIZE.serialize(identifier).hex())
        self.version = Version(
            start_string=start_string,
            version=version,
            services=client_services,
            timestamp=int(time()),
            addr_recv_services=recv_services,
            addr_recv_IP_address=recv_IP_address,
            addr_recv_port=recv_port,
            addr_trans_services=trans_services,
            addr_trans_IP_address=trans_IP_address,
            addr_trans_port=trans_port,
            identifier=identifier,
            start_height=start_height
        )
        return True

    def ready_recv(self,
            listen: int | tuple[int, int]
        ) -> bool:
        self.recv = RecvPeer(
            identifier=self.logger.name + ':recv',
            IP_address=self.version.payload.addr_recv_IP_address,
            port=self.version.payload.addr_recv_port,
            listen=listen if isinstance(listen, int) else listen[0],
            mesSequence=self.mesSequence
        )
        return True
    
    def ready_trans(self,
            listen: int | tuple[int, int]
    ) -> bool:
        self.trans = TransPeer(
            identifier=self.logger.name + ':trans',
            IP_address=self.version.payload.addr_trans_IP_address,
            port=self.version.payload.addr_trans_port,
            listen=listen if isinstance(listen, int) else listen[-1],
            mesSequence=self.mesSequence,
            actSequence=self.actSequence
        )
        return True


    