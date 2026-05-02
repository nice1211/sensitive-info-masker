"""
纯文本文件处理器 (txt / md / csv)
"""
from core.detector import SensitiveDetector
from core.masker import Masker


def mask_text_file(filepath, detector: SensitiveDetector, items=None):
    """
    对纯文本文件执行脱敏
    items: 可选，前端传来的已筛选检测项列表。为 None 时自动检测。
    返回: (masked_content, mapping)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    masker = Masker()
    detections = items if items is not None else detector.detect(content)
    masked, mapping = masker.mask_text(content, detections)
    return masked, mapping


def unmask_text_file(filepath, mapping):
    """
    对纯文本文件执行还原
    返回: restored_content
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    return Masker.unmask_text(content, mapping)


def save_text(content, output_path):
    """保存文本内容到文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
