import argparse
import os
from config import Config
from app import App
from logger import setup_logging 

def arguments():
    parser = argparse.ArgumentParser(description='Find Domain Tool')
    parser.add_argument('-c', '--config', default='config.json5', help='Config file path')
    parser.add_argument('-d', '--domain', help='Domain to query')
    parser.add_argument('-u', '--url', help='Config information from url')
    return parser.parse_args()

def main():
    args = arguments()
    if args.domain:
        domain = args.domain
    else:
        domain = os.environ.get('DOMAIN')
    if args.url:
        url = args.url
    else:
        url = os.environ.get('DOMAIN_URL')

    config = Config()
    config.load_from_file(args.config)   

    if url:
        config.setting.url = url

    # datetime.now().strftime("%Y%m%d")
    setup_logging(
        config.setting.log_file, 
        config.setting.log_dir, 
        config.setting.log_level,
        )

    App(config, domain).run()

if __name__ == "__main__":
    main()
