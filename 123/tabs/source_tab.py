# tabs/source_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import akshare as ak

class SourceTab:
    """数据源设置标签页"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        source_frame = ttk.LabelFrame(self.parent, text="数据源配置", padding=10)
        source_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Label(source_frame, text="A股数据源:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=10)
        ttk.Label(source_frame, text="使用AKShare获取A股历史数据").grid(row=0, column=1, sticky='w', padx=10)
        
        ttk.Button(source_frame, text="测试A股数据连接", command=self.test_akshare).grid(row=1, column=0, pady=5)
        
        ttk.Label(source_frame, text="备用数据源:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=10)
        ttk.Label(source_frame, text="如AKShare失败，将自动使用Yahoo Finance").grid(row=2, column=1, sticky='w', padx=10)
        
        self.source_status = tk.StringVar()
        self.source_status.set("数据源状态: 未测试")
        ttk.Label(source_frame, textvariable=self.source_status, font=('Arial', 9)).grid(row=3, column=0, columnspan=2, pady=10)
        
    def test_akshare(self):
        try:
            stock_code = "002531"
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                   start_date=start_date, end_date=end_date, adjust="")
            
            if not df.empty:
                self.source_status.set("✅ AKShare连接成功！可以获取A股数据")
                self.app.log("AKShare测试成功")
                messagebox.showinfo("成功", "AKShare连接正常")
            else:
                self.source_status.set("⚠️ AKShare返回空数据")
        except Exception as e:
            self.source_status.set(f"❌ AKShare连接失败: {str(e)}")
            self.app.log(f"AKShare测试失败: {str(e)}")