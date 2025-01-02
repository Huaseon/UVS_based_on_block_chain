'''
@File     : Global.py
@Time     : 2025/01/02 15:52:38
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
from src.utils.data import SERIALIZE

# 密钥版本字节序列格式
KEY_VERSION_SERIALIZE = SERIALIZE('<4s')
# 深度序列格式
DEPTH_SERIALIZE = SERIALIZE('<B')
# 父指纹序列格式
PARENT_FINGERPRINT_SERIALIZE = SERIALIZE('<4s')
# 子编号序列格式
CHILD_NUMBER_SERIALIZE = SERIALIZE('<4s')
# 链码序列格式
CHAIN_CODE_SERIALIZE = SERIALIZE('<32s')
# 密钥序列格式
KEY_SERIALIZA = SERIALIZE('<33s')