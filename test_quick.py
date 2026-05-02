"""快速测试检测引擎"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.detector import SensitiveDetector
from core.masker import Masker

text = open('test_sample.txt', 'r', encoding='utf-8').read()

print("=== 检测结果 ===")
d = SensitiveDetector()
results = d.detect(text)
for r in results:
    print(f"  {r['type']:12s} | {r['value']}")

print(f"\n共检测到 {len(results)} 处敏感信息")

print("\n=== 脱敏测试 ===")
m = Masker()
masked, mapping = m.mask_text(text, results)
print(masked)

print("\n=== 映射表 ===")
for k, v in mapping.items():
    print(f"  {k} -> {v}")

print("\n=== 还原测试 ===")
restored = Masker.unmask_text(masked, mapping)
assert restored == text, "还原失败！"
print("还原成功，与原文完全一致")
