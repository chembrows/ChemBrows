#!/usr/bin/python
# coding: utf-8

"""
This script freezes the app using PyInstaller and PyUpdater.

Will produce a Linux executable.
Will produce a Windows Installer with Inno Setup.
Will produce an installable MacOS pkg.

https://github.com/peterbrook/assetjet/blob/master/deploy/deploy.py
https://github.com/peterbrook/assetjet/blob/master/deploy/build_inno_setup.py
"""

import sys
import os
import subprocess
import distutils.util
from distutils.dir_util import copy_tree
from shutil import copyfile
from shutil import rmtree

app_name = 'ChemBrows'
create_installer = True

# Start the program after compiling/extraction
play = False

# Freeze/bundle the program
bundle = True

# Get the current platform and print it
compiling_platform = distutils.util.get_platform()
print("Compiling platform: {}".format(compiling_platform))


# Get the current version from the version file
with open('config/version.txt', 'r') as version_file:
    version = version_file.read().rstrip()

if compiling_platform == 'win-amd64':
    # Name of Windows installer, architecture dependent
    installerName = 'setup_{0}_{1}_(64bit)'.format(app_name, version)
    platform = 'win'
    extension = '.zip'

elif compiling_platform == 'linux-x86_64':
    platform = 'nix64'
    extension = '.tar.gz'

elif "macosx" in compiling_platform:
    platform = 'mac'
    extension = '.tar.gz'

else:
    print("Platform not recognized, EXITING NOW !")
    sys.exit()


# Freeze !!!
if bundle:
    subprocess.call("pyinstaller setup.spec", shell=True)

    print('done freezing')

# Unzip file
print('unzipping')


# Extract the archive
# Build the name of the archive
# Ex: ChemBrows-nix64-0.9.8.tar.gz
filename = '{}-{}-{}'.format(app_name, version, platform)
path_archive = os.path.join('.', 'dist', filename)

if platform == 'win':
    # Run ChemBrows
    if play:
        subprocess.call("{}\\ChemBrows.exe".format(path_archive),
                        shell=True)

if platform == 'nix64' or platform == 'mac':
    # Run ChemBrows
    if play:
        subprocess.call("{}/ChemBrows".format(path_archive),
                        shell=True)


if platform == 'win':
    pass

elif platform == 'mac':

    copyfile('deploy/OSX_extras/Info.plist', './dist/ChemBrows.app/Contents/Info.plist')
    copyfile('images/icon.icns', './dist/ChemBrows.app/Contents/Resources/PythonApplet.icns')
    copy_tree('dist/{}'.format(filename), 'dist/ChemBrows.app/Contents/MacOS/')

    print("Files copied")

    # os.chmod('./pyu-data/new/ChemBrows.app/Contents/MacOS/ChemBrows', 0o777)

    # print("Permissions changed")
    print('Mac OS fixes applied')


elif platform == 'nix64':
    copyfile('deploy/Linux_extras/README', 'dist/{}/README'.format(filename))
    os.chmod('./dist/{}/ChemBrows'.format(filename), 0o777)


# Create installer for windows
if create_installer and platform == 'win':
    innoSetupLoc = "C:\Program Files (x86)\Inno Setup 5\ISCC"

    architecture = sys.platform

    # Compile it
    print('compiling inno setup..')
    subprocess.call('{} \
          "/dAppName={}" \
          "/dVersion={}" \
          "/dArchitecture={}" \
          "/dOutputBaseFilename={}" \
          deploy/inno_installer.iss'.format(innoSetupLoc,
                                     app_name,
                                     version,
                                     architecture,
                                     installerName)
         )

elif create_installer and platform == 'mac':

    # Clean the dir first
    try:
        rmtree('dist/build/')
    except FileNotFoundError:
        print("No previous build directory")

    print('Creating a .pkg for Mac OS...')

    with open('deploy/OSX_extras/template.packproj', 'r') as template:
        text = template.read()

        simplified_version = version.split('.')[:-1]
        simplified_version = '.'.join(simplified_version)
        text = text.replace('LICENSE_PATH', os.path.abspath('LICENSE.txt'))
        text = text.replace('VERSION_DESCRIPTION', simplified_version)
        text = text.replace('INFO_STRING', 'ChemBrows {} Copyrights © 2015 ChemBrows'.format(simplified_version))
        text = text.replace('ICON_FILE', os.path.abspath('images/icon.icns'))
        text = text.replace('VERSION_SIMPLE', simplified_version)
        text = text.replace('MAJOR_VERSION', version.split('.')[0])
        text = text.replace('MINOR_VERSION', version.split('.')[1])
        text = text.replace('APP_PATH', os.path.abspath('dist/ChemBrows.app'))
        text = text.replace('POST_INSTALL_PATH', os.path.abspath('deploy/OSX_extras/post_install.sh'))

        with open('dist/chembrows.packproj', 'w') as packproj:
            packproj.write(text)

    subprocess.call('freeze dist/chembrows.packproj -d pyu-data/new/', shell=True)

    # Make the post-install script (called postflight by Iceberg) executable
    # !!!!!!!! For now, I have to do it manually on Linux, and also compress
    # the pkg on Linux
    os.chmod('dist/build/ChemBrows.pkg/Contents/Resources/postflight', 0o777)
    os.rename("dist/build/ChemBrows.pkg", "dist/build/ChemBrows-{}.pkg".format(version))
    print('Done creating a .pkg for Mac OS...')
