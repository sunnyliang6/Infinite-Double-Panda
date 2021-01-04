####################################
# 15-112 Term Project
# Name: Sunny Liang
# This game is based on the original Double Panda game: 
# https://www.coolmathgames.com/0-double-panda
####################################

####################################
# This file contains: 
#   Player parent class
#       GiantPanda child class
#       Red Panda child class
#   Enemy parent class
#       BasicEnemy child class
#       ArcherEnemy child class
#   Weapon class 
# Each class contains properties of the object and may contain images.
####################################

import math, random, copy, time
import pygame as py
# following framework from cmu_112_graphics
from cmu_112_graphics import *

# players that the user controls
# two types of Player: GiantPanda and RedPanda
class Player(object):
    width = 50
    height = 56 # made this a class attribute to access in Platform
                # class without having to make an instance

    def __init__(self):
        self.walkSpeed = 10 # originally self.dx in main.py

        # movement booleans
        self.isWalkingRight = False
        self.isWalkingLeft = False
        self.isFalling = False
        self.isJumping = False
        self.reachedTopOfJump = False

        # jump-related
        jumpHeightConstant = 20
        self.jumpHeight = self.height + jumpHeightConstant
        self.jumpSpeed = 15
        self.jumpStartingHeight = self.y

        self.spriteCounter = 3
        self.spriteStanding = 3

        self.livesLeft = 5
        self.platformUnder = None

# one of the players is giant panda
class GiantPanda(Player):
    def __init__(self, name, app):
        self.name = name
        self.app = app

        # following pictures adapted from: https://www.coolmathgames.com/0-double-panda
        self.spritesRight = [self.app.loadImage('images/gp/gp-rspr1.png'),
                             self.app.loadImage('images/gp/gp-rspr2.png'),
                             self.app.loadImage('images/gp/gp-rspr3.png'),
                             self.app.loadImage('images/gp/gp-rspr4.png'),
                             self.app.loadImage('images/gp/gp-rspr5.png'),
                             self.app.loadImage('images/gp/gp-rspr6.png')]
        self.spritesLeft =  [self.app.loadImage('images/gp/gp-lspr1.png'),
                             self.app.loadImage('images/gp/gp-lspr2.png'),
                             self.app.loadImage('images/gp/gp-lspr3.png'),
                             self.app.loadImage('images/gp/gp-lspr4.png'),
                             self.app.loadImage('images/gp/gp-lspr5.png'),
                             self.app.loadImage('images/gp/gp-lspr6.png')]
        self.spritesCurrDir = self.spritesRight

        # starting position
        self.x = 250
        self.y = 475 # 475 is floorLevel, y is anchored south in view

        # corners of body
        self.x0 = self.x - self.width / 2
        self.x1 = self.x + self.width / 2
        self.y0 = self.y
        self.y1 = self.y - self.height

        super().__init__()

        # GiantPanda specific ability: killing enemies
        self.canKill = True
    
    def __eq__(self, other):
        return (isinstance(other, GiantPanda) and (self.name == other.name))

# the other player is red panda
class RedPanda(Player):
    def __init__(self, name, app):
        self.name = name
        self.app = app

        # following pictures adapted from: https://www.coolmathgames.com/0-double-panda
        self.spritesRight = [self.app.loadImage('images/rp/rp-rspr1.png'),
                             self.app.loadImage('images/rp/rp-rspr2.png'),
                             self.app.loadImage('images/rp/rp-rspr3.png'),
                             self.app.loadImage('images/rp/rp-rspr4.png'),
                             self.app.loadImage('images/rp/rp-rspr5.png'),
                             self.app.loadImage('images/rp/rp-rspr6.png')]
        self.spritesLeft =  [self.app.loadImage('images/rp/rp-lspr1.png'),
                             self.app.loadImage('images/rp/rp-lspr2.png'),
                             self.app.loadImage('images/rp/rp-lspr3.png'),
                             self.app.loadImage('images/rp/rp-lspr4.png'),
                             self.app.loadImage('images/rp/rp-lspr5.png'),
                             self.app.loadImage('images/rp/rp-lspr6.png')]
        self.spritesCurrDir = self.spritesRight

        # starting position
        self.x = 180 # default otherPlayer is set back from currPlayer
        self.y = 475 # 475 is floorLevel, y is anchored south in view

        # corners of body
        self.x0 = self.x - self.width / 2
        self.x1 = self.x + self.width / 2
        self.y0 = self.y
        self.y1 = self.y - self.height

        super().__init__()

        # RedPanda specific ability: climbing
        self.climbSpeed = 10
        self.isClimbingUp = False
        self.isClimbingDown = False
        self.isOnBamboo = False
        self.isJumpingOffBambooRight = False
        self.isJumpingOffBambooLeft = False
    
    def __eq__(self, other):
        return (isinstance(other, RedPanda) and (self.name == other.name))

# enemies cause players to lose lives when they collide or get attacked
# two types of Enemy: BasicEnemy and ArcherEnemy
class Enemy(object):
    width = 50 
    height = 60

    def __init__(self, platform, app):
        self.walkSpeed = 5
        self.spriteCounter = 0

        # Enemy is on a platform
        self.platform = platform
        self.maxLeft = platform.x0 + Enemy.width / 2
        self.maxRight = platform.x1 - Enemy.width / 2

        # starting position
        self.x = random.randint(self.maxLeft, self.maxRight)
        self.y = app.floorLevel - platform.height
        self.collidingWithPlayers = False

        # corners of body
        self.x0 = self.x - self.width / 2
        self.x1 = self.x + self.width / 2
        self.y0 = self.y
        self.y1 = self.y - self.height

        self.collidingWithGP = False
        self.collidingWithRP = False

    # following function derived from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
    def getSprites(self, spritesheet, spriteY0, spriteY1):
        # get sprites from one spritesheet
        spritesInDir = [ ]
        for i in range(4):
            spriteWidth = 350 # based on image at url
            spriteSheetMargin = 50 # based on image at url
            spriteSheetWidth, spriteSheetHeight = spritesheet.size
            sprite = spritesheet.crop((spriteSheetMargin+spriteSheetWidth/4*i, 
                                       spriteY0, 
                                       spriteWidth+spriteSheetWidth/4*i, 
                                       spriteY1))
            scaleFactor = Enemy.width / spriteWidth
            sprite = self.app.scaleImage(sprite, scaleFactor)
            spritesInDir.append(sprite)
        return spritesInDir

    # check if the enemy is colliding with given player
    def checkCollisions(self, player):
        playerX0 = player.x0 + 5 # leeway
        playerX1 = player.x1 - 5

        if not (player.y0 <= self.y1): # cannot lose life from jumping on enemy head
            if (self.y1 <= player.y1 < self.y0 and
                (self.x0 <= playerX1 <= self.x1 or self.x0 <= playerX0 <= self.x1)):
                if (player.name == 'Giant Panda'):
                    self.collidingWithGP = True
                if (player.name == 'Red Panda'):
                    self.collidingWithRP = True
            else: # finish colliding
                if (self.collidingWithGP and player.name == 'Giant Panda'):
                    self.collidingWithGP = False
                    return True
                if (self.collidingWithRP and player.name == 'Red Panda'):
                    self.collidingWithRP = False
                    return True
        return False

# BasicEnemy wanders on a platform and can walk towards the player
class BasicEnemy(Enemy):
    def __init__(self, platform, app):
        super().__init__(platform, app)
        self.name = 'Basic Enemy'
        self.app = app
        self.scoreGain = 250

        # following pictures adapted from: https://www.coolmathgames.com/0-double-panda
        # self.spritesRight = [self.app.loadImage('images/be-rspr1.png'),
        #                          self.app.loadImage('images/be-rspr2.png'),
        #                          self.app.loadImage('images/be-rspr3.png'),
        #                          self.app.loadImage('images/be-rspr4.png'),
        #                          self.app.loadImage('images/be-rspr5.png'),
        #                          self.app.loadImage('images/be-rspr6.png')]
        # self.spritesLeft =  [self.app.loadImage('images/be-lspr1.png'),
        #                          self.app.loadImage('images/be-lspr2.png'),
        #                          self.app.loadImage('images/be-lspr3.png'),
        #                          self.app.loadImage('images/be-lspr4.png'),
        #                          self.app.loadImage('images/be-lspr5.png'),
        #                          self.app.loadImage('images/be-lspr6.png')]
        # self.spritesCurrDir = self.spritesRight
        spritesheet = self.app.loadImage('images/basicenemysprites.png')
        spriteHeight = 420 # based on image at url
        self.spritesRight = self.getSprites(spritesheet, 1900, 1900 + spriteHeight)
        self.spritesLeft = self.getSprites(spritesheet, 1300, 1300 + spriteHeight)
        self.spritesCurrDir = self.spritesRight

    # when the GiantPanda kills the enemy, it gains points from the enemy
    def die(self):
        return self.scoreGain

    def __eq__(self, other):
        return (isinstance(other, BasicEnemy) and (self.x == other.x) and (self.y == other.y))

    def __repr__(self):
        return f'{self.name} at ({self.x}, {self.y})'

# ArcherEnemy wanders and attacks using Weapon
class ArcherEnemy(Enemy):
    def __init__(self, platform, app):
        super().__init__(platform, app)
        self.name = 'Archer Enemy'
        self.app = app
        self.scoreGain = 300

        # following pictures adapted from: https://www.coolmathgames.com/0-double-panda
        # self.spritesRight = [self.app.loadImage('images/ae-rspr1.png'),
        #                          self.app.loadImage('images/ae-rspr2.png'),
        #                          self.app.loadImage('images/ae-rspr3.png'),
        #                          self.app.loadImage('images/ae-rspr4.png'),
        #                          self.app.loadImage('images/ae-rspr5.png'),
        #                          self.app.loadImage('images/ae-rspr6.png')]
        # self.spritesLeft =  [self.app.loadImage('images/ae-lspr1.png'),
        #                          self.app.loadImage('images/ae-lspr2.png'),
        #                          self.app.loadImage('images/ae-lspr3.png'),
        #                          self.app.loadImage('images/ae-lspr4.png'),
        #                          self.app.loadImage('images/ae-lspr5.png'),
        #                          self.app.loadImage('images/ae-lspr6.png')]
        # self.spritesCurrDir = self.spritesRight
        spritesheet = self.app.loadImage('images/archerenemysprites.png')
        spriteHeight = 420 # based on image at url
        self.spritesRight = self.getSprites(spritesheet, 1900, 1900 + spriteHeight)
        self.spritesLeft = self.getSprites(spritesheet, 1300, 1300 + spriteHeight)
        self.spritesCurrDir = self.spritesRight

        # ArcherEnemy specific ability: shooting
        self.tempShootingSprite = None
        self.weapon = Weapon(self.x, self.y - (self.height // 2), self.app)
        self.isShooting = False
        self.shootCount = 0 # can only shoot 3 times at once every 3 seconds
        self.shootingWaitTime = 3 # seconds
        self.shootingStartWaitTime = 0

    # when the GiantPanda kills the enemy, it gains points from the enemy
    def die(self):
        return self.scoreGain

    # reset the Weapon and reset boolean
    def resetWeapon(self):
        self.isShooting = False
        self.weapon.reset(self.x, self.y - (self.height // 2))

    def __eq__(self, other):
        return (isinstance(other, ArcherEnemy) and (self.x == other.x) and (self.y == other.y))
    
    def __repr__(self):
        return f'{self.name} at ({self.x}, {self.y})'

# ArcherEnemy can use this to attack
class Weapon(object):
    def __init__(self, x, y, app):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.v = 13 # shooting speed

        # target position
        self.xt = 0
        self.yt = 0
        self.targetPlayer = None

    # determine the dx and dy needed to increment the Weapon towards the target
    def shootingCalculations(self, xt, yt, player):
        self.xt = xt
        self.yt = yt
        self.targetPlayer = player
        distX = xt - self.x
        distY = yt - self.y
        distance = ((distX) ** 2 + (distY) ** 2) ** 0.5
        if (distance > 0):
            angle = math.acos(distX / distance)
        self.dx = self.v * math.cos(angle)
        self.dy = self.v * math.sin(angle)
    
    # reset the Weapon to default values
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.targetPlayer = None