"""
敏感信息检测引擎
使用正则表达式 + 自定义词表检测中文环境下的各类 PII
"""
import re
import os


# ─── 正则模式定义 ───────────────────────────────────────────────

PATTERNS = {
    'ID_CARD': re.compile(
        r'(?<!\d)'
        r'[1-9]\d{5}'                       # 地区码
        r'(?:19|20)\d{2}'                    # 年
        r'(?:0[1-9]|1[0-2])'                # 月
        r'(?:0[1-9]|[12]\d|3[01])'           # 日
        r'\d{3}[\dXx]'                       # 顺序码+校验码
        r'(?!\d)',
    ),
    'PHONE': re.compile(
        r'(?<!\d)'
        r'1[3-9]\d{9}'
        r'(?!\d)',
    ),
    'BANK_CARD': re.compile(
        r'(?<!\d)'
        r'[3-6]\d{15,18}'
        r'(?!\d)',
    ),
    'EMAIL': re.compile(
        r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
    ),
    'TEL': re.compile(
        r'(?<!\d)'
        r'(?:0\d{2,3}[-\s]?)?\d{7,8}'
        r'(?:[-\s]\d{1,4})?'
        r'(?!\d)',
    ),
    'AMOUNT': re.compile(
        r'[¥￥]\s?[\d,]+\.?\d*'
        r'|[\d,]+\.?\d*\s?(?:万元|元|万)',
    ),
    'COMPANY': re.compile(
        r'[\u4e00-\u9fff]{2,15}'
        r'(?:集团|股份|有限公司|有限责任公司|公司|合伙企业|工作室|研究院|研究所)',
    ),
    'ADDRESS': re.compile(
        r'(?:[\u4e00-\u9fff]{2,6}(?:省|自治区))?'
        r'(?:[\u4e00-\u9fff]{2,6}(?:市))'
        r'(?:[\u4e00-\u9fff]{2,6}(?:区|县|市))?'
        r'(?:[\u4e00-\u9fff]{2,20}(?:路|街|道|巷|弄|号|栋|楼|室|层|单元|大厦|广场|小区|园区|工业园))'
        r'[\u4e00-\u9fff0-9\-]*',
    ),
}

# TEL 容易误报，只在上下文有提示时匹配 → 通过后处理过滤
# BANK_CARD 与 ID_CARD 可能重叠 → 优先 ID_CARD

# 检测优先级（先匹配的优先）
PRIORITY_ORDER = [
    'ID_CARD', 'BANK_CARD', 'PHONE', 'EMAIL',
    'COMPANY', 'ADDRESS', 'AMOUNT', 'TEL',
]


class SensitiveDetector:
    """敏感信息检测器"""

    def __init__(self, custom_names_file=None):
        self.custom_words = []
        if custom_names_file and os.path.exists(custom_names_file):
            self._load_custom_words(custom_names_file)

    def _load_custom_words(self, filepath):
        """加载自定义敏感词列表"""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word and not word.startswith('#'):
                    self.custom_words.append(word)
        # 按长度降序排列，确保先匹配长词
        self.custom_words.sort(key=len, reverse=True)

    def detect(self, text):
        """
        检测文本中的敏感信息
        返回: [{'type': str, 'value': str, 'start': int, 'end': int}, ...]
        """
        results = []
        occupied = set()  # 已占用的字符位置，防止重叠

        # 1) 先匹配自定义敏感词
        for word in self.custom_words:
            for m in re.finditer(re.escape(word), text):
                span = set(range(m.start(), m.end()))
                if not span & occupied:
                    results.append({
                        'type': 'CUSTOM',
                        'value': m.group(),
                        'start': m.start(),
                        'end': m.end(),
                    })
                    occupied |= span

        # 2) 按优先级匹配正则模式
        for ptype in PRIORITY_ORDER:
            pattern = PATTERNS[ptype]
            for m in pattern.finditer(text):
                span = set(range(m.start(), m.end()))
                if not span & occupied:
                    # TEL 额外过滤：长度太短的纯数字跳过（减少误报）
                    value = m.group().strip()
                    if ptype == 'TEL':
                        digits = re.sub(r'\D', '', value)
                        if len(digits) < 7:
                            continue
                        # 如果已经被 PHONE 匹配过的号码跳过
                        if len(digits) == 11 and digits.startswith('1'):
                            continue
                    if ptype == 'AMOUNT':
                        # 过滤掉太小的金额（如 "1元"）
                        num_str = re.sub(r'[¥￥,\s万元]', '', value)
                        try:
                            if float(num_str) < 100:
                                continue
                        except ValueError:
                            continue
                    results.append({
                        'type': ptype,
                        'value': m.group(),
                        'start': m.start(),
                        'end': m.end(),
                    })
                    occupied |= span

        # 按位置排序
        results.sort(key=lambda x: x['start'])
        return results

    def detect_summary(self, text):
        """
        返回检测摘要，便于预览
        返回: {'total': int, 'by_type': {type: count}, 'items': [...]}
        """
        items = self.detect(text)
        by_type = {}
        for item in items:
            by_type[item['type']] = by_type.get(item['type'], 0) + 1
        return {
            'total': len(items),
            'by_type': by_type,
            'items': items,
        }
