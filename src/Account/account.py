'''
@File     : Account.py
@Time     : 2024/12/29 09:06:50
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
from src.Account.CONF.Global import *

# 定义分层确定性账户
class HierarchicalDeterministicAccount(object):
    def __init__(self,
        key_version: bytes,
        depth: int,
        parent_fingerprint: bytes,
        child_number: bytes,
        chain_code: bytes,
        key: bytes
    ) -> None:
        self.key = key
        self.chain_code = chain_code
        self.child_number = child_number
        self.parent_fingerprint = parent_fingerprint
        self.depth = depth
        self.key_version = key_version

    def serialize(self) -> bytes:
        key_version = KEY_VERSION_SERIALIZE.serialize(self.key_version)
        depth = DEPTH_SERIALIZE.serialize(self.depth)
        parent_fingerprint = PARENT_FINGERPRINT_SERIALIZE.serialize(self.parent_fingerprint)
        child_number = CHILD_NUMBER_SERIALIZE.serialize(self.child_number)
        chain_code = CHAIN_CODE_SERIALIZE.serialize(self.chain_code)
        key = KEY_SERIALIZA.serialize(self.key)
        return key_version + depth + parent_fingerprint + child_number + chain_code + key
    
    @staticmethod
    def deserialize(data: bytes):
        key_version, data = KEY_VERSION_SERIALIZE.deserialize(data)
        depth, data = DEPTH_SERIALIZE.deserialize(data)
        parent_fingerprint, data = PARENT_FINGERPRINT_SERIALIZE.deserialize(data)
        child_number, data = CHILD_NUMBER_SERIALIZE.deserialize(data)
        chain_code, data = CHAIN_CODE_SERIALIZE.deserialize(data)
        key, data = KEY_SERIALIZA.deserialize(data)
        return HierarchicalDeterministicAccount(key_version, depth, parent_fingerprint, child_number, chain_code, key)

    def __str__(self) -> str:
        key_version = self.key_version.hex()
        depth = DEPTH_SERIALIZE.serialize(self.depth).hex()
        parent_fingerprint = self.parent_fingerprint.hex()
        child_number = self.child_number.hex()
        chain_code = self.chain_code.hex()
        key = self.key.hex()
        return f'{{\n\t"key_version:<char[4]>": {key_version},\n\t"depth:<uint8_t>": {depth},\n\t"parent_fingerprint:<char[4]>": {parent_fingerprint},\n\t"child_number:<char[4]>": {child_number},\n\t"chain_code:<char[32]>": {chain_code},\n\t"key:<char[33]>": {key}\n}}'


if __name__ == '__main__':
    from src.Account.CONF.Local import *

    account = HierarchicalDeterministicAccount(
        PUBLIC_KEY_VERSION,
        0,
        b'\x00\x00\x00\x00',
        b'\x00\x00\x00\x01',
        b'\x00'*32,
        b'\x00'*33
    )
    print(HierarchicalDeterministicAccount.deserialize(account.serialize()))
    
        