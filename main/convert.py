# NOTE very jank and hardcoded [will likely recquire modifications to run]
# Meant for converting old .lvl files to .json
if __name__ != '__main__':
    from os import listdir
    from main.code.engine.engine import Engine
    from main.code.engine.types.vector import vec2d

    engine = Engine(32, 60, vec2d(256, 256))

    for file in listdir(engine.paths['levels']):
        if file[-4:] == '.lvl':
            engine.lvl.convert(file[:-4])
else:
    message = 'This file should not be refferenced or imported.'
    raise NotImplementedError(message)
