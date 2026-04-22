# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Definimos los archivos y carpetas a incluir
added_files = [
    ('src', 'src'),  # Incluimos el código fuente para asegurar rutas internas
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'pdf2docx', 
        'docx2pdf', 
        'PIL', 
        'pypdf',
        'docx',
        'fitz',  # PyMuPDF
        'pdfplumber',
        'docx.enum.text',
        'docx.oxml.ns'
    ],
    hookspath=[],
    hooksconfig={},
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
    name='PDFProcessor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False oculta la consola negra al abrir la app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
