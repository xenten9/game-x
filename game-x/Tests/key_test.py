from inputs import ObjKeyboard
import pygame
from game import Window
import ast

run = 1
WIN = Window(400, 300)
while run == 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = 0
        if event.type == pygame.KEYDOWN:
            print(event.scancode)