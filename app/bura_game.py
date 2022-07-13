from cgi import test
import warnings
from dataclasses import dataclass
from typing import Tuple

import math

warnings.filterwarnings("ignore", category=DeprecationWarning)
import asyncio

from starkware.starknet.testing.starknet import Starknet, StarknetContract
from starkware.starkware_utils.error_handling import StarkException
from utils import TestSigner as Signer

import pygame as pygame
import sys
import time

grey = (220, 220, 220)
black = (0, 0, 0)
green = (0, 200, 0)
red = (255, 0, 0)
light_slat = (119, 136, 153)
dark_slat = (47, 79, 79)
dark_red = (255, 0, 0)

display_width, display_height = 900, 700
background_color =  (34,139,34)
grey = (220,220,220)




#button display
def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac, (x, y, w, h))
        if click[0] == 1 != None:
            action()
    else:
        pygame.draw.rect(gameDisplay, ic, (x, y, w, h))

    TextSurf, TextRect = text_objects(msg, font)
    TextRect.center = ((x + (w/2)), (y + (h/2)))
    gameDisplay.blit(TextSurf, TextRect)



@dataclass
class Account:
    signer: Signer
    contract: StarknetContract

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


# async def game_simulator():

#     starknet, account1, account2, bura_game = await contract_factory()

#     player1 = account1.contract
#     player2 = account2.contract
#     address1 = account1.contract.contract_address
#     address2 = account2.contract.contract_address
#     game = bura_game.contract_address

#     # print("Player 1 joined from: ", address1)
#     # await account1.signer.send_transaction(
#     #     account=player1, to=game, selector_name="join_game", calldata=[3]
#     # )

#     # print("Player 2 joined from: ", address2)
#     # await account2.signer.send_transaction(
#     #     account=player2, to=game, selector_name="join_game", calldata=[5]
#     # )

#     # trump = (await bura_game.get_trump().invoke()).result[0]
#     # print("Trump suit:", trump)

#     pmap = {}
#     pmap[address1] = (account1, "1")
#     pmap[address2] = (account2, "2")

#     pygame.init()

#     clock = pygame.time.Clock()

#     gameDisplay = pygame.display.set_mode((display_width, display_height))
#     pygame.display.set_caption('Bura')

#     gameDisplay.fill(background_color)
#     pygame.draw.rect(gameDisplay, grey, pygame.Rect(0, 0, 250, 700))


#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False

#             # button("Deal", 30, 100, 150, 50, light_slat, dark_slat, play_blackjack.deal)
#             # button("Hit", 30, 200, 150, 50, light_slat, dark_slat, play_blackjack.hit)
#             # button("Stand", 30, 300, 150, 50, light_slat, dark_slat, play_blackjack.stand)
#             # button("EXIT", 30, 500, 150, 50, light_slat, dark_red, play_blackjack.exit)
        
#         pygame.display.flip()

#     # for x in range(100):

#     #     challenger = (await bura_game.get_mover().invoke()).result[0]
#     #     responder = (await bura_game.get_other().invoke()).result[0]

#     #     (mcontract, mname) = pmap[challenger]
#     #     (ocontract, oname) = pmap[responder]
#     #     print("--------------------------------------------")

#     #     print("Mover: Player " + mname)
#     #     print("Other: Player " + oname)

#     #     status = await make_a_move("C", mname, mcontract, oname, ocontract, bura_game)
#     #     if status == 0:
#     #         break
#     #     elif status == 1:
#     #         continue

#     #     status = await make_a_move("R", oname, ocontract, mname, mcontract, bura_game)
#     #     if status == 0:
#     #         break
#     #     elif status == 1:
#     #         continue


# loop = asyncio.get_event_loop()
# loop.run_until_complete(game_simulator())
# loop.close()



pygame.init()
font = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()
gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Bura')

gameDisplay.fill(background_color)
#pygame.draw.rect(gameDisplay, grey, pygame.Rect(0, 0, 250, 700))



# def display_card(card_location:int, card_name:str, selected:bool, event) -> bool:
#     x = 400
#     y = 500    
#     s = 20
#     gap = 40   

#     (mx,my) = pygame.mouse.get_pos()

#     clicked = event.type == pygame.MOUSEBUTTONDOWN

#     c = pygame.image.load('app/img/' + card_name +'.png').convert()
#     print(c.get_rect())
#     (w,h) = c.get_size()
#     lw = 8
#     x += card_location*(w + gap)

#     gameDisplay.blit(c, (x, y))
#     print(c.get_rect())
        
#     border_color = (3,56,100)

#     if x + w > mx > x and y + h > my > y:
#         if not selected and clicked:
#             pygame.draw.line(gameDisplay, border_color, (x, y - lw/2),(x + w + lw - 1 , y - lw /2), width=lw)
#             pygame.draw.line(gameDisplay, border_color, (x + w + lw/2 - 1, y),(x + w + lw/2 - 1 , y + h + lw), width=lw)
#             pygame.draw.line(gameDisplay, border_color, (x - lw, y + h + lw/2),(x + w , y + h + lw/2), width=lw)
#             pygame.draw.line(gameDisplay, border_color, (x - lw/2 - 1, y + h),(x - lw/2 - 1, y - lw + 1), width=lw)
#             selected = True            
#         elif selected and clicked:            
#             pygame.draw.line(gameDisplay, background_color, (x, y - lw/2),(x + w + lw - 1 , y - lw /2), width=lw)
#             pygame.draw.line(gameDisplay, background_color, (x + w + lw/2 - 1, y),(x + w + lw/2 - 1 , y + h + lw), width=lw)
#             pygame.draw.line(gameDisplay, background_color, (x - lw, y + h + lw/2),(x + w , y + h + lw/2), width=lw)
#             pygame.draw.line(gameDisplay, background_color, (x - lw/2 - 1, y + h),(x - lw/2 - 1, y - lw + 1), width=lw)                
#             selected = False            

    
#     return selected


def button_send(player_cards, event):

    x = 450
    y = 650
    w = 144
    h = 40
    inactive_color = (180,180,158)
    active_color = (228,234,23)

    (mx,my) = pygame.mouse.get_pos()
    clicked = event.type == pygame.MOUSEBUTTONDOWN

    pygame.draw.rect(gameDisplay, active_color, (x, y, w, h))



    textSurface = font.render("Send", True, black)
    TextRect = textSurface.get_rect()
    TextRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(textSurface, TextRect)

    if x + w > mx > x and y + h > my > y and clicked:
        for cs in player_cards.sprites():
            if cs.clicked:
                cs.play( 0, -190)   


def button_claim(player_cards, event):

    x = 70
    y = 250
    w = 144
    h = 40
    inactive_color = (180,180,158)
    active_color = (228,234,23)

    (mx,my) = pygame.mouse.get_pos()
    clicked = event.type == pygame.MOUSEBUTTONDOWN

    pygame.draw.rect(gameDisplay, active_color, (x, y, w, h))



    textSurface = font.render("Claim", True, black)
    TextRect = textSurface.get_rect()
    TextRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(textSurface, TextRect)

    if x + w > mx > x and y + h > my > y and clicked:
        pass
        

def button_raise(player_cards, event):

    x = 70
    y = 310
    w = 144
    h = 40
    inactive_color = (180,180,158)
    active_color = (228,234,23)

    (mx,my) = pygame.mouse.get_pos()
    clicked = event.type == pygame.MOUSEBUTTONDOWN

    pygame.draw.rect(gameDisplay, active_color, (x, y, w, h))



    textSurface = font.render("Raise", True, black)
    TextRect = textSurface.get_rect()
    TextRect.center = ((x + (w / 2)), (y + (h / 2)))
    gameDisplay.blit(textSurface, TextRect)

    if x + w > mx > x and y + h > my > y and clicked:
        pass


class CardSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, r = None, s = None):
        super().__init__()

        if r and s:
            self.image = pygame.image.load('app/img/' + r + s + '.png').convert()
            self.active = True
        else:
            self.image = pygame.image.load('app/img/back.png').convert()
            self.active = False

        self.rect = self.image.get_rect(center = (x, y))
        self.clicked = False
        
        self.rank = r
        self.suit = s

    def update(self, event):        
        if event.type == pygame.MOUSEBUTTONDOWN and self.active:
            if self.rect.collidepoint(event.pos):
                if self.clicked == False:
                    self.rect = self.rect.move(0,-25)
                else:
                    self.rect = self.rect.move(0, 25)

                self.clicked = not self.clicked
    
    def play(self, x, y):        
        self.rect = self.rect.move(x,y)
        self.clicked = False
        self.active = False       
        


other_cards = pygame.sprite.Group([
    CardSprite(400, 150 ), 
    CardSprite(520, 150 ),
    CardSprite(640, 150 ) 
    ])

player_cards = pygame.sprite.Group([
    CardSprite(400, 550, '8', 'H'), 
    CardSprite(520, 550, 'K', 'S'),
    CardSprite(640, 550, 'A', 'C') 
    ])


running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        player_cards.update(event)

        #gameDisplay.fill(0)
        gameDisplay.fill(background_color)
        player_cards.draw(gameDisplay)
        other_cards.draw(gameDisplay)
        button_send(player_cards, event)
        button_claim(player_cards, event)
        button_raise(player_cards, event)        
    
    pygame.display.flip()
    
    