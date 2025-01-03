'''
@File     : BLOCK.py
@Time     : 2024/12/29 09:07:16
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')

import hashlib
from typing import List
from src.utils.data import compactSize
from src.Transaction.transaction import TRANSACTION, AuditMission
from src.V.v1.CONFIG import *

# 定义区块类
class BLOCK(object):
    def __init__(self,
        block_header: 'BlockHeader',
        txns: List[TRANSACTION]
    ) -> None:
        self.txns = txns
        self.txn_count = compactSize(len(self.txns))
        self.block_header = block_header
        if len(self.block_header) != len(BLOCK_HEADER_SERIALIZE):
            raise ValueError('Invalid block_header')

    def serialize(self) -> bytes:
        return self.block_header.serialize() \
        + self.txn_count.serialize() \
        + b''.join([txn.serialize() for txn in self.txns])

    @staticmethod
    def deserialize(data: bytes) -> 'BLOCK':
        block_header, data = BlockHeader.deserialize(data)
        txn_count, data = compactSize.deserialize(data)
        txns = []
        for _ in range(txn_count - 1):
            txn, data = TRANSACTION.deserialize(data)
            txns.append(txn)
        else:
            _last = TRANSACTION.deserialize(data)
        
        return BLOCK(
            block_header=block_header,
            txns=txns + [_last]
        ) if isinstance(_last, TRANSACTION) else (
            BLOCK(
                block_header=block_header,
                txns=txns + [_last[0]]
            ), _last[-1]
        )
    
    def __len__(self) -> int:
        return len(self.serialize())
    
    def __str__(self) -> str:
        string_block_header = str(self.block_header).replace('\n', '\n\t')
        string_txns = ", ".join([str(txn).replace('\n', '\n\t\t') for txn in self.txns])
        string_txns = f'[\n\t\t{string_txns}\n\t]'
        return f'block: {{\n\t"block_header": {string_block_header},\n\t"txn_count": {self.txn_count},\n\t"txns": {string_txns}\n}}'   

# 定义区块头类
class BlockHeader(object):
    def __init__(self,
        previous_block_header_hash: str,
        merkle_root_hash: str,
        time: int,
        version: int = VERSION_DEFAULT,
    ) -> None:
        self.time = time
        self.merkle_root_hash = merkle_root_hash
        self.previous_block_header_hash = previous_block_header_hash
        self.version = version

    # 计算区块头哈希
    def _hash(self) -> str:
        return hashlib.sha256(
            self.serialize()
        ).hexdigest()

    # 序列化区块头
    def serialize(self) -> bytes:
        return BLOCK_HEADER_SERIALIZE.serialize(
            self.version,
            bytes.fromhex(self.previous_block_header_hash),
            bytes.fromhex(self.merkle_root_hash),
            self.time
        )
            
    # 反序列化区块头
    @staticmethod
    def deserialize(data: bytes) -> 'BlockHeader':
        version, previous_block_header_hash, merkle_root_hash, time, data = BLOCK_HEADER_SERIALIZE.deserialize(data)
        return BlockHeader(
            version=version,
            previous_block_header_hash=previous_block_header_hash.hex(),
            merkle_root_hash=merkle_root_hash.hex(),
            time=time
        ) if not data else (
            BlockHeader(
                version=version,
                previous_block_header_hash=previous_block_header_hash.hex(),
                merkle_root_hash=merkle_root_hash.hex(),
                time=time
            ), data
        )

    def __len__(self) -> int:
        return len(self.serialize())

    def __str__(self) -> str:
        return f'block header: {{\n\t"version:<uint332_t>": {self.version},\n\t"previous_block_header_hash:<char[32]>": {self.previous_block_header_hash}\n\t"merkle_root_hash:<char[32]>": {self.merkle_root_hash}\n\t"time:<uint32_t>": {self.time}\n}}'

# 定义默克尔树类
class MerkleTree(object):
    def __init__(self,
        txns: List[TRANSACTION],
    ) -> None:
        if len(txns) < 1 or not isinstance(txns[0], AuditMission):
            raise ValueError('Invalid txns')
        self.txns = [txns[0]]
        self.merkle_tree = [[1, self.txns[0]._hash(), self.txns[0]._hash()]]
        for txn in txns[1:]:
            self.update(txn)

    def update(self, tx: TRANSACTION) -> None:
        txid = tx._hash()
        
        if txid in self.merkle_tree[0]:
            return
        self.txns.append(tx)

        for _ in self.merkle_tree:
            if _[0] % 2 == 0:
                _ += [txid, txid]
            else:
                _[-1] = txid
            txid = self.pair_hash(*_[-2:])
            _[0] += 1
        else:
            self.merkle_tree.append([1, txid, txid])
        
    def root(self) -> str:
        return self.merkle_tree[-1][1]

    @staticmethod
    def pair_hash(a: str, b: str) -> str:
        return hashlib.sha256(
                bytes.fromhex(a) + bytes.fromhex(b)
        ).hexdigest()

    def __len__(self) -> int:
        return len(self.txns)

if __name__ == '__main__':
    # 模块测试代码
    pass