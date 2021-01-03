# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['autozoom.py'],
             pathex=['C:\\Users\\Jerry Luo\\Desktop\\Projects\\Scripts\\autozoom'],
             binaries=[],
             datas=[],
             hiddenimports=['pyautogui','schedule','opencv-python','pillow'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [
   ("scheduleA.json", "C:\\Users\\Jerry Luo\\Desktop\\Projects\\Scripts\\autozoom\\scheduleA.json","DATA"),
   ("scheduleB.json", "C:\\Users\\Jerry Luo\\Desktop\\Projects\\Scripts\\autozoom\\scheduleB.json","DATA"),
   ("scheduleC.json", "C:\\Users\\Jerry Luo\\Desktop\\Projects\\Scripts\\autozoom\\scheduleC.json","DATA"),
   ("join.PNG", "C:\\Users\\Jerry Luo\\Desktop\\Projects\\Scripts\\autozoom\\join.PNG","DATA"),
   ("open.png", "C:\\Users\\Jerry Luo\\Desktop\\Projects\\Scripts\\autozoom\\open.png","DATA"),
   ("password.PNG", "C:\\Users\\Jerry Luo\\Desktop\\Projects\\Scripts\\autozoom\\password.PNG","DATA"),
]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='autozoom',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='autozoom')
