"""
脱敏与还原核心逻辑
"""


# 类型标签的中英文映射（用于生成可读的占位符）
TYPE_LABELS = {
    'ID_CARD': 'ID',
    'PHONE': 'PHONE',
    'BANK_CARD': 'BANK',
    'EMAIL': 'EMAIL',
    'TEL': 'TEL',
    'AMOUNT': 'AMOUNT',
    'COMPANY': 'COMPANY',
    'ADDRESS': 'ADDR',
    'CUSTOM': 'CUSTOM',
}


class Masker:
    """脱敏器：将敏感信息替换为占位符，并维护映射关系"""

    def __init__(self):
        # 占位符 -> 原始值
        self.mapping = {}
        # 原始值 -> 占位符（确保同一值用同一占位符）
        self._reverse = {}
        # 各类型计数器
        self._counters = {}

    def _get_placeholder(self, ptype, value):
        """获取或创建占位符"""
        if value in self._reverse:
            return self._reverse[value]

        label = TYPE_LABELS.get(ptype, ptype)
        count = self._counters.get(label, 0) + 1
        self._counters[label] = count
        placeholder = f'[{label}_{count:03d}]'

        self.mapping[placeholder] = value
        self._reverse[value] = placeholder
        return placeholder

    def mask_text(self, text, detections):
        """
        对文本执行脱敏
        detections: detector.detect() 的返回结果
        返回: (masked_text, mapping_dict)
        """
        if not detections:
            return text, {}

        # 从后往前替换，避免位置偏移
        result = text
        for item in sorted(detections, key=lambda x: x['start'], reverse=True):
            placeholder = self._get_placeholder(item['type'], item['value'])
            result = result[:item['start']] + placeholder + result[item['end']:]

        return result, dict(self.mapping)

    @staticmethod
    def unmask_text(text, mapping):
        """
        还原文本
        mapping: {placeholder: original_value}
        """
        result = text
        # 按占位符长度降序排列，防止短占位符误替换长占位符的一部分
        for placeholder in sorted(mapping.keys(), key=len, reverse=True):
            result = result.replace(placeholder, mapping[placeholder])
        return result

    def get_mapping(self):
        """返回当前映射表（副本）"""
        return dict(self.mapping)

    def reset(self):
        """重置状态"""
        self.mapping.clear()
        self._reverse.clear()
        self._counters.clear()
