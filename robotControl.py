import pygame
from pygame.locals import *
from robot import Robot
import time
import logging
"""Imports all important files and systems"""

FORMAT = '[%(levelname)5s] %(asctime)-15s %(filename)s:%(lineno)d %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('robot_control')
logger.setLevel(logging.ERROR)

class RobotControl(object):

    def __init__(self, robot):
        self.robot = robot
        self.exit = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.pan_head = 0
        self.tilt_head = 0
        self.screen = None
        self.key_state = {K_d : False, K_s : False, K_a : False, K_w : False, K_SPACE : False}
        self.left_whl_velo = 0
        self.right_whl_velo = 0
        self.TANK_WHEEL_VELO = 100


    def start(self):
        """start function that opens pygame window."""
        pygame.init()
        s_width = 1360
        s_height = 768 #int((9.0/16.0)  * s_width)
        self.screen = pygame.display.set_mode((s_width, s_height))
        pygame.display.set_caption('Robot Control')
        pygame.mouse.set_visible(1)

        done = False
        prev_x = 0
        prev_y = 0
        while not self.exit:
            for event in pygame.event.get():
                if event.type in [MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
                    self.handleMouseEvent(event)

                if event.type in [KEYUP, KEYDOWN]:
                    """looks for actions in the keyboard and handles them e.g. Spacebar == turn ears red."""
                    self.doAuxKeys(event)
                    self.doLinAngKeys(event)
                    self.doTankKeys(event)

            self.robot.send_cmd_set()
            self.draw_screen()
            pygame.time.wait(30)



    def doTankKeys(self, event):
        """Function holding values for u, o, j, & l keys. valeus are set_speed of wheels."""
        tank_key_pressed = False
        if event.key == K_u :
            tank_key_pressed = True
            if event.type == KEYDOWN:
                self.left_whl_velo = self.TANK_WHEEL_VELO
                logger.debug('JUST SET THE LEFT WHEEL TO: %d', self.left_whl_velo)
            else:
                self.left_whl_velo = 0
                logger.debug('JUST UNSET THE LEFT WHEEL TO: %d', self.left_whl_velo)

        if event.key == K_j :
            tank_key_pressed = True
            if event.type == KEYDOWN:
                self.left_whl_velo = -1 * self.TANK_WHEEL_VELO
            else:
                self.left_whl_velo = 0
        if event.key == K_o :
            tank_key_pressed = True
            if event.type == KEYDOWN:
                self.right_whl_velo = self.TANK_WHEEL_VELO
                logger.debug("The current wheel speed of o: %d", self.right_whl_velo)
            else:
                self.right_whl_velo = 0


        if event.key == K_l :
            tank_key_pressed = True
            if event.type == KEYDOWN:
                self.right_whl_velo = -1 * self.TANK_WHEEL_VELO
            else:
                self.right_whl_velo = 0

        logger.debug("key: %d  type: %d   left_whl_velo: %d  right_whl_velo: %d", event.key, event.type, self.left_whl_velo, self.right_whl_velo)
        if tank_key_pressed:
            self.robot.set_wheels(self.left_whl_velo, self.right_whl_velo)



    def doLinAngKeys(self, event):
        """Function that holds values of keys: W, A, S, & D, values are lin_ang_body: speed of wheels and turn intensity."""
        acc_linear = 50
        acc_angular = 250
        logger.debug(event)
        self.key_state[event.key] = (event.type == KEYDOWN)

        evtWasLinAngKey = event.key in [K_a, K_d, K_s, K_w]
        a = self.key_state[K_a]
        s = self.key_state[K_s]
        w = self.key_state[K_w]
        d = self.key_state[K_d]

        result = (0, 0)
        back = (-100, 0)
        fwd = (100, 0)

        if a and d:
            # ignore a and d if they are both pressed
            if w:
                result = fwd
            elif s:
                result = back
        elif w and d:
            result = (100, -2)
        elif w and a:
            result = (100, 2)
        elif s and a:
            result = (-100, 2)
        elif s and d:
            result = (-100, -2)
        elif d:
            result = (100, -4)
        elif s:
            result = back
        elif w:
            result = fwd
        elif a:
            result = (100, 4)

        if evtWasLinAngKey:
            self.robot.lin_ang_body(result[0], result[1], acc_linear, acc_angular)


    def doAuxKeys(self, event):
        if (event.key == K_SPACE):
            if event.type == KEYDOWN:
                self.robot.set_left_ear_rgb(1, 0, 0)
                self.robot.set_right_ear_rgb(1, 0, 0)
                self.robot.set_chest_rgb(1, 0, 0)
            elif event.type == KEYUP:
                self.robot.set_left_ear_rgb(0, 1, 0)
                self.robot.set_right_ear_rgb(0, 1, 0)
                self.robot.set_chest_rgb(0, 1, 0)
        if (event.key == K_ESCAPE):
            self.exit = True
        if event.key == K_f:
            if (event.type == KEYUP):
                pygame.display.toggle_fullscreen()
        if event.key == K_c:
            if (event.type == KEYUP):
                pygame.mouse.set_pos([self.centerScreenX(), self.centerScreenY()])
                pygame.mouse.set_pos([self.centerScreenX(), self.centerScreenY()])
                self.tilt_head = 0
                self.pan_head = 0


    def draw_screen(self):
        """unction that draws objeects and text on the screen."""
        basicFont = pygame.font.SysFont(None, 48) #Coordinates
        text = "(%d, %d)" % (self.last_mouse_x, self.last_mouse_y)
        surface = basicFont.render(text, True, (255, 255, 255))
        surfacerect = surface.get_rect()
        surfacerect.centerx = self.screen.get_rect().centerx
        surfacerect.centery = self.screen.get_rect().centery
        self.screen.fill((255, 135, 34))
        self.screen.blit(surface, surfacerect)

        font = pygame.font.SysFont("Helvetica", 48) #Robot Name
        text_surface = font.render(self.robot.name, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (997.5, 719)
        self.screen.blit(text_surface, text_rect)

        #buttons draw
        if self.robot.isButton1Pressed == True:
            pygame.draw.circle(self.screen, (36, 255, 97), (135, 250), 15)
        if self.robot.isButton2Pressed == True:
            pygame.draw.circle(self.screen, (36, 255, 97), (265, 250), 15)
        if self.robot.isButton3Pressed == True:
            pygame.draw.circle(self.screen, (36, 255, 97), (200, 135), 15)
        if self.robot.isButtonMainPressed == True:
            pygame.draw.circle(self.screen, (36, 255, 97), (200, 200), 30)
        pygame.draw.circle(self.screen, (255, 255, 255), (200, 200), 30)
        pygame.draw.circle(self.screen, (255, 255, 255), (135, 250), 15)
        pygame.draw.circle(self.screen, (255, 255, 255), (265, 250), 15)
        pygame.draw.circle(self.screen, (255, 255, 255), (200, 135), 15)


        pygame.draw.circle(self.screen, (0, 0, 0), (1000, 450), 104) #Robot Pic
        pygame.draw.circle(self.screen, (0, 0, 0), (905, 600), 104)
        pygame.draw.circle(self.screen, (0, 0, 0), (1080, 600), 104)
        pygame.draw.circle(self.screen, (0, 205, 253), (1000, 450), 100)
        pygame.draw.circle(self.screen, (0, 205, 253), (905, 600), 100)
        pygame.draw.circle(self.screen, (0, 205, 253), (1080, 600), 100)

        pygame.draw.circle(self.screen, (255, 135, 34), (1000, 450), 65)
        pygame.draw.circle(self.screen, (255, 255, 255), (1000, 450), 50)
        pygame.draw.circle(self.screen, (0, 0, 0), (1000, 450), 20)
        pygame.draw.polygon(self.screen, (0, 0, 0), [(965, 530), (1030, 530), (997.5, 575)])
        pygame.draw.polygon(self.screen, (36, 255, 97), [(980, 535), (1015, 535), (997.5, 565)])

        pygame.display.update()

    def handleMouseEvent(self, event):
        """If mouse does action call it and push it to a command set"""
        logger.debug("looking at event: %s", event)
        #print event.pos
        x = event.pos[0]
        y = event.pos[1]
        tilt_incr = 2
        pan_incr = 2

        if self.last_mouse_x > x:
            print "MOVING LEFT"
            self.pan_head = max(self.robot.MIN_HEAD_PAN, self.pan_head + pan_incr)
        elif self.last_mouse_x < x:
            print "MOVING RIGHT"
            self.pan_head = min(self.robot.MAX_HEAD_PAN, self.pan_head - pan_incr)

        if self.last_mouse_y < y:
            print"MOVING UP"
            self.tilt_head = min(self.robot.MAX_HEAD_TILT, self.tilt_head + tilt_incr)
        elif self.last_mouse_y > y:
            print "MOVING DOWN"
            self.tilt_head = max(self.robot.MIN_HEAD_TILT, self.tilt_head - tilt_incr)

        """eye_on = event.buttons[0] == 0"""
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.robot.set_eye(False)
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.robot.set_eye(True)

        self.last_mouse_x = x
        self.last_mouse_y = y
        self.robot.pan_head(self.pan_head)
        self.robot.tilt_head(self.tilt_head)


    def centerScreenX(self):
        return self.getScreenRect().centerx

    def centerScreenY(self):
        return self.getScreenRect().centery

    def getScreenRect(self):
        return self.screen.get_rect()
