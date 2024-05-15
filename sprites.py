from settings import *
from timer import Timer

class Sprite(pg.sprite.Sprite):
    def __init__(self, pos, surf=pg.Surface((TILE_SIZE, TILE_SIZE)), groups=None, z=Z_LAYERS['main']):
        super().__init__(groups)        # assigns sprite to group when you create it
        self.image = surf
        self.rect = self.image.get_rect(topleft=(float(pos[0]), float(pos[1])))
        self.old_rect = self.rect.copy()
        self.z = z

class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups, z=Z_LAYERS['main'], animation_speed=ANIMATION_SPEED):
        self.frames, self.frame_index = frames, 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animation_speed = animation_speed

    def animate(self, delta_time):
        self.frame_index += self.animation_speed * delta_time
        self.image = self.frames[int(self.frame_index % len(self.frames))]      # index should not exceed len(self.frames)

    def update(self, delta_time):
        self.animate(delta_time)

class Item(Sprite):
    def __init__(self, item_type, collision_sprites, pos, surf, groups):
        super().__init__(pos=pos, surf=surf, groups=groups)
        self.image = surf
        self.item_type = item_type
        self.direction = vector(1, 1)
        self.speed = 30
        self.gravity = 1000
        self.z = Z_LAYERS['main']
        self.offset = self.rect.y - 16  # must move mushroom/flower up before moving right
        self.rect = self.image.get_rect(topleft=(float(pos[0]), float(pos[1])))
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.moved_up = False

    def update(self, delta_time):
        # move
        if self.rect.y > self.offset and self.moved_up == False: 
            self.rect.y -= self.direction.y * self.speed * delta_time            
        else:
            self.moved_up = True         
            if self.item_type == 'electric flower':
                pass
            else: 
                self.rect.x += self.direction.x * self.speed * delta_time

            self.rect_right = pg.Rect((self.rect.topright + vector(0, self.rect.height / 4)), (1, self.rect.height / 2)) # (length, top), (width, height)
            self.rect_left = pg.Rect((self.rect.topleft + vector(-2, self.rect.height / 4)), (1, self.rect.height / 2))
            self.rect_bottom = pg.Rect(pg.Rect(self.rect.bottomleft, (self.rect.width, 2)) )
            
            # collision (left or right wall)
            if self.rect_right.collidelist(self.collision_rects) > 0 and self.direction.x > 0:
                self.direction.x *= -1
                #print("item move left")            
            if self.rect_left.collidelist(self.collision_rects) > 0 and self.direction.x < 0:
                self.direction.x *= -1
                #print("item move right")            
            
            # item falls off edge
            if self.rect_bottom.collidelist(self.collision_rects) < 0:
                self.rect.y += 2
                #print("item move down")

class Block(Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(pos=pos, surf=surf, groups=groups)
        self.image = surf
        self.z = Z_LAYERS['fg']
        self.rect = self.image.get_rect(topleft=(float(pos[0]), float(pos[1])))

class Flag(Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(pos=pos, surf=surf, groups=groups)
        self.image = surf
        self.is_created = False
        self.z = Z_LAYERS['bg details']
        self.rect = self.image.get_rect(topleft=(float(pos[0]), float(pos[1])))

class Coin(Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(pos=pos, surf=surf, groups=groups)
        self.image = surf
        self.is_created = False
        self.z = Z_LAYERS['bg details']
        self.rect = self.image.get_rect(topleft=(float(pos[0]), float(pos[1])))

class Score(Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(pos=pos, surf=surf, groups=groups)
        self.image = surf
        self.z = Z_LAYERS['fg']
        self.rect = self.image.get_rect(topleft=(float(pos[0]), float(pos[1]) - 32))
        self.direction = 1
        self.speed = 30
        self.timer = Timer(1500)
        self.timer.activate()

    def update(self, delta_time):
        self.timer.update()
        self.rect.y -= self.direction * self.speed * delta_time
        if not self.timer.active:
            self.kill()

