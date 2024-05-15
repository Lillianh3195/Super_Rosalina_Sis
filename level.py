from settings import *
from sprites import Sprite, AnimatedSprite, Item, Block, Score, Flag
from player import Player
from groups import AllSprites
from enemies import Goomba, KoopaTroopa, Shell
from powers import LaserBeam, Electricity
from random import choice
from timer import Timer
from os.path import join


class Level:
    def __init__(self, game, tmx_map, level_frames, audio_files, data): 
        self.game = game
        self.display = game.display
        self.data = data

        # level data
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_bottom = tmx_map.height * TILE_SIZE        

        # groups
        self.all_sprites = AllSprites(game=self.game, width=self.level_width, height=self.level_bottom)
        self.collision_sprites = pg.sprite.Group()
        self.damage_sprites = pg.sprite.Group()
        self.goomba_sprites = pg.sprite.Group()
        self.koopa_troopa_sprites = pg.sprite.Group()
        self.shell_sprites = pg.sprite.Group()
        self.laser_beam_sprites = pg.sprite.Group()
        self.electricity_sprites = pg.sprite.Group()
        self.power_damage_sprites = pg.sprite.Group()
        self.item_box_sprites = pg.sprite.Group()
        self.item_sprites = pg.sprite.Group()
        self.coin_sprites = pg.sprite.Group()
        self.bg_sprites = pg.sprite.Group()
        self.bg_detail_sprites = pg.sprite.Group()

        self.setup(tmx_map, level_frames, audio_files)

        # timers
        self.timers = {
            'item block': Timer(100),
            'sound block': Timer(200),
            'shell block': Timer(50)
        }

        # frames
        self.laser_beam_surf = level_frames['laser beam']
        self.electricity_surf = level_frames['electricity']
        self.mushroom_surf = level_frames['normal mushroom']
        self.glitch_mushroom_surf = level_frames['glitch mushroom']
        self.electric_flower_surf = level_frames['electric flower']
        self.block_surf = level_frames['block']
        self.flag_surf = level_frames['flag']
        self.score_200_surf = level_frames['200']
        self.score_1000_surf = level_frames['1000']
        self.shell_surf = level_frames['koopa troopa']

        # audio
        self.audio_files = audio_files
        self.volume = 0.4
        self.powerup_appears_sound = audio_files['powerup appears']
        self.powerup_appears_sound.set_volume(self.volume)
        self.powerup_sound = audio_files['powerup']
        self.powerup_sound.set_volume(self.volume)
        self.dead_sound = audio_files['dead']
        self.dead_sound.set_volume(self.volume)
        self.kick_sound = audio_files['kick']
        self.kick_sound.set_volume(self.volume)
        self.power_down_sound = audio_files['power down']
        self.power_down_sound.set_volume(self.volume)
        self.electric_ball_sound = audio_files['electric ball']
        self.electric_ball_sound.set_volume(self.volume)
        self.laser_beam_sound = audio_files['laser beam']
        self.laser_beam_sound.set_volume(self.volume - 0.2)
        self.bump_sound = audio_files['bump']
        self.bump_sound.set_volume(self.volume)
        self.stage_clear_sound = audio_files['stage clear']
        self.stage_clear_sound.set_volume(self.volume)
        self.coin_sound = audio_files['coin']
        self.coin_sound.set_volume(self.volume)


        self.sound_played = False
        self.created_flag = False
        self.created_item = False


    def setup(self, tmx_map, level_frames, audio_files): 
        # Tiles
        for x, y, surf in tmx_map.get_layer_by_name('BG').tiles():
            Sprite((x, y), surf, self.all_sprites, Z_LAYERS['bg']) 

        for layer in ['BG', 'Terrain', 'FG']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == 'Terrain':
                    groups.append(self.collision_sprites)                                
                match layer:
                    case 'BG': z = Z_LAYERS['bg']
                    case 'FG': z = Z_LAYERS['fg']
                    case _ : z = Z_LAYERS['main']
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z) 
                # x and y are grid positions --> gotta convert to pixel position
                # terrain are all_sprites AND collision_sprites
        
        # Objects
        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'player':
                self.player = Player(
                    pos=(obj.x, obj.y), 
                    groups=self.all_sprites, 
                    collision_sprites=self.collision_sprites,
                    frames=level_frames['player'],
                    audio_files=audio_files,
                    create_laser_beam=self.create_laser_beam,
                    create_electricity=self.create_electricity)    # player is in all_sprites, but has access to collision sprites
            else:
                if obj.name == 'item box':
                    frames = level_frames[obj.name]
                    AnimatedSprite((obj.x, obj.y), frames, (self.all_sprites, self.item_box_sprites, self.collision_sprites))
        
        # Background details
        for obj in tmx_map.get_layer_by_name('BG details'):
            if obj.name == 'flag':
                self.flag = Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.bg_detail_sprites))

        # Coins
        for obj in tmx_map.get_layer_by_name('Coins'):
            if obj.name == 'coin':
                frames = level_frames[obj.name]
                AnimatedSprite((obj.x, obj.y), frames, (self.all_sprites, self.coin_sprites))

        # Enemies
        for obj in tmx_map.get_layer_by_name('Enemies'):
            if obj.name == 'goomba':
                Goomba(self.game, self, (obj.x, obj.y), level_frames['goomba'], (self.all_sprites, self.damage_sprites, self.goomba_sprites), self.collision_sprites, self.player, self.data) # goomba is not inside collision_sprite group, might have to change this
            if obj.name == 'koopa troopa': 
                #KoopaTroopa(self.game, (obj.x, obj.y), level_frames['koopa troopa'], (self.all_sprites, self.collision_sprites))    # is collidable, where player can stand on top of it
                KoopaTroopa(self.game, (obj.x, obj.y), level_frames['koopa troopa'], (self.all_sprites, self.damage_sprites, self.koopa_troopa_sprites), self.collision_sprites, self.player)   


    def create_laser_beam(self, pos, direction):
        LaserBeam(pos, (self.all_sprites, self.power_damage_sprites, self.laser_beam_sprites), self.laser_beam_surf, direction, 200)
        if not self.timers['sound block'].active: 
            self.laser_beam_sound.play()
        self.timers['sound block'].activate()
        
    def create_electricity(self, pos, direction):
        Electricity(pos, (self.all_sprites, self.power_damage_sprites, self.electricity_sprites), self.electricity_surf, direction, 100, self.collision_sprites)
        if not self.timers['sound block'].active: 
            self.electric_ball_sound.play()
        self.timers['sound block'].activate()

    def create_block(self, pos):
        Block(pos, self.block_surf, self.all_sprites)

    def create_flag(self, pos):
        Flag(pos, self.flag_surf, self.all_sprites)

    def create_item(self, pos):
        item_type = choice(['mushroom', 'electric flower', 'glitch mushroom'])
        #print(item_type)
        if not self.timers['item block'].active:
            if item_type == 'mushroom':
                self.item = Item(item_type=item_type, collision_sprites=self.collision_sprites, pos=pos, surf=self.mushroom_surf, groups=(self.all_sprites, self.item_sprites)) 
            elif item_type == 'glitch mushroom':
                self.item = Item(item_type=item_type, collision_sprites=self.collision_sprites, pos=pos, surf=self.glitch_mushroom_surf, groups=(self.all_sprites, self.item_sprites))  
            elif item_type == 'electric flower':
                self.item = Item(item_type=item_type, collision_sprites=self.collision_sprites, pos=pos, surf=self.electric_flower_surf, groups=(self.all_sprites, self.item_sprites))   
            
    def stomp_collision(self): 
        # Goombas
        for sprite in self.goomba_sprites:             
            if sprite.rect.colliderect(self.player.hitbox_rect):
                if self.player.hitbox_rect.bottom >= sprite.rect.top and int(self.player.old_rect.bottom) <= int(sprite.old_rect.top) and not sprite.is_dying:
                    Score(sprite.rect.topleft, sprite.score_200_surf, sprite.all_sprites)
                    self.data.score += 200
                    sprite.is_dying = True                
                    if not sprite.timers['sound block'].active: 
                        sprite.stomp_sound.play()
                        self.player.direction.y = -(self.player.jump_height - 50)
                    sprite.timers['sound block'].activate()
                    sprite.is_dying = True
                    sprite.timers['dying block'].activate() 

        # Koopa Troopas
        for sprite in self.koopa_troopa_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                if self.player.hitbox_rect.bottom >= sprite.rect.top and int(self.player.old_rect.bottom) <= int(sprite.old_rect.top) and not sprite.is_dying:
                    if not sprite.timers['sound block'].active: 
                        sprite.kick_sound.play()
                    sprite.timers['sound block'].activate()    
                    sprite.player.direction.y = -(self.player.jump_height - 50)
                    sprite.kill()
                    Shell(self.game, sprite.rect.topleft, self.shell_surf, (self.all_sprites, self.damage_sprites, self.shell_sprites), self.collision_sprites, self.player)
                    self.timers['shell block'].activate()            
        
        # Shells
        for sprite in self.shell_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                if self.player.hitbox_rect.bottom >= sprite.rect.top and int(self.player.old_rect.bottom) <= int(sprite.old_rect.top) and not sprite.is_dying:
                    if not sprite.timers['sound block'].active: 
                        sprite.kick_sound.play()
                    sprite.timers['sound block'].activate()    
                    sprite.player.direction.y = -(self.player.jump_height - 50)                    
                    if sprite.state == 'shell':       # player stops moving shell
                        sprite.state = 'idle shell'   
                        sprite.is_dying = False
                    elif sprite.state == 'idle shell' and not self.timers['shell block'].active:    # player hops on shell
                        sprite.is_dying = True
    
    def enemy_collision(self): 
        # Player takes damage
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):  
                if (self.player.hitbox_rect.left <= sprite.rect.right and int(self.player.old_rect.left) >= int(sprite.old_rect.right)) or (self.player.hitbox_rect.right >= sprite.rect.left and int(self.player.old_rect.right) <= int(sprite.old_rect.left)):            
                    if sprite in self.shell_sprites:
                        if sprite.state == 'idle shell':
                            sprite.direction = 1 if self.player.facing_right else -1
                            sprite.is_dying = True
                        else: # moving shell hurts player
                            if self.player.small and not self.player.timers['invincible'].active:                      
                                self.game.game_over()
                            else: 
                                self.player.get_damage()
                                if not self.timers['sound block'].active: 
                                    self.power_down_sound.play()
                                self.timers['sound block'].activate()                
                    else: 
                        if self.player.small and not self.player.timers['invincible'].active:                      
                            self.game.game_over()
                        else: 
                            self.player.get_damage()
                            if not self.timers['sound block'].active: 
                                self.power_down_sound.play()
                            self.timers['sound block'].activate()
        
    def shell_collision(self): 
        goomba_collisions = pg.sprite.groupcollide(self.shell_sprites, self.goomba_sprites, False, True)
        koopa_troopa_collisions = pg.sprite.groupcollide(self.shell_sprites, self.koopa_troopa_sprites, False, True)
        if len(goomba_collisions) > 0:
            if not self.timers['sound block'].active: 
                self.kick_sound.play()
            self.timers['sound block'].activate()
        if len(koopa_troopa_collisions) > 0:
            if not self.timers['sound block'].active: 
                self.kick_sound.play()
            self.timers['sound block'].activate()
    
    def power_collision(self):
        # Enemies perish if player's powers hit them
        terrain_collisions = pg.sprite.groupcollide(self.power_damage_sprites, self.collision_sprites, True, False)
        collisions = pg.sprite.groupcollide(self.power_damage_sprites, self.damage_sprites, True, True)
        
        if len(terrain_collisions) > 0:
            self.bump_sound.play()

        if len(collisions) > 0:
            if not self.timers['sound block'].active: 
                self.kick_sound.play()
            self.timers['sound block'].activate()
            # print("Enemy is hit!")
        
        for power_sprites, damage_sprites in collisions.items():
            for damage_sprite in damage_sprites:
                Score(damage_sprite.rect.topleft, self.score_200_surf, self.all_sprites)
                self.data.score += 200

    def item_box_collision(self):
        for sprite in self.item_box_sprites:
            player_top_rect = pg.Rect(self.player.hitbox_rect.topleft, (self.player.hitbox_rect.width, 2)) 
            item_box_bottom_rect = pg.Rect(sprite.rect.bottomleft, (sprite.rect.width, 2))
            if item_box_bottom_rect.colliderect(player_top_rect):
                self.create_block(sprite.rect.topleft)
                
                self.created_item = True
                self.create_item(sprite.rect.topleft)
                self.timers['item block'].activate()
                if not self.timers['sound block'].active: 
                    self.powerup_appears_sound.play()
                self.timers['sound block'].activate()
                sprite.kill()                
                
    def item_collision(self):  
        if self.item_sprites:
            item_sprites = pg.sprite.spritecollide(self.player, self.item_sprites, True)    # removes sprite and stores it in item_sprites
            if item_sprites:
                Score(item_sprites[0].rect.topleft, self.score_1000_surf, self.all_sprites)
                self.data.score += 1000
                print(item_sprites[0].item_type)
                if not self.timers['sound block'].active: 
                    self.powerup_sound.play()
                self.timers['sound block'].activate()             
                if item_sprites[0].item_type == 'glitch mushroom':
                    self.player.type = 'glitch'                    
                if item_sprites[0].item_type == 'electric flower':
                    self.player.type = 'electric'
                self.player.timers['flicker'].activate()
                self.player.small = False
                self.player.flicker() 

    def coin_collision(self): 
        if self.coin_sprites:
            coin_sprites = pg.sprite.spritecollide(self.player, self.coin_sprites, True)
            if coin_sprites:   
                self.coin_sound.play()             
                self.data.score += 200
                self.data.coin_count += 1
                
    def check_constraint(self): 
        # left and right; player should not move beyond tilemap
        if self.player.hitbox_rect.left <= 0:
            self.player.hitbox_rect.left = 0  
        if self.player.hitbox_rect.right >= self.level_width:
           self.player.hitbox_rect.right = self.level_width

        # bottom border; if player falls then game over
        if self.player.hitbox_rect.bottom > self.level_bottom:
             self.game.game_over()        

        # success; player cleared the stage        
        for sprite in self.bg_detail_sprites:
            if self.player.hitbox_rect.colliderect(sprite.rect) and self.created_flag == False:
                self.create_flag((sprite.rect.x + 8, sprite.rect.y + 8))
                self.created_flag = True
                self.stage_clear_sound.play()
                self.game.game_cleared()
    
    def update_timers(self): 
        for timer in self.timers.values():
            timer.update()

    def update(self, delta_time):
        self.display.fill(BG_COLOR)
        self.update_timers()
        self.all_sprites.update(delta_time) 
        self.stomp_collision()
        self.enemy_collision()
        self.shell_collision() 
        self.item_box_collision()
        self.item_collision()  
        self.coin_collision()
        self.power_collision() 
        self.check_constraint()
        self.all_sprites.draw(target_pos=self.player.hitbox_rect.center)
