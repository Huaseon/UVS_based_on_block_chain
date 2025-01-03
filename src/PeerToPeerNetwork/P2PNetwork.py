'''
@File     : P2PNetwork.py
@Time     : 2024/12/28 22:07:07
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
import socket
from asyncio import LifoQueue, run
import logging

# 定义Peer类
class Peer(object):
    def __init__(self,
        name: str,
        IP_address: str,
        port: int,
        listen: int,
        sequence: LifoQueue
    ) -> None:
        if not self.ready_listen(name=name, IP_address=IP_address, port=port, listen=listen):
            raise Exception('Failed to initialize the listener.')
        self.sequence = sequence

    def ready_listen(self,
        name: str,
        IP_address: str,
        port: int,
        listen: int
    ) -> bool:
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.bind((IP_address, port))
        self.skt.listen(listen)
        self.logger = logging.getLogger(name=name)
        self.logger.info(f'Listening on {IP_address}:{port}')
        return True

# 定义TransPeer类
# 需要实现一个responce方法，根据sequence中的数据进行响应
class TransPeer(Peer):
    def __init__(self,
        name: str,
        IP_address: str,
        port: int,
        listen: int,
        mesSequence: LifoQueue,
        actSequence: LifoQueue,
    ) -> None:
        super().__init__(name=name, IP_address=IP_address, port=port, listen=listen, sequence=mesSequence)
        self.actSequence = actSequence
        run(self.responce())
    
    async def responce(self):
        while True:
            data, addr = self.sequence.get()
            message = MSG.deserialize(data)
            self.logger.info(f'Received a message from {addr}, and the message is {message}')
            res = message.responce(addr)
            if isinstance(res, tuple):
                self.skt.connect(res[0])
                self.skt.sendall(res[1])
                self.skt.close()
                self.logger.info(f'Sent a {len(res[1])}.L.message. to {res[0]}')
            else:
                self.actSequence.put_nowait(res)
                self.logger.info(f'Put a {len(res)}.L.message into the actSequence')
            



# 定义RecvPeer类
# 需要实现一个recv方法，接收数据并存入sequence
class RecvPeer(Peer):
    def __init__(self,
        name: str,
        IP_address: str,
        port: int,
        listen: int,
        mesSequence: LifoQueue
    ) -> None:
        super().__init__(name=name, IP_address=IP_address, port=port, listen=listen, sequence=mesSequence)
        run(self.recv())
        
    async def recv(self):
        while True:
            conn, addr = self.skt.accept()
            data = b''
            self.logger.info(f'Received a connection from {addr}')
            while _:=conn.recv(1024):
                data += _
            else:
                self.sequence.put_nowait((data, addr))
                conn.close()
                self.logger.info(f'Received a {len(data)}.L.message from {addr}')

# class Action(object):
#     def __init__(self, data: bytes) -> None:
#         self.data = data
#         self.data_header, data = 

#     def act(self, client) -> None:
#         pass