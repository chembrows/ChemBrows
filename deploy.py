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
# import shutil
from zipfile import ZipFile
# import build_inno_setup

create_installer = True
app_name = 'ChemBrows'

# Get the current version from the version file
with open('config/version.txt', 'r') as version_file:
    version = version_file.read().rstrip()

# Name of Windows installer
if distutils.util.get_platform() == 'win-amd64':
    installerName = 'setup {0} {1} (64bit)'.format(app_name, version)
else:
    installerName = 'setup {0} {1} (32bit)'.format(app_name, version)

# Name of Esky zip file (without zip extension)
filename = '{0}-{1}.{2}'.format(app_name, version,
                                distutils.util.get_platform())

# Freeze !!!
subprocess.call('python setup.py bdist_esky', shell=True)
print('done with esky')

# Unzip file
print('unzipping')

with ZipFile(os.path.join('dist', filename + '.zip'), "r") as zf:
    zf.extractall('./dist/' + filename)

print('unzipping done')

if sys.platform in ['win32', 'cygwin', 'win64']:
    pass
elif sys.platform == 'darwin':
    pass
else:
    os.chmod('./dist/{}/{}/gui'.format(filename, filename), 755)


# Create installer
if create_installer:
    # TODO: find location
    innoSetupLoc = "C:\Program Files\Inno Setup 5\ISCC"

    architecture = sys.platform

    # Compile it
    print('compiling inno setup..')
    subprocess.call('{} \
          "/dAppName={}" \
          "/dVersion={}" \
          "/dArchitecture={}" \
          "/dOutputBaseFilename={}" \
          inno_installer.iss'.format(innoSetupLoc,
                                     app_name,
                                     version,
                                     architecture,
                                     installerName)
         )
