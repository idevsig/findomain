import sys

'''
退出程序
'''


def die(msg):
    print(msg)
    sys.exit(1)


'''
检测是否为 JSON 数据
'''


def json_check(msg):
    try:
        res = msg.json()
        # print(res)
        return res
    except Exception as e:
        print(f'Error: json check {e}')
        return str(e)
