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
brain = Dqn(3,3,0.9)
action2rotation = [0,1,2]
last_reward = 0
scores = []

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
        self.rect = self.image.get_rect(topleft=location)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self):
        screen.blit(self.image, self.rect)
    def user_events(self,action):
        """
        Support function, handles user events; called from game.move_all().
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.state = self.game.stop
                return
 
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
        self.score_record = []
        self.time_record = []
    
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
        self.boundaries = pygame.sprite.Group()
        for item in boundary_list:
            new_boundary = Boundary(item[0], item[1], item[2])
            self.boundaries.add(new_boundary)
        self.state = self.game_loop

    def game_loop(self):
        global brain
        global last_reward
        global scores

        # create our 'player', right now he's just a rectangle
        self.save_button = Button("Save", GREEN, (710, 570))
        self.load_button = Button("Load", GREEN, (710, 20))
        self.player = Player((20,80))
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
        self.vector = np.zeros(3)
        state = (10.0)*np.ones(3)
        action = np.random.randint(3)
        
        while self.running:
            self.check_events()
            #action = np.random.randint(3)
            (state,reward) = self.environment(action)
            last_state = state
            last_reward = reward
            action = brain.update(last_reward, last_state)
            scores.append(brain.score())

            #print(reward)
    def measurements(self,location,orientation,range,resolution):
        self.d = range*resolution
        self.reading = pygame.sprite.Group()
        self.elements = int(1/resolution)
        self.read_array = np.ones(self.elements)
        self.elements_array = np.ones(self.elements)
        self.count = self.elements
        self.detected = self.elements
        while range >= 0:
            self.detected -= 1
            range = range - self.d
            self.x = int(location[0] + range*np.cos(orientation))
            self.y = int(location[1] + range*np.sin(orientation))
            self.sensor = Sensor((self.x,self.y))
            self.sensor.draw()
            if pygame.sprite.spritecollideany(self.sensor, self.enemies):
                self.count = self.detected
                self.sensor.kill()
        self.elements_array[self.elements:self.count:-1] = 0
        return np.sum(self.elements_array)
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
        print(self.score_record)
        print(self.time_record)
        pygame.quit()
        sys.exit()
    def environment(self,action):
        """
        This the environment where the agent lives
        """
        # action taken by the agent
        self.player.user_events(action)
        #self.player.user_events_kb()
        # draw elements in the environments and get new state
        screen.blit(self.background, (0, 0))
        for i in range(len(self.dividers)):
            draw_dashed_line(screen, (255,255,255), (0,self.dividers[i]), (img_width,self.dividers[i]), width=5, dash_length=10)
        for boundary in self.boundaries:
                boundary.draw()
        self.range = 300
        self.resolution = 0.1
        self.posDir = [(self.player.rect.topright,-np.pi/8),(self.player.rect.midright,0),(self.player.rect.bottomright,np.pi/8)]
        for k in range(len(self.posDir)):
            self.vector[k] = self.measurements(self.posDir[k][0],self.posDir[k][1],self.range,self.resolution)
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
            self.player.kill()
            self.running = False
            self.state = self.init
            self.score_record.append(self.score)
            self.time_record.append(time)
            reward -= 100
        if pygame.sprite.spritecollideany(self.player, self.boundaries):
            reward -= 50
        if self.player.rect.centery >= 120 and self.player.rect.centery <= 135:
            reward += 25
        if self.player.rect.centery >= 235 and self.player.rect.centery <= 250:
            reward += 25
        if self.player.rect.centery >= 350 and self.player.rect.centery <= 365:
            reward += 25
        if self.player.rect.centery >= 465 and self.player.rect.centery <= 480:
            reward += 25
        # display information on screen
        self.data = {'SL': self.vector[0], 'SC': self.vector[1], 'SR': self.vector[2]}
        self.total_score = {'Score':self.score}
        self.current_reward = {'Reward':reward}
        self.y_position = {'Position':self.player.rect.centery}
        txt = "Self-Driving Car - Time: {} ".format(time)
        pygame.display.set_caption(txt)  # dynamic caption
        self.display(self.total_score, 500, 2, "SCORE: {Score}",GREEN,35)
        self.display(self.data, 30, 550, "STATE: [{SL}, {SC}, {SR}]",BLACK,25)
        self.display(self.current_reward, 350, 550, "REWARD: {Reward}",YELLOW,25)
        self.display(self.y_position, 550, 550, "y: {Position}",BLUE,25)
        pygame.display.flip()
        clock.tick(30)
        # return new state and rewards
        return self.vector,reward
    def check_events(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
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
                    self.running = False
                    self.state = self.stop
                elif self.load_button.rect.collidepoint(pos):
                    brain.load()
                    
                



def main():
    # initialize pygame
    game = Game()
    while True:
        game.state()
    quit() 

if __name__ == '__main__':
    main()