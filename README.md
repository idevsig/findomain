# findomain

查询域名是否已被注册

## 先决条件
- [uv](https://github.com/astral-sh/uv)
  ```bash
  # On macOS and Linux.
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## 安装
- 源码安装
  ```bash
  uv tool install .
  ```

- 通过 Git 仓库安装
  ```bash
  uv tool install git+https://github.com/idev-sig/findomain.git@main
  ```

## 运行

```bash
# 安装依赖
uv sync

# 修改配置信息（默认 config.json5）
# 可通过 -c / --config 指定配置的文件
uv run findomain -c ./config.json5

# 运行
uv run findomain

# 或者 从网络读取配置信息
DOMAIN_URL=http://0.0.0.0:8000/config.json uv run findomain

# 指定域名
DOMAIN=idev.top uv run findomain
# 或
uv run findomain -d idev.top
```

查询完成之后，将脚本 `scripts/merge.sh` 复制到结果目录，执行合并所有结果文件，并生成一个 `.csv` 文件。

## 配置

- 可配置环境变量 `FD_CONFIG_JSON` 作为全局的值（内容格式参考 [`config.json5`](config.json5)）
- 设置环境变量 `FD_DOMAIN_URL` 后，可以从该网址获取域名部分的配置信息，并覆盖本地的配置信息。
- 设置环境变量 `FD_LOG_LEVEL` 后，可指定日志级别，如 `FD_LOG_LEVEL=debug`

<details>
<summary>查看配置信息</summary>

- [config.toml](config.toml)
- [config.json5](config.json5)

```json5
{
  // 设置
  "setting": {
    // 域名信息获取网址，断点查询使用，即 domain 项
    "url": "",
    // 查询结果上传到指定服务器
    // 比如 https://github.com/dutchcoders/transfer.sh 搭建的站点
    // 参数中带有 @，则会被替换成日期
    "server_url": "",
    // 上传到指定服务器的鉴权信息
    // eg: username:password
    "server_auth": "",
    // 本次查询域名列表保存文件名
    "domain_file": "domains.log",
    // 最大查询次数
    "max_retries": 3,
    // 日志级别
    // CRITICAL = 50
    // FATAL = CRITICAL
    // ERROR = 40
    // WARNING = 30
    // WARN = WARNING
    // INFO = 20
    // DEBUG = 10
    // NOTSET = 0
    "log_level": "DEBUG",
    // 日志目录
    "log_dir": "logs",
    // 日志文件名
    "log_file": "runtime.log",
    // 结果文件名
    "result_file": "result.csv"
  },
  // 域名
  "domain": {
    // 后缀
    "suffixes": "com",
    // 长度
    "length": 1,
    // 组合模式
    // 1.纯数字，2.纯字母，3.纯数字+纯字母，4.数字与字母混合，5.自定义字符
    // 6.杂米（不含纯数字和字母），7.杂米，自定义字符
    "mode": 1,
    // 自定义组合字母表
    "alphabets": "",
    // 起始域名（以此域名开始记录(含)，字符长度必须与 length 一致）
    "start_char": "",
    // 结束域名（以此域名结束记录(含)，字符长度必须与 length 一致）
    "end_char": "",
    // 组合前缀
    "prefix": "",
    // 组合后缀
    "suffix": "",
    // 断点续查网址 {"start_char": "", "updated_time": ""}
    "resume_url": ""
  },
  // Whois
  "whois": {
    // 使用代理（功能未实现）
    "proxy": false,
    // 默认 Whois 提供商
    // west.西部数码(带注册时间),qcloud.腾讯云,zzidc.景安
    // 比如: west,qcloud,zzidc
    "dnp": ""
  },
  // 通知
  "notify": {
    // 提供者，逗号分隔。如 feishu,dingtalk
    "providers": "",
    // 钉钉
    "dingtalk": {
      // 钉钉 access_token
      "token": "",
      // 钉钉 Secret
      "secret": ""
    },
    // 飞书
    "feishu": {
      // 飞书 Token
      "token": "",
      // 飞书 Secret
      "secret": ""
    },
    // Lark
    "lark": {
      // Lark Token
      "token": "",
      // Lark Secret
      "secret": ""
    }
  }
}
```

</details>

**设置 `setting.url`** 后，该网址返回的数据信息

```json5
{
  // 后缀
  "suffixes": "com",
  // 长度
  "length": 1,
  // 组合模式
  // 1.纯数字，2.纯字母，3.纯数字+纯字母，4.数字与字母混合，5.自定义字符
  // 6.杂米（不含纯数字和字母），7.杂米，自定义字符
  "mode": 1,
  // 自定义组合字母表
  "alphabets": "",
  // 起始域名（以此域名开始记录(含)，字符长度必须与 length 一致）
  "start_char": "",
  // 结束域名（以此域名结束记录(含)，字符长度必须与 length 一致）
  "end_char": "",
  // 组合前缀
  "prefix": "",
  // 组合后缀
  "suffix": "",
  // 断点续查网址 {"start_char": "", "updated_time": ""}
  "resume_url": ""
}
```

## 命令行帮助信息
```bash
findomain --help
usage: findomain [-h] [-c CONFIG] [-d DOMAIN] [-u URL] [-t TRANSFER] [-p DNP]

Find Domain Tool

options:
  -h, --help            show this help message and exit
  -c, --config CONFIG   Config file path
  -d, --domain DOMAIN   Domain to query
  -u, --url URL         Config information from url
  -s, --server_url SERVER_URL
                        Server url for uploading query results
  -a, --server_auth SERVER_AUTH
                        Server auth for uploading query results
  -p, --dnp DNP         Whois providers, eg: west, qcloud, zzidc
```
> -c 指定配置文件路径，如 config.toml 或 config.json5   
> -d 查询单个域名，如 idev.top。可通过环境变量设置 `FD_DOMAIN`   
> -u 从网络获取域名(`domain`)部分信息，如 http://0.0.0.0:8000/domain_info.json , 可通过环境变量 `FD_DOMAIN_URL` 设置   
> -s 上传查询结果的服务器地址，可通过环境变量 `FD_SERVER_URL` 设置。含 `@` 则会替换成日期 `yyyyMMdd`   
> -a 上传查询结果的服务器鉴权信息，可通过环境变量 `FD_SERVER_AUTH` 设置   
> -p 指定 Whois 提供商，可通过环境变量 `FD_DNP` 设置   

## 仓库镜像

- https://git.jetsung.com/idev/findomain
- https://framagit.org/idev/findomain
- https://gitcode.com/idev/findomain
- https://github.com/idev-sig/findomain
