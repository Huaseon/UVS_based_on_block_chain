'''
@File     : Msg.py
@Time     : 2024/12/31 14:14:25
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
from src.V.v1.CONFIG import *

# 定义消息报头类
class MessageHeader(object):
    def __init__(self,
        start_string: bytes | int,
        command_name: bytes,
        payload_size: int,
        checksum: bytes,
    ):
        self.checksum = checksum
        self.payload_size = payload_size
        self.command_name = command_name
        self.start_string = start_string if isinstance(start_string, bytes) else start_string.to_bytes(4, 'big')
    def serialize(self):
        return MESSAGE_HEADER_SERIALIZE.serialize(
            self.start_string,
            self.command_name,
            self.payload_size,
            self.checksum
        )
    
    def deserialize(self, data):
        start_string, command_name, payload_size, checksum, data = MESSAGE_HEADER_SERIALIZE.deserialize(data)
        self.start_string = start_string
        self.command_name = command_name
        self.payload_size = payload_size
        self.checksum = checksum

    def __str__(self):
        start_string = START_STRING_SERIALIZE.serialize(self.start_string).hex()
        command_name = COMMAND_NAME_SERIALIZE.serialize(self.command_name).hex()
        payload_size = PAYLOAD_SIZE_SERIALIZE.serialize(self.payload_size).hex()
        checksum = CHECKSUM_SERIALIZE.serialize(self.checksum).hex()
        return f'MessageHeader: {{\n\t"start_string:<char[4]>": {start_string},\n\t"command_name:<char[12]>": {command_name},\n\t"payload_size:<uint32_t>": {payload_size},\n\t"checksum:<char[4]>": {checksum}\n}}'
    
# 定义数据消息类（库存INVENTORY）
class INVENTORY(object):
    def __init__(self,
        type_identifier: int,
        hash: bytes,
    ):
        self.hash = hash
        self.type_identifier = type_identifier
    
    def serialize(self) -> bytes:
        return INVENTORY_SERIALIZE.serialize(
            self.type_identifier,
            self.hash
        )

    @staticmethod
    def deserialize(data: bytes) -> 'INVENTORY':
        type_identifier, hash, data = INVENTORY_SERIALIZE.deserialize(data)
        return INVENTORY(
            type_identifier=type_identifier,
            hash = hash
        ) if not data else (
            INVENTORY(
                type_identifier=type_identifier,
                hash = hash
            ),
            data
        )
    def __str__(self):
        type_identifier = TYPE_IDENTIFIER_SERIALIZE.serialize(self.type_identifier).hex()
        hash = HASH_SERIALIZE.serialize(self.hash).hex()
        return f'Inventory: {{\n\t"type_identifier:<uint32_t>": {type_identifier},\n\t"hash:<char[32]>": {hash}\n}}'
    

if __name__ == "__main__":
    # 模块测试
    from src.PeerToPeerNetwork.NetConf.LocalNet import *
    import hashlib
    msg_header = MessageHeader(
        start_string=START_STRING,
        command_name=b'block',
        payload_size=32,
        checksum=b'1234'
    )
    print(msg_header.serialize())
    print(msg_header)
    inv = INVENTORY(
        type_identifier=MSG_WITNESS_BLOCK,
        hash=hashlib.sha256(b'').digest()
    )
    print(inv)