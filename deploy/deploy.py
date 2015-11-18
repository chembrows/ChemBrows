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

# Name of Windows installer
if distutils.util.get_platform() == 'win-amd64':
    installerName = 'setup {0} {1} (64bit)'.format(app_name, version)
else:
    installerName = 'setup {0} {1} (32bit)'.format(app_name, version)


if sys.platform == 'darwin':
    platform = distutils.util.get_platform().replace('.', '_')
    # import os, shutil, fnmatch
    # folder = './dist/'
    # for the_file in os.listdir(folder):
        # file_path = os.path.join(folder, the_file)
        # if fnmatch.fnmatch(file_path, "*.app"):
            # os.remove(file_path)
else:
    platform = distutils.util.get_platform()

# Freeze !!!
subprocess.call('python3 setup.py bdist_esky', shell=True)
print('done with esky')

# Unzip file
print('unzipping')


# Name of Esky zip file (without zip extension)
filename = '{}-{}.{}'.format(app_name, version, platform)

with ZipFile(os.path.join('./dist', filename + '.zip'), "r") as zf:
    zf.extractall('./dist/' + filename)

print('unzipping done')

if sys.platform in ['win32', 'cygwin', 'win64']:
    pass
elif sys.platform == 'darwin':
    os.chmod('dist/{}/{}.app/{}/{}.app/Contents/MacOS/gui'.format(filename, app_name, filename, app_name), 755)
else:
    os.chmod('./dist/{}/{}/gui'.format(filename, filename), 755)

# Create installer
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
