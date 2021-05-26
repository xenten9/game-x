# Standard library
from os import path, remove, mkdir, getcwd
import sys
from shutil import copytree, rmtree, copy as shcopy

# External libraries
import PyInstaller.__main__
from py7zr import SevenZipFile
from main.code.engine.constants import cprint, clear_terminal, colorize

# Build instructions
def get_version() -> str:
    """Get version in format (v#.#.#Optional[-alpha|beta])"""
    # Get user input of version
    version = input('version: ')

    if version == 'exit':
        sys.exit()

    if '-' in version:
        version_parts = version.split('-')
        prefix, suffix = version_parts[0:2]
    else:
        version_parts = [version]
        prefix = version
        suffix = ''


    # Check prefix
    if prefix[0] != 'v':
        msg = colorize('Prefix must start with v', 'red')
        raise ValueError(msg)

    version_numbers = prefix[1:].split('.')
    if len(version_numbers) != 3:
        msg = colorize('Prefix must be 3 numbers long', 'red')
        raise ValueError(msg)

    for num in version_numbers:
        try:
            int(num)
        except (TypeError, ValueError) as error:
            msg = colorize('Prefix must be integers', 'red')
            raise ValueError(msg) from error


    # Check suffix
    if suffix != '':
        if suffix not in ('alpha', 'beta'):
            msg = colorize('Suffix must be in the form (alpha, beta)', 'red')
            raise ValueError(msg)

        if len(version_parts) > 2:
            msg = colorize('Version must be in form prefix-suffix', 'red')
            raise ValueError(msg)


    # Proper version
    return version

def main():
    # Clear the terminal
    clear_terminal()

    # Get version
    osname = sys.platform
    if osname.startswith('win'):
        os_platform = 'windows'
    elif osname.startswith('linux'):
        os_platform = 'linux'
    else:
        msg = 'unable to build for systems other than win & linux'
        msg = colorize(msg, 'red')
        raise RuntimeError(msg)

    # Get directories and version
    version = get_version()
    dir_main = getcwd()
    dir_dist = path.join(dir_main, 'dist')

    # Clean directory
    dir_version = path.join(dir_dist, version)
    if not path.exists(dir_version):
        mkdir(dir_version)
    dir_os = path.join(dir_version, os_platform)
    if path.exists(dir_os):
        rmtree(dir_os)
    mkdir(dir_os)
    cprint('~~Directory Cleaned~~\n', 'green')

    # Create executable
    executable_name = 'game-x_'+version+'-'+os_platform
    print('Creating executable...')
    arguments = ['game.pyw', '--onefile', '--noconsole', '-n'+executable_name]
    PyInstaller.__main__.run(arguments)
    executable = path.join(dir_dist, executable_name)
    if os_platform == 'windows':
        executable += '.exe'
    cprint('~~EXECUTABLE CREATED~~\n', 'green')

    # Create folder based on system version
    dir_game = path.join(dir_os, executable_name)
    print('Creating game folder...')
    mkdir(dir_game)

    print('Moving assets directory...')
    dir_assets = path.join(dir_main, 'assets')
    dir_new_assets = path.join(dir_game, 'assets')
    copytree(dir_assets, dir_new_assets)

    print('Moving executable...')
    shcopy(executable, dir_game)
    remove(executable)
    cprint('~~GAME FOLDER CREATED~~\n', 'green')

    # Compress folder to .7z
    print('Creating 7z file...')
    with SevenZipFile(dir_game+'.7z', 'w') as archive:
        archive.writeall(dir_game, executable_name)
    cprint('~~GAME FOLDER COMPRESSED TO 7Z~~', 'green')

    # Cleanup
    print('Cleaning up temp files...')
    spec = path.join(dir_main, executable_name+'.spec')
    build = path.join(dir_main, 'build', executable_name)

    # Remove spec files
    if path.exists(spec):
        msg = 'Removing: spec file - {}'.format(path.basename(spec))
        cprint(msg, 'yellow')
        remove(spec)

    # Remove build files
    if path.exists(build):
        msg = 'Removing: build folder - {}'.format(path.basename(build))
        cprint(msg, 'yellow')
        rmtree(build)

    # Finalize
    text = '~~Version {} {}'.format(version, os_platform)
    text += ': build created with no errors~~'
    cprint(text, 'green')

if __name__ == '__main__':
    main()
