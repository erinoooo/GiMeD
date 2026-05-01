# gimed.spec — PyInstaller build spec
block_cipher = None

a = Analysis(
    ['gimed/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'gimed.cli',
        'gimed.ui',
        'gimed.system',
        'gimed.desktop',
        'gimed.xrdp',
        'gimed.wireguard',
        'simple_term_menu',
        'rich',
        'rich.console',
        'rich.panel',
        'rich.progress',
        'rich.text',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gimed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    onefile=True,
)
