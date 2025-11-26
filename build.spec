# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# 项目根目录
project_root = Path(SPECPATH)

# 应用程序配置
app_name = "redis-ttk"
main_script = "main.py"

# 数据文件和隐藏导入
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
    "redis",
    "redis.connection",
    "redis.client",
    "tkinter",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.filedialog",
]

# 收集所有 ttkbootstrap 相关文件
collect_all = [
    "ttkbootstrap",
]

# 排除的模块
excludes = [
    "pytest",
    "unittest",
    "test",
    "tests",
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

# 收集所有指定的包
for pkg in collect_all:
    a.datas += collect_all_packages(pkg)

# PYZ 配置
pyz = PYZ(a.pure)

# 可执行文件配置
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 应用程序，不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows 特定配置
    version=None,
    uac_admin=False,
    uac_uiaccess=False,
    # macOS 特定配置
    bundle_identifier=None,
)

# macOS 应用程序包配置（可选）
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name=f"{app_name}.app",
        icon=None,
        bundle_identifier="com.redis-ttk.app",
        info_plist={
            "NSPrincipalClass": "NSApplication",
            "NSAppleScriptEnabled": False,
            "CFBundleDocumentTypes": [],
        },
    )
