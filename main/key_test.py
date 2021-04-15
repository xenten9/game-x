from engine.engine import GameHandler
from pygame import event as pyevent
from os import path
from pygame.locals import QUIT
from pygame.locals import (KEYUP, KEYDOWN, MOUSEBUTTONDOWN,
                           MOUSEBUTTONUP, MOUSEMOTION)

PATH = {}
PATH['DEFAULT'] = __file__[:-len(path.basename(__file__))]
PATH['ASSETS'] = path.join(PATH['DEFAULT'], 'assets')
PATH['SPRITES'] = path.join(PATH['ASSETS'], 'sprites')
PATH['LEVELS'] = path.join(PATH['ASSETS'], 'levels')
PATH['TILEMAPS'] = path.join(PATH['ASSETS'], 'tilemaps')

SIZE = (480, 320)

GAME = GameHandler(SIZE, 32, PATH, None)

def main():
    """Main game loop."""
    while GAME.run:
        GAME.input.reset()

        # Event Handler
        for event in pyevent.get():
            # Exit game
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                print(event.scancode)

        # Quit by escape
        if GAME.input.kb.get_key_pressed(41):
            GAME.end()
            return


if __name__ == '__main__':
    main()
