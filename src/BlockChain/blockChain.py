'''
@File     : BlockChain.py
@Time     : 2024/12/28 22:06:15
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

from hashlib import sha256
from typing import List, Tuple

# # 链结构
# class BlockChain(object):
#     def __init__(self) -> None:
#         self.blocks = []
#         self.blocks.append(Block.genesis())
    
#     def add_block(self, data: str) -> None:
#         self.blocks.append(Block.mine_block(self.blocks[-1], data))
    
#     def __str__(self) -> str:
#         return '\n'.join([str(block) for block in self.blocks])

