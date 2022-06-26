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
    calldata = [1, 2]  # C6, CA
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="send_challenge2", calldata=calldata
    )
    calldata = [2, 3]  # SQ, CJ
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="send_response2", calldata=calldata,
    )
    # assert that player 2 won the round with pile1 = 0 and pile2 = 16
    pile1 = await contract.get_pile(address1).invoke()
    pile2 = await contract.get_pile(address2).invoke()
    assert pile1.result == (0,) and pile2.result == (16,)

    # assert that challenger and responder got swapped
    challenger = await contract.get_challenger().invoke()
    responder = await contract.get_responder().invoke()
    assert challenger.result == (address2,) and responder.result == (address1,)

    # assert that drawn cards are C8,HQ and CK HK
    card11 = await contract.get_card(address1, 1).invoke()
    card12 = await contract.get_card(address1, 2).invoke()
    card21 = await contract.get_card(address2, 2).invoke()
    card22 = await contract.get_card(address2, 3).invoke()
    assert (
        card11.result == (2,)
        and card12.result == (24,)
        and card21.result == (7,)
        and card22.result == (25,)
    )

    # ---------------------- ROUND 2 ----------------------------
    calldata = [1, 3]  # H10, HK
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="send_challenge2", calldata=calldata
    )
    calldata = [1, 3]  # C8, D7
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="send_response2", calldata=calldata,
    )
    # assert that player 2 won the round with pile1 = 0 and pile2 = 30
    pile1 = await contract.get_pile(address1).invoke()
    pile2 = await contract.get_pile(address2).invoke()
    assert pile1.result == (0,) and pile2.result == (30,)

    # assert that challenger and responder got swapped
    challenger = await contract.get_challenger().invoke()
    responder = await contract.get_responder().invoke()
    assert challenger.result == (address2,) and responder.result == (address1,)

    # assert that drawn cards are S8,D9 and S9 SK
    card11 = await contract.get_card(address1, 1).invoke()
    card12 = await contract.get_card(address1, 3).invoke()
    card21 = await contract.get_card(address2, 1).invoke()
    card22 = await contract.get_card(address2, 3).invoke()
    assert (
        card11.result == (29,)
        and card12.result == (12,)
        and card21.result == (30,)
        and card22.result == (34,)
    )

    # ---------------------- ROUND 3 ----------------------------
    calldata = [2]  # CK
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="send_challenge1", calldata=calldata
    )
    calldata = [3]  # D9
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="send_response1", calldata=calldata,
    )
    # assert that player 2 won the round with pile1 = 0 and pile2 = 34
    pile1 = await contract.get_pile(address1).invoke()
    pile2 = await contract.get_pile(address2).invoke()
    assert pile1.result == (0,) and pile2.result == (34,)

    # assert that challenger and responder got swapped
    assert (await contract.get_challenger().invoke()).result == (address2,)
    assert (await contract.get_responder().invoke()).result == (address1,)

    # assert that drawn cards are H7 and SA
    assert (await contract.get_card(address1, 3).invoke()).result == (19,)
    assert (await contract.get_card(address2, 2).invoke()).result == (35,)

    # ---------------------- ROUND 4 ----------------------------
    calldata = [1, 2, 3]  # S9, SA, SK
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="send_challenge3", calldata=calldata
    )
    calldata = [1, 2, 3]  # S8, HQ, H7
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="send_response3", calldata=calldata,
    )
    # assert that player 2 won the round with pile1 = 0 and pile2 = 52

    assert (await contract.get_pile(address1).invoke()).result == (0,)
    assert (await contract.get_pile(address2).invoke()).result == (52,)

    # assert that challenger and responder got swapped
    assert (await contract.get_challenger().invoke()).result == (address2,)
    assert (await contract.get_responder().invoke()).result == (address1,)

    # assert that drawn cards are S8,D9 and S9 SK
    assert (await contract.get_card(address1, 1).invoke()).result == (13,)
    assert (await contract.get_card(address1, 2).invoke()).result == (26,)
    assert (await contract.get_card(address1, 3).invoke()).result == (14,)
    assert (await contract.get_card(address2, 1).invoke()).result == (3,)
    assert (await contract.get_card(address2, 2).invoke()).result == (28,)
    assert (await contract.get_card(address2, 3).invoke()).result == (9,)

    # player 2 raise the bet, and player 1 accepts it
    assert (await contract.get_round_point_challenge_sent().invoke()).result == (0,)
    await account2.signer.send_transaction(
        account=player2,
        to=game,
        selector_name="raise_round_point_challenge",
        calldata=[],
    )
    assert (await contract.get_round_point_caller().invoke()).result == (address2,)
    assert (await contract.get_round_point_challenge_sent().invoke()).result == (1,)
    assert (await contract.get_round_point().invoke()).result == (1,)

    await account1.signer.send_transaction(
        account=player1,
        to=game,
        selector_name="raise_round_point_responce",
        calldata=[1],
    )

    assert (await contract.get_round_point_challenge_sent().invoke()).result == (0,)
    assert (await contract.get_round_point().invoke()).result == (2,)
    assert (await contract.get_round_point_caller().invoke()).result == (address2,)

    # ---------------------- ROUND 5 ----------------------------
    calldata = [1, 2, 3]  # S9, SA, SK
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="claim_win", calldata=[]
    )
    # assert that piles have been reset
    assert (await contract.get_pile(address1).invoke()).result == (0,)
    assert (await contract.get_pile(address2).invoke()).result == (0,)
    # assert player 2 is leading 2:0
    assert (await contract.get_score(address1).invoke()).result == (0,)
    assert (await contract.get_score(address2).invoke()).result == (2,)

    # assert that drawn cards are S8,D9 and S9 SK
    # assert (await contract.get_card(address1, 1).invoke()).result == (13,)
    # assert (await contract.get_card(address1, 2).invoke()).result == (26,)
    # assert (await contract.get_card(address1, 3).invoke()).result == (14,)
    # assert (await contract.get_card(address2, 1).invoke()).result == (3,)
    # assert (await contract.get_card(address2, 2).invoke()).result == (28,)
    # assert (await contract.get_card(address2, 3).invoke()).result == (9,)
