# -*- mode: python -*-

import os
import distutils.util

DIR_PATH = os.getcwd()
COMPILING_PLATFORM = distutils.util.get_platform()

PATH_EXE = [os.path.join(DIR_PATH, 'gui.py')]

if COMPILING_PLATFORM == 'win-amd64':
    platform = 'win'
    hookspath = ['C:\\Users\\djipey\\AppData\Local\\Programs\\Python\\Python35\\Lib\\site-packages\\pyupdater\\hooks']
elif COMPILING_PLATFORM == 'linux-x86_64':
    platform = 'nix64'
    hookspath = ['/home/djipey/.local/share/virtualenvs/cb/lib/python3.5/site-packages/pyupdater/hooks']
elif "macosx" and "x86_64" in COMPILING_PLATFORM:
    hookspath = ['/Users/djipey/anaconda3/lib/python3.5/site-packages/pyupdater/hooks']
    platform = 'mac'



block_cipher = None

added_files = [('images/*', 'images'),
               ('journals/*', 'journals'),
               ('config/data.bin', 'config'),
               ('config/regex.txt', 'config'),
               ('config/stop_words.txt', 'config'),
               ('config/tuto.txt', 'config'),
               ('config/version.txt', 'config'),
               ('config/whatsnew.txt', 'config'),
               ('config/fields/*', 'config/fields')
               ]

imports = ['packaging', 'packaging.version', 'packaging.specifiers',
           'packaging.requirements', 'sklearn.neighbors.typedefs']

excludes = ['pyi_rth_pkgres', 'pyi_rth_qt5plugins', 'lib2to3', 'runpy',
            'xmlrpc', 'doctest', 'tty', 'getopt']

a = Analysis(PATH_EXE,
             pathex=[DIR_PATH] * 2,
             binaries=None,
             datas=added_files,
             hiddenimports=imports,
             hookspath=hookspath,
             runtime_hooks=[],
             excludes=excludes,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

rm_bins = ['libQtWebKit', 'libQtGui', 'libQtXmlPatterns', 'libmysqlclient',
           'libQt3Support', 'libwebp', 'libXss', 'libXft', 'libcrypto',
           'libtcl', 'libtk', 'libX11', 'libgstreamer', 'libgcrypt',
           'libQtOpenGL.so', 'libfbclient', 'libfreetype', 'libgcc_s',
           'libsqlite3', 'libQtDBus', 'libsystemd', 'libgstvideo', 'liborc',
           'libharfbuzz', 'libpcre', 'libmng', 'bncursesw', 'libgstbase',
           'libgstaudio', 'liblcms2', 'libQtSvg', 'liblapack', 'libatlas',
           'libgobject', 'libquadmath', 'libgsttag', 'libmpdec',
           'libgstpbutils', 'libxcb-glx', 'libICE', 'libQtXml',
           'libfontconfig', 'libglapi', 'libgraphite2', 'libexpat',
           'libXext', 'liblz4']

full_tuples = []
for each_bin in a.binaries:
    for each_rm_bin in rm_bins:
        if each_rm_bin in each_bin[0]:
            full_tuples.append((each_bin[0], None, None))

a.binaries = a.binaries - TOC(full_tuples)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=platform,
          debug=False,
          strip=True,
          upx=True,
          console=False)
