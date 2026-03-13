# config.py
import os
import json
from datetime import datetime

class Config:
    """全局配置类"""
    
    # 数据文件路径
    RULES_FILE = 'monitor_rules.json'
    WATCHLIST_FILE = 'watchlist.json'
    POSITION_FILE = 'position.json'
    
    # 默认设置
    DEFAULT_INTERVAL = 60
    DEFAULT_HISTORY_DAYS = 60
    DEFAULT_UP_THRESHOLD = 5
    DEFAULT_DOWN_THRESHOLD = -5
    DEFAULT_ALERT_INTERVAL = 30
    
    # 默认自选股
    DEFAULT_WATCHLIST = [
        {'code': '002531', 'name': '天顺风能', 'market': 'A股', 'added_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {'code': '600036', 'name': '招商银行', 'market': 'A股', 'added_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
        {'code': '000858', 'name': '五粮液', 'market': 'A股', 'added_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
    ]
    
    # 默认规则
    DEFAULT_RULES = [
        {
            'type': '筹码集中度',
            'condition': '买入条件',
            'chip_percent': 90,
            'price_range': 15,
            'action': '买入信号',
            'remark': '筹码集中，适合买入',
            'enabled': True
        },
        {
            'type': '筹码集中度',
            'condition': '卖出条件',
            'chip_percent': 90,
            'price_range': 25,
            'action': '卖出信号',
            'remark': '筹码分散，考虑卖出',
            'enabled': True
        }
    ]