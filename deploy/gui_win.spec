# -*- mode: python -*-

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

a = Analysis(['gui.py'],
             pathex=['C:\\Users\\djipey\\Desktop\\ChemBrows'],
             binaries=[],
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
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='gui',
          debug=False,
          strip=False,
          upx=True,
          console=True )
		  
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
		  
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='gui')
