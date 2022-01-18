from sys import exit
from bitcoin.core.script import *
from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress

from utils import *
from config import my_private_key, my_public_key, my_address, faucet_address
from ex1 import send_from_P2PKH_transaction


cust1_private_key = CBitcoinSecret(
    'cTsq2iGz29kkRVGVJQ1hTR2ofX4uXJqeZbCfyTamSNQndgtvT8jS')
cust1_public_key = cust1_private_key.pub
cust2_private_key = CBitcoinSecret(
    'cQ2x2B8g3QQdqTwjTzsqWiW5WRb8TKMFsyAZDtZQ873PvynVfh2J')
cust2_public_key = cust2_private_key.pub
cust3_private_key = CBitcoinSecret(
    'cSLzFsTxDCJeHgmudAmh22Pbzfbvdi1J1xk8nRiWYosZ1CBmQm6j')
cust3_public_key = cust3_private_key.pub


######################################################################
# TODO: Complete the scriptPubKey implementation for Exercise 2

# You can assume the role of the bank for the purposes of this problem
# and use my_public_key and my_private_key in lieu of bank_public_key and
# bank_private_key.
ex2a_txout_scriptPubKey = [CBitcoinSecret('cS2HDN48vQUjPYNp9ngM8XPXhyxTeNrB6FoFQK5PbY9kh5FYoeXT').pub,     #银行公钥
OP_CHECKSIGVERIFY, 
OP_1,
cust1_private_key.pub,
cust2_private_key.pub,
cust3_private_key.pub,       #三个客户的公钥
OP_3,
OP_CHECKMULTISIG
]
######################################################################

if __name__ == '__main__':
    ######################################################################
    # TODO: set these parameters correctly
    amount_to_send = 0.014
    txid_to_spend = (
        '78132f73a68b6d9ebc1a4839b45315740561efbc59022694e0ebefacf3fb814a')
    utxo_index = 0
    ######################################################################

    response = send_from_P2PKH_transaction(
        amount_to_send, txid_to_spend, utxo_index,
        ex2a_txout_scriptPubKey)
    print(response.status_code, response.reason)
    print(response.text)
