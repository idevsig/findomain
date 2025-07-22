from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QueryResult:
    """域名查询结果数据结构"""

    domain: str  # 域名
    available: bool  # 是否可注册
    registration_date: str | None = None  # 注册时间
    expiration_date: str | None = None  # 过期时间
    error_code: int = 0  # 查询操作
    provider: str | None = None  # 提供商

    @property
    def is_success(self) -> bool:
        """查询是否成功"""
        return self.error_code == 0

    def to_tuple(self):
        """转换为元组格式（兼容现有代码）"""
        return (
            self.domain,
            self.available,
            self.registration_date,
            self.expiration_date,
            self.error_code,
        )

    def to_json(self):
        """转换为 JSON 格式"""
        return {
            "domain": self.domain,
            "available": self.available,
            "registration_date": self.registration_date,
            "expiration_date": self.expiration_date,
            "error_code": self.error_code,
            "provider": self.provider,
        }

    def to_array(self):
        """转换为数组格式"""
        return [
            self.domain,
            self.available,
            self.registration_date,
            self.expiration_date,
            self.error_code,
            self.provider,
        ]

    def to_string(self):
        """转换为字符串格式"""
        return f"{self.domain}, {self.available}, {self.registration_date}, {self.expiration_date}, {self.error_code}, {self.provider}"
