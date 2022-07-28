
import pygame as pygame
import logging

logger = logging.getLogger("Controller")
handler  = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s|%(name)s|%(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class SpriteController():

    @classmethod
    async def create(cls, player, engine):
        self = SpriteController()
        self.player = player
        self.engine = engine       

        await self.set_engine_cards()
        await self.set_player_cards()
        await self.set_trump_score_mover()

        return self


    async def restart_engine(self):
        self.engine.points = 0
        self.engine.hidden_cards = 0
    
    async def set_trump_score_mover(self):

        self.trump = await self.player.retrieve_trump()
        image = pygame.image.load('app/img/suit' + str(self.trump) + '.png').convert()
        ts = pygame.sprite.Sprite()
        ts.image = image
        ts.rect = image.get_rect(center = (142, 180))
        font = pygame.font.SysFont("Consolas", 20)
        black = (0, 0, 0)

        (self.score_engine, self.score_player)  = await self.player.retrieve_score()
        score_sprite1 = pygame.sprite.Sprite()
        sign1 = '+' if self.score_engine >= 0 else ''
        score_sprite1.image = font.render(f"Engine Score: {sign1}{self.score_engine}", True, black)
        score_sprite1.rect = score_sprite1.image.get_rect(center = (142, 70))

        sign2 = '+' if self.score_player >= 0 else ''
        score_sprite2 = pygame.sprite.Sprite()
        score_sprite2.image = font.render(f"Player Score: {sign2}{self.score_player}", True, black)
        score_sprite2.rect = score_sprite2.image.get_rect(center = (142, 105))

        self.trump_and_score = pygame.sprite.Group([ts, score_sprite1, score_sprite2])        

        self.is_player_mover = await self.player.is_mover()        
        self.is_challenge_active = False
        self.is_player_raise_point_caller = None
        self.is_raise_point_challenge_active = False


        mover = 'player' if self.is_player_mover else 'engine'
        logger.info(f'Mover: {mover}. Trump {"♣♦♥♠"[self.trump]}. ScoreP: {self.score_player}. ScoreE: {self.score_engine}')

    async def set_engine_cards(self):
        (c1, c2, c3) = await self.engine.retrieve_hand()
        logger.info(f"Engine hand: {c1.get_card_str()}, {c2.get_card_str()}, {c3.get_card_str()}")
        self.engine_cards = pygame.sprite.Group([
            CardSprite(400, 150, c1, 1, True ), 
            CardSprite(520, 150, c2, 2, True ),
            CardSprite(640, 150, c3, 3, True ) 
            ])
        

    async def set_player_cards(self):
        (c1, c2, c3) = await self.player.retrieve_hand()        
        logger.info(f"Player hand: {c1.get_card_str()}, {c2.get_card_str()}, {c3.get_card_str()}")
        self.player_cards = pygame.sprite.Group([
            CardSprite(400, 550, c1, 1, False ), 
            CardSprite(520, 550, c2, 2, False ),
            CardSprite(640, 550, c3, 3, False ) 
            ])  



    async def update(self, event):


        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     played_sprites = [s for s in self.player_cards.sprites() if s.played ]
        #     if len(played_sprites) > 0:
        #         await self.set_engine_cards()
        #         await self.set_player_cards()        
        #         if not self.is_player_mover and not self.is_challenge_active:
        #             await self.engine_challenge()
        #     elif not self.is_player_mover and not self.is_challenge_active:
        #         await self.engine_challenge()
        
        player_selected = [s for s in self.player_cards.sprites() if s.selected ]

        if self.is_player_mover and self.is_challenge_active:
            engine_played = [s for s in self.engine_cards.sprites() if s.played ]
            allow_select = len(player_selected) < len(engine_played)
            self.player_cards.update(event, [], allow_select)
        else:
            self.player_cards.update(event, player_selected)

        self.engine_cards.update(event, [])
        self.trump_and_score.update()


       
    async def draw(self, display):
        self.player_cards.draw(display)
        self.engine_cards.draw(display)
        self.trump_and_score.draw(display)       




    async def player_challenge(self):
        if not self.assert_game_state('player_challenge', 
                is_player_mover = self.is_player_mover, 
                is_challenge_active = not self.is_challenge_active,
                is_raise_point_challenge_active = not self.is_raise_point_challenge_active ):
            return                        
    
        player_idxs = [ s.index for s in self.player_cards.sprites() if s.selected ]
        player_crds = [ s.card  for s in self.player_cards.sprites() if s.selected ]
        if player_idxs:
            if await self.player.challenge(player_idxs):
                self.is_challenge_active = True
                self.is_player_mover = False

                success, engine_cards = await self.engine.response(player_crds)
                if success:
                    self.is_challenge_active = False

                    if engine_cards:
                        self.is_player_mover = False

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
                        self.is_player_mover = True

                        for idx in player_idxs:
                            for (i,s) in enumerate(self.player_cards.sprites()):
                                if s.index == idx:
                                    s.play(0, -160)
                                    es = self.engine_cards.sprites()[i]
                                    es.play(0, 180)
                else:
                    logger.info(f'player_challenge(): Failed to recieve engine response')
            else:
                #something went wrong .reset selection
                logger.info(f'player_challenge(): Failed to send player challenge')
                for idx in player_idxs:
                    for s in self.player_cards.sprites():
                        if s.index == idx:                  
                            s.select() #this will unselect card
        

    
    async def player_response(self):

        if not self.assert_game_state('player_response', 
                is_player_mover = self.is_player_mover, 
                is_challenge_active = self.is_challenge_active,
                is_raise_point_challenge_active = not self.is_raise_point_challenge_active ):
            return

        player_idxs = [ s.index for s in self.player_cards.sprites() if s.selected ]
        if player_idxs:
            success, player_cards = await self.player.response(player_idxs)
            if success:
                self.is_challenge_active = False

                if player_cards:
                    self.is_player_mover = True

                    for idx in player_idxs:
                        for s in self.player_cards.sprites():
                            if s.index == idx:
                                s.play(0, -160)
        
                else:
                    self.is_player_mover = False
                    engine_crds = [ s.card for s in self.engine_cards.sprites() if s.selected ]
                    self.engine.update_points(engine_crds)

                    for idx in player_idxs:
                        for s in self.player_cards.sprites():
                            if s.index == idx:
                                s.hide()
                                s.play(0, -160)
            else:
                logger.info(f'player_response(): Failed to send player response')
            


    async def engine_challenge(self):
        if not self.assert_game_state('engine_challenge', 
                is_player_mover = not self.is_player_mover, 
                is_challenge_active = not self.is_challenge_active,
                is_raise_point_challenge_active = not self.is_raise_point_challenge_active ):
            return
        
        status = await self.engine.claim_win()
        if status:            
            await self.set_engine_cards()
            await self.set_player_cards()
            await self.set_trump_score_mover()            
            return

        engine_idxs = await self.engine.challenge()            
        if engine_idxs:
            self.is_challenge_active = True
            self.is_player_mover = True
            
            for idx in engine_idxs:
                for s in self.engine_cards.sprites():
                    if s.index == idx:                
                        s.show() #show engine's card
                        s.play(0, 180)
        else:  
            logger.info(f'engine_challenge(): Challenge not sent')              
        

    
    async def send_action(self):
        if self.is_player_mover:
            if self.is_challenge_active:                
                await self.player_response()
            else:
                await self.player_challenge()                
        else:
            logger.info(f"send_action(): Action ignored. It's not player's move.")


                
    async def claim_action(self):    
        if self.is_player_mover:            
            status = await self.player.claim_win()
            if status:
                await self.set_engine_cards()
                await self.set_player_cards()
                await self.set_trump_score_mover()
                await self.restart_engine()
        else:
            logger.info(f"claim_action(): Can't claim. It's not player's move.")


    async def raise_point_action(self):
        if not self.assert_game_state('raise_point_action', 
                is_player_mover = self.is_player_mover,                 
                is_player_raise_point_caller = not self.is_player_raise_point_caller,
                is_raise_point_challenge_active = not self.is_raise_point_challenge_active                
                ):
            return

        if await self.player.raise_point_challenge():
            self.is_point_challenge_active = True
            self.is_player_raise_point_caller = True
            (success, game_state) = await self.engine.raise_point_response()

            if success:
                self.is_point_challenge_active = False                
            else:
                logger.info(f"raise_point_action(): engine.raise_point_response() failed")
        else:
            logger.info(f"raise_point_action(): Ignored because raised point failed")


    def is_continue_state(self):
        player_played_cards = [s for s in self.player_cards.sprites() if s.played ]
        engine_played_cards = [s for s in self.engine_cards.sprites() if s.played ]
        return player_played_cards and engine_played_cards



    async def continue_action(self):
        if self.is_continue_state():
            await self.set_engine_cards()
            await self.set_player_cards()

        if self.assert_game_state('continue_action', 
                is_player_mover = not self.is_player_mover,
                is_challenge_active = not self.is_challenge_active ):
            await self.engine_challenge()


    def assert_game_state( self, caller, 
                is_player_mover = None, 
                is_challenge_active = None, 
                is_raise_point_challenge_active = None, 
                is_player_raise_point_caller = None            
                ) -> bool:

        if is_player_mover != None and not is_player_mover:
                logger.info(f'{caller}(): Ignored because is_player_mover = {is_player_mover}')
                return False
        
        if is_challenge_active != None and not is_challenge_active:
                logger.info(f'{caller}(): Ignored because is_challenge_active = {is_challenge_active}')
                return False
        
        if is_raise_point_challenge_active != None and not is_raise_point_challenge_active:
                logger.info(f'{caller}(): Ignored because is_raise_point_challenge_active = {is_raise_point_challenge_active}')
                return False
        
        if is_player_raise_point_caller != None and not is_player_raise_point_caller:
                logger.info(f'{caller}(): Ignored because is_player_raise_point_caller = {is_player_raise_point_caller}')
                return False

        return True




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

