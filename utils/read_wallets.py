import json
import os

root_dir = os.path.dirname(os.path.abspath(__file__))


class ReadWallets:
    def get_accounts(self):
        with open(root_dir + '/../accounts/wallets.json', 'r') as fcc_file:
            return json.load(fcc_file)
