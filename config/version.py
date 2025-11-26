"""
版本信息模块
从 pyproject.toml 文件中读取版本信息
"""

import sys
from pathlib import Path
from typing import Optional


def get_version() -> str:
    """
    从 pyproject.toml 文件中读取版本号
    
    Returns:
        str: 版本号，如果读取失败则返回 "unknown"
    """
    try:
        # 尝试使用 tomllib (Python 3.11+)
        if sys.version_info >= (3, 11):
            import tomllib
            
            # 确定 pyproject.toml 文件路径
            if getattr(sys, 'frozen', False):
                # 打包后的可执行文件
                base_path = Path(sys._MEIPASS)
            else:
                # 开发环境
                base_path = Path(__file__).parent.parent
            
            pyproject_path = base_path / "pyproject.toml"
            
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    return data.get("project", {}).get("version", "unknown")
        
        # 回退到手动解析（兼容旧版本 Python）
        return _parse_version_manually()
        
    except Exception as e:
        print(f"读取版本号失败: {e}")
        return "unknown"


def _parse_version_manually() -> str:
    """
    手动解析 pyproject.toml 文件中的版本号
    用于兼容不支持 tomllib 的 Python 版本
    
    Returns:
        str: 版本号，如果读取失败则返回 "unknown"
    """
    try:
        # 确定 pyproject.toml 文件路径
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            base_path = Path(sys._MEIPASS)
        else:
            # 开发环境
            base_path = Path(__file__).parent.parent
        
        pyproject_path = base_path / "pyproject.toml"
        
        if not pyproject_path.exists():
            return "unknown"
        
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 简单的正则表达式解析版本号
        import re
        
        # 查找 version = "x.x.x" 模式
        version_pattern = r'version\s*=\s*["\']([^"\']+)["\']'
        match = re.search(version_pattern, content)
        
        if match:
            return match.group(1)
        
        return "unknown"
        
    except Exception as e:
        print(f"手动解析版本号失败: {e}")
        return "unknown"


def get_app_info() -> dict:
    """
    获取应用程序完整信息
    
    Returns:
        dict: 包含版本号、名称等信息的字典
    """
    try:
        # 确定 pyproject.toml 文件路径
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            base_path = Path(sys._MEIPASS)
        else:
            # 开发环境
            base_path = Path(__file__).parent.parent
        
        pyproject_path = base_path / "pyproject.toml"
        
        if not pyproject_path.exists():
            return {
                "name": "Redis TTK Client",
                "version": "unknown",
                "description": "基于 ttkbootstrap 的现代化 Redis 客户端",
                "author": "涵曦"
            }
        
        # 尝试使用 tomllib
        if sys.version_info >= (3, 11):
            import tomllib
            
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                project = data.get("project", {})
                
                # 获取作者信息
                authors = project.get("authors", [])
                author = authors[0].get("name", "涵曦") if authors else "涵曦"
                
                return {
                    "name": project.get("name", "redis-ttk"),
                    "version": project.get("version", "unknown"),
                    "description": project.get("description", "基于 ttkbootstrap 的现代化 Redis 客户端"),
                    "author": author
                }
        
        # 回退到手动解析
        return _parse_app_info_manually(pyproject_path)
        
    except Exception as e:
        print(f"读取应用信息失败: {e}")
        return {
            "name": "Redis TTK Client",
            "version": "unknown",
            "description": "基于 ttkbootstrap 的现代化 Redis 客户端",
            "author": "涵曦"
        }


def _parse_app_info_manually(pyproject_path: Path) -> dict:
    """
    手动解析应用程序信息
    
    Args:
        pyproject_path: pyproject.toml 文件路径
        
    Returns:
        dict: 应用程序信息
    """
    try:
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        import re
        
        # 解析各个字段
        name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
        author_match = re.search(r'name\s*=\s*["\']([^"\']+)["\'].*?email', content, re.DOTALL)
        
        return {
            "name": name_match.group(1) if name_match else "redis-ttk",
            "version": version_match.group(1) if version_match else "unknown",
            "description": desc_match.group(1) if desc_match else "基于 ttkbootstrap 的现代化 Redis 客户端",
            "author": author_match.group(1) if author_match else "涵曦"
        }
        
    except Exception as e:
        print(f"手动解析应用信息失败: {e}")
        return {
            "name": "Redis TTK Client",
            "version": "unknown",
            "description": "基于 ttkbootstrap 的现代化 Redis 客户端",
            "author": "涵曦"
        }
