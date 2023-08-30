import itertools
from .helpers import die


class Domain:
    '''
    域名生成器
    '''
    # {'suffixes': 'cn', 'length': 3, 'mode': 2, 'characters': '', 'start_char': '', 'prefix': '', 'suffix': ''} 1

    def __init__(self, domain) -> None:
        self.verify(domain)

        self.suffixes = domain['suffixes']
        self.length = domain['length']
        self.mode = domain['mode']
        self.alphabets = domain['alphabets']
        self.start_char = domain['start_char']
        self.prefix = domain['prefix']
        self.suffix = domain['suffix']

        # 默认组合字符
        self.domain_characters = ''

    def verify(self, domain):
        '''
        校验域名信息合法性
        '''
        # 校验
        if len(domain['suffixes']) < 2:
            die(f"Invalid domain suffixes: {domain['suffixes']}")

        if domain['length'] < 0:
            die(f"Invalid domain length: {domain['length']}")

        if domain['start_char']:
            domain_length = domain['length'] + \
                len(domain['prefix']) + len(domain['suffix'])
            if len(domain['start_char']) != domain_length:
                die(
                    f"Invalid start char length: {domain_length}, start_char: {domain['start_char']}")

    def maker(self):
        '''
        生成组合数据
        '''
        domains = []  # 域名列表
        if self.mode == 1:  # 纯数字
            self.add_only_numbers()
        elif self.mode == 2:  # 纯字母
            self.add_only_characters()
        elif self.mode == 3:  # 纯数字 + 纯字母
            self.add_only_numbers()
            # 生成纯数字
            domains = self.generate()
            # 清空所有字符
            self.clear_all_chars()
            self.add_only_characters()
        elif self.mode == 4 or self.mode == 6:  # 数字+字母
            self.add_only_numbers()
            self.add_only_characters()
        elif self.mode == 5 or self.mode == 7:  # 自定义字符
            self.set_custom_chars(self.alphabets)
        else:  # 纯数字
            self.add_only_numbers()

        # 合并域名列表
        domains.extend(self.generate())

        # 过滤
        filter_domains = self.filter_domain(domains, self.start_char)

        # 添加域名后缀
        return self.append_suffix(filter_domains)

    def filter_domain(self, domains, filter):
        '''
        过滤域名数组
        '''
        if not filter:
            return domains
        try:
            index = domains.index(str(filter))
            return domains[index:]
        except ValueError:
            return domains

    def append_suffix(self, domains):
        '''
        添加域名后缀
        '''
        domains = [
            f"{''.join(domain)}.{self.suffixes}" for domain in domains]
        return domains

    def gen_only_alphabet(self):
        '''
        生成 a-z 的字符串
        '''
        return ''.join(chr(i) for i in range(97, 123))

    def gen_only_number(self, min=0, max=9):
        '''
        生成 0-9 的数字
        '''
        return ''.join(str(i) for i in range(min, max + 1))

    def add_only_numbers(self):
        '''
        添加纯数字
        '''
        self.domain_characters += '0123456789'

    def add_only_characters(self):
        '''
        添加纯字母
        '''
        self.domain_characters += self.gen_only_alphabet()

    def set_custom_chars(self, chars):
        '''
        设置为自定义字符
        '''
        self.domain_characters = chars

    def clear_all_chars(self):
        '''
        清空字符
        '''
        self.domain_characters = ''

    def generate_list(self):
        '''
        组合域名数据列表
        '''
        return itertools.product(self.domain_characters, repeat=self.length)

    def generate_number_char(self):
        '''
        生成同时包含字母和数字的组合（杂米）
        '''
        combinations = []

        list = self.generate_list()
        for chars in list:
            combination = ''.join(chars)

            if any(char.isdigit() for char in combination) and any(char.isalpha() for char in combination) and '-' not in combination:
                combinations.append(combination)

        return combinations

    def generate(self):
        '''
        域名添加前后缀
        '''
        if self.mode == 6 or self.mode == 7:
            gen_combinations = self.generate_number_char()
        else:
            gen_combinations = self.generate_list()

        domains = [
            f"{self.prefix}{''.join(combination)}{self.suffix}" for combination in gen_combinations]
        return domains
