import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
import asyncio

from starkware.starknet.testing.starknet import Starknet, StarknetContract
from starkware.starkware_utils.error_handling import StarkException
from utils import TestSigner as Signer

from engine.simple_bura_engine import SimpleBuraEngine
from engine.simple_bura_engine import Card

from TextProgress import TextProgress

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

pygame.init()
font = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()
gameDisplay = pygame.display.set_mode((display_width, display_height))

async def button_send(player_cards, other_cards, event, signer, account, contract, engine):

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
        idxs = {}
        for (i,cs) in enumerate(player_cards.sprites()):
            if cs.clicked:        
                cs.play(0, -160)
                idxs[i+1] = cs.card
        
        if len(idxs) > 0:
            print(idxs)
            success = await send_challenge(signer, account, contract, idxs)
            if success:                
                resp = await engine.respond(list(idxs.values()))
                if len(resp):
                    for (i, idx) in enumerate(idxs.keys()):
                        ocs = other_cards.sprites()[idx-1]
                        ocs.open(resp[i])
                        ocs.play(0, 180)
                        #TODO: Move card to engine's pile
            else:
                pass
                #TODO: implement case when human wins the challenge
            


        

async def send_challenge(signer, account, contract, idxs:dict) -> bool:
    try:
        if len(idxs) == 1:
            await signer.send_transaction(
                account=account,
                to=contract.contract_address,
                selector_name="send_challenge1",
                calldata=list(idxs.keys()),
            )            
            return True
        elif len(idxs) == 2:
            await signer.send_transaction(
                account=account,
                to=contract.contract_address,
                selector_name="send_challenge2",
                calldata=list(idxs.keys()),
            )            
        else:
            await signer.send_transaction(
                account=account,
                to=contract.contract_address,
                selector_name="send_challenge3",
                calldata=list(idxs.keys()),
            )
    except StarkException:
        print("Transaction failed. Please try again...")
        return False
        


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
    def __init__(self, x, y, c = None):
        super().__init__()

        if c:
            self.image = pygame.image.load('app/img/' + c.get_rank_str() + c.get_suit_str() + '.png').convert()
            self.active = True
        else:
            self.image = pygame.image.load('app/img/back.png').convert()
            self.active = False

        self.rect = self.image.get_rect(center = (x, y))
        self.clicked = False
        
        self.card = c

    def open(self, c):
        self.card = c
        self.image = pygame.image.load('app/img/' + c.get_rank_str() + c.get_suit_str() + '.png').convert()        


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
        


async def get_cards(signer, account, contract):
    # assert that drawn cards are C8,HQ and CK HK
    cards = (
        await signer.send_transaction(
            account=account,
            to=contract.contract_address,
            selector_name="get_cards",
            calldata=[],
        )
    ).result[0]

    (c1, c2, c3) = cards

    return (Card(c1), Card(c2), Card(c3))


async def game_wrapper():

    pygame.display.set_caption('Bura')
    gameDisplay.fill(background_color)
    pygame.display.flip()

    renderer = TextProgress(font, 'Initializing Local Starknet Session...', black, (100, 40, 40))
    text = renderer.render(0)
    gameDisplay.blit(text, (0, 0))
    pygame.display.flip()

    starknet = await Starknet.empty()
    bura_contract = await starknet.deploy("contracts/contract.cairo")

    renderer1 = TextProgress(font, 'Initializing Bura Game Engine...', black, (100, 40, 40))
    text1 = renderer1.render(0)
    gameDisplay.blit(text1, (0, 25))
    pygame.display.flip()
    engine = await SimpleBuraEngine().create(starknet, bura_contract)    

    renderer2 = TextProgress(font, 'Setting Up Player Account Contract...', black, (100, 40, 40))
    text2 = renderer2.render(0)
    gameDisplay.blit(text2, (0, 50))
    pygame.display.flip()

    human_signer = Signer(private_key=123456789)
    account = await starknet.deploy("contracts/Account.cairo", constructor_calldata=[human_signer.public_key])
    await human_signer.send_transaction( account=account, to=bura_contract.contract_address, selector_name="join_game", calldata=[5])


    trump = (await bura_contract.get_trump().invoke()).result[0]

    mover = (await bura_contract.get_mover().invoke()).result[0]
    other = (await bura_contract.get_other().invoke()).result[0]    
    
    other_cards = pygame.sprite.Group([
        CardSprite(400, 150 ), 
        CardSprite(520, 150 ),
        CardSprite(640, 150 ) 
        ])


    (c1,c2,c3) = await get_cards(human_signer, account, bura_contract)
    player_cards = pygame.sprite.Group([
        CardSprite(400, 550, c1), 
        CardSprite(520, 550, c2),
        CardSprite(640, 550, c3) 
        ])


    running = True
    while running:

        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            player_cards.update(event)

            #gameDisplay.fill(0)
            gameDisplay.fill(background_color)
            player_cards.draw(gameDisplay)
            other_cards.draw(gameDisplay)
            await button_send(player_cards, other_cards, event, human_signer, account, bura_contract, engine)
            button_claim(player_cards, event)
            button_raise(player_cards, event)        
        
        pygame.display.flip()



loop = asyncio.get_event_loop()
loop.run_until_complete(game_wrapper())
loop.close()

    