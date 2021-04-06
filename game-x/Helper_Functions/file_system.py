"""File system used to simplify the creation and access of files."""
# file access object
from os import getcwd, chdir, remove

class ObjFile:
    """Used to access files."""
    def __init__(self, directory=getcwd(), fname=""):
        # desired directory
        self.dir = directory
        # name of file
        self.name = fname
        # file identifier
        self.file = None

    # change directory
    def change_dir(self):
        """Changes directory to desired directory."""
        if getcwd() != self.dir:
            chdir(self.dir)

    # delete file if it exists
    def delete(self):
        """Deletes the file from the desired directory"""
        self.change_dir()
        try:
            remove(self.name)
        except FileNotFoundError:
            pass

    # create files and return the file identifier
    def create(self, overide: bool):
        """Creates a file at the desired directory."""
        # check if we are at the directory we want
        self.change_dir()
        try:
            # try to create new file
            self.file = open(self.name, 'x')
        except FileExistsError:
            if overide:
                # delete file and make new one
                self.delete()
                self.file = open(self.name, 'x')

    # open a file for reading
    def read(self):
        """Opens the desired file in read mode."""
        self.change_dir()
        self.file = open(self.name, 'r')

    # open a file for writing
    def write(self):
        """Opens the desired file in write mode."""
        self.change_dir()
        self.file = open(self.name, 'w')

    # open a file for appending
    def append(self):
        """Opens the desired file in append mode."""
        self.change_dir()
        self.file = open(self.name, 'a')

    # close file
    def close(self):
        """Closes the file object."""
        self.file.close()
