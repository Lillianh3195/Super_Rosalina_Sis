from settings import *
from os.path import join
from timer import Timer

class Player(pg.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, frames, audio_files, create_laser_beam, create_electricity):
        super().__init__(groups)

        # image
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = 'small walk', True
        self.type = ''
        self.move_state = ''
        self.image = self.frames[self.state][self.frame_index]
        self.z = Z_LAYERS['main']
        self.small = True

        # rects
        self.rect = self.image.get_rect(topleft=(float(pos[0]), float(pos[1])))
        self.hitbox_rect = self.rect.inflate(-20, 0)    # get rid of whitespace around player;  shrink rect by 10 pixels from the right, and 10 pixels from the left  
        self.old_rect = self.hitbox_rect.copy()

        # movement
        self.direction = vector()
        self.speed = 100 
        self.gravity = 1000
        self.jump = False
        self.jump_height = 350
        self.attacking = False

        # attack powers
        self.attack_direction = 1
        self.has_fired = False
        self.create_laser_beam = create_laser_beam
        self.create_electricity = create_electricity

        # collision
        self.collision_sprites = collision_sprites
        self.on_surface = {'floor': False, 'left': False, 'right': False}

        # timers
        self.timers = {
            'attack block': Timer(800),
            'flicker': Timer(800),
            'invincible': Timer(500),
            'sound block': Timer(100)
        }

        # audio
        self.volume = 0.4
        self.small_jump_sound = audio_files['small jump']
        self.small_jump_sound.set_volume(self.volume)
        self.super_jump_sound = audio_files['super jump']
        self.super_jump_sound.set_volume(self.volume)
      

    def input(self):
        keys = pg.key.get_pressed()
        input_vector = vector(0, 0)     # direction
        
        if keys[pg.K_RIGHT]:
            input_vector.x += 1
            self.facing_right = True
        if keys[pg.K_LEFT]:
            input_vector.x -= 1
            self.facing_right = False
        if keys[pg.K_x]:
            if self.type == 'electric' or self.type == 'glitch':
                self.attack()
        
        # normalize direction vector so that length the length of the vector is always 1 (ensures that direction does not affect our speed, and only gives us the direction)
        # Only normalize if there's an input vector at all
        # Normalize only the x direction, since we want direction to affect the y direction
        self.direction.x = input_vector.normalize().x if input_vector else input_vector.x     

        if keys[pg.K_UP] or keys[pg.K_SPACE]:
            self.jump = True 

    def attack(self):
        if not self.timers['attack block'].active:
            self.attacking = True
            self.frame_index = 0
            self.timers['attack block'].activate()

    def move(self, delta_time):
        # horizontal
        self.hitbox_rect.x += self.direction.x * self.speed * delta_time
        self.collision('horizontal')

        # vertical
        self.direction.y += self.gravity / 2 * delta_time       # average of downward velocity
        self.hitbox_rect.y += self.direction.y * delta_time
        self.direction.y += self.gravity / 2 * delta_time       

        if self.jump:
            # player can only jump if they're on the floor
            if self.on_surface['floor']:
                self.direction.y = -self.jump_height
                if self.small:
                    if not self.timers['sound block'].active: 
                        self.small_jump_sound.play()
                    self.timers['sound block'].activate()
                else:
                    if not self.timers['sound block'].active: 
                        self.super_jump_sound.play()
                    self.timers['sound block'].activate()
            self.jump = False
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def check_contact(self):
        floor_rect = pg.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))    # (length, top), (width, height)
        right_rect = pg.Rect((self.hitbox_rect.topright + vector(0, self.hitbox_rect.height / 4)), (2, self.hitbox_rect.height / 2))
        left_rect = pg.Rect((self.hitbox_rect.topleft + vector(-2, self.hitbox_rect.height / 4)), (2, self.hitbox_rect.height / 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        #collisions
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['left'] = True if left_rect.collidelist(collide_rects) >= 0 else False

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == 'horizontal':
                    # left, player's left collides with sprite's right
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right):
                        self.hitbox_rect.left = sprite.rect.right

                    # right, player's right collides with sprite's left
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox_rect.right = sprite.rect.left
                else:   # vertical
                    # top, player's top collides with sprite's bottom
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom

                    # bottom, player's bottom collides with sprite's top
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                    # if we have a vertical collision, set y direction to 0 (else our gravity keeps increasing)
                    self.direction.y = 0
    
          
    def update_timers(self):
        for timer in self.timers.values():
             timer.update()

    def animate(self, delta_time):
        self.frame_index += 10 * delta_time
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pg.transform.flip(self.image, True, False)   # flip image depending on direction it's facing

        if self.attacking and self.frame_index > len(self.frames[self.state]):        
            self.attacking = False
            self.has_fired = False
        
        if self.attacking and int(self.frame_index) == 0:
            self.attack_direction = 1 if self.facing_right else -1
            # fire laser beam
            if self.type == 'glitch' and self.has_fired == False:
                self.create_laser_beam(self.rect.center, self.attack_direction)
                self.has_fired = True 
            # fire electricity
            if self.type == 'electric' and self.has_fired == False:
                self.create_electricity(self.rect.center, self.attack_direction)
                self.has_fired = True

    def get_type(self):  
        if self.small:
            self.type = 'small'
        elif self.type == 'glitch':
            pass
        elif self.type == 'electric':
            pass       
        else: 
            self.type = 'big' 

    def get_move_state(self):
        if self.on_surface['floor']:
            if self.attacking:
                self.move_state = 'attack'
            else: 
                self.move_state = 'idle' if self.direction.x == 0 else 'walk'
        else:
            if self.attacking:
                self.move_state = 'attack'
            else: 
                self.move_state = 'jump' if self.direction.y < 0 else 'fall'  

    def get_state(self):
        self.get_type()
        self.get_move_state()
        self.state = self.type + ' ' + self.move_state

    def get_damage(self):
        #print("Player was damaged")  
        print(self.type) 
        if not self.timers['invincible'].active:
            if self.type == 'electric' or self.type == 'glitch':
                self.type = 'big'  
            else:
                self.small = True
        self.timers['invincible'].activate()     
        self.timers['flicker'].activate()
        self.flicker()

    def flicker(self):        
        if self.timers['flicker'].active:
            self.state = 'transition'
            white_mask = pg.mask.from_surface(self.image)
            white_surf = white_mask.to_surface()
            white_surf.set_colorkey('black')
            self.image = white_surf

    def update(self, delta_time):
        self.old_rect = self.hitbox_rect.copy()    # get previous position
        self.update_timers()
        self.input()
        self.move(delta_time)       # get current position
        self.check_contact()
        self.get_state()
        self.flicker()
        self.animate(delta_time)
        