'''
@File     : CONF.py
@Time     : 2024/12/31 14:07:09
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
from src.utils.data import SERIALIZE
from hashlib import sha256

# Headers消息中的交易计数（后缀）
TX_COUNT_ON_HEADERS_SERIALIZE = SERIALIZE('<B')
TX_COUNT_ON_HEADERS = 0x00

# Payload为空
EMPTY_PAYLOAD = b''





