# -*- mode: python ; coding: utf-8 -*-

# ============================================================
# PianoTrans PyInstaller Spec - 全量打包 (含 PyTorch + CUDA)
# 预计体积: 4-5 GB，打包时间: 15-30 分钟
# ============================================================

import os
import sys

block_cipher = None

# ---- 项目路径 ----
PROJECT_DIR = os.path.dirname(os.path.abspath(SPECPATH))

# ---- 收集所有 torch 内容 (包括 CUDA DLL) ----
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# torch 全套
torch_binaries, torch_datas, torch_hiddenimports = collect_all('torch')

# torchvision (如果装了的话)
try:
    tv_binaries, tv_datas, tv_hiddenimports = collect_all('torchvision')
except Exception:
    tv_binaries, tv_datas, tv_hiddenimports = [], [], []

# torchaudio
try:
    ta_binaries, ta_datas, ta_hiddenimports = collect_all('torchaudio')
except Exception:
    ta_binaries, ta_datas, ta_hiddenimports = [], [], []

# librosa 数据文件
librosa_datas = collect_data_files('librosa')

# numba 数据 + 隐藏导入
numba_datas = collect_data_files('numba')
numba_hidden = collect_submodules('numba')

# sklearn
sklearn_hidden = collect_submodules('sklearn')
sklearn_datas = collect_data_files('sklearn')

# soundfile
try:
    sf_datas = collect_data_files('soundfile')
except Exception:
    sf_datas = []

# ---- 汇编所有数据 ----
all_datas = (
    librosa_datas +
    numba_datas +
    sklearn_datas +
    sf_datas +
    torch_datas +
    tv_datas +
    ta_datas
)

# ---- 汇编所有隐藏导入 ----
hiddenimports = list(set(
    torch_hiddenimports +
    tv_hiddenimports +
    ta_hiddenimports +
    numba_hidden +
    sklearn_hidden +
    [
        # sklearn 特定
        'sklearn.neighbors._partition_nodes',
        'sklearn.utils._typedefs',
        'sklearn.utils._weight_vector',
        'sklearn.utils._cython_blas',
        # numba
        'numba.cuda',
        'numba.cuda.cudadrv',
        'numba.cuda.cudadrv.driver',
        # 音频
        'resampy',
        'audioread',
        'audioread.ffdec',
        'soundfile',
        'soundfile._soundfile',
        # 项目
        'piano_transcription_inference',
        'piano_transcription_inference.models',
        'piano_transcription_inference.pytorch_utils',
        'piano_transcription_inference.utilities',
        'piano_transcription_inference.config',
        'piano_transcription_inference.piano_vad',
        'torchlibrosa',
        'torchlibrosa.stft',
        # tkinter (GUI)
        'tkinter',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
        # misc
        'mido',
        'matplotlib',
        'matplotlib.backends.backend_agg',
        'librosa',
        'librosa.beat',
        'librosa.onset',
        'scipy',
        'numpy',
        'pooch',
        'soxr',
        'lazy_loader',
    ]
))

# ---- 开始分析 ----
a = Analysis(
    [os.path.join(PROJECT_DIR, 'PianoTrans.py')],
    pathex=[PROJECT_DIR],
    binaries=torch_binaries + tv_binaries + ta_binaries,
    datas=all_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[
        os.path.join(PROJECT_DIR, 'pyi_rth_torch.py'),
    ],
    excludes=[
        'tkinter.test',
        'matplotlib.tests',
        'scipy.tests',
        'numpy.tests',
        'numba.tests',
        'librosa.tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ---- PYZ ----
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ---- EXE ----
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PianoTrans',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,          # 保留控制台看日志
    icon=None,
)

# ---- COLLECT: 所有内容打包到一个文件夹 ----
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,             # 关掉 UPX，CUDA DLL 压缩后可能损坏
    upx_exclude=[],
    name='PianoTrans',
)
