from bitcoin import SelectParams
from bitcoin.base58 import decode
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret, P2PKHBitcoinAddress


SelectParams('testnet')

my_private_key = CBitcoinSecret(
    'cUhH6hpmQrWq5t1d3ZLWSk2PYG4NEPcoyQfbQELiWriDB1QHDgtf')
my_public_key = my_private_key.pub
my_address = P2PKHBitcoinAddress.from_pubkey(my_public_key)
# 测试币发送回的地址
faucet_address = CBitcoinAddress('mv4rnyY3Su5gjcDNzbMLKBQkBicCtHUtFB')

