"""
Module: log_util
Author: likanghui
Date: 2025-08-23

Description:
    JSON 日志 + 按 logType 分文件写入 + 按天轮转
"""

import json
import logging
import os
import threading
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from typing import Optional, Dict

# 线程局部存储
LOCAL_DATA = threading.local()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            '@timestamp': self.formatTime(record, '%Y-%m-%dT%H:%M:%S%z'),
            'level': record.levelname,
            'message': record.getMessage(),
            'type': record.name,  # logger 名称
            'logType': LOCAL_DATA.logType,
        }

        # 公共字段
        if hasattr(LOCAL_DATA, "options"):
            for k, v in LOCAL_DATA.options.get('options', {}).items():
                log_record[k] = v

        # 从 extra 里拿 logType
        extra = record.__dict__

        if "label" in extra:
            log_record["logName"] = extra["label"]
        return json.dumps(log_record, ensure_ascii=False)


# ===================================================
# 多文件分流 Handler：按 logType -> 独立文件 + 轮转
# ===================================================
class MultiTaskTimedRotatingHandler(logging.Handler):
    def __init__(
        self,
        base_dir: str,
        prefix: str = "",
        when: str = "D",
        backupCount: int = 7,
        encoding: str = "utf-8",
        level: int = logging.INFO,
        formatter: Optional[logging.Formatter] = None,
    ):
        super().__init__(level=level)
        self.base_dir = base_dir
        self.prefix = prefix
        self.when = when
        self.backupCount = backupCount
        self.encoding = encoding
        self.default_log_type = None
        self._handlers: Dict[str, TimedRotatingFileHandler] = {}
        os.makedirs(self.base_dir, exist_ok=True)
        if formatter:
            self.setFormatter(formatter)

    def _pick_key(self, record: logging.LogRecord) -> str:
        log_type = getattr(record, "logType", None)
        if not log_type and hasattr(LOCAL_DATA, "logType"):
            log_type = LOCAL_DATA.logType
        if not log_type and record.name:
            log_type = record.name.split('.')[-1]
        return (log_type or self.default_log_type).lower()

    def _ensure_handler(self, key: str) -> TimedRotatingFileHandler:
        h = self._handlers.get(key)
        if h is None:
            filename = os.path.join(self.base_dir, f"{self.prefix}{key}.log")
            h = TimedRotatingFileHandler(filename, when=self.when,
                                         backupCount=self.backupCount, encoding=self.encoding)
            h.setLevel(self.level)
            if self.formatter:
                h.setFormatter(self.formatter)
            self._handlers[key] = h
        return h

    def emit(self, record: logging.LogRecord) -> None:
        self._ensure_handler(self._pick_key(record)).emit(record)


# =========================================
# 对外：安装日志（根 logger 统一管理 handler）
# =========================================
def install_logging(
    base_dir: str,
    prefix: str,
    when: str,
    backup_count: int = 14,
    console: bool = False,
    level: int = logging.INFO,
) -> None:
    """
    在应用启动时调用一次，初始化日志系统。
    """
    json_formatter = JsonFormatter()

    root = logging.getLogger()
    root.setLevel(level)

    for h in list(root.handlers):
        root.removeHandler(h)

    multi = MultiTaskTimedRotatingHandler(
        base_dir=base_dir,
        prefix=prefix,
        when=when,
        backupCount=backup_count,
        level=level,
        formatter=json_formatter,
    )
    root.addHandler(multi)

    if console:
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(json_formatter)
        root.addHandler(sh)


# ===========================
# 日志调用包装
# ===========================
class LogUtil:
    def __init__(self, name: str):
        self._log = self._create_log(name=name)

    def info(self, message: str, extra=None):
        self._log.info(msg=message, extra=extra or {})

    def error(self, message: str, extra=None):
        self._log.error(msg=message, extra=extra or {})

    def warning(self, message: str, extra=None):
        self._log.warning(msg=message, extra=extra or {})

    def _create_log(self, name: str, level: int = logging.INFO):
        logger = logging.getLogger(name=name)
        logger.setLevel(level)
        logger.propagate = True
        return logger

    def set_options(self, options: dict):
        LOCAL_DATA.options = options or {}

    def set_log_type(self, log_type: str):
        LOCAL_DATA.logType = log_type
