import pygame as pygame

class CardSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, c = None):
        super().__init__()

        if c:
            self.image = pygame.image.load('app/img/' + c.get_rank_str() + c.get_suit_str() + '.png').convert()
            self.closed = False
        else:
            self.image = pygame.image.load('app/img/back.png').convert()
            self.closed = True

        self.rect = self.image.get_rect(center = (x, y))
        self.selected = False
        self.played = False
        
        self.card = c

    def show(self, c):
        self.card = c
        self.image = pygame.image.load('app/img/' + c.get_rank_str() + c.get_suit_str() + '.png').convert()
        self.closed = False        


    def update(self, event, selected_sprites):        
        if not self.closed and not self.played and event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if len(selected_sprites) > 0: 
                    if selected_sprites[0].card.suit == self.card.suit:
                        self.select()
                else:
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
    def __init__(self, player, engine, display):
        self.player = player
        self.engine = engine
        self.player_cards = None
        self.engine_cards = None
    

    async def set_engine_cards(self):
        self.engine_cards = pygame.sprite.Group([
            CardSprite(400, 150 ), 
            CardSprite(520, 150 ),
            CardSprite(640, 150 ) 
            ])

    async def set_player_cards(self):
        (c1, c2, c3) = await self.player.retrieve_hand()
        self.player_cards = pygame.sprite.Group([
            CardSprite(400, 550, c1), 
            CardSprite(520, 550, c2),
            CardSprite(640, 550, c3) 
            ])

    async def update(self, event):
        selected_sprites = [s for s in self.player_cards.sprites() if s.selected ]
        self.player_cards.update(event, selected_sprites)        
        self.engine_cards.update(event, [])

    async def draw(self, display):
        self.player_cards.draw(display)
        self.engine_cards.draw(display)


    async def make_move(self):
        idxs = {}
        for (i,cs) in enumerate(self.player_cards.sprites()):
            if cs.selected:        
                cs.play(0, -160)
                idxs[i+1] = cs.card
        
        if len(idxs) > 0:
            print(idxs)
            success = await self.player.challenge(list(idxs.keys()))
            if success:                
                resp = await self.engine.respond()
                if len(resp):
                    for (i, idx) in enumerate(idxs.keys()):
                        ocs = self.engine_cards.sprites()[idx-1]
                        ocs.show(resp[i])
                        ocs.play(0, 180)
                        #TODO: Move card to engine's pile
            else:
                pass
                #TODO: implement case when human wins the challenge      

    
