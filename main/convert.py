# Meant for converting old .lvl files to .json
if __name__ != '__main__':
    raise RuntimeError('file convert.py is not a module and should not be imported')
else:
    from os import listdir
    from engine.engine import Engine
    from engine.types.vector import vec2d

    engine = Engine(32, 60, vec2d(256, 256))

    for file in listdir(engine.paths['levels']):
        if file[-4:] == '.lvl':
            engine.lvl.convert(file[:-4])
