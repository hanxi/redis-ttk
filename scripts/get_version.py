#!/usr/bin/env python3
"""
版本号读取脚本
从 pyproject.toml 中读取项目版本号
"""

import sys
import tomllib
from pathlib import Path


def get_version():
    """从 pyproject.toml 读取版本号"""
    try:
        # 获取项目根目录
        project_root = Path(__file__).parent.parent
        pyproject_path = project_root / "pyproject.toml"
        
        if not pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")
        
        # 读取 pyproject.toml
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        
        # 获取版本号
        version = data.get("project", {}).get("version")
        if not version:
            raise ValueError("Version not found in pyproject.toml")
        
        return version
    
    except Exception as e:
        print(f"Error reading version: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """主函数"""
    version = get_version()
    print(version)


if __name__ == "__main__":
    main()
