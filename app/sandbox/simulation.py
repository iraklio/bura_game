from cgi import test
import warnings
from dataclasses import dataclass
from typing import Tuple

warnings.filterwarnings("ignore", category=DeprecationWarning)
import asyncio

from starkware.starknet.testing.starknet import Starknet, StarknetContract
from starkware.starkware_utils.error_handling import StarkException
from utils import TestSigner as Signer


class Suit:
    def __init__(self, s):
        self.suit = "♣♦♥♠"[s]

    def print(self):
        return self.suit


class Card:
    def __init__(self, card):
        (s, r) = divmod(card, 9)
        self.value = "6789TJQKA"[r]
        self.suit = "♣♦♥♠"[s]

    def print(self):
        return self.value + self.suit


@dataclass
class Account:
    signer: Signer
    contract: StarknetContract


async def get_cards(pp, account, contract):
    # assert that drawn cards are C8,HQ and CK HK
    cards = (
        await account.signer.send_transaction(
            account=account.contract,
            to=contract.contract_address,
            selector_name="get_cards",
            calldata=[],
        )
    ).result[0]

    (c1, c2, c3) = cards  # (cards[0], cards[1], cards[2])

    print(
        "Player " + pp + " cards:",
        Card(c1).print(),
        Card(c2).print(),
        Card(c3).print(),
    )

    return (c1, c2, c3)


async def raise_point_challenge(pp, account, contract):
    raise_point = input("Raise Point? ")
    if raise_point.lower() == "y":
        await account.signer.send_transaction(
            account=account.contract,
            to=contract.contract_address,
            selector_name="raise_point_challenge",
            calldata=[],
        )
        print("Player " + pp + " offered point raise.")
        return True
    else:
        return False


async def raise_point_response(pp, account, contract):
    raise_point = input("Accept the Raise Point? ")
    if raise_point.lower() == "y":
        print("Player " + pp + " accepts point raise.")
        status = (
            await account.signer.send_transaction(
                account=account.contract,
                to=contract.contract_address,
                selector_name="raise_point_accept",
                calldata=[],
            )
        ).result[0]
        (round_state, game_state) = (status[0], status[1])
        return (round_state, game_state)
    else:
        print("Player " + pp + " declines point raise.")
        status = (
            await account.signer.send_transaction(
                account=account.contract,
                to=contract.contract_address,
                selector_name="raise_point_decline",
                calldata=[],
            )
        ).result[0]
        (round_state, game_state) = (status[0], status[1])

        print("Player " + pp + " lost the round")
        scores = (await contract.get_scores().invoke()).result
        print(
            "Game score: Player 1: "
            + str(scores[0] - 21)
            + ". Player 2: "
            + str(scores[1] - 21)
        )
        print("Starting a new round... ")
        trump = (await contract.get_trump().invoke()).result[0]
        print("Trump suit:", Suit(trump).print())
        return (round_state, game_state)


async def claim_win(pp, account, contract):
    claim_win = input("Claim Win? ")
    if claim_win.lower() == "y":
        status = (
            await account.signer.send_transaction(
                account=account.contract,
                to=contract.contract_address,
                selector_name="claim_win",
                calldata=[],
            )
        ).result[0]
        (round_state, game_state) = (status[0], status[1])

        if round_state == 1:
            print("Player " + pp + " claimed and won")
        else:
            print("Player " + pp + " claimed and lost")

        scores = (await contract.get_scores().invoke()).result

        print(
            "Game score: Player 1: "
            + str(scores[0] - 21)
            + ". Player 2: "
            + str(scores[1] - 21)
        )
        print("Starting a new round... ")
        trump = (await contract.get_trump().invoke()).result[0]
        print("Trump suit:", Suit(trump).print())
        return (round_state, game_state)
    else:
        return (2, 2)


async def send_challenge(account, contract, cards):
    try:
        idxs = input("Enter card(s) to play: ")
        idxs = idxs.split(" ")
        if len(idxs) == 1:
            await account.signer.send_transaction(
                account=account.contract,
                to=contract.contract_address,
                selector_name="send_challenge1",
                calldata=[int(idxs[0])],
            )

            (c) = (await contract.get_challenge1().invoke()).result
            print(c)
            print("Challenge: ", Card(cards[int(idxs[0]) - 1]).print())

        elif len(idxs) == 2:
            await account.signer.send_transaction(
                account=account.contract,
                to=contract.contract_address,
                selector_name="send_challenge2",
                calldata=[int(idxs[0]), int(idxs[1])],
            )
            
            (res1, res2) = (await contract.get_challenge2().invoke()).result     
            print((res1, res2))




            print(
                "Challenge: ",
                Card(cards[int(idxs[0]) - 1]).print(),
                Card(cards[int(idxs[1]) - 1]).print(),
            )
        else:
            await account.signer.send_transaction(
                account=account.contract,
                to=contract.contract_address,
                selector_name="send_challenge3",
                calldata=[int(idxs[0]), int(idxs[1]), int(idxs[2])],
            )
            print(
                "Challenge: ",
                Card(cards[int(idxs[0]) - 1]).print(),
                Card(cards[int(idxs[1]) - 1]).print(),
                Card(cards[int(idxs[2]) - 1]).print(),
            )
    except StarkException:
        print("Transaction failed. Please try again...")
        await send_challenge(account, contract, cards)


async def send_response(account, contract):
    try:
        idxs = input("Enter card(s) to play: ")
        idxs = idxs.split(" ")
        if len(idxs) == 1:
            resp = (
                await account.signer.send_transaction(
                    account=account.contract,
                    to=contract.contract_address,
                    selector_name="send_response1",
                    calldata=[int(idxs[0])],
                )
            ).result[0]

            if int(resp[0]) != 99:
                print("Response:", Card(int(resp[0])).print())

        elif len(idxs) == 2:
            resp = (
                await account.signer.send_transaction(
                    account=account.contract,
                    to=contract.contract_address,
                    selector_name="send_response2",
                    calldata=[int(idxs[0]), int(idxs[1])],
                )
            ).result[0]
            if int(resp[0]) != 99:
                print(
                    "Response:", Card(int(resp[0])).print(), Card(int(resp[1])).print()
                )

        else:
            resp = (
                await account.signer.send_transaction(
                    account=account.contract,
                    to=contract.contract_address,
                    selector_name="send_response3",
                    calldata=[int(idxs[0]), int(idxs[1]), int(idxs[2])],
                )
            ).result[0]
            if int(resp[0]) != 99:
                print(
                    "Response:",
                    Card(int(resp[0])).print(),
                    Card(int(resp[1])).print(),
                    Card(int(resp[2])).print(),
                )
    except StarkException:
        print("Transaction failed. Please try again...")
        await send_response(account, contract)


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


async def make_a_move(type, mname, mcontract, oname, ocontract, game_contract):
    cards = await get_cards(mname, mcontract, game_contract)
    (round_state, game_state) = await claim_win(mname, mcontract, game_contract)
    if round_state != 2:
        if game_state == 0:
            print("Game Over: Player " + oname + " won")
            return 0
        elif game_state == 1:
            print("Game Over: Player " + mname + " won")
            return 0
        else:
            return 1
    elif await raise_point_challenge(mname, mcontract, game_contract):
        round_state, game_state = await raise_point_response(
            oname, ocontract, game_contract
        )
        if round_state != 2:
            if game_state == 1:
                print("Game Over: Player " + mname + " won")
                return 0
            else:
                return 1
        else:
            if type == "C":
                await send_challenge(mcontract, game_contract, cards)                
            else:
                await send_response(mcontract, game_contract)
    else:
        if type == "C":
            await send_challenge(mcontract, game_contract, cards)            
        else:
            await send_response(mcontract, game_contract)

    return 2


async def game_simulator():

    starknet, account1, account2, bura_game = await contract_factory()

    player1 = account1.contract
    player2 = account2.contract
    address1 = account1.contract.contract_address
    address2 = account2.contract.contract_address
    game = bura_game.contract_address

    print("Player 1 joined from: ", address1)
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="join_game", calldata=[3]
    )

    print("Player 2 joined from: ", address2)
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="join_game", calldata=[5]
    )

    trump = (await bura_game.get_trump().invoke()).result[0]
    print("Trump suit:", Suit(trump).print())

    pmap = {}
    pmap[address1] = (account1, "1")
    pmap[address2] = (account2, "2")

    for x in range(100):

        challenger = (await bura_game.get_mover().invoke()).result[0]
        responder = (await bura_game.get_other().invoke()).result[0]

        print(challenger)

        (mcontract, mname) = pmap[challenger]
        (ocontract, oname) = pmap[responder]
        print("--------------------------------------------")

        print("Mover: Player " + mname)
        print("Other: Player " + oname)

        status = await make_a_move("C", mname, mcontract, oname, ocontract, bura_game)
        if status == 0:
            break
        elif status == 1:
            continue

        status = await make_a_move("R", oname, ocontract, mname, mcontract, bura_game)
        if status == 0:
            break
        elif status == 1:
            continue


loop = asyncio.get_event_loop()
loop.run_until_complete(game_simulator())
loop.close()

