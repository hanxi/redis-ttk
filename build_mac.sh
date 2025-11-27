#!/bin/bash

# Redis-TTK macOS 打包脚本
# 解决 macOS 应用打包和运行问题

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
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "此脚本仅支持 macOS 系统"
        exit 1
    fi
    
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
    
    # 确保安装了构建依赖，使用项目配置中的版本约束
    pdm install -dG build
    
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
    
    local app_path="dist/Redis-TTK.app"
    
    if [[ -d "$app_path" ]]; then
        # 修复可执行文件权限
        chmod +x "$app_path/Contents/MacOS/Redis-TTK"
        
        # 修复整个应用包的权限
        find "$app_path" -type f -name "*.so" -exec chmod +x {} \;
        find "$app_path" -type f -name "*.dylib" -exec chmod +x {} \;
        
        log_success "权限修复完成"
    else
        log_error "找不到应用程序包: $app_path"
        exit 1
    fi
}

# 测试应用程序
test_app() {
    log_info "测试应用程序..."
    
    local app_path="dist/Redis-TTK.app"
    
    if [[ -d "$app_path" ]]; then
        log_info "尝试启动应用程序..."
        
        # 在后台启动应用程序
        open "$app_path" &
        local open_pid=$!
        
        # 等待应用启动
        sleep 5
        
        # 检查应用是否在运行（使用更精确的进程名匹配）
        if pgrep -f "Redis-TTK.app" > /dev/null || pgrep -f "redis-ttk" > /dev/null; then
            log_success "应用程序启动成功！"
            log_info "应用程序正在运行中，请检查是否正常显示"
            log_info "测试完成后，应用程序将继续运行，您可以手动关闭它"
        else
            # 检查应用程序包是否存在且可执行
            local exe_path="$app_path/Contents/MacOS/redis-ttk"
            if [[ -x "$exe_path" ]]; then
                log_warning "应用程序包存在但可能启动失败"
                log_info "您可以尝试手动双击应用程序或检查系统日志"
                log_info "如果遇到安全提示，请在系统偏好设置 -> 安全性与隐私中允许运行"
            else
                log_error "应用程序可执行文件不存在或无执行权限"
            fi
        fi
    else
        log_error "找不到应用程序包进行测试"
    fi
}

# 创建 DMG 文件（可选）
create_dmg() {
    log_info "是否创建 DMG 安装包？(y/N)"
    read -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "创建 DMG 安装包..."
        
        local app_path="dist/Redis-TTK.app"
        local dmg_path="dist/Redis-TTK.dmg"
        
        if [[ -d "$app_path" ]]; then
            # 创建临时目录
            local temp_dir=$(mktemp -d)
            cp -R "$app_path" "$temp_dir/"
            
            # 创建 DMG
            hdiutil create -volname "Redis-TTK" -srcfolder "$temp_dir" -ov -format UDZO "$dmg_path"
            
            # 清理临时目录
            rm -rf "$temp_dir"
            
            if [[ -f "$dmg_path" ]]; then
                log_success "DMG 文件创建完成: $dmg_path"
            else
                log_error "DMG 文件创建失败"
            fi
        else
            log_error "找不到应用程序包"
        fi
    fi
}

# 显示构建结果
show_results() {
    log_info "构建结果:"
    echo
    
    local app_path="dist/Redis-TTK.app"
    local dmg_path="dist/Redis-TTK.dmg"
    
    if [[ -d "$app_path" ]]; then
        local app_size=$(du -sh "$app_path" | cut -f1)
        echo "✅ 应用程序包: $app_path (大小: $app_size)"
    fi
    
    if [[ -f "$dmg_path" ]]; then
        local dmg_size=$(du -sh "$dmg_path" | cut -f1)
        echo "✅ DMG 安装包: $dmg_path (大小: $dmg_size)"
    fi
    
    echo
    log_info "使用方法:"
    echo "1. 双击 Redis-TTK.app 直接运行"
    echo "2. 或者拖拽到 Applications 文件夹安装"
    echo "3. 如果遇到安全提示，请在系统偏好设置 -> 安全性与隐私中允许运行"
}

# 显示帮助信息
show_help() {
    echo "Redis-TTK macOS 打包脚本"
    echo
    echo "用法:"
    echo "  $0 [选项]"
    echo
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -c, --clean    仅清理构建文件"
    echo "  --no-test      跳过应用程序测试"
    echo "  --no-dmg       跳过 DMG 创建"
    echo
    echo "此脚本将:"
    echo "1. 检查系统环境和依赖"
    echo "2. 清理旧的构建文件"
    echo "3. 安装构建依赖"
    echo "4. 检查现有的 build.spec 文件"
    echo "5. 使用 build.spec 执行打包"
    echo "6. 修复权限问题"
    echo "7. 测试应用程序"
    echo "8. 可选创建 DMG 安装包"
    echo
}

# 主函数
main() {
    local skip_test=false
    local skip_dmg=false
    
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
            --no-test)
                skip_test=true
                shift
                ;;
            --no-dmg)
                skip_dmg=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "开始 Redis-TTK macOS 打包流程..."
    echo
    
    # 执行构建步骤
    check_environment
    clean_build
    install_build_deps
    check_spec_file
    build_app
    fix_permissions
    
    if [[ "$skip_test" != true ]]; then
        test_app
    fi
    
    if [[ "$skip_dmg" != true ]]; then
        create_dmg
    fi
    
    show_results
    
    log_success "打包流程完成！"
}

# 运行主函数
main "$@"
