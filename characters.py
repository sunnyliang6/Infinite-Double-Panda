####################################
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

import random, os, math
import pygame as pg
from settings import *
vec = pg.math.Vector2

# user controls Players
class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        self.pos = vec(0, floorLevel)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        # movement booleans
        self.isRunning = False
        self.isInAir = False

        self.livesLeft = livesLeft
        self.platformUnderneath = None
        self.enemyUnderneath = None
    
    # updates x direction
    def updateX(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            if self.pos.x - playerWidth / 2 > edgeLimit:
                self.acc.x = -playerAcc
            else: # cannot go farther than the edgeLimit
                self.vel.x = 0
                self.acc.x = 0
        if keys[pg.K_RIGHT]:
            self.acc.x = playerAcc
        
        # apply friction to control maximum speed and inertia
        self.acc.x += self.vel.x * playerFriction

        if self.pos.x > self.game.playerMaxX:
            self.game.playerMaxX = self.pos.x

        if abs(self.vel.x) > 0.3:
            self.isRunning = True
        else:
            self.isRunning = False

    # returns lowest platform top to land on or -1 if none available
    def checkIfOnPlatform(self):
        lowest = -1
        for plat in self.game.platforms:
            if (plat.rect.left < self.rect.left + playerFeetX < plat.rect.right or
                plat.rect.left < self.rect.right - playerFeetX < plat.rect.right):
                if plat.rect.bottom >= self.rect.bottom >= plat.rect.top:
                    if plat.rect.top > lowest:
                        lowest = plat.rect.top
        return lowest
    
    # returns otherPlayer top to land on, otherwise returns -1
    def checkIfOnOtherPlayer(self, collisionSetOff):
        if self.name == self.game.currPlayer.name:
            other = self.game.otherPlayer
        else:
            other = self.game.currPlayer
        if (self.rect.left < other.rect.left + playerFeetX < self.rect.right or 
            self.rect.left < other.rect.right - playerFeetX < self.rect.right):
            if 0 < self.rect.bottom - other.rect.top <= collisionSetOff:
                return other.rect.top
        return -1

    # returns floorLevel to jump on, otherwise returns -1
    def checkIfOnFloor(self):
        if self.rect.bottom >= floorLevel:
            return floorLevel
        return -1

    # returns Enemy top to land on, otherwise returns -1
    def checkIfOnEnemy(self, collisionSetOff):
        for enemy in self.game.enemies:
            if (self.rect.left < enemy.rect.left + playerFeetX < self.rect.right or 
                self.rect.left < enemy.rect.right - playerFeetX < self.rect.right):
                if 0 < self.rect.bottom - enemy.rect.top <= collisionSetOff:
                    return (enemy, enemy.rect.top)
        return (None, -1)

    # updates y direction
    def updateY(self):
        # stop falling only if Player is on a platform or floor
        if self.vel.y > 0:
            # land on platform, otherPlayer's head, floor, or enemy's head
            self.rect.y += playerCollisionSetOff
            platCollision = self.checkIfOnPlatform()
            otherPlayerCollision = self.checkIfOnOtherPlayer(playerCollisionSetOff)
            floorCollision = self.checkIfOnFloor()
            (enemy, enemyCollision) = self.checkIfOnEnemy(playerCollisionSetOff)
            self.rect.y -= playerCollisionSetOff

            # stop falling if Player is on a platform or floor
            newPosY = max(platCollision, otherPlayerCollision, floorCollision, enemyCollision)
            if newPosY != -1:
                self.pos.y = newPosY
                self.vel.y = 0
            if newPosY == enemyCollision and enemy != None and self.name == 'Giant Panda':
                self.game.score += enemy.die()
                self.game.enemies.remove(enemy)

        if self.vel.y == 0:
            self.isInAir = False
        else:
            self.isInAir = True
    
    # updates current image of sprite
    def updateImage(self):
        # set direction of sprites
        if self.vel.x > 0:
            self.spritesCurrDir = self.spritesRight
        elif self.vel.x < 0:
            self.spritesCurrDir = self.spritesLeft

        # change sprite counter if not standing or in air
        if self.isRunning and not self.isInAir:
            # self.spriteCounter = (1 + self.spriteCounter) % len(self.spritesCurrDir)
            self.spriteCounter = (1 + self.spriteCounter) % (playerRepeatSprite * playerNumSprites)
            spriteNum = self.spriteCounter // playerRepeatSprite
        else:
            spriteNum = self.spriteStanding
            self.spriteCounter = spriteNum * playerRepeatSprite
        self.image = self.spritesCurrDir[spriteNum]

    # updates movement
    # physics in following function derived from: https://youtu.be/8LRI0RLKyt0
    def update(self):
        self.acc = vec(0, playerGravity) # implement gravity
        if self.game.currPlayer.name == self.name:
            self.updateX()
        # kinematic equations
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        # self.rect.midbottom = self.pos
        self.updateY()
        self.rect.midbottom = self.pos
        if self.game.currPlayer.name == self.name:
            self.checkCandyCollisions()
        self.updateImage()

    # sets velocity in both directions and x acceleration to 0
    def stop(self):
        self.vel.x = 0
        self.vel.y = 0
        self.acc = vec(0, playerGravity)
        self.isRunning = False
        self.isInAir = False

    # sets upward velocity for jump
    def jump(self):
        # jump only if Player is standing on a platform, otherPlayer's head, floor, or enemy's head
        # following 'algorithm' derived from: https://youtu.be/9S7fWevICtY
        self.rect.y += 1
        platCollision = self.checkIfOnPlatform()
        otherPlayerCollision = self.checkIfOnOtherPlayer(1)
        floorCollision = self.checkIfOnFloor()
        enemyCollision = -1
        if self.name == 'Red Panda':
            # RedPanda can jump while on an Enemy
            (enemy, enemyCollision) = self.checkIfOnEnemy(1)
        self.rect.y -= 1
        if (platCollision != -1 or 
            otherPlayerCollision != -1 or 
            floorCollision != -1 or
            enemyCollision != -1):
            self.vel.y = -playerJumpVel

    # checks for collision with candy and eat it if there is 
    def checkCandyCollisions(self):
        for candy in self.game.candies:
            collision = pg.sprite.collide_rect(candy, self)
            if collision:
                if (candy.candyType == 'Fried Rice' and 
                    self.name == self.game.giantPanda.name):
                    # only RedPanda can eat fried rice
                    continue
                self.game.score += candy.scoreGain
                self.game.candies.remove(candy)

    # draws with appropriate shift
    def draw(self):
        self.game.screen.blit(self.image, (self.rect.x - self.game.scrollX, self.rect.y))

# GiantPanda is a Player that the user can control and has the unique ability
# of killing Enemies
class GiantPanda(Player):
    def __init__(self, name, game):
        super().__init__(game)
        self.name = name
        self.getSpriteImages()
        self.image = self.spritesCurrDir[self.spriteStanding]
        self.rect = self.image.get_rect()

        # starting position
        self.rect.centerx = self.pos.x = gpStartingX
        self.rect.bottom = self.pos.y = floorLevel

        # GiantPanda specific ability: killing enemies
        self.canKill = True
        self.enemyUnderneath = None
    
    # gets images of GiantPanda
    def getSpriteImages(self):
        self.spriteCounter = 3
        self.spriteStanding = 3
        # following images captured from: https://www.coolmathgames.com/0-double-panda
        self.spritesRight = [pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-rspr1.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-rspr2.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-rspr3.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-rspr4.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-rspr5.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-rspr6.png')).convert()]
        self.spritesLeft =  [pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-lspr1.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-lspr2.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-lspr3.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-lspr4.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-lspr5.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'gp', 'gp-lspr6.png')).convert()]
        self.spritesCurrDir = self.spritesRight

# RedPanda is a Player that the user can control and has the unique ability of
# climbing bamboo
class RedPanda(Player):
    def __init__(self, name, game):
        super().__init__(game)
        self.name = name
        self.getSpriteImages()
        self.image = self.spritesCurrDir[self.spriteStanding]
        self.rect = self.image.get_rect()

        # starting position
        self.rect.centerx = self.pos.x = rpStartingX
        self.rect.bottom = self.pos.y = floorLevel

        # RedPanda specific ability: climbing
        self.climbSpeed = 10
        self.isClimbingUp = False
        self.isClimbingDown = False
        self.isAtBamboo = False

        self.isOnBamboo = False
        self.isInAirOffBambooRight = False
        self.isInAirOffBambooLeft = False
        self.currBamboo = None

    # gets images of RedPanda
    def getSpriteImages(self):
        self.spriteCounter = 3
        self.spriteStanding = 3
        # following images captured from: https://www.coolmathgames.com/0-double-panda
        self.spritesRight = [pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-rspr1.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-rspr2.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-rspr3.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-rspr4.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-rspr5.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-rspr6.png')).convert()]
        self.spritesLeft =  [pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-lspr1.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-lspr2.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-lspr3.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-lspr4.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-lspr5.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'rp', 'rp-lspr6.png')).convert()]
        self.spritesCurrDir = self.spritesRight
        self.image = self.spritesCurrDir[self.spriteStanding]

    # calls super class update() if not climbing
    def update(self):
        if not self.isAtBamboo:
            super().update()
        else:
            self.climb()

    # returns True if at a bamboo
    def atBamboo(self):
        for bamboo in self.game.bamboos:
            if (bamboo.rect.left <= self.rect.centerx <= bamboo.rect.right):
                self.isAtBamboo = True
                return True
        self.isAtBamboo = False
        return False

    # updates position while climbing up or down or jumping off a bamboo
    def climb(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            if self.rect.top - playerClimbVel > edgeLimit:
                self.rect.y -= playerClimbVel
        if keys[pg.K_DOWN]:
            if self.rect.bottom + playerClimbVel <= floorLevel:
                self.rect.y += playerClimbVel
            else: # reached floor
                self.rect.bottom = floorLevel
                self.isAtBamboo = False
        self.pos.y = self.rect.bottom
        self.vel.x = 0
        if keys[pg.K_LEFT] or keys[pg.K_RIGHT]:
            self.isAtBamboo = False
            self.vel.y = -playerJumpVel
            self.acc = vec(0, playerGravity)
            self.updateX()
            # kinematic equations
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc
            self.rect.midbottom = self.pos

# Enemy are controlled by the game and causes Player's to lose lives
class Enemy(pg.sprite.Sprite):
    def __init__(self, game, platform):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        self.pos = vec(0, floorLevel)
        self.vel = vec(enemyWalkVel, 0)

        # Enemy is on a platform
        self.platform = platform
        self.maxLeft = platform.rect.left + enemyWidth / 2
        self.maxRight = platform.rect.right - enemyWidth / 2

        # starting position
        self.pos.x = random.randint(self.maxLeft, self.maxRight)
        self.pos.y = platform.rect.top

        self.collidingWithGP = False
        self.collidingWithRP = False

    # increments step / updates position
    def autoStep(self):
        self.pos.x += self.vel.x

        if self.pos.x < self.maxLeft: 
            # too far off left
            self.spritesCurrDir = self.spritesRight
            self.pos.x = self.maxLeft
            self.vel.x = +enemyWalkVel
        elif self.pos.x > self.maxRight: 
            # too far off right
            self.spritesCurrDir = self.spritesLeft
            self.pos.x = self.maxRight
            self.vel.x = -enemyWalkVel
        
        self.rect.centerx = self.pos.x

    # check if Enemy is colliding with Players
    def checkPlayerCollisions(self):
        for player in [self.game.currPlayer, self.game.otherPlayer]:
            # cannot lose life from jumping on enemy head
            if not (player.rect.bottom == self.rect.top): 
                # check for collision
                player.rect.left += playerFeetX
                player.rect.right -= playerFeetX
                collision = pg.sprite.collide_rect(self, player)
                player.rect.left -= playerFeetX
                player.rect.right += playerFeetX
                if collision:
                    if (player.name == 'Giant Panda'):
                        self.collidingWithGP = True
                    if (player.name == 'Red Panda'):
                        self.collidingWithRP = True
                else: # finish colliding
                    if (self.collidingWithGP and player.name == 'Giant Panda'):
                        self.collidingWithGP = False
                        player.livesLeft -= 1
                    if (self.collidingWithRP and player.name == 'Red Panda'):
                        self.collidingWithRP = False
                        player.livesLeft -= 1

    # when the GiantPanda kills the Enemy, it gains points from the Enemy
    def die(self):
        return self.scoreGain

    # draws with appropriate shift
    def draw(self):
        self.game.screen.blit(self.image, (self.rect.x - self.game.scrollX, self.rect.y))

# BasicEnemy is an Enemy that wanders a platform
class BasicEnemy(Enemy):
    def __init__(self, game, platform):
        super().__init__(game, platform)
        self.name = 'Basic Enemy'
        self.scoreGain = 250

        self.getSpriteImages()
        self.image = self.spritesCurrDir[self.spriteStanding]
        self.rect = self.image.get_rect()

        # starting position
        self.rect.centerx = self.pos.x
        self.rect.bottom = self.pos.y

    # gets images of BasicEnemy
    def getSpriteImages(self):
        self.spriteCounter = 3
        self.spriteStanding = 3
        # following images captured from: https://www.coolmathgames.com/0-double-panda
        self.spritesRight = [pg.image.load(os.path.join(imagesFolder, 'be', 'be-rspr1.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'be', 'be-rspr2.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'be', 'be-rspr3.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'be', 'be-rspr4.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'be', 'be-rspr5.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'be', 'be-rspr6.png')).convert()]
        self.spritesLeft =  [pg.image.load(os.path.join(imagesFolder, 'be', 'be-lspr1.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'be', 'be-lspr2.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'be', 'be-lspr3.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'be', 'be-lspr4.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'be', 'be-lspr5.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'be', 'be-lspr6.png')).convert()]
        self.spritesCurrDir = self.spritesRight

    # increments step / updates position
    # BasicEnemy can walk towards player if it is on the same platform
    # and the score is high (>= 10k)
    def autoStep(self):
        if (self.game.score >= 10000):
            for player in [self.game.currPlayer, self.game.otherPlayer]:
                if (self.rect.top < player.rect.bottom <= self.rect.bottom and
                    (self.platform.rect.left <= player.rect.left < self.platform.rect.right or
                     self.platform.rect.left < player.rect.right <= self.platform.rect.left)):
                    # close enough to player
                    if (player.rect.centerx + playerWidth < self.rect.centerx):
                        self.vel.x = -enemyWalkVel
                        continue
                    elif (player.rect.centerx - playerWidth > self.rect.centerx):
                        self.vel.x = +enemyWalkVel
                        continue
        
        super().autoStep()

    # updates current image of sprite
    def updateImage(self):
        # set direction of sprites
        if self.vel.x > 0:
            self.spritesCurrDir = self.spritesRight
        elif self.vel.x < 0:
            self.spritesCurrDir = self.spritesLeft

        # change sprite counter if not standing or shooting
        if self.vel.x != 0:
            self.spriteCounter = (1 + self.spriteCounter) % (enemyRepeatSprite * enemyNumSprites)
            spriteNum = self.spriteCounter // enemyRepeatSprite
        else:
            spriteNum = self.spriteStanding
            self.spriteCounter = spriteNum * enemyRepeatSprite
        self.image = self.spritesCurrDir[spriteNum]

    def update(self):
        self.autoStep()
        self.updateImage()
        self.checkPlayerCollisions()

# ArcherEnemy is an Enemy that wanders a platform and shoots at Players
class ArcherEnemy(Enemy):
    def __init__(self, game, platform):
        super().__init__(game, platform)
        self.name = 'Archer Enemy'
        self.scoreGain = 300

        self.getSpriteImages()
        self.image = self.spritesCurrDir[self.spriteStanding]
        self.rect = self.image.get_rect()

        # starting position
        self.rect.centerx = self.pos.x
        self.rect.bottom = self.pos.y

        # ArcherEnemy specific ability: shooting
        self.weapon = Weapon(game, self)
        self.isShooting = False
        self.shootCount = 0 # can only shoot 3 times at once every 3 seconds
        self.shootingStartWaitTime = 0

    # gets images of ArcherEnemy
    def getSpriteImages(self):
        self.spriteCounter = 3
        self.spriteStanding = 3
        # following images captured from: https://www.coolmathgames.com/0-double-panda
        self.spritesRight = [pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-rspr1.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-rspr2.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-rspr3.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-rspr4.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-rspr5.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-rspr6.png')).convert()]
        self.spritesLeft =  [pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-lspr1.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-lspr2.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-lspr3.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-lspr4.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-lspr5.png')).convert(),
                             pg.image.load(os.path.join(imagesFolder, 'ae', 'ae-lspr6.png')).convert()]
        self.spritesCurrDir = self.spritesRight

    def autoStep(self):
        if not self.isShooting:
            super().autoStep()

    # returns the Player that is close enough to shoot at or None otherwise
    def checkCloseEnoughToShoot(self):
        # enemy should be at or above the target player
        if (0 < abs(self.rect.centerx - self.game.currPlayer.rect.centerx) < 200 and
            self.rect.centery <= self.game.currPlayer.rect.centery):
            return self.game.currPlayer
        elif (0 < abs(self.rect.centerx - self.game.otherPlayer.rect.centerx) < 200 and
            self.rect.centery <= self.game.otherPlayer.rect.centery):
            return self.game.otherPlayer
        return None

    # predicts where to shoot
    def predictTarget(self, targetPlayer):
        if (self.game.score <= 10000):
            targetX = targetPlayer.rect.centerx
            targetY = targetPlayer.rect.centery
        else: # enemy shooting AI
            # speed of weapon increases
            self.weapon.v *= 1.01
            targetY = targetPlayer.rect.centery
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

        self.weapon.shootingCalculations(targetX, targetY, targetPlayer)

    # resets the Weapon and reset boolean
    def resetWeapon(self):
        self.isShooting = False
        self.weapon.reset()

    # handles whether ArcherEnemy can shoot 
    def checkShooting(self):
        if self.shootCount > 2:
            # already shot 3 (maximum) times
            self.isShooting = False
            currTime = pg.time.get_ticks()
            if self.shootingStartWaitTime == 0:
                # start waiting before it can shoot again
                self.shootingStartWaitTime = currTime
            elif currTime - self.shootingStartWaitTime > enemyShootWaitTime:
                # reset variables to be able to shoot again
                self.shootCount = 0
                self.shootingStartWaitTime = 0
        else:
            # has not shot maximum times yet
            result = self.checkCloseEnoughToShoot()
            if result != None:
                # close enough to shoot, start shooting
                self.isShooting = True
                self.weapon.setPos(self.rect.centerx, self.rect.centery)
                self.predictTarget(result)
                self.weapon.update()
            else:
                self.isShooting = False
                self.shootCount = 0
                self.resetWeapon()

    # updates current image of sprite
    def updateImage(self):
        # set direction of sprites
        if self.isShooting:
            # face target while shooting
            if self.weapon.targetPlayer.pos.x < self.pos.x:
                self.spritesCurrDir = self.spritesLeft
            elif self.weapon.targetPlayer.pos.x > self.pos.x:
                self.spritesCurrDir = self.spritesRight
        else:
            if self.vel.x > 0:
                self.spritesCurrDir = self.spritesRight
            elif self.vel.x < 0:
                self.spritesCurrDir = self.spritesLeft

        # change sprite counter if not standing or shooting
        if self.vel.x != 0 and not self.isShooting:
            self.spriteCounter = (1 + self.spriteCounter) % (enemyRepeatSprite * enemyNumSprites)
            spriteNum = self.spriteCounter // enemyRepeatSprite
        else:
            spriteNum = self.spriteStanding
            self.spriteCounter = spriteNum * enemyRepeatSprite
        self.image = self.spritesCurrDir[spriteNum]

    def update(self):
        if self.isShooting and self.weapon.pos.x != 0 and self.weapon.pos.y != 0:
            self.weapon.update()
        else:
            self.checkShooting()
        self.autoStep()
        self.updateImage()
        self.checkPlayerCollisions()

    # draws ArcherEnemy and weapon with appropriate shift
    def draw(self):
        self.game.screen.blit(self.image, (self.rect.x - self.game.scrollX, self.rect.y))
        if self.isShooting or 0 < self.shootCount <= 2:
            self.weapon.draw()

# carried by ArcherEnemy and deals damage to Players
class Weapon(pg.sprite.Sprite):
    def __init__(self, game, enemy):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        self.image = pg.Surface((10, 10))
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

        self.pos = vec(0, 0)
        self.vel = vec(0, 0)
        self.enemy = enemy

        # target position
        self.targetX = 0
        self.targetY = 0
        self.targetPlayer = None

    # determines the dx and dy needed to increment the Weapon towards the target
    def shootingCalculations(self, targetX, targetY, player):
        self.targetX = targetX
        self.targetY = targetY
        self.targetPlayer = player
        distX = self.targetX - self.rect.centerx
        distY = self.targetY - self.rect.centery
        distance = ((distX) ** 2 + (distY) ** 2) ** 0.5
        if (distance > 0):
            angle = math.acos(distX / distance)
        self.vel.x = enemyShootVel * math.cos(angle)
        self.vel.y = enemyShootVel * math.sin(angle)

    # sets current position to given parameters
    def setPos(self, x, y):
        self.pos.x = self.rect.centerx = x
        self.pos.y = self.rect.centery = y

    # resets position to default
    def reset(self):
        self.setPos(0, 0)
        self.vel.x = 0
        self.vel.y = 0

    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        if self.pos.y > floorLevel:
            # passed through floor
            self.reset()
            self.enemy.shootCount += 1
        elif abs(self.pos.x - self.enemy.pos.x) > 400:
            # passed distance of 400 (went too far)
            self.reset()
            self.enemy.shootCount += 1
        else:
            # collided with targetPlayer
            collision = pg.sprite.collide_rect(self, self.targetPlayer)
            if collision:
                self.targetPlayer.livesLeft -= 1
                self.reset()
                self.enemy.shootCount += 1

        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y

    # draws with appropriate shift
    def draw(self):
        self.game.screen.blit(self.image, (self.rect.x - self.game.scrollX, self.rect.y))
