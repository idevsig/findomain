from __future__ import annotations

import itertools

from type.enum import Mode
from utils.util import remove_special_chars, remove_suffix


class Domain:
    """
    域名生成器
    {'suffixes': 'cn', 'length': 3, 'mode': 2, 'characters': '', 'start_char': '', 'end_char': '', 'prefix': '', 'suffix': '', 'resume_url': ''}
    """

    DOMAIN_SUFFIX_MIN_LENGTH = 2
    DOMAIN_LENGTH_MIN = 1

    def __init__(self, domain) -> None:
        # 移除后缀且保留英文大小写和数字
        start_char = remove_special_chars(remove_suffix(domain.start_char))
        end_char = remove_special_chars(remove_suffix(domain.end_char))

        # 默认组合字符
        self.domain_characters = ''

        self.suffixes = domain.suffixes
        self.length = domain.length
        self.mode = domain.mode
        self.alphabets = domain.alphabets

        self.start_char = start_char
        self.end_char = end_char
        self.prefix = domain.prefix
        self.suffix = domain.suffix

    def verify(self):
        """
        校验域名信息合法性
        """
        # 校验
        if len(self.suffixes) < self.DOMAIN_SUFFIX_MIN_LENGTH:
            raise ValueError(f'Invalid domain suffixes: {self.suffixes}')

        if self.length < self.DOMAIN_LENGTH_MIN:
            raise ValueError(f'Invalid domain length: {self.length}')

        if self.start_char:
            domain_length = self.length + len(self.prefix) + len(self.suffix)

            if len(self.start_char) != domain_length:
                raise ValueError(
                    f'Invalid start char length: {domain_length}, start_char: {self.start_char}',
                )

    def maker(self):
        """
        生成组合数据
        """
        self.verify()

        domains = []  # 域名列表
        if self.mode == Mode.PureNumbers.value:  # 纯数字
            self.add_only_numbers()
        elif self.mode == Mode.PureLetters.value:  # 纯字母
            self.add_only_characters()
        elif self.mode == Mode.NumbersAndLetters.value:  # 纯数字 + 纯字母
            self.add_only_numbers()
            # 生成纯数字
            domains = self.generate()
            # 清空所有字符
            self.clear_all_chars()
            self.add_only_characters()
        elif (
            self.mode == Mode.MixedNumbersAndLetters.value
            or self.mode == Mode.MixedNoPure.value
        ):  # 数字+字母
            self.add_only_numbers()
            self.add_only_characters()
        elif (
            self.mode == Mode.CustomCharacters.value
            or self.mode == Mode.MixedWithCustom.value
        ):  # 自定义字符
            self.set_custom_chars(self.alphabets)
        else:  # 纯数字
            self.add_only_numbers()

        # 合并域名列表
        domains.extend(self.generate())

        # 过滤
        filter_domains = self.filter_domain(
            domains, self.start_char, self.end_char
        )

        # 添加域名后缀
        return self.append_suffix(filter_domains)

    def filter_domain(self, domains, start=None, end=None):
        """
        过滤域名列表，返回从 start 到 end（包含）的子列表。
        如果 start 或 end 为空（None 或空字符串）或不在 domains 中，则忽略对应条件。

        参数:
            domains (list): 域名字符串列表。
            start (str, optional): 开始过滤的域名。如果为空或不在列表中，从开头开始。
            end (str, optional): 结束过滤的域名（包含）。如果为空或不在列表中，到末尾结束。

        返回:
            list: 从 start 到 end（包含）的域名子列表。

        异常:
            TypeError: 如果 domains 不是列表，或 domains 包含非字符串元素。
        """
        # 验证输入
        if not isinstance(domains, list):
            raise TypeError('domains 必须是一个列表')

        if not domains:
            return []

        # 验证 domains 中所有元素都是字符串
        if not all(isinstance(domain, str) for domain in domains):
            raise TypeError('所有域名必须是字符串')

        # 默认从列表开头开始
        start_index = 0
        # 默认到列表末尾
        end_index = len(domains) - 1

        # 处理 start 参数
        if start and isinstance(start, str) and start in domains:
            start_index = domains.index(start)

        # 处理 end 参数
        if end and isinstance(end, str) and end in domains:
            end_index = domains.index(end)

        # 验证 end_index 不小于 start_index
        if end_index < start_index:
            return []

        return domains[start_index : end_index + 1]

    def append_suffix(self, domains):
        """
        添加域名后缀
        """
        domains = [f'{"".join(domain)}.{self.suffixes}' for domain in domains]
        return domains

    def gen_only_alphabet(self):
        """
        生成 a-z 的字符串
        """
        return ''.join(chr(i) for i in range(97, 123))

    def gen_only_number(self, min=0, max=9):
        """
        生成 0-9 的数字
        """
        return ''.join(str(i) for i in range(min, max + 1))

    def add_only_numbers(self):
        """
        添加纯数字
        """
        self.domain_characters += '0123456789'

    def add_only_characters(self):
        """
        添加纯字母
        """
        self.domain_characters += self.gen_only_alphabet()

    def set_custom_chars(self, chars):
        """
        设置为自定义字符
        """
        self.domain_characters = chars
        if not self.domain_characters:
            raise ValueError('Custom characters cannot be empty.')

    def clear_all_chars(self):
        """
        清空字符
        """
        self.domain_characters = ''

    def generate_list(self):
        """
        组合域名数据列表
        """
        return itertools.product(self.domain_characters, repeat=self.length)

    def generate_number_char(self):
        """
        生成同时包含字母和数字的组合（杂米）
        """
        combinations = []

        list = self.generate_list()
        for chars in list:
            combination = ''.join(chars)

            if (
                any(char.isdigit() for char in combination)
                and any(char.isalpha() for char in combination)
                and '-' not in combination
            ):
                combinations.append(combination)

        return combinations

    def generate(self):
        """
        域名添加前后缀
        """
        if (
            self.mode == Mode.MixedNoPure.value
            or self.mode == Mode.MixedWithCustom.value
        ):
            gen_combinations = self.generate_number_char()
        else:
            gen_combinations = self.generate_list()

        return [
            f'{self.prefix}{"".join(combination)}{self.suffix}'
            for combination in gen_combinations
        ]
