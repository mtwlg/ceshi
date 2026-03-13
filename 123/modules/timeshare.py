# modules/timeshare.py
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from widgets.chart_widget import TimeShareChart

class TimeShareModule:
    """分时图功能模块"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_symbol = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面"""
        # 控制栏
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(control_frame, text="日期选择:").pack(side='left', padx=5)
        self.date_var = tk.StringVar(value="今日")
        date_combo = ttk.Combobox(control_frame, textvariable=self.date_var, 
                                  values=["今日", "昨日", "近5日"], width=10)
        date_combo.pack(side='left', padx=5)
        date_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        ttk.Button(control_frame, text="刷新", command=self.refresh_data).pack(side='left', padx=5)
        
        # 图表区域
        self.chart = TimeShareChart(self.parent)
        
        # 数据表格
        table_frame = ttk.LabelFrame(self.parent, text="分时数据", padding=5)
        table_frame.pack(fill='x', padx=5, pady=5)
        
        columns = ('时间', '价格', '涨跌幅', '成交量', '均价')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=5)
        
        col_widths = [100, 80, 80, 100, 80]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
            
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def load_data(self, symbol, name):
        """加载分时数据"""
        self.current_symbol = symbol
        self.current_name = name
        
        # 获取数据
        data = self.fetch_timeshare_data(symbol)
        
        if data:
            # 绘制图表
            self.chart.plot_timeshare(data, name)
            
            # 更新表格
            self.update_table(data)
            
    def fetch_timeshare_data(self, symbol):
        """获取分时数据"""
        try:
            # 处理代码格式
            market_symbol = self.app.data_fetcher.format_symbol(symbol, 'A股')
            
            # 获取今日分钟数据
            stock = yf.Ticker(market_symbol)
            hist = stock.history(period="1d", interval="1m")
            
            if hist.empty:
                return None
                
            # 计算均价
            hist['Avg'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
            
            # 转换为列表
            data = []
            prev_close = hist['Close'].iloc[0]
            
            for idx, row in hist.iterrows():
                time_str = idx.strftime('%H:%M')
                change = ((row['Close'] - prev_close) / prev_close) * 100
                
                data.append({
                    'time': time_str,
                    'price': round(row['Close'], 2),
                    'change': round(change, 2),
                    'volume': int(row['Volume']),
                    'avg_price': round(row['Avg'], 2),
                    'prev_close': prev_close
                })
                
            return data
            
        except Exception as e:
            self.app.log(f"获取分时数据失败: {str(e)}")
            return None
            
    def update_table(self, data):
        """更新表格"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for d in data[-20:]:  # 只显示最近20条
            self.tree.insert('', 'end', values=(
                d['time'],
                d['price'],
                f"{d['change']:+.2f}%",
                f"{d['volume']/1000:.0f}K",
                d['avg_price']
            ))
            
    def on_date_change(self, event):
        """日期选择变化"""
        if self.current_symbol:
            self.load_data(self.current_symbol, self.current_name)
            
    def refresh_data(self):
        """刷新数据"""
        if self.current_symbol:
            self.load_data(self.current_symbol, self.current_name)