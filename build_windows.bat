@echo off
REM Redis-TTK Windows 打包脚本

setlocal enabledelayedexpansion

REM 颜色定义（Windows 10+ 支持 ANSI 转义序列）
REM 检查是否禁用颜色输出
if defined NO_COLOR (
    set "RED="
    set "GREEN="
    set "YELLOW="
    set "BLUE="
    set "NC="
) else if defined FORCE_COLOR (
    if "%FORCE_COLOR%"=="0" (
        set "RED="
        set "GREEN="
        set "YELLOW="
        set "BLUE="
        set "NC="
    ) else (
        set "RED=[31m"
        set "GREEN=[32m"
        set "YELLOW=[33m"
        set "BLUE=[34m"
        set "NC=[0m"
    )
) else (
    set "RED=[31m"
    set "GREEN=[32m"
    set "YELLOW=[33m"
    set "BLUE=[34m"
    set "NC=[0m"
)

REM 日志函数
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM 检查系统环境
:check_environment
call :log_info "检查系统环境..."

python --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Python 未安装或不在 PATH 中"
    exit /b 1
)

pdm --version >nul 2>&1
if errorlevel 1 (
    call :log_error "PDM 未安装，请运行: pip install pdm"
    exit /b 1
)

call :log_success "系统环境检查通过"
goto :eof

REM 清理旧的构建文件
:clean_build
call :log_info "清理旧的构建文件..."

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

call :log_success "构建文件清理完成"
goto :eof

REM 安装构建依赖
:install_build_deps
call :log_info "安装构建依赖..."

pdm lock
pdm install -dG build
if errorlevel 1 (
    call :log_error "构建依赖安装失败"
    exit /b 1
)

call :log_success "构建依赖安装完成"
goto :eof

REM 检查现有的 spec 文件
:check_spec_file
call :log_info "检查 PyInstaller spec 文件..."

if exist build.spec (
    call :log_success "找到现有的 build.spec 文件，将使用它进行打包"
) else (
    call :log_error "未找到 build.spec 文件"
    call :log_info "请确保项目根目录下存在 build.spec 文件"
    exit /b 1
)
goto :eof

REM 执行打包
:build_app
call :log_info "开始打包应用程序..."

pdm run pyinstaller build.spec --clean --noconfirm
if errorlevel 1 (
    call :log_error "打包失败"
    exit /b 1
)

call :log_success "应用程序打包完成"
goto :eof

REM 修复可执行文件名称
:fix_executable_name
call :log_info "修复可执行文件名称..."

REM 检查可能的可执行文件名称
set "found_exe="
if exist "dist\Redis-TTK.exe" (
    set "found_exe=dist\Redis-TTK.exe"
) else if exist "dist\redis-ttk.exe" (
    set "found_exe=dist\redis-ttk.exe"
) else if exist "dist\main.exe" (
    set "found_exe=dist\main.exe"
)

if not "%found_exe%"=="" (
    REM 如果文件名不是 redis-ttk.exe，重命名它
    if not "%found_exe%"=="dist\redis-ttk.exe" (
        move "%found_exe%" "dist\redis-ttk.exe"
        call :log_info "重命名可执行文件: %found_exe% -> dist\redis-ttk.exe"
    )
    call :log_success "可执行文件名称修复完成"
) else (
    call :log_error "找不到可执行文件，检查的路径: Redis-TTK.exe, redis-ttk.exe, main.exe"
    call :log_info "dist 目录内容："
    if exist dist dir dist
    exit /b 1
)
goto :eof

REM 验证可执行文件
:verify_executable
call :log_info "验证可执行文件..."

set "exe_path=dist\redis-ttk.exe"

if exist "%exe_path%" (
    dir "%exe_path%"
    call :log_success "Windows 可执行文件验证完成"
) else (
    call :log_error "找不到可执行文件进行验证"
    call :log_info "dist 目录内容："
    if exist dist dir dist
    exit /b 1
)
goto :eof

REM 显示构建结果
:show_results
call :log_info "构建结果:"
echo.

set "exe_path=dist\redis-ttk.exe"

if exist "%exe_path%" (
    for %%A in ("%exe_path%") do set "exe_size=%%~zA"
    set /a "exe_size_mb=!exe_size! / 1048576"
    echo ✅ 可执行文件: %exe_path% (大小: !exe_size_mb! MB)
)

echo.
call :log_info "使用方法:"
echo 1. 双击 redis-ttk.exe 直接运行
echo 2. 或者在命令行中运行: redis-ttk.exe
goto :eof

REM 显示帮助信息
:show_help
echo Redis-TTK Windows 打包脚本
echo.
echo 用法:
echo   %~nx0 [选项]
echo.
echo 选项:
echo   -h, --help     显示此帮助信息
echo   -c, --clean    仅清理构建文件
echo   --no-verify    跳过可执行文件验证
echo.
echo 此脚本将:
echo 1. 检查系统环境和依赖
echo 2. 清理旧的构建文件
echo 3. 安装构建依赖
echo 4. 检查现有的 build.spec 文件
echo 5. 使用 build.spec 执行打包
echo 6. 验证可执行文件
echo.
goto :eof

REM 主函数
:main
set "skip_verify=false"

REM 解析命令行参数
:parse_args
if "%~1"=="" goto :start_build
if "%~1"=="-h" goto :show_help_and_exit
if "%~1"=="--help" goto :show_help_and_exit
if "%~1"=="-c" goto :clean_and_exit
if "%~1"=="--clean" goto :clean_and_exit
if "%~1"=="--no-verify" (
    set "skip_verify=true"
    shift
    goto :parse_args
)

call :log_error "未知选项: %~1"
call :show_help
exit /b 1

:show_help_and_exit
call :show_help
exit /b 0

:clean_and_exit
call :clean_build
call :log_success "清理完成"
exit /b 0

:start_build
call :log_info "开始 Redis-TTK Windows 打包流程..."
echo.

REM 执行构建步骤
call :check_environment
if errorlevel 1 exit /b 1

call :clean_build
if errorlevel 1 exit /b 1

call :install_build_deps
if errorlevel 1 exit /b 1

call :check_spec_file
if errorlevel 1 exit /b 1

call :build_app
if errorlevel 1 exit /b 1

call :fix_executable_name
if errorlevel 1 exit /b 1

if "%skip_verify%"=="false" (
    call :verify_executable
    if errorlevel 1 exit /b 1
)

call :show_results

call :log_success "打包流程完成！"
goto :eof

REM 运行主函数
call :main %*
