import base64
import datetime
import hmac
import json
import os
import time

import requests
from dotenv import load_dotenv

from utils.read_wallets import ReadWallets

load_dotenv()

# https://www.okx.com/docs-v5/en/#overview-api-resources-and-support
BASE_URL = 'https://aws.okx.com'

apiKey = os.getenv("OKX_API_KEY", None)
secretKey = os.getenv("OKX_SECRET_KEY", None)
passPhrase = os.getenv("OKX_PASS_PHRASE", None)


def get_time():
    now = datetime.datetime.utcnow()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"


def signature(timestamp, method, request_path, body, secret_key):
    if str(body) == '{}' or str(body) == 'None':
        body = ''
    message = str(timestamp) + str.upper(method) + request_path + str(body)
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)


class OkexClient:
    def __init__(self, apikey: str, apisecret: str, password: str):
        self.apikey = apikey
        self.apisecret = apisecret
        self.password = password
        self.baseURL = 'https://www.okex.com'

    def get_header(self, sign, timestamp):
        header = {
            "OK-ACCESS-KEY": self.apikey,
            "OK-ACCESS-SIGN": sign,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.password,
            "Content-Type": "application/json",
        }
        return header

    def getCurrencies(self, ccy):
        """
        Get current ETH withdraw fee
        :param ccy:
        :return:
        """
        path = "/api/v5/asset/currencies?ccy=" + ccy
        timestamp = get_time()
        sign = signature(timestamp, "get", path, None, secretKey)
        result = requests.get(BASE_URL + path, headers=self.get_header(sign, timestamp))

        res = result.json()
        if res['code'] == '0':
            chain = filter(lambda coin: coin['chain'] == "ETH-ERC20", res['data'])
            return list(chain)[0]['minFee']
        else:
            print("getCurrencies failed: ", result.text)

    def withdraw(self, ccy, amt, fee, toAddress):
        """
         Batch withdraw ETH into Accounts
        :param ccy:
        :param amt:
        :param fee:
        :param toAddress:
        :return:
        """

        path = "/api/v5/asset/withdrawal"
        for i in range(len(toAddress)):
            time.sleep(5)
            body = {
                "ccy": ccy,
                "dest": 4,
                "amt": str(amt),
                "toAddr": toAddress[i]['address'],
                "fee": str(fee),
                "chain": "ETH-ERC20"}

            timestamp = get_time()
            body = json.dumps(body)
            sign = signature(timestamp, "POST", path, body, secretKey)
            result = requests.post(BASE_URL + path, headers=self.get_header(sign, timestamp), data=body)
            res = result.json()

            print(result.text)
            if res['code'] == '0':
                print("Withdraw success wallet: ", i)
            else:
                print("Withdraw failed: ", result.text)


if __name__ == '__main__':
    wallets = ReadWallets()
    accounts = wallets.get_accounts()

    client = OkexClient(apiKey, secretKey, passPhrase)
    fee = client.getCurrencies("ETH")
    print("Fee: ", fee)
    # client.withdraw("ETH", 0.01, fee, accounts)
