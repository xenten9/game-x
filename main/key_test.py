from Helper_Functions.inputs import ObjKeyboard
import pygame
import ast

TILESIZE = 32

# Handles graphics
class Window():
    """Handles graphics."""
    def __init__(self, width: int, height: int):
        self.display = pygame.display.set_mode((width, height))
        self.height, self.height = width, height

run = 1
WIN = Window(400, 300)
while run == 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = 0
        if event.type == pygame.KEYDOWN:
            print(event.scancode)
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(event.button)