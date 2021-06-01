from os import path, remove, mkdir, getcwd
import sys
from shutil import copytree, rmtree, copy as shcopy

import PyInstaller.__main__
from py7zr import SevenZipFile
from main.code.engine.constants import cprint, clear_terminal, colorize
import re

# Build instructions
def get_version() -> str:
    """Get version in format (v#.#.#Optional[-alpha|beta])"""
    # Get user input of version
    version = input("version: ")

    if version == "exit":
        sys.exit()

    reg = r"(v[0-9]\.[0-9]\.[0-9])+(-alpha|-beta)?"
    if re.fullmatch(reg, version):
        return version
    else:
        raise ValueError("Improper version string")


def main():
    # Clear the terminal
    clear_terminal()

    # Get version
    osname = sys.platform
    if osname.startswith("win"):
        os_platform = "windows"
    elif osname.startswith("linux"):
        os_platform = "linux"
    else:
        msg = "unable to build for systems other than win & linux"
        msg = colorize(msg, "red")
        raise RuntimeError(msg)

    # Get directories and version
    version = get_version()
    dir_main = getcwd()
    dir_dist = path.join(dir_main, "dist")

    # Clean directory
    dir_version = path.join(dir_dist, version)
    if not path.exists(dir_version):
        mkdir(dir_version)
    dir_os = path.join(dir_version, os_platform)
    if path.exists(dir_os):
        rmtree(dir_os)
    mkdir(dir_os)
    cprint("~~Directory Cleaned~~\n", "green")

    # Create executable
    executable_name = "game-x_" + version + "-" + os_platform
    print("Creating executable...")

    arguments = [
        "game.py",
        "--onefile",
        "--noconsole",
        "--debug=all",
        "-n" + executable_name,
    ]

    PyInstaller.__main__.run(arguments)
    executable = path.join(dir_dist, executable_name)
    if os_platform == "windows":
        executable += ".exe"
    cprint("~~EXECUTABLE CREATED~~\n", "green")

    # Create folder based on system version
    dir_game = path.join(dir_os, executable_name)
    print("Creating game folder...")
    mkdir(dir_game)

    print("Moving assets directory...")
    dir_assets = path.join(dir_main, "assets")
    dir_new_assets = path.join(dir_game, "assets")
    copytree(dir_assets, dir_new_assets)

    print("Moving executable...")
    shcopy(executable, dir_game)
    remove(executable)
    cprint("~~GAME FOLDER CREATED~~\n", "green")

    # Compress folder to .7z
    if input("Zip file y/n?") == "y":
        print("Creating 7z file...")
        with SevenZipFile(dir_game + ".7z", "w") as archive:
            archive.writeall(dir_game, executable_name)
        cprint("~~GAME FOLDER COMPRESSED TO 7Z~~", "green")

    # Cleanup
    print("Cleaning up temp files...")
    spec = path.join(dir_main, executable_name + ".spec")
    build = path.join(dir_main, "build", executable_name)

    # Remove spec files
    if path.exists(spec):
        msg = f"Removing: spec file - {path.basename(spec)}"
        cprint(msg, "yellow")
        remove(spec)

    # Remove build files
    if path.exists(build):
        msg = f"Removing: build folder - {path.basename(build)}"
        cprint(msg, "yellow")
        rmtree(build)

    # Finalize
    text = f"\n~~Version {version} {os_platform}"
    text += ": build created with no errors~~"
    cprint(text, "green")


if __name__ == "__main__":
    main()
