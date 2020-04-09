# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['FileCopy.py'],
             pathex=['C:\\Users\\Y.Kojima\\OneDrive - ADSTEC\\00_Yuki_Documentation\\※ローカル※イメージング\\97_その他、時系列振分け\\200304_JFE_尾端検出トラブル解析用ソフト\\FileCopy_v1.2\\FileCopy'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='FileCopy',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
