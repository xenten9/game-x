"""Debuging tools."""
from datetime import datetime
from .menu import ObjMenu, ObjTextElement
from ..helper_functions.file_system import ObjFile
from .vector import vec2d

class ObjDebug():
    def __init__(self, game: object):
        # Game var
        self.game = game

        # Menu vars
        self.menu = ObjMenu(game, (160, 36))
        self.menu.blank()
        text = ObjTextElement(self.menu, 'fps')
        text.set_vars(size=vec2d(128, 12), font='consolas', backdrop=1)
        text = ObjTextElement(self.menu, 'campos')
        text.set_vars(size=vec2d(128, 12), font='consolas', backdrop=1,
                      pos=vec2d(0, 12))
        text = ObjTextElement(self.menu, 'memory')
        text.set_vars(size=vec2d(128, 12), font='consolas', backdrop=1,
                      pos=vec2d(0, 24))

        # Debug file vars
        self.debug_path = game.PATH['DEBUGLOG']
        self.date_time = datetime.now()
        self.date_time = self.date_time.strftime('%Y-%m-%d_%Hh%M_%S')
        self.file = ObjFile(self.debug_path, '{}.txt'.format(self.date_time))
        self.file.append()
        self.file.file.write(self.date_time + '\n')
        self.file.close()

        # Timing vars
        self.time_record = {}
        self.clock = 0
        self.on = True

    def __bool__(self):
        # If treated as a boolean
        return self.on

    def tick(self):
        """Called once every frame."""
        self.clock += 1
        if self.clock == self.game.FPS * 10:
            self.clock = 0
            self.record(10)

    def record(self, time: float):
        """Record time data to file."""
        self.file.append()
        file = self.file.file
        file.write('###\n')
        size = 0
        for item in self.time_record:
            size = max(size, len(item))

        for item in self.time_record:
            text = item
            while len(text) < size:
                text += ' '
            text = '{}: {:.1f}%\n'.format(text, 100 * (self.time_record[item] / time))
            file.write(text)
            self.time_record[item] = 0
