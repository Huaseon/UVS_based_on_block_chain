'''
@File     : P2PNetwork.py
@Time     : 2024/12/28 22:07:07
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
import socket
import threading
from asyncio import LifoQueue

# 定义Peer类
class Peer(object):
    def __init__(self,
        IP_address: str,
        port: int,
        listen: int,
        sequence: LifoQueue
    ) -> None:
        if not self.ready_listen(IP_address=IP_address, port=port, listen=listen):
            raise Exception('Failed to initialize the listener.')
        self.sequence = sequence

    def ready_listen(self,
        IP_address: str,
        port: int,
        listen: int
    ) -> bool:
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.bind((IP_address, port))
        self.skt.listen(listen)
        return True

# 定义TransPeer类
# 需要实现一个responce方法，根据sequence中的数据进行响应

# 定义RecvPeer类
# 需要实现一个recv方法，接收数据并存入sequence