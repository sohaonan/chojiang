# 抽奖系统

一个简单的抽奖系统，支持多个奖池、白名单功能和导入导出功能。

## 功能特点

- 支持多个奖池管理
- 支持白名单功能
- 支持从CSV和Word文件导入参与者
- 支持导出参与者列表
- 美观的抽奖动画效果
- 管理员密码保护

## 使用说明

1. 下载最新版本的 `lottery.exe`
2. 双击运行程序
3. 默认管理密码：123456
4. 可以在 `config.json` 中修改管理密码

## 开发环境

- Python 3.9+
- 依赖包：
  - python-docx
  - Pillow
  - py2app

## 构建说明

使用 GitHub Actions 自动构建 Windows 版本

## 本地开发环境设置

1. 安装 Python 3.9 或更高版本
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 本地运行

直接运行 Python 文件：
```bash
python lottery.py
```

注意：如果遇到编码错误，请确保：
1. Python 文件开头有编码声明：`# -*- coding: utf-8 -*-`
2. 使用 UTF-8 编码保存文件
3. 终端支持中文显示

## 本地打包

### Windows 系统
```bash
pyinstaller --noconfirm --onedir --windowed ^
  --add-data "config.json;." ^
  --add-data "logo.jpg;." ^
  --name "lottery" ^
  --hidden-import tkinter ^
  --hidden-import tkinter.ttk ^
  --hidden-import PIL ^
  --hidden-import PIL.Image ^
  --hidden-import PIL.ImageTk ^
  lottery.py
```

### macOS 系统
```bash
pyinstaller --noconfirm --onedir --windowed \
  --add-data "config.json:." \
  --add-data "logo.jpg:." \
  --name "lottery" \
  --hidden-import tkinter \
  --hidden-import tkinter.ttk \
  --hidden-import PIL \
  --hidden-import PIL.Image \
  --hidden-import PIL.ImageTk \
  lottery.py
```

## 打包后的文件结构

打包完成后，在 `dist/lottery` 目录下会生成以下文件：
- `lottery.exe`（Windows）或 `lottery`（macOS）：主程序
- `config.json`：配置文件
- `logo.jpg`：程序图标
- 其他必要的运行文件

## 配置文件说明

`config.json` 文件格式：
```json
{
  "admin": {
    "password": "123456"
  }
}
```

## 常见问题

1. 如果运行时提示缺少模块，请确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

2. 如果打包时出错，请确保：
   - Python 版本正确（3.9 或更高）
   - 所有依赖包都已安装
   - 所有资源文件（config.json, logo.jpg）都在正确的位置

3. 如果程序无法运行，请尝试：
   - 以管理员身份运行
   - 检查配置文件格式是否正确
   - 检查资源文件是否存在

4. 如果遇到编码问题：
   - 确保所有 Python 文件都使用 UTF-8 编码
   - 在文件开头添加 `# -*- coding: utf-8 -*-`
   - 使用支持中文的编辑器（如 VS Code、PyCharm 等） 