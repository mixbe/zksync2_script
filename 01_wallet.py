import json
import os

from eth_account import Account

root_dir = os.path.dirname(os.path.abspath(__file__))


def saveETHWallet(jsonData):
    file_path = root_dir + '/accounts/wallets.json'
    if os.path.exists(file_path):
        raise RuntimeError("Wallets  existed")
    with open(file_path, 'w') as f:
        json.dump(jsonData, f, indent=4)


def createNewETHWallet(number):
    wallets = []
    for id in range(number):
        # 添加一些随机性
        account = Account.create('zksync Random  Seed' + str(id))
        # 私钥
        privateKey = account._key_obj
        # 公钥
        publicKey = privateKey.public_key
        # 地址
        address = publicKey.to_checksum_address()
        wallet = {
            "index": id,
            "address": address,
            "privateKey": str(privateKey)
        }
        wallets.append(wallet)

    return wallets


# https://eth.antcave.club/1000
if __name__ == '__main__':
    wallets = createNewETHWallet(10)
    saveETHWallet(wallets)
