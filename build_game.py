# Standard library
import os
from os import sys
import shutil

# External libraries
import PyInstaller.__main__
import py7zr
from main.code.constants import cprint, clear_terminal
clear_terminal()

# Build instructions
def get_version() -> str:
    """Get version in format (v#.#.#Optional[-alpha|beta])"""
    # Get user input of version
    version = input('version: ')

    # Check for suffix
    if '-' in version:
        version_parts = version.split('-')
        if len(version_parts) > 2:
            raise ValueError('Too many parts')
        prefix = version_parts[0]
        suffix = version_parts[1]
        if suffix not in ('alpha', 'beta'):
            raise ValueError('Suffix must be in (alpha, beta)')
    else:
        prefix = version

    # Check for v
    if prefix[0] == 'v':
        prefix = prefix[1:]
    else:
        raise ValueError('Version suffix must start with v')

    # Check version number
    prefix_parts = prefix.split('.')
    if len(prefix_parts) != 3:
        raise ValueError('Version number must have 3 numbers')
    for part in prefix_parts:
        try:
            int(part)
        except TypeError as e:
            print('Version numbers must be integers')
            raise e

    # Proper version
    return version

def copy_dir(src: str, dst: str):
    for src_dir, _, files in os.walk(src):
        dst_dir = src_dir.replace(src, dst, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)

def main():
    # Get version
    osname = sys.platform
    if osname.startswith('win'):
        os_platform = 'windows'
    elif osname.startswith('linux'):
        os_platform = 'linux'
    else:
        err = 'unable to build for systems other than win & linux'
        raise RuntimeError(err)

    # Get directories and version
    version = get_version()
    dir_main = os.getcwd()
    dir_dist = os.path.join(dir_main, 'dist')

    # Clean directory
    dir_version = os.path.join(dir_dist, version)
    if not os.path.exists(dir_version):
        os.mkdir(dir_version)
    dir_os = os.path.join(dir_version, os_platform)
    if os.path.exists(dir_os):
        shutil.rmtree(dir_os)
    os.mkdir(dir_os)
    cprint('~~Directory Cleaned~~\n', 'green')

    # Create executable
    executable_name = 'game-x_'+version+'-'+os_platform
    print('Creating executable...')
    arguments = ['game.pyw', '--onefile', '--noconsole', '-n'+executable_name]
    PyInstaller.__main__.run(arguments)
    executable = os.path.join(dir_dist, executable_name)
    if os_platform == 'windows':
        executable += '.exe'
    cprint('~~EXECUTABLE CREATED~~\n', 'green')

    # Create folder based on system version
    dir_game = os.path.join(dir_os, executable_name)
    print('Creating game folder...')
    os.mkdir(dir_game)

    print('Moving assets directory...')
    dir_assets = os.path.join(dir_main, 'assets')
    dir_new_assets = os.path.join(dir_game, 'assets')
    copy_dir(dir_assets, dir_new_assets)

    print('Moving executable...')
    shutil.copy(executable, dir_game)
    os.remove(executable)
    cprint('~~GAME FOLDER CREATED~~\n', 'green')

    # Compress folder to .7z
    print('Creating 7z file...')
    with py7zr.SevenZipFile(dir_game+'.7z', 'w') as archive:
        archive.writeall(dir_game, executable_name)
    cprint('~~GAME FOLDER COMPRESSED TO 7Z~~', 'green')

    # Cleanup
    print('Cleaning up temp files...')
    spec = os.path.join(dir_main, executable_name+'.spec')
    build = os.path.join(dir_main, 'build', executable_name)
    if os.path.exists(spec):
        print('Removing: spec file - {}'.format(os.path.basename(spec)))
        os.remove(spec)
    if os.path.exists(build):
        print('Removing: build folder - {}'.format(os.path.basename(build)))
        shutil.rmtree(build)

    # Finalize
    text = '~~Version {} {}'.format(version, os_platform)
    text += ': build created with no errors~~'
    cprint(text, 'green')

if __name__ == '__main__':
    main()
