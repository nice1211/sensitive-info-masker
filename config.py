import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 服务端口
PORT = 5000

# 目录配置
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
MAPPING_DIR = os.path.join(BASE_DIR, 'mappings')

# 加密密钥文件路径
KEY_FILE = os.path.join(BASE_DIR, '.secret_key')

# 自定义敏感词列表
CUSTOM_NAMES_FILE = os.path.join(BASE_DIR, 'custom_names.txt')

# 支持的文件扩展名
ALLOWED_EXTENSIONS = {'.txt', '.md', '.csv', '.docx', '.xlsx'}

# 确保目录存在
for d in [UPLOAD_DIR, OUTPUT_DIR, MAPPING_DIR]:
    os.makedirs(d, exist_ok=True)
