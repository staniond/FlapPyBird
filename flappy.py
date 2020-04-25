from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *

from globals import *
from evolution import *


def main():
    global SCREEN, FPSCLOCK, FPS
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Flappy Bird')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    IMAGES['player'] = (
        # red bird
        (
            pygame.image.load(PLAYERS_LIST[0][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[0][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[0][2]).convert_alpha(),
        ),
        # blue bird
        (
            pygame.image.load(PLAYERS_LIST[1][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[1][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[1][2]).convert_alpha(),
        ),
        # yellow bird
        (
            pygame.image.load(PLAYERS_LIST[2][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[2][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[2][2]).convert_alpha(),
        ),
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die'] = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit'] = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point'] = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing'] = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    evolution = Evolution(POPULATION_SIZE)

    show_welcome = True
    show_best_bird = False
    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), False, True),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(pygame.image.load(PLAYERS_LIST[0][0]).convert_alpha()),
            getHitmask(pygame.image.load(PLAYERS_LIST[0][1]).convert_alpha()),
            getHitmask(pygame.image.load(PLAYERS_LIST[0][2]).convert_alpha()),
        )

        if show_welcome:
            show_welcome = False
            showWelcomeAnimation()

        skip_game_over, crashInfo = mainGame(evolution, show_best_bird)

        if not show_best_bird:
            evolution.new_population()

        if not skip_game_over:
            show_best_bird = showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    """Shows welcome screen animation of flappy bird"""
    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            # any key
            if event.type == KEYDOWN:
                # make first flap sound and return values for mainGame
                # SOUNDS['wing'].play()
                return

        basex = -((-basex + 4) % baseShift)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(evolution, show_best_bird):
    birds = [Bird(evolution.best_brain.clone())] if show_best_bird else evolution.population
    score = 0

    basex = 0
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [newPipe1[0], newPipe2[0]]
    upperPipes[0]['x'] = SCREENWIDTH + 200
    upperPipes[1]['x'] = SCREENWIDTH + 200 + (SCREENWIDTH / 2)

    # list of lowerpipe
    lowerPipes = [newPipe1[1], newPipe2[1]]
    lowerPipes[0]['x'] = SCREENWIDTH + 200
    lowerPipes[1]['x'] = SCREENWIDTH + 200 + (SCREENWIDTH / 2)

    pipeVelX = -4

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_s:
                return_val = False, {
                    'groundCrash': False,
                    'basex': basex,
                    'upperPipes': upperPipes,
                    'lowerPipes': lowerPipes,
                    'score': score,
                    'lastBird': birds[0]
                }
                if show_best_bird:
                    return return_val
                else:
                    for bird in birds:
                        evolution.previous_population.append(bird)
                    return return_val
            # if event.type == KEYDOWN and event.key == K_UP:
            #     birds[0].flap()

        for bird in birds:
            bird.think(upperPipes, lowerPipes)

        # update birds and remove crashed ones
        for bird in list(birds):
            crashed, groundCrash = bird.update(upperPipes, lowerPipes)
            if crashed:
                if not show_best_bird:
                    evolution.previous_population.append(bird)
                if len(birds) == 1:  # we have a last bird that crashed, end of generation
                    return True, {
                        'groundCrash': groundCrash,
                        'basex': basex,
                        'upperPipes': upperPipes,
                        'lowerPipes': lowerPipes,
                        'score': score,
                        'lastBird': birds[0]
                    }
                else:
                    birds.remove(bird)

        # play sound if birds are in the middle of a pipe
        playerMidPos = birds[0].playerx + birds[0].images[0].get_width() / 2  # arbitrary bird,all x coords are the same
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                # SOUNDS['point'].play()
                score += 1

        # basex change
        basex = -((-basex + 100) % baseShift)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if len(upperPipes) > 0 and 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if len(upperPipes) > 0 and upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(score)

        for bird in birds:
            bird.blit(SCREEN)

        pygame.display.update()
        FPSCLOCK.tick(FPS if show_best_bird else -1)


def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    bird = crashInfo['lastBird']
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playerHeight = bird.images[0].get_height()
    playerAccY = 2
    playerVelRot = 7
    basex = crashInfo['basex']
    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_n:
                return False
            if event.type == KEYDOWN and event.key == K_b:
                return True

        # player y shift
        if bird.playery + playerHeight < BASEY - 1:
            bird.playery += min(bird.playerVelY, BASEY - bird.playery - playerHeight)

        # player velocity change
        if bird.playerVelY < 15:
            bird.playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:
            if bird.playerRot > -90:
                bird.playerRot -= playerVelRot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        playerSurface = pygame.transform.rotate(bird.images[1], bird.playerRot)
        SCREEN.blit(playerSurface, (playerx, bird.playery))
        SCREEN.blit(IMAGES['gameover'], (50, 180))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
        playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight, 'gap': gapY},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE, 'gap': gapY + PIPEGAPSIZE},  # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0  # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player.playerIndex
    playerWidth = player.images[0].get_width()
    playerHeight = player.images[0].get_height()

    # if player crashes into ground
    if player.playery + playerHeight >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player.playerx, player.playery, playerWidth, playerHeight)
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False


def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


if __name__ == '__main__':
    main()
