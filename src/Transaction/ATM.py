'''
@File     : ATM.py
@Time     : 2024/12/31 14:03:34
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
import hashlib
from src.utils.data import compactSize
from src.V.v1.CONFIG import *


# 区块中第一笔交易为ATM交易
class AuditMission(object):
    def __init__(self,
        height: int,
        ATM_script: bytes
    ) -> None:
        self.sequence = SEQUENCE_DEFAULT
        self.ATM_script = ATM_script
        self.height = compactSize(height)
        self.script_bytes = compactSize(len(self.ATM_script) + len(self.height))
        if self.script_bytes > MAX_ATM_SCRIPT_SIZE:
            raise ValueError('Invalid ATM_script')
        self.index = INDEX_ON_ATM_DEFAULT
        self.hash = '00' * len(HASH_SERIALIZE)
    
    def serialize(self) -> bytes:
        return (HASH_SERIALIZE + INDEX_SERIALIZE).serialize(
            bytes.fromhex(self.hash),
            self.index
        ) + self.script_bytes.serialize() \
        + self.height.serialize() \
        + self.ATM_script \
        + SEQUENCE_SERIALIZE.serialize(self.sequence)
    
    @staticmethod
    def deserialize(data: bytes) -> 'AuditMission':
        hash, index, data = (HASH_SERIALIZE + INDEX_SERIALIZE).deserialize(data)
        if hash != b'\x00' * len(HASH_SERIALIZE):
            raise ValueError('Invalid data')
        if index != SEQUENCE_DEFAULT:
            raise ValueError('Invalid data')
        script_bytes, data = compactSize.deserialize(data)
        height, data = compactSize.deserialize(data)
        ATM_script, sequence, data = SERIALIZE(f'<{script_bytes - len(height)}sI').deserialize(data)
        if sequence != SEQUENCE_DEFAULT:
            raise ValueError('Invalid data')
        return AuditMission(
            height=int(height),
            ATM_script=ATM_script
        ) if not data else (
            AuditMission(
                height=int(height),
                ATM_script=ATM_script
            ), data
        )
    
    def _hash(self) -> str:
        return hashlib.sha256(
            self.serialize()
        ).hexdigest()

    def __str__(self):
        return f'Audit-Mission: {{\n\t"hash:<char[32]>": {self.hash},\n\t"index:<uint32_t>": {self.index},\n\t"script_bytes:<compactSize uint>": {int(self.script_bytes)},\n\t"height:<Varies>": {int(self.height)},\n\t"ATM_script:<binary|script>": {self.ATM_script},\n\t"sequence:<uint32_t>": {self.sequence}\n}}'

    def __len__(self) -> int:
        return len(self.serialize())
