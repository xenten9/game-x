"""Used to run main application outside of debug mode."""
# Import main from main application
from main.main_application import main

# run if ran directly
if __name__ == '__main__':
    main()
else:
    message = 'This file should not be refferenced or imported.'
    raise NotImplementedError(message)
