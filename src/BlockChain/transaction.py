'''
@File     : Transaction.py
@Time     : 2024/12/28 22:06:33
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import hashlib
import sys
sys.path.append('.')
from typing import List
from src.utils.data import compactSize
from src.BlockChain.v1.CONFIG import *

# 定义交易类
class TRANSACTION(object):
    def __init__(self,
        tx_in: List['TxIn'],
        tx_out: List['TxOut'],
        lock_time: int,
        version: int = VERSION_DEFAULT,
    ) -> None:
        self.lock_time = lock_time
        if self.lock_time < 0:
            raise ValueError('Invalid lock_time')
        self.tx_out = tx_out
        self.tx_out_count = compactSize(len(self.tx_out))
        self.tx_in = tx_in
        self.tx_in_count = compactSize(len(self.tx_in))
        self.version = version

    def serialize(self) -> bytes:
        return VERSION_SERIALIZE.serialize(self.version) \
            + self.tx_in_count.serialize() \
            + b''.join([tx_in.serialize() for tx_in in self.tx_in]) \
            + self.tx_out_count.serialize() \
            + b''.join([tx_out.serialize() for tx_out in self.tx_out]) \
            + LOCK_TIME_SERIALIZE.serialize(self.lock_time)
    
    @staticmethod
    def deserialize(data: bytes) -> 'TRANSACTION':
        version, data = VERSION_SERIALIZE.deserialize(data)
        tx_in_count, data = compactSize.deserialize(data)
        tx_in = []
        for _ in range(tx_in_count):
            txin, data = TxIn.deserialize(data)
            tx_in.append(txin)
        tx_out_count, data = compactSize.deserialize(data)
        tx_out = []
        for _ in range(tx_out_count):
            txout, data = TxOut.deserialize(data)
            tx_out.append(txout)
        lock_time, data = LOCK_TIME_SERIALIZE.deserialize(data)
        return TRANSACTION(
            version=version,
            tx_in=tx_in,
            tx_out=tx_out,
            lock_time=lock_time,
        ) if not data else (
            TRANSACTION(
                version=version,
                tx_in=tx_in,
                tx_out=tx_out,
                lock_time=lock_time,
            ), data
        )
    
    def __str__(self) -> str:
        string_tx_in = [str(txin).replace("\n", "\n\t\t") for txin in self.tx_in]
        string_tx_in = f'[\n\t\t{", ".join(string_tx_in)}\n\t]'
        string_tx_out = [str(txout).replace("\n", "\n\t\t") for txout in self.tx_out]
        string_tx_out = f'[\n\t\t{", ".join(string_tx_out)}\n\t]'
        return f'transaction: {{\n\t"version:<uint32_t>": {self.version},\n\t"tx_in_count:<compactSize uint>": {self.tx_in_count},\n\t"tx_in:<List[TxIn]>": {string_tx_in},\n\t"tx_out_count:<compactSize uint>": {self.tx_out_count},\n\t"tx_out:<List[TxOut]>": {string_tx_out},\n\t"lock_time:<uint32_t>": {self.lock_time}\n}}'

    def _hash(self) -> str:
        return hashlib.sha256(
            self.serialize()
        ).hexdigest()

    def __len__(self) -> int:
        return len(self.serialize())

# 定义交易输入类
class TxIn(object):
    def __init__(self,
        previous_output: 'outpoint',
        signature_script: bytes,
    ) -> None:
        self.sequence = SEQUENCE_DEFAULT
        self.signature_script = signature_script
        self.script_bytes = compactSize(len(signature_script))
        if self.script_bytes > MAX_SIGNATURE_SCRIPT_SIZE:
            raise ValueError('Invalid signature_script')
        self.previous_output = previous_output
    
    def serialize(self) -> bytes:
        return self.previous_output.serialize() \
        + self.script_bytes.serialize() \
        + self.signature_script \
        + SEQUENCE_SERIALIZE.serialize(self.sequence)
    
    @staticmethod
    def deserialize(data: bytes) -> 'TxIn':
        previous_output, data = outpoint.deserialize(data)
        script_bytes, data = compactSize.deserialize(data)
        signature_script, data = data[:script_bytes], data[script_bytes:]
        if script_bytes != len(signature_script):
            raise ValueError('Invalid data')
        sequence, data = SEQUENCE_SERIALIZE.deserialize(data)
        if sequence != SEQUENCE_DEFAULT:
            raise ValueError('Invalid data')
        return TxIn(
            previous_output=previous_output,
            signature_script=signature_script,
        ) if not data else (
            TxIn(
                previous_output=previous_output,
                signature_script=signature_script
            ), data
        )
    
    def __str__(self) -> str:
        string_previous_output = str(self.previous_output).replace('\n', '\n\t')
        return f'TxIn: {{\n\t"previous_output:<outpoint>": {string_previous_output},\n\t"script_bytes:<compactSize uint>": {int(self.script_bytes)},\n\t"signature_script:<binary|script>": {self.signature_script},\n\t"sequence:<uint32_t>": {self.sequence}\n}}'

    def _hash(self) -> str:
        return hashlib.sha256(
            self.serialize()
        ).hexdigest()

    def __len__(self) -> int:
        return len(self.serialize())

# 定义特定输出类
class outpoint(object):
    def __init__(self,
        hash: str,
        index: int
    ) -> None:
        self.index = index
        self.hash = hash
    
    def serialize(self) -> bytes:
        return OUTPOINT_SERIALIZE.serialize(
            bytes.fromhex(self.hash),
            self.index
        )
    
    @staticmethod
    def deserialize(data: bytes) -> 'outpoint':
        hash, index, data = OUTPOINT_SERIALIZE.deserialize(data)
        return outpoint(
            hash=hash.hex(),
            index=index
        ) if not data else (
            outpoint(
                hash=hash.hex(),
                index=index
            ), data
        )
    
    def __str__(self):
        return f'outpoint: {{\n\t"hash:<char[32]>": {self.hash},\n\t"index:<uint32_t>": {self.index}\n}}'

    def _hash(self) -> str:
        return hashlib.sha256(
            self.serialize()
        ).hexdigest()

    def __len__(self) -> int:
        return len(self.serialize())

# 定义交易输出类
class TxOut(object):
    def __init__(self,
        value: int,
        pk_script: bytes
    ) -> None:
        self.pk_script = pk_script
        self.pk_script_bytes = compactSize(len(pk_script))
        if self.pk_script_bytes > MAX_PK_SCRIPT_SIZE:
            raise ValueError('Invalid pk_script')
        self.value = value
        if self.value < 0:
            raise ValueError('Invalid value')

    def serialize(self) -> bytes:
        return VALUE_SERIALIZE.serialize(self.value) \
        + self.pk_script_bytes.serialize() + self.pk_script
    
    @staticmethod
    def deserialize(data: bytes) -> 'TxOut':
        value, data = VALUE_SERIALIZE.deserialize(data)
        pk_script_bytes, data = compactSize.deserialize(data)
        pk_script, data = data[:pk_script_bytes], data[pk_script_bytes:]
        if pk_script_bytes != len(pk_script):
            raise ValueError('Invalid pk_script')
        return TxOut(
            value=value,
            pk_script=pk_script
        ) if not data else (
            TxOut(
                value=value,
                pk_script=pk_script
            ), data
        )
    
    def __str__(self):
        return f'TxOut: {{\n\t"value:<uint64_t>": {self.value},\n\t"pk_script_bytes:<compactSize>": {int(self.pk_script_bytes)},\n\t"pk_script:<binary|script>": {self.pk_script}\n}}'

    def _hash(self) -> str:
        return hashlib.sha256(
            self.serialize()
        ).hexdigest()
    
    def __len__(self) -> int:
        return len(self.serialize())

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

if __name__ == '__main__':
    # 模块测试代码
    # 创建一个交易输入
    previous_output = outpoint(hash='00' * 32, index=0)
    signature_script = b'\x01\x02\x03'
    tx_in = TxIn(previous_output, signature_script)

    # 创建一个交易输出
    value = 50
    pk_script = b'\x04\x05\x06'
    tx_out = TxOut(value, pk_script)

    # 创建一个交易
    transaction = TRANSACTION(
        tx_in=[tx_in],
        tx_out=[tx_out],
        lock_time=0
    )

    # 序列化交易
    serialized_transaction = transaction.serialize()
    print(f'Serialized Transaction: {serialized_transaction.hex()}')

    # 反序列化交易
    deserialized_transaction = TRANSACTION.deserialize(serialized_transaction)
    print(f'Deserialized Transaction: {deserialized_transaction}')

    # 创建一个ATM交易
    height = 100
    ATM_script = b'\x07\x08\x09'
    audit_mission = AuditMission(height, ATM_script)

    # 序列化ATM交易
    serialized_audit_mission = audit_mission.serialize()
    print(f'Serialized Audit Mission: {serialized_audit_mission.hex()}')

    # 反序列化ATM交易
    deserialized_audit_mission = AuditMission.deserialize(serialized_audit_mission)
    print(f'Deserialized Audit Mission: {deserialized_audit_mission}')
    
    
