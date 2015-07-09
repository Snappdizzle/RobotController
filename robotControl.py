import pygame
from pygame.locals import *
from robot import Robot
import time
class RobotControl(object):


    def __init__(self, robot):
        self.robot = robot
        self.exit = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.pan_head = 0
        self.tilt_head = 0
        self.screen = None

    def start(self):
         '''This class add keyboard and mouse control logic to a robot'''
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
                self.handleKeyEvent(event)
                self.handleMouseEvent(event)
                self.robot.send_cmd_set()
            self.draw_screen()

    def handleKeyEvent(self, event):
        acc_linear = 50.0
        acc_angular = 12.0
        if (event.type == KEYUP) or (event.type == KEYDOWN):
            #print event
            if (event.key == K_ESCAPE):
                self.exit = True
            elif event.key == K_a:
                if (event.type == KEYDOWN):
                    self.robot.lin_ang_body(100, -6, acc_linear, acc_angular)
                elif (event.type == KEYUP):
                    self.robot.lin_ang_body(0, 0, 0, 0)
            elif event.key == K_d:
                if (event.type == KEYDOWN):
                    self.robot.lin_ang_body(100, 6, acc_linear, acc_angular)
                elif (event.type == KEYUP):
                    self.robot.lin_ang_body(0, 0, 0, 0)
            elif event.key == K_w:
                if (event.type == KEYDOWN):
                    self.robot.lin_ang_body(100, 0, acc_linear, acc_angular)
                elif (event.type == KEYUP):
                    self.robot.lin_ang_body(0, 0, 0, 0)
            elif event.key == K_s:
                if (event.type == KEYDOWN):
                    self.robot.lin_ang_body(-100, 0, acc_linear, acc_angular)
                elif (event.type == KEYUP):
                    self.robot.lin_ang_body(0, 0, 0, 0)
            elif event.key == K_SPACE:
                print "Spacebar detected..."
                if (event.type == KEYDOWN):
                    self.robot.set_chest_rgb(1, 0, 0)
                    self.robot.set_left_ear_rgb(1, 0, 0)
                    self.robot.set_right_ear_rgb(1, 0, 0)
                elif (event.type == KEYUP):
                    self.robot.set_chest_rgb(0, 1, 0)
                    self.robot.set_left_ear_rgb(0, 1, 0)
                    self.robot.set_right_ear_rgb(0, 1, 0)
            elif event.key == K_f:
                if (event.type == KEYUP):
                    pygame.display.toggle_fullscreen()

    def draw_screen(self):
        basicFont = pygame.font.SysFont(None, 48)
        text = "(%d, %d)" % (self.last_mouse_x, self.last_mouse_y)
        surface = basicFont.render(text, True, (255, 255, 255))
        surfacerect = surface.get_rect()
        surfacerect.centerx = self.screen.get_rect().centerx
        surfacerect.centery = self.screen.get_rect().centery
        self.screen.fill((41, 221, 253))
        self.screen.blit(surface, surfacerect)
        pygame.display.update()

    def handleMouseEvent(self, event):
        if event.type == pygame.MOUSEMOTION:
            #print event.pos
            x = event.pos[0]
            y = event.pos[1]
            tilt_incr = 2
            pan_incr = 2

            if self.last_mouse_x > x:
                print "MOVING LEFT"
                self.pan_head = max(self.robot.MIN_HEAD_PAN, self.pan_head - pan_incr)
            elif self.last_mouse_x < x:
                print "MOVING RIGHT"
                self.pan_head = min(self.robot.MAX_HEAD_PAN, self.pan_head + pan_incr)

            if self.last_mouse_y < y:
                print"MOVING UP"
                self.tilt_head = min(self.robot.MAX_HEAD_TILT, self.tilt_head + tilt_incr)
            elif self.last_mouse_y > y:
                print "MOVING DOWN"
                self.tilt_head = max(self.robot.MIN_HEAD_TILT, self.tilt_head - tilt_incr)

            self.last_mouse_x = x
            self.last_mouse_y = y
            self.robot.pan_head(self.pan_head)
            self.robot.tilt_head(self.tilt_head)
