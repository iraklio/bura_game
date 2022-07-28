
from engine import Card
from starkware.starkware_utils.error_handling import StarkException

from utils import TestSigner as Signer

import logging

logger = logging.getLogger("Bura.Player")
handler  = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s|%(name)s|%(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


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
    

    async def is_mover(self) -> bool:
        mover = (await self.bura_contract.get_mover().invoke()).result[0]
        return mover == self.account.contract_address


    async def retrieve_trump(self):
        trump = (await self.bura_contract.get_trump().invoke()).result[0]
        return trump


    async def retrieve_score(self):        
        (s1, s2) = (await self.bura_contract.get_scores().invoke()).result
        return s1 - 21, s2 - 21
    
    async def challenge(self, idxs:list) -> bool:
        try:            
            selector_name = f"send_challenge{len(idxs)}"            
            await self.signer.send_transaction(
                    account=self.account,
                    to=self.bura_contract.contract_address,
                    selector_name=selector_name,
                    calldata=idxs,
                )                
            logger.info(f'Calling: {selector_name}({idxs})')
            return True
        except StarkException:
            logger.info(f'challenge(): Exception thrown when sending a challenge')
            return False


    async def response(self, idxs:list):
        try:
            selector_name = f"send_response{len(idxs)}"
            resp = (await self.signer.send_transaction(
                        account=self.account,
                        to=self.bura_contract.contract_address,
                        selector_name=selector_name,
                        calldata=idxs,
                    )).result[0]

            logger.info(f'Calling: {selector_name}({idxs})')
            return (True, []) if resp[0] == 99 else (True, [ Card(x) for x in resp ])
        except StarkException:
            logger.info(f'response(): Exception thrown when sending a response')
            return (False, [])


    async def claim_win(self) -> bool:
        try:
            status = (await self.signer.send_transaction(
                    account=self.account,
                    to=self.bura_contract.contract_address,
                    selector_name='claim_win',
                    calldata=[],
                )).result[0]            
            logger.info(f'Calling: claim_win(). Game state = {status}')
            return status
        except StarkException:            
            return []
    
    async def raise_point_challenge(self) -> bool:
        try:
            await self.signer.send_transaction(
                    account=self.account,
                    to=self.bura_contract.contract_address,
                    selector_name='raise_point_challenge',
                    calldata=[],
                )
            logger.info(f'Calling: raise_point_challenge()')
            return True
        except StarkException:
            logger.info(f'Failed calling: raise_point_challenge()')            
            return False



    async def raise_point_response(self, accept):
        selector_name = 'raise_point_accept' if accept else 'raise_point_decline'
        try:
            status = (await self.signer.send_transaction(
                    account=self.account,
                    to=self.bura_contract.contract_address,
                    selector_name=selector_name,
                    calldata=[],
                )).result[0]
            logger.info(f'Calling: {selector_name}({accept})')
            return (True, status)
        except StarkException:
            logger.info(f'Failed calling: {selector_name}({accept})')
            return (False, None)

        
        