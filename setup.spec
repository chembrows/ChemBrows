# -*- mode: python -*-

import os
import distutils.util

DIR_PATH = os.getcwd()
COMPILING_PLATFORM = distutils.util.get_platform()

PATH_EXE = [os.path.join(DIR_PATH, 'gui.py')]

with open('config/version.txt', 'r', encoding='utf-8') as version_file:
    version = version_file.read().strip()

if COMPILING_PLATFORM == 'win-amd64':
    platform = 'win'
    STRIP = False
elif COMPILING_PLATFORM == 'linux-x86_64':
    platform = 'nix64'
    STRIP = True
elif "macosx" and "x86_64" in COMPILING_PLATFORM:
    platform = 'mac'
    STRIP = True


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
           'packaging.requirements', 'sklearn.neighbors.typedefs',
           'scipy._lib.messagestream']

excludes = ['xmlrpc', 'doctest', 'tty', 'getopt', 'tcl', 'tkinter',
            'pyi_rth_pkgres', 'pyi_rth_qt5plugins', 'lib2to3']


a = Analysis(['gui.py'],
             pathex=PATH_EXE,
             binaries=None,
             datas=added_files,
             hiddenimports=imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=excludes,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

rm_bins = ['libQtWebKit', 'libQtGui', 'libQtXmlPatterns', 'libmysqlclient',
           'libQt3Support', 'libwebp', 'libXss', 'libXft', 'libtcl', 'libtk',
           'libX11', 'libgstreamer', 'libgcrypt', 'libQtOpenGL.so',
           'libfbclient', 'libfreetype', 'libsqlite3', 'libQtDBus',
           'libsystemd', 'libgstvideo', 'liborc', 'libharfbuzz', 'libpcre',
           'libmng', 'bncursesw', 'libgstbase', 'libgstaudio', 'liblcms2',
           'libQtSvg', 'libatlas', 'libgobject', 'libgsttag', 'libmpdec',
           'libgstpbutils', 'libICE', 'libQtXml', 'libfontconfig', 'libglapi',
           'libgraphite2', 'libexpat', 'libXext', 'liblz4', 'libqdds',
           'libqgif', 'libqjp2', 'libqsvg', 'libqtga', 'libqwbmp', 'libqwebp',
           'libqtiff', 'libQt5PrintSupport', 'libunistring', 'libgnutls',
           'libglib-2.0', 'libkrb5', 'libgmp', 'libcups', 'libstdc++',
           '_cffi_backend', 'libQt5Svg', '_decimal', 'libxcb-glx',
           'mkl_avx512_mic', 'mkl_core', 'mkl_avx512', 'mkl_avx2', 'mkl_avx',
           'mkl_mc3', 'mkl_mc', 'mkl_def', 'mkl_intel_thread',
           'mkl_tbb_thread', 'mkl_sequential', 'mkl_vml_avx512_mic',
           'mkl_vml_avx', 'mkl_vml_avx512', 'svml_dispmd']

full_tuples = []
for each_bin in a.binaries:
    for each_rm_bin in rm_bins:
        if each_rm_bin in each_bin[0]:
            full_tuples.append((each_bin[0], None, None))

a.binaries = a.binaries - TOC(full_tuples)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='ChemBrows',
          debug=False,
          strip=STRIP,
          upx=True,
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=STRIP,
               upx=True,
               name='ChemBrows-{}-{}'.format(version, platform))

if platform == 'mac':
    app = BUNDLE(exe,
                 name='ChemBrows.app',
                 icon=None,
                 bundle_identifier=None)
