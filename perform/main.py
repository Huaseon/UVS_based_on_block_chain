'''
@File     : main.py
@Time     : 2025/01/03 20:01:22
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
from src.Client.Client import CLIENT
from perform.CONF.Local import *
import threading
import time
import random

if __name__ == '__main__':
    node_TOP = threading.Thread(
        target=CLIENT,
        kwargs=NODE_TOP
    )

    node_A = threading.Thread(
        target=CLIENT,
        kwargs=NODE_A
    )
    node_B = threading.Thread(
        target=CLIENT,
        kwargs=NODE_B
    )
    node_TOP.start()
    time.sleep(random.uniform(0.05, 1.0))
    node_A.start()
    time.sleep(random.uniform(0.05, 1.0))
    node_B.start()

