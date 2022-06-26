from cgi import test
import warnings
from dataclasses import dataclass
from typing import Tuple

warnings.filterwarnings("ignore", category=DeprecationWarning)
import asyncio

from starkware.starknet.testing.starknet import Starknet, StarknetContract
from starkware.starkware_utils.error_handling import StarkException
from utils import TestSigner as Signer


@dataclass
class Account:
    signer: Signer
    contract: StarknetContract


# Reusable local network & contracts to save testing time
# @pytest_asyncio.fixture(scope="module")


async def contract_factory() -> Tuple[Starknet, Account, Account, StarknetContract]:
    starknet = await Starknet.empty()
    player1_signer = Signer(private_key=12345)
    account1 = Account(
        signer=player1_signer,
        contract=await starknet.deploy(
            "contracts/Account.cairo", constructor_calldata=[player1_signer.public_key]
        ),
    )
    player2_signer = Signer(private_key=123456789)
    account2 = Account(
        signer=player2_signer,
        contract=await starknet.deploy(
            "contracts/Account.cairo", constructor_calldata=[player2_signer.public_key],
        ),
    )
    contract = await starknet.deploy("contracts/contract.cairo")

    return starknet, account1, account2, contract


async def test_perdesen():

    starknet, account1, account2, contract = await contract_factory()

    player1 = account1.contract
    player2 = account2.contract
    address1 = account1.contract.contract_address
    address2 = account2.contract.contract_address
    game = contract.contract_address

    name = input("Enter card index:")
    print("card index", name)

    z = await contract.fisher_yates_shuffle().invoke()
    print(z)
    # assert z.result[0] == (6)


loop = asyncio.get_event_loop()
loop.run_until_complete(test_perdesen())
loop.close()

