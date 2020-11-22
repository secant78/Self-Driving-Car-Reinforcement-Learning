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
BLUE = (0,0,255)

# create the screen object
# here we pass it a size of 800x600
img_width = 800
img_height = 600
screen = pygame.display.set_mode((img_width, img_height))
clock = pygame.time.Clock()
button_font = pygame.font.SysFont("Segoe Print", 16)

X = img_width
Y = img_height
boundary_list = [
            ((0, 50), (X, 20), 'x'),  # walls: ((location), (size), direction)
            ((0, 530), (X, 20), 'x'),
            ]

# Getting our AI, which we call "brain", and that contains our neural network that represents our Q-function
brain = Dqn(9,3,0.9)
#last_reward = 0
#scores = []

# functions
def draw_dashed_line(surf, color, start_pos, end_pos, width=1, dash_length=10):
    origin = Point(start_pos)
    target = Point(end_pos)
    slope = Point()
    displacement = target - origin
    length = len(displacement)
    # slope = displacement / length
    slope.x = displacement.x/length
    slope.y = displacement.y/length

    for index in range(0, int(length/dash_length), 2):
        start = origin + (slope *    index    * dash_length)
        end   = origin + (slope * (index + 1) * dash_length)
        pygame.draw.line(surf, color, start.get(), end.get(), width)

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

class Boundary(pygame.sprite.Sprite):
    """
    The Boundary() object is a simple surface and Rect element.
    It has a direction ("x" or "y"); this is used to detect 
    when cars drive outside the lane
    """
    def __init__(self, location, size, direction):
        super(Boundary, self).__init__()
        self.surface = pygame.surface.Surface(size)
        self.surface.fill(WHITE)
        self.rect = self.surface.get_rect(topleft=location)
        self.dir = direction
    def draw(self):
        screen.blit(self.surface, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self,location):
        super(Player, self).__init__()
        self.width = 200
        self.height = 100
        self.image = pygame.image.load('white_car.png').convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.image.get_rect(center=location)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self):
        screen.blit(self.image, self.rect)
    def user_events(self,action):
        """
        Support function, handles user events; called from game.move_all().
        """
        # move the player
        if action == 0 and self.rect.top > 0:
            self.rect.top -= 5
        if action == 1:
            self.rect.top -= 0
        if action == 2 and self.rect.bottom < img_height:
            self.rect.top += 5
    
    def user_events_kb(self):
        """
        Support function, handles user events; called from game.move_all().
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.state = self.game.stop
                return
 
        # move the player
        keys = pygame.key.get_pressed()  # handles keys constantly pressed
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.left -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < X:
            self.rect.left += 5
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.top -= 5
        if keys[pygame.K_DOWN] and self.rect.bottom < Y:
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
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 10
    def draw(self):
        screen.blit(self.image, self.rect)
    def move(self):
        self.rect.move_ip(-self.speed, 0)
        # if self.rect.right < 0:
        #     self.kill()

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

class SensorState(pygame.sprite.Sprite):
    def __init__(self,location):
        super(SensorState, self).__init__()
        self.surface = pygame.surface.Surface([1, 1])
        self.x = location[0]
        self.y = location[1]
        self.rect = self.surface.get_rect(center=(self.x, self.y))
    def draw(self):
        screen.blit(self.surface, self.rect)
    

class Button():
    def __init__(self, txt, color, location, size):
        self.surf = pygame.Surface((size[0], size[1]))
        self.rect = self.surf.get_rect(center=location)
        self.surf.fill(WHITE)
        pygame.draw.rect(self.surf, BLACK, (0, 0, size[0], size[1]), 1)
        txt_surf = button_font.render(txt, 1, color)
        txt_rect = txt_surf.get_rect(center=(size[0]//2, size[1]//2))
        self.surf.blit(txt_surf, txt_rect)
 
    def draw(self):
        screen.blit(self.surf, self.rect)

class Game():
    def __init__(self):
        self.state = self.game_start  # the all-important game.state initialization
        self.score_record = []
        self.time_record = []
        self.flag = 0
    
    def game_start(self):
        "This game state generates a start screen"
        manual_mode = Button("Manual Mode", BLUE, (img_width//2, 300),(200,40))
        training_mode = Button("Training Mode", BLUE, (img_width//2, 350),(200,40))
        automatic_mode = Button("Automatic Mode", BLUE, (img_width//2, 400),(200,40))
        txt = "FINAL PROJECT - MATH 637"
        txt_surf = button_font.render(txt, 1, BLACK)
        txt_rect = txt_surf.get_rect(center=(img_width//2, 200))
        
        while True:  # wait for mouse click at button
            screen.fill(WHITE)
            screen.blit(txt_surf, txt_rect)
            manual_mode.draw()  #draw button
            training_mode.draw()
            automatic_mode.draw()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = self.stop
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if manual_mode.rect.collidepoint(pos):
                        self.flag = 1
                        self.state = self.init
                        return
                    if training_mode.rect.collidepoint(pos):
                        self.flag = 2
                        self.state = self.init
                        return
                    if automatic_mode.rect.collidepoint(pos):
                        self.flag = 3
                        self.state = self.init
                        return
            pygame.time.wait(20)
    def init(self):
        # create save button
        self.save_button = Button("Save", GREEN, (745, 25),(100,40))
        self.load_button = Button("Load", GREEN, (640, 25),(100,40))
        self.boundaries = pygame.sprite.Group()
        for item in boundary_list:
            new_boundary = Boundary(item[0], item[1], item[2])
            self.boundaries.add(new_boundary)
        self.state = self.start_timer
        self.initial_pos = [125,240,355,470] # possible initial positions
        self.factor = 0.034 # scaling factor for lateral distance
        self.epoch = 0
    def start_timer(self):
        self.start = pygame.time.get_ticks()  # used for timer
        self.epoch += 1
        
        self.state = self.game_loop
    def game_loop(self):
        lane = np.random.randint(4)
        if self.flag == 3:
            lane = 2
            brain.load()
        # create our 'player', right now he's just a rectangle
        self.player = Player((120,self.initial_pos[lane]))
        # dodged cars score
        self.score = 0
        self.background = pygame.Surface(screen.get_size())
        self.background.fill((128, 128, 128))
        # Create a custom event for adding a new enemy.
        self.ADDENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ADDENEMY, 3000)
        # ADDCLOUD = pygame.USEREVENT + 2
        # pygame.time.set_timer(ADDCLOUD, 1000)
        self.enemies = pygame.sprite.Group()
        # define dividers' positions
        self.dividers = (185,300,415)
        self.running = True
        state = (10.0)*np.ones(9)
        action = np.random.randint(3)
        while self.running:
            self.check_events()
            (next_state, reward) = self.environment(action)
            if self.flag == 2: # training mode
                action = brain.update(reward, next_state)
            state = next_state
            #
    def measurements(self,location,orientation,sensor_range,resolution):
        sensor_range_draw = sensor_range
        distance_draw = sensor_range_draw*resolution
        while sensor_range_draw >= 0:
            sensor_range_draw = sensor_range_draw - distance_draw
            x = int(location[0] + sensor_range_draw*np.cos(orientation))
            y = int(location[1] + sensor_range_draw*np.sin(orientation))
            sensor = Sensor((x,y))
            sensor.draw()
            if pygame.sprite.spritecollideany(sensor, self.enemies):
                sensor.kill()
        distance = sensor_range*0.01
        path = 0
        while sensor_range >= path:
            path = path + distance
            x = int(location[0] + path*np.cos(orientation))
            y = int(location[1] + path*np.sin(orientation))
            sensor_state = SensorState((x,y))
            if pygame.sprite.spritecollideany(sensor_state, self.enemies):
                d = math.sqrt(math.pow(x-location[0],2) + math.pow(y-location[1],2))
                break
            else:
                d = sensor_range
        return round(10*d/sensor_range,2)
    def display(self, num, x, y, message_format,color,font_size):
        """display the score"""
        # max_dodged = 10 
        font = pygame.font.SysFont("comicsansms", font_size)
        text = font.render(message_format.format(**num), True, color)
        screen.blit(text, (x, y))
    def stop(self):
        """
        This game state terminates the program
        """
        pygame.quit()
        sys.exit()
    def environment(self,action):
        """
        This the environment where the agent lives
        """
        vector = np.zeros(9)
        # action taken by the agent
        if self.flag == 1: # manual control
            self.player.user_events_kb()
        else:
            self.player.user_events(action)
        #
        # draw elements in the environments and get new state
        screen.blit(self.background, (0, 0))
        for i in range(len(self.dividers)):
            draw_dashed_line(screen, (255,255,255), (0,self.dividers[i]), (img_width,self.dividers[i]), width=5, dash_length=10)
        for boundary in self.boundaries:
                boundary.draw()
        sensor_range = 300
        resolution = 0.1
        angle_factor = (np.pi/180)
        self.posDir = [(self.player.rect.midtop,-90.0*angle_factor),\
                        (self.player.rect.topright,-45.0*angle_factor),\
                        (tuple(map(lambda x, y: (x + y)/2, self.player.rect.topright, self.player.rect.midright)),-22.5*angle_factor),\
                        (self.player.rect.midright,0),\
                        (tuple(map(lambda x, y: (x + y)/2, self.player.rect.bottomright, self.player.rect.midright)),22.5*angle_factor),\
                        (self.player.rect.bottomright,45.0*angle_factor),\
                        (self.player.rect.midbottom,90.0*angle_factor)]
        
        for k in range(len(self.posDir)):
            vector[k] = self.measurements(self.posDir[k][0],self.posDir[k][1],sensor_range,resolution)
        delta_l = (self.player.rect.centery-self.player.rect.height//2)-65
        delta_r = 535-(self.player.rect.centery+self.player.rect.height//2)
        vector[-2] = max(round(delta_l*self.factor,2),0.0)
        vector[-1] = max(round(delta_r*self.factor,2),0.0)
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        for enemy in self.enemies:
            enemy.move()
            if (enemy.rect.right < 0):
                enemy.kill()
                self.score += 1
        self.save_button.draw()
        self.load_button.draw()
        # set rewards
        reward = 0
        time = (pygame.time.get_ticks()-self.start)//100/10
        if pygame.sprite.spritecollideany(self.player, self.enemies, pygame.sprite.collide_mask):
            reward = -100
            self.player.kill()
            self.state = self.start_timer
            self.score_record.append(self.score)
            self.time_record.append(time)
            self.running = False
        if pygame.sprite.spritecollideany(self.player, self.boundaries):
            reward = -10
        #if self.player.rect.centery >= 120 and self.player.rect.centery <= 135:
        if self.player.rect.centery == self.initial_pos[0]:
            reward = 1
        #if self.player.rect.centery >= 235 and self.player.rect.centery <= 250:
        if self.player.rect.centery == self.initial_pos[1]:
            reward = 10
        #if self.player.rect.centery >= 350 and self.player.rect.centery <= 365:
        if self.player.rect.centery == self.initial_pos[2]:
            reward = 10
        #if self.player.rect.centery >= 465 and self.player.rect.centery <= 480:
        if self.player.rect.centery == self.initial_pos[3]:
            reward = 1
        # display information on screen
        data = {'SL': vector[0], 'SLF': vector[1], 'SMLF': vector[2], 'SF': vector[3], 'SMRF': vector[4], 'SRF': vector[5], 'SR': vector[6],
                'SDL': vector[7], 'SDR': vector[8]}
        total_score = {'Score':self.score}
        current_reward = {'Reward':reward}
        txt = "Self-Driving Car Project - Time: {0} - Epoch: {1} ".format(time,self.epoch)
        pygame.display.set_caption(txt)  # dynamic caption
        self.display(total_score, 350, 1, "SCORE: {Score}",GREEN,35)
        self.display(current_reward, 650, 550, "REWARD: {Reward}",YELLOW,22)
        self.display(data, 5, 550, "STATE: [{SL}, {SLF}, {SMLF}, {SF}, {SMRF}, {SRF}, {SR}, {SDL}, {SDR}]",BLACK,22)
        pygame.display.flip()
        clock.tick(30)
        # return new state and rewards
        return vector,reward
    def check_events(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.flag == 2:
                        print("saving scores")
                        np.array(self.score_record).dump(open('array_score.npy', 'wb'))
                        print("saving times")
                        np.array(self.time_record).dump(open('array_time.npy', 'wb'))
                        print("...done!")
                    self.running = False
                    self.state = self.game_start
            elif event.type == QUIT:
                self.running = False
                self.state = self.stop
            elif event.type == self.ADDENEMY:
                self.new_enemy = Enemy()
                self.enemies.add(self.new_enemy)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if self.save_button.rect.collidepoint(pos):
                    brain.save()
                if self.load_button.rect.collidepoint(pos):
                    brain.load()
            
def main():
    # initialize pygame
    game = Game()
    while True:
        game.state()
    quit() 

if __name__ == '__main__':
    main()