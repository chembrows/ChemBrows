"""
This script freezes the app using Esky with cx_Freeze and produces a Windows
Installer with Inno Setup.

TODO: extend for Mac and Linux

https://github.com/peterbrook/assetjet/blob/master/deploy/deploy.py
https://github.com/peterbrook/assetjet/blob/master/deploy/build_inno_setup.py
"""

import sys
import os
import subprocess
import distutils.util
from zipfile import ZipFile

app_name = 'ChemBrows'
create_installer = True

# Get the current version from the version file
with open('config/version.txt', 'r') as version_file:
    version = version_file.read().rstrip()


# Name of Windows installer, architecture dependent
if distutils.util.get_platform() == 'win-amd64':
    installerName = 'setup {0} {1} (64bit)'.format(app_name, version)
else:
    installerName = 'setup {0} {1} (32bit)'.format(app_name, version)


# get_platform returns a different string than the one used by py2app
if sys.platform == 'darwin':
    platform = distutils.util.get_platform().replace('.', '_')
else:
    platform = distutils.util.get_platform()

# Freeze !!!
subprocess.call('python3 setup.py bdist_esky', shell=True)
print('done with esky')

# Unzip file
print('unzipping')


# Build the name of the Esky zip file
filename = '{}-{}.{}'.format(app_name, version, platform)

with ZipFile(os.path.join('./dist', filename + '.zip'), "r") as zf:
    zf.extractall('./dist/' + filename)

print('unzipping done')


# Change permissions to allow execution
if sys.platform in ['win32', 'cygwin', 'win64']:
    pass
elif sys.platform == 'darwin':

    os.chmod('dist/{}/{}.app/{}/{}.app/Contents/MacOS/gui'.format(filename, app_name, filename, app_name), 0o744)

    # Get the path where the chnages will be made
    path_fixes = 'dist/{}/{}.app/Contents/'.format(filename, app_name)

    # Modify CFBundleExecutable in the Info.plist of the bundle.app
    with open(path_fixes + 'Info.plist', 'r+') as info_plist:
        text = info_plist.read()
        text = text.replace('<string>gui</string>', '<string>launcher</string>')
        info_plist.seek(0)
        info_plist.write(text)
        info_plist.truncate()

    with open(path_fixes + 'MacOS/launcher', 'w+') as launcher:
        text = "#!/usr/bin/env bash"
        text += "\n"
        text += "cd \"${0%/*}\""
        text += "\n"
        # text += "open ../../ChemBrows-0.8.0.macosx-10_10-x86_64/ChemBrows.app"
        text += "open ../../{}/{}.app".format(filename, app_name)
        launcher.write(text)

    os.chmod(path_fixes + 'MacOS/launcher', 0o744)


    # TODO: créer fichier launcher avec path correct
          # modifier fichier Info.plist
          # renommer-renommer bundle.app
else:
    # TODO: change to 0o755 ?
    os.chmod('./dist/{}/{}/gui'.format(filename, filename), 755)




# Create installer for windows
if create_installer and sys.platform in ['win32', 'cygwin', 'win64']:
    innoSetupLoc = "C:\Program Files\Inno Setup 5\ISCC"

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
