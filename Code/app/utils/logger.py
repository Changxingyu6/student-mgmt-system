"""
日志工具模块
提供结构化日志配置和日志记录功能
"""
import logging
import os
from datetime import datetime
from pathlib import Path

# 获取当前文件所在目录
UTILS_DIR = Path(__file__).resolve().parent
APP_DIR = UTILS_DIR.parent
LOG_DIR = APP_DIR / "logs"

# 确保日志目录存在
LOG_DIR.mkdir(exist_ok=True)


class LoggerConfig:
    """日志配置类"""
    
    @staticmethod
    def get_today_log_filename(prefix: str) -> str:
        """获取当日日志文件名，格式：YYYYMMDD_prefix.log"""
        today = datetime.now().strftime("%Y%m%d")
        return f"{today}_{prefix}.log"
    
    @staticmethod
    def configure_logging():
        """配置日志系统"""
        # 创建日志目录
        LOG_DIR.mkdir(exist_ok=True)
        
        # 获取当日日志文件路径
        app_log_path = LOG_DIR / LoggerConfig.get_today_log_filename("app")
        error_log_path = LOG_DIR / LoggerConfig.get_today_log_filename("error")
        
        # 创建主日志记录器
        logger = logging.getLogger("app")
        logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if logger.handlers:
            logger.handlers.clear()
        
        # 1. 控制台处理器（彩色输出）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        
        # 2. 应用日志文件处理器（所有级别）
        app_file_handler = logging.FileHandler(str(app_log_path), encoding="utf-8")
        app_file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        app_file_handler.setFormatter(file_formatter)
        
        # 3. 错误日志文件处理器（仅ERROR级别及以上）
        error_file_handler = logging.FileHandler(str(error_log_path), encoding="utf-8")
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(file_formatter)
        
        # 添加处理器
        logger.addHandler(console_handler)
        logger.addHandler(app_file_handler)
        logger.addHandler(error_file_handler)
        
        return logger


# 创建全局日志实例
logger = LoggerConfig.configure_logging()


def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器"""
    if name:
        return logging.getLogger(f"app.{name}")
    return logger
