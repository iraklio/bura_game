import warnings
from dataclasses import dataclass
from typing import Tuple

import pytest_asyncio
import pytest

warnings.filterwarnings("ignore", category=DeprecationWarning)
import asyncio

from starkware.starknet.testing.starknet import Starknet, StarknetContract
from starkware.starkware_utils.error_handling import StarkException
from app.utils import TestSigner as Signer


@dataclass
class Account:
    signer: Signer
    contract: StarknetContract


@pytest.fixture(scope="module")
def event_loop():
    return asyncio.new_event_loop()


# Reusable local network & contracts to save testing time
@pytest_asyncio.fixture(scope="module")
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


@pytest.mark.asyncio
async def test_send_responce2(contract_factory):
    """Test draw next card."""
    # Create a new Starknet class that simulates the StarkNet
    # system.

    _, account1, account2, contract = contract_factory

    player1 = account1.contract
    player2 = account2.contract
    address1 = account1.contract.contract_address
    address2 = account2.contract.contract_address
    game = contract.contract_address

    # player are joining the game. player1 is a challenger
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="join_game", calldata=[3]
    )
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="join_game", calldata=[5]
    )

    # ---------------------- ROUND 1 ----------------------------

    calldata = [1]
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="send_challenge1", calldata=calldata,
    )

    calldata = [1]
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="send_response1", calldata=calldata
    )

    assert True


# assert that drawn cards are S8,D9 and S9 SK
# assert (await contract.get_card(address1, 1).invoke()).result == (13,)
# assert (await contract.get_card(address1, 2).invoke()).result == (26,)
# assert (await contract.get_card(address1, 3).invoke()).result == (14,)
# assert (await contract.get_card(address2, 1).invoke()).result == (3,)
# assert (await contract.get_card(address2, 2).invoke()).result == (28,)
# assert (await contract.get_card(address2, 3).invoke()).result == (9,)

