from flappy import *
from birdbrain import BirdBrain


class Bird:
    def __init__(self, brain=None):
        self.brain = brain if brain is not None else BirdBrain()

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

        self.fitness = 0
        self.playerIndex = self.loopIter = 0

    def think(self, upperPipes, lowerPipes):
        output = self.brain.forward(self.get_world_data(upperPipes, lowerPipes))
        if output[0] > output[1]:
            self.flap()

    def flap(self):
        if self.playery > -2 * self.images[0].get_height():
            self.playerVelY = self.playerFlapAcc
            self.playerFlapped = True
            # SOUNDS['wing'].play()

    # returns if bird has crashed
    def update(self, upperPipes, lowerPipes):
        # check for crash here
        crashTest = checkCrash(self, upperPipes, lowerPipes)

        if crashTest[0]:
            if not crashTest[1]:  # crash into pipe, get fitness if close to gap
                pipe_index = self.get_closest_pipe(upperPipes)
                middle_gap = upperPipes[pipe_index]['gap'] + PIPEGAPSIZE / 2
                self.fitness -= abs(middle_gap - (self.playery + self.images[0].get_height() / 2)) // 20
            else:
                self.fitness -= 15  # about max penalization for crashing into pipe - crashing into ground is even worse
            # play hit and die sounds
            # SOUNDS['hit'].play()
            # if not crashTest[1]:
            #     SOUNDS['die'].play()
            return crashTest
        else:
            self.fitness += 1

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

    # gets normalized (to <0, 1>) data for bird's neural network input
    def get_world_data(self, upperPipes, lowerPipes):
        closest_index = self.get_closest_pipe(upperPipes)
        return [
            self.playery / BASEY,  # bird y location
            (self.playerVelY / self.playerMaxVelY) / 2 + .5,  # bird y velocity
            # pipe x location
            (upperPipes[closest_index]['x'] + IMAGES['pipe'][0].get_width() - self.playerx) / 150,
            upperPipes[closest_index]['gap'] / BASEY,  # closest upper pipe y location
            lowerPipes[closest_index]['gap'] / BASEY,  # closest lower pipe y location
            (upperPipes[closest_index + 1]['gap'] + PIPEGAPSIZE / 2) / BASEY,  # next upper pipe y location
        ]

    def get_closest_pipe(self, pipes):
        for i, pipe in enumerate(pipes):
            if pipe['x'] + IMAGES['pipe'][0].get_width() > self.playerx:
                return i
