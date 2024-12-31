'''
@File     : test_BLOCK.py
@Time     : 2024/12/30 16:53:02
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
import unittest
from src.BlockChain.block import BLOCK, BlockHeader
from src.Transaction.transaction import TRANSACTION
from tests.data.local import *

class TestBlock(unittest.TestCase):

    def setUp(self):
        self.block_header = BlockHeader(**json_block_header())
        self.transactions = [TRANSACTION(**json_transaction()) for _ in range(int(time()) % 9 + 1)]
        self.block = BLOCK(self.block_header, self.transactions)

    def test_block_initialization(self):
        self.assertEqual(self.block.block_header, self.block_header)
        self.assertEqual(self.block.txn_count, len(self.transactions))
        self.assertEqual(self.block.txns, self.transactions)

    def test_block_serialization(self):
        serialized_block = self.block.serialize()
        self.assertIsInstance(serialized_block, bytes)

    def test_block_deserialization(self):
        serialized_block = self.block.serialize()
        deserialized_block = BLOCK.deserialize(serialized_block)
        self.assertIsInstance(deserialized_block, BLOCK)
        self.assertEqual(deserialized_block.serialize(), self.block.serialize())

if __name__ == '__main__':
    unittest.main()