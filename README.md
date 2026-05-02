# 🔒 敏感信息加密工具

本地运行的敏感信息脱敏工具，自动检测并替换文件中的敏感信息，**数据不出本机**。

## ✨ 功能特性

- 🔍 **智能检测** - 自动识别姓名、手机号、身份证号、银行卡号、邮箱、公司名、地址等
- 🛡️ **一键脱敏** - 将敏感信息替换为安全的占位符
- 🔓 **精确还原** - 通过加密映射表，随时还原原始内容
- 📝 **自定义词库** - 支持添加自定义敏感词（人名、公司名、项目名等）
- 📂 **多格式支持** - txt / md / csv / docx / xlsx
- 🔐 **本地加密** - 映射表使用 Fernet 加密存储，密钥仅存本地

## 🚀 快速开始

### 方式一：双击启动
直接双击 `启动.bat`，自动安装依赖并打开浏览器。

### 方式二：手动启动
```bash
pip install -r requirements.txt
python app.py
```
访问 http://localhost:5000

## 📖 使用流程

1. **脱敏**：上传文件 → 查看检测结果 → 确认脱敏 → 下载脱敏文件
2. **处理**：将脱敏后的文件交给 AI / 第三方处理
3. **还原**：上传处理后的文件 + 选择映射表 → 一键还原

## 🛠️ 技术栈

- **后端**: Python / Flask
- **前端**: HTML / CSS / JavaScript
- **加密**: cryptography (Fernet)

## 📁 项目结构

```
├── app.py              # Flask 主应用
├── config.py           # 配置文件
├── core/               # 核心引擎
│   ├── detector.py     # 敏感信息检测器
│   ├── masker.py       # 脱敏/还原处理
│   └── crypto.py       # 加密模块
├── handlers/           # 文件格式处理器
│   ├── text_handler.py
│   ├── docx_handler.py
│   └── xlsx_handler.py
├── static/             # 前端资源
├── requirements.txt
└── 启动.bat            # Windows 一键启动
```

## 📄 License

MIT
