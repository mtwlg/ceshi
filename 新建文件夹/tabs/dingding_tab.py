# tabs/dingding_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

class DingDingTab:
    """钉钉设置标签页"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        settings_frame = ttk.LabelFrame(self.parent, text="钉钉机器人设置", padding=10)
        settings_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Label(settings_frame, text="Webhook地址:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.webhook_entry = ttk.Entry(settings_frame, width=50)
        self.webhook_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="密钥:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.secret_entry = ttk.Entry(settings_frame, width=50, show="*")
        self.secret_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="提醒手机号:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.phone_entry = ttk.Entry(settings_frame, width=50)
        self.phone_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
        ttk.Label(settings_frame, text="多个手机号用逗号分隔").grid(row=3, column=1, sticky='w', padx=5)
        
        ttk.Button(settings_frame, text="测试连接", command=self.test_dingding).grid(row=4, column=1, pady=10)
        
    def test_dingding(self):
        webhook = self.webhook_entry.get()
        if not webhook:
            messagebox.showwarning("警告", "请输入Webhook地址")
            return
            
        message = "【测试消息】投资监控系统连接成功！"
        phones = self.phone_entry.get()
        
        success = self.app.ding_sender.send_message(webhook, message, phones)
        if success:
            messagebox.showinfo("成功", "测试消息发送成功")
        else:
            messagebox.showerror("失败", "测试消息发送失败")