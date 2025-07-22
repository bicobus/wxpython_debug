# -*- coding: utf-8 -*-
# © 2025 bicobus <bicobus@keemail.me>

import sys
from cx_Freeze import setup, Executable

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('previewframe.py', base=base, target_name='previewframe.exe')
]
buildexe = {
    'include_msvcr': True
}

setup(
    executables=executables,
    options={
        "build_exe": buildexe
    }
)
