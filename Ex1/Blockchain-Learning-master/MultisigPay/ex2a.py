from sys import exit
from bitcoin.core.script import *
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret, P2PKHBitcoinAddress
from config.utils import *
from config.config import my_private_key, my_public_key, my_address, faucet_address
from SplitandPay.ex1 import send_from_P2PKH_transaction

# 仨用户的私钥和公钥，在keygen.py中生成
cust1_private_key = CBitcoinSecret(
    'cUD21crs2mhbkAvXktD4cm8mQnVZjC3iwV6vLLPiNkbEdATr2gTD')
cust1_public_key = cust1_private_key.pub
cust2_private_key = CBitcoinSecret(
    'cQxQTLfw7BrGr5KRSypACjMtB4VE9DScT9za6wWVoEKbgtEiD3y4')
cust2_public_key = cust2_private_key.pub
cust3_private_key = CBitcoinSecret(
    'cVPMd2Z5Qk2J8S3Qxk2DhxKcSYrmQL8iqRbYzXQaM2dj5pyyA7js')
cust3_public_key = cust3_private_key.pub


######################################################################
# TODO: Complete the scriptPubKey implementation for Exercise 3
# You can assume the role of the bank for the purposes of this problem
# and use my_public_key and my_private_key in lieu of bank_public_key and
# bank_private_key.

# 锁定脚本
# 锁定脚本类似于把这笔钱输入到一个保险箱里，只有满足开锁要求才能拿出来
# 开锁要求是一个bank签名和至少一个用户签名，因此可以分解为以下两端验证过程
# 1：验证bank(表现为my_public_key, OP_CHECKSIG)
# 2：验证其中一个用户签名(类似于一个1-3方案的多重签名脚本)
# 一个M-N方案的多重签名脚本的锁定脚本形式为 OP_M, pubKey 1, pubKey 2, ..., pubKey N, OP_N, OP_CHECKMULTISIG
# 经过CHECKSIG和CHECKMULTISIG，会导致栈中有两个验证结果(两个true)，然而我们只需要一个，所以把CHECKSIG修改为CHECKSIGVERIFY(验证后不保留结果)

ex2a_txout_scriptPubKey = [my_public_key, OP_CHECKSIGVERIFY,
                           OP_1, cust1_public_key, cust2_public_key, cust3_public_key, OP_3, OP_CHECKMULTISIG]

######################################################################

if __name__ == '__main__':
    ######################################################################
    # TODO: set these parameters correctly
    amount_to_send = 0.0001111
    txid_to_spend = (
        '2c9e96cc4ab1f93467a31db58c12d208c630f30f01111e03da0551da0556812d')
    utxo_index = 1
    ######################################################################

    response = send_from_P2PKH_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        ex2a_txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)
