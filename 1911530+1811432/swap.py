import time
import alice
import bob

######################################################################
#                                                                    #
#                                                                    #
#              CS251 Project 2: Cross-chain Atomic Swap              #
#                                                                    #
#                                                                    #
#                                                                    #
#              Written by: 朱浩泽 1911530  1811432 王润泽              #
#              December 11, 2021                                     #
#              Version 1.0.1                                         #
#                                                                    #
######################################################################
#
# In this assignment we will implement a cross-chain atomic swap
# between two parties, Alice and Bob.
#
# Alice has bitcoin on BTC Testnet3 (the standard bitcoin testnet).
# Bob has bitcoin on BCY Testnet (Blockcypher's Bitcoin testnet).
# They want to trade ownership of their respective coins securely,
# something that can't be done with a simple transaction because
# they are on different blockchains.
#
# This method also works between other cryptocurrencies and altcoins,
# for example trading n Bitcoin for m Litecoin.
# 
# The idea here is to set up transactions around a secret x, that
# only one party (Alice) knows. In these transactions only H(x) 
# will be published, leaving x secret. 
# 
# Transactions will be set up in such a way that once x is revealed,
# both parties can redeem the coins sent by the other party.
#
# If x is never revealed, both parties will be able to retrieve their
# original coins safely, without help from the other.
#
#
#
######################################################################
#                           BTC Testnet3                             #     
######################################################################
#
# Alice ----> UTXO ----> Bob (with x)
#               |
#               |
#               V
#             Alice (after 48 hours)
#
######################################################################
#                            BCY Testnet                             #
######################################################################
#
#   Bob ----> UTXO ----> Alice (with x)
#               |
#               |
#               V
#              Bob (after 24 hours)
#
######################################################################

######################################################################
#
# Configured for your addresses
# 
# TODO: Fill in all of these fields
#

alice_txid_to_spend     = "94143dbfd34bc5f52e22a924ed91c10df5b784ba4fcdc4e00542de21b81207a8" 
alice_utxo_index        = 0
alice_amount_to_send    = 0.03

bob_txid_to_spend       = "5e753673c4db5d2084a66735f472e9b48f53e5f69d4484bd43a484f78ba07241"
bob_utxo_index          = 0
bob_amount_to_send      = 0.01

# Get current block height (for locktime) in 'height' parameter for each blockchain (and put it into swap.py):
#  curl https://api.blockcypher.com/v1/btc/test3
btc_test3_chain_height  = 2108093

#  curl https://api.blockcypher.com/v1/bcy/test3
bcy_test_chain_height   = 65659

# Parameter for how long Alice/Bob should have to wait before they can take back their coins
## alice_locktime MUST be > bob_locktime
alice_locktime = 5
bob_locktime = 3

tx_fee = 0.001

broadcast_transactions = True
alice_redeems = True

#
#
######################################################################


######################################################################
#
# Read the following function.
# 
# There's nothing to implement here, but it outlines the structure
# of how Alice and Bob will communicate to perform this cross-
# chain atomic swap.
#
# You will run swap.py to test your code.
#
######################################################################

def atomic_swap(broadcast_transactions=False, alice_redeems=True):
    # Alice reveals the hash of her secret x but not the secret itself
    hash_of_secret = alice.hash_of_secret()

    # Alice creates a transaction redeemable by Bob (with x) or by Bob and Alice
    alice_swap_tx, alice_swap_scriptPubKey = alice.alice_swap_tx(
        alice_txid_to_spend,
        alice_utxo_index,
        alice_amount_to_send - tx_fee,
    )

    # Alice creates a time-locked transaction to return coins to herself
    alice_return_coins_tx = alice.return_coins_tx(
        alice_amount_to_send - (2 * tx_fee),
        alice_swap_tx,
        btc_test3_chain_height + alice_locktime,
        alice_swap_scriptPubKey,
    )

    # Alice asks Bob to sign her transaction
    bob_signature_BTC = bob.sign_BTC(alice_return_coins_tx, alice_swap_scriptPubKey)

    # Alice broadcasts her first transaction, only after Bob signs this one
    if broadcast_transactions:
        alice.broadcast_BTC(alice_swap_tx)

    # The same situation occurs, with roles reversed
    bob_swap_tx, bob_swap_scriptPubKey = bob.bob_swap_tx(
        bob_txid_to_spend,
        bob_utxo_index,
        bob_amount_to_send - tx_fee,
        hash_of_secret,
    )
    bob_return_coins_tx = bob.return_coins_tx(
        bob_amount_to_send - (2 * tx_fee),
        bob_swap_tx,
        bcy_test_chain_height + bob_locktime,
    )

    alice_signature_BCY = alice.sign_BCY(bob_return_coins_tx, bob_swap_scriptPubKey)

    if broadcast_transactions:
        bob.broadcast_BCY(bob_swap_tx)

    if broadcast_transactions:
        print('Sleeping for 20 minutes to let transactions confirm...')
        time.sleep(60 * 20)

    if alice_redeems:
        # Alice redeems her coins, revealing x publicly (it's now on the blockchain)
        alice_redeem_tx, alice_secret_x = alice.redeem_swap(
            bob_amount_to_send - (2 * tx_fee),
            bob_swap_tx,
            bob_swap_scriptPubKey,
        )
        if broadcast_transactions:
            alice.broadcast_BCY(alice_redeem_tx)

        # Once x is revealed, Bob may also redeem his coins
        bob_redeem_tx = bob.redeem_swap(
            alice_amount_to_send - (2 * tx_fee),
            alice_swap_tx,
            alice_swap_scriptPubKey,
            alice_secret_x,
        )
        if broadcast_transactions:
            bob.broadcast_BTC(bob_redeem_tx)
    else:
        
        # Bob and Alice may take back their original coins after the specified time has passed
        completed_bob_return_tx = bob.complete_return_tx(
            bob_return_coins_tx,
            bob_swap_scriptPubKey,
            alice_signature_BCY,
        )
        completed_alice_return_tx = alice.complete_return_tx(
            alice_return_coins_tx,
            alice_swap_scriptPubKey,
            bob_signature_BTC,
        )
        if broadcast_transactions:
            print('Sleeping for bob_locktime blocks to pass locktime...')
            time.sleep(10 * 60 * bob_locktime)
            bob.broadcast_BCY(completed_bob_return_tx)

            print('Sleeping for alice_locktime blocks to pass locktime...')
            time.sleep(10 * 60 * max(alice_locktime - bob_locktime, 0))
            alice.broadcast_BTC(completed_alice_return_tx)

if __name__ == '__main__':
    atomic_swap(broadcast_transactions, alice_redeems)


#Alice swap tx (BTC) created successfully!
#Bob swap tx (BCY) created successfully!
#Bob return coins (BCY) tx created successfully!
#Alice return coins tx (BTC) created successfully!



# Alice swap tx (BTC) created successfully!
# 201 Created
# {
#   "tx": {
#     "block_height": -1,
#     "block_index": -1,
#     "hash": "02688427fd96e1bfeba4114ac4835227f267e812d237b1ff2651fbf59669df88",
#     "addresses": [
#       "mxzP48hgsix8MNAqXwnoye2nxZnWngt4wz"
#     ],
#     "total": 2900000,
#     "fees": 164949,
#     "size": 266,
#     "vsize": 266,
#     "preference": "high",
#     "relayed_by": "111.33.78.5",
#     "received": "2021-12-10T08:12:00.134121592Z",
#     "ver": 1,
#     "double_spend": false,
#     "vin_sz": 1,
#     "vout_sz": 1,
#     "confirmations": 0,
#     "inputs": [
#       {
#         "prev_hash": "94143dbfd34bc5f52e22a924ed91c10df5b784ba4fcdc4e00542de21b81207a8",
#         "output_index": 0,
#         "script": "483045022100bdfe8994ba2421e46b63678fc3304f8ead3760e23955576bd11ab66455928bbf022033f8c62fa66fe107893c034d1fc3ad9c6d23f481a68a9c2a14151321573aa6ad0121036aae1a0bdbef8c67a9eef01da5f5815a2ac52da61ef1f265b3a9aaa4c1766807",
#         "output_value": 3064949,
#         "sequence": 4294967295,
#         "addresses": [
#           "mxzP48hgsix8MNAqXwnoye2nxZnWngt4wz"
#         ],
#         "script_type": "pay-to-pubkey-hash",
#         "age": 2106694
#       }
#     ],
#     "outputs": [
#       {
#         "value": 2900000,
#         "script": "2103b63ffe7daec20d21e82c4c43887ce070c4ac0a1f49d9b6b82efe832630345151ad7621036aae1a0bdbef8c67a9eef01da5f5815a2ac52da61ef1f265b3a9aaa4c1766807ac63755167a914853b775079232503df966e626618e1d388a957208768",
#         "addresses": null,
#         "script_type": "unknown"
#       }
#     ]
#   }
# }
# Bob swap tx (BCY) created successfully!
# 201 Created
# {
#   "tx": {
#     "block_height": -1,
#     "block_index": -1,
#     "hash": "2a1b2ee753e550302204391edfed6498306d121ef39f8ed9cf1787094dc75983",
#     "addresses": [
#       "BxTB2z5YtpYHG1pjbgG9Q6w5jAjP5iXvo3"
#     ],
#     "total": 900000,
#     "fees": 100000,
#     "size": 266,
#     "vsize": 266,
#     "preference": "high",
#     "relayed_by": "221.238.245.34",
#     "received": "2021-12-10T08:12:01.093211726Z",
#     "ver": 1,
#     "double_spend": false,
#     "vin_sz": 1,
#     "vout_sz": 1,
#     "confirmations": 0,
#     "inputs": [
#       {
#         "prev_hash": "5e753673c4db5d2084a66735f472e9b48f53e5f69d4484bd43a484f78ba07241",
#         "output_index": 0,
#         "script": "483045022100b1ce295c26b5c043b27377253f7635d297d3527122cc23dd245b77d5121b3cf602200860f3b272b4f8a7be83aaaccc6f5cace4e02b659f0013c8228b8040ac51c7e801210210aca0881548895f25c9292f54aee603c0004b0783a2820741787164bc861007",
#         "output_value": 1000000,
#         "sequence": 4294967295,
#         "addresses": [
#           "BxTB2z5YtpYHG1pjbgG9Q6w5jAjP5iXvo3"
#         ],
#         "script_type": "pay-to-pubkey-hash",
#         "age": 65669
#       }
#     ],
#     "outputs": [
#       {
#         "value": 900000,
#         "script": "2102e7d0cc9a3f1dd51d6c3c1ef893ed8d354c20d2bfc6b90b62c021cbd527273fbaad76210210aca0881548895f25c9292f54aee603c0004b0783a2820741787164bc861007ac63755167a914853b775079232503df966e626618e1d388a957208768",
#         "addresses": null,
#         "script_type": "unknown"
#       }
#     ]
#   }
# }
# Sleeping for 20 minutes to let transactions confirm...
# Alice redeem from swap tx (BCY) created successfully!
# 201 Created
# {
#   "tx": {
#     "block_height": -1,
#     "block_index": -1,
#     "hash": "3e34e88cb53e2415a8f79b8a756253d011ae974b350785cf37fbe99f42e6445b",
#     "addresses": [
#       "C4tTcPPkp7W44TPPhG3CVWd88MxPidfYGC"
#     ],
#     "total": 800000,
#     "fees": 100000,
#     "size": 183,
#     "vsize": 183,
#     "preference": "high",
#     "relayed_by": "221.238.245.34",
#     "received": "2021-12-10T08:32:02.22030873Z",
#     "ver": 1,
#     "double_spend": false,
#     "vin_sz": 1,
#     "vout_sz": 1,
#     "confirmations": 0,
#     "inputs": [
#       {
#         "prev_hash": "2a1b2ee753e550302204391edfed6498306d121ef39f8ed9cf1787094dc75983",
#         "output_index": 0,
#         "script": "187468697349734153656372657450617373776f72643132334830450221009dd3261a7fbf9cb758f619a8138448b1df27e06055428c3923fc7d3de0d01535022020c04dff05af8d2e79b4776ba27f272d657d86339e1f99318c99ad15a55b648001",
#         "output_value": 900000,
#         "sequence": 4294967295,
#         "script_type": "unknown",
#         "age": 65758
#       }
#     ],
#     "outputs": [
#       {
#         "value": 800000,
#         "script": "76a91481040df0670e5153d8f0064b8c22f09efa9586c588ac",
#         "addresses": [
#           "C4tTcPPkp7W44TPPhG3CVWd88MxPidfYGC"
#         ],
#         "script_type": "pay-to-pubkey-hash"
#       }
#     ]
#   }
# }
# Bob redeem from swap tx (BTC) created successfully!
# 201 Created
# {
#   "tx": {
#     "block_height": -1,
#     "block_index": -1,
#     "hash": "a1270545ad0d517dd3924ac447e441666a96046e9be4d2a0fda3ca1b239419ad",
#     "addresses": [
#       "mvgtajCFAz2X6vLvAqJ7MgAxXRaSTaL2oC"
#     ],
#     "total": 2799999,
#     "fees": 100001,
#     "size": 182,
#     "vsize": 182,
#     "preference": "high",
#     "relayed_by": "117.131.219.34",
#     "received": "2021-12-10T08:32:03.162803838Z",
#     "ver": 1,
#     "double_spend": false,
#     "vin_sz": 1,
#     "vout_sz": 1,
#     "confirmations": 0,
#     "inputs": [
#       {
#         "prev_hash": "02688427fd96e1bfeba4114ac4835227f267e812d237b1ff2651fbf59669df88",
#         "output_index": 0,
#         "script": "187468697349734153656372657450617373776f72643132334730440220641b057ff9dd1760f4082b74c5cc78be76374b8b24cd4ae2b3ec688d0d8089c002207e4b0d07a1f9c70cde5d9fdc5b60e3671cffe84c79c0c4dd2f8dc5605f16038d01",
#         "output_value": 2900000,
#         "sequence": 4294967295,
#         "script_type": "unknown",
#         "age": 0
#       }
#     ],
#     "outputs": [
#       {
#         "value": 2799999,
#         "script": "76a914a66af283e796645da20e8d8096852ba21b2fcd1f88ac",
#         "addresses": [
#           "mvgtajCFAz2X6vLvAqJ7MgAxXRaSTaL2oC"
#         ],
#         "script_type": "pay-to-pubkey-hash"
#       }
#     ]
#   }
# }
