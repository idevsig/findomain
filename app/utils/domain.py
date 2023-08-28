import itertools
from .helpers import die

'''
域名生成器
'''


class Domain:
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

    '''
    校验域名信息合法性
    '''

    def verify(self, domain):
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

    '''
    生成组合数据
    '''

    def maker(self):
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
        elif self.mode == 4:  # 数字+字母
            self.add_only_numbers()
            self.add_only_characters()
        elif self.mode == 5:  # 自定义字符
            self.set_custom_chars(self.alphabets)
        else:  # 纯数字
            self.add_only_numbers()

        # 合并域名列表
        domains.extend(self.generate())

        # 过滤
        filter_domains = self.filter_domain(domains, self.start_char)

        # 添加域名后缀
        return self.append_suffix(filter_domains)

    '''
    过滤域名数组
    '''

    def filter_domain(self, domains, filter):
        if not filter:
            return domains
        try:
            index = domains.index(str(filter))
            return domains[index:]
        except ValueError:
            return domains

    '''
    添加域名后缀
    '''

    def append_suffix(self, domains):
        domains = [
            f"{''.join(domain)}.{self.suffixes}" for domain in domains]
        return domains

    '''
    生成 a-z 的字符串
    '''

    def gen_only_alphabet(self):
        return ''.join(chr(i) for i in range(97, 123))

    '''
    添加纯数字
    '''

    def add_only_numbers(self):
        self.domain_characters += '0123456789'

    '''
    添加纯字母
    '''

    def add_only_characters(self):
        self.domain_characters += self.gen_only_alphabet()

    '''
    设置为自定义字符
    '''

    def set_custom_chars(self, chars):
        self.domain_characters = chars

    '''
    清空字符
    '''

    def clear_all_chars(self):
        self.domain_characters = ''

    '''
    组合域名数据列表
    '''

    def generate_list(self):
        return itertools.product(self.domain_characters, repeat=self.length)

    '''
    域名添加前后缀
    '''

    def generate(self):
        gen_combinations = self.generate_list()
        domains = [
            f"{self.prefix}{''.join(combination)}{self.suffix}" for combination in gen_combinations]
        return domains
