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
import pygame as py
from characters import *
from terrain import *
# following framework from cmu_112_graphics
from cmu_112_graphics import *

# following mode derived from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html#subclassingModalApp
class SplashScreenMode(Mode):
    def appStarted(self):
        # background contains images from the original Double Panda game:
        # https://www.coolmathgames.com/0-double-panda
        self.background = self.loadImage('images/introbackground.png')

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
        #self.maxCurrPlayerX = self.currPlayer.x
        #self.enemyUnderCurrPlayer = None

        # does not change for either current character
        self.scrollX = 0
        self.dirKeysPressed = set()

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
        self.background = self.loadImage('images/gamebackground.png')
        self.floor = self.loadImage('images/floor.png')

        # generate standard starting terrain
        self.startingTerrain()

        self.gameOver = False
        # game over image contains images from the original Double Panda game:
        # https://www.coolmathgames.com/0-double-panda
        self.gameOverImage = self.loadImage('images/gameover.png')

    # generate starting terrain for every new game
    def startingTerrain(self):
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

        # enemies
        self.enemies = []
        enemy1 = ArcherEnemy(platform4, self)
        self.enemies.append(enemy1)
        platform4.addEnemy(enemy1)
        enemy2 = BasicEnemy(platform2, self)
        self.enemies.append(enemy2)
        platform2.addEnemy(enemy2)

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
            if (not self.currPlayer.isWalkingRight and 
                not self.currPlayer.isWalkingRight and 
                not self.currPlayer.isJumping and 
                not self.currPlayer.isFalling):
                if self.currPlayer == self.giantPanda:
                    self.currPlayer = self.redPanda
                    self.otherPlayer = self.giantPanda
                else:
                    self.currPlayer = self.giantPanda
                    self.otherPlayer = self.redPanda
                self.isSwitching = True
                # check if old currPlayer is on new currPlayer's head
                self.otherPlayerIsOnCurr = self.otherPlayerOnCurrPlayer()
                # currPlayerHead = self.currPlayer.y - self.currPlayer.height
                # if (self.otherPlayer.y == currPlayerHead):
                #     self.otherPlayerIsOnCurr = True
                return
        elif (event.key == 'Right'):
            if (self.currPlayer == self.redPanda):
                if self.currPlayer.isOnBamboo:
                    self.currPlayer.isJumpingOffBambooRight = True
                    self.currPlayer.jumpStartingHeight = self.currPlayer.y
                elif not self.currPlayer.isJumpingOffBambooRight:
                    self.currPlayer.isWalkingRight = True
            else:
                self.currPlayer.isWalkingRight = True
        elif (event.key == 'Left'):
            if (self.currPlayer == self.redPanda):
                if self.currPlayer.isOnBamboo:
                    self.currPlayer.isJumpingOffBambooLeft = True
                    self.currPlayer.jumpStartingHeight = self.currPlayer.y
                elif not self.currPlayer.isJumpingOffBambooLeft:
                    self.currPlayer.isWalkingLeft = True
            else:
                self.currPlayer.isWalkingLeft = True
        elif (event.key == 'Up'):
            if (self.currPlayer == self.redPanda and 
                not self.currPlayer.isWalkingRight and 
                not self.currPlayer.isWalkingLeft):
                self.currPlayer.currBamboo = self.currPlayer.atBamboo(self.bamboos)
                if ((self.currPlayer.currBamboo != None and 
                    self.currPlayer.y == self.currPlayer.currBamboo.startingHeight)
                    or self.currPlayer.isOnBamboo):
                    self.currPlayer.isClimbingUp = True
                    self.currPlayer.isOnBamboo = True
                    return
                else:
                    pass
            if (self.currPlayer.y == self.findGoalHeight(self.currPlayer)):
                # only allowed to jump if currPlayer is on a ground
                self.currPlayer.isJumping = True
                self.currPlayer.jumpStartingHeight = self.currPlayer.y
        elif (event.key == 'Down'):
            if (self.currPlayer == self.redPanda and self.currPlayer.isOnBamboo):
                self.currPlayer.isClimbingUp = False
                self.currPlayer.isClimbingDown = True

    # called every key release
    def keyReleased(self, event):
        if (event.key == 'Right'):
            self.currPlayer.isWalkingRight = False
        elif (event.key == 'Left'):
            self.currPlayer.isWalkingLeft = False
        elif (event.key == 'Up' and self.currPlayer == self.redPanda):
            self.currPlayer.isClimbingUp = False
        elif (event.key == 'Down' and self.currPlayer == self.redPanda):
            self.currPlayer.isClimbingDown = False
        # note: do not control jumping boolean flag here because it is being
        # turned off by itself when currPlayer reaches ground

    ####################################
    # Movement methods
    ####################################

    # following function derived from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
    # scroll to make player visible as needed
    def makePlayerVisible(self, walkSpeed):
        # cannot scroll to the left of the starting position
        if (self.currPlayer.x > self.width / 2):
            self.scrollX += walkSpeed

    # return height to land on (platform or floor) after jump
    # mainly a helper method for Player.fall()
    def findGoalHeight(self, player):
        possibleGoals = [] # possible platforms to land on
        possibleEnemyHeads = dict()
        possiblePlatforms = dict()

        # find possible platform or enemy head to land on
        for platform in self.platforms:
            realPlatformHeight = self.floorLevel - platform.height
            # check if currPlayer is between x0 and x1 of platform (add if possible)
            if (platform.x0 < player.x0 < platform.x1 or 
                platform.x0 < player.x1 < platform.x1):
                possibleGoals.append(realPlatformHeight)
                possiblePlatforms[realPlatformHeight] = platform
                
                # check if it is possible to land on an enemy's head (add if possible)
                for enemy in platform.enemiesOn:
                    if (enemy.x0 < player.x0 < enemy.x1 or enemy.x0 < player.x1 < enemy.x1):
                        enemyHead = enemy.y - enemy.height
                        possibleGoals.append(enemyHead)
                        possibleEnemyHeads[enemyHead] = enemy

        # find possible otherPlayer head to land on (currPlayer can land on otherPlayer)
        # (this function must be usable for otherPlayer as well)
        if (player == self.currPlayer):
            # check if it is possible to land on otherPlayer's head (add if possible)
            if (self.otherPlayer.x0 <= player.x0 <= self.otherPlayer.x1 or 
                self.otherPlayer.x0 <= player.x1 <= self.otherPlayer.x1):
                otherPlayerHead = self.otherPlayer.y - self.otherPlayer.height
                possibleGoals.append(otherPlayerHead)

        # find closest goalHeight
        bestGoalHeight = self.floorLevel
        for possibleGoal in possibleGoals:
            # check if y is higher than possibleGoal (or equal to)
            # check if possibleGoal is closer to y than bestGoalHeight
            if (player.y <= possibleGoal and possibleGoal < bestGoalHeight):
                bestGoalHeight = possibleGoal
        
        # if goalHeight is an enemy's head, giantPanda should be ready to kill it
        # if (player == self.giantPanda):
        if (bestGoalHeight in possibleEnemyHeads):
            player.enemyUnderneath = possibleEnemyHeads[bestGoalHeight]
        else:
            player.enemyUnderneath = None
        
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

    # returns True if otherPlayer is on currPlayer's head
    def otherPlayerOnCurrPlayer(self):
        if (self.otherPlayer.y == self.currPlayer.y1):
            if (self.otherPlayer.x0 <= self.currPlayer.x0 <= self.otherPlayer.x1 or 
                self.otherPlayer.x0 <= self.currPlayer.x1 <= self.otherPlayer.x1):
                return True
        return False

    # control movements of currPlayer by calling move methods based on boolean flags
    # called every timerFired
    def timerFiredMovements(self):
        # always be able to move right or left if 'R' or 'L' key is being pressed
        if self.currPlayer.isWalkingRight:
            dx = +self.currPlayer.walkSpeed
            self.currPlayer.step(dx, self.platforms, self.otherPlayer)
            self.makePlayerVisible(dx) # change scroll (for drawing view)
            self.checkCandyCollisions()
        elif self.currPlayer.isWalkingLeft:
            dx = -self.currPlayer.walkSpeed
            self.currPlayer.step(dx, self.platforms, self.otherPlayer)
            self.makePlayerVisible(dx) # change scroll (for drawing view)
            self.checkCandyCollisions()
        
        if self.currPlayer.isJumping:
            if self.otherPlayerIsOnCurr:
                self.otherPlayer.isFalling = True
            self.currPlayer.jump()
            self.checkCandyCollisions()
        elif self.currPlayer.isFalling:
            goalHeight = self.findGoalHeight(self.currPlayer)
            self.currPlayer.fall(goalHeight, self.enemies)
            self.checkCandyCollisions()
        elif self.isSwitching:
            # execute the transition faster than usual timeDelay
            self.timerDelay = self.timerDelayDuringSwitching
            self.switchTransition()
        
        # redPanda specific actions
        if (self.currPlayer == self.redPanda):
            if self.currPlayer.isClimbingUp:
                if self.otherPlayerIsOnCurr:
                    self.otherPlayer.isFalling = True
                self.currPlayer.climbUp()
            elif self.currPlayer.isClimbingDown:
                self.currPlayer.climbDown()
            elif self.currPlayer.isJumpingOffBambooRight:
                dx = +self.currPlayer.walkSpeed
                self.currPlayer.jumpOffBamboo(dx)
                self.makePlayerVisible(dx) # change scroll (for drawing view)
                self.checkCandyCollisions()
            elif self.currPlayer.isJumpingOffBambooLeft:
                dx = -self.currPlayer.walkSpeed
                self.currPlayer.jumpOffBamboo(dx)
                self.makePlayerVisible(dx) # change scroll (for drawing view)
                self.checkCandyCollisions()
            
            # check if currPlayer as redPanda is STILL on an enemy's head
            # purpose: currPlayer should fall if enemy walks out from underneath
            if (self.currPlayer.enemyUnderneath != None):
                if (self.currPlayer.x0 > self.currPlayer.enemyUnderneath.x1 or 
                    self.currPlayer.x1 < self.currPlayer.enemyUnderneath.x0):
                    self.currPlayer.isFalling = True
                    self.currPlayer.enemyUnderneath = None # reset

        # check if otherPlayer is STILL on currPlayer's head
        # purpose: otherPlayer should fall if currPlayer walks out from underneath
        if self.otherPlayerIsOnCurr:
            # check if currPlayer walked out from underneath
            if (self.otherPlayer.x0 > self.currPlayer.x1 - self.currPlayer.walkSpeed or
                self.otherPlayer.x1 < self.currPlayer.x0 + self.currPlayer.walkSpeed):
                self.otherPlayer.isFalling = True
                self.otherPlayerIsOnCurr = False # reset
        
        if self.otherPlayer.isFalling:
            goalHeight = self.findGoalHeight(self.otherPlayer)
            self.otherPlayer.fall(goalHeight, self.enemies)

    ####################################
    # Enemy methods
    ####################################

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
                enemy.autoStepEnemy()
            elif (isinstance(enemy, ArcherEnemy)):
                if ((enemy.shootCount > 2 or enemy.shootCount == 0) and 
                    enemy.isShooting == False):
                    enemy.autoStepEnemy()

            # check collisions
            self.checkEnemyCollisions(enemy)

            # check if it can shoot
            if (isinstance(enemy, ArcherEnemy)):
                if enemy.isShooting:
                    # increment shoot if is shooting
                    enemy.incrementShooting()
                else:
                    if (enemy.shootCount > 2):
                        if (enemy.shootingStartWaitTime == 0):
                            enemy.shootingStartWaitTime = time.time()
                        elif (time.time() - enemy.shootingStartWaitTime > enemy.shootingWaitTime):
                            enemy.shootCount = 0
                            enemy.shootingStartWaitTime = 0
                        continue
                    
                    result = enemy.closeEnoughToShoot()
                    if (result != None):
                        # start shooting if it is close enough to shoot
                        enemy.isShooting = True
                        enemy.predictTarget(result)
                        # start shooting
                        enemy.weapon.x = enemy.x
                        enemy.weapon.y = enemy.y - (enemy.height // 2)
                        enemy.incrementShooting()
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
        if (self.platforms[-1].x1 - Player.maxX < self.width / 2): # 400
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
        # # draw background sky
        # canvas.create_image(0, 0, 
        #                     image=self.getCachedPhotoImage(self.background), 
        #                     anchor='nw')
        
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
                sprite = enemy.spritesCurrDir[enemy.spriteCounter]
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
        currPlayerSprite = self.currPlayer.spritesCurrDir[self.currPlayer.spriteCounter]
        canvas.create_image(cx, self.currPlayer.y, image=self.getCachedPhotoImage(currPlayerSprite), anchor='s')
    
    # draws the other player
    def drawOtherPlayer(self, canvas):
        cx = self.otherPlayer.x - self.scrollX
        otherPlayerSprite = self.otherPlayer.spritesCurrDir[self.otherPlayer.spriteCounter]
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
        self.background = self.loadImage('images/instructions.png')

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