from settings import *
from random import choice
from timer import Timer
from sprites import Score

class Goomba(pg.sprite.Sprite):
    def __init__(self, game, level, pos, frames, groups, collision_sprites, player, data):
        super().__init__(groups)
        self.game = game
        self.display = game.display
        self.level = level
        self.frames, self.frame_index = frames, 0
        self.state = 'walk'
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft = (float(pos[0]), float(pos[1])))
        self.old_rect = self.rect.copy()
        self.z = Z_LAYERS['main']
        self.score_200_surf = game.level_frames['200']
        self.all_sprites = level.all_sprites
        self.data = data

        self.direction = choice((-1, 1))
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 30
        self.player = player
        self.is_dying = False

        self.timers = {
            'dying block': Timer(1500),
            'sound block': Timer(200)
        }

        # audio
        self.volume = 0.4
        self.stomp_sound = self.game.audio_files['stomp']
        self.stomp_sound.set_volume(self.volume) 

    def update(self, delta_time):
        self.old_rect = self.rect.copy()
        self.timers['dying block'].update()
        self.timers['sound block'].update()    
        # animate
        self.frame_index += 2 * delta_time
        if self.is_dying:          
            self.image = self.frames['dead'][0]
            if not self.timers['dying block'].active:
                self.kill()
        else: 
            self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
            # move
            self.rect.x += self.direction * self.speed * delta_time        

        self.rect_right = pg.Rect((self.rect.topright + vector(0, self.rect.height / 4)), (1, self.rect.height / 2)) # (length, top), (width, height)
        self.rect_left = pg.Rect((self.rect.topleft + vector(-2, self.rect.height / 4)), (1, self.rect.height / 2))
        self.rect_bottomright = pg.Rect(self.rect.bottomright, (1, 2))   # pos and size (1 px to right, 1 px down)
        self.rect_bottomleft = pg.Rect(self.rect.bottomleft, (-1, 2))    # pos and size (1 px to left, 1 px down)

        # collision (left or right wall)
        if self.rect_right.collidelist(self.collision_rects) > 0 and self.direction > 0:
            self.direction *= -1
            #print("goomba move left")
        if self.rect_left.collidelist(self.collision_rects) > 0 and self.direction < 0:
            self.direction *= -1
            #print("goomba move right")

        # collision (edge of cliff)
        if self.rect_bottomright.collidelist(self.collision_rects) < 0 and self.direction > 0:
            self.direction *= -1
            #print("goomba move left")
        if self.rect_bottomleft.collidelist(self.collision_rects) < 0 and self.direction < 0:
            self.direction *= -1
            #print("goomba move right")
  

class KoopaTroopa(pg.sprite.Sprite):
    def __init__(self, game, pos, frames, groups, collision_sprites, player):
        super().__init__(groups)
        self.game = game
        self.display = game.display
        self.frames, self.frame_index = frames, 0
        self.state = 'walk'
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft = (float(pos[0]), float(pos[1])))
        self.old_rect = self.rect.copy()
        self.z = Z_LAYERS['main']

        self.direction = choice((-1, 1))
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 30
        self.is_dying = False  
        self.player = player
        self.gravity = 1000
        self.offset = self.rect.y + 10

        # audio
        self.volume = 0.4
        audio_files = self.game.audio_files
        self.kick_sound = audio_files['kick']
        self.kick_sound.set_volume(self.volume)

        self.timers = {
            'sound block': Timer(200)
        }   
   
    def update(self, delta_time):
        self.old_rect = self.rect.copy()
        self.timers['sound block'].update() 
        if self.state == 'walk':
            self.frame_index += 2 * delta_time  # animate
            self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
            self.rect.x += self.direction * self.speed * delta_time # move
        elif self.state == 'turn':
            self.frame_index += 2 * delta_time  # animate
            if int(self.frame_index % len(self.frames[self.state])) >= len(self.frames[self.state]) - 1:
                self.state = 'walk'
            else: 
                self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
                self.rect.x += self.direction * self.speed * delta_time # move

        if self.direction < 0:  
            self.image
        else:
            self.image = pg.transform.flip(self.image, True, False)

        self.rect_right = pg.Rect((self.rect.topright + vector(0, self.rect.height / 4)), (1, self.rect.height / 2)) # (length, top), (width, height)
        self.rect_left = pg.Rect((self.rect.topleft + vector(-2, self.rect.height / 4)), (1, self.rect.height / 2))

        self.rect_bottomright = pg.Rect(self.rect.bottomright, (1, 2))   # pos and size (1 px to right, 1 px down)
        self.rect_bottomleft = pg.Rect(self.rect.bottomleft, (-1, 2))    # pos and size (1 px to left, 1 px down)

        # collision (left or right wall)
        if self.rect_right.collidelist(self.collision_rects) > 0 and self.direction > 0:
            if self.state == 'walk': 
                self.state = 'turn' 
            else:
                if not self.timers['sound block'].active: 
                    self.kick_sound.play()
                self.timers['sound block'].activate()                   
            self.direction *= -1           
            #print("koopa move left")
        if self.rect_left.collidelist(self.collision_rects) > 0 and self.direction < 0:
            if self.state == 'walk':
                self.state = 'turn' 
            else: 
                if not self.timers['sound block'].active: 
                    self.kick_sound.play()
                self.timers['sound block'].activate()                
            self.direction *= -1  
            #print("kooopa move right")

        # collision (edge of cliff)
        if self.rect_bottomright.collidelist(self.collision_rects) < 0 and self.direction > 0:
            if self.state == 'walk':
                self.state = 'turn'                    
            self.direction *= -1
            #print("koopa move left from cliff")
        if self.rect_bottomleft.collidelist(self.collision_rects) < 0 and self.direction < 0:
            if self.state == 'walk':
                self.state = 'turn'                    
            self.direction *= -1
            #print("koopa move right from cliff")


class Shell(pg.sprite.Sprite):
    def __init__(self, game, pos, frames, groups, collision_sprites, player):
        super().__init__(groups)
        self.game = game
        self.display = game.display
        self.frames, self.frame_index = frames, 0
        self.state = 'idle shell'
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft = (float(pos[0]), float(pos[1]) ))
        self.old_rect = self.rect.copy()
        self.z = Z_LAYERS['main']

        self.direction = choice((-1, 1))
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 30
        self.is_dying = False  
        self.player = player
        self.gravity = 1000
        self.offset = self.rect.y + 10

        # audio
        self.volume = 0.4
        audio_files = self.game.audio_files
        self.kick_sound = audio_files['kick']
        self.kick_sound.set_volume(self.volume)

        self.timers = {
            'sound block': Timer(200)
        }   

    def update(self, delta_time):
        self.old_rect = self.rect.copy()
        self.timers['sound block'].update()
        if self.state == 'idle shell':
            self.image = self.frames[self.state][0]  
        if self.is_dying:   
            self.state = 'shell'       
            self.frame_index += 6 * delta_time  # animate            
            self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]) - 1)]
            self.rect.x += self.direction * self.speed * 5 * delta_time 

        if self.direction < 0:  
            self.image
        else:
            self.image = pg.transform.flip(self.image, True, False)

        self.rect_right = pg.Rect((self.rect.topright + vector(0, self.rect.height / 4)), (1, self.rect.height / 2)) # (length, top), (width, height)
        self.rect_left = pg.Rect((self.rect.topleft + vector(-2, self.rect.height / 4)), (1, self.rect.height / 2))
        
        self.rect_bottomright = pg.Rect(self.rect.bottomright, (1, 2))   # pos and size (1 px to right, 1 px down)
        self.rect_bottomleft = pg.Rect(self.rect.bottomleft, (-1, 2))    # pos and size (1 px to left, 1 px down)

        # collision (left or right wall)
        if self.rect_right.collidelist(self.collision_rects) > 0 and self.direction > 0:
            if not self.timers['sound block'].active: 
                self.kick_sound.play()
            self.timers['sound block'].activate()                   
            self.direction *= -1           
            #print("koopa move left")
            
        if self.rect_left.collidelist(self.collision_rects) > 0 and self.direction < 0:            
            if not self.timers['sound block'].active: 
                self.kick_sound.play()
            self.timers['sound block'].activate()                
            self.direction *= -1  
            #print("kooopa move right")

        # shell falls off the cliff
        if self.rect_bottomright.collidelist(self.collision_rects) < 0 and self.direction > 0:
            self.rect.y += 5 
        if self.rect_bottomleft.collidelist(self.collision_rects) < 0 and self.direction < 0:
            self.rect.y += 5 
            