####################################
# This game is based on the original Double Panda game: 
# https://www.coolmathgames.com/0-double-panda

####################################
# Run this file to run the project
# This file contains the game loop
####################################

import random, os
import pygame as pg
from characters import *
from terrain import *
from settings import *

class Game(object):
    # initializes game window, etc.
    def __init__(self):
        pg.init() # initialize pygame modules
        # pg.mixer.init() # initialize mixer for music
        self.screen = pg.display.set_mode((screenWidth, screenHeight))
        pg.display.set_caption(title)
        self.clock = pg.time.Clock()
        self.running = True

    # starts new game
    def new(self):
        self.score = 0
        self.getHelp = False
        self.players = pg.sprite.Group()
        self.playerMaxX = 0

        # initialize the two players
        self.giantPanda = GiantPanda('Giant Panda', self)
        self.players.add(self.giantPanda)
        self.redPanda = RedPanda('Red Panda', self)
        self.players.add(self.redPanda)

        # default direction current player is giantPanda
        self.currPlayer = self.giantPanda
        self.otherPlayer = self.redPanda

        # does not change for either current character
        self.scrollX = 0

        # for switching between players
        self.isSwitching = False
        self.otherPlayerIsOnCurr = False

        # background image is from the original Double Panda game:
        # https://www.coolmathgames.com/0-double-panda
        self.background = pg.image.load(os.path.join(imagesFolder, 'gamebackground.png')).convert()

        self.platforms = []
        self.floor = Floor(self)
        self.bamboos = []
        self.candies = []
        self.enemies = []

        # generate standard starting terrain
        self.startingTerrain()

    # generates starting terrain for every new game
    def startingTerrain(self):
        # platforms
        plat1 = Platform(self, 1, 600, 300)
        plat2 = Platform(self, 2.5, 500, 425)
        plat3 = Platform(self, 3.5, 675, 350)
        plat4 = Platform(self, 1, 1150, 300)
        self.platforms.extend([plat1, plat2, plat3, plat4])

        # bamboos
        bamboo1 = Bamboo(self, 1100)
        self.bamboos.append(bamboo1)

        # candies
        candy1 = Candy(self, 650, plat1.rect.top)
        candy2 = Candy(self, 750, plat3.rect.top)
        candy3 = Candy(self, 800, plat3.rect.top)
        candy4 = Candy(self, 850, plat3.rect.top)
        candy5 = Candy(self, 1300, plat4.rect.top)
        self.candies.extend([candy1, candy2, candy3, candy4, candy5])

        # enemies
        enemy1 = ArcherEnemy(self, plat4)
        self.enemies.append(enemy1)
        plat4.addEnemy(enemy1)

        enemy2 = BasicEnemy(self, plat2)
        self.enemies.append(enemy2)
        plat2.addEnemy(enemy2)

    # game loop
    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(fps) # standardizes fps across machines
            self.events()
            self.update()
            self.draw()

    # checks for events
    def events(self):
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                # check for jumping or climbing
                if self.isSwitching:
                    return
                if event.key == pg.K_h:
                    self.showHelpScreen()
                    return
                if event.key == pg.K_UP:
                    if self.currPlayer.name == self.redPanda.name:
                        if not self.currPlayer.atBamboo():
                            self.currPlayer.jump()
                    else:
                        self.currPlayer.jump()
                # check for switching players
                if event.key == pg.K_SPACE:
                    self.currPlayer.stop()
                    if self.currPlayer.name == self.giantPanda.name:
                        self.currPlayer = self.redPanda
                        self.otherPlayer = self.giantPanda
                    else:
                        self.currPlayer = self.giantPanda
                        self.otherPlayer = self.redPanda
                    self.isSwitching = True

    ####################################
    # Update helper methods
    ####################################

    # following function derived from makePlayerVisibile() from https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html
    # scroll to make currPlayer etc. visible as needed
    def makePlayerVisible(self):
        # cannot scroll to the left of the starting position
        centerX = screenWidth / 2
        if (self.currPlayer.rect.centerx > centerX):
            self.scrollX = self.currPlayer.rect.centerx - centerX

    # manipulates self.scrollX to bring the new currPlayer to center of canvas
    def switchTransition(self):
        leftEdgeToStartDist = screenWidth / 2
        # leftEdgeToStartDist is the distance from the left edge of the screen
        
        if (scrollSpeedWhenSwitching >= abs((self.currPlayer.rect.centerx - leftEdgeToStartDist) - self.scrollX)):
            # reached the new currPlayer
            self.scrollX = self.currPlayer.rect.centerx - leftEdgeToStartDist
            self.isSwitching = False
        elif (0 > (self.currPlayer.rect.centerx - leftEdgeToStartDist) - self.scrollX):
            # cannot scroll past the left of the starting position
            if (self.scrollX <= scrollSpeedWhenSwitching):
                self.scrollX = 0
                self.isSwitching = False
            else:
                # new currPlayer is to the left of old currPlayer
                self.scrollX -= scrollSpeedWhenSwitching
        elif (0 < (self.currPlayer.rect.centerx - leftEdgeToStartDist) - self.scrollX):
            # new currPlayer is to the right of old currPlayer
            self.scrollX += scrollSpeedWhenSwitching

    def updateEnemies(self):
        for enemy in self.enemies:
            enemy.update()

    # updates attributes
    def update(self):
        if self.giantPanda.livesLeft < 1 or self.redPanda.livesLeft < 1:
            self.playing = False
        elif self.isSwitching:
            self.switchTransition()
        else:
            self.makePlayerVisible()
            self.players.update()
            self.updateEnemies()
        
        # generate more terrain, enemies, and candy as Player moves
        if (self.platforms[-1].rect.right - self.playerMaxX < screenWidth / 2): # 400
            self.generateTerrain()

    ####################################
    # Terrain generation methods
    ####################################

    # returns list of last 5 or less platforms
    def getLastFewPlatforms(self):
        if (len(self.platforms) < 5):
            return self.platforms
        else:
            return self.platforms[-5::+1]

    # returns the furthest rect.right from the given list of platforms
    def getFurthestRight(self, platforms):
        furthestRight = 0
        for platform in platforms:
            if platform.rect.right > furthestRight:
                furthestRight = platform.rect.right
        
        furthestBambooRight = self.bamboos[-1].x + bambooWidth / 2
        if (furthestBambooRight > furthestRight):
            furthestRight = furthestBambooRight

        return furthestRight

    # generates a group of platforms with enemies, candy, and a bamboo if necessary
    def generateTerrain(self):
        # Inspired by https://youtu.be/iQXLQzOaIpE and the 15-112 Game AI TA 
        # Mini-Lecture to use probabilities (random number). From the video, 
        # I was also inspired to use a loop to generate 'terrain.'

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
        furthestRight = self.getFurthestRight(lastFewPlatforms)
        x0SetOffChoices = [100, 150, 200]
        skippedLevel = False
        
        # generate bamboo if required (too high to reach by just jumping on e/o)
        if (bottomLevel > 2):
            generatedBamboo = False

            # probability of bamboo being on the left or right
            probBambooLR = random.choice([0, 1])

            if (probBambooLR == 0): 
                # generate bamboo to the left of the group of platforms
                self.generateBamboo(furthestRight, 0)
                generatedBamboo = True
                x0SetOffChoices = [250]
        
        # generate platforms by looping from bottom to top levels
        while level <= topLevel:
            # further platforms up can be set off farther
            if (level > bottomLevel):
                x0SetOffChoices.extend([i for i in range(x0SetOffChoices[-1]+50, 401, 50)])

            # calculate x and width of new platform
            x = furthestRight + random.choice(x0SetOffChoices)
            width = random.randint(platMinLength, platMaxLength)
            
            # create new platform
            newPlatform = Platform(self, level, x, width)
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
        x = random.randint(platform.rect.left + candyWidth / 2, 
                           int(platform.rect.left + (platform.rect.right - platform.rect.left) / 2))
        # randomly choose where to start at the beginning of the platform
        x1 = random.randint(int(platform.rect.left + (platform.rect.right - platform.rect.left) / 2), 
                            platform.rect.right - candyWidth)
        
        # there should only be one on a platform at a time
        # only red panda can eat fried rice
        madeFriedRice = False

        # loop through the length of the platform
        while (x < x1):
            newCandy = Candy(self, x, platform.rect.top)

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
            x += candyWidth + 20

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
        platformLength = platform.rect.width
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
                newEnemy = BasicEnemy(self, platform)
            else:
                if (topLevel - platform.level < 1):
                    # archer enemies should only appear on the top level to be
                    # able to be killed
                    newEnemy = ArcherEnemy(self, platform)
                else:
                    newEnemy = BasicEnemy(self, platform)

            self.enemies.append(newEnemy)
            platform.addEnemy(newEnemy)

            enemyCount -= 1

    # generate one bamboo next to a group of platforms that requires it
    def generateBamboo(self, furthestRight, levelCount):
        # Inspired by https://youtu.be/iQXLQzOaIpE and Game AI TA Mini-Lecture
        # to use probabilities (random number).

        if (furthestRight != 0):
            # this means that the bamboo is to the left of the platforms
            xSetOff = random.randint(130, 150)
            newBamboo = Bamboo(self, xSetOff + furthestRight)
        elif (levelCount != 0):
            # this means that the bamboo is to the right of the platforms

            # find furthest x1
            furthestRight = 0
            furthestPlatform = self.platforms[-1]
            for i in range(-1, levelCount * -1 - 1, -1):
                right = self.platforms[i].rect.right
                if (right > furthestRight):
                    furthestRight = right
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
            newBamboo = Bamboo(self, xSetOff + furthestRight)

        self.bamboos.append(newBamboo)

    ####################################
    # Draw methods
    ####################################

    def drawPlatforms(self):
        for plat in self.platforms:
            plat.draw()

    def drawBamboos(self):
        for bamboo in self.bamboos:
            bamboo.draw()

    def drawCandies(self):
        for candy in self.candies:
            candy.draw()

    def drawEnemies(self):
        for enemy in self.enemies:
            enemy.draw()

    def drawScore(self):
        self.drawText('Lives Left', 15, white, 8, screenHeight - 69, 'left')
        self.drawText(f'Giant Panda: {self.giantPanda.livesLeft}', 15, white, 8, screenHeight - 46, 'left')
        self.drawText(f'Red Panda: {self.redPanda.livesLeft}', 15, white, 8, screenHeight - 23, 'left')
        self.drawText(f'Score: {self.score}', 15, white, screenWidth - 6, screenHeight - 23, 'right')

    # draw next screen
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.floor.draw()
        self.drawPlatforms()
        self.drawBamboos()
        self.drawCandies()
        self.drawEnemies()
        self.drawScore()
        self.otherPlayer.draw()
        self.currPlayer.draw()

        # after drawing everything, flip the display
        pg.display.flip()

    # game splash/start/intro screen
    def showIntroScreen(self):
        # intro image contains images from the original Double Panda game:
        # https://www.coolmathgames.com/0-double-panda
        image = pg.image.load(os.path.join(imagesFolder, 'intro.png')).convert()
        self.screen.blit(image, (0, 0))
        pg.display.flip()
        self.waitForKeyPress()

    # instructions screen
    def showHelpScreen(self):
        # instructions image contains images from the original Double Panda game:
        # https://www.coolmathgames.com/0-double-panda
        image = pg.image.load(os.path.join(imagesFolder, 'instructions.png')).convert()
        self.screen.blit(image, (0, 0))
        pg.display.flip()
        self.waitForKeyPress()

    # game over screen
    def showGameOverScreen(self):
        # game over image contains images from the original Double Panda game:
        # https://www.coolmathgames.com/0-double-panda
        if not self.running:
            return
        image = pg.image.load(os.path.join(imagesFolder, 'gameover.png')).convert()
        self.screen.blit(image, (0, 0))
        self.drawText(f'{self.score}', 20, tan, 410, 367, 'left')
        pg.display.flip()
        self.waitForKeyPress()

    # needs citation
    def waitForKeyPress(self):
        waiting = True
        while waiting:
            self.clock.tick(fps)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYDOWN:
                    waiting = False

    def drawText(self, text, size, color, x, y, align):
        font = pg.font.SysFont('helvetica', size)
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if align == 'left':
            rect.left = x
            rect.y = y
        elif align == 'right':
            rect.right = x
            rect.y = y
        self.screen.blit(surface, rect)

g = Game()
g.showIntroScreen()
g.showHelpScreen()
while g.running:
    g.new()
    g.run()
    g.showGameOverScreen()
pg.quit()