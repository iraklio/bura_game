from time import sleep
import pygame as pygame
from engine.simple_bura_engine import less, sort

class CardSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, card, index, closed):
        super().__init__()

        if closed:
            self.image = pygame.image.load('app/img/back.png').convert()
        else:
            self.image = pygame.image.load('app/img/' + card.get_rank_str() + card.get_suit_str() + '.png').convert()
            
        self.x = x
        self.y = y
        self.card = card
        self.index = index
        self.closed = closed        
        
        self.rect = self.image.get_rect(center = (x, y))
        self.selected = False
        self.played = False        
        

    def show(self):        
        image_path = 'app/img/' + self.card.get_rank_str() + self.card.get_suit_str() + '.png'
        self.image = pygame.image.load(image_path).convert()
        self.closed = False
    
    def hide(self):        
        self.image = pygame.image.load('app/img/back.png').convert()
        self.closed = True    
    

    def update(self, event, selected_sprites, allow_select = True):
        # if event.type == pygame.MOUSEBUTTONDOWN and self.played:
        #     self.kill()
        if not self.closed and not self.played and event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if len(selected_sprites) > 0: 
                    if selected_sprites[0].card.suit == self.card.suit:
                        self.select()
                elif allow_select or self.selected:
                    self.select()        

    def select(self):        
        if self.selected == False:
            self.rect = self.rect.move(0,-25)
        else:
            self.rect = self.rect.move(0, 25)

        self.selected = not self.selected


    def play(self, x, y):        
        self.rect = self.rect.move(x,y)
        self.selected = False
        self.played = True



class SpriteController():

    @classmethod
    async def create(cls, player, engine):

        self = SpriteController()
        self.player = player
        self.engine = engine

        await self.set_engine_cards()
        await self.set_player_cards()
        self.is_engine_challenger = await self.player.is_engine_challenger()
        self.trump = await self.player.retrieve_trump()        
        return self
    

    async def set_engine_cards(self):
        (c1, c2, c3) = await self.engine.retrieve_hand()
        print("Engine: ",c1.get_card_str(), c2.get_card_str(), c3.get_card_str())
        self.engine_cards = pygame.sprite.Group([
            CardSprite(400, 150, c1, 1, True ), 
            CardSprite(520, 150, c2, 2, True ),
            CardSprite(640, 150, c3, 3, True ) 
            ])
        

    async def set_player_cards(self):
        (c1, c2, c3) = await self.player.retrieve_hand()
        print("Player: ",c1.get_card_str(), c2.get_card_str(), c3.get_card_str())
        self.player_cards = pygame.sprite.Group([
            CardSprite(400, 550, c1, 1, False ), 
            CardSprite(520, 550, c2, 2, False ),
            CardSprite(640, 550, c3, 3, False ) 
            ])     

    async def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            played_sprites = [s for s in self.player_cards.sprites() if s.played ]
            if len(played_sprites) > 0:
                await self.set_engine_cards()
                await self.set_player_cards()
        
                if self.is_engine_challenger:
                    await self.engine_challenge()
                

        
        player_selected = [s for s in self.player_cards.sprites() if s.selected ]

        if self.is_engine_challenger:
            engine_played = [s for s in self.engine_cards.sprites() if s.played ]
            allow_select = len(player_selected) < len(engine_played)
            self.player_cards.update(event, [], allow_select)
        else:
            self.player_cards.update(event, player_selected)

        self.engine_cards.update(event, [])
       
    async def draw(self, display):
        self.player_cards.draw(display)
        self.engine_cards.draw(display)


    

    async def player_challenge(self):

        player_idxs = [s.index for s in self.player_cards.sprites() if s.selected ]
        if player_idxs:
            if await self.player.challenge(player_idxs):
                engine_cards = await self.engine.response()
                if engine_cards:
                    self.is_engine_challenger = True                    
                    for idx in player_idxs:
                        for s in self.player_cards.sprites():
                            if s.index == idx:
                                s.play(0, -160)
                    
                    for c in engine_cards:
                        for s in self.engine_cards.sprites():
                            if s.card.id == c.id:
                                s.show() #show engine's card
                                s.play(0, 180)
                    
                else:                    
                    self.is_engine_challenger = False
                    for idx in player_idxs:
                        for (i,s) in enumerate(self.player_cards.sprites()):
                            if s.index == idx:
                                s.play(0, -160)
                                es = self.engine_cards.sprites()[i]
                                es.play(0, 180)

                    
            else:
                #something went wrong .reset selection
                for idx in player_idxs:
                    for s in self.player_cards.sprites():
                        if s.index == idx:                  
                            s.select() #this will unselect card

    
    async def player_response(self):        
        player_idxs = [ s.index for s in self.player_cards.sprites() if s.selected ]
        if player_idxs:
            player_cards = await self.player.response(player_idxs)            
            if player_cards:
                self.is_engine_challenger = False
                for idx in player_idxs:
                    for s in self.player_cards.sprites():
                        if s.index == idx:
                            s.play(0, -160)
     
            else:
                self.is_engine_challenger = True
                for idx in player_idxs:
                    for s in self.player_cards.sprites():
                        if s.index == idx:
                            s.hide()
                            s.play(0, -160)
                


    async def engine_challenge(self):                        
        engine_idxs = await self.engine.challenge()        
        if engine_idxs:             
            for idx in engine_idxs:
                for s in self.engine_cards.sprites():
                    if s.index == idx:                
                        s.show() #show engine's card
                        s.play(0, 180)
        else:                
            print("Engine failed to calculate challenge")
                

    async def send_action(self):
        
        if self.is_engine_challenger:
            #player is responding to the challenge
            await self.player_response()
        else:
            #player is challenging            
            await self.player_challenge()

            

    
