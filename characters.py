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

# following framework from cmu_112_graphics
from cmu_112_graphics import *

# players that the user controls
# two types of Player: GiantPanda and RedPanda
class Player(object):
    scaledWidth = 50 # desired width
    scaledHeight = 56 # made this a class attribute to access in Platform class
                      # without having to make an instance
    
    # following function derived from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
    def getSprites(self, spritesheet, spriteY0, spriteY1):
        # get sprites from one spritesheet
        spritesInDir = [ ]
        for i in range(6):
            spriteWidth = 100 # based on image
            spriteSheetMargin = 0 # based on image
            spriteSheetWidth, spriteSheetHeight = spritesheet.size
            sprite = spritesheet.crop((spriteSheetWidth/6*i, 
                                       spriteY0, 
                                       spriteWidth+spriteSheetWidth/6*i, 
                                       spriteY1))
            scaleFactor = Player.scaledWidth / spriteWidth
            sprite = self.app.scaleImage(sprite, scaleFactor)
            spritesInDir.append(sprite)
        return spritesInDir

# one of the players is giant panda
class GiantPanda(Player):
    def __init__(self, name, app):
        self.name = name
        self.app = app
        # following pictures adapted from: https://www.coolmathgames.com/0-double-panda
        spritesheetRight = self.app.loadImage('gpspritesheetright.png')
        spritesheetLeft = self.app.loadImage('gpspritesheetleft.png')
        spriteHeight = 112 # based on image
        self.spritesMoveRight = super().getSprites(spritesheetRight, 0, spriteHeight)
        self.spritesMoveLeft = super().getSprites(spritesheetLeft, 0, spriteHeight)
        self.currSpritesInDir = self.spritesMoveRight
        self.spriteCounter = 2

        # starting position
        self.startingX = 250
        self.x = self.startingX
        self.y = 475 # y is anchored south in view

        # corners of body
        self.x0 = self.x - self.scaledWidth / 2
        self.x1 = self.x + self.scaledWidth / 2
        self.y0 = self.y
        self.y1 = self.y - self.scaledHeight

        self.isFalling = False
        self.livesLeft = 5
        self.platformUnder = None

        self.canKill = True
    
    def __eq__(self, other):
        return (isinstance(other, GiantPanda) and (self.name == other.name))

# the other player is red panda
class RedPanda(Player):
    def __init__(self, name, app):
        self.name = name
        self.app = app
        # following pictures adapted from: https://www.coolmathgames.com/0-double-panda
        spritesheetRight = self.app.loadImage('rpspritesheetRight.png')
        spritesheetLeft = self.app.loadImage('rpspritesheetLeft.png')
        spriteHeight = 112 # based on image
        self.spritesMoveRight = super().getSprites(spritesheetRight, 0, spriteHeight)
        self.spritesMoveLeft = super().getSprites(spritesheetLeft, 0, spriteHeight)
        self.currSpritesInDir = self.spritesMoveRight
        self.spriteCounter = 2

        # starting position
        self.startingX = 180 # default otherPlayer is set back from currPlayer
        self.x = self.startingX
        self.y = 475 # y is anchored south in view

        # corners of body
        self.x0 = self.x - self.scaledWidth / 2
        self.x1 = self.x + self.scaledWidth / 2
        self.y0 = self.y
        self.y1 = self.y - self.scaledHeight

        self.isFalling = False
        self.livesLeft = 5
        self.platformUnder = None
    
    def __eq__(self, other):
        return (isinstance(other, RedPanda) and (self.name == other.name))

# enemies cause players to lose lives when they collide or get attacked
# two types of Enemy: BasicEnemy and ArcherEnemy
class Enemy(object):
    scaledWidth = 50 # desired width
    scaledHeight = 60

    def __init__(self, platform, app):
        self.app = app
        self.platform = platform
        self.maxLeft = platform.x0 + Enemy.scaledWidth / 2
        self.maxRight = platform.x1 - Enemy.scaledWidth / 2

        # starting position
        self.x = random.randint(self.maxLeft, self.maxRight)
        self.y = app.floorLevel - platform.height
        self.collidingWithPlayers = False

        # corners of body
        self.x0 = self.x - self.scaledWidth / 2
        self.x1 = self.x + self.scaledWidth / 2
        self.y0 = self.y
        self.y1 = self.y - self.scaledHeight

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
            scaleFactor = Enemy.scaledWidth / spriteWidth
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

        # note: will have different picture later
        # following picture from https://i.pinimg.com/originals/7d/59/5a/7d595a64c99a634d94759de8096cca14.png
        spritesheet = self.app.loadImage('basicenemysprites.png')
        spriteHeight = 420 # based on image at url
        self.spritesMoveRight = self.getSprites(spritesheet, 1900, 1900 + spriteHeight)
        self.spritesMoveLeft = self.getSprites(spritesheet, 1300, 1300 + spriteHeight)
        self.currSpritesInDir = self.spritesMoveRight
        self.spriteCounter = 1
        self.scoreGain = 250
        self.dx = 5

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

        # note: will have different picture later
        # following picture from https://i.pinimg.com/originals/7d/59/5a/7d595a64c99a634d94759de8096cca14.png
        spritesheet = self.app.loadImage('archerenemysprites.png')
        spriteHeight = 420 # based on image at url
        self.spritesMoveRight = self.getSprites(spritesheet, 1900, 1900 + spriteHeight)
        self.spritesMoveLeft = self.getSprites(spritesheet, 1300, 1300 + spriteHeight)
        self.currSpritesInDir = self.spritesMoveRight
        self.tempShootingSprite = None
        self.spriteCounter = 1
        self.scoreGain = 300
        self.dx = 5

        self.weapon = Weapon(self.x, self.y - (self.scaledHeight // 2), self.app)
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
        self.weapon.reset(self.x, self.y - (self.scaledHeight // 2))

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