import csv

from eth_account import Account


def saveETHWallet(jsonData):
    with open('wallets.csv', 'w', encoding='utf-8-sig', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["index", "address", "private_key", "public_key"])
        csv_writer.writerows(jsonData)


def createNewETHWallet():
    wallets = []
    for id in range(100):
        # 添加一些随机性
        account = Account.create('zksync Random  Seed' + str(id))
        # 私钥
        privateKey = account._key_obj
        # 公钥
        publicKey = privateKey.public_key
        # 地址
        address = publicKey.to_checksum_address()
        wallet = {
            "id": id,
            "address": address,
            "privateKey": privateKey,
            "publicKey": publicKey
        }
        wallets.append(wallet.values())

    return wallets


# https://eth.antcave.club/1000
if __name__ == '__main__':
    wallets = createNewETHWallet()
    saveETHWallet(wallets)
