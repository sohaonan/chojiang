@echo off
setlocal

echo 开始打包 Windows 版本...

:: 清理旧的构建文件
rmdir /s /q build dist

:: 使用 PyInstaller 打包 Windows 版本
pyinstaller --noconfirm --onedir --windowed ^
    --add-data "config.json;." ^
    --add-data "logo.jpg;." ^
    --name "抽奖程序" ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --hidden-import PIL.ImageTk ^
    lottery.py

:: 复制配置文件到应用程序目录
copy config.json "dist\抽奖程序\"

:: 创建说明文档
echo 使用说明：> "dist\抽奖程序\使用说明.txt"
echo 1. 双击"抽奖程序.exe"运行程序>> "dist\抽奖程序\使用说明.txt"
echo 2. 如果无法运行，请右键选择"以管理员身份运行">> "dist\抽奖程序\使用说明.txt"
echo 3. 配置文件 config.json 可以修改管理密码>> "dist\抽奖程序\使用说明.txt"

echo 打包完成！
echo 程序已生成在 dist\抽奖程序 目录下
pause 