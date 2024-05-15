from settings import *
from timer import Timer

class LaserBeam(pg.sprite.Sprite):
    def __init__(self, pos, groups, frames, direction, speed):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos+vector(30 * direction, 0))
        self.direction = direction
        self.speed = speed
        self.z = Z_LAYERS['main']

        self.timers = {
            'laser beam block': Timer(500)
        }
        
    def update(self, delta_time):
        # animate 
        self.frame_index += 4 * delta_time
        self.image = self.frames[int(self.frame_index % len(self.frames))]
        self.image = pg.transform.flip(self.image, True, False)

        # move
        self.rect.x += self.direction * self.speed * delta_time


class Electricity(pg.sprite.Sprite):
    def __init__(self, pos, groups, frames, direction, speed, collision_sprites):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos+vector(30 * direction, 0))
        self.rect = self.rect.inflate(-25, -25)
        self.direction = direction
        self.speed = speed
        self.z = Z_LAYERS['main']
        self.collision_rects = [sprite.rect for sprite in collision_sprites]

        self.gravity = 1
        self.jump_height = 6
        self.velocity = self.jump_height
    
    def update(self, delta_time):
        # animate 
        self.frame_index += 4 * delta_time
        self.image = self.frames[int(self.frame_index % len(self.frames))]

        self.rect_bottom = pg.Rect(self.rect.bottomleft, (self.rect.width, 2))
        # move
        self.rect.y -= self.velocity
        self.velocity -= self.gravity
        if self.velocity < -self.jump_height:  
            self.velocity = self.jump_height
        self.rect.x += self.direction * self.speed * delta_time



