####################################
# 15-112 Term Project
# Name: Sunny Liang
# This game is based on the original Double Panda game: 
# https://www.coolmathgames.com/0-double-panda
####################################

####################################
# Run this file to run the project.
# This file contains the main app that controls player movements, terrain
# generation based on rules, etc. 
# This file also contains different modes of the app (splash screen
# and instructions screen).
####################################

import math, random, copy, time
from characters import *
from terrain import *
# following framework from cmu_112_graphics
from cmu_112_graphics import *

# following mode derived from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#subclassingModalApp
class SplashScreenMode(Mode):
    def appStarted(self):
        # background contains images from the original Double Panda game:
        # https://www.coolmathgames.com/0-double-panda
        self.background = self.loadImage('introbackground.png')

    def redrawAll(self, canvas):
        canvas.create_image(self.width/2, self.height/2, image=ImageTk.PhotoImage(self.background))
        
    def keyPressed(self, event):
        self.app.setActiveMode(self.app.helpMode)

# the name of the following mode derived from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#subclassingModalApp
class GameMode(Mode):
    def appStarted(self):
        # initialize the two players
        self.giantPanda = GiantPanda('Giant Panda', self)
        self.redPanda = RedPanda('Red Panda', self)

        # default direction current player is giantPanda
        self.currPlayer = self.giantPanda
        self.otherPlayer = self.redPanda

        # starting floor level for players
        self.floorLevel = 475
        self.giantPanda.y = self.floorLevel
        self.redPanda.y = self.floorLevel
        self.maxCurrPlayerX = self.currPlayer.x
        self.enemyUnderCurrPlayer = None

        # does not change for either current character
        self.scrollX = 0
        self.dx = 10
        self.dirKeysPressed = set()

        # for walking
        self.currPlayerIsWalkingRight = False
        self.currPlayerIsWalkingLeft = False
        # note: isFalling is defined in GiantPanda and RedPanda

        # for jumping
        self.jumpHeightConstant = 20
        self.jumpHeight = Player.scaledHeight + self.jumpHeightConstant
        self.jumpSpeed = 15
        self.jumpStartingHeight = self.floorLevel
        self.currPlayerIsJumping = False
        self.currPlayerReachedTopOfJump = False
        self.jumpsPerPress = 0

        # for climbing
        self.climbSpeed = 10
        self.currPlayerIsClimbingUp = False
        self.currPlayerIsClimbingDown = False
        self.currPlayerIsOnBamboo = False
        self.currPlayerIsJumpingOffBambooRight = False
        self.currPlayerIsJumpingOffBambooLeft = False

        # for switching between players
        self.scrollSpeedWhenSwitching = 10
        self.isSwitching = False
        self.otherPlayerIsOnCurr = False

        # timer delays
        self.defaultTimerDelay = 50
        self.timerDelayDuringSwitching = 5
        self.timerDelay = self.defaultTimerDelay

        # background
        # background and floor images are from the original Double Panda game:
        # https://www.coolmathgames.com/0-double-panda
        self.background = self.loadImage('gamebackground.png')
        self.floor = self.loadImage('floor.png')

        # platforms
        self.platforms = []
        platform1 = Platform(1, 600, 900, self)
        platform2 = Platform(2.5, 500, 925, self)
        platform3 = Platform(3.5, 675, 1025, self)
        platform4 = Platform(1, 1150, 1450, self)
        self.platforms.extend([platform1, platform2, platform3, platform4])

        # candies
        self.score = 0
        self.candies = []
        candy1 = Candy(650, self.floorLevel - platform1.height, self)
        candy2 = Candy(750, self.floorLevel - platform3.height, self)
        candy3 = Candy(800, self.floorLevel - platform3.height, self)
        candy4 = Candy(850, self.floorLevel - platform3.height, self)
        candy5 = Candy(1300, self.floorLevel - platform4.height, self)
        self.candies.extend([candy1, candy2, candy3, candy4, candy5])

        # bamboos
        self.bamboos = []
        bamboo1 = Bamboo(1100, self.floorLevel, self)
        self.bamboos.append(bamboo1)
        self.currBamboo = None

        # enemies
        self.enemies = []
        enemy1 = ArcherEnemy(platform4, self)
        self.enemies.append(enemy1)
        platform4.addEnemy(enemy1)
        enemy2 = BasicEnemy(platform2, self)
        self.enemies.append(enemy2)
        platform2.addEnemy(enemy2)

        self.gameOver = False
        # game over image contains images from the original Double Panda game:
        # https://www.coolmathgames.com/0-double-panda
        self.gameOverImage = self.loadImage('gameover.png')

    # called every key press
    def keyPressed(self, event):
        if self.gameOver or event.key == 'r':
            self.appStarted()
        
        if self.isSwitching:
            # cannot do anything else while game over or switching players
            return

        if (event.key == 'h'):
            self.app.setActiveMode(self.app.helpMode)
        elif (event.key == 's'):
            self.score += 10000
        elif (event.key == 'Space'): # switch players
            if (not self.currPlayerIsWalkingRight and 
                not self.currPlayerIsWalkingRight and 
                not self.currPlayerIsJumping and 
                not self.currPlayer.isFalling):
                if self.currPlayer == self.giantPanda:
                    self.currPlayer = self.redPanda
                    self.otherPlayer = self.giantPanda
                else:
                    self.currPlayer = self.giantPanda
                    self.otherPlayer = self.redPanda
                self.isSwitching = True
                # check if old currPlayer is on new currPlayer's head
                currPlayerHead = self.currPlayer.y - self.currPlayer.scaledHeight
                if (self.otherPlayer.y == currPlayerHead):
                    self.otherPlayerIsOnCurr = True
                return
        elif (event.key == 'Right'):
            if (self.currPlayer == self.redPanda and self.currPlayerIsOnBamboo):
                self.currPlayerIsJumpingOffBambooRight = True
                self.jumpStartingHeight = self.currPlayer.y
            elif (not self.currPlayerIsJumpingOffBambooRight):
                self.currPlayerIsWalkingRight = True
        elif (event.key == 'Left'):
            if (self.currPlayer == self.redPanda and self.currPlayerIsOnBamboo):
                self.currPlayerIsJumpingOffBambooLeft = True
                self.jumpStartingHeight = self.currPlayer.y
            elif (not self.currPlayerIsJumpingOffBambooLeft):
                self.currPlayerIsWalkingLeft = True
        elif (event.key == 'Up'):
            if (self.currPlayer == self.redPanda and 
                not self.currPlayerIsWalkingRight and 
                not self.currPlayerIsWalkingLeft):
                self.currBamboo = self.atBamboo()
                if ((self.currBamboo != None and self.currPlayer.y == self.currBamboo.startingHeight)
                    or self.currPlayerIsOnBamboo):
                    self.currPlayerIsClimbingUp = True
                    self.currPlayerIsOnBamboo = True
                    return
                else:
                    pass
            if (self.currPlayer.y == self.findGoalHeight(self.currPlayer)):
                # only allowed to jump if currPlayer is on a ground
                self.currPlayerIsJumping = True
                self.jumpStartingHeight = self.currPlayer.y
        elif (event.key == 'Down'):
            if self.currPlayerIsOnBamboo:
                self.currPlayerIsClimbingUp = False
                self.currPlayerIsClimbingDown = True

    # called every key release
    def keyReleased(self, event):
        if (event.key == 'Right'):
            self.currPlayerIsWalkingRight = False
        elif (event.key == 'Left'):
            self.currPlayerIsWalkingLeft = False
        elif (event.key == 'Up'):
            self.currPlayerIsClimbingUp = False
        elif (event.key == 'Down'):
            self.currPlayerIsClimbingDown = False
        # note: do not control jumping boolean flag here because it is being
        # turned off by itself when currPlayer reaches ground

    # returns True if currPlayer (redPanda) is at a bamboo
    def atBamboo(self):
        for bamboo in self.bamboos:
            x0 = bamboo.x - Bamboo.width / 2
            x1 = bamboo.x + Bamboo.width / 2
            if (x0  <= self.currPlayer.x <= x1):
                return bamboo
        return None

    ####################################
    # Move methods
    ####################################

    # following function derived from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
    # scroll to make player visible as needed
    def makePlayerVisible(self, dx):
        # cannot scroll to the left of the starting position
        if (self.currPlayer.x > self.width / 2):
            self.scrollX += dx

    # executes stepping of currPlayer
    def stepCurrPlayer(self, dx):
        # update currPlayer's position
        if (self.currPlayer.x - (self.currPlayer.scaledWidth / 2) + dx > 0):
            # cannot walk to the left of the starting position
            self.currPlayer.x += dx
            self.currPlayer.x0 += dx
            self.currPlayer.x1 += dx
            if (self.currPlayer.x > self.maxCurrPlayerX): # update maxCurrPlayerX
                self.maxCurrPlayerX = self.currPlayer.x

        # change scroll (for drawing view)
        self.makePlayerVisible(dx) # careful: dx is already negative for moving left

        # get the correct sprite image list
        if (dx < 0): # moving left
            self.currPlayer.currSpritesInDir = self.currPlayer.spritesMoveLeft
        elif (dx > 0): # moving right
            self.currPlayer.currSpritesInDir = self.currPlayer.spritesMoveRight
        
        # go to next sprite image
        if (not self.currPlayerIsJumpingOffBambooRight and
            not self.currPlayerIsJumpingOffBambooLeft and 
            not self.currPlayerIsJumping and 
            not self.currPlayer.isFalling):
            self.currPlayer.spriteCounter = (1 + self.currPlayer.spriteCounter) % len(self.currPlayer.currSpritesInDir)
        
        # check if walking off the edge
        if (self.currPlayer.y != self.floorLevel):
            # if the currPlayer is not on a platform
            self.currPlayer.isFalling = not self.checkIfCurrPlayerOnPlatform()
        
        self.checkCandyCollisions()

    # returns True if currPlayer is on a platform
    # used to check whether to fall off platform while walking
    def checkIfCurrPlayerOnPlatform(self):
        for platform in self.platforms:
            if (platform.x0 <= self.currPlayer.x <= platform.x1 and
                self.currPlayer.y == self.floorLevel - platform.height):
                return True
        
        # check if it is possible to land on otherPlayer's head
        if (self.otherPlayer.x - self.otherPlayer.scaledWidth / 2 <=
            self.currPlayer.x <= 
            self.otherPlayer.x + self.otherPlayer.scaledWidth / 2):
            otherPlayerHead = self.otherPlayer.y - self.otherPlayer.scaledHeight
            if (self.currPlayer.y == otherPlayerHead):
                return True
        
        return False
    
    # increment climb
    def climbUpCurrPlayer(self):
        if (self.currPlayer.y - self.currPlayer.scaledHeight - self.climbSpeed > 0):
            # cannot past top of screen
            self.currPlayer.y -= self.climbSpeed
            self.currPlayer.y0 -= self.climbSpeed
            self.currPlayer.y1 -= self.climbSpeed
                
        # go to next sprite image
        self.currPlayer.spriteCounter = (1 + self.currPlayer.spriteCounter) % len(self.currPlayer.currSpritesInDir)
    
    # increment climb
    def climbDownCurrPlayer(self):
        if (self.currPlayer.y - self.currBamboo.startingHeight + self.climbSpeed <= 0):
            # cannot climb down past bottom of bamboo
            self.currPlayer.y += self.climbSpeed
            self.currPlayer.y0 += self.climbSpeed
            self.currPlayer.y1 += self.climbSpeed
        else: # landed
            self.currPlayer.currSpritesInDir = self.currPlayer.spritesMoveRight
            self.currPlayerIsClimbingDown = False 
            self.currPlayerIsOnBamboo = False
            self.currBamboo = None
                
        # go to next sprite image
        self.currPlayer.spriteCounter = (1 + self.currPlayer.spriteCounter) % len(self.currPlayer.currSpritesInDir)

    # increment jumping off bamboo in a direction
    def jumpOffBambooCurrPlayer(self, dx):
        self.currPlayerIsClimbingUp = False
        self.currPlayerIsClimbingDown = False
        self.currPlayerIsOnBamboo = False
        self.currBamboo = None

        # jump off left or right

        # update currPlayer's position
        if (self.currPlayer.x - (self.currPlayer.scaledWidth / 2) + dx > 0):
            # cannot walk to the left of the starting position
            self.currPlayer.x += dx
            self.currPlayer.x0 += dx
            self.currPlayer.x1 += dx
            if (self.currPlayer.x > self.maxCurrPlayerX): # update maxCurrPlayerX
                self.maxCurrPlayerX = self.currPlayer.x

        # change scroll (for drawing view)
        self.makePlayerVisible(dx) # careful: dx is already negative for moving left

        # get the correct sprite image list
        if (dx < 0): # moving left
            self.currPlayer.currSpritesInDir = self.currPlayer.spritesMoveLeft
        elif (dx > 0): # moving right
            self.currPlayer.currSpritesInDir = self.currPlayer.spritesMoveRight

        if (self.currPlayerReachedTopOfJump == False): # jump up
            if (self.currPlayer.y > self.jumpStartingHeight - self.jumpHeight):
                self.currPlayer.y -= self.jumpSpeed
                self.currPlayer.y0 -= self.jumpSpeed
                self.currPlayer.y1 -= self.jumpSpeed
            else:
                self.currPlayer.y = self.jumpStartingHeight - self.jumpHeight
                self.currPlayerReachedTopOfJump = True
        else: # reached top of jump
            goalHeight = self.findGoalHeight(self.currPlayer)
            if (abs(self.currPlayer.y - goalHeight) > self.jumpSpeed): # fall down
                self.currPlayer.y += self.jumpSpeed
                self.currPlayer.y0 += self.jumpSpeed
                self.currPlayer.y1 += self.jumpSpeed
            elif (abs(self.currPlayer.y - goalHeight) <= self.jumpSpeed): # reached ground
                self.currPlayer.y = self.currPlayer.y0 = goalHeight
                self.currPlayer.y1 = goalHeight- self.currPlayer.scaledHeight
                self.currPlayerReachedTopOfJump = False
                self.currPlayerIsJumpingOffBambooRight = False
                self.currPlayerIsJumpingOffBambooLeft = False
                return

        self.checkCandyCollisions()

    # increment y coordinate of currPlayer during the jump
    def jumpCurrPlayer(self):
        # increment y coordinate based on what part of the jump currPlayer is on
        if (self.currPlayerReachedTopOfJump == False): # jump up
            if (self.currPlayer.y > self.jumpStartingHeight - self.jumpHeight):
                self.currPlayer.y -= self.jumpSpeed
                self.currPlayer.y0 -= self.jumpSpeed
                self.currPlayer.y1 -= self.jumpSpeed
            else:
                self.currPlayerReachedTopOfJump = True
        else: # fall back down
            self.currPlayer.isFalling = True
            self.currPlayerIsJumping = False
            self.currPlayerReachedTopOfJump = False
        self.checkCandyCollisions()

    # increment y coordinate of currPlayer down during fall
    def fallPlayer(self, player, dy):
        goalHeight = self.findGoalHeight(player)
        #if (player.y < goalHeight):
        if (abs(player.y - goalHeight) > self.jumpSpeed):
            player.y += dy
            player.y0 += dy
            player.y1 += dy
        elif (abs(player.y - goalHeight) <= self.jumpSpeed): # reached ground
            player.y = player.y0 = goalHeight
            player.y1 = goalHeight - player.scaledHeight
            player.isFalling = False
            # when giant panda lands on the enemy, kill it
            if (self.currPlayer == self.giantPanda):
                if (self.enemyUnderCurrPlayer != None):
                    if (self.giantPanda.canKill):
                        self.score += self.enemyUnderCurrPlayer.die()
                        self.giantPanda.canKill = False
                        self.enemies.remove(self.enemyUnderCurrPlayer)
                        self.enemyUnderCurrPlayer.platform.enemiesOn.remove(self.enemyUnderCurrPlayer)
                        self.enemyUnderCurrPlayer = None
                        self.currPlayer.isFalling = True
                else:
                    # can only kill once per time on enemy's head
                    self.giantPanda.canKill = True
        self.checkCandyCollisions()

    # find height to land on (platform or floor) after jump
    # mainly a helper method for fallCurrPlayer()
    def findGoalHeight(self, player):
        possibleGoals = [] # possible platforms to land on
        possibleEnemyHeads = dict()
        possiblePlatforms = dict()

        # loop through list of platforms
        # check if currPlayer is between x0 and x1 of them (add if possible)
        for platform in self.platforms:
            realPlatformHeight = self.floorLevel - platform.height
            if (platform.x0 < player.x0 < platform.x1 or 
                platform.x0 < player.x1 < platform.x1):
                possibleGoals.append(realPlatformHeight)
                possiblePlatforms[realPlatformHeight] = platform
                
                # check if it is possible to land on an enemy's head (add if possible)
                for enemy in platform.enemiesOn:
                    if (enemy.x0 < player.x0 < enemy.x1 or enemy.x0 < player.x1 < enemy.x1):
                        enemyHead = enemy.y - enemy.scaledHeight
                        possibleGoals.append(enemyHead)
                        possibleEnemyHeads[enemyHead] = enemy

        # this function must be usable for otherPlayer as well
        # currPlayer can land on otherPlayer
        if (player == self.currPlayer):
            # check if it is possible to land on otherPlayer's head (add if possible)
            if (self.otherPlayer.x0 <= player.x0 <= self.otherPlayer.x1 or 
                self.otherPlayer.x0 <= player.x1 <= self.otherPlayer.x1):
                otherPlayerHead = self.otherPlayer.y - self.otherPlayer.scaledHeight
                possibleGoals.append(otherPlayerHead)

        bestGoalHeight = self.floorLevel
        # check all possible platforms to land on 
        # if there is a closer one to land on, land on that one
        for possibleGoal in possibleGoals:
            # check if y is higher than possibleGoal (or equal to)
            # check if possibleGoal is closer to y than bestGoalHeight
            if (player.y <= possibleGoal and 
                possibleGoal < bestGoalHeight):
                bestGoalHeight = possibleGoal
        
        if (bestGoalHeight in possibleEnemyHeads):
            # if giantPanda lands on enemy, kill the enemy
            self.enemyUnderCurrPlayer = possibleEnemyHeads[bestGoalHeight]
        else:
            self.enemyUnderCurrPlayer = None
            
        return bestGoalHeight

    # manipulates self.scrollX to bring the new currPlayer to center of canvas
    def switchTransition(self):
        leftEdgeToStartDist = self.width / 2
        # leftEdgeToStartDist is the distance from the left edge of the screen
        # at the start of the game to the starting position 300
        # note: starting position 300 is for the first currPlayer
        
        if (self.scrollX > self.currPlayer.x - leftEdgeToStartDist):
            # cannot scroll past the left of the starting position
            if (self.scrollX <= 0):
                self.isSwitching = False
                self.timerDelay = self.defaultTimerDelay
            else:
                # new currPlayer is to the left of old currPlayer
                self.scrollX -= self.scrollSpeedWhenSwitching
        elif (self.scrollX < self.currPlayer.x - leftEdgeToStartDist):
            # new currPlayer is to the right of old currPlayer
            self.scrollX += self.scrollSpeedWhenSwitching
        elif (self.currPlayer.x - self.scrollX == leftEdgeToStartDist):
            # reached the new currPlayer
            self.isSwitching = False
            self.timerDelay = self.defaultTimerDelay

    # check for collision with candy and eat it if there is 
    def checkCandyCollisions(self):
        for candy in self.candies:
            candyX0 = candy.x - candy.width // 2
            candyX1 = candy.x + candy.width // 2
            candyY0 = candy.y - candy.height
            candyY1 = candy.y
            if ((candyX0 <= self.currPlayer.x0 <= candyX1 or candyX0 <= self.currPlayer.x1 <= candyX1) and
                (candyY0 <= self.currPlayer.y0 <= candyY1 or candyY0 <= self.currPlayer.y1 <= candyY1)):
                if (candy.candyType == 'Fried Rice' and 
                    self.currPlayer == self.giantPanda):
                    continue
                self.score += candy.scoreGain
                self.candies.remove(candy)
    
    # returns distance between (x0, y0) and (x1, y1)
    def dist(self, x0, y0, x1, y1):
        return ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5

    # otherPlayer should fall if currPlayer walks out from under it
    def otherPlayerFallIfOnCurrPlayer(self):
        currPlayerHead = self.currPlayer.y - self.currPlayer.scaledHeight
        if (self.otherPlayer.y == currPlayerHead and 
            (self.otherPlayer.x0 <= self.currPlayer.x0 <= self.otherPlayer.x1 or 
             self.otherPlayer.x0 <= self.currPlayer.x1 <= self.otherPlayer.x1)):
            self.otherPlayer.isFalling = True

    # control movements of currPlayer by calling move methods based on boolean flags
    # called every timerFired
    def timerFiredMovements(self):
        # always be able to move right or left if 'R' or 'L' key is being pressed
        if self.currPlayerIsWalkingRight:
            self.stepCurrPlayer(+self.dx)
        elif self.currPlayerIsWalkingLeft:
            self.stepCurrPlayer(-self.dx)
        
        if self.currPlayerIsJumping:
            self.otherPlayerFallIfOnCurrPlayer()
            self.jumpCurrPlayer()
        elif self.currPlayer.isFalling:
            self.fallPlayer(self.currPlayer, self.jumpSpeed)
        elif self.currPlayerIsClimbingUp:
            self.otherPlayerFallIfOnCurrPlayer()
            self.climbUpCurrPlayer()
        elif self.currPlayerIsClimbingDown:
            self.climbDownCurrPlayer()
        elif self.currPlayerIsJumpingOffBambooRight:
            self.jumpOffBambooCurrPlayer(+self.dx)
        elif self.currPlayerIsJumpingOffBambooLeft:
            self.jumpOffBambooCurrPlayer(-self.dx)
        elif self.isSwitching:
            # execute the transition faster than usual timeDelay
            self.timerDelay = self.timerDelayDuringSwitching
            self.switchTransition()
        
        # check if otherPlayer is on currPlayer's head
        # purpose: otherPlayer should fall if currPlayer walks out from underneath
        if self.otherPlayerIsOnCurr:
            # check if currPlayer walked out from underneath
            if (self.otherPlayer.x0 > self.currPlayer.x1 - self.dx or
                self.otherPlayer.x1 < self.currPlayer.x0 + self.dx):
                self.otherPlayer.isFalling = True
        if self.otherPlayer.isFalling:
            self.fallPlayer(self.otherPlayer, self.jumpSpeed)
        
        # check if currPlayer as redPanda is on an enemy's head
        # purpose: currPlayer should fall if enemy walks out from underneath
        if (self.enemyUnderCurrPlayer != None):
            if (self.currPlayer.x0 > self.enemyUnderCurrPlayer.x1 or 
                self.currPlayer.x1 < self.enemyUnderCurrPlayer.x0):
                self.enemyUnderCurrPlayer = None # reset
                self.currPlayer.isFalling = True

    ####################################
    # Enemy methods
    ####################################

    # returns the player that is close enough to shoot at or None otherwise
    def closeEnoughToShoot(self, enemy):
        # enemy should be at or above the target player
        if (0 < abs(enemy.x - self.currPlayer.x) < 200 and
            enemy.y <= self.currPlayer.y):
            return self.currPlayer
        elif (0 < abs(enemy.x - self.otherPlayer.x) < 200 and
            enemy.y <= self.currPlayer.y):
            return self.otherPlayer
        return None

    # predict where to shoot
    def predictTarget(self, enemy, targetPlayer):
        # stepping does not change weapon's position, so reset it here
        enemy.weapon.x = enemy.x

        if (self.score <= 10000):
            targetX = targetPlayer.x
            targetY = targetPlayer.y - targetPlayer.scaledHeight // 2
            enemy.weapon.shootingCalculations(targetX, targetY, targetPlayer)
        else:
            # speed of weapon increases
            enemy.weapon.v *= 1.01
            
            # targetX changes based on direction of currPlayer
            if (self.currPlayerIsWalkingLeft):
                if (enemy.shootCount == 0):
                    targetX = targetPlayer.x
                elif (enemy.shootCount == 1):
                    targetX = targetPlayer.x - 150
                elif (enemy.shootCount == 2):
                    targetX = targetPlayer.x - 300
            elif (self.currPlayerIsWalkingRight):
                if (enemy.shootCount == 0):
                    targetX = targetPlayer.x
                elif (enemy.shootCount == 1):
                    targetX = targetPlayer.x + 150
                elif (enemy.shootCount == 2):
                    targetX = targetPlayer.x + 300
            else:
                targetX = targetPlayer.x

        targetY = targetPlayer.y - targetPlayer.scaledHeight // 2
        enemy.weapon.shootingCalculations(targetX, targetY, targetPlayer)

        if (targetX < enemy.x):
            enemy.tempShootingSprite = enemy.spritesMoveLeft[0]
        elif (targetX > enemy.x):
            enemy.tempShootingSprite = enemy.spritesMoveRight[0]
        else:
            enemy.tempShootingSprite = enemy.currSpritesInDir[enemy.spriteCounter]

    # increment the weapon's position
    def incrementShooting(self, enemy):
        weapon = enemy.weapon
        newX = weapon.x + weapon.dx
        newY = weapon.y + weapon.dy

        if (weapon.y > self.floorLevel): 
            # passed through floor
            enemy.resetWeapon()
            enemy.shootCount += 1
        elif (abs(weapon.x - enemy.x) > 400):
            # passed distance of 400 (went too far)
            enemy.resetWeapon()
            enemy.shootCount += 1
        elif (weapon.targetPlayer.x0 <= newX <= weapon.targetPlayer.x1 and
              weapon.targetPlayer.y0 >= newY >= weapon.targetPlayer.y1):
            # hit target
            enemy.weapon.targetPlayer.livesLeft -= 1
            enemy.resetWeapon()
            enemy.shootCount += 1
        else:
            # increment position
            weapon.x = newX
            weapon.y = newY

    # increment the enemy's position
    def autoStepEnemy(self, enemy):
        # update enemy's position

        # BasicEnemy can walk towards player if it is on the same platform
        # and the score is high
        if (isinstance(enemy, BasicEnemy) and self.score >= 10000):
            for player in [self.currPlayer, self.otherPlayer]:
                if (enemy.y0 > player.y >= enemy.y1 and
                    (enemy.platform.x0 <= player.x0 < enemy.platform.x1 or
                     enemy.platform.x0 < player.x1 <= enemy.platform.x1)):
                    # close enough to player
                    if (player.x + player.scaledWidth < enemy.x):
                        enemy.currSpritesInDir = enemy.spritesMoveLeft
                        continue
                    elif (player.x - player.scaledWidth > enemy.x):
                        enemy.currSpritesInDir = enemy.spritesMoveRight
                        continue

        if (enemy.currSpritesInDir == enemy.spritesMoveRight):
            newX = enemy.x + enemy.dx
            newX0 = enemy.x0 + enemy.dx
            newX1 = enemy.x1 + enemy.dx
        elif (enemy.currSpritesInDir == enemy.spritesMoveLeft):
            newX = enemy.x - enemy.dx
            newX0 = enemy.x0 - enemy.dx
            newX1 = enemy.x1 - enemy.dx
        
        if (newX < enemy.maxLeft): 
            # too far off left
            enemy.currSpritesInDir = enemy.spritesMoveRight
            enemy.x = enemy.maxLeft
        elif (newX > enemy.maxRight): 
            # too far off right
            enemy.currSpritesInDir = enemy.spritesMoveLeft
            enemy.x = enemy.maxRight
        else:
            enemy.x = newX
            enemy.x0 = newX0
            enemy.x1 = newX1

        # go to next sprite image
        enemy.spriteCounter = (1 + enemy.spriteCounter) % len(enemy.currSpritesInDir)

    # check if enemy is colliding with players
    def checkEnemyCollisions(self, enemy):
        for player in [self.currPlayer, self.otherPlayer]:
            if (enemy.checkCollisions(player)):
                player.livesLeft -= 1

    # control movements of enemies
    # called every timerFired
    def timerFiredEnemies(self):
        # pause enemies while switching
        if self.isSwitching:
            return
        
        for enemy in self.enemies:
            # increment step
            if (isinstance(enemy, BasicEnemy)):
                self.autoStepEnemy(enemy)
            elif (isinstance(enemy, ArcherEnemy)):
                if ((enemy.shootCount > 2 or enemy.shootCount == 0) and 
                    enemy.isShooting == False):
                    self.autoStepEnemy(enemy)

            # check collisions
            self.checkEnemyCollisions(enemy)

            # check if it can shoot
            if (isinstance(enemy, ArcherEnemy)):
                if enemy.isShooting:
                    # increment shoot if is shooting
                    self.incrementShooting(enemy)
                else:
                    if (enemy.shootCount > 2):
                        if (enemy.shootingStartWaitTime == 0):
                            enemy.shootingStartWaitTime = time.time()
                        elif (time.time() - enemy.shootingStartWaitTime > enemy.shootingWaitTime):
                            enemy.shootCount = 0
                            enemy.shootingStartWaitTime = 0
                        continue
                    
                    result = self.closeEnoughToShoot(enemy)
                    if (result != None):
                        # start shooting if it is close enough to shoot
                        enemy.isShooting = True
                        self.predictTarget(enemy, result)
                        # start shooting
                        enemy.weapon.x = enemy.x
                        enemy.weapon.y = enemy.y - (enemy.scaledHeight // 2)
                        self.incrementShooting(enemy)
                    else:
                        enemy.shootCount = 0
                        enemy.resetWeapon()

    ####################################
    # Terrain generation methods
    ####################################

    # returns list of last 5 or less platforms
    def getLastFewPlatforms(self):
        if (len(self.platforms) < 5):
            return self.platforms
        else:
            return self.platforms[-5::+1]

    # returns the furthest x1 from the given list of platforms
    def getFurthestX1(self, platforms):
        furthestX1 = 0
        for platform in platforms:
            if platform.x1 > furthestX1:
                furthestX1 = platform.x1
        
        furthestBambooX1 = self.bamboos[-1].x + Bamboo.width / 2
        if (furthestBambooX1 > furthestX1):
            furthestX1 = furthestBambooX1

        return furthestX1

    # generates a group of platforms with enemies, candy, and a bamboo if necessary
    def generateTerrain(self):
        # Inspired by https://youtu.be/iQXLQzOaIpE and Game AI TA Mini-Lecture
        # to use probabilities (random number). From the video, I was also 
        # inspired to use a loop to generate 'terrain.'

        # determine where the bottom platform will be
        
        r1 = random.randint(0, 100)
        if (r1 < 40):
            bottomLevel = 1
        elif (40 <= r1 < 60):
            bottomLevel = 2
        elif (60 <= r1 < 75):
            bottomLevel = 2.5
        elif (75 <= r1 < 88):
            bottomLevel = 3
        else:
            bottomLevel = 4

        # determine where the top platform will be 
        if (self.score < 1500): 
            # depends on the score (higher score -> higher top level)
            if (bottomLevel < 3):
                topLevel = 3
            else:
                topLevel = bottomLevel + 1
        else:
            r2 = random.randint(0, 100)
            if (r2 < 70):
                topLevel = 5
            else:
                if (bottomLevel < 4):
                    topLevel = 4
                else:
                    topLevel = 5

        level = bottomLevel
        levelCount = 1
        lastFewPlatforms = self.getLastFewPlatforms()
        furthestX1 = self.getFurthestX1(lastFewPlatforms)
        x0SetOffChoices = [100, 150, 200]
        skippedLevel = False
        
        # generate bamboo if required (too high to reach by just jumping on e/o)
        if (bottomLevel > 2):
            generatedBamboo = False

            # probability of bamboo being on the left or right
            probBambooLR = random.choice([0, 1])

            if (probBambooLR == 0): 
                # generate bamboo to the left of the group of platforms
                self.generateBamboo(furthestX1, 0)
                generatedBamboo = True
                x0SetOffChoices = [250]
        
        # generate platforms by looping from bottom to top levels
        while level <= topLevel:
            # further platforms up can be set off farther
            if (level > bottomLevel):
                x0SetOffChoices.extend([i for i in range(x0SetOffChoices[-1]+50, 401, 50)])

            # calculate x0 and x1 of new platform
            x0 = furthestX1 + random.choice(x0SetOffChoices)
            x1 = x0 + random.randint(Platform.minLength, Platform.maxLength)
            
            # create new platform
            newPlatform = Platform(level, x0, x1, self)
            self.platforms.append(newPlatform)
            self.generateCandy(newPlatform, bottomLevel)
            self.generateEnemies(newPlatform, topLevel)

            # determine next platform to add
            # randomly skip a platform (requiring one player to jump on the other's head)
            r3 = random.randint(0, 100)
            if (bottomLevel != 2 and not skippedLevel):
                if (r3 < 20):
                    level += 1.5
                    skippedLevel = True
                elif (20 <= r3 < 40):
                    level += 2
                    skippedLevel = True
                else:
                    level += 1
            else:
                level += 1
            levelCount += 1
        
        if (bottomLevel > 2 and generatedBamboo == False):
            self.generateBamboo(0, levelCount - 1)

    # generate candy on a given platform
    def generateCandy(self, platform, bottomLevel):
        # Inspired by https://youtu.be/iQXLQzOaIpE and Game AI TA Mini-Lecture
        # to use probabilities (random number). From the video, I was also 
        # inspired to use a loop to generate 'terrain.'

        # every platform have candy

        # randomly choose where to start at the beginning of the platform
        x = random.randint(platform.x0 + Candy.standardWidth / 2, 
                           int(platform.x0 + (platform.x1 - platform.x0) / 2))
        # randomly choose where to start at the beginning of the platform
        x1 = random.randint(int(platform.x0 + (platform.x1 - platform.x0) / 2), 
                            platform.x1 - Candy.standardWidth)
        
        # there should only be one on a platform at a time
        # only red panda can eat fried rice
        madeFriedRice = False

        # loop through the length of the platform
        while (x < x1):
            newCandy = Candy(x, self.floorLevel - platform.height, self)

            # decide whether to make fried rice
            if (madeFriedRice == False):
                if (bottomLevel > 2): 
                    # increase chance of fried rice if bottomLevel > 2
                    probFriedRice = random.randint(0, 100)
                    if (platform.level == 5):
                        newCandy.makeIntoFriedRice()
                        madeFriedRice = True
                    elif (platform.level == 4 and probFriedRice < 90):
                        newCandy.makeIntoFriedRice()
                        madeFriedRice = True
                    elif (platform.level == 3 and probFriedRice < 80):
                        newCandy.makeIntoFriedRice()
                        madeFriedRice = True
                    elif (platform.level == 2.5 and probFriedRice < 70):
                        newCandy.makeIntoFriedRice()
                        madeFriedRice = True
                else:
                    probFriedRice = random.randint(0, 100)
                    if (probFriedRice < 10):
                        newCandy.makeIntoFriedRice()
                        madeFriedRice = True

            self.candies.append(newCandy)
            x += Candy.standardWidth + 20
    
    # generate enemies on a given platform
    def generateEnemies(self, platform, topLevel):
        # Inspired by https://youtu.be/iQXLQzOaIpE and Game AI TA Mini-Lecture
        # to use probabilities (random number). From the video, I was also 
        # inspired to use a loop to generate 'terrain.'

        # probability of this platform having enemy(ies)
        probEnemy = random.randint(0, 100)
        if (self.score < 5000 and probEnemy < 60):
            # very low score (< 5k) has 40% chance of enemy
            return
        elif (5000 <= self.score < 10000 and probEnemy < 50):
            # low score (< 10k) has 50% chance of enemy
            return
        elif (self.score >= 10000 and probEnemy < 40):
            # high score (>= 10k) has 60% chance of enemy
            return

        # determine how many enemies on the platform
        probEnemyCount = random.randint(0, 100)
        platformLength = platform.x1 - platform.x0
        if (self.score < 5000):
            # very low score (< 5k) will only have 1 enemy per platform
            enemyCount = 1
        elif (5000 <= self.score < 10000):
            if (probEnemy < 15 and platformLength > 300):
                # low score (< 10k) has <15% chance of having 2 enemies per platform
                enemyCount = 2
            else:
                # low score (< 10k) has 85% chance of having 1 enemies per platform
                enemyCount = 1
        elif (self.score >= 10000):
            if (probEnemyCount < 5 and platformLength > 400):
                # high score (>= 10k) has <5% chance of having 3 enemies per platform
                enemyCount = 3
            elif (5 <= probEnemyCount < 20 and platformLength > 300):
                # high score (>= 10k) has <15% chance of having 2 enemies per platform
                enemyCount = 2
            else:
                # high score (>= 10k) has 80% chance of having 1 enemies per platform
                enemyCount = 1
        
        # loop through enemyCount to generate enemies on the platform
        while (enemyCount > 0):
            # determine what type of enemy
            probType = random.randint(0, 10)
            if (probType < 6):
                newEnemy = BasicEnemy(platform, self)
            else:
                if (topLevel - platform.level < 1):
                    # archer enemies should only appear on the top level to be
                    # able to be killed
                    newEnemy = ArcherEnemy(platform, self)
                else:
                    newEnemy = BasicEnemy(platform, self)

            self.enemies.append(newEnemy)
            platform.addEnemy(newEnemy)

            enemyCount -= 1

    # generate one bamboo next to a group of platforms that requires it
    def generateBamboo(self, furthestX1, levelCount):
        # Inspired by https://youtu.be/iQXLQzOaIpE and Game AI TA Mini-Lecture
        # to use probabilities (random number).

        if (furthestX1 != 0):
            # this means that the bamboo is to the left of the platforms
            xSetOff = random.randint(130, 150)
            newBamboo = Bamboo(xSetOff + furthestX1, self.floorLevel, self)
        elif (levelCount != 0):
            # this means that the bamboo is to the right of the platforms

            # find furthest x1
            furthestX1 = 0
            furthestPlatform = self.platforms[-1]
            for i in range(-1, levelCount * -1 - 1, -1):
                x1 = self.platforms[i].x1
                if (x1 > furthestX1):
                    furthestX1 = x1
                    furthestPlatform = self.platforms[i]

            # find what the x setoff should be
            lastLevel = furthestPlatform.level
            if (lastLevel == 5 or lastLevel == 4.5):
                xSetOff = 100
            elif (lastLevel == 4 or lastLevel == 3.5):
                xSetOff = random.randint(100, 150)
            elif (lastLevel == 3):
                xSetOff = random.randint(150, 200)
            elif (lastLevel == 2.5):
                xSetOff = random.randint(200, 250)
            newBamboo = Bamboo(xSetOff + furthestX1, self.floorLevel, self)

        self.bamboos.append(newBamboo)

    # called every timerDelay
    def timerFired(self):
        # check if game is over
        if (self.giantPanda.livesLeft < 1 or self.redPanda.livesLeft < 1):
            self.gameOver = True
            return
        
        # generate more terrain, enemies, and candy as player moves
        if (self.platforms[-1].x1 - self.maxCurrPlayerX < self.width / 2): # 400
            self.generateTerrain()

        self.timerFiredMovements()
        self.timerFiredEnemies()
        
    ####################################
    # View methods
    ####################################

    # following function copied & pasted from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
    # lines of code that call this function are derived from this website as well
    def getCachedPhotoImage(self, image):
        # stores a cached version of the PhotoImage in the PIL/Pillow image
        if ('cachedPhotoImage' not in image.__dict__):
            image.cachedPhotoImage = ImageTk.PhotoImage(image)
        return image.cachedPhotoImage

    # following code derived from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
    # (the idea of using a scroll variable is from this website)
    # draws background
    def drawBackground(self, canvas):
        # draw background sky
        canvas.create_image(0, 0, 
                            image=self.getCachedPhotoImage(self.background), 
                            anchor='nw')
        
        # draw floor
        canvas.create_image(0, self.floorLevel, 
                            image=self.getCachedPhotoImage(self.floor), 
                            anchor='nw')

        # draw platforms
        for platform in self.platforms:
            x0 = platform.x0 - self.scrollX
            y0 = self.floorLevel - platform.height
            x1 = platform.x1 - self.scrollX
            y1 = self.floorLevel - platform.height + 20
            canvas.create_rectangle(x0, y0, x1, y1, fill='black')
        
        # draw bamboos
        for bamboo in self.bamboos:
            x0 = bamboo.x - Bamboo.width / 2 - self.scrollX
            x1 = bamboo.x + Bamboo.width / 2 - self.scrollX
            canvas.create_rectangle(x0, bamboo.startingHeight, 
                                    x1, 0, fill='green', width=0)

    # draws candies
    def drawCandy(self, canvas):
        for candy in self.candies:
            x = candy.x - self.scrollX
            y = candy.y
            width = candy.width
            height = candy.height
            canvas.create_image(x, y, 
                                image=self.getCachedPhotoImage(candy.image),
                                anchor='s')

    # draws the enemies
    def drawEnemies(self, canvas):
        for enemy in self.enemies:
            cx = enemy.x - self.scrollX
            if (isinstance(enemy, ArcherEnemy) and 
                (enemy.isShooting or 0 < enemy.shootCount <= 2)):
                # draw weapon
                r = 10
                weapon = enemy.weapon
                x = weapon.x - self.scrollX
                y = weapon.y
                canvas.create_oval(x-r, y-r, x+r, y+r, fill='pink', width=0)

                # change sprite
                sprite = enemy.tempShootingSprite
            else:
                sprite = enemy.currSpritesInDir[enemy.spriteCounter]
            canvas.create_image(cx, enemy.y, image=self.getCachedPhotoImage(sprite), anchor='s')

    # draws the current score
    def drawLivesLeftAndScore(self, canvas):
        canvas.create_text(20, self.height - 60, text='Lives Left', anchor='w',
                           font='Roboto 14 bold', fill='white')
        canvas.create_text(20, self.height - 40, 
                           text=f'Giant Panda: {self.giantPanda.livesLeft}', 
                           anchor='w', font='Roboto 12', fill='white')
        canvas.create_text(20, self.height - 20, 
                           text=f'Red Panda: {self.redPanda.livesLeft}', 
                           anchor='w', font='Roboto 12', fill='white')
        canvas.create_text(self.width - 20, self.height - 20, 
                           text=f'Score: {self.score}', anchor='e', 
                           font='Roboto 14 bold', fill='white')

    # draws the current player (the one being controlled right now)
    def drawCurrPlayer(self, canvas):
        cx = self.currPlayer.x - self.scrollX
        currPlayerSprite = self.currPlayer.currSpritesInDir[self.currPlayer.spriteCounter]
        canvas.create_image(cx, self.currPlayer.y, image=self.getCachedPhotoImage(currPlayerSprite), anchor='s')
    
    # draws the other player
    def drawOtherPlayer(self, canvas):
        cx = self.otherPlayer.x - self.scrollX
        otherPlayerSprite = self.otherPlayer.currSpritesInDir[self.otherPlayer.spriteCounter]
        canvas.create_image(cx, self.otherPlayer.y, image=self.getCachedPhotoImage(otherPlayerSprite), anchor='s')

    # draws game over screen
    def drawGameOver(self, canvas):
        canvas.create_image(self.width/2, self.height/2, 
                            image=self.getCachedPhotoImage(self.gameOverImage))
        canvas.create_text(self.width/2 + 60, self.height/2 + 75, 
                           text=f'{self.score}',
                           font='Roboto 30 bold', fill='brown')

    def redrawAll(self, canvas):
        self.drawBackground(canvas)
        self.drawCandy(canvas)
        self.drawEnemies(canvas)
        self.drawLivesLeftAndScore(canvas)
        self.drawOtherPlayer(canvas)
        self.drawCurrPlayer(canvas)
        if self.gameOver:
            self.drawGameOver(canvas)

# following mode derived from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#subclassingModalApp
class HelpMode(Mode):
    def appStarted(self):
        # background contains images from the original Double Panda game:
        # https://www.coolmathgames.com/0-double-panda
        self.background = self.loadImage('instructions.png')

    def redrawAll(self, canvas):
        canvas.create_image(self.width/2, self.height/2, image=ImageTk.PhotoImage(self.background))
        
    def keyPressed(self, event):
        self.app.setActiveMode(self.app.gameMode)

# following class copied & pasted from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#subclassingModalApp
class MyModalApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode = SplashScreenMode()
        app.gameMode = GameMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.splashScreenMode)
        app.timerDelay = 50

app = MyModalApp(width=800, height=600)