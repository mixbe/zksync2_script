import os

from dotenv import load_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import HexStr
from eth_utils import remove_0x_prefix
from web3 import Web3
from zksync2.core.types import Token
from zksync2.manage_contracts.zksync_contract import ZkSyncContract
from zksync2.module.module_builder import ZkSyncBuilder
from zksync2.provider.eth_provider import EthereumProvider

from utils.private_utils import EnvPrivateKey
from utils.read_wallets import ReadWallets


def deposit(zksync_provider: Web3,
            eth_web3: Web3,
            eth_provider: EthereumProvider,
            account: LocalAccount,
            amount: float,
            to: HexStr = None) -> tuple[HexStr, HexStr]:
    """
    Deposit ETH from L1 to L2 network
    :param zksync_provider:
        Instance of ZkSync provider
    :param eth_web3:
        Instance of Ethereum Web3 provider
    :param eth_provider:
        Instance of Ethereum provider
    :param account:
        From which ETH account the withdrawal will be made
    :param amount:
        How much would the withdrawal will contain
    :return:
        Deposit transaction hashes on L1 and L2 networks
    """
    # execute deposit on L1 network
    print("Executing deposit transaction on L1 network")
    l1_tx_receipt = eth_provider.deposit(token=Token.create_eth(),
                                         to=to,
                                         amount=Web3.to_wei(amount, 'ether'),
                                         l2_gas_limit=1123680,
                                         gas_limit=200000,
                                         gas_price=int(eth_web3.eth.gas_price * 1.2))

    # Check if deposit transaction was successful
    if not l1_tx_receipt["status"]:
        raise RuntimeError("Deposit transaction on L1 network failed")

    # Get ZkSync contract on L1 network
    zksync_contract = ZkSyncContract(zksync_provider.zksync.main_contract_address, eth_web3, account)

    # Get hash of deposit transaction on L2 network
    l2_hash = zksync_provider.zksync.get_l2_hash_from_priority_op(l1_tx_receipt, zksync_contract)

    # Wait for deposit transaction on L2 network to be finalized (5-7 minutes)
    print("Waiting for deposit transaction on L2 network to be finalized (5-7 minutes)")
    l2_tx_receipt = zksync_provider.zksync.wait_for_transaction_receipt(transaction_hash=l2_hash,
                                                                        timeout=360,
                                                                        poll_latency=10)

    # return deposit transaction hashes from L1 and L2 networks
    return l1_tx_receipt['transactionHash'].hex(), l2_tx_receipt['transactionHash'].hex()


if __name__ == "__main__":
    # Get the private key from OS environment variables
    # PRIVATE_KEY = bytes.fromhex(os.environ.get("PRIVATE_KEY"))

    load_dotenv()
    zksync_url = os.getenv('ZKSYNC_URL')
    eth_url = os.getenv('ETH_URL')
    if zksync_url is None:
        print("Err: ZKSYNC_URL not set")
    if eth_url is None:
        print("Err: ETH_URL not set")

    wallets = ReadWallets()
    accounts = wallets.get_accounts()

    for wallet in accounts:
        # Get account object by providing private key of the sender

        account: LocalAccount = Account.from_key(bytes.fromhex(remove_0x_prefix(HexStr(wallet['privateKey']))))

        # Connect to zkSync network
        zk_web3 = ZkSyncBuilder.build(zksync_url)

        # connect to Ethereum network
        eth_web3 = Web3(Web3.HTTPProvider(eth_url))

        # Create Ethereum provider
        eth_provider = EthereumProvider(zk_web3, eth_web3, account)

        # Perform the deposit
        amount = 0.001

        l1_tx_hash, l2_tx_hash = deposit(zk_web3, eth_web3, eth_provider, account, amount, None)

        print(f"L1 transaction: {l1_tx_hash}")
        print(f"L2 transaction: {l2_tx_hash}")
