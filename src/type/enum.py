from __future__ import annotations

import enum


class Mode(enum.IntEnum):
    PureNumbers = 1  # 纯数字
    PureLetters = 2  # 纯字母
    NumbersAndLetters = 3  # 数字+字母
    MixedNumbersAndLetters = 4  # 数字与字母混合
    CustomCharacters = 5  # 自定义字符
    MixedNoPure = 6  # 杂米（不含纯数字和字母）
    MixedWithCustom = 7  # 杂米，自定义字符
