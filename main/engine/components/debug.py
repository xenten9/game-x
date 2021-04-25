"""Debuging tools."""
from datetime import datetime
from .menu import ObjMenu, ObjTextElement
from ..helper_functions.file_system import ObjFile
from .vector import vec2d

class ObjDebug():
    def __init__(self, game: object, debug: bool):
        # Game var
        self.game = game
        self.on = debug

        if debug:
            # Menu vars
            self.menu = ObjMenu(game, (160, 60))
            self.menu.blank()
            fps = ObjTextElement(self.menu, 'fps')
            size = 12
            font = 'consolas'
            backdrop = 1
            fps.set_vars(size=size, font=font, backdrop=backdrop)

            campos = ObjTextElement(self.menu, 'campos')
            pos = vec2d(0, 12)
            campos.set_vars(size=size, font=font, backdrop=backdrop, pos=pos)

            text = ObjTextElement(self.menu, 'memory')
            pos = vec2d(0, 24)
            text.set_vars(size=size, font=font, backdrop=backdrop, pos=pos)

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
        size = 0
        total = 0
        for item in self.time_record:
            total += self.time_record[item]
            size = max(size, len(item))

        file.write('###\n')
        file.write('Total: {:.1f}%\n'.format(total * (100 / time)))

        for item in self.time_record:
            text = item
            while len(text) < size:
                text += ' '
            text = '{}: {:.1f}%\n'.format(text, 100 * (self.time_record[item] / time))
            file.write(text)
            self.time_record[item] = 0
        file.close()
