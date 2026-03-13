# modules/announcements.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json

class AnnouncementsModule:
    """公告功能模块"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_symbol = None
        self.announcements = []
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面"""
        # 控制栏
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(control_frame, text="公告类型:").pack(side='left', padx=5)
        self.type_var = tk.StringVar(value="全部")
        type_combo = ttk.Combobox(control_frame, textvariable=self.type_var,
                                  values=["全部", "定期报告", "临时公告", "股东大会", "分红配股"], width=15)
        type_combo.pack(side='left', padx=5)
        type_combo.bind('<<ComboboxSelected>>', self.on_type_change)
        
        ttk.Label(control_frame, text="日期范围:").pack(side='left', padx=5)
        self.date_range = ttk.Combobox(control_frame, 
                                       values=["近一周", "近一月", "近三月", "近一年"], width=10)
        self.date_range.set("近一月")
        self.date_range.pack(side='left', padx=5)
        self.date_range.bind('<<ComboboxSelected>>', self.on_date_change)
        
        ttk.Button(control_frame, text="搜索", command=self.search).pack(side='left', padx=5)
        ttk.Button(control_frame, text="刷新", command=self.refresh_data).pack(side='left', padx=5)
        
        # 公告列表
        list_frame = ttk.LabelFrame(self.parent, text="公告列表", padding=5)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('日期', '公告标题', '类型', '文件')
        self.announcement_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        col_widths = [100, 400, 100, 80]
        for col, width in zip(columns, col_widths):
            self.announcement_tree.heading(col, text=col)
            self.announcement_tree.column(col, width=width)
            
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.announcement_tree.yview)
        self.announcement_tree.configure(yscrollcommand=scrollbar.set)
        
        self.announcement_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.announcement_tree.bind('<<TreeviewSelect>>', self.on_announcement_select)
        
        # 公告内容
        content_frame = ttk.LabelFrame(self.parent, text="公告内容", padding=5)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.content_text = tk.Text(content_frame, height=10, wrap=tk.WORD)
        scrollbar2 = ttk.Scrollbar(content_frame, orient='vertical', command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar2.set)
        
        self.content_text.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
    def load_data(self, symbol, name):
        """加载公告数据"""
        self.current_symbol = symbol
        
        # 获取公告数据
        self.announcements = self.fetch_announcements(symbol)
        self.update_list()
        
    def fetch_announcements(self, symbol):
        """获取公告数据（模拟）"""
        # 这里应该从真实的公告API获取数据
        # 使用模拟数据
        announcements = []
        
        types = ['定期报告', '临时公告', '股东大会', '分红配股']
        titles = [
            '2024年第一季度报告',
            '关于召开2023年度股东大会的通知',
            '2023年年度权益分派实施公告',
            '关于公司董事辞职的公告',
            '关于投资新建项目的公告',
            '关于获得政府补助的公告',
            '关于控股股东部分股份质押的公告',
            '2023年年度报告摘要'
        ]
        
        for i in range(20):
            date = datetime.now() - timedelta(days=i*2)
            announcements.append({
                'date': date.strftime('%Y-%m-%d'),
                'title': f"{titles[i % len(titles)]}{'' if i < len(titles) else '（补充）'}",
                'type': types[i % len(types)],
                'file': 'PDF',
                'content': f"""这是{date.strftime('%Y-%m-%d')}发布的公告内容。

{titles[i % len(titles)]}

重要内容提示：
1. 本次公告涉及公司重大事项
2. 敬请投资者注意投资风险
3. 具体内容详见附件

公告正文：
根据相关法律法规的规定，现将有关事项公告如下：
一、基本情况
二、审议程序
三、对公司的影响
四、备查文件

特此公告。

{self.current_symbol}股份有限公司董事会
{date.strftime('%Y年%m月%d日')}"""
            })
            
        return announcements
        
    def update_list(self):
        """更新公告列表"""
        for item in self.announcement_tree.get_children():
            self.announcement_tree.delete(item)
            
        # 根据筛选条件过滤
        filtered = self.filter_announcements()
        
        for ann in filtered:
            self.announcement_tree.insert('', 'end', values=(
                ann['date'],
                ann['title'],
                ann['type'],
                ann['file']
            ))
            
    def filter_announcements(self):
        """筛选公告"""
        filtered = self.announcements
        
        # 按类型筛选
        ann_type = self.type_var.get()
        if ann_type != '全部':
            filtered = [a for a in filtered if a['type'] == ann_type]
            
        # 按日期筛选
        date_range = self.date_range.get()
        if date_range != '全部':
            days = {
                '近一周': 7,
                '近一月': 30,
                '近三月': 90,
                '近一年': 365
            }.get(date_range, 30)
            
            cutoff = datetime.now() - timedelta(days=days)
            filtered = [a for a in filtered if datetime.strptime(a['date'], '%Y-%m-%d') >= cutoff]
            
        return filtered
        
    def on_type_change(self, event):
        """类型变化"""
        self.update_list()
        
    def on_date_change(self, event):
        """日期范围变化"""
        self.update_list()
        
    def search(self):
        """搜索"""
        self.update_list()
        
    def refresh_data(self):
        """刷新数据"""
        if self.current_symbol:
            self.announcements = self.fetch_announcements(self.current_symbol)
            self.update_list()
            
    def on_announcement_select(self, event):
        """选择公告"""
        selected = self.announcement_tree.selection()
        if not selected:
            return
            
        item = self.announcement_tree.item(selected[0])
        values = item['values']
        
        # 查找对应的公告内容
        for ann in self.announcements:
            if ann['date'] == values[0] and ann['title'] == values[1]:
                self.content_text.delete(1.0, 'end')
                self.content_text.insert('end', ann['content'])
                break