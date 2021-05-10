from math import floor

from ..engine.engine import Engine
from ..engine.components.draw import Draw
from ..engine.components.menu import Menu, MenuElement
from ..engine.components.menu import MenuText, MenuRect
from ..engine.components.menu import MenuButtonFull
from ..engine.types.vector import vec2d
from .constants import SIZE
from ..engine.components.maths import f_limit

# Entities
class Entity():
    """Base class for all game entities."""
    def __init__(self, engine: Engine):
        self.engine = engine

    def post_init(self):
        pass

    def update_early(self, pause: bool):
        """Update called first."""
        pass

    def update(self, pause: bool):
        """Update called second."""
        pass

    def update_late(self, pause: bool):
        """Update called last."""
        pass

    def draw(self, draw: Draw):
        """Draw called in between back and foreground."""
        pass

class ObjJukeBox(Entity):
    """Responsible for sick beats."""
    def __init__(self, engine: Engine, key: int, name: str, data: dict):
        super().__init__(engine)
        engine.obj.instantiate_object(key, self)
        self.key = key
        self.name = name
        self.data = data

        # Music vars
        current_music = engine.aud.music.get_current()
        self.music = data['name']
        self.loops = data['loops']
        self.volume = data['volume']

        if self.music is not None: # Add new music
            if current_music is None: # Start playing music
                engine.aud.music.load(self.music)
                engine.aud.music.set_volume(self.volume)
                engine.aud.music.play(self.loops)

            elif current_music != self.music: # Queue up music
                engine.aud.music.stop(1500)
                engine.aud.music.queue(self.music, self.loops, self.volume)

        elif current_music is not None: # Fade music
            engine.aud.music.stop(1000)

    def update(self, paused: bool):
        if paused:
            self.engine.aud.music.set_volume(self.volume / 4)
        else:
            self.engine.aud.music.set_volume(self.volume)

class ObjMainMenu(Entity):
    def __init__(self, engine: Engine, key: int, name: str, data: dict):
        engine.obj.instantiate_object(key, self)
        super().__init__(engine)
        self.key = key
        self.name = name
        self.data = data
        self.engine.cam.pos = vec2d(0, 0)

        # Title menu
        self.title_menu = Menu(engine, SIZE)

        # TITLE
        title = MenuText(engine, self.title_menu, 'title')
        title.size = 36
        title.color = (144, 240, 240)
        title.text = 'Game-X: Now with depth!'
        title.pos = SIZE / 2
        title.font = 'consolas'
        title.center = 5

        # START BUTTON
        start_button = MenuButtonFull(engine, self.title_menu, 'start-button')
        start_button.size = vec2d(128, 32)
        start_button.pos = SIZE / 2 + vec2d(0, 32)
        start_button.center = 5

        start_button.text.color = (128, 200, 200)
        start_button.text.text = 'Start'
        start_button.text.font = 'consolas'
        start_button.text.depth = 16

        start_button.button.call = self.pressed

        # OPTION BUTTON
        option_button = MenuButtonFull(engine, self.title_menu, 'option-button')
        option_button.size = vec2d(128, 32)
        option_button.pos = SIZE/2 + vec2d(0, 64)
        option_button.center = 5

        option_button.text.color = (128, 200, 200)
        option_button.text.text = 'Options'
        option_button.text.font = 'consolas'
        option_button.text.depth = 16

        option_button.button.call = self.pressed

        # QUIT BUTTON
        quit_button = MenuButtonFull(engine, self.title_menu, 'quit-button')
        quit_button.size = vec2d(128, 32)
        quit_button.pos = SIZE/2 + vec2d(0, 96)
        quit_button.center = 5

        quit_button.text.color = (128, 200, 200)
        quit_button.text.text = 'Quit'
        quit_button.text.font = 'consolas'
        quit_button.text.depth = 16

        quit_button.button.call = self.pressed

        # Option menu
        self.option_menu = Menu(self.engine, SIZE)
        self.option_menu.visible = False

        # TITLE
        title = MenuText(engine, self.option_menu, 'title')
        title.size = 24
        title.pos = SIZE / 2
        title.text = 'Options:'
        title.center = 5

        # VOLUME SLIDER
        #slider_rect = MenuRect(self.option_menu, 'slider-rect')
        #size = vec2d(100, 24)
        #pos += vec2d(-50, 12)
        #color = (64, 64, 64)
        #slider_rect.set_vars(size=size, pos=pos, color=color)

        #slider_button = MenuButton(self.option_menu, 'slider-button')
        #slider_button.set_vars(size=size, pos=pos, call=call, held=True)

        # RETURN Button
        return_button = MenuButtonFull(engine, self.option_menu, 'return-button')
        return_button.pos = SIZE/2 + vec2d(0, 128)
        return_button.center = 5
        return_button.size = vec2d(128, 24)

        return_button.text.text = 'Return'
        return_button.text.color = (128, 128, 128)
        return_button.text.depth = 16

        return_button.button.call = self.pressed

    def update(self, pause: bool):
        self.title_menu.get('start-button').update()
        self.title_menu.get('option-button').update()
        self.title_menu.get('quit-button').update()
        #self.option_menu.get('slider-button').update()
        self.option_menu.get('return-button').update()

    def draw(self, draw: Draw):
        self.title_menu.draw(draw)
        self.option_menu.draw(draw)

    def pressed(self, element: MenuElement, pos: vec2d):
        if element.name == 'start-button-button':
            self.engine.lvl.load('level1')
        elif element.name == 'option-button-button':
            self.title_menu.visible = False
            self.option_menu.visible = True
        elif element.name == 'return-button-button':
            self.title_menu.visible = True
            self.option_menu.visible = False
        elif element.name == 'quit-button-button':
            self.engine.end()
        if element.name == 'slider-button':
            x = floor(pos.x)
            x = f_limit(x, 0, 100)
            size = vec2d(x, 24)
            self.option_menu.get('slider-rect').set_vars(size=size)

class ObjPauseMenu(Entity):
    def __init__(self, engine: Engine, key: int, name: str, data:dict):
        engine.obj.instantiate_object(key, self)
        super().__init__(engine)
        self.key = key
        self.name = name
        self.data = data

        # Title menu
        self.menu = Menu(engine, SIZE)

        # BACKGROUND
        background = MenuRect(engine, self.menu, 'background')
        background.size = SIZE
        background.color = (0, 0, 0, 223)
        background.depth = 8
        background.center = 7

        # TITLE
        title = MenuText(engine, self.menu, 'title')
        title.size = 36
        title.color = (144, 240, 240)
        title.text = 'Paused'
        title.pos = SIZE / 2
        title.font = 'consolas'
        title.center = 5

        # START BUTTON
        resume = MenuButtonFull(engine, self.menu, 'resume')
        resume.size = vec2d(128, 32)
        resume.pos = SIZE / 2 + vec2d(0, 32)
        resume.center = 5

        resume.text.color = (128, 200, 200)
        resume.text.text = 'Resume'
        resume.text.font = 'consolas'
        resume.text.depth = 16

        resume.button.call = self.pressed

        # OPTION BUTTON
        reset = MenuButtonFull(engine, self.menu, 'reset')
        reset.size = vec2d(128, 32)
        reset.pos = SIZE/2 + vec2d(0, 64)
        reset.center = 5

        reset.text.color = (128, 200, 200)
        reset.text.text = 'Reset'
        reset.text.font = 'consolas'
        reset.text.depth = 16

        reset.button.call = self.pressed

        # QUIT BUTTON
        quit = MenuButtonFull(engine, self.menu, 'quit')
        quit.size = vec2d(128, 32)
        quit.pos = SIZE/2 + vec2d(0, 96)
        quit.center = 5

        quit.text.color = (128, 200, 200)
        quit.text.text = 'Quit'
        quit.text.font = 'consolas'
        quit.text.depth = 16

        quit.button.call = self.pressed

    def update(self, pause: bool):
        self.menu.get('resume').update()
        self.menu.get('reset').update()
        self.menu.get('quit').update()

    def draw(self, draw: Draw):
        self.menu.draw(draw)

    def pressed(self, element: MenuElement, pos: vec2d):
        print(element.name)
        if element.name == 'resume-button':
            self.menu.visible = False
            self.engine.pause()
        elif element.name == 'reset-button':
            self.engine.lvl.reset()
            self.engine.pause()
        elif element.name == 'quit-button':
            self.engine.lvl.load('mainmenu')
            self.engine.pause()
