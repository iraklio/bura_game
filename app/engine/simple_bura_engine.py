
from starkware.starkware_utils.error_handling import StarkException
from utils import TestSigner as Signer


class Card():
    def __init__(self, id:int):
        (s,r) = divmod(id,9)
        self.id = id
        self.rank = r
        self.suit = s
        

    def get_point(self) -> int:
        if self.rank == 4:
            return 10
        elif self.rank == 5:
            return 2
        elif self.rank == 6:
            return 3
        elif self.rank == 7:
            return 4
        elif self.rank == 8:
            return 11
        else:
            return 0

    def get_rank_str(self) -> str:
        return "6789TJQKA"[self.rank]        

    def get_suit_str(self) -> str:    
        return "CDHS"[self.suit]
    
    def get_card_str(self) -> str:        
        r = "6789TJQKA"[self.rank]
        s = "♣♦♥♠"[self.suit]
        return r + s
    


class SimpleBuraEngine():

    def __init__(self) -> None:

        self.pile = []
        self.pile_count = 0
        self.pile_other = []
        self.unplayed_cards = range(36)

    
    @classmethod
    async def create(cls, starknet, bura_contract):

        self = SimpleBuraEngine()
        self.signer = Signer(private_key=12345)
        self.account = await starknet.deploy("contracts/Account.cairo", constructor_calldata=[self.signer.public_key])    
        self.bura_contract = bura_contract
        await self.signer.send_transaction(account=self.account, to=bura_contract.contract_address, selector_name="join_game", calldata=[3])

        return self


    async def retrieve_hand(self):
    # assert that drawn cards are C8,HQ and CK HK
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
    

    async def retrieve_challenge(self) -> list:        
        try:
            ctype = (await self.bura_contract.get_challenge_type().invoke()).result[0]            
            if ctype == 1:
                c1 = (await self.bura_contract.get_challenge1().invoke()).result[0]
                return [Card(c1)]
            elif ctype == 2:                
                (c1, c2) = (await self.bura_contract.get_challenge2().invoke()).result
                return [Card(c1), Card(c2)]
            elif ctype == 3:
                (c1, c2, c3) =  (await self.bura_contract.get_challenge3().invoke()).result
                return [Card(c1), Card(c2), Card(c3)]
            else:
                print(f"Invalid challenge type: {ctype}")
                return []

        except StarkException:            
            print('Error in retrieve_challenge')
            return []

    async def retrieve_trump(self):
        trump = (await self.bura_contract.get_trump().invoke()).result[0]
        return trump


    async def challenge(self) -> list:
        try:
            selector_name, calldata = await self.calculate_challenge()        
            await self.signer.send_transaction(
                    account=self.account,
                    to=self.bura_contract.contract_address,
                    selector_name=selector_name,
                    calldata=calldata,
                )
            return calldata            
        except StarkException:            
            return []
        

    async def calculate_challenge(self) -> list:
        (c1, c2, c3) = await self.retrieve_hand()
        trump = await self.retrieve_trump()
        calldata = []
        if c1.suit == c2.suit and c2.suit == c3.suit:
            calldata = [1, 2, 3]
        elif c1.suit == c2.suit:
            calldata =  [1, 2]
        elif c2.suit == c3.suit:
            calldata =  [2, 3]
        elif c1.suit == c3.suit:
            calldata =  [1, 3]
        else:
            if c1.rank <=3 and c1.suit != trump:
                calldata =  [1]
            elif c2.rank <=3 and c2.suit != trump:
                calldata =  [2]
            elif c3.rank <=3 and c3.suit != trump:
                calldata = [3]
            elif c1.rank in [5, 6, 7] and c1.suit != trump:
                calldata = [1]
            elif c2.rank in [5, 6, 7] and c2.suit != trump:
                calldata =  [2]
            elif c3.rank in [5, 6, 7] and c3.suit != trump:
                calldata =  [3]
            else:
                calldata = [1]
        
        selector_name = f"send_challenge{len(calldata)}"
        return selector_name, calldata


    async def response(self) -> list:
        selector_name, calldata = await self.calculate_response()
        response = (
            await self.signer.send_transaction(
                account=self.account,
                to=self.bura_contract.contract_address,
                selector_name=selector_name,
                calldata=calldata,
            )
        ).result[0]

        print("response: ", response)

        if response[0] == 99:
            return []
        else:
            res = []
            for r in response:
                res.append(Card(r))
            return res

    async def calculate_response(self) -> list:
        (c1, c2, c3) = await self.retrieve_hand()        
        hand = (c1, c2, c3)
        trump = await self.retrieve_trump()
        ch = await self.retrieve_challenge()

        calldata = []
        selector_name = ""
        idx_point = []
        if len(ch) == 1:
            selector_name = "send_response1"
            for (i,c) in enumerate(hand):
                idx_point.append((i+1, c.get_point()))
                if c.suit == ch[0].suit:
                    if c.rank > ch[0].rank:
                        calldata = [i+1]
                        break
                elif c.suit == trump:
                    calldata = [i+1]
                    break

            if not calldata:
                idx_point.sort(key=lambda x: x[1])
                calldata = [idx_point[0][0]]                    

        elif len(ch) == 2:
            selector_name = "send_response2"
            chs = sort(ch, trump)
            o1 = chs[0]
            o2 = chs[1]
            if less(o1, c1, trump) and less(o2, c2, trump):
                calldata =  [1, 2]
            elif less(o1, c1, trump) and less(o2, c3, trump):
                calldata =  [1, 3]
            elif less(o1, c2, trump) and less(o2, c3, trump):
                calldata =  [2, 3]
            else:
                for (i,c) in enumerate(hand):
                    idx_point.append((i+1, c.get_point()))
                idx_point.sort(key=lambda x: x[1])
                calldata = [idx_point[0][0], idx_point[1][0]]

        elif len(ch) == 3:
            selector_name = "send_response3"
            calldata = [ 1, 2, 3]


        print("calldata", calldata)
        return selector_name, calldata
      
    
    async def claim(self) -> bool:
        """Claim win and return the result - won/lost."""
        pass

    
    async def raise_challenge(self) -> bool:
        """Raise the point bet"""
        pass

    async def raise_respond(self) -> bool:
        """Respond to raise from the opponent"""
        pass



def less(c1, c2, trump) -> bool:
    return c1.rank < c2.rank if c1.suit == c2.suit else c2.suit == trump
    

def sort(cards, trump) -> list:
    if len(cards) == 0 or len(cards) == 1:
        return cards

    if len(cards) == 2:
        c1 = cards[0]
        c2 = cards[1]
        if less(c1, c2, trump):
            return [c1, c2]
        else:
            return [c2, c1]

    if len(cards) == 3:
        c1 = cards[0]
        c2 = cards[1]
        c3 = cards[2]
        if less(c2, c1, trump):
            (c1, c2) = (c2, c1)
        if less(c3, c2, trump):
            (c2, c3) = (c3, c2)
        if less(c2, c1, trump):
            (c1, c2) = (c2, c1)
        return [c1, c2, c3]
