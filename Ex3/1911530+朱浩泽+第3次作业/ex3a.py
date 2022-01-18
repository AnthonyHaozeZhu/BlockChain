from sys import exit
from bitcoin.core.script import *

from utils import *
from config import my_private_key, my_public_key, my_address, faucet_address
from ex1 import send_from_P2PKH_transaction


######################################################################
# TODO: Complete the scriptPubKey implementation for Exercise 3
ex3a_txout_scriptPubKey = [OP_2DUP, OP_ADD, 190, OP_EQUALVERIFY, OP_SUB, 1530 ,OP_EQUAL]
#在b中将xy压栈，复制xy（OP_2DUP），取出栈顶的xy相加（OP_ADD）和190比较（OP_EQUALVERIFY），相等直接继续
#将剩下的xy相减（OP_SUB）和1530比较（OP_EQUALVERIFY），相等返回true
######################################################################

if __name__ == '__main__':
    ######################################################################
    # TODO: set these parameters correctly
    amount_to_send = 0.01
    txid_to_spend = (
        '02d6ee08cd6effadd530cbea4fc51a14d26b0b74707062f2e27252750571789a')
    utxo_index = 1
    ######################################################################

    response = send_from_P2PKH_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        ex3a_txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)
