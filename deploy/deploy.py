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
import tarfile

app_name = 'ChemBrows'
create_installer = True

# Start the program after compiling/extraction
play = False

# Freeze/bundle the program
bundle = False

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

else:
    print("Platform not recognized, EXITING NOW !")
    sys.exit()

# get_platform returns a different string than the one used by py2app
# if sys.platform == 'darwin':
    # platform = distutils.util.get_platform().replace('.', '_')

# Freeze !!!
if bundle:
    subprocess.call("pyupdater build --app-version {} setup.spec".format(version),
                    shell=True)
    subprocess.call("pyupdater pkg --process --sign", shell=True)

    print('done freezing')

# Unzip file
print('unzipping')

# Build the name of the archive
# Ex: ChemBrows-nix64-0.9.8.tar.gz
filename = '{}-{}-{}'.format(app_name, platform, version)
path_archive = os.path.join('.', 'pyu-data', 'deploy', filename)

if platform == 'win':
    # Exctract the zip file
    with zipfile.ZipFile(path_archive + extension) as zf:
        zf.extractall(os.path.join('.', 'pyu-data', 'deploy', filename))

    print('unzipping done')

    # Run ChemBrows
    if play:
        subprocess.call("{}\\ChemBrows.exe".format(path_archive),
                        shell=True)

if platform == 'nix64':
    # Extract the tar.gz file
    with tarfile.open(path_archive + extension, "r:gz") as tf:
        tf.extractall(os.path.join('.', 'pyu-data', 'deploy', filename))

    print('unzipping done')

    # Run ChemBrows
    if play:
        subprocess.call("{}/ChemBrows".format(path_archive),
                        shell=True)


# Change permissions to allow execution
if platform == 'win':
    pass
elif sys.platform == 'darwin':

    os.chmod('dist/{}/{}.app/{}/{}.app/Contents/MacOS/gui'.format(filename, app_name, filename, app_name), 0o777)
    os.chmod('dist/{}/{}.app/Contents/MacOS/gui'.format(filename, app_name, filename, app_name), 0o777)

    # Get the path where the changes will be made
    path_fixes = 'dist/{}/{}.app/Contents/'.format(filename, app_name)

    # To fix issue #104 of Esky. Copy some files stored in deploy. It should be
    # temporary, and it's not optimized yet (not all the modules in python35.zip are
    # required)
    copyfile('deploy/OSX_extras/zlib.so', path_fixes + 'Resources/lib/python3.5/lib-dynload/zlib.so')
    copyfile('deploy/OSX_extras/python35.zip', path_fixes + 'Resources/lib/python35.zip')

    # # Modify CFBundleExecutable in the Info.plist of the bundle.app
    # with open(path_fixes + 'Info.plist', 'r+') as info_plist:
        # text = info_plist.read()

        # # # Modify the executable
        # # text = text.replace('<string>gui</string>', '<string>launcher</string>')

        # # Set LSUIElement to 1 to avoid double icons
        # text = text.replace('<dict>\n\t<key>CFBundleDevelopmentRegion</key>',
                            # '<dict>\n\t<key>LSUIElement</key>\n\t<string>1</string>\n\t<key>CFBundleDevelopmentRegion</key>')

        # info_plist.seek(0)
        # info_plist.write(text)
        # info_plist.truncate()

    # with open(path_fixes + 'MacOS/launcher', 'w+') as launcher:
        # text = "#!/usr/bin/env bash"
        # text += "\n"
        # text += "cd \"${0%/*}\""
        # text += "\n"
        # text += "open ../../{}/{}.app".format(filename, app_name)
        # launcher.write(text)

    # os.chmod(path_fixes + 'MacOS/launcher', 0o777)

    # print('Mac OS fixes applied')

    print('Starting copying icons')
    copyfile('images/icon.icns', path_fixes + 'Resources/PythonApplet.icns')
    copyfile('images/icon.icns', 'dist/{}/{}.app/{}/{}.app/Contents/Resources/PythonApplet.icns'.format(filename, app_name, filename, app_name))
    print('Done copying icons')


else:
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

elif create_installer and sys.platform == 'darwin':

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
        text = text.replace('APP_PATH', os.path.abspath('dist/{}/{}.app'.format(filename, app_name)))
        text = text.replace('POST_INSTALL_PATH', os.path.abspath('deploy/OSX_extras/post_install.sh'))

        with open('dist/chembrows.packproj', 'w') as packproj:
            packproj.write(text)

    subprocess.call('freeze dist/chembrows.packproj -d dist/', shell=True)

    # Make the post-install script (called postflight by Iceberg) executable
    # !!!!!!!! For now, I have to do it manually on Linux, and also compress
    # the pkg on Linux
    os.chmod('dist/build/ChemBrows.pkg/Contents/Resources/postflight', 0o777)
    print('Done creating a .pkg for Mac OS...')
