'''
@File     : CONFIG.py
@Time     : 2024/12/29 09:58:08
@Author   : H.SEON
@Contact  : dsj34473@163.com
'''

import sys
sys.path.append('.')
from src.utils.data import SERIALIZE

'''
默认值/最值/常量
'''
# 版本默认值
VERSION_DEFAULT = 1
# ATM 索引默认值
INDEX_ON_ATM_DEFAULT = 0xFFFFFFFF
# 序列号默认值
SEQUENCE_DEFAULT = 0xFFFFFFFF

# ATM 脚本最大长度
MAX_ATM_SCRIPT_SIZE = 100
# 公钥脚本最大长度
MAX_PK_SCRIPT_SIZE = 10000
# 签名最大长度
MAX_SIGNATURE_SCRIPT_SIZE = 10000


'''
序列化格式
'''
# 序列号序列化格式
SEQUENCE_SERIALIZE = SERIALIZE('<I')
# 哈希（散列）序列化格式
HASH_SERIALIZE = SERIALIZE('<32s')
# 索引序列化格式
INDEX_SERIALIZE = SERIALIZE('<I')
# 花费数量序列化格式
VALUE_SERIALIZE = SERIALIZE('<Q')
# 版本号序列化格式
VERSION_SERIALIZE = SERIALIZE('<I')
# 锁定时间序列化格式
LOCK_TIME_SERIALIZE = SERIALIZE('<I')
# 时间戳序列化格式
TIME_SERIALIZE = SERIALIZE('<I')
# 特定输出序列化格式
OUTPOINT_SERIALIZE = HASH_SERIALIZE + INDEX_SERIALIZE
# 区块头序列化格式
BLOCK_HEADER_SERIALIZE = VERSION_SERIALIZE + HASH_SERIALIZE + HASH_SERIALIZE + TIME_SERIALIZE

if __name__ == "__main__":
    print("version_default", VERSION_DEFAULT)
    print("index_on_ATM_default", INDEX_ON_ATM_DEFAULT)
    print("sequence_default", SEQUENCE_DEFAULT)
    print("max_atm_script_size", MAX_ATM_SCRIPT_SIZE)
    print("max_pk_script_size", MAX_PK_SCRIPT_SIZE)
    print("max_signature_script_size", MAX_SIGNATURE_SCRIPT_SIZE)
    print("sequence_serialize", SEQUENCE_SERIALIZE)
    print("hash_serialize", HASH_SERIALIZE)
    print("index_serialize", INDEX_SERIALIZE)
    print("value_serialize", VALUE_SERIALIZE)
    print("version_serialize", VERSION_SERIALIZE)
    print("lock_time_serialize", LOCK_TIME_SERIALIZE)
    print("time_serialize", TIME_SERIALIZE)
    print("outpoint_serialize", OUTPOINT_SERIALIZE)
    print("block_header_serialize", BLOCK_HEADER_SERIALIZE)




