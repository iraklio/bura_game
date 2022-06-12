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


# The testing library uses python's asyncio. So the following
# decorator and the ``async`` keyword are needed.
# @pytest.mark.asyncio
# async def test_join_game(contract_factory):
#     """Test draw next card."""
#     # Create a new Starknet class that simulates the StarkNet
#     # system.

#     _, account1, account2, contract = contract_factory

#     p1 = await contract.get_player1().invoke()
#     p2 = await contract.get_player2().invoke()
#     tt = await contract.get_trump().invoke()
#     assert (
#         (p1.result == (account1.contract.contract_address,))
#         and (p2.result == (account2.contract.contract_address,))
#         and (tt.result == (3,))
#     )


# @pytest.mark.asyncio
# async def test_send_challenge1(contract_factory):
#     """Test draw next card."""
#     # Create a new Starknet class that simulates the StarkNet
#     # system.

#     _, account1, account2, contract = contract_factory

#     await account1.signer.send_transaction(
#         account=account1.contract,
#         to=contract.contract_address,
#         selector_name="join_game",
#         calldata=[],
#     )
#     await account2.signer.send_transaction(
#         account=account2.contract,
#         to=contract.contract_address,
#         selector_name="join_game",
#         calldata=[],
#     )

#     idx = 2
#     await account1.signer.send_transaction(
#         account=account1.contract,
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

    _, account1, account2, contract = contract_factory

    player1 = account1.contract
    player2 = account2.contract
    address1 = account1.contract.contract_address
    address2 = account2.contract.contract_address
    game = contract.contract_address

    # player are joining the game. player1 is a challenger
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="join_game", calldata=[]
    )
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="join_game", calldata=[]
    )

    # ---------------------- ROUND 1 ----------------------------
    idx1 = 1  # C6
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="send_challenge1", calldata=[idx1]
    )
    idx2 = 3  # CJ
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="send_response1", calldata=[idx2],
    )
    # assert that player 2 won the round with pile1 = 0 and pile2 = 2
    pile1 = await contract.get_pile(address1).invoke()
    pile2 = await contract.get_pile(address2).invoke()
    assert pile1.result == (0,) and pile2.result == (2,)

    # assert that challenger and responder got swapped
    challenger = await contract.get_challenger().invoke()
    responder = await contract.get_responder().invoke()
    assert challenger.result == (address2,) and responder.result == (address1,)

    # assert that drawn cards are C8 and CK
    card1 = await contract.get_card(address1, 1).invoke()
    card2 = await contract.get_card(address2, 3).invoke()
    assert card1.result == (2,) and card2.result == (7,)

    # ---------------------- ROUND 2 ----------------------------
    # player2 challenges player1
    idx1 = 3  # CK
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="send_challenge1", calldata=[idx1]
    )
    idx2 = 2  # CA
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="send_response1", calldata=[idx2],
    )
    # assert that player 1 won the round with pile1 = 15 and pile2 = 2
    pile1 = await contract.get_pile(address1).invoke()
    pile2 = await contract.get_pile(address2).invoke()
    assert pile1.result == (15,) and pile2.result == (2,)
    # assert that challenger and responder got swapped
    challenger = await contract.get_challenger().invoke()
    responder = await contract.get_responder().invoke()
    assert challenger.result == (address1,) and responder.result == (address2,)

    # assert that drawn cards are HK and HQ
    card1 = await contract.get_card(address1, 2).invoke()
    card2 = await contract.get_card(address2, 3).invoke()
    assert card1.result == (25,) and card2.result == (24,)

    # ---------------------- ROUND 3 ----------------------------
    # player1 challenges player2
    idx1 = 2  # HK
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="send_challenge1", calldata=[idx1]
    )
    idx2 = 2  # SQ
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="send_response1", calldata=[idx2],
    )
    # assert that player 1 won the round with pile1 = 15 and pile2 = 9
    pile1 = await contract.get_pile(address1).invoke()
    pile2 = await contract.get_pile(address2).invoke()
    assert pile1.result == (15,) and pile2.result == (9,)
    # assert that challenger and responder got swapped
    challenger = await contract.get_challenger().invoke()
    responder = await contract.get_responder().invoke()
    assert challenger.result == (address2,) and responder.result == (address1,)

    # assert that drawn cards are HK and HQ
    card1 = await contract.get_card(address1, 2).invoke()
    card2 = await contract.get_card(address2, 2).invoke()
    assert card1.result == (29,) and card2.result == (30,)

    # ---------------------- ROUND 4 ----------------------------
    # player1 challenges player2
    idx1 = 1  # HK
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="send_challenge1", calldata=[idx1]
    )
    idx2 = 2  # SQ
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="send_response1", calldata=[idx2],
    )
    # assert that player 1 won the round with pile1 = 25 and pile2 = 9
    pile1 = await contract.get_pile(address1).invoke()
    pile2 = await contract.get_pile(address2).invoke()
    assert pile1.result == (25,) and pile2.result == (9,)
    # assert that challenger and responder got swapped
    challenger = await contract.get_challenger().invoke()
    responder = await contract.get_responder().invoke()
    assert challenger.result == (address1,) and responder.result == (address2,)

    # assert that drawn cards are HK and HQ
    card1 = await contract.get_card(address1, 2).invoke()
    card2 = await contract.get_card(address2, 1).invoke()
    assert card1.result == (34,) and card2.result == (12,)


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
