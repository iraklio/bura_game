from engine.simple_bura_engine import SimpleBuraEngine
from engine.simple_bura_engine import Card
from starkware.starkware_utils.error_handling import StarkException

from utils import TestSigner as Signer

class BuraPlayer():
    def __init__(self) -> None:
        pass
        

    @classmethod
    async def create(cls, starknet, bura_contract):
        self = BuraPlayer()

        self.signer = Signer(private_key=12345679)
        self.account = await starknet.deploy("contracts/Account.cairo", constructor_calldata=[self.signer.public_key])    
        self.bura_contract = bura_contract
        await self.signer.send_transaction(
            account=self.account, to=bura_contract.contract_address, selector_name="join_game", calldata=[3])
        return self

    async def retrieve_hand(self):    
        cards = (
            await self.signer.send_transaction(
                account=self.account,
                to=self.bura_contract.contract_address,
                selector_name="get_cards",
                calldata=[],
            )
        ).result[0]

        (c1, c2, c3) = cards
        return (Card(c1), Card(c2), Card(c3))
    

    async def retrieve_trump(self):
        trump = (await self.bura_contract.get_trump().invoke()).result[0]
        return trump


    

    async def challenge(self, idxs:list) -> bool:
        try:
            selector_name = f"send_challenge{len(idxs)}"
            await self.signer.send_transaction(
                    account=self.account,
                    to=self.bura_contract.contract_address,
                    selector_name=selector_name,
                    calldata=idxs,
                )            
            return True            
        except StarkException:            
            return False




    async def respond(self, idxs:list) -> bool:
        try:
            selector_name = f"send_response{len(idxs)}"
            await self.signer.send_transaction(
                    account=self.account,
                    to=self.bura_contract.contract_address,
                    selector_name=selector_name,
                    calldata=idxs,
                )            
            return True            
        except StarkException:            
            return False
    

        
        