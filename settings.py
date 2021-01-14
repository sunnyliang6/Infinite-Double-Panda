####################################
# This game is based on the original Double Panda game: 
# https://www.coolmathgames.com/0-double-panda
####################################

####################################
# This file contains basic settings for the game.
####################################

import os

# display
title = "Infinite Double Panda"
screenWidth = 800
screenHeight = 600
fps = 30
floorLevel = 475
edgeLimit = 10
scrollSpeedWhenSwitching = 10

# set up assets folders
gameFolder = os.path.dirname(__file__) # __file__ is the location of this file
imagesFolder = os.path.join(gameFolder, 'images')

# color rgbs
black = (0, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
tan = (186, 96, 3)

# game properties
playerLayer = 2 # controls order to draw allSprites
enemyLayer = 2
terrainLayer = 1

# player properties
gpStartingX = 250
rpStartingX = 180
playerWidth = 50
playerHeight = 56
playerAcc = 1.0
playerGravity = 0.8
playerFriction = -0.15 # affects maximum speed and time it takes to stop mvt
playerJumpVel = 12
playerClimbVel = 4
playerCollisionSetOff = 6
playerFeetX = 15
livesLeft = 5
playerRepeatSprite = 3
playerNumSprites = 6

# enemy properties
enemyWidth = 50
enemyHeight = 56
enemyWalkVel = 1
enemyRepeatSprite = 3
enemyNumSprites = 6
enemyShootVel = 8
enemyShootWaitTime = 3000

# terrain properties
levelHeight = playerHeight + 15
platMinLength = 125
platMaxLength = 450
platHeight = 20
bambooWidth = 30
candyWidth = 40