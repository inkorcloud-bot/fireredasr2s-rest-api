"""
配置加载器模块
"""

import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any
from .logger import get_logger

logger = get_logger(__name__)
_global_config: Dict[str, Any] = {}

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """加载配置文件和环境变量，返回合并后的配置"""
    global _global_config
    
    # 加载 .env 文件
    load_dotenv()
    
    # 加载 YAML 配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            _global_config = yaml.safe_load(f) or {}
            logger.info(f"配置文件加载成功: {config_path}")
    except FileNotFoundError:
        logger.warning(f"配置文件不存在: {config_path}, 使用空配置")
        _global_config = {}
    
    # 合并环境变量
    _global_config = _merge_nested_config(_global_config)
    
    return _global_config


def get_config() -> Dict[str, Any]:
    """获取全局配置"""
    return _global_config


def _merge_nested_config(config: Dict[str, Any], env_prefix: str = "FIRERED_") -> Dict[str, Any]:
    """合并环境变量到配置（下划线分隔嵌套键）"""
    result = config.copy()
    
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            # 移除前缀，转换为小写
            config_key = key[len(env_prefix):].lower()
            # 分割嵌套键
            keys = config_key.split('_')
            
            # 类型转换
            try:
                if value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                    value = float(value)
                elif value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
            except ValueError:
                pass
            
            # 嵌套赋值
            current = result
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
    
    return result
