'''
@File     : data.py
@Time     : 2024/12/29 08:31:33
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import struct
from typing import Any

# compactSize
class compactSize(object):
    def __init__(self, value: int):
        self.value = value
    
    def __len__(self):
        if self.value < 253:
            return 1
        elif self.value < 0x10000:
            return 3
        elif self.value < 0x100000000:
            return 5
        elif self.value < 0x10000000000000000:
            return 9
        else:
            raise ValueError('Invalid compactSize value')

    def __bytes__(self):
        match len(self):
            case 1:
                return self.value.to_bytes(1, 'little')
            case 3:
                return b'\xfd' + self.value.to_bytes(2, 'little')
            case 5:
                return b'\xfe' + self.value.to_bytes(4, 'little')
            case 9:
                return b'\xff' + self.value.to_bytes(8, 'little')
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
    
    def __add__(self, other: any):
        return compactSize(self.value + (other.value if isinstance(other, compactSize) else other))
    
    def __repr__(self) -> str:
        return f'{self.value}'

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