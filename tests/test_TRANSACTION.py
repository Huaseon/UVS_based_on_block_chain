'''
@File     : test_TRANSACTION.py
@Time     : 2024/12/30 20:17:46
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
import unittest
from src.Transaction.transaction import *
from tests.data.local import *

class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.transaction = TRANSACTION(**json_transaction())

    def test_transaction_initialization(self):
        self.assertIsInstance(self.transaction.version, int)
        self.assertEqual(self.transaction.tx_in_count, len(self.transaction.tx_in))
        self.assertEqual(self.transaction.tx_out_count, len(self.transaction.tx_out))
        self.assertGreaterEqual(self.transaction.lock_time, 0)

    def test_transaction_serialization(self):
        serialized_transaction = self.transaction.serialize()
        self.assertIsInstance(serialized_transaction, bytes)

    def test_transaction_deserialization(self):
        serialized_transaction = self.transaction.serialize()
        deserialized_transaction = TRANSACTION.deserialize(serialized_transaction)
        self.assertIsInstance(deserialized_transaction, TRANSACTION)
        self.assertEqual(deserialized_transaction.serialize(), self.transaction.serialize())

if __name__ == '__main__':
    unittest.main()