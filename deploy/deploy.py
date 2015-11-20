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
from shutil import copyfile

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
    python_exe = 'python3'
else:
    platform = distutils.util.get_platform()
    python_exe = 'python'

# Freeze !!!
subprocess.call('{} setup.py bdist_esky'.format(python_exe), shell=True)
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

        # Modify the executable
        text = text.replace('<string>gui</string>', '<string>launcher</string>')

        # Set LSUIElement to 1 to avoid double icons
        text = text.replace('<dict>\n\t<key>CFBundleDevelopmentRegion</key>',
                            '<dict>\n\t<key>LSUIElement</key>\n\t<string>1</string>\n\t<key>CFBundleDevelopmentRegion</key>')

        info_plist.seek(0)
        info_plist.write(text)
        info_plist.truncate()

    with open(path_fixes + 'MacOS/launcher', 'w+') as launcher:
        text = "#!/usr/bin/env bash"
        text += "\n"
        text += "cd \"${0%/*}\""
        text += "\n"
        text += "open ../../{}/{}.app".format(filename, app_name)
        launcher.write(text)

    os.chmod(path_fixes + 'MacOS/launcher', 0o744)

    print('Mac OS fixes applied')

    print('Starting copying icons')
    copyfile('images/icon.icns', path_fixes + 'Resources/PythonApplet.icns')
    copyfile('images/icon.icns', 'dist/{}/{}.app/{}/{}.app/Contents/Resources/PythonApplet.icns'.format(filename, app_name, filename, app_name))
    print('Done copying icons')


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

elif create_installer and sys.platform == 'darwin':

    print('Creating a .pkg for Mac OS...')

    with open('deploy/template.packproj', 'r') as template:
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

        with open('dist/chembrows.packproj', 'w') as packproj:
            packproj.write(text)

    subprocess.call('freeze dist/chembrows.packproj -d dist/', shell=True)
    print('Done creating a .pkg for Mac OS...')

