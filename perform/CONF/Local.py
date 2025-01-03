'''
@File     : Local.py
@Time     : 2025/01/02 19:23:00
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')

# 顶端IP
TOP_IP = '127.0.0.1'
# 顶端端口
TOP_RECV_PORT = 60001
TOP_TRANS_PORT = 60002
# 客户端IP
CLIENT_IP = '127.0.0.1'

def PORT():
    for i in range(60003, 69999):
        yield i

CLIENT_PORT = PORT()

START_STRING = b'\xfa\xbf\xb5\xda'

VERSION_DEFAULT = 1

# TOP 服务 发起任务
SERVICES_TOP = 0x01 # 0b01
# A 服务 接收任务
SERVICES_A = 0x02 # 0b10
# B 服务 发起/接收任务
SERVICES_B = 0x03 # 0b11

# 测试用例
# 节点
NODE_TOP = {
    "start_string": START_STRING,
    "version": VERSION_DEFAULT,
    "client_services": SERVICES_A,
    "client_identifier": 0x00,
    "client_start_height": 1,
    "client_listen": 5,
    "recv_services": SERVICES_TOP,
    "recv_IP_address": TOP_IP,
    "recv_port": TOP_RECV_PORT,
    "trans_services": SERVICES_TOP,
    "trans_IP_address": TOP_IP,
    "trans_port": TOP_TRANS_PORT,
    "TOP_RECV_SERVICES": SERVICES_TOP,
    "TOP_RECV_IP_ADDRESS": TOP_IP,
    "TOP_RECV_PORT": TOP_RECV_PORT
}
NODE_A= {
    "start_string": START_STRING,
    "version": VERSION_DEFAULT,
    "client_services": SERVICES_A,
    "client_identifier": 0x01,
    "client_start_height": 1,
    "client_listen": 5,
    "recv_services": SERVICES_A,
    "recv_IP_address": CLIENT_IP,
    "recv_port": next(CLIENT_PORT),
    "trans_services": SERVICES_A,
    "trans_IP_address": CLIENT_IP,
    "trans_port": next(CLIENT_PORT),
    "TOP_RECV_SERVICES": SERVICES_TOP,
    "TOP_RECV_IP_ADDRESS": TOP_IP,
    "TOP_RECV_PORT": TOP_RECV_PORT
}

NODE_B= {
    "start_string": START_STRING,
    "version": VERSION_DEFAULT,
    "client_services": SERVICES_B,
    "client_identifier": 0x02,
    "client_start_height": 1,
    "client_listen": 5,
    "recv_services": SERVICES_B,
    "recv_IP_address": CLIENT_IP,
    "recv_port": next(CLIENT_PORT),
    "trans_services": SERVICES_B,
    "trans_IP_address": CLIENT_IP,
    "trans_port": next(CLIENT_PORT),
    "TOP_RECV_SERVICES": SERVICES_TOP,
    "TOP_RECV_IP_ADDRESS": TOP_IP,
    "TOP_RECV_PORT": TOP_RECV_PORT
}
