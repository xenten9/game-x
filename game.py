"""Used to run main application outside of debug mode."""
import os
import sys
from main.main_application import main
import logging

if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        main_path = os.path.dirname(sys.executable)

        logging.basicConfig(
            filename=os.path.join(main_path, "log.txt"), level=logging.DEBUG
        )
        try:
            main()
        except Exception:
            logging.error("A critical error occurred.", exc_info=True)

    else:
        main()

else:
    FILE = os.path.basename(__file__)
    msg = f"{FILE} should not be refferenced or imported."
    raise NotImplementedError(msg)
