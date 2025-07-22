from __future__ import annotations

import argparse
import os

from app import App
from config import Config
from logger import setup_logging
from utils.util import remove_suffix


def arguments():
    parser = argparse.ArgumentParser(description="Find Domain Tool")
    parser.add_argument(
        "-c",
        "--config",
        default="config.json5",
        help="Config file path",
    )
    parser.add_argument("-d", "--domain", help="Domain to query")
    parser.add_argument("-u", "--url", help="Config information from url")
    parser.add_argument(
        "-s",
        "--server_url",
        help="Server url for uploading query results",
    )
    parser.add_argument(
        "-a",
        "--server_auth",
        help="Server auth for uploading query results",
    )
    parser.add_argument(
        "-p",
        "--dnp",
        help="Whois providers, eg: west, qcloud, zzidc",
    )
    return parser.parse_args()


def load_config(args):
    config = Config()
    config.load_from_file(args.config)
    if args.url:
        config.setting.url = args.url
    if args.server_url:
        config.setting.server_url = args.server_url
    if args.server_auth:
        config.setting.server_auth = args.server_auth
    if args.dnp:
        config.whois.dnp = args.dnp.replace(" ", "")

    # 从环境变量中加载配置
    if os.environ.get("FD_DOMAIN_URL"):
        config.setting.url = os.environ.get("FD_DOMAIN_URL")
    if os.environ.get("FD_SERVER_URL"):
        config.setting.server_url = os.environ.get("FD_SERVER_URL")
    if os.environ.get("FD_SERVER_AUTH"):
        config.setting.server_auth = os.environ.get("FD_SERVER_AUTH")
    if os.environ.get("FD_DNP"):
        config.whois.dnp = os.environ.get("FD_DNP").replace(" ", "")
    if os.environ.get("FD_LOG_LEVEL"):
        config.setting.log_level = os.environ.get("FD_LOG_LEVEL")
    if os.environ.get("FD_START_CHAR"):
        config.domain.start_char = remove_suffix(os.environ.get("FD_START_CHAR"))
    return config


def main():
    args = arguments()
    config = load_config(args)

    # datetime.now().strftime("%Y%m%d")
    setup_logging(
        config.setting.log_file,
        config.setting.log_dir,
        config.setting.log_level,
    )

    domain = args.domain or os.environ.get("FD_DOMAIN")
    # 简单判断域名是否合法
    if domain and "." not in domain:
        raise ValueError(f"Invalid domain: {domain}")

    App(config).run(domain)


if __name__ == "__main__":
    main()
