# app_mixin_ui.py
import tkinter as tk
from tkinter import ttk

from tabs.watchlist_tab import WatchlistTab
from tabs.monitor_tab import MonitorTab
from tabs.rule_tab import RuleTab
from tabs.alert_tab import AlertTab
from tabs.chip_tab import ChipTab
from tabs.source_tab import SourceTab
from tabs.dingding_tab import DingDingTab
from tabs.position_tab import PositionTab
from tabs.log_tab import LogTab

class AppMixinUI:
    def create_widgets(self):
        """创建主界面"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.tabs = {}
        
        # 自选股监控
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='自选股监控')
        self.tabs['watchlist'] = WatchlistTab(frame, self)
        
        # 实时监控
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='实时监控')
        self.tabs['monitor'] = MonitorTab(frame, self)
        
        # 规则设置
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='买卖规则')
        self.tabs['rule'] = RuleTab(frame, self)
        
        # 涨跌提醒
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='涨跌提醒')
        self.tabs['alert'] = AlertTab(frame, self)
        
        # 筹码分析
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='筹码分析')
        self.tabs['chip'] = ChipTab(frame, self)
        
        # 数据源设置
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='数据源设置')
        self.tabs['source'] = SourceTab(frame, self)
        
        # 钉钉设置
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='钉钉设置')
        self.tabs['dingding'] = DingDingTab(frame, self)
        
        # 持仓设置
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='持仓设置')
        self.tabs['position'] = PositionTab(frame, self)
        
        # 日志
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='监控日志')
        self.tabs['log'] = LogTab(frame, self)