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
import zipfile
from shutil import copyfile
from shutil import rmtree
import tarfile

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
    installerName = 'setup {0} {1} (64bit)'.format(app_name, version)
    platform = 'win'
    extension = '.zip'

elif compiling_platform == 'linux-x86_64':
    platform = 'nix64'
    extension = '.tar.gz'

elif "macosx" and "x86_64" in compiling_platform:
    platform = 'mac'
    extension = '.tar.gz'

else:
    print("Platform not recognized, EXITING NOW !")
    sys.exit()

# get_platform returns a different string than the one used by py2app
# if sys.platform == 'darwin':
    # platform = distutils.util.get_platform().replace('.', '_')

# Freeze !!!
if bundle:
    subprocess.call("pyupdater build --app-version {} setup.spec".
                    format(version), shell=True)
    # subprocess.call("pyupdater pkg --process --sign", shell=True)

    print('done freezing')

# Unzip file
print('unzipping')


# Extract the archive
# Build the name of the archive
# Ex: ChemBrows-nix64-0.9.8.tar.gz
filename = '{}-{}-{}'.format(app_name, platform, version)
path_archive = os.path.join('.', 'pyu-data', 'new', filename)

if platform == 'win':
    # Exctract the zip file
    with zipfile.ZipFile(path_archive + extension) as zf:
        zf.extractall(os.path.join('.', 'pyu-data', 'new', filename))

    print('unzipping done')

    # Run ChemBrows
    if play:
        subprocess.call("{}\\ChemBrows.exe".format(path_archive),
                        shell=True)
if platform == 'nix64' or platform == 'mac':
    # Extract the tar.gz file
    with tarfile.open(path_archive + extension, "r:gz") as tf:
        tf.extractall(os.path.join('.', 'pyu-data', 'new', filename))

    print('unzipping done')

    # Run ChemBrows
    if play:
        subprocess.call("{}/ChemBrows".format(path_archive),
                        shell=True)


if platform == 'win':
    pass

elif platform == 'mac':

    # Clean the dir first
    try:
        rmtree('./pyu-data/new/ChemBrows.app')
    except FileNotFoundError:
        print("No previous ChemBrows.app")

    os.makedirs('./pyu-data/new/ChemBrows.app', exist_ok=True)
    os.makedirs('./pyu-data/new/ChemBrows.app/Contents', exist_ok=True)
    os.makedirs('./pyu-data/new/ChemBrows.app/Contents/MacOS', exist_ok=True)
    os.makedirs('./pyu-data/new/ChemBrows.app/Contents/Resources', exist_ok=True)

    print("App architecture created")

    copyfile('deploy/OSX_extras/Info.plist', './pyu-data/new/ChemBrows.app/Contents/Info.plist')
    copyfile('images/icon.icns', './pyu-data/new/ChemBrows.app/Contents/Resources/PythonApplet.icns')
    copyfile("{}/ChemBrows".format(path_archive), './pyu-data/new/ChemBrows.app/Contents/MacOS/ChemBrows')

    print("Files copied")

    os.chmod('./pyu-data/new/ChemBrows.app/Contents/MacOS/ChemBrows', 0o777)

    print("Permissions changed")
    print('Mac OS fixes applied')


elif platform == 'nix64':
    # copyfile('deploy/Linux_extras/README', 'dist/{}/README'.format(filename))
    # os.chmod('./dist/{}/gui'.format(filename), 0o777)
    # os.chmod('./dist/{}/{}/gui'.format(filename, filename), 0o777)
    pass


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
        text = text.replace('APP_PATH', os.path.abspath('pyu-data/new/ChemBrows.app'))
        text = text.replace('POST_INSTALL_PATH', os.path.abspath('deploy/OSX_extras/post_install.sh'))

        with open('pyu-data/new/chembrows.packproj', 'w') as packproj:
            packproj.write(text)

    # os.rename("path/to/current/file.foo", "path/to/new/desination/for/file.foo")

    subprocess.call('freeze pyu-data/new/chembrows.packproj -d pyu-data/new/', shell=True)

    # Make the post-install script (called postflight by Iceberg) executable
    # !!!!!!!! For now, I have to do it manually on Linux, and also compress
    # the pkg on Linux
    os.chmod('pyu-data/new/build/ChemBrows.pkg/Contents/Resources/postflight', 0o777)
    os.rename("pyu-data/new/build/ChemBrows.pkg", "pyu-data/new/build/ChemBrows-{}.pkg".format(version))
    print('Done creating a .pkg for Mac OS...')
