"""Used to run main application outside of debug mode."""
if __name__ != '__main__':
    # If imported
    from os import path
    message = '{} should not be refferenced or imported.'.format(path.basename(__file__))
    raise NotImplementedError(message)

else:
    # If ran directly
    from main.main_application import main
    main()
