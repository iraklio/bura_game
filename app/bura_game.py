import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import asyncio

from starkware.starknet.testing.starknet import Starknet, StarknetContract
from starkware.starkware_utils.error_handling import StarkException

from engine.simple_bura_engine import SimpleBuraEngine
from bura_player import BuraPlayer
from TextProgress import TextProgress
from sprite_controller import CardSprite, SpriteController

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
display = pygame.display.set_mode((display_width, display_height))

async def button_send( controller, event):

    (x,y,w,h) = (450, 650, 144, 40)
    inactive_color = (180, 180, 158)
    active_color = (228,234,23)
    pygame.draw.rect(display, active_color, (x, y, w, h))
    textSurface = font.render("Send", True, black)
    TextRect = textSurface.get_rect()
    TextRect.center = ((x + (w / 2)), (y + (h / 2)))
    display.blit(textSurface, TextRect)

    (mx, my) = pygame.mouse.get_pos()
    if x + w > mx > x and y + h > my > y and event.type == pygame.MOUSEBUTTONDOWN:
        await controller.make_move()
      


async def button_claim( controller, event):

    x = 70
    y = 250
    w = 144
    h = 40
    inactive_color = (180,180,158)
    active_color = (228,234,23)

    (mx,my) = pygame.mouse.get_pos()
    clicked = event.type == pygame.MOUSEBUTTONDOWN
    pygame.draw.rect(display, active_color, (x, y, w, h))
    textSurface = font.render("Claim", True, black)
    TextRect = textSurface.get_rect()
    TextRect.center = ((x + (w / 2)), (y + (h / 2)))
    display.blit(textSurface, TextRect)
    if x + w > mx > x and y + h > my > y and clicked:
        pass
        

async def button_raise( controller, event):

    x = 70
    y = 310
    w = 144
    h = 40
    inactive_color = (180,180,158)
    active_color = (228,234,23)
    (mx,my) = pygame.mouse.get_pos()
    clicked = event.type == pygame.MOUSEBUTTONDOWN
    pygame.draw.rect(display, active_color, (x, y, w, h))
    textSurface = font.render("Raise", True, black)
    TextRect = textSurface.get_rect()
    TextRect.center = ((x + (w / 2)), (y + (h / 2)))
    display.blit(textSurface, TextRect)

    if x + w > mx > x and y + h > my > y and clicked:
        pass
        

def show_message(msg, x, y):
    renderer = TextProgress(font, msg, black, (100, 40, 40))
    text = renderer.render(0)
    display.blit(text, (x, y))
    pygame.display.flip()


async def game_wrapper():

    pygame.display.set_caption('Bura')
    display.fill(background_color)
    pygame.display.flip()

    show_message('Initializing Local Starknet Session...', 0, 0)
    starknet = await Starknet.empty()
    bura_contract = await starknet.deploy("contracts/contract.cairo")

    show_message('Initializing Bura Game Engine...', 0, 25)
    engine = await SimpleBuraEngine().create(starknet, bura_contract)    

    show_message('Setting Up Player Account...', 0, 50)
    player = await BuraPlayer().create(starknet, bura_contract)

    controller = SpriteController(player, engine, display)
    await controller.set_engine_cards()
    await controller.set_player_cards()   
    

    running = True
    while running:

        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            #display.fill(0)
            display.fill(background_color)
            #player_cards.update(event)

            await controller.update(event)
            await controller.draw(display)

            
            #player_cards.draw(display)
            #other_cards.draw(display)
            await button_send( controller, event)
            await button_claim(controller, event)
            await button_raise(controller, event)        
        
        pygame.display.flip()



loop = asyncio.get_event_loop()
loop.run_until_complete(game_wrapper())
loop.close()

    