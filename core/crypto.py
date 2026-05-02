"""
映射表加密存储
使用 Fernet 对称加密保护映射表
"""
import json
import os
from cryptography.fernet import Fernet


class CryptoManager:
    """映射表加密管理器"""

    def __init__(self, key_file):
        self.key_file = key_file
        self.fernet = Fernet(self._load_or_create_key())

    def _load_or_create_key(self):
        """加载或生成密钥"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def save_mapping(self, mapping, filepath):
        """加密保存映射表"""
        data = json.dumps(mapping, ensure_ascii=False).encode('utf-8')
        encrypted = self.fernet.encrypt(data)
        with open(filepath, 'wb') as f:
            f.write(encrypted)

    def load_mapping(self, filepath):
        """解密读取映射表"""
        with open(filepath, 'rb') as f:
            encrypted = f.read()
        data = self.fernet.decrypt(encrypted)
        return json.loads(data.decode('utf-8'))

    def list_mappings(self, mapping_dir):
        """列出所有映射表文件"""
        results = []
        if not os.path.exists(mapping_dir):
            return results
        for fname in sorted(os.listdir(mapping_dir), reverse=True):
            if fname.endswith('.enc'):
                fpath = os.path.join(mapping_dir, fname)
                stat = os.stat(fpath)
                results.append({
                    'filename': fname,
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                })
        return results
