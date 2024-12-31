'''
@File     : LocalNet.py
@Time     : 2024/12/31 14:11:05
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')

'''
本地网络配置
'''
# 起始字符串
START_STRING = 0xfabfb5da

# 数据顶端IP地址
DATA_HOST = '127.0.0.1'
# 数据顶端端口号
DATA_PORT = 60001

# 终端IP地址
TERMINAL_HOST = '127.0.0.1'
# 终端端口号
TERMINAL_PORT = 60002

# 节点IP地址
LOCAL_HOST = '127.0.0.1'
# 节点最小端口号
MIN_PORT = 60003
# 节点最大端口号
MAX_PORT = 69998

# 端口号生成器
def get_port():
    for port in range(MIN_PORT, MAX_PORT + 1):
        yield port
    else:
        raise ValueError('No available port')

LOCAL_PORT = get_port()


