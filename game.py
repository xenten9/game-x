"""Used to run main application outside of debug mode."""
import os
from main.main_application import main

if __name__ == '__main__':
    main()
else:
    FILE = os.path.basename(__file__)
    MSG = '{} should not be refferenced or imported.'.format(FILE)
    raise NotImplementedError(MSG)
