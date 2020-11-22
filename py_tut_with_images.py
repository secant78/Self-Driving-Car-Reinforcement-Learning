import sys
# import the pygame module
import pygame

# import random for random numbers!
import random

import time

import math

import numpy as np

# import pygame.locals for easier access to key coordinates
from pygame.locals import *

# Importing the Dqn object from our AI in ai.py
from aii import Dqn

pygame.init()

# colors definition
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (20, 200, 50)

brain = Dqn(3,3,0.9)
last_reward = 0
action2rotation = [0,10,-10]
scores = []

# create the screen object
# here we pass it a size of 800x600
img_width = 800
img_height = 600
screen = pygame.display.set_mode((img_width, img_height))
clock = pygame.time.Clock()
button_font = pygame.font.SysFont("Segoe Print", 16)

# functions
def draw_dashed_line(surf, color, start_pos, end_pos, width=1, dash_length=10):
    origin = Point(start_pos)
    target = Point(end_pos)
    slope = Point()
    displacement = target - origin
    length = len(displacement)
    slope.x = displacement.x/length
    slope.y = displacement.y/length

    for index in range(0, int(length/dash_length), 2):
        start = origin + (slope *    index    * dash_length)
        end   = origin + (slope * (index + 1) * dash_length)
        pygame.draw.line(surf, color, start.get(), end.get(), width)

def draw_solid_line(surf, color, start_pos, end_pos, width=1):
    origin = Point(start_pos)
    target = Point(end_pos)
    pygame.draw.line(surf, color, origin.get(), target.get(), width)

# classes

class Point:
    # constructed using a normal tupple
    def __init__(self, point_t = (0,0)):
        self.x = float(point_t[0])
        self.y = float(point_t[1])
    # define all useful operators
    def __add__(self, other):
        return Point((self.x + other.x, self.y + other.y))
    def __sub__(self, other):
        return Point((self.x - other.x, self.y - other.y))
    def __mul__(self, scalar):
        return Point((self.x*scalar, self.y*scalar))
    def __div__(self, scalar):
        return Point((self.x/scalar, self.y/scalar))
    def __len__(self):
        return int(math.sqrt(self.x**2 + self.y**2))
    # get back values in original tuple format
    def get(self):
        return (self.x, self.y)


class Player(pygame.sprite.Sprite):
    def __init__(self,location):
        super(Player, self).__init__()
        self.width = 200
        self.height = 100
        self.image = pygame.image.load('white_car.png').convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.image.get_rect(topleft=location)

    def draw(self):
        screen.blit(self.image, self.rect)
    def user_events(self):
        """
    Support function, handles user events; called from game.move_all().
    """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.state = game.stop
                return
 
        # move the player
        #self.rect.top -=5
        keys= pygame.key.get_pressed()  # handles keys constantly pressed
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.left -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < img_width:
            self.rect.left += 5
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.top -= 5
        if keys[pygame.K_DOWN] and self.rect.bottom < img_height:
            self.rect.top += 5

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.width = 200
        self.height = 100
        self.image = pygame.image.load('yellow_car.png').convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        self.lane = random.randint(0, 3)
        self.lanePos = (80,195,310,425)
        self.rect = self.image.get_rect(
            topleft=(random.randint(820, 900), self.lanePos[self.lane]))
        self.speed = 10
        self.killed = 0
        
    def move(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

class Sensor(pygame.sprite.Sprite):
    def __init__(self,location):
        super(Sensor, self).__init__()
        self.surface = pygame.surface.Surface([6, 6])
        self.surface.fill(WHITE)
        pygame.draw.circle(self.surface, RED, [3, 3], 3)
        self.surface.set_colorkey(WHITE)
        self.x = location[0]
        self.y = location[1]
        self.rect = self.surface.get_rect(center=(self.x, self.y))
    def draw(self):
        screen.blit(self.surface, self.rect)
    

class Button():
    def __init__(self, txt, color, location):
        self.surf = pygame.Surface((100, 40))
        self.rect = self.surf.get_rect(center=location)
        self.surf.fill(WHITE)
        pygame.draw.rect(self.surf, BLACK, (0, 0, 100, 40), 1)
        txt_surf = button_font.render(txt, 1, color)
        txt_rect = txt_surf.get_rect(center=(50, 20))
        self.surf.blit(txt_surf, txt_rect)
 
    def draw(self):
        screen.blit(self.surf, self.rect)

class Game():
    
    def __init__(self):
        self.state = self.game_start  # the all-important game.state initialization
    
    def game_start(self):
        "This game state generates a start screen"
        play = Button("Play", GREEN, (img_width//2, 400))
        txt = "Demo - place any GAME START text here"
        txt_surf = button_font.render(txt, 1, BLACK)
        txt_rect = txt_surf.get_rect(center=(img_width//2, 200))
        while True:  # wait for mouse click at button
            screen.fill(WHITE)
            screen.blit(txt_surf, txt_rect)
            play.draw()  #draw button
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = self.stop
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if play.rect.collidepoint(pos):
                        self.state = self.init
                        return
            pygame.time.wait(20)
    def init(self):
        self.start = pygame.time.get_ticks()  # used for timer
        self.state = self.game_loop

    def game_loop(self):
        # create our 'player', right now he's just a rectangle
        global last_reward
        global scores
        self.player = Player((20,80))

        background = pygame.Surface(screen.get_size())
        background.fill((128, 128, 128))
        # Create a custom event for adding a new enemy.
        ADDENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(ADDENEMY, 3000)
        # ADDCLOUD = pygame.USEREVENT + 2
        # pygame.time.set_timer(ADDCLOUD, 1000)
        self.enemies = pygame.sprite.Group()
        # clouds = pygame.sprite.Group()
        all_sprites = pygame.sprite.Group()
        all_sprites.add(self.player)

        # define dividers' positions
        dividers = (185,300,415)
        # define boundaries' positions
        boundaries = (50,530)

        running = True
        self.vector = np.zeros(3)
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                        self.state = self.game_start
                elif event.type == QUIT:
                    running = False
                elif event.type == ADDENEMY:
                    self.new_enemy = Enemy()
                    self.enemies.add(self.new_enemy)
                    all_sprites.add(self.new_enemy)
                    
            screen.blit(background, (0, 0))
            for i in range(len(dividers)):
                draw_dashed_line(screen, (255,255,255), (0,dividers[i]), (img_width,dividers[i]), width=5, dash_length=10)
            for j in range(len(boundaries)):
                draw_solid_line(screen, (255,255,255), (0,boundaries[j]), (img_width,boundaries[j]), width=20)
            #pressed_keys = pygame.key.get_pressed()
            self.player.user_events()
            self.player.draw()
            self.range = 200
            self.resolution = 0.1
            self.vector[0] = self.measurements(self.player.rect.midright,0,self.range,self.resolution)
            self.vector[1] = self.measurements(self.player.rect.topright,-np.pi/8,self.range,self.resolution)
            self.vector[2] = self.measurements(self.player.rect.bottomright,np.pi/8,self.range,self.resolution)
            
            #print(self.vector)
            
            last_signal = [self.vector[0], self.vector[1], self.vector[2]]
        
            #print(last_signal)
            action = brain.update(last_reward, last_signal)
            #print(action)
            
            scores.append(brain.score())
            
            rotation = action2rotation[action]
            
            #print(rotation)
            
            
            
            
            #self.rect.top -=5
            #self.rect.top +=5
            
            if rotation == 10 and self.player.rect.top >5:
                for i in range(0,10):
                    
                    self.player.rect.top -=1
                    last_reward = 50
                
            elif rotation == -10 and self.player.rect.bottom <img_height - 5:
                for i in range(0,10):
                    self.player.rect.top +=1
                    last_reward = 50
            
            #enemies.move()
            # clouds.update()
            for entity in all_sprites:
                screen.blit(entity.image, entity.rect)
            for enemy in self.enemies:
                enemy.move()
                
                
            if pygame.sprite.spritecollideany(self.player, self.enemies):
                self.player.kill()
                last_reward = -500
                running = False
                self.state = self.init
                
                
            #if pygame.sprite.spritecollideany(self.player, self.enemies):
            #    last_reward = -500
            
                
            else: # otherwise
                last_reward = 100 # driving towards objective reward

            #if self.player.rect.top <5:
            #    last_reward = -100
            
            #if self.player.rect.top >= 5:
            #    last_reward = 50
            
            #if self.player.rect.bottom < img_height -5:
            #    last_reward = 50
            
            #if self.player.rect.bottom >= img_height -5:
            #    last_reward = -100
            
            print(last_reward)
               

            pygame.display.flip()
            clock.tick(30)
    
    '''
    def update(self):
        global last_reward
        global brain
        
        
        
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            last_reward = -500
            
                
        else: # otherwise
            last_reward = 100 # driving towards objective reward

        if self.player.rect.top == 0:
            last_reward = -100
            
        if self.player.rect.top > 0:
            last_reward = 50
            
        if self.player.rect.bottom < img_height:
            last_reward = 50
            
        if self.player.rect.bottom == img_height:
            last_reward = -100
            
        print(last_reward)
            
        '''
            
    def measurements(self,location,orientation,range,resolution):
        self.d = range*resolution
        self.reading = pygame.sprite.Group()
        self.elements = int(1/resolution)
        self.read_array = np.ones(self.elements)
        self.points = 0
        while range >= 0:
            range = range - self.d
            self.x = int(location[0] + range*np.cos(orientation))
            self.y = int(location[1] + range*np.sin(orientation))
            self.sensor = Sensor((self.x,self.y))
            self.sensor.draw()
            self.reading.add(self.sensor)
        
        for sensor in self.reading:
            for enemy in self.enemies:
                if sensor.rect.colliderect(enemy.rect):
                    self.reading.remove(sensor)
                    self.points = self.points + 1
                    self.read_array[self.elements:self.elements-self.points:-1] = 0
        return np.sum(self.read_array)
    
     
    '''
    def update(self):

        global brain
        global last_reward
        global score


        #orientation = Vector(*self.car.velocity).angle((xx,yy))/180.
        #last_signal = [self.car.signal1, self.car.signal2, self.car.signal3, orientation, -orientation]
        last_signal = [self.vector[0], self.vector[1], self.vector[2]]
        
        print(last_signal)
        action = brain.update(last_reward, last_signal)
        scores.append(brain.score())
        rotation = action2rotation[action]
        #print(rotation)
        self.car.move(rotation)
        distance = np.sqrt((self.car.x - goal_x)**2 + (self.car.y - goal_y)**2)
        self.ball1.pos = self.car.sensor1
        self.ball2.pos = self.car.sensor2
        self.ball3.pos = self.car.sensor3
        
#        self.steps += 1
        
        if sand[int(self.car.x),int(self.car.y)] > 0:
            self.car.velocity = Vector(1, 0).rotate(self.car.angle)
            last_reward = -500 # sand reward
        else: # otherwise
            self.car.velocity = Vector(1, 0).rotate(self.car.angle)
            last_reward = -40.0#/(distance+1)  # driving away from objective reward
            if distance < last_distance:
                last_reward = 500.0#/(distance+1) # driving towards objective reward

        if self.car.x < 10:
            self.car.x = 10
            last_reward = -100 # too close to edges of the wall reward
        if self.car.x > self.width - 10:
            self.car.x = self.width - 10
            last_reward = -100 #
        if self.car.y < 10:
            self.car.y = 10
            last_reward = -100 #
        if self.car.y > self.height - 10:
            self.car.y = self.height - 10
            last_reward = -100 #

#        if distance < 100:
#            goal_x = self.width-goal_x
#            goal_y = self.height-goal_y
#            last_reward = self.last_steps - self.steps # reward for reaching the objective faster than last round (may want to scale this)
#            self.last_steps = self.steps 
#            self.steps = 0
        last_distance = distance
       # print(last_reward)
       
       '''

def main():
    #game_init()
    #game_intro()
    # initialize pygame
    
    game = Game()
    while True:
        game.state()

    
    
    #game_loop()
    #pygame.quit()
    quit() 

if __name__ == '__main__':
    main()