from settings import *

class AllSprites(pg.sprite.Group):
    def __init__(self, game, width, height, bg_tile=None):
        super().__init__()
        # build our own custom group that works like sprite.Group()
        self.game = game
        self.display = game.display
        self.offset = vector()    
        self.width, self.height = width * TILE_SIZE, height * TILE_SIZE
        self.borders = {
            'left': 0,
            'right': -self.width + SCREEN_WIDTH,
            'bottom': -self.height + SCREEN_HEIGHT
        }

    def camera_constraint(self):
        self.offset.x = self.offset.x if self.offset.x < self.borders['left'] else self.borders['left']
        self.offset.x = self.offset.x if self.offset.x > self.borders['right'] else self.borders['right']
        self.offset.y = self.offset.y if self.offset.y > self.borders['bottom'] else self.borders['bottom']
    
    def draw(self, target_pos):
        # camera should be based around player's target position
        self.offset.x = -(target_pos[0] - self.display.get_width() / 2)
        self.offset.y = -(target_pos[1] - self.display.get_height() / 2)
        self.camera_constraint()

        # draw sprite based on its layer
        for sprite in sorted(self, key = lambda sprite: sprite.z):     # loops over all sprites contained within this group
            offset_pos = sprite.rect.topleft + self.offset
            self.display.blit(sprite.image, offset_pos)
