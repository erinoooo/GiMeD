# gimed.spec — PyInstaller build spec
# Usage: pyinstaller gimed.spec

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
        # questionary + prompt_toolkit internals
        'questionary',
        'prompt_toolkit',
        'prompt_toolkit.input',
        'prompt_toolkit.output',
        'prompt_toolkit.filters',
        'prompt_toolkit.key_binding',
        'prompt_toolkit.shortcuts',
        # rich internals
        'rich',
        'rich.console',
        'rich.panel',
        'rich.progress',
        'rich.text',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
