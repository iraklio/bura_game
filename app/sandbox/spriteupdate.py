import pygame

class SpriteObject(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super().__init__() 
        #self.original_image = pygame.Surface((100, 100), pygame.SRCALPHA)

        self.image = pygame.image.load('app/img/' + name + '.png').convert()        
        # pygame.draw.circle(self.original_image, color, (55, 55), 55)
        # self.click_image = pygame.Surface((100, 100), pygame.SRCALPHA)
        # pygame.draw.circle(self.click_image, color, (55, 55), 55)
        # pygame.draw.circle(self.click_image, (255, 255, 255), (55, 55), 55, 4)
        # self.image = self.original_image 
        self.rect = self.image.get_rect(center = (x, y))
        self.clicked = False

    def update(self, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    if self.clicked == False:
                        self.rect = self.rect.move(0,-25)
                    else:
                        self.rect = self.rect.move(0, 25)

                    self.clicked = not self.clicked
                        

        

pygame.init()
window = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()

#sprite_object = SpriteObject(*window.get_rect().center, (128, 128, 0))
group = pygame.sprite.Group([
    SpriteObject(window.get_width() // 3, window.get_height() // 3, '8H'),
    SpriteObject(window.get_width() * 2 // 3, window.get_height() // 3, 'QS'),
    SpriteObject(window.get_width() // 3, window.get_height() * 2 // 3, 'AC'),
    # SpriteObject(window.get_width() * 2// 3, window.get_height() * 2 // 3, (128, 128, 0)),
])



run = True
while run:
    clock.tick(60)
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            run = False 

    group.update(event_list)

    window.fill(0)
    group.draw(window)
    
    pygame.display.flip()

pygame.quit()
exit()