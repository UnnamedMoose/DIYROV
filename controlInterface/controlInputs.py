# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 20:28:58 2015

@author: artur
"""

import pygame


pygame.init()
print "Joystics: ", pygame.joystick.get_count()
print "Mouses: ", pygame.mouse
my_joystick = pygame.joystick.Joystick(0)
my_joystick.init()
clock = pygame.time.Clock()

while 1:
    for event in pygame.event.get():
        print my_joystick.get_axis(0),  my_joystick.get_axis(1) 
        clock.tick(40)

pygame.quit ()