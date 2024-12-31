'''
@File     : test_MERKLEBLOCK.py
@Time     : 2024/12/31 11:43:03
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
import unittest
from src.BlockChain.block import MerkleBlock, BlockHeader
from src.Transaction.transaction import TRANSACTION
from tests.data.local import json_merkle_block, json_transaction

class Test_MERKLEBLOCK(unittest.TestCase):
    def setUp(self):
        self.merkle_block = MerkleBlock(
            **json_merkle_block()
        )

    def test_merkle_block_initialization(self):
        self.assertEqual(
            len(self.merkle_block.txns), self.merkle_block.merkle_tree[0][0]
        )
        self.assertEqual(
            self.merkle_block.root(), self.merkle_block.merkle_tree[-1][1]
        )
        self.assertEqual(
            self.merkle_block.root(), self.merkle_block.merkle_tree[-1][2]
        )
        self.assertEqual(
            self.merkle_block.root(), self.merkle_block.block_header.merkle_root_hash
        )

    def test_merkle_block_update(self):
        tx = TRANSACTION(
            **json_transaction()
        )
        _len, _root = len(self.merkle_block), self.merkle_block.root()

        self.merkle_block.update(tx)

        self.assertIs(
            _len + 1 == len(self.merkle_block), True
        )
        self.assertIs(
            _root == self.merkle_block.root(), False
        )
        self.assertEqual(
            self.merkle_block.root(), self.merkle_block.merkle_tree[-1][2]
        )
        self.assertEqual(
            self.merkle_block.root(), self.merkle_block.block_header.merkle_root_hash
        )

if __name__ == '__main__':
    unittest.main()