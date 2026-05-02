"""API 端到端测试 - 完整流程"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

BASE = 'http://localhost:5000'

# 1. 扫描
print("=== 1. 扫描 ===")
with open('test_sample.txt', 'rb') as f:
    r = requests.post(f'{BASE}/api/scan', files={'file': f})
data = r.json()
print(f"检测到: {data.get('total', 0)} 处")
print(f"类型分布: {json.dumps(data.get('by_type', {}), ensure_ascii=False)}")
upload_name = data.get('upload_name')

# 2. 执行脱敏
print("\n=== 2. 脱敏 ===")
r = requests.post(f'{BASE}/api/mask', json={'upload_name': upload_name})
data = r.json()
print(f"脱敏数量: {data.get('masked_count', 0)}")
output_file = data.get('output_file')
mapping_file = data.get('mapping_file')
print(f"输出: {output_file}, 映射: {mapping_file}")

# 3. 下载脱敏文件到本地（模拟真实用户下载）
print("\n=== 3. 下载脱敏文件 ===")
r = requests.get(f'{BASE}/api/download/{output_file}')
temp_file = os.path.join('uploads', '_test_masked.txt')
with open(temp_file, 'wb') as f:
    f.write(r.content)
print(f"已保存到: {temp_file} ({len(r.content)} bytes)")

# 4. 模拟用户上传脱敏文件进行还原
print("\n=== 4. 还原 ===")
with open(temp_file, 'rb') as f:
    r = requests.post(f'{BASE}/api/unmask',
                       files={'file': (output_file, f)},
                       data={'mapping': mapping_file})
data = r.json()
restored_file = data.get('output_file')
print(f"还原输出: {restored_file}")

# 5. 下载还原文件并对比
print("\n=== 5. 验证还原 ===")
r = requests.get(f'{BASE}/api/download/{restored_file}')
# 两个都按 binary 对比
original = open('test_sample.txt', 'rb').read()
restored = r.content
if restored == original:
    print("PASS: 还原后与原文完全一致（binary match）")
else:
    # 尝试忽略 \r 差异
    orig_norm = original.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    rest_norm = restored.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    if orig_norm == rest_norm:
        print("PASS: 还原后与原文一致（忽略换行符差异）")
    else:
        print("FAIL: 还原后与原文不一致")
        print(f"原文长度: {len(original)}, 还原长度: {len(restored)}")

# 清理
os.remove(temp_file)
print("\n全部测试完成")
