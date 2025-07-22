from __future__ import annotations

import os
import tomllib as tomli

import json5


class Setting:
    """Settings for the application"""

    def __init__(self):
        # URL for fetching domain information, used for breakpoint queries
        self.url = ''
        # Server URL for uploading query results
        # If the URL contains '@', it will be replaced with the current date
        self.server_url = ''
        # Authentication for the server (if required)
        # eg: username:password
        self.server_auth = ''
        # Path to domain list file
        self.domain_file = 'domains.log'
        # Maximum query retries
        self.max_retries = 3
        # Log level
        self.log_level = 20
        # Log directory
        self.log_dir = 'logs'
        # Log file name
        self.log_file = 'runtime.log'
        # result file
        self.result_file = 'result.csv'

    def update_from_dict(self, data):
        """Update Setting attributes from a dictionary"""
        self.url = data.get('url', self.url)
        self.server_url = data.get('server_url', self.server_url)
        self.server_auth = data.get('server_auth', self.server_auth)
        self.domain_file = data.get('domain_file', self.domain_file)
        self.max_retries = data.get('max_retries', self.max_retries)
        self.log_level = data.get('log_level', self.log_level)
        self.log_dir = data.get('log_dir', self.log_dir)
        self.log_file = data.get('log_file', self.log_file)
        self.result_file = data.get('result_file', self.result_file)


class Domain:
    """Domain configuration"""

    def __init__(self):
        # Domain suffixes
        self.suffixes = 'com'
        # Domain length
        self.length = 1
        # Combination mode
        # 1: Pure numbers, 2: Pure letters, 3: Numbers + Letters,
        # 4: Mixed numbers and letters, 5: Custom characters
        # 6: Mixed (no pure numbers or letters), 7: Mixed with custom characters
        self.mode = 5
        # Custom character set for combinations
        self.alphabets = ''
        # Starting domain (included in query, must match length)
        self.start_char = ''
        # Combination prefix
        self.prefix = ''
        # Combination suffix
        self.suffix = ''
        # Completion status
        self.done = 0

    def update_from_dict(self, data):
        """Update Domain attributes from a dictionary"""
        self.suffixes = data.get('suffixes', self.suffixes)
        self.length = data.get('length', self.length)
        self.mode = data.get('mode', self.mode)
        self.alphabets = data.get('alphabets', self.alphabets)
        self.start_char = data.get('start_char', self.start_char)
        self.prefix = data.get('prefix', self.prefix)
        self.suffix = data.get('suffix', self.suffix)
        self.done = data.get('done', self.done)


class Whois:
    """Whois configuration"""

    def __init__(self):
        # Use proxy (not implemented)
        self.proxy = False
        # Default Whois providers
        # Options: west (Western Digital with registration time),
        # qcloud (Tencent Cloud), zzidc (ZZIDC)
        # Example: "west,qcloud,zzidc"
        self.dnp = ''

    def update_from_dict(self, data):
        """Update Whois attributes from a dictionary"""
        self.proxy = data.get('proxy', self.proxy)
        self.dnp = data.get('dnp', self.dnp)


class Dingtalk:
    """DingTalk notification configuration"""

    def __init__(self):
        # DingTalk access token
        self.token = ''
        # DingTalk secret
        self.secret = ''

    def update_from_dict(self, data):
        """Update Dingtalk attributes from a dictionary"""
        self.token = data.get('token', self.token)
        self.secret = data.get('secret', self.secret)


class Feishu:
    """Feishu notification configuration"""

    def __init__(self):
        # Feishu token
        self.token = ''
        # Feishu secret
        self.secret = ''

    def update_from_dict(self, data):
        """Update Feishu attributes from a dictionary"""
        self.token = data.get('token', self.token)
        self.secret = data.get('secret', self.secret)


class Lark:
    """Lark notification configuration"""

    def __init__(self):
        # Lark token
        self.token = ''
        # Lark secret
        self.secret = ''

    def update_from_dict(self, data):
        """Update Lark attributes from a dictionary"""
        self.token = data.get('token', self.token)
        self.secret = data.get('secret', self.secret)


class Notify:
    """Notification configuration"""

    def __init__(self):
        # Providers notifications
        self.providers = ''
        # DingTalk configuration
        self.dingtalk = Dingtalk()
        # Feishu configuration
        self.feishu = Feishu()
        # Lark configuration
        self.lark = Lark()

    def update_from_dict(self, data):
        """Update Notify attributes from a dictionary"""
        self.providers = data.get('providers', self.providers)
        self.dingtalk.update_from_dict(data.get('dingtalk', {}))
        self.feishu.update_from_dict(data.get('feishu', {}))
        self.lark.update_from_dict(data.get('lark', {}))


class Config:
    """Overall configuration for the domain query tool"""

    def __init__(self):
        self.setting = Setting()
        self.domain = Domain()
        self.whois = Whois()
        self.notify = Notify()

    def load_from_file(self, file_path):
        """Load configuration from a file and override default values"""
        if self.load_from_environment():
            return

        if file_path.endswith('.toml'):
            self.load_from_toml(file_path)
        elif (
            file_path.endswith('.jsonc')
            or file_path.endswith('.json')
            or file_path.endswith('.json5')
        ):
            self.load_from_json(file_path)
        else:
            raise ValueError('Unsupported file format')

    def load_from_environment(self):
        """Load configuration from environment variables and override default values"""
        if os.environ.get('FD_CONFIG_JSON'):
            try:
                data = json5.loads(os.environ.get('FD_CONFIG_JSON'))
                self.setting.update_from_dict(data.get('setting', {}))
                self.domain.update_from_dict(data.get('domain', {}))
                self.whois.update_from_dict(data.get('whois', {}))
                self.notify.update_from_dict(data.get('notify', {}))
                return True
            except Exception as e:
                print(f'Error loading config from environment variable: {e}')
                return False

    def load_from_toml(self, file_path):
        """Load configuration from a TOML file and override default values"""
        try:
            with open(file_path, 'rb') as f:
                data = tomli.load(f)
            self.setting.update_from_dict(data.get('setting', {}))
            self.domain.update_from_dict(data.get('domain', {}))
            self.whois.update_from_dict(data.get('whois', {}))
            self.notify.update_from_dict(data.get('notify', {}))
        except FileNotFoundError:
            print(f'Config file {file_path} not found, using default values')
        except tomli.TOMLDecodeError:
            print(
                f'Error decoding TOML file {file_path}, using default values',
            )
        except Exception as e:
            print(f'Error loading config: {e}, using default values')

    def load_from_json(self, file_path):
        """Load configuration from a JSONC file and override default values"""
        try:
            with open(file_path) as f:
                data = json5.load(f)
            self.setting.update_from_dict(data.get('setting', {}))
            self.domain.update_from_dict(data.get('domain', {}))
            self.whois.update_from_dict(data.get('whois', {}))
            self.notify.update_from_dict(data.get('notify', {}))
        except FileNotFoundError:
            print(f'Config file {file_path} not found, using default values')
        except Exception as e:
            print(f'Error loading config: {e}, using default values')

    def __str__(self) -> str:
        """Return a string representation of the Config object."""
        return (
            f'Config(\n'
            f'  setting={vars(self.setting)},\n'
            f'  domain={vars(self.domain)},\n'
            f'  whois={vars(self.whois)},\n'
            f"  notify={{'providers': '{self.notify.providers}', "
            f"'dingtalk': {vars(self.notify.dingtalk)}, "
            f"'feishu': {vars(self.notify.feishu)}}}\n)"
        )

    def __repr__(self) -> str:
        """Return a detailed string representation of the Config object."""
        return self.__str__()

    def json(self) -> str:
        """Return a JSON representation of the Config object."""
        import json

        config_dict = {
            'setting': vars(self.setting),
            'domain': vars(self.domain),
            'whois': vars(self.whois),
            'notify': {
                'providers': self.notify.providers,
                'dingtalk': vars(self.notify.dingtalk),
                'feishu': vars(self.notify.feishu),
                'lark': vars(self.notify.lark),
            },
        }
        return json.dumps(config_dict, indent=2)


# Example usage:
# config = Config()
# config.load_from_toml("config.toml")
