# findomain

查询域名是否已被注册

## TODOS

- 代理 IP 功能
- 多线程
- 断点查询

## 运行

```bash
# 安装依赖
pip install -r requirements.txt

# 更新配置文件 config.yml

# 运行
python run.py

# 或者 从网络读取配置信息
YAML_URL=http://0.0.0.0:8000/config.yml python run.py
```

## 配置信息

> 设置环境变量 `YAML_URL` 后，可以从该网址获取配置文件，并保存覆盖到 `config.yml`。

[config.yml](config.yml)

```yaml
# 设置
setting:
  # 域名信息获取网址，断点查询使用，即 domain 项
  url: ""
  # 查询结果保存网址
  # 具体 https://github.com/dutchcoders/transfer.sh 搭建的站点
  transfer: ""
  # 域名列表文件地址
  data_path: domain.txt
  # 日志文件
  log_path: domain.log

# 域名
domain:
  # 后缀
  suffixes: cn
  # 长度
  length: 3
  # 组合模式
  # 1.纯数字，2.纯字母，3.纯数字+纯字母，4.数字与字母混合，5.自定义字符
  mode: 3
  # 自定义组合字母表
  alphabets: ""
  # 起始域名（以此域名开始记录(含)，字符长度必须与 length 一致）
  start_char: ""
  # 组合前缀
  prefix: ""
  # 组合后缀
  suffix: ""

# Whois
whois:
  # 使用代理
  proxy: false
  # 默认 Whois 提供商
  # west.西部数码(带注册时间),qcloud.腾讯云,zzidc.景安
  # 比如: west,qcloud,zzidc
  isp:

# 通知
notify:
  # 启用
  enable: ""

  # 钉钉
  dingtalk:
    # 钉钉 access_token
    token: ""
    # 钉钉 Secret
    secret: ""
  # 飞书
  feishu:
    # 飞书 Token
    token: ""
    # 飞书 Secret
    secret: ""
```
