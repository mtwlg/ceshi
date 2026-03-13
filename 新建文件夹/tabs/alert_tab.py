# tabs/alert_tab.py
import tkinter as tk
from tkinter import ttk, scrolledtext

class AlertTab:
    """涨跌提醒标签页"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面"""
        alert_frame = ttk.LabelFrame(self.parent, text="涨跌幅提醒设置", padding=10)
        alert_frame.pack(fill='x', padx=10, pady=5)
        
        # 启用涨跌提醒
        self.enable_alert = tk.BooleanVar(value=True)
        ttk.Checkbutton(alert_frame, text="启用涨跌幅提醒", variable=self.enable_alert).grid(row=0, column=0, columnspan=2, sticky='w', pady=5)
        
        # 涨跌幅阈值设置
        ttk.Label(alert_frame, text="上涨提醒阈值(%):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.up_threshold = ttk.Entry(alert_frame, width=10)
        self.up_threshold.insert(0, str(self.app.config.DEFAULT_UP_THRESHOLD))
        self.up_threshold.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(alert_frame, text="下跌提醒阈值(%):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.down_threshold = ttk.Entry(alert_frame, width=10)
        self.down_threshold.insert(0, str(self.app.config.DEFAULT_DOWN_THRESHOLD))
        self.down_threshold.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # 提醒间隔
        ttk.Label(alert_frame, text="最小提醒间隔(分钟):").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.alert_interval = ttk.Entry(alert_frame, width=10)
        self.alert_interval.insert(0, str(self.app.config.DEFAULT_ALERT_INTERVAL))
        self.alert_interval.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        # 提醒格式预览
        preview_frame = ttk.LabelFrame(self.parent, text="提醒格式预览", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        preview_text = """go-stock [涨跌报警]
天顺风能(sz002531)
•  当前价格: 11.23  +3.31%
•  最高价: 11.24  +3.40%
•  最低价: 10.87  0.00%
•  昨收价: 10.87
•  今开价: 10.96
•  成本价: 10.50  +6.95%  +0.73 ¥
•  成本数量: 1000股
•  日期: 2026-03-11 13:00:00"""
        
        preview = scrolledtext.ScrolledText(preview_frame, height=10, width=60)
        preview.insert('1.0', preview_text)
        preview.config(state='disabled')
        preview.pack(padx=5, pady=5)