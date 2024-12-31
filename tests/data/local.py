'''
@File     : local.py
@Time     : 2024/12/30 18:47:47
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
from src.BlockChain.transaction import *
from src.BlockChain.block import *
from time import time
from random import randint
import hashlib

def json_output():
    return {
        'hash': hashlib.sha256(str(randint(1, 1000)).encode()).hexdigest(),
        'index': int(time()) % 9 + 1,
    }

def json_txin():
    return {
        'previous_output': outpoint(**json_output()),
        'signature_script': hashlib.sha256(hex(int(time()) // 2).encode()).digest(),
    }

def json_txout():
    return {
        'value': int(time()) % 59 + 1,
        'pk_script': hashlib.sha256(hex(int(time()) // 3).encode()).digest(),
    }

def json_transaction():
    return {
        'version': 1,
        'tx_in': [TxIn(**json_txin()) for _ in range(int(time()) % 9 + 1)],
        'tx_out': [TxOut(**json_txout()) for _ in range(int(time()) % 9 + 1)],
        'lock_time': int(time()) % 3 + 1,
    }

def json_block_header():
    return {
        'version': 1,
        'previous_block_header_hash': hashlib.sha256(hex(int(time()) // 5).encode()).hexdigest(),
        'merkle_root_hash': hashlib.sha256(hex(int(time()) // 7)[2:].encode()).hexdigest(),
        'time': int(time()),
    }

def json_block():
    return {
        'block_header': BlockHeader(**json_block_header()),
        'txns': [TRANSACTION(**json_transaction()) for _ in range(int(time()) % 3 + 1)],
    }


def json_merkle_block():
    return {
        'block_header': BlockHeader(**json_block_header()),
        'txns': [AuditMission(**json_ATM()), ] + [TRANSACTION(**json_transaction()) for _ in range(int(time()) % 4)],
    }

def json_ATM():
    return {
        'height': int(time()) % 99 + 1,
        'ATM_script': hashlib.sha256(hex(int(time()) // 11).encode()).digest(),
    }


if __name__ == '__main__':
    # print(outpoint(**json_output()))
    # print(TxIn(**json_txin()))
    # print(TxOut(**json_txout()))
    # print(TRANSACTION(**json_transaction()))
    # print(BlockHeader(**json_block_header()))
    # print(BLOCK(**json_block()))
    pass