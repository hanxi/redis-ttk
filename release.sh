#!/bin/bash

# Redis-TTK 发布脚本
# 自动更新版本号、创建 git tag 并触发 GitHub Actions 构建

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装或不在 PATH 中"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装或不在 PATH 中"
        exit 1
    fi
    
    if ! command -v pdm &> /dev/null; then
        log_error "PDM 未安装或不在 PATH 中"
        log_info "请运行: pip install pdm"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 获取当前版本
get_current_version() {
    python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
print(data['project']['version'])
"
}

# 更新版本号
update_version() {
    local new_version=$1
    log_info "更新版本号到 $new_version"
    
    # 使用 Python 脚本更新版本号
    python3 -c "
import tomllib
import re

# 读取当前配置
with open('pyproject.toml', 'rb') as f:
    content = f.read().decode('utf-8')

# 替换版本号
new_content = re.sub(
    r'version = \"[^\"]+\"',
    f'version = \"$new_version\"',
    content
)

# 写回文件
with open('pyproject.toml', 'w', encoding='utf-8') as f:
    f.write(new_content)
"
    
    log_success "版本号已更新到 $new_version"
}

# 验证版本号格式
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "版本号格式无效: $version"
        log_info "请使用语义化版本格式: x.y.z (例如: 1.0.0)"
        return 1
    fi
    return 0
}

# 增加版本号
increment_version() {
    local current_version=$1
    local increment_type=$2
    
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case $increment_type in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
        *)
            log_error "无效的版本增加类型: $increment_type"
            return 1
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# 检查工作目录状态
check_git_status() {
    log_info "检查 Git 工作目录状态..."
    
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "当前目录不是 Git 仓库"
        exit 1
    fi
    
    if [[ -n $(git status --porcelain) ]]; then
        log_warning "工作目录有未提交的更改"
        echo "未提交的文件:"
        git status --short
        echo
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "发布已取消"
            exit 0
        fi
    fi
    
    log_success "Git 状态检查通过"
}

# 创建并推送 tag
create_and_push_tag() {
    local version=$1
    local tag_name="v$version"
    
    log_info "创建 Git tag: $tag_name"
    
    # 检查 tag 是否已存在
    if git rev-parse "$tag_name" >/dev/null 2>&1; then
        log_error "Tag $tag_name 已存在"
        exit 1
    fi
    
    # 提交版本更改
    git add pyproject.toml
    git commit -m "chore: bump version to $version" || {
        log_warning "没有需要提交的更改"
    }
    
    # 创建 tag
    git tag -a "$tag_name" -m "Release version $version"
    
    # 推送到远程
    log_info "推送到远程仓库..."
    git push origin main || git push origin master
    git push origin "$tag_name"
    
    log_success "Tag $tag_name 已创建并推送"
    log_info "GitHub Actions 将自动开始构建..."
}

# 显示帮助信息
show_help() {
    echo "Redis-TTK 发布脚本"
    echo
    echo "用法:"
    echo "  $0 [选项] [版本号]"
    echo
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -p, --patch    增加补丁版本号 (x.y.z -> x.y.z+1)"
    echo "  -m, --minor    增加次版本号 (x.y.z -> x.y+1.0)"
    echo "  -M, --major    增加主版本号 (x.y.z -> x+1.0.0)"
    echo
    echo "示例:"
    echo "  $0 --patch           # 自动增加补丁版本"
    echo "  $0 --minor           # 自动增加次版本"
    echo "  $0 --major           # 自动增加主版本"
    echo "  $0 1.2.3             # 设置为指定版本"
    echo
}

# 主函数
main() {
    log_info "开始 Redis-TTK 发布流程..."
    
    # 检查依赖
    check_dependencies
    
    # 检查 Git 状态
    check_git_status
    
    # 获取当前版本
    current_version=$(get_current_version)
    log_info "当前版本: $current_version"
    
    local new_version=""
    local increment_type=""
    
    # 解析命令行参数
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--patch)
            increment_type="patch"
            ;;
        -m|--minor)
            increment_type="minor"
            ;;
        -M|--major)
            increment_type="major"
            ;;
        "")
            # 交互式选择
            echo "请选择版本增加类型:"
            echo "1) Patch (补丁版本: $current_version -> $(increment_version "$current_version" "patch"))"
            echo "2) Minor (次版本: $current_version -> $(increment_version "$current_version" "minor"))"
            echo "3) Major (主版本: $current_version -> $(increment_version "$current_version" "major"))"
            echo "4) Custom (自定义版本)"
            echo
            read -p "请选择 (1-4): " -n 1 -r choice
            echo
            
            case $choice in
                1) increment_type="patch" ;;
                2) increment_type="minor" ;;
                3) increment_type="major" ;;
                4) 
                    read -p "请输入新版本号: " new_version
                    if ! validate_version "$new_version"; then
                        exit 1
                    fi
                    ;;
                *)
                    log_error "无效选择"
                    exit 1
                    ;;
            esac
            ;;
        *)
            # 直接指定版本号
            new_version="$1"
            if ! validate_version "$new_version"; then
                exit 1
            fi
            ;;
    esac
    
    # 计算新版本号
    if [[ -n "$increment_type" ]]; then
        new_version=$(increment_version "$current_version" "$increment_type")
    fi
    
    log_info "新版本: $new_version"
    
    # 确认发布
    echo
    read -p "确认发布版本 $new_version? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "发布已取消"
        exit 0
    fi
    
    # 更新版本号
    update_version "$new_version"
    
    # 创建并推送 tag
    create_and_push_tag "$new_version"
    
    log_success "发布流程完成!"
    log_info "请访问 GitHub Actions 页面查看构建进度"
    log_info "构建完成后，可执行文件将在 GitHub Releases 页面发布"
}

# 运行主函数
main "$@"
