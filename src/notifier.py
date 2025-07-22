from __future__ import annotations

import logging

from notify.dingtalk import Dingtalk
from notify.feishu import Feishu
from notify.lark import Lark

# 通知类映射
NOTIFICATION_CLASSES = {
    "dingtalk": Dingtalk,
    "feishu": Feishu,
    "lark": Lark,
}


def send_notify(config, msg_arr: list[str], file_path: str):
    if not config.providers:
        return None

    providers = str(config.providers).replace(" ", "").split(",")
    for provider in providers:
        notify_class = NOTIFICATION_CLASSES.get(provider)
        if not notify_class:
            logging.warning(f"Unsupported provider: {provider}")
            continue

        try:
            provider_config = getattr(config, provider, None)
            if not provider_config:
                logging.warning(f"Missing configuration for {provider}")
                continue

            token = getattr(provider_config, "token", None)
            secret = getattr(provider_config, "secret", None)
            if not token:
                logging.warning(f"Missing token for {provider}")
                continue

            # 如果不是飞书或 lark 平台，则必须含 secret
            if not (provider == "feishu" or provider == "lark") and not secret:
                logging.warning(f"Missing secret for {provider}")
                continue

            notify = notify_class(token, secret)

            if msg_arr:
                upload_url, *rest = msg_arr
                message = f"Upload URL: {upload_url}"
                if rest:
                    message += f"\nDelete URL: {rest[0]}"
                notify.send(message)
            elif file_path:
                with open(file_path, "rb") as f:
                    notify.send(f.read().decode("utf-8"))

        except Exception as e:
            logging.error(
                f"Failed to send notification via {provider}: {str(e)}",
            )
