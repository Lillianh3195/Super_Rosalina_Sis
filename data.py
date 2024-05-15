from settings import *
import pygame.font 
import pygame.freetype
from timer import Timer
from os.path import join

class Data:
  def __init__(self, game, audio_files):
    self.game = game 
    self.display = game.display
    self.display_rect = game.display.get_rect()
    self.text_color = (255, 255, 255)
    self.score = 0
    self.countdown = 300
    self.coin_count = 0
    self.last_second = 0
    self.font = pg.font.SysFont(None, 24)
    self.time_warning_sound = audio_files['time warning']
    self.time_warning_sound.set_volume(0.4)
    self.timer = Timer(400)
    self.prep()


  def prep(self):
    self.prep_score()
    self.prep_time()
    self.prep_coin()

  def prep_score(self):
    # Turn the score into a rendered image     
    self.rosalina_str = 'Rosalina'
    self.rosalina_image = self.font.render(self.rosalina_str, True, self.text_color)
    self.rosalina_rect = self.rosalina_image.get_rect()
    self.rosalina_rect.left = self.display_rect.left + 20
    self.rosalina_rect.top += 10

    self.score_str = f'{self.score}'
    self.score_image = self.font.render(self.score_str, True, self.text_color)
    self.score_rect = self.score_image.get_rect()
    self.score_rect.left = self.display_rect.left + 20
    self.score_rect.top += 30

  def prep_time(self):
    self.time_str = 'Time'
    self.time_image = self.font.render(self.time_str, True, self.text_color)
    self.time_rect = self.time_image.get_rect()
    self.time_rect.right = self.display_rect.right - 20
    self.time_rect.top += 10
   
    self.countdown_str = f'{self.countdown}'
    self.countdown_image = self.font.render(self.countdown_str, True, self.text_color)
    self.countdown_rect = self.countdown_image.get_rect()
    self.countdown_rect.right = self.display_rect.right - 20
    self.countdown_rect.top += 30   

  def prep_coin(self):
    self.coin_str = f'x {self.coin_count}'
    self.coin_count_image = self.font.render(self.coin_str, True, self.text_color)
    self.coin_count_rect = self.coin_count_image.get_rect()
    self.coin_count_rect.centerx = self.display_rect.centerx + 25
    self.coin_count_rect.top += 30

    self.coin_image = pg.image.load(join('images', 'items', 'coins', '0.png'))
    self.coin_rect = self.coin_image.get_rect()
    self.coin_rect.centerx = self.display_rect.centerx 
    self.coin_rect.top += 28

   
  def draw(self):   
    self.display.blit(self.rosalina_image, self.rosalina_rect)
    self.display.blit(self.score_image, self.score_rect)
    self.display.blit(self.coin_image, self.coin_rect)
    self.display.blit(self.coin_count_image, self.coin_count_rect)
    self.display.blit(self.time_image, self.time_rect)    
    self.display.blit(self.countdown_image, self.countdown_rect) 

  def update(self, delta_time): 
    current_second = int(pg.time.get_ticks() / 1000)
    # Update countdown
    if current_second != self.last_second:
      self.countdown -= 1
      self.last_second = current_second
    # Play time warning if countdown reaches 50 seconds
    if self.countdown == 50:
      if not self.timer.active:
        self.time_warning_sound.play()
      self.timer.activate()
    # Game over if countdown reaches 0
    if self.countdown == 0:
      self.game.game_over()
    self.prep_score()
    self.prep_time()
    self.prep_coin()
    self.draw()
    
  
    
        


