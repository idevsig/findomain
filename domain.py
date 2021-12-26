import itertools

class Domain():
    def __init__(self, length = 3, characters = ''):
        self.domain_characters = characters
        self.domain_length = length

    def set_length(self, length):
        self.domain_length = length

    '''
    生成 a-z 的字符列表
    '''
    def get_alphabets(self):
        alphabets_in_lowercase=[]
        for i in range(97,123):
            alphabets_in_lowercase.append(chr(i))     
        return alphabets_in_lowercase 

    '''
    添加纯数字
    '''
    def add_only_numbers(self):
        self.domain_characters += '0123456789'

    '''
    添加纯字母
    '''
    def add_only_characters(self):
        alphabets = self.get_alphabets()
        self.domain_characters += ''.join(alphabets)

    '''
    自定义字符
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
    def make_domains(self):
        gen_alphabets = itertools.product(self.domain_characters, repeat = self.domain_length)

        alphabets = []
        for a in gen_alphabets:
            alphabets.append(''.join(a))

        return alphabets    