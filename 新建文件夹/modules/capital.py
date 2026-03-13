# modules/capital.py
import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime, timedelta
import json

class CapitalModule:
    """资金流向功能模块"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_symbol = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面"""
        # 创建左右两栏
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 左侧：资金流向图表
        left_frame = ttk.LabelFrame(main_frame, text="资金流向图", padding=5)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.create_capital_chart(left_frame)
        
        # 右侧：资金明细
        right_frame = ttk.LabelFrame(main_frame, text="资金明细", padding=5)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        self.create_capital_details(right_frame)
        
    def create_capital_chart(self, parent):
        """创建资金流向图表"""
        # 使用简单的条形图显示
        self.chart_frame = ttk.Frame(parent)
        self.chart_frame.pack(fill='both', expand=True)
        
        # 创建画布
        self.canvas = tk.Canvas(self.chart_frame, bg='white', height=300)
        self.canvas.pack(fill='both', expand=True)
        
    def create_capital_details(self, parent):
        """创建资金明细"""
        # 统计数据
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill='x', pady=5)
        
        self.stats_labels = {}
        stats_items = [
            ('主力净流入', 'main_net'),
            ('主力流入', 'main_inflow'),
            ('主力流出', 'main_outflow'),
            ('散户净流入', 'retail_net'),
            ('散户流入', 'retail_inflow'),
            ('散户流出', 'retail_outflow'),
            ('超大单净流入', 'super_large_net'),
            ('大单净流入', 'large_net'),
            ('中单净流入', 'medium_net'),
            ('小单净流入', 'small_net')
        ]
        
        for i, (label, key) in enumerate(stats_items):
            frame = ttk.Frame(stats_frame)
            frame.grid(row=i//2, column=i%2, sticky='w', padx=10, pady=2)
            
            ttk.Label(frame, text=f"{label}:", width=10).pack(side='left')
            self.stats_labels[key] = ttk.Label(frame, text="--", font=('Arial', 10, 'bold'))
            self.stats_labels[key].pack(side='left', padx=5)
            
        # 历史资金流向
        history_frame = ttk.LabelFrame(parent, text="历史资金流向", padding=5)
        history_frame.pack(fill='both', expand=True, pady=5)
        
        columns = ('日期', '主力净流入', '散户净流入', '净占比')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
            
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def load_data(self, symbol, name):
        """加载资金数据"""
        self.current_symbol = symbol
        
        # 模拟数据（实际应从API获取）
        data = self.fetch_capital_data(symbol)
        
        if data:
            self.update_display(data)
            
    def fetch_capital_data(self, symbol):
        """获取资金数据（模拟）"""
        # 这里应该从真实的API获取数据
        # 由于A股资金数据需要专业数据源，这里使用模拟数据
        
        import random
        
        # 生成模拟数据
        main_inflow = random.uniform(1000, 5000)
        main_outflow = random.uniform(800, 4000)
        retail_inflow = random.uniform(500, 2000)
        retail_outflow = random.uniform(400, 1800)
        
        main_net = main_inflow - main_outflow
        retail_net = retail_inflow - retail_outflow
        
        data = {
            'main_inflow': main_inflow,
            'main_outflow': main_outflow,
            'main_net': main_net,
            'retail_inflow': retail_inflow,
            'retail_outflow': retail_outflow,
            'retail_net': retail_net,
            'super_large_net': main_net * 0.6,
            'large_net': main_net * 0.4,
            'medium_net': retail_net * 0.3,
            'small_net': retail_net * 0.7,
            'history': []
        }
        
        # 生成历史数据
        for i in range(5):
            date = (datetime.now() - timedelta(days=i+1)).strftime('%m-%d')
            data['history'].append({
                'date': date,
                'main_net': random.uniform(-1000, 1000),
                'retail_net': random.uniform(-500, 500),
                'ratio': random.uniform(-5, 5)
            })
            
        return data
        
    def update_display(self, data):
        """更新显示"""
        # 更新统计标签
        for key, label in self.stats_labels.items():
            if key in data:
                value = data[key]
                if abs(value) > 10000:
                    text = f"{value/10000:.2f}亿"
                else:
                    text = f"{value:.2f}万"
                    
                # 设置颜色
                if 'net' in key:
                    if value > 0:
                        label.config(text=text, foreground='red')
                    elif value < 0:
                        label.config(text=text, foreground='green')
                    else:
                        label.config(text=text, foreground='black')
                else:
                    label.config(text=text, foreground='black')
                    
        # 绘制资金流向图
        self.draw_capital_chart(data)
        
        # 更新历史数据
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        for item in data['history']:
            color = 'red' if item['main_net'] > 0 else 'green'
            self.history_tree.insert('', 'end', values=(
                item['date'],
                f"{item['main_net']/10000:.2f}亿",
                f"{item['retail_net']/10000:.2f}亿",
                f"{item['ratio']:+.2f}%"
            ), tags=(color,))
            
        self.history_tree.tag_configure('red', foreground='red')
        self.history_tree.tag_configure('green', foreground='green')
        
    def draw_capital_chart(self, data):
        """绘制资金流向图"""
        self.canvas.delete('all')
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:
            self.canvas.after(100, lambda: self.draw_capital_chart(data))
            return
            
        # 绘制标题
        self.canvas.create_text(width//2, 20, text="今日资金流向", font=('Arial', 12, 'bold'))
        
        # 绘制柱状图
        bar_width = 60
        spacing = 40
        start_x = (width - (bar_width * 4 + spacing * 3)) // 2
        
        items = [
            ('主力流入', data['main_inflow'], 'red'),
            ('主力流出', data['main_outflow'], 'green'),
            ('散户流入', data['retail_inflow'], 'lightcoral'),
            ('散户流出', data['retail_outflow'], 'lightgreen')
        ]
        
        max_value = max([abs(item[1]) for item in items]) * 1.2
        
        for i, (label, value, color) in enumerate(items):
            x = start_x + i * (bar_width + spacing)
            
            # 计算柱状图高度
            bar_height = (value / max_value) * (height - 150)
            
            # 绘制柱子
            y0 = height - 100
            y1 = y0 - bar_height
            self.canvas.create_rectangle(x, y0, x + bar_width, y1, 
                                       fill=color, outline='black')
            
            # 绘制标签
            self.canvas.create_text(x + bar_width//2, y0 + 20, text=label, font=('Arial', 9))
            
            # 绘制数值
            if value > 10000:
                text = f"{value/10000:.1f}亿"
            else:
                text = f"{value:.0f}万"
            self.canvas.create_text(x + bar_width//2, y1 - 10, text=text, font=('Arial', 9, 'bold'))