#!/bin/bash

# Redis-TTK Linux 打包脚本

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

# 检查系统环境
check_environment() {
    log_info "检查系统环境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装或不在 PATH 中"
        exit 1
    fi
    
    if ! command -v pdm &> /dev/null; then
        log_error "PDM 未安装，请运行: pip install pdm"
        exit 1
    fi
    
    log_success "系统环境检查通过"
}

# 清理旧的构建文件
clean_build() {
    log_info "清理旧的构建文件..."
    
    rm -rf build/
    rm -rf dist/
    
    log_success "构建文件清理完成"
}

# 安装构建依赖
install_build_deps() {
    log_info "安装构建依赖..."
    
    # 确保安装了构建依赖
    pdm add -dG build pyinstaller
    
    log_success "构建依赖安装完成"
}

# 检查现有的 spec 文件
check_spec_file() {
    log_info "检查 PyInstaller spec 文件..."
    
    if [[ -f "build.spec" ]]; then
        log_success "找到现有的 build.spec 文件，将使用它进行打包"
        return 0
    else
        log_error "未找到 build.spec 文件"
        log_info "请确保项目根目录下存在 build.spec 文件"
        exit 1
    fi
}

# 执行打包
build_app() {
    log_info "开始打包应用程序..."
    
    # 使用现有的 build.spec 文件进行打包
    pdm run pyinstaller build.spec --clean --noconfirm
    
    if [[ $? -eq 0 ]]; then
        log_success "应用程序打包完成"
    else
        log_error "打包失败"
        exit 1
    fi
}

# 修复应用程序权限
fix_permissions() {
    log_info "修复应用程序权限..."
    
    local exe_path="dist/Redis-TTK"
    
    if [[ -f "$exe_path" ]]; then
        # 修复可执行文件权限
        chmod +x "$exe_path"
        
        log_success "权限修复完成"
    else
        log_error "找不到可执行文件: $exe_path"
        exit 1
    fi
}

# 验证可执行文件
verify_executable() {
    log_info "验证可执行文件..."
    
    local exe_path="dist/Redis-TTK"
    
    if [[ -f "$exe_path" ]]; then
        file "$exe_path"
        ls -la "$exe_path"
        log_success "Linux 可执行文件验证完成"
    else
        log_error "找不到可执行文件进行验证"
        exit 1
    fi
}

# 显示构建结果
show_results() {
    log_info "构建结果:"
    echo
    
    local exe_path="dist/Redis-TTK"
    
    if [[ -f "$exe_path" ]]; then
        local exe_size=$(du -sh "$exe_path" | cut -f1)
        echo "✅ 可执行文件: $exe_path (大小: $exe_size)"
    fi
    
    echo
    log_info "使用方法:"
    echo "1. 直接运行: ./Redis-TTK"
    echo "2. 或者复制到系统 PATH 中"
}

# 显示帮助信息
show_help() {
    echo "Redis-TTK Linux 打包脚本"
    echo
    echo "用法:"
    echo "  $0 [选项]"
    echo
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -c, --clean    仅清理构建文件"
    echo "  --no-verify    跳过可执行文件验证"
    echo
    echo "此脚本将:"
    echo "1. 检查系统环境和依赖"
    echo "2. 清理旧的构建文件"
    echo "3. 安装构建依赖"
    echo "4. 检查现有的 build.spec 文件"
    echo "5. 使用 build.spec 执行打包"
    echo "6. 修复权限问题"
    echo "7. 验证可执行文件"
    echo
}

# 主函数
main() {
    local skip_verify=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--clean)
                clean_build
                log_success "清理完成"
                exit 0
                ;;
            --no-verify)
                skip_verify=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "开始 Redis-TTK Linux 打包流程..."
    echo
    
    # 执行构建步骤
    check_environment
    clean_build
    install_build_deps
    check_spec_file
    build_app
    fix_permissions
    
    if [[ "$skip_verify" != true ]]; then
        verify_executable
    fi
    
    show_results
    
    log_success "打包流程完成！"
}

# 运行主函数
main "$@"
