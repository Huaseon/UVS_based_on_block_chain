'''
@File     : CONF.py
@Time     : 2024/12/31 14:07:09
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
from src.utils.data import SERIALIZE
import struct

# 哈希（散列）序列化
HASH_SERIALIZE = SERIALIZE('<32s')
# 起始字符串序列化格式
START_STRING_SERIALIZE = SERIALIZE('<4s')
# 命令名序列化格式
COMMAND_NAME_SERIALIZE = SERIALIZE('<12s')
# 负载大小序列化格式
PAYLOAD_SIZE_SERIALIZE = SERIALIZE('<I')
# 校验和序列化格式
CHECKSUM_SERIALIZE = SERIALIZE('<4s')
# 消息报头序列化格式
MESSAGE_HEADER_SERIALIZE = START_STRING_SERIALIZE + COMMAND_NAME_SERIALIZE + PAYLOAD_SIZE_SERIALIZE + CHECKSUM_SERIALIZE

# 消息类型标识符序列化格式
TYPE_IDENTIFIER_SERIALIZE = SERIALIZE('<I')
# 数据消息序列化格式
INVENTORY_SERIALIZE = TYPE_IDENTIFIER_SERIALIZE + HASH_SERIALIZE

'''
可用的类型标识符
'''
# TXID 类型标识符
MSG_TX = 1
# 区块头类型标识符
MSG_BLOCK = 2
# 过滤器区块加载类型标识符
MSG_FILTERED_BLOCK = 3
# 紧凑区块类型标识符
MSG_CMPCT_BLOCK = 4
# 见证交易类型标识符
MSG_WITNESS_TX = MSG_TX | 0x40000000
# 见证区块类型标识符
MSG_WITNESS_BLOCK = MSG_BLOCK | 0x40000000
# 见证过滤器区块加载类型标识符
MSG_FILTERED_WITNESS_BLOCK = MSG_FILTERED_BLOCK | 0x40000000


# Headers消息中的交易计数（后缀）
TX_COUNT_ON_HEADERS_SERIALIZE = SERIALIZE('<B')
TX_COUNT_ON_HEADERS = 0x00

# 随机数序列化
NONCE_SERIALIZE = SERIALIZE('<Q')

# Payload为空
EMPTY_PAYLOAD = b''

# Unix时间戳序列化
TIME_SERIALIZE = SERIALIZE('<I')
# 时间戳序列化
TIMESTAMP_SERIALIZE = SERIALIZE('<Q')
# 服务序列化
SERVICES_SERIALIZE = SERIALIZE('<Q')
# 最佳区块高度
START_HEIGHT_SERIALIZE = SERIALIZE('<I')

# 服务标识符
Unnamed = 0x00
NODE_NETWORK = 0x01
NODE_GETUTXO = 0x02
NODE_BLOOM = 0x04
NODE_WITNESS = 0x08
NODE_XTHIN = 0x10
NODE_NETWORK_LIMITED = 0x20

# IP地址序列化
# IP_SERIALIZE

# 端口序列化
PORT_SERIALIZE = SERIALIZE('>H')

# FLAGS
class FLAGS(int):
    def __new__(cls, flags: int) -> 'FLAGS':
        return super().__new__(cls, cls.normalize(flags))

    def __init__(self, flags: int) -> None:
        self.reversed_flags = int(f'{int(self):<0{len(self) * 8}b}'[-1::-1], 2)

    def __bytes__(self) -> bytes:
        return self.serialize()

    @staticmethod
    def from_bytes(data: bytes, flag_byte_count: int) -> 'FLAGS':
        return FLAGS.deserialize(data, flag_byte_count)

    def serialize(self) -> bytes:
        return self.reversed_flags.to_bytes(len(self), 'big')

    @staticmethod
    def deserialize(data: bytes, flag_byte_count: int) -> 'FLAGS':
        reversed_flags = int.from_bytes(data[:flag_byte_count], 'big')
        flags, data = int(f'{reversed_flags:<0{flag_byte_count * 8}b}'[-1::-1], 2), data[flag_byte_count:]
        return FLAGS(
            flags
        ) if not data else (
            FLAGS(
                flags
            ), data
        )

    @staticmethod
    def normalize(flags: int) -> int:
        if not flags:
            raise ValueError('Invalid flags')
        return flags if flags ^ 0 else FLAGS.normalize(flags >> 1)

    def __len__(self) -> int:
        bit_count = int(self).bit_length()
        return (bit_count // 8) + (bit_count % 8 != 0)

# NetworkIPAddress
class NetworkIPAddress(object):
    def __init__(self,
        time: int,
        services: int,
        IP_address: str,
        port: int
    ):
        self.time = time
        self.services = services
        self.IP_address = IP_address
        self.port = port
    
    def serialize(self) -> bytes:
        return TIME_SERIALIZE.serialize(self.time) \
            + SERVICES_SERIALIZE.serialize(self.services) \
            + IP_SERIALIZE.serialize(self.IP_address) \
            + PORT_SERIALIZE.serialize(self.port)
    
    @staticmethod
    def deserialize(data: bytes) -> 'NetworkIPAddress':
        time, data = TIME_SERIALIZE.deserialize(data)
        services, data = SERVICES_SERIALIZE.deserialize(data)
        IP_address, data = IP_SERIALIZE.deserialize(data)
        port, data = PORT_SERIALIZE.deserialize(data)
        return NetworkIPAddress(
            time=time,
            services=services,
            IP_address=IP_address,
            port=port
        ), data
    
    def __len__(self) -> int:
        return len(self.serialize())
    
    def __str__(self) -> str:
        time = TIME_SERIALIZE.serialize(self.time).hex()
        services = SERVICES_SERIALIZE.serialize(self.services).hex()
        IP_address = IP_SERIALIZE.serialize(self.IP_address).hex()
        port = PORT_SERIALIZE.serialize(self.port).hex()
        return f'{{\n\t"time:<uint32_t>": {time},\n\t"services:<uint64_t>": {services}\n\t"IP address:<char[16]>": {IP_address},\n\t"port:<uint16_t>": {port}\n}}'

# IP_SERIALIZE
class IP_SERIALIZE(SERIALIZE):
    
    # 10字节的0
    NULL_ = SERIALIZE('>10x')
    # 2字节的1
    _ONE_ = SERIALIZE('>H')
    _one_ = 0xffff
    # 4字节的IPv4
    _IPv4 = SERIALIZE('>BBBB')

    # 16字节的IPv6
    IPv6 = str(NULL_ + _ONE_ + _IPv4)
    
    @staticmethod
    def serialize(ipv4: str) -> bytes:
        ipv4 = IP_SERIALIZE.normalize(ipv4)
        return struct.pack(
            IP_SERIALIZE.IPv6,
            IP_SERIALIZE._one_,
            *map(int, ipv4.split('.'))
        )

    @staticmethod
    def deserialize(data: bytes) -> str:
        _one_, *args = struct.unpack(
            IP_SERIALIZE.IPv6,
            data[:struct.calcsize(IP_SERIALIZE.IPv6)]
        )
        data = data[struct.calcsize(IP_SERIALIZE.IPv6):]
        if _one_ != IP_SERIALIZE._one_:
            raise ValueError('Invalid IP address')
        return '.'.join(map(str, args)), data
    
    @staticmethod
    def normalize(ip: str) -> str:
        return ip if not ip.startswith('::ffff:') else ip[7:]



