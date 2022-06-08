import warnings
from dataclasses import dataclass
from typing import Tuple

import pytest_asyncio
import pytest

warnings.filterwarnings("ignore", category=DeprecationWarning)
import asyncio

from starkware.starknet.testing.starknet import Starknet, StarknetContract
from starkware.starkware_utils.error_handling import StarkException
from utils import TestSigner as Signer

some_vehicle = 1


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
    player1_account = Account(
        signer=player1_signer,
        contract=await starknet.deploy(
            "contracts/Account.cairo", constructor_calldata=[player1_signer.public_key]
        ),
    )
    player2_signer = Signer(private_key=123456789)
    player2_account = Account(
        signer=player2_signer,
        contract=await starknet.deploy(
            "contracts/Account.cairo", constructor_calldata=[player2_signer.public_key],
        ),
    )
    contract = await starknet.deploy("contracts/contract.cairo")

    return starknet, player1_account, player2_account, contract


# The testing library uses python's asyncio. So the following
# decorator and the ``async`` keyword are needed.
# @pytest.mark.asyncio
# async def test_join_game(contract_factory):
#     """Test draw next card."""
#     # Create a new Starknet class that simulates the StarkNet
#     # system.

#     _, player1_account, player2_account, contract = contract_factory

#     p1 = await contract.get_player1().invoke()
#     p2 = await contract.get_player2().invoke()
#     tt = await contract.get_trump().invoke()
#     assert (
#         (p1.result == (player1_account.contract.contract_address,))
#         and (p2.result == (player2_account.contract.contract_address,))
#         and (tt.result == (3,))
#     )


# @pytest.mark.asyncio
# async def test_send_challenge1(contract_factory):
#     """Test draw next card."""
#     # Create a new Starknet class that simulates the StarkNet
#     # system.

#     _, player1_account, player2_account, contract = contract_factory

#     await player1_account.signer.send_transaction(
#         account=player1_account.contract,
#         to=contract.contract_address,
#         selector_name="join_game",
#         calldata=[],
#     )
#     await player2_account.signer.send_transaction(
#         account=player2_account.contract,
#         to=contract.contract_address,
#         selector_name="join_game",
#         calldata=[],
#     )

#     idx = 2
#     await player1_account.signer.send_transaction(
#         account=player1_account.contract,
#         to=contract.contract_address,
#         selector_name="send_challenge1",
#         calldata=[idx],
#     )

#     ch1 = await contract.get_challenge(1).invoke()
#     ch2 = await contract.get_challenge(2).invoke()
#     ch3 = await contract.get_challenge(3).invoke()

#     assert (ch1.result == (8,)) and (ch2.result == (99,)) and (ch3.result == (99,))


@pytest.mark.asyncio
async def test_send_responce1(contract_factory):
    """Test draw next card."""
    # Create a new Starknet class that simulates the StarkNet
    # system.

    _, player1_account, player2_account, contract = contract_factory

    await player1_account.signer.send_transaction(
        account=player1_account.contract,
        to=contract.contract_address,
        selector_name="join_game",
        calldata=[],
    )
    await player2_account.signer.send_transaction(
        account=player2_account.contract,
        to=contract.contract_address,
        selector_name="join_game",
        calldata=[],
    )

    idx1 = 2
    await player1_account.signer.send_transaction(
        account=player1_account.contract,
        to=contract.contract_address,
        selector_name="send_challenge1",
        calldata=[idx1],
    )

    idx2 = 1
    await player2_account.signer.send_transaction(
        account=player2_account.contract,
        to=contract.contract_address,
        selector_name="send_response1",
        calldata=[idx2],
    )

    p1 = await contract.get_pile(player1_account.contract.contract_address).invoke()
    p2 = await contract.get_pile(player2_account.contract.contract_address).invoke()
    # ch3 = await contract.get_challenge(3).invoke()

    assert p2.result == (0,) and p1.result == (21,)
    # assert p2.result == (14,) and p1.result == (0,)
    # assert 0 == 0


# @pytest.mark.asyncio
# async def test_draw_next_card(contract_factory):
#     """Test draw next card."""
#     # Create a new Starknet class that simulates the StarkNet
#     # system.
#     _, contract = contract_factory

#     # Invoke draw_next_card() few times.
#     next_card1 = await contract.draw_next_card().invoke()
#     head1 = await contract.get_head().invoke()
#     next_card2 = await contract.draw_next_card().invoke()
#     next_card3 = await contract.draw_next_card().invoke()
#     assert (next_card3.result == (8,)) and (next_card2.result == (22,))
