# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# 项目根目录
project_root = Path(SPECPATH)

# 应用程序配置
app_name = "Redis-TTK"
main_script = "main.py"

# 数据文件
datas = [
    (str(project_root / "config"), "config"),
    (str(project_root / "gui"), "gui"),
]

# 隐藏导入模块
hiddenimports = [
    "ttkbootstrap",
    "ttkbootstrap.themes",
    "ttkbootstrap.style",
    "ttkbootstrap.constants",
    "ttkbootstrap.utility",
    "ttkbootstrap.validation",
    "ttkbootstrap.scrolled",
    "ttkbootstrap.dialogs",
    "ttkbootstrap.tooltip",
    "ttkbootstrap.tableview",
    "ttkbootstrap.toast",
    "redis",
    "redis.connection",
    "redis.client",
    "redis.exceptions",
    "redis.sentinel",
    "redis.retry",
    "redis.backoff",
    "tkinter",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.filedialog",
    "tkinter.simpledialog",
    "tkinter.colorchooser",
    "tkinter.font",
    "json",
    "configparser",
    "threading",
    "queue",
    "datetime",
    "pathlib",
    "typing",
]

# 排除的模块
excludes = [
    "pytest",
    "unittest",
    "test",
    "tests",
    "setuptools",
    "pip",
    "wheel",
]

# 分析配置
a = Analysis(
    [main_script],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

# 手动添加 ttkbootstrap 主题文件
try:
    import ttkbootstrap
    ttkbootstrap_path = Path(ttkbootstrap.__file__).parent
    
    # 添加 ttkbootstrap 包目录下的所有文件
    for item in ttkbootstrap_path.rglob("*"):
        if item.is_file() and not item.name.startswith('.'):
            rel_path = item.relative_to(ttkbootstrap_path.parent)
            a.datas.append((str(rel_path), str(item), "DATA"))
            
except ImportError:
    pass

# PYZ 配置
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 可执行文件配置
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 收集文件
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)

# macOS 应用程序包配置
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{app_name}.app",
        icon=None,
        bundle_identifier="com.redis-ttk.app",
        version="0.1.2",
        info_plist={
            "NSPrincipalClass": "NSApplication",
            "NSAppleScriptEnabled": False,
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "10.13.0",
            "CFBundleDocumentTypes": [],
            "CFBundleURLTypes": [],
            "NSRequiresAquaSystemAppearance": False,
            "LSApplicationCategoryType": "public.app-category.developer-tools",
            "CFBundleShortVersionString": "0.1.2",
            "CFBundleVersion": "0.1.2",
            "NSHumanReadableCopyright": "Copyright © 2024 涵曦. All rights reserved.",
        },
    )
