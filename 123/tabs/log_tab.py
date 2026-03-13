# tabs/log_tab.py
import tkinter as tk
from tkinter import ttk, scrolledtext

class LogTab:
    """日志标签页"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面"""
        self.log_text = scrolledtext.ScrolledText(self.parent, height=30)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Button(self.parent, text="清除日志", command=self.clear_log).pack(pady=5)
        
    def add_log(self, message):
        """添加日志"""
        self.log_text.insert('end', message)
        self.log_text.see('end')
        
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, 'end')