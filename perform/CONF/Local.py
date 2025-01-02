'''
@File     : Local.py
@Time     : 2025/01/02 19:23:00
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
import socket

# 顶端IP
TOP_IP = '127.0.0.1'
# 顶端端口
TOP_PORT = 60001

# 

# 顶端
class TOP(object):
    def __init__(self):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.connect((TOP_IP, TOP_PORT))
    
    def listen(self):
        self.skt.listen(5)
        while True:
            data = self.skt.recv(1024)
            print(data)