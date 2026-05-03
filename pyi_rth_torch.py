# ============================================================
# PyInstaller Runtime Hook for PyTorch CUDA
# 文件名: pyi_rth_torch.py
# 
# 作用: 在 frozen exe 启动时，确保 torch 的 CUDA DLL 在 PATH 里，
#       这样 torch.cuda.is_available() 才能找到显卡。
# ============================================================

import os
import sys
import glob


def _add_torch_lib_to_path():
    """把 torch/lib/ 目录加到 PATH，CUDA 才能加载 DLL。"""
    if not getattr(sys, 'frozen', False):
        return  # dev 模式不需要

    base = sys._MEIPASS

    # 可能的 torch/lib 位置:
    # 1. sys._MEIPASS/torch/lib/
    # 2. sys._MEIPASS/ (DLL 直接在这一层)
    candidates = [
        os.path.join(base, 'torch', 'lib'),
        base,
    ]

    # 也搜索子目录 (PyInstaller 可能把 DLL 散落在不同位置)
    for d in candidates:
        if os.path.isdir(d):
            # 找到 cublas*.dll 或 _C*.pyd 才算有效
            dlls = glob.glob(os.path.join(d, 'cublas*.dll'))
            dlls += glob.glob(os.path.join(d, 'cudnn*.dll'))
            if dlls or (os.path.exists(os.path.join(d, 'nvrtc*.dll'))):
                path = os.environ.get('PATH', '')
                if d not in path:
                    os.environ['PATH'] = d + os.pathsep + path
                    print(f'[TorchHook] Added to PATH: {d}')
                return

    # 如果上面都找不到，扫描整个 _MEIPASS
    for root, dirs, files in os.walk(base):
        if any(f.startswith('cublas') and f.endswith('.dll') for f in files):
            path = os.environ.get('PATH', '')
            if root not in path:
                os.environ['PATH'] = root + os.pathsep + path
                print(f'[TorchHook] Added to PATH (scanned): {root}')
            return


_add_torch_lib_to_path()
