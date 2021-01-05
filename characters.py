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
#from terrain import *
# following framework from cmu_112_graphics
from cmu_112_graphics import *

# players that the user controls
# two types of Player: GiantPanda and RedPanda
class Player(object):
    width = 50
    height = 56 # made this a class attribute to access in Platform
                # class without having to make an instance
    maxX = 0

    def __init__(self, app):
        self.app = app
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
        self.jumpSpeed = 7 # cannot be too small, will cross 0
        self.fallSpeed = 0
        self.jumpStartingHeight = self.y

        self.spriteCounter = 3
        self.spriteStanding = 3

        self.livesLeft = 5
        self.platformUnderneath = None
        self.enemyUnderneath = None
    
    ####################################
    # Movement methods
    ####################################
    
    # returns True if Player is on a platform or otherPlayer head
    # used to check whether to fall off platform while walking
    # helper for step()
    def checkIfOnPlatform(self, platforms, otherPlayer):
        # check if Player is on a platform
        for platform in platforms:
            if (platform.x0 <= self.x <= platform.x1 and
                self.y == self.app.floorLevel - platform.height):
                return True

        # check if Player is on otherPlayer's head
        if (self.y == otherPlayer.y1):
            if (otherPlayer.x0 <= self.x0 <= otherPlayer.x1 or 
                otherPlayer.x0 <= self.x1 <= otherPlayer.x1):
                return True
        
        return False
    
    # increment x coordinate while walking
    def step(self, walkSpeed, platforms, otherPlayer):
        # going to next sprite image is taken care of in child class step()

        # update currPlayer's position
        if (self.x - (self.width / 2) + walkSpeed > 0):
            # cannot walk to the left of the starting position
            self.x += walkSpeed
            self.x0 += walkSpeed
            self.x1 += walkSpeed
            if (self.x > Player.maxX): # update maxX
                Player.maxX = self.x

        # get the correct sprite image list
        if (walkSpeed < 0): # moving left
            self.spritesCurrDir = self.spritesLeft
        elif (walkSpeed > 0): # moving right
            self.spritesCurrDir = self.spritesRight

        # check if walking off the edge
        if (self.y != self.app.floorLevel):
            # if the currPlayer is not on a platform
            self.isFalling = not self.checkIfOnPlatform(platforms, otherPlayer)
    
    # increment y coordinate up during the jump
    def jump(self):
        if (self.reachedTopOfJump == False): 
            # jump up
            if (self.y > self.jumpStartingHeight - self.jumpHeight): 
                # has not reached top of jump
                # following formula is derived from: https://www.techwithtim.net/tutorials/game-development-with-python/pygame-tutorial/jumping/
                dy = 0.6 * (self.jumpSpeed ** 2) # parabolic jumping
                # print('jump', self.y, dy, self.jumpSpeed)
                self.y -= dy
                self.y0 -= dy
                self.y1 -= dy
                self.jumpSpeed -= 1
            else:
                # reached top of jump
                self.reachedTopOfJump = True
                self.y = self.jumpStartingHeight - self.jumpHeight
        else: 
            # start to fall back down
            self.isJumping = False
            self.fallSpeed = self.jumpSpeed + 1
            self.jumpSpeed = 7 # reset
            self.isFalling = True
            self.reachedTopOfJump = False
    
    # increment y coordinate down during fall
    def fall(self, goalHeight):
        # following formula is derived from: https://www.techwithtim.net/tutorials/game-development-with-python/pygame-tutorial/jumping/
        dy = 0.5 * (self.fallSpeed ** 2) # parabolic jumping
        if (abs(self.y - goalHeight) > dy):
            # has not reached ground
            # print('fall', self.y, dy, self.fallSpeed)
            self.y += dy
            self.y0 += dy
            self.y1 += dy
            self.fallSpeed += 1
        elif (abs(self.y - goalHeight) <= dy): 
            # reached ground
            self.y = self.y0 = goalHeight
            # print('fall', self.y, dy, self.jumpSpeed)
            self.y1 = goalHeight - self.height
            self.isFalling = False
            self.fallSpeed = 0 # reset

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
        
        super().__init__(app)

        # GiantPanda specific ability: killing enemies
        self.canKill = True
        self.enemyUnderneath = None
    
    # wrapper for step function
    def step(self, walkSpeed, platforms, otherPlayer):
        super().step(walkSpeed, platforms, otherPlayer)

        # go to next sprite image
        if (not self.isJumping and not self.isFalling):
            self.spriteCounter = (1 + self.spriteCounter) % len(self.spritesCurrDir)
    
    # wrapper for fall function: giantPanda can kill enemy during fall
    def fall(self, goalHeight, enemies):
        super().fall(goalHeight)
        # when giant panda lands on the enemy, kill it
        if (self.enemyUnderneath != None):
            if self.canKill:
                self.app.score += self.enemyUnderneath.die()
                self.canKill = False
                enemies.remove(self.enemyUnderneath)
                self.enemyUnderneath.platform.enemiesOn.remove(self.enemyUnderneath)
                self.enemyUnderneath = None
                self.isFalling = True
        else:
            # can only kill once per time on enemy's head
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

        super().__init__(app)

        # RedPanda specific ability: climbing
        self.climbSpeed = 10
        self.isClimbingUp = False
        self.isClimbingDown = False
        self.isOnBamboo = False
        self.isJumpingOffBambooRight = False
        self.isJumpingOffBambooLeft = False
        self.currBamboo = None
    
    # wrapper for step function
    def step(self, walkSpeed, platforms, otherPlayer):
        super().step(walkSpeed, platforms, otherPlayer)

        # go to next sprite image
        if (not self.isJumping and not self.isFalling and 
            not self.isJumpingOffBambooRight and
            not self.isJumpingOffBambooLeft):
            self.spriteCounter = (1 + self.spriteCounter) % len(self.spritesCurrDir)

    # wrapper for fall function: redPanda cannot kill enemy during fall
    def fall(self, goalHeight, enemies):
        super().fall(goalHeight)

    # returns True if redPanda is at a bamboo
    def atBamboo(self, bamboos):
        for bamboo in bamboos:
            x0 = bamboo.x - bamboo.width / 2
            x1 = bamboo.x + bamboo.width / 2
            if (x0  <= self.x <= x1):
                return bamboo
        return None
    
    # increment climb up
    def climbUp(self):
        # cannot past top of screen
        if (self.y - self.height - self.climbSpeed > 0):
            self.y -= self.climbSpeed
            self.y0 -= self.climbSpeed
            self.y1 -= self.climbSpeed
                
        # go to next sprite image
        self.spriteCounter = (1 + self.spriteCounter) % len(self.spritesCurrDir)
    
    # increment climb down
    def climbDown(self):
        # cannot climb down past bottom of bamboo
        if (self.currPlayer.y - self.currBamboo.startingHeight + self.climbSpeed <= 0):
            self.y += self.climbSpeed
            self.y0 += self.climbSpeed
            self.y1 += self.climbSpeed
        else: # reached floor
            self.spritesCurrDir = self.spritesRight
            self.isClimbingDown = False 
            self.isOnBamboo = False
            self.currBamboo = None
                
        # go to next sprite image
        self.currPlayer.spriteCounter = (1 + self.currPlayer.spriteCounter) % len(self.currPlayer.spritesCurrDir)
    
    # increment jumping off bamboo left or right
    def jumpOffBamboo(self, walkSpeed):
        # reset values
        self.isClimbingUp = False
        self.isClimbingDown = False
        self.isOnBamboo = False
        self.currBamboo = None

        # increment step
        if (self.x - (self.width / 2) + walkSpeed > 0):
            # cannot walk to the left of the starting position
            self.x += walkSpeed
            self.x0 += walkSpeed
            self.x1 += walkSpeed
            if (self.x > Player.maxX): # update maxX
                self.maxX = self.x

        # get the correct sprite direction list
        if (walkSpeed < 0): # moving left
            self.spritesCurrDir = self.spritesLeft
        elif (walkSpeed > 0): # moving right
            self.spritesCurrDir = self.spritesRight

        # increment jump
        if (self.reachedTopOfJump == False): # jump up
            if (self.y > self.jumpStartingHeight - self.jumpHeight):
                # has not reached top of jump
                # following formula is derived from: https://www.techwithtim.net/tutorials/game-development-with-python/pygame-tutorial/jumping/
                dy = 0.6 * (self.jumpSpeed ** 2) # parabolic jumping
                # print('jump', self.y, dy, self.jumpSpeed)
                self.y -= dy
                self.y0 -= dy
                self.y1 -= dy
                self.jumpSpeed -= 1
            else:
                self.y = self.jumpStartingHeight - self.jumpHeight
                self.fallSpeed = self.jumpSpeed + 1
                self.jumpSpeed = 7 # reset
                self.reachedTopOfJump = True
        else: # reached top of jump
            goalHeight = self.app.findGoalHeight(self)
            # following formula is derived from: https://www.techwithtim.net/tutorials/game-development-with-python/pygame-tutorial/jumping/
            dy = 0.5 * (self.fallSpeed ** 2) # parabolic jumping
            if (abs(self.y - goalHeight) > dy):
                # has not reached ground
                # print('fall', self.y, dy, self.fallSpeed)
                self.y += dy
                self.y0 += dy
                self.y1 += dy
                self.fallSpeed += 1
            elif (abs(self.y - goalHeight) <= dy): # reached ground
                self.y = self.y0 = goalHeight
                # print('fall', self.y, dy, self.jumpSpeed)
                self.y1 = goalHeight - self.height
                self.reachedTopOfJump = False
                self.isJumpingOffBambooRight = False
                self.isJumpingOffBambooLeft = False
                self.fallSpeed = 0 # reset
                return

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

    # increment step / update position
    def autoStepEnemy(self):
        if (self.spritesCurrDir == self.spritesRight):
            newX = self.x + self.walkSpeed
            newX0 = self.x0 + self.walkSpeed
            newX1 = self.x1 + self.walkSpeed
        elif (self.spritesCurrDir == self.spritesLeft):
            newX = self.x - self.walkSpeed
            newX0 = self.x0 - self.walkSpeed
            newX1 = self.x1 - self.walkSpeed
        
        if (newX < self.maxLeft): 
            # too far off left
            self.spritesCurrDir = self.spritesRight
            self.x = self.maxLeft
        elif (newX > self.maxRight): 
            # too far off right
            self.spritesCurrDir = self.spritesLeft
            self.x = self.maxRight
        else:
            self.x = newX
            self.x0 = newX0
            self.x1 = newX1

        # go to next sprite image
        self.spriteCounter = (1 + self.spriteCounter) % len(self.spritesCurrDir)

    # when the GiantPanda kills the enemy, it gains points from the enemy
    def die(self):
        return self.scoreGain

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

    # increment step / update position
    # BasicEnemy can walk towards player if it is on the same platform
    # and the score is high
    def autoStepEnemy(self):
        if (self.app.score >= 10000):
            for player in [self.app.currPlayer, self.app.otherPlayer]:
                if (self.y0 > player.y >= self.y1 and
                    (self.platform.x0 <= player.x0 < self.platform.x1 or
                     self.platform.x0 < player.x1 <= self.platform.x1)):
                    # close enough to player
                    if (player.x + player.width < self.x):
                        self.spritesCurrDir = self.spritesLeft
                        continue
                    elif (player.x - player.width > self.x):
                        self.spritesCurrDir = self.spritesRight
                        continue
        
        super().autoStepEnemy()

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

    # returns the player that is close enough to shoot at or None otherwise
    def closeEnoughToShoot(self):
        # enemy should be at or above the target player
        if (0 < abs(self.x - self.app.currPlayer.x) < 200 and
            self.y <= self.app.currPlayer.y):
            return self.app.currPlayer
        elif (0 < abs(self.x - self.app.otherPlayer.x) < 200 and
            self.y <= self.app.otherPlayer.y):
            return self.app.otherPlayer
        return None

    # predict where to shoot
    def predictTarget(self, targetPlayer):
        # stepping does not change weapon's position, so reset it here
        self.weapon.x = self.x

        if (self.app.score <= 10000):
            targetX = targetPlayer.x
            targetY = targetPlayer.y - targetPlayer.height // 2
            self.weapon.shootingCalculations(targetX, targetY, targetPlayer)
        else:
            # speed of weapon increases
            self.weapon.v *= 1.01
            
            # targetX changes based on direction of currPlayer
            if (self.currPlayer.isWalkingLeft):
                if (self.shootCount == 0):
                    targetX = targetPlayer.x
                elif (self.shootCount == 1):
                    targetX = targetPlayer.x - 150
                elif (self.shootCount == 2):
                    targetX = targetPlayer.x - 300
            elif (self.currPlayer.isWalkingRight):
                if (self.shootCount == 0):
                    targetX = targetPlayer.x
                elif (self.shootCount == 1):
                    targetX = targetPlayer.x + 150
                elif (self.shootCount == 2):
                    targetX = targetPlayer.x + 300
            else:
                targetX = targetPlayer.x

        targetY = targetPlayer.y - targetPlayer.height // 2
        self.weapon.shootingCalculations(targetX, targetY, targetPlayer)

        if (targetX < self.x):
            self.tempShootingSprite = self.spritesLeft[0]
        elif (targetX > self.x):
            self.tempShootingSprite = self.spritesRight[0]
        else:
            self.tempShootingSprite = self.spritesCurrDir[self.spriteCounter]

    # increment the weapon's position
    def incrementShooting(self):
        weapon = self.weapon
        newX = weapon.x + weapon.dx
        newY = weapon.y + weapon.dy

        if (weapon.y > self.app.floorLevel): 
            # passed through floor
            self.resetWeapon()
            self.shootCount += 1
        elif (abs(weapon.x - self.x) > 400):
            # passed distance of 400 (went too far)
            self.resetWeapon()
            self.shootCount += 1
        elif (weapon.targetPlayer.x0 <= newX <= weapon.targetPlayer.x1 and
              weapon.targetPlayer.y0 >= newY >= weapon.targetPlayer.y1):
            # hit target
            weapon.targetPlayer.livesLeft -= 1
            self.resetWeapon()
            self.shootCount += 1
        else:
            # increment position
            weapon.x = newX
            weapon.y = newY

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