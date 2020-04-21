from flappy import *


class Bird:
    def __init__(self):
        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        self.images = (
            IMAGES['player'][randPlayer][0],
            IMAGES['player'][randPlayer][1],
            IMAGES['player'][randPlayer][2],
        )

        self.playerIndexGen = cycle([0, 1, 2, 1])
        self.playerx, self.playery = int(SCREENWIDTH * 0.2), int((SCREENHEIGHT - self.images[0].get_height()) / 2)

        # player velocity, max velocity, downward accleration, accleration on flap
        self.playerVelY = -9  # player's velocity along Y, default same as playerFlapped
        self.playerMaxVelY = 10  # max vel along Y, max descend speed
        self.playerMinVelY = -8  # min vel along Y, max ascend speed
        self.playerAccY = 1  # players downward accleration
        self.playerRot = 45  # player's rotation
        self.playerVelRot = 3  # angular speed
        self.playerRotThr = 20  # rotation threshold
        self.playerFlapAcc = -9  # players speed on flapping
        self.playerFlapped = False  # True when player flaps

        self.score = 0
        self.playerIndex = self.loopIter = 0

    def order_flap(self):
        if self.playery > -2 * self.images[0].get_height():
            self.playerVelY = self.playerFlapAcc
            self.playerFlapped = True
            SOUNDS['wing'].play()

    # returns if bird has crashed
    def update(self, upperPipes, lowerPipes):
        # check for crash here
        crashTest = checkCrash(self, upperPipes, lowerPipes)

        if crashTest[0]:
            # play hit and die sounds
            SOUNDS['hit'].play()
            if not crashTest[1]:
                SOUNDS['die'].play()
            return crashTest

        # check for score
        playerMidPos = self.playerx + self.images[0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                self.score += 1

        if (self.loopIter + 1) % 3 == 0:
            self.playerIndex = next(self.playerIndexGen)
        self.loopIter = (self.loopIter + 1) % 30

        # rotate the player
        if self.playerRot > -90:
            self.playerRot -= self.playerVelRot

        # player's movement
        if self.playerVelY < self.playerMaxVelY and not self.playerFlapped:
            self.playerVelY += self.playerAccY
        if self.playerFlapped:
            self.playerFlapped = False
            self.playerRot = 45  # more rotation to cover the threshold (calculated in visible rotation)

        playerHeight = self.images[self.playerIndex].get_height()
        self.playery += min(self.playerVelY, BASEY - self.playery - playerHeight)
        return False, False  # keep bird, it did not crash

    def blit(self, screen):
        # Player rotation has a threshold
        visibleRot = self.playerRotThr
        if self.playerRot <= self.playerRotThr:
            visibleRot = self.playerRot

        playerSurface = pygame.transform.rotate(self.images[self.playerIndex], visibleRot)
        screen.blit(playerSurface, (self.playerx, self.playery))

    def think(self):
        pass
