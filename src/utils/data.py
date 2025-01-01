'''
@File     : data.py
@Time     : 2024/12/29 08:31:33
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import struct
from typing import Any

# compactSize
class compactSize(int):
    def __new__(cls, value: int) -> 'compactSize':
        value = int(value)
        if value < 0:
            raise ValueError('Invalid compactSize value')
        return int.__new__(cls, value)
    
    def __len__(self):
        if int(self) < 253:
            return 1
        elif int(self) < 0x10000:
            return 3
        elif int(self) < 0x100000000:
            return 5
        elif int(self) < 0x10000000000000000:
            return 9
        else:
            raise ValueError('Invalid compactSize value')

    def __bytes__(self):
        match len(self):
            case 1:
                return int(self).to_bytes(1, 'little')
            case 3:
                return b'\xfd' + int(self).to_bytes(2, 'little')
            case 5:
                return b'\xfe' + int(self).to_bytes(4, 'little')
            case 9:
                return b'\xff' + int(self).to_bytes(8, 'little')
            case _:
                raise ValueError('Invalid compactSize value')
    
    def serialize(self):
        return bytes(self)

    @staticmethod
    def from_bytes(data: bytes) -> tuple['compactSize', bytes]:
        
        if data[0] < 253:
            return compactSize(data[0]), data[1:]
        elif data[0] == 253:
            return compactSize(int.from_bytes(data[1:3], 'little')), data[3:]
        elif data[0] == 254:
            return compactSize(int.from_bytes(data[1:5], 'little')), data[5:]
        elif data[0] == 255:
            return compactSize(int.from_bytes(data[1:9], 'little')), data[9:]
        else:
            raise ValueError('Invalid compactSize value')
    
    @staticmethod
    def deserialize(data: bytes):
        return compactSize.from_bytes(data)
    
    def __add__(self, other: int) -> 'compactSize':
        if int(other) < 0:
            raise ValueError('Invalid compactSize value')
        return compactSize(int(self) + (int(other) if isinstance(other, compactSize) else other))
    
    def __sub__(self, other: int) -> 'compactSize':
        if int(self) < int(other):
            raise ValueError('Invalid compactSize value')
        return compactSize(int(self) - (int(other) if isinstance(other, compactSize) else other))

    def __str__(self) -> str:
        return str(int(self))

# SERIALIZE_FORMAT
class SERIALIZE(str):
    char = ('x', 'c', 'b', 'B', '?', 'h', 'H', 'i', 'I', 'l', 'L', 'q', 'Q', 'n', 'N', 'e', 'f', 'd', 's', 'p', 'P')
    
    def __new__(cls, format: str) -> 'SERIALIZE':
        return str.__new__(cls, cls.normalize(format))
    
    def __len__(self) -> int:
        return struct.calcsize(str(self))
    
    @staticmethod
    def normalize(format: str) -> str:
        format = str(format)
        if (format)[0] not in SERIALIZE.char and format[0] != '<':
            raise ValueError('Invalid format')
        return format if format.startswith('<') else '<' + format

    def __add__(self, other: str) -> 'SERIALIZE':
        other = str(other)
        return SERIALIZE(str(self) + SERIALIZE.normalize(other)[1:])

    def serialize(self, *args) -> bytes:
        return struct.pack(
            str(self),
            *args
        )
    
    def deserialize(self, data: bytes) -> Any:
        return *struct.unpack(
            str(self),
            data[:len(self)]
        ), data[len(self):]

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
