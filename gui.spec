# -*- mode: python -*-

block_cipher = None

imports = ['packaging', 'packaging.version', 'packaging.specifiers',
           'packaging.requirements', 'sklearn.neighbors.typedefs', 'QtWebEngineProcess']

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


a = Analysis(['gui.py'],
             pathex=['/home/djipey/informatique/python/ChemBrows'],
             binaries=[],
             datas=added_files,
             hiddenimports=imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='gui')
