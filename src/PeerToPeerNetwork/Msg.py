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
from src.BlockChain.block import BLOCK, BlockHeader
from src.PeerToPeerNetwork.NetConf.Global import *
from src.Transaction.transaction import TRANSACTION, TxIn, TxOut, outpoint
from abc import ABC, abstractmethod

# 消息类
class MSG(ABC):
    @abstractmethod
    def __init__(self,
        start_string: bytes | int,
        **kwargs
    ):
        pass
    
    @abstractmethod
    def serialize(self) -> bytes:
        pass

    @staticmethod
    @abstractmethod
    def deserialize(data: bytes) -> 'MSG':
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @staticmethod
    def toMSG(data: bytes) -> 'MSG':
        message_header = MessageHeader.deserialize(data)
        message_header, data = message_header if isinstance(message_header, tuple) else (message_header, b'')
        message = MSG._toMSG(message_header, data)
        message, data = message if isinstance(message, tuple) else (message, b'')
        if message_header.checksum != message.payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        return message if not data else (
            message,
            data
        )
    
    @staticmethod
    def _toMSG(
        message_header: 'MessageHeader',
        data: bytes
    ) -> 'MSG':
        data = message_header.serialize() + data
        command_name = message_header.command_name
        if command_name == case_block:
            return Block.deserialize(data)
        elif command_name == case_getblocks:
            return GetBlocks.deserialize(data)
        elif command_name == case_inv:
            return Inv.deserialize(data)
        elif command_name == case_getdata:
            return GetData.deserialize(data)
        elif command_name == case_getheaders:
            return GetHeaders.deserialize(data)
        elif command_name == case_headers:
            return Headers.deserialize(data)
        elif command_name == case_merkleblock:
            return MerkleBlock.deserialize(data)
        elif command_name == case_mempool:
            return Mempool.deserialize(data)
        elif command_name == case_tx:
            return Tx.deserialize(data)
        elif command_name == case_notfound:
            return Notfound.deserialize(data)
        elif command_name == case_addr:
            return Addr.deserialize(data)
        elif command_name == case_getaddr:
            return GetAddr.deserialize(data)
        elif command_name == case_ping:
            return Ping.deserialize(data)
        elif command_name == case_pong:
            return Pong.deserialize(data)
        elif command_name == case_sendheaders:
            return SendHeaders.deserialize(data)
        elif command_name == case_verack:
            return VerAck.deserialize(data)
        elif command_name == case_version:
            return Version.deserialize(data)
        else:
            raise ValueError('Command name is not correct')


# PAYLOAD
class PAYLOAD(ABC):
    
    @abstractmethod
    def __init__(self, **kwargs) -> None:
        pass

    @abstractmethod
    def serialize(self) -> bytes:
        pass
    
    @staticmethod
    @abstractmethod
    def deserialize(data: bytes) -> 'PAYLOAD':
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass
    
    @abstractmethod
    def _hash(self) -> bytes:
        pass

    # @abstractmethod
    # def act(self, client: 'CLIENT') -> None:
    #     pass

    
        

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
        self.start_string = start_string if isinstance(start_string, bytes) else start_string.to_bytes(len(START_STRING_SERIALIZE), 'big')
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


# 定义Block消息类
class Block(MSG):
    def __init__(self,
        start_string: bytes | int,
        block: BLOCK
    ):
        self.payload = Block_(
            block=block
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_BLOCK,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Block':
        message_header, data = MessageHeader.deserialize(data)
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_BLOCK):
            raise ValueError('Command name is not block')
        
        payload = Block_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return Block(
            start_string=message_header.start_string,
            block=payload.block
        ) if not data else (
            Block(
                start_string=message_header.start_string,
                block=payload.block
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<Block_>": {payload}\n}}'

# 定义Payload_Block消息类
class Block_(PAYLOAD):
    def __init__(self,
        block: BLOCK
    ):
        self.block = block
    
    def serialize(self) -> bytes:
        return self.block.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Block_':
        block = BLOCK.deserialize(data)
        block, data = block if isinstance(block, tuple) else (block, b'')
        return Block_(
            block=block
        ) if not data else (
            Block_(
                block=block
            ),
            data
        )

    def __len__(self) -> int:
        return len(self.serialize())
    
    def __str__(self) -> str:
        return self.block.__str__().replace('\n', '\n\t')
    
    def _hash(self) -> bytes:
        return sha256(self.serialize()).digest()
    
    def act(self, client: 'CLIENT') -> None:
        client.blockchain.add_block(self.block)
        client.logger.info(f'Added a block with height {self.block.header.height} into the blockchain')
    

# 定义GetBlocks消息类
class GetBlocks(MSG):
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
            command_name=COMMAND_NAME_GETBLOCKS,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'GetBlocks':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_GETBLOCKS):
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
class GetBlocks_(PAYLOAD):
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
class Inv(MSG):
    def __init__(self,
        start_string: bytes | int,
        inventory: list[INVENTORY]
    ):
        self.payload = Inv_(
            inventory=inventory
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_INV,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )

    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()

    @staticmethod
    def deserialize(data: bytes) -> 'Inv':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_INV):
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
class Inv_(PAYLOAD):
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
class GetData(MSG):
    def __init__(self,
        start_string: bytes | int,
        inventory: list[INVENTORY]
    ):
        self.payload = GetData_(
            inventory=inventory
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_GETDATA,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'GetData':
        message_header, data = MessageHeader.deserialize(data)
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_GETDATA):
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
class GetHeaders(MSG):
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
            command_name=COMMAND_NAME_GETHEADERS,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'GetHeaders':
        message_header, data = MessageHeader.deserialize(data)
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_GETHEADERS):
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
class Headers(MSG):
    def __init__(self,
        start_string: bytes | int,
        headers: list[BlockHeader]             
    ):
        self.payload = Headers_(
            headers=headers
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_HEADERS,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Headers':
        message_header, data = MessageHeader.deserialize(data)
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_HEADERS):
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
class Headers_(PAYLOAD):
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

# 定义Payload_EMPTY消息类
class EMPTY_(PAYLOAD):
    
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
class Mempool(MSG):
    def __init__(self,
        start_string: bytes | int
    ):
        self.payload = Mempool_()
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_MEMPOOL,
            payload_size=0,
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize()+self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Mempool':
        message_header = MessageHeader.deserialize(data)
        message_header, data = message_header if isinstance(message_header, tuple) else (message_header, b'')
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_MEMPOOL):
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
class MerkleBlock(MSG):
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
            command_name=COMMAND_NAME_MERKLEBLOCK,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()

    @staticmethod
    def deserialize(data: bytes) -> 'MerkleBlock':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_MERKLEBLOCK):
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
class MerkleBlock_(PAYLOAD):
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
class Tx(MSG):
    def __init__(self,
        start_string: bytes | int,
        transaction: 'TRANSACTION'
    ):
        self.payload = Tx_(
            transaction=transaction
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_TX,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()

    @staticmethod
    def deserialize(data: bytes) -> 'Tx':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_TX):
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
class Tx_(PAYLOAD):
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
class Notfound(MSG):
    def __init__(self,
        start_string: bytes | int,
        inventory: list[INVENTORY]
    ):
        self.payload = Notfound_(
            inventory=inventory
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_NOTFOUND,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )

    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Notfound':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_NOTFOUND):
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
class Addr(MSG):
    def __init__(self,
         start_string: bytes | int,
         IP_addresses: list[NetworkIPAddress]        
    ):
        self.payload = Addr_(
            IP_addresses=IP_addresses
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_ADDR,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Addr':
        message_header, data = MessageHeader.deserialize(data)
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_ADDR):
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
class Addr_(PAYLOAD):
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
class GetAddr(MSG):
    def __init__(self,
        start_string: bytes | int
    ):
        self.payload = GetAddr_()
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_GETADDR,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )

    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()

    @staticmethod
    def deserialize(data: bytes) -> 'GetAddr':
        message_header = MessageHeader.deserialize(data)
        message_header, data = message_header if isinstance(message_header, tuple) else (message_header, b'')
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_GETADDR):
            raise ValueError('Command name is not getaddr')
        
        payload = GetAddr_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return GetAddr(
            start_string=message_header.start_string
        ) if not data else (
            GetAddr(
                start_string=message_header.start_string
            ),
            data
        )

    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<GetAddr_>: {payload}\n}}'

# 定义Payload_GetAddr消息
GetAddr_: TypeAlias = EMPTY_

# 定义Ping消息
class Ping(MSG):
    def __init__(self,
        start_string: bytes | int,
        nonce: int
    ):
        self.payload = Ping_(
            nonce=nonce
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_PING,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Ping':
        message_header, data = MessageHeader.deserialize(data)
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_PING):
            raise ValueError('Command name is not ping')
        
        payload = Ping_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return Ping(
            start_string=message_header.start_string,
            nonce=payload.nonce
        ) if not data else (
            Ping(
                start_string=message_header.start_string,
                nonce=payload.nonce
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<Ping_>: {payload}\n}}'

# 定义Payload_Ping消息
class Ping_(PAYLOAD):
    def __init__(self,
        nonce: int
    ):
        self.nonce = nonce
    
    def serialize(self) -> bytes:
        return NONCE_SERIALIZE.serialize(self.nonce)
    
    @staticmethod
    def deserialize(data: bytes) -> 'Ping_':
        nonce, data = NONCE_SERIALIZE.deserialize(data)
        return Ping_(
            nonce=nonce
        ) if not data else (
            Ping_(
                nonce=nonce
            ),
            data
        )
    
    def __len__(self) -> int:
        return len(self.serialize())
    
    def __str__(self) -> str:
        return NONCE_SERIALIZE.serialize(self.nonce).hex()
    
    def _hash(self) -> bytes:
        return sha256(self.serialize()).digest()

# 定义Pong消息
class Pong(MSG):
    def __init__(self,
        start_string: bytes | int,
        nonce: int        
    ):
        self.payload = Pong_(
            nonce=nonce
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_PONG,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Pong':
        message_header = MessageHeader.deserialize(data)
        message_header, data = message_header if isinstance(message_header, tuple) else (message_header, b'')

        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_PONG):
            raise ValueError('Command name is not pong')
        
        payload = Pong_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return Pong(
            start_string=message_header.start_string,
            nonce=payload.nonce
        ) if not data else (
            Pong(
                start_string=message_header.start_string,
                nonce=payload.nonce
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<Pong_>: {payload}\n}}'

# 定义Payload_Pong消息
Pong_: TypeAlias = Ping_

# 定义SendHeaders消息
class SendHeaders(MSG):
    def __init__(self,
        start_string: bytes | int,
    ):
        self.payload = SendHeaders_()
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_SENDHEADERS,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'SendHeaders':
        message_header = MessageHeader.deserialize(data)
        message_header, data = message_header if isinstance(message_header, tuple) else (message_header, b'')
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_SENDHEADERS):
            raise ValueError('Command name is not sendheaders')
        
        payload = SendHeaders_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return SendHeaders(
            start_string=message_header.start_string
        ) if not data else (
            SendHeaders(
                start_string=message_header.start_string
            ),
            data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<SendHeaders_>: {payload}\n}}'

# 定义Payload_SendHeaders消息
SendHeaders_: TypeAlias = EMPTY_

# 定义VerAck消息
class VerAck(MSG):
    def __init__(self,
        start_string: bytes | int
    ):
        self.payload = VerAck_()
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_VERACK,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'VerAck':
        message_header = MessageHeader.deserialize(data)
        message_header, data = message_header if isinstance(message_header, tuple) else (message_header, b'')
        
        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_VERACK):
            raise ValueError('Command name is not verack')
        
        payload = VerAck_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return VerAck(
            start_string=message_header.start_string
        ) if not data else (
            VerAck(
                start_string=message_header.start_string
            ),
            data
        )

    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<VerAck_>: {payload}\n}}'

# 定义Payload_VerAck消息
VerAck_: TypeAlias = EMPTY_

# 定义Version消息
class Version(MSG):
    def __init__(self,
        start_string: bytes | int,
        version: int,
        services: int,
        timestamp: int,
        addr_recv_services: int,
        addr_recv_IP_address: str,
        addr_recv_port: int,
        addr_trans_services: int,
        addr_trans_IP_address: str,
        addr_trans_port: int,
        identifier: int,
        start_height: int,
    ):
        self.payload = Version_(
            version=version,
            services=services,
            timestamp=timestamp,
            addr_recv_services=addr_recv_services,
            addr_recv_IP_address=addr_recv_IP_address,
            addr_recv_port=addr_recv_port,
            addr_trans_services=addr_trans_services,
            addr_trans_IP_address=addr_trans_IP_address,
            addr_trans_port=addr_trans_port,
            identifier=identifier,
            start_height=start_height
        )
        self.message_header = MessageHeader(
            start_string=start_string,
            command_name=COMMAND_NAME_VERSION,
            payload_size=len(self.payload),
            checksum=self.payload._hash()[:len(CHECKSUM_SERIALIZE)]
        )
    
    def serialize(self) -> bytes:
        return self.message_header.serialize() + self.payload.serialize()
    
    @staticmethod
    def deserialize(data: bytes) -> 'Version':
        message_header, data = MessageHeader.deserialize(data)

        if message_header.command_name != COMMAND_NAME_SERIALIZE.serialize(COMMAND_NAME_VERSION):
            raise ValueError('Command name is not version')
        
        payload = Version_.deserialize(data)
        payload, data = payload if isinstance(payload, tuple) else (payload, b'')
        
        if message_header.checksum != payload._hash()[:len(CHECKSUM_SERIALIZE)]:
            raise ValueError('Checksum is not correct')
        
        return Version(
            start_string=message_header.start_string,
            version=payload.version,
            services=payload.services,
            timestamp=payload.timestamp,
            addr_recv_services=payload.addr_recv_services,
            addr_recv_IP_address=payload.addr_recv_IP_address,
            addr_recv_port=payload.addr_recv_port,
            addr_trans_services=payload.addr_trans_services,
            addr_trans_IP_address=payload.addr_trans_IP_address,
            addr_trans_port=payload.addr_trans_port,
            identifier=payload.identifier,
            start_height=payload.start_height
        ) if not data else (
            Version(
                start_string=message_header.start_string,
                version=payload.version,
                services=payload.services,
                timestamp=payload.timestamp,
                addr_recv_services=payload.addr_recv_services,
                addr_recv_IP_address=payload.addr_recv_IP_address,
                addr_recv_port=payload.addr_recv_port,
                addr_trans_services=payload.addr_trans_services,
                addr_trans_IP_address=payload.addr_trans_IP_address,
                addr_trans_port=payload.addr_trans_port,
                identifier=payload.identifier,
                start_height=payload.start_height
            ), data
        )
    
    def __str__(self) -> str:
        message_header = self.message_header.__str__().replace('\n', '\n\t')
        payload = self.payload.__str__().replace('\n', '\n\t')
        return f'{{\n\t"message_header:<MessageHeader>": {message_header},\n\t"payload:<Version_>: {payload}\n}}'
        

# 定义Payload_Version消息
class Version_(PAYLOAD):
    def __init__(self,
        version: int,
        services: int,
        timestamp: int,
        addr_recv_services: int,
        addr_recv_IP_address: str,
        addr_recv_port: int,
        addr_trans_services: int,
        addr_trans_IP_address: str,
        addr_trans_port: int,
        identifier: int,
        start_height: int,
    ):
        self.start_height = start_height
        self.identifier = identifier
        self.addr_trans_port = addr_trans_port
        self.addr_trans_IP_address = addr_trans_IP_address
        self.addr_trans_services = addr_trans_services
        self.addr_recv_port = addr_recv_port
        self.addr_recv_IP_address = addr_recv_IP_address
        self.addr_recv_services = addr_recv_services
        self.timestamp = timestamp
        self.services = services
        self.version = version
    
    def serialize(self) -> bytes:
        version = VERSION_SERIALIZE.serialize(self.version)
        services = SERVICES_SERIALIZE.serialize(self.services)
        timestamp = TIMESTAMP_SERIALIZE.serialize(self.timestamp)
        addr_recv_services = SERVICES_SERIALIZE.serialize(self.addr_recv_services)
        addr_recv_IP_address = IP_SERIALIZE.serialize(self.addr_recv_IP_address)
        addr_recv_port = PORT_SERIALIZE.serialize(self.addr_recv_port)
        addr_trans_services = SERVICES_SERIALIZE.serialize(self.addr_trans_services)
        addr_trans_IP_address = IP_SERIALIZE.serialize(self.addr_trans_IP_address)
        addr_trans_port = PORT_SERIALIZE.serialize(self.addr_trans_port)
        identifer = IDENTIFIER_SERIALIZE.serialize(self.identifier)
        start_height = START_HEIGHT_SERIALIZE.serialize(self.start_height)
        return version + services + timestamp \
            + addr_recv_services + addr_recv_IP_address + addr_recv_port \
            + addr_trans_services + addr_trans_IP_address + addr_trans_port \
            + identifer + start_height
    
    @staticmethod
    def deserialize(data: bytes) -> 'Version_':
        version, data = VERSION_SERIALIZE.deserialize(data)
        services, data = SERVICES_SERIALIZE.deserialize(data)
        timestamp, data = TIMESTAMP_SERIALIZE.deserialize(data)
        addr_recv_services, data = SERVICES_SERIALIZE.deserialize(data)
        addr_recv_IP_address, data = IP_SERIALIZE.deserialize(data)
        addr_recv_port, data = PORT_SERIALIZE.deserialize(data)
        addr_trans_services, data = SERVICES_SERIALIZE.deserialize(data)
        addr_trans_IP_address, data = IP_SERIALIZE.deserialize(data)
        addr_trans_port, data = PORT_SERIALIZE.deserialize(data)
        identifier, data = IDENTIFIER_SERIALIZE.deserialize(data)
        start_height, data = START_HEIGHT_SERIALIZE.deserialize(data)
        return Version_(
            version=version,
            services=services,
            timestamp=timestamp,
            addr_recv_services=addr_recv_services,
            addr_recv_IP_address=addr_recv_IP_address,
            addr_recv_port=addr_recv_port,
            addr_trans_services=addr_trans_services,
            addr_trans_IP_address=addr_trans_IP_address,
            addr_trans_port=addr_trans_port,
            identifier=identifier,
            start_height=start_height
        ) if not data else (
            Version_(
                version=version,
                services=services,
                timestamp=timestamp,
                addr_recv_services=addr_recv_services,
                addr_recv_IP_address=addr_recv_IP_address,
                addr_recv_port=addr_recv_port,
                addr_trans_services=addr_trans_services,
                addr_trans_IP_address=addr_trans_IP_address,
                addr_trans_port=addr_trans_port,
                identifier=identifier,
                start_height=start_height
            ), data
        )

    def __len__(self) -> int:
        return len(self.serialize())
    
    def _hash(self) -> bytes:
        return sha256(self.serialize()).digest()
    
    def __str__(self) -> str:
        version = VERSION_SERIALIZE.serialize(self.version).hex()
        services = SERVICES_SERIALIZE.serialize(self.services).hex()
        timestamp = TIMESTAMP_SERIALIZE.serialize(self.timestamp).hex()
        addr_recv_services = SERVICES_SERIALIZE.serialize(self.addr_recv_services).hex()
        addr_recv_IP_address = IP_SERIALIZE.serialize(self.addr_recv_IP_address).hex()
        addr_recv_port = PORT_SERIALIZE.serialize(self.addr_recv_port).hex()
        addr_trans_services = SERVICES_SERIALIZE.serialize(self.addr_trans_services).hex()
        addr_trans_IP_address = IP_SERIALIZE.serialize(self.addr_trans_IP_address).hex()
        addr_trans_port = PORT_SERIALIZE.serialize(self.addr_trans_port).hex()
        idnetifier = IDENTIFIER_SERIALIZE.serialize(self.identifier).hex()
        start_height = START_HEIGHT_SERIALIZE.serialize(self.start_height).hex()
        return f'''{{\n\t"version:<uint32_t>": {version},\n\t"services:<uint64_t>": {services},\n\t"timestamp:<uint64_t>": {timestamp}\
            ,\n\t"addr_recv_services:<uint64_t>": {addr_recv_services},\n\t"addr_recv_IP_address:<char[16]>": {addr_recv_IP_address},\n\t"addr_recv_port:<uint16_t>": {addr_recv_port}\
            ,\n\t"addr_trans_services:<uint64_t>": {addr_trans_services},\n\t"addr_trans_IP_address:<char[16]>": {addr_trans_IP_address},\n\t"addr_trans_port:<uint16_t>": {addr_trans_port}\
            ,\n\t"conce:<uint64_t>": {idnetifier},\n\t"start_height:<uint32_t>": {start_height}\n}}'''


if __name__ == "__main__":
    # 模块测试
    from src.PeerToPeerNetwork.NetConf.LocalNet import *

    msg_header = MessageHeader(
        start_string=START_STRING,
        command_name=b'block',
        payload_size=32,
        checksum=b'1234'
    )
    print(MessageHeader.deserialize(msg_header.serialize()))
    
    inv = INVENTORY(
        type_identifier=MSG_WITNESS_BLOCK,
        hash=sha256(b'').digest()
    )
    print(INVENTORY.deserialize(inv.serialize()))

    block = Block(
        start_string=START_STRING,
        block=BLOCK(
            block_header=BlockHeader(
                version=VERSION_DEFAULT,
                previous_block_header_hash=sha256(b'').hexdigest(),
                merkle_root_hash=sha256(b'1').hexdigest(),
                time=0,
            ),
            txns=[
                TRANSACTION(
                    version=VERSION_DEFAULT,
                    tx_in=[
                        TxIn(
                            previous_output=outpoint(
                                hash=sha256(b'').hexdigest(),
                                index=0
                            ),
                            signature_script=b''
                        ), TxIn(
                            previous_output=outpoint(
                                hash=sha256(b'1').hexdigest(),
                                index=0
                            ),
                            signature_script=b''
                        )
                    ],
                    tx_out=[
                        TxOut(
                            value=0,
                            pk_script=b''
                        )
                    ],
                    lock_time=0
                ), TRANSACTION(
                    version=VERSION_DEFAULT,
                    tx_in=[
                        TxIn(
                            previous_output=outpoint(
                                hash=sha256(b'2').hexdigest(),
                                index=0
                            ),
                            signature_script=b''
                        )
                    ],
                    tx_out=[
                        TxOut(
                            value=1,
                            pk_script=b''
                        ), TxOut(
                            value=2,
                            pk_script=b''
                        )
                    ],
                    lock_time=0
                )
            ]
        )    
    )
    print(Block.deserialize(block.serialize()))

    get_blocks = GetBlocks(
        start_string=START_STRING,
        version=VERSION_DEFAULT,
        block_header_hashes=[sha256(b'').digest(), sha256(b'1').digest()],
        stop_hash=sha256(b'').digest()
    )

    print(GetBlocks.deserialize(get_blocks.serialize()))

    inv = Inv(
        start_string=START_STRING,
        inventory=[
            INVENTORY(
                type_identifier=MSG_WITNESS_BLOCK,
                hash=sha256(b'').digest()
            ), INVENTORY(
                type_identifier=MSG_WITNESS_BLOCK,
                hash=sha256(b'1').digest()
            )
        ]
    )
    print(Inv.deserialize(inv.serialize()))

    get_data = GetData(
        start_string=START_STRING,
        inventory=[
            INVENTORY(
                type_identifier=MSG_WITNESS_BLOCK,
                hash=sha256(b'').digest()
            ), INVENTORY(
                type_identifier=MSG_WITNESS_BLOCK,
                hash=sha256(b'1').digest()
            )
        ]
    )
    print(GetData.deserialize(get_data.serialize()))

    get_headers = GetHeaders(
        start_string=START_STRING,
        version=VERSION_DEFAULT,
        block_header_hashes=[sha256(b'').digest(), sha256(b'1').digest()],
        stop_hash=sha256(b'').digest()
    )
    print(GetHeaders.deserialize(get_headers.serialize()))

    headers = Headers(
        start_string=START_STRING,
        headers=[
            BlockHeader(
                version=VERSION_DEFAULT,
                previous_block_header_hash=sha256(b'').hexdigest(),
                merkle_root_hash=sha256(b'1').hexdigest(),
                time=0,
            ), BlockHeader(
                version=VERSION_DEFAULT,
                previous_block_header_hash=sha256(b'1').hexdigest(),
                merkle_root_hash=sha256(b'').hexdigest(),
                time=1,
            )
        ]
    )
    print(Headers.deserialize(headers.serialize()))

    mempool = Mempool(
        start_string=START_STRING
    )
    print(Mempool.deserialize(mempool.serialize()))

    merkle_block = MerkleBlock(
        start_string=START_STRING,
        block_header=BlockHeader(
            version=VERSION_DEFAULT,
            previous_block_header_hash=sha256(b'').hexdigest(),
            merkle_root_hash=sha256(b'1').hexdigest(),
            time=0,
        ),
        transaction_count=99,
        hashes=[sha256(b'').digest(), sha256(b'1').digest(), sha256(b'2').digest(), sha256(b'3').digest()], 
        flags=0b10111
    )
    print(MerkleBlock.deserialize(merkle_block.serialize()))

    tx = Tx(
        start_string=START_STRING,
        transaction=TRANSACTION(
            version=VERSION_DEFAULT,
            tx_in=[
                TxIn(
                    previous_output=outpoint(
                        hash=sha256(b'').hexdigest(),
                        index=0
                    ),
                    signature_script=b''
                )
            ],
            tx_out=[
                TxOut(
                    value=0,
                    pk_script=b''
                )
            ],
            lock_time=0
        )
    )
    print(Tx.deserialize(tx.serialize()))

    notfound = Notfound(
        start_string=START_STRING,
        inventory=[
            INVENTORY(
                type_identifier=MSG_WITNESS_BLOCK,
                hash=sha256(b'').digest()
            ), INVENTORY(
                type_identifier=MSG_WITNESS_BLOCK,
                hash=sha256(b'1').digest()
            )
        ]
    )
    print(Notfound.deserialize(notfound.serialize()))

    addr = Addr(
        start_string=START_STRING,
        IP_addresses=[
            NetworkIPAddress(
                time=0,
                services=NODE_NETWORK,
                IP_address=TERMINAL_IP,
                port=TERMINAL_PORT
            )
        ]
    )
    print(Addr.deserialize(addr.serialize()))

    get_addr = GetAddr(
        start_string=START_STRING
    )
    print(GetAddr.deserialize(get_addr.serialize()))

    ping = Ping(
        start_string=START_STRING,
        nonce=0
    )
    print(Ping.deserialize(ping.serialize()))
    
    pong = Pong(
        start_string=START_STRING,
        nonce=0
    )
    print(Pong.deserialize(pong.serialize()))

    send_headers = SendHeaders(
        start_string=START_STRING
    )
    print(SendHeaders.deserialize(send_headers.serialize()))

    verack = VerAck(
        start_string=START_STRING
    )
    print(VerAck.deserialize(verack.serialize()))

    version = Version(
        start_string=START_STRING,
        version=VERSION_DEFAULT,
        services=NODE_NETWORK,
        timestamp=0,
        addr_recv_services=1,
        addr_recv_IP_address=TERMINAL_IP,
        addr_recv_port=TERMINAL_PORT,
        addr_trans_services=NODE_NETWORK,
        addr_trans_IP_address=LOCAL_IP,
        addr_trans_port=next(LOCAL_PORT),
        identifier=0,
        start_height=0
    )
    print(Version.deserialize(version.serialize()))