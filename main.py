from settings import *
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import join
from support import *
from data import Data
from button import Button
from timer import Timer

class LaunchScreen:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen_rect = self.screen.get_rect()
        pg.display.set_caption('Super Rosalina Sis.')

        self.game_active = False              # MUST be before Button is created
        self.play_button = Button(game=self, text='PLAY GAME', x=self.screen_rect.centerx, y=self.screen_rect.centery + 150)
        self.launch_screen_music = pg.mixer.Sound(join('sound', 'Morning Peppermint.wav'))
        self.bg_music = pg.mixer.Sound(join('sound', 'bg music.wav'))
        self.bg_music.set_volume(0.2)
        self.prepare_launch_screen()

    def check_events(self):
        for event in pg.event.get():
            type = event.type
            if type == pg.QUIT:
                pg.quit()
                sys.exit() 
            elif type == pg.MOUSEBUTTONDOWN: 
                b = self.play_button
                x, y = pg.mouse.get_pos()
                if b.rect.collidepoint(x, y):
                    b.press_play()
            elif type == pg.MOUSEMOTION: 
                b = self.play_button
                x, y = pg.mouse.get_pos()
                b.select(b.rect.collidepoint(x, y))

    def activate(self): 
        self.launch_screen_music.stop()
        g = Game()
        g.play()

    def prepare_launch_screen(self):
        self.launch_screen_music.play(loops=-1)
        self.mountain_image = pg.transform.scale_by(pg.image.load(join('images', 'bg', 'mountains.png')), 2.4)
        self.mountain_image_rect = self.mountain_image.get_rect()
        self.mountain_image_rect.y -= 300

        self.logo_image = pg.image.load(join('images', 'bg', 'logo.png'))
        self.logo_image_rect = self.logo_image.get_rect()
        self.logo_image_rect.y -= 100        

    def run_launch_screen(self):
        """Start launch screen loop for the game."""
        while True:  
            self.check_events()
            self.update()

    def draw(self):
        self.screen.blit(self.mountain_image, self.mountain_image_rect) 
        self.screen.blit(self.logo_image, self.logo_image_rect) 
    
    def update(self):  
        # Update images on the screen, and flip to the new screen
        self.screen.fill((162, 225, 232))
        self.draw()
        self.play_button.update()
        pg.display.flip()

    
class Game:
    def __init__(self):
        pg.init()
        # render onto the smaller display, then scale it up to the screen
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display = pg.Surface((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.display_rect = self.display.get_rect()
        self.screen_rect = self.screen.get_rect()
        pg.display.set_caption('Super Rosalina Sis.')
        self.clock = pg.time.Clock()

        self.game_active = True
        self.play_button = Button(game=self, text='Play again?', x=self.screen_rect.centerx, y=self.screen_rect.centery - 200)
        self.bg_music = pg.mixer.Sound(join('sound', 'bg music.wav'))
        self.bg_music.set_volume(0.2)
        self.bg_music.play(loops=-1)
        self.gameover_sound = pg.mixer.Sound(join('sound', 'dead.wav'))
        self.gameover_sound.set_volume(0.4)
        self.timer = Timer(500)        
        self.import_assets()
        self.data = Data(game=self, audio_files=self.audio_files)

        self.tmx_maps = {0: load_pygame(join('data', 'tilemap.tmx'))}
        self.level = Level(game=self, tmx_map=self.tmx_maps[0], level_frames=self.level_frames, audio_files=self.audio_files, data=self.data)

    def import_assets(self):
        self.level_frames = {
            'flag': import_image('images', 'items', 'flag'),
            'item box': import_folder('images', 'item_box'),
            'player': import_sub_folders('images', 'player'),
            'goomba': import_sub_folders('images', 'enemies', 'goomba'),
            'koopa troopa': import_sub_folders('images', 'enemies', 'koopa troopa'),
            'laser beam': import_folder('images', 'items', 'laser beam'),
            'electricity': import_folder('images', 'items', 'electricity'),
            'normal mushroom': import_image('images', 'items', 'normal mushroom'),
            'glitch mushroom': import_image('images', 'items', 'glitch mushroom'),
            'electric flower': import_image('images', 'items', 'electric flower'),
            'block': import_image('images', 'items', 'block'),
            'coin': import_folder('images', 'items', 'coins'),
            '200': import_image('images', 'items', '200'),
            '1000': import_image('images', 'items', '1000')
        }
        #print(self.level_frames)

        self.audio_files = {
            'bump': pg.mixer.Sound(join('sound', 'bump.wav')),
            'coin': pg.mixer.Sound(join('sound', 'coin.wav')),
            'dead': pg.mixer.Sound(join('sound', 'dead.wav')),
            'electric ball': pg.mixer.Sound(join('sound', 'electric ball.wav')),
            'flag pole': pg.mixer.Sound(join('sound', 'flag pole.wav')),
            'game over': pg.mixer.Sound(join('sound', 'game over.wav')),
            'kick': pg.mixer.Sound(join('sound', 'kick.wav')),
            'laser beam': pg.mixer.Sound(join('sound', 'laser beam.wav')),
            'power down': pg.mixer.Sound(join('sound', 'power down.wav')),        
            'powerup appears': pg.mixer.Sound(join('sound', 'powerup appears.wav')),
            'powerup': pg.mixer.Sound(join('sound', 'powerup.wav')),
            'small jump': pg.mixer.Sound(join('sound', 'small jump.wav')),
            'stage clear': pg.mixer.Sound(join('sound', 'stage clear.wav')),
            'stomp': pg.mixer.Sound(join('sound', 'stomp.wav')),
            'super jump': pg.mixer.Sound(join('sound', 'super jump.wav')),
            'time warning': pg.mixer.Sound(join('sound', 'time warning.wav'))          
        }

    def check_events(self):
        for event in pg.event.get():
            type = event.type
            if type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif type == pg.MOUSEBUTTONDOWN:
                b = self.play_button
                x, y = pg.mouse.get_pos()
                if b.rect.collidepoint(x, y):
                    b.press_play()
            elif type == pg.MOUSEMOTION:
                b = self.play_button
                x, y = pg.mouse.get_pos()
                b.select(b.rect.collidepoint(x, y))

    def game_cleared(self):
        self.bg_music.stop()
        pg.mouse.set_visible(True)
        self.play_button.show()
        self.game_active = False
        print('Stage Cleared!')

    def restart(self):
        g = Game()
        g.play()

    def game_over(self):        
        print('Game Over !') 
        self.gameover_sound.play() 
        self.bg_music.stop()
        time.sleep(3)      
        self.restart()

    def activate(self): 
        self.game_active = True
        self.restart()
    
    def play(self):
        finished = False
        self.display.fill(BG_COLOR)

        while not finished:
            self.check_events()

            if self.game_active:
                delta_time = self.clock.tick(60) / 1000      # get time in seconds, so 60fps
                self.check_events()
                self.level.update(delta_time)
                self.data.update(delta_time)            
                self.screen.blit(pg.transform.scale(self.display, self.screen.get_size()), (0, 0))   #scale display up to screen
                pg.display.update()                  
            else:
                self.play_button.update()             

            pg.display.flip()  
            #time.sleep(0.02)  

if __name__ == '__main__':
    l = LaunchScreen()
    l.run_launch_screen()