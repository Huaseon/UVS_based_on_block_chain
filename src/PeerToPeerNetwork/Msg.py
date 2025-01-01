'''
@File     : Msg.py
@Time     : 2024/12/31 14:14:25
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
from hashlib import sha256
from src.V.v1.CONFIG import *
from src.utils.data import compactSize
from typing import TypeAlias
from src.BlockChain.block import BlockHeader
from src.PeerToPeerNetwork.NetConf.Global import *
from src.Transaction.transaction import TRANSACTION, TxIn, TxOut, outpoint, AuditMission

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
    
    @staticmethod
    def deserialize(data):
        start_string, command_name, payload_size, checksum, data = MESSAGE_HEADER_SERIALIZE.deserialize(data)
        return MessageHeader(
            start_string=start_string,
            command_name=command_name,
            payload_size=payload_size,
            checksum=checksum
        ) if not data else (
            MessageHeader(
                start_string=start_string,
                command_name=command_name,
                payload_size=payload_size,
                checksum=checksum
            ),
            data
        )

    def __str__(self):
        start_string = START_STRING_SERIALIZE.serialize(self.start_string).hex()
        command_name = COMMAND_NAME_SERIALIZE.serialize(self.command_name).hex()
        payload_size = PAYLOAD_SIZE_SERIALIZE.serialize(self.payload_size).hex()
        checksum = CHECKSUM_SERIALIZE.serialize(self.checksum).hex()
        return f'{{\n\t"start_string:<char[4]>": {start_string},\n\t"command_name:<char[12]>": {command_name},\n\t"payload_size:<uint32_t>": {payload_size},\n\t"checksum:<char[4]>": {checksum}\n}}'
    
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
        return f'{{\n\t"type_identifier:<uint32_t>": {type_identifier},\n\t"hash:<char[32]>": {hash}\n}}'
    
    def __len__(self) -> int:
        return len(self.serialize())

# 定义GetBlocks消息类
class GetBlocks(object):
    def __init__(self,
        start_string: bytes | int,
        version: int,
        block_header_hashes: list[bytes],
        stop_hash: bytes
    ):
        self.payload = GetBlocks_(
            version=version,
            block_header_hashes=block_header_hashes,
            stop_hash=stop_hash
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=b'getblocks',
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'GetBlocks':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(b'getblocks'):
            raise ValueError('Command name is not getblocks')
        payload = GetBlocks_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return GetBlocks(
            start_string=message_header.start_string,
            version=payload.version,
            block_header_hashes=payload.block_header_hashes,
            stop_hash=payload.stop_hash
        ) if not data else (
            GetBlocks(
                start_string=message_header.start_string,
                version=payload.version,
                block_header_hashes=payload.block_header_hashes,
                stop_hash=payload.stop_hash
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<GetBlocks_>": {payload}\n}}'
    
# 定义Payload_GetBlocks消息类
class GetBlocks_(object):
    def __init__(self,
        version: int,
        block_header_hashes: list[bytes],
        stop_hash: bytes
    ):
        self.stop_hash = stop_hash
        self.block_header_hashes = block_header_hashes
        self.hash_count = compactSize(len(self.block_header_hashes))
        self.version = version

    def serialize(self) -> bytes:
        version = VERSION_SERIALIZE.serialize(self.version)
        hash_count = compactSize.serialize(self.hash_count)
        block_header_hashes = b''.join(self.block_header_hashes)
        stop_hash = HASH_SERIALIZE.serialize(self.stop_hash)
        return version + hash_count + block_header_hashes + stop_hash
    
    @staticmethod
    def deserialize(data: bytes) -> 'GetBlocks_':
        version, data = VERSION_SERIALIZE.deserialize(data)
        hash_count, data = compactSize.deserialize(data)
        block_header_hashes = []
        for _ in range(hash_count):
            block_header_hashe, data = HASH_SERIALIZE.deserialize(data)
            block_header_hashes.append(block_header_hashe)
        stop_hash, data = HASH_SERIALIZE.deserialize(data)
        return GetBlocks_(
            version=version,
            block_header_hashes=block_header_hashes,
            stop_hash=stop_hash
        ) if not data else (
            GetBlocks_(
                version=version,
                block_header_hashes=block_header_hashes,
                stop_hash=stop_hash
            ),
            data
        )
    
    def __str__(self) -> str:
        version = VERSION_SERIALIZE.serialize(self.version).hex()
        hash_count = compactSize.serialize(self.hash_count).hex()
        block_header_hashes = '[\n\t' + ',\n\t'.join([block_header_hashe.hex() for block_header_hashe in self.block_header_hashes]) + '\n]'
        block_header_hashes = block_header_hashes.replace('\n', '\n\t')
        stop_hash = HASH_SERIALIZE.serialize(self.stop_hash).hex()
        return f'{{\n\t"version:<uint32_t>": {version},\n\t"hash_count:<var_int>": {hash_count},\n\t"block_header_hashes:<char[32]>": {block_header_hashes},\n\t"stop_hash:<char[32]>": {stop_hash}\n}}'

    def __len__(self) -> int:
        return len(self.serialize())
    
    def _hash(self) -> bytes:
        return sha256(self.serialize()).digest()

# 定义Inv消息类
class Inv(object):
    def __init__(self,
        start_string: bytes | int,
        inventory: list[INVENTORY]
    ):
        self.payload = Inv_(
            inventory=inventory
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=b'inv',
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )

    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()

    @staticmethod
    def deserialize(data: bytes) -> 'Inv':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(b'inv'):
            raise ValueError('Command name is not inv')
        payload = Inv_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        return Inv(
            start_string=message_header.start_string,
            inventory=payload.inventory
        ) if not data else (
            Inv(
                start_string=message_header.start_string,
                inventory=payload.inventory
            ),
            data
        )

    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<Inv_>": {payload}\n}}'

# 定义Payload_Inv消息类
class Inv_(object):
    def __init__(self,
        inventory: list[INVENTORY]
    ):
        self.inventory = inventory
        self.inventory_count = compactSize(len(self.inventory))

    def serialize(self) -> bytes:
        inventory_count = compactSize.serialize(self.inventory_count)
        inventory = b''.join([inv.serialize() for inv in self.inventory])
        return inventory_count + inventory

    @staticmethod
    def deserialize(data: bytes) -> 'Inv_':
        inventory_count, data = compactSize.deserialize(data)
        inventory = []
        for _ in range(inventory_count - 1):
            inv, data = INVENTORY.deserialize(data)
            inventory.append(inv)
        else:
            inv = INVENTORY.deserialize(data)
            inv, data = inv if isinstance(inv, tuple) else (inv, b'')
            inventory.append(inv)
        return Inv_(
            inventory=inventory
        ) if not data else (
            Inv_(
                inventory=inventory
            ),
            data
        )

    def __str__(self) -> str:
        inventory_count = compactSize.serialize(self.inventory_count).hex()
        inventory = '[\n\t' + ',\n\t'.join([inv.__str__().replace('\n', '\n\t') for inv in self.inventory]) + '\n]'
        inventory = inventory.replace('\n', '\n\t')
        return f'{{\n\t"inventory_count:<compactSize uint>": {inventory_count},\n\t"inventory:<list[Inventory]>": {inventory}\n}}'

    def __len__(self) -> int:
        return len(self.serialize())

    def _hash(self) -> bytes:
        return sha256(self.serialize()).digest()

# 定义GetData消息类
class GetData(object):
    def __init__(self,
        start_string: bytes | int,
        inventory: list[INVENTORY]
    ):
        self.payload = GetData_(
            inventory=inventory
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=b'getdata',
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'GetData':
        message_header, data = MessageHeader.deserialize(data)
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(b'getdata'):
            raise ValueError('Command name is not getdata')
        
        payload = GetData_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return GetData(
            start_string=message_header.start_string,
            inventory=payload.inventory
        ) if not data else (
            GetData(
                start_string=message_header.start_string,
                inventory=payload.inventory
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<GetData_>": {payload}\n}}'

# 定义Payload_GetData消息类
GetData_: TypeAlias = Inv_

# 定义GetHeaders消息类
class GetHeaders(object):
    def __init__(self,
        start_string: bytes | int,
        version: int,
        block_header_hashes: list[bytes],
        stop_hash: bytes
    ):
        self.payload = GetHeaders_(
            version=version,
            block_header_hashes=block_header_hashes,
            stop_hash=stop_hash
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=b'getheaders',
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'GetHeaders':
        message_header, data = MessageHeader.deserialize(data)
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(b'getheaders'):
            raise ValueError('Command name is not getheaders')
         
        payload = GetHeaders_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
       
        return GetHeaders(
            start_string=message_header.start_string,
            version=payload.version,
            block_header_hashes=payload.block_header_hashes,
            stop_hash=payload.stop_hash
        ) if not data else (
            GetHeaders(
                start_string=message_header.start_string,
                version=payload.version,
                block_header_hashes=payload.block_header_hashes,
                stop_hash=payload.stop_hash
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<GetHeaders_>": {payload}\n}}'

# 定义Payload_GetHeaders消息类
GetHeaders_: TypeAlias = GetBlocks_

# 定义Headers消息类
class Headers(object):
    def __init__(self,
        start_string: bytes | int,
        headers: list[BlockHeader]             
    ):
        self.payload = Headers_(
            headers=headers
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=b'headers',
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Headers':
        message_header, data = MessageHeader.deserialize(data)
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(b'headers'):
            raise ValueError('Command name is not headers')
        
        payload = Headers_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return Headers(
            start_string=message_header.start_string,
            headers=payload.headers
        ) if not data else (
            Headers(
                start_string=message_header.start_string,
                headers=payload.headers
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<Headers_>": {payload}\n}}'

# 定义Payload_Headers消息类
class Headers_(object):
    def __init__(self,
        headers: list[BlockHeader]
    ):
        self.headers = headers
        self.count = compactSize(len(self.headers))

    def serialize(self) -> bytes:
        count = compactSize.serialize(self.count)
        headers = b''.join([header.serialize() for header in self.headers]) + TX_COUNT_ON_HEADERS_SERIALIZE.serialize(TX_COUNT_ON_HEADERS)
        return count + headers
    
    @staticmethod
    def deserialize(data: bytes) -> 'Headers_':
        count, data = compactSize.deserialize(data)
        headers = []
        for _ in range(count):
            header, data = BlockHeader.deserialize(data)
            headers.append(header)
        tx_count, data = TX_COUNT_ON_HEADERS_SERIALIZE.deserialize(data)
        if tx_count != TX_COUNT_ON_HEADERS:
            raise ValueError('TX_COUNT_ON_HEADERS is not correct')
        return Headers_(
            headers=headers
        ) if not data else (
            Headers_(
                headers=headers
            ),
            data
        )
    
    def __str__(self) -> str:
        count = compactSize.serialize(self.count).hex()
        headers = '[\n\t' + ',\n\t'.join([header.__str__().replace('\n', '\n\t') for header in self.headers]) + '\n]'
        headers = headers.replace('\n', '\n\t')
        tx_count = TX_COUNT_ON_HEADERS_SERIALIZE.serialize(TX_COUNT_ON_HEADERS).hex()
        return f'{{\n\t"count:<compactSize uint>": {count},\n\t"headers:<list[BlockHeader]>": {headers},\n\t"tx_count:<null>": {tx_count}\n}}'

    def __len__(self) -> int:
        return len(self.serialize())

    def _hash(self) -> bytes:
        return sha256(self.serialize()).digest()

# 定义Payload_EMPTY消息
class EMPTY_(object):
    
    def __init__(self):
        pass
    
    def serialize(data) -> bytes:
        return EMPTY_PAYLOAD
    
    @staticmethod
    def deserialize(data: bytes) -> 'EMPTY_':
        return EMPTY_() if not data else (
            EMPTY_(),
            data
        )
    
    def __str__(self) -> str:
        return EMPTY_PAYLOAD.hex()

    def __len__(self) -> int:
        return len(self.serialize())
    
    def _hash(self) -> bytes:
        return sha256(sha256(self.serialize()).digest()).digest()

# 定义Mempool消息类
class Mempool(object):
    def __init__(self,
        start_string: bytes | int
    ):
        self.payload = Mempool_()
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=b'mempool',
            payload_size=0,
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize()+self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Mempool':
        message_header = MessageHeader.deserialize(data)
        message_header, data = message_header if isinstance(message_header, tuple) else (message_header, b'')
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(b'mempool'):
            raise ValueError('Command name is not mempool')
        
        payload = Mempool_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return Mempool(
            start_string=message_header.start_string
        ) if not data else (
            Mempool(
                start_string=message_header.start_string
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<Mempool_>": {payload}\n}}'

# 定义Payload_Mempool消息类
Mempool_: TypeAlias = EMPTY_

# 定义MerkleBlock消息类
class MerkleBlock(object):
    def __init__(self,
        start_string: bytes | int,
        block_header: BlockHeader,
        transaction_count: int,
        hashes: list[bytes],
        flags: int
    ):
        self.payload = MerkleBlock_(
            block_header=block_header,
            transaction_count=transaction_count,
            hashes=hashes,
            flags=flags
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=b'merkleblock',
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()

    @staticmethod
    def deserialize(data: bytes) -> 'MerkleBlock':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(b'merkleblock'):
            raise ValueError('Command name is not merkleblock')
        payload = MerkleBlock_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        return MerkleBlock(
            start_string=message_header.start_string,
            block_header=payload.block_header,
            transaction_count=payload.transaction_count,
            hashes=payload.hashes,
            flags=payload.flags
        ) if not data else (
            MerkleBlock(
                start_string=message_header.start_string,
                block_header=payload.block_header,
                transaction_count=payload.transaction_count,
                hashes=payload.hashes,
                flags=payload.flags
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<MerkleBlock_>": {payload}\n}}'

# 定义Payload_MerkleBlock消息类
class MerkleBlock_(object):
    def __init__(self,
        block_header: 'BlockHeader',
        transaction_count: int,
        hashes: list[bytes],
        flags: int
    ) -> None:
        self.flags = FLAGS(flags)
        self.flag_byte_count = compactSize(len(self.flags))
        self.hashes = hashes
        self.hash_count = compactSize(len(self.hashes))
        if self.hash_count != self.flags.bit_count():
            raise ValueError('Hash count is not equal to flag count')
        self.transaction_count = compactSize(transaction_count)
        self.block_header = block_header

    def serialize(self) -> bytes:
        block_header = self.block_header.serialize()
        transaction_count = self.transaction_count.serialize()
        hash_count = self.hash_count.serialize()
        hashes = b''.join(self.hashes)
        flag_byte_count = self.flag_byte_count.serialize()
        flags = self.flags.serialize()
        return block_header + transaction_count + hash_count + hashes + flag_byte_count + flags

    @staticmethod
    def deserialize(data: bytes) -> 'MerkleBlock_':
        block_header, data = BlockHeader.deserialize(data)
        transaction_count, data = compactSize.deserialize(data)
        hash_count, data = compactSize.deserialize(data)
        hashes = []
        for _ in range(hash_count):
            hash, data = HASH_SERIALIZE.deserialize(data)
            hashes.append(hash)
        flag_byte_count, data = compactSize.deserialize(data)
        flags = FLAGS.deserialize(data, flag_byte_count)
        flags, data = flags if isinstance(flags, tuple) else (flags, b'')

        return MerkleBlock_(
            block_header=block_header,
            transaction_count=transaction_count,
            hashes=hashes,
            flags=flags
        ) if not data else (
            MerkleBlock_(
                block_header=block_header,
                transaction_count=transaction_count,
                hashes=hashes,
                flags=flags
            ),
            data
        )

    def __len__(self) -> int:
        return len(self.serialize())
    
    def __str__(self) -> str:
        block_header = self.block_header.__str__().replace('\n', '\n\t')
        transaction_count = compactSize.serialize(self.transaction_count).hex()
        hash_count = compactSize.serialize(self.hash_count).hex()
        hashes = '[\n\t' + ',\n\t'.join([hash.hex() for hash in self.hashes]) + '\n]'
        hashes = hashes.replace('\n', '\n\t')
        flag_byte_count = compactSize.serialize(self.flag_byte_count).hex()
        flags = self.flags.serialize().hex()
        return f'{{\n\t"block_header:<BlockHeader>": {block_header},\n\t"transaction_count:<compactSize uint>": {transaction_count},\n\t"hash_count:<compactSize uint>": {hash_count},\n\t"hashes:<list[bytes]>": {hashes},\n\t"flag_byte_count:<compactSize uint>": {flag_byte_count},\n\t"flags:<FLAGS>": {flags}\n}}'

    def _hash(self) -> bytes:
        return sha256(self.serialize()).digest()

# 定义Tx消息类
class Tx(object):
    def __init__(self,
        start_string: bytes | int,
        transaction: 'TRANSACTION'
    ):
        self.payload = Tx_(
            transaction=transaction
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=b'tx',
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()

    @staticmethod
    def deserialize(data: bytes) -> 'Tx':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(b'tx'):
            raise ValueError('Command name is not tx')
        payload = Tx_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        return Tx(
            start_string=message_header.start_string,
            transaction=payload.transaction
        ) if not data else (
            Tx(
                start_string=message_header.start_string,
                transaction=payload.transaction
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<Tx_>": {payload}\n}}'

# 定义Payload_Tx消息类
class Tx_(object):
    def __init__(self,
        transaction: TRANSACTION
    ) -> None:
        self.transaction = transaction

    def serialize(self) -> bytes:
        return self.transaction.serialize()

    @staticmethod
    def deserialize(data: bytes) -> 'Tx_':
        transaction = TRANSACTION.deserialize(data)
        transaction, data = transaction if isinstance(transaction, tuple) else (transaction, b'')
        return Tx_(
            transaction=transaction
        ) if not data else (
            Tx_(
                transaction=transaction
            ),
            data
        )

    def __len__(self) -> int:
        return len(self.serialize())
    
    def __str__(self) -> str:
        return self.transaction.__str__().replace('\n', '\n\t')

    def _hash(self) -> bytes:
        return sha256(self.serialize()).digest()

# 定义Notfound消息
class Notfound(object):
    def __init__(self,
        start_string: bytes | int,
        inventory: list[INVENTORY]
    ):
        self.payload = Notfound_(
            inventory=inventory
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=b'notfound',
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )

    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Notfound':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(b'notfound'):
            raise ValueError('Command name is not notfound')
        payload = Notfound_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        return Notfound(
            start_string=message_header.start_string,
            inventory=payload.inventory
        ) if not data else (
            Notfound(
                start_string=message_header.start_string,
                inventory=payload.inventory
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<Notfound_>": {payload}\n}}'


# 定义Payload_Notfound消息
Notfound_: TypeAlias = Inv_

# 定义Addr消息
class Addr(object):
    def __init__(self,
         start_string: bytes | int,
         IP_addresses: list[NetworkIPAddress]        
    ):
        self.payload = Addr_(
            IP_addresses=IP_addresses
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=b'addr',
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Addr':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(b'addr'):
            raise ValueError('Command name is not addr')
        payload = Addr_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        return Addr(
            start_string=message_header.start_string,
            IP_addresses=payload.IP_addresses
        ) if not data else (
            Addr(
                start_string=message_header.start_string,
                IP_addresses=payload.IP_addresses
            ),
            data
        )

    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<Addr_>: {payload}\n}}'

# 定义Payload_Addr消息
class Addr_(object):
    def __init__(self,
        IP_addresses: list[NetworkIPAddress]
    ):
        self.IP_addresses = IP_addresses
        self.IP_address_count = compactSize(len(self.IP_addresses))

    def serialize(self) -> bytes:
        IP_address_count = compactSize.serialize(self.IP_address_count)
        IP_addresses = b''.join([IP_address.serialize() for IP_address in self.IP_addresses])
        return IP_address_count + IP_addresses

    @staticmethod
    def deserialize(data: bytes) -> 'Addr_':
        IP_address_count, data = compactSize.deserialize(data)
        IP_addresses = []
        for _ in range(IP_address_count - 1):
            IP_address, data = NetworkIPAddress.deserialize(data)
            IP_addresses.append(IP_address)
        else:
            IP_address = NetworkIPAddress.deserialize(data)
            IP_address, data = IP_address if isinstance(IP_address, tuple) else (IP_address, b'')
            IP_addresses.append(IP_address)
        return Addr_(
            IP_addresses=IP_addresses
        ) if not data else (
            Addr_(
                IP_addresses=IP_addresses
            ),
            data
        )

    def __len__(self) -> int:
        return len(self.serialize())
    
    def __str__(self) -> str:
        IP_address_count = compactSize.serialize(self.IP_address_count).hex()
        IP_addresses = '[\n\t' + ',\n\t'.join([IP_address.__str__().replace('\n', '\n\t') for IP_address in self.IP_addresses]) + '\n]'
        IP_addresses = IP_addresses.replace('\n', '\n\t')
        return f'{{\n\t"IP address count:<compactSize uint>": {IP_address_count},\n\t"IP addresses:<list[NetworkIPAddress]>": {IP_addresses}\n}}'

    def _hash(self) -> bytes:
        return sha256(self.serialize()).digest()

# 定义GetAddr消息

# 定义Payload_GetAddr消息

if __name__ == "__main__":
    # 模块测试
    from src.PeerToPeerNetwork.NetConf.LocalNet import *
    # msg_header = MessageHeader(
    #     start_string=START_STRING,
    #     command_name=b'block',
    #     payload_size=32,
    #     checksum=b'1234'
    # )
    # print(MessageHeader.deserialize(msg_header.serialize()))
    
    # inv = INVENTORY(
    #     type_identifier=MSG_WITNESS_BLOCK,
    #     hash=sha256(b'').digest()
    # )
    # print(INVENTORY.deserialize(inv.serialize()))

    # get_blocks = GetBlocks(
    #     start_string=START_STRING,
    #     version=VERSION_DEFAULT,
    #     block_header_hashes=[sha256(b'').digest(), sha256(b'1').digest()],
    #     stop_hash=sha256(b'').digest()
    # )

    # print(GetBlocks.deserialize(get_blocks.serialize()))

    # inv = Inv(
    #     start_string=START_STRING,
    #     inventory=[
    #         INVENTORY(
    #             type_identifier=MSG_WITNESS_BLOCK,
    #             hash=sha256(b'').digest()
    #         ), INVENTORY(
    #             type_identifier=MSG_WITNESS_BLOCK,
    #             hash=sha256(b'1').digest()
    #         )
    #     ]
    # )
    # print(Inv.deserialize(inv.serialize()))

    # get_data = GetData(
    #     start_string=START_STRING,
    #     inventory=[
    #         INVENTORY(
    #             type_identifier=MSG_WITNESS_BLOCK,
    #             hash=sha256(b'').digest()
    #         ), INVENTORY(
    #             type_identifier=MSG_WITNESS_BLOCK,
    #             hash=sha256(b'1').digest()
    #         )
    #     ]
    # )
    # print(GetData.deserialize(get_data.serialize()))

    # get_headers = GetHeaders(
    #     start_string=START_STRING,
    #     version=VERSION_DEFAULT,
    #     block_header_hashes=[sha256(b'').digest(), sha256(b'1').digest()],
    #     stop_hash=sha256(b'').digest()
    # )
    # print(GetHeaders.deserialize(get_headers.serialize()))

    # headers = Headers(
    #     start_string=START_STRING,
    #     headers=[
    #         BlockHeader(
    #             version=VERSION_DEFAULT,
    #             previous_block_header_hash=sha256(b'').hexdigest(),
    #             merkle_root_hash=sha256(b'1').hexdigest(),
    #             time=0,
    #         ), BlockHeader(
    #             version=VERSION_DEFAULT,
    #             previous_block_header_hash=sha256(b'1').hexdigest(),
    #             merkle_root_hash=sha256(b'').hexdigest(),
    #             time=1,
    #         )
    #     ]
    # )
    # print(Headers.deserialize(headers.serialize()))

    # mempool = Mempool(
    #     start_string=START_STRING
    # )
    # print(Mempool.deserialize(mempool.serialize()))

    # merkle_block = MerkleBlock(
    #     start_string=START_STRING,
    #     block_header=BlockHeader(
    #         version=VERSION_DEFAULT,
    #         previous_block_header_hash=sha256(b'').hexdigest(),
    #         merkle_root_hash=sha256(b'1').hexdigest(),
    #         time=0,
    #     ),
    #     transaction_count=99,
    #     hashes=[sha256(b'').digest(), sha256(b'1').digest(), sha256(b'2').digest(), sha256(b'3').digest()], 
    #     flags=0b10111
    # )
    # print(MerkleBlock.deserialize(merkle_block.serialize()))

    # tx = Tx(
    #     start_string=START_STRING,
    #     transaction=TRANSACTION(
    #         version=VERSION_DEFAULT,
    #         tx_in=[
    #             TxIn(
    #                 previous_output=outpoint(
    #                     hash=sha256(b'').hexdigest(),
    #                     index=0
    #                 ),
    #                 signature_script=b''
    #             )
    #         ],
    #         tx_out=[
    #             TxOut(
    #                 value=0,
    #                 pk_script=b''
    #             )
    #         ],
    #         lock_time=0
    #     )
    # )
    # print(Tx.deserialize(tx.serialize()))

    # notfound = Notfound(
    #     start_string=START_STRING,
    #     inventory=[
    #         INVENTORY(
    #             type_identifier=MSG_WITNESS_BLOCK,
    #             hash=sha256(b'').digest()
    #         ), INVENTORY(
    #             type_identifier=MSG_WITNESS_BLOCK,
    #             hash=sha256(b'1').digest()
    #         )
    #     ]
    # )
    # print(Notfound.deserialize(notfound.serialize()))

    # addr = Addr(
    #     start_string=START_STRING,
    #     IP_addresses=[
    #         NetworkIPAddress(
    #             time=0,
    #             services=1,
    #             IP_address=TERMINAL_IP,
    #             port=TERMINAL_PORT
    #         )
    #     ]
    # )
    # print(Addr.deserialize(addr.serialize()))