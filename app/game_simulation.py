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
    card11 = (
        await account.signer.send_transaction(
            account=account.contract,
            to=contract.contract_address,
            selector_name="get_card",
            calldata=[1],
        )
    ).result[0][0]
    card12 = (
        await account.signer.send_transaction(
            account=account.contract,
            to=contract.contract_address,
            selector_name="get_card",
            calldata=[2],
        )
    ).result[0][0]
    card13 = (
        await account.signer.send_transaction(
            account=account.contract,
            to=contract.contract_address,
            selector_name="get_card",
            calldata=[3],
        )
    ).result[0][0]

    print(
        "Player " + pp + " cards:",
        Card(card11).print(),
        Card(card12).print(),
        Card(card13).print(),
    )


async def send_challenge(account, contract):
    idxs = input("Enter card(s) to play: ")
    idxs = idxs.split(" ")
    if len(idxs) == 1:
        await account.signer.send_transaction(
            account=account.contract,
            to=contract.contract_address,
            selector_name="send_challenge1",
            calldata=[int(idxs[0])],
        )
        ch1 = (await contract.get_challenge(1).invoke()).result[0]
        print("Challenge: ", Card(ch1).print())

    elif len(idxs) == 2:
        await account.signer.send_transaction(
            account=account.contract,
            to=contract.contract_address,
            selector_name="send_challenge2",
            calldata=[int(idxs[0]), int(idxs[1])],
        )
        ch1 = (await contract.get_challenge(1).invoke()).result[0]
        ch2 = (await contract.get_challenge(2).invoke()).result[0]
        print("Challenge: ", Card(ch1).print(), Card(ch2).print())
    else:
        await account.signer.send_transaction(
            account=account.contract,
            to=contract.contract_address,
            selector_name="send_challenge3",
            calldata=[int(idxs[0]), int(idxs[1]), int(idxs[2])],
        )
        ch1 = (await contract.get_challenge(1).invoke()).result[0]
        ch2 = (await contract.get_challenge(2).invoke()).result[0]
        ch3 = (await contract.get_challenge(3).invoke()).result[0]
        print("Challenge: ", Card(ch1).print(), Card(ch2).print(), Card(ch3).print())


async def send_response(account, contract):
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
            print("Response:", Card(int(resp[0])).print(), Card(int(resp[1])).print())

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


async def game_simulator():

    starknet, account1, account2, contract = await contract_factory()

    player1 = account1.contract
    player2 = account2.contract
    address1 = account1.contract.contract_address
    address2 = account2.contract.contract_address
    game = contract.contract_address

    print("player 1 joined from: ", address1)
    await account1.signer.send_transaction(
        account=player1, to=game, selector_name="join_game", calldata=[3]
    )

    print("player 2 joined from: ", address2)
    await account2.signer.send_transaction(
        account=player2, to=game, selector_name="join_game", calldata=[5]
    )

    trump = (await contract.get_trump().invoke()).result[0]
    print("Trump suit:", Suit(trump).print())

    for x in range(6):
        challenger = (await contract.get_challenger().invoke()).result[0]
        responder = (await contract.get_responder().invoke()).result[0]

        if challenger == address1:
            print("Challenger: Player 1")
            print("Responder:  Player 2")
        else:
            print("Challenger: Player 2")
            print("Responder:  Player 1")

        if challenger == address1:
            await get_cards("1", account1, contract)
            await send_challenge(account1, contract)
        else:
            await get_cards("2", account2, contract)
            await send_challenge(account2, contract)

        if responder == address1:
            await get_cards("1", account1, contract)
            await send_response(account1, contract)
        else:
            await get_cards("2", account2, contract)
            await send_response(account2, contract)


loop = asyncio.get_event_loop()
loop.run_until_complete(game_simulator())
loop.close()

