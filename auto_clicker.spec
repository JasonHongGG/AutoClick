# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['auto_clicker.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='auto_clicker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

import shutil
import os

# Post-build: Copy targets folder to dist
# We assume the build is running in the project root
project_dir = os.getcwd()
dist_dir = os.path.join(project_dir, 'dist')
targets_src = os.path.join(project_dir, 'targets')
targets_dst = os.path.join(dist_dir, 'targets')

if os.path.exists(targets_src):
    print(f"Copying {targets_src} to {targets_dst}...")
    if os.path.exists(targets_dst):
        shutil.rmtree(targets_dst)
    shutil.copytree(targets_src, targets_dst)
    print("Copy complete.")
else:
    print(f"Warning: {targets_src} does not exist, skipping copy.")
