import sys


def die(msg):
    '''
    退出程序
    '''
    print(msg)
    sys.exit(1)


def json_check(msg):
    '''
    检测是否为 JSON 数据
    :param msg: Response 内容
    '''
    try:
        res = msg.json()
        # print(res)
        return res
    except Exception as e:
        print(f'Error: json check {e}')
        return str(e)


def write_file(file_path, str):
    '''
    数据写入文件
    :param file_path: 文件路径
    :param str: 内容
    '''
    with open(file_path, "w") as file:
        file.write(str)
