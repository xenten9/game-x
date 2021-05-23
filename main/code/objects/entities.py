"""All entities."""
# Standard library
from time import sleep
from random import random

# Local imports
from ..engine.engine import Engine
from ..engine.components.draw import Draw
from ..engine.components.menu import Menu, MenuButton, MenuElement, MenuSlider
from ..engine.components.menu import MenuText, MenuRect
from ..engine.components.menu import MenuButtonFull
from ..engine.components.maths import f_limit
from ..engine.types.vector import vec2d
from ..engine.types.entity import Entity
from ..constants import SIZE
from ..engine.constants import colorize

# Entities
class ObjJukeBox(Entity):
    """Responsible for sick beats."""
    def __init__(self, engine: Engine, key: int, name: str, data: dict):
        super().__init__(engine, key, name, data)
        engine.obj.instantiate_object(key, self)

        # Music vars
        music = engine.aud.music
        current_music = music.get_current()
        self.music = self.data['name']
        self.loops = self.data['loops']
        self.volume = self.data['volume']

        if self.music is None:
            if current_music is not None:
                # Fade music
                music.stop(1000)
        else:
            if music.fading:
                # Replace next song
                music.queue(self.music, self.loops, self.volume)
            else:
                if current_music is None:
                    # Start playing music
                    music.load(self.music)
                    music.volume = self.volume
                    music.play(self.loops)

                elif current_music != self.music: # Queue up music
                    music.stop(1500)
                    music.queue(self.music, self.loops, self.volume)



    def update(self, paused: bool):
        if self.engine.aud.music.get_current() == self.music:
            if paused:
                self.engine.aud.music.volume = self.volume / 4
            else:
                self.engine.aud.music.volume = self.volume

class ObjMainMenu(Entity):
    def __init__(self, engine: Engine, key: int, name: str, data: dict):
        engine.obj.instantiate_object(key, self)
        super().__init__(engine, key, name, data)
        self.key = key
        self.name = name
        self.data = data
        self.engine.cam.pos = vec2d(0, 0)
        self.engine.aud.sfx.add('beep.ogg')

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
        volume_slider = MenuSlider(engine, self.option_menu, 'volume-slider')
        volume_slider.size = vec2d(100, 24)
        volume_slider.pos = SIZE/2 + vec2d(0, 24)
        volume_slider.center = 5

        volume_slider.rect_slide.color = (64, 64, 64)

        volume_slider.button.call = self.pressed

        # RETURN Button
        save_button = MenuButtonFull(engine, self.option_menu, 'save-button')
        save_button.pos = SIZE/2 + vec2d(0, 104)
        save_button.center = 5
        save_button.size = vec2d(128, 24)

        save_button.text.text = 'Save'
        save_button.text.color = (128, 128, 128)
        save_button.text.depth = 16

        save_button.button.call = self.pressed

        # RETURN Button
        return_button = MenuButtonFull(engine, self.option_menu, 'return-button')
        return_button.pos = SIZE/2 + vec2d(0, 128)
        return_button.center = 5
        return_button.size = vec2d(128, 24)

        return_button.text.text = 'Return'
        return_button.text.color = (128, 128, 128)
        return_button.text.depth = 16

        return_button.button.call = self.pressed

    def update(self, paused: bool):
        self.title_menu.get('start-button').update()
        self.title_menu.get('option-button').update()
        self.title_menu.get('quit-button').update()
        self.option_menu.get('volume-slider').update()
        self.option_menu.get('save-button').update()
        self.option_menu.get('return-button').update()
        if self.option_menu.visible:
            if self.engine.inp.kb.get_key_pressed(41):
                self.option_menu.visible = False
                self.title_menu.visible = True

    def draw(self, draw: Draw):
        self.title_menu.draw(draw)
        self.option_menu.draw(draw)

    def pressed(self, element: MenuButton, pos: vec2d):
        if element.name == 'start-button-button':
            self._beep()
            self._rsleep(0.4)
            self.engine.lvl.load('level1')
        elif element.name == 'option-button-button':
            self._beep()
            self.title_menu.visible = False
            self.option_menu.visible = True
            vol = self.option_menu.get('volume-slider')
            self.engine.settings.load()
            if isinstance(vol, MenuSlider):
                vol.value = self.engine.settings.volume
        elif element.name == 'return-button-button':
            self._beep()
            self._rsleep(0.05)
            self.title_menu.visible = True
            self.option_menu.visible = False
        elif element.name == 'quit-button-button':
            self._beep()
            self._rsleep(0.5)
            self.engine.end()
        elif element.name == 'volume-slider-button':
            x = pos.x
            x = f_limit(x, 0, 1)
            if isinstance(element.menu, MenuSlider):
                element.menu.value = x
        elif element.name == 'save-button-button':
            self._beep()
            menu = self.option_menu
            settings = self.engine.settings

            volume = menu.get('volume-slider')
            if isinstance(volume, MenuSlider):
                settings.volume = volume.value

            settings.save()

    def _beep(self):
        self.engine.aud.sfx.play('beep.ogg')

    def _rsleep(self, time: float, var: float = None):
        if var is None:
            var = 1/8
        elif var > 1:
            raise ValueError(colorize('Variance must be <= 1.', 'red'))
        s = time * (((random()-.5)*var)+1)
        sleep(s)

class ObjPauseMenu(Entity):
    def __init__(self, engine: Engine, key: int, name: str, data:dict):
        engine.obj.instantiate_object(key, self)
        super().__init__(engine, key, name, data)
        self.key = key
        self.name = name
        self.data = data
        self.engine.aud.sfx.add('beep.ogg')

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

    def update(self, paused: bool):
        self.menu.get('resume').update()
        self.menu.get('reset').update()
        self.menu.get('quit').update()

    def draw(self, draw: Draw):
        self.menu.draw(draw)

    def pressed(self, element: MenuElement, pos: vec2d):
        if element.name == 'resume-button':
            self._beep()
            self.menu.visible = False
            self.engine.pause()
        elif element.name == 'reset-button':
            self._beep()
            self.engine.lvl.reset()
            self.engine.pause()
        elif element.name == 'quit-button':
            self._beep()
            self.engine.lvl.load('mainmenu')
            self.engine.pause()

    def _beep(self):
        self.engine.aud.sfx.play('beep.ogg')
