# modules/details.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pandas as pd

class DetailsModule:
    """详细信息功能模块"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_symbol = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面"""
        # 创建标签页
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 公司概况
        self.create_company_profile()
        
        # 财务数据
        self.create_financial_data()
        
        # 股东信息
        self.create_shareholder_info()
        
        # 分红融资
        self.create_dividend_info()
        
    def create_company_profile(self):
        """公司概况"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='公司概况')
        
        # 基本信息
        info_frame = ttk.LabelFrame(frame, text="基本信息", padding=10)
        info_frame.pack(fill='x', padx=5, pady=5)
        
        self.info_labels = {}
        info_items = [
            ('公司名称', 'company_name'),
            ('英文名称', 'eng_name'),
            ('上市日期', 'list_date'),
            ('注册资本', 'registered_capital'),
            ('所属行业', 'industry'),
            ('主营业务', 'business'),
            ('法人代表', 'legal_rep'),
            ('总经理', 'general_manager'),
            ('董事会秘书', 'secretary'),
            ('注册地址', 'address'),
            ('办公地址', 'office_address'),
            ('公司电话', 'phone'),
            ('公司传真', 'fax'),
            ('公司网址', 'website')
        ]
        
        for i, (label, key) in enumerate(info_items):
            frame = ttk.Frame(info_frame)
            frame.pack(fill='x', pady=2)
            
            ttk.Label(frame, text=f"{label}:", width=15).pack(side='left')
            self.info_labels[key] = ttk.Label(frame, text="--", wraplength=400)
            self.info_labels[key].pack(side='left', padx=5)
            
        # 公司简介
        intro_frame = ttk.LabelFrame(frame, text="公司简介", padding=10)
        intro_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.intro_text = tk.Text(intro_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(intro_frame, orient='vertical', command=self.intro_text.yview)
        self.intro_text.configure(yscrollcommand=scrollbar.set)
        
        self.intro_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_financial_data(self):
        """财务数据"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='财务数据')
        
        # 创建左右两栏
        left_frame = ttk.Frame(frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        right_frame = ttk.Frame(frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # 主要指标
        metrics_frame = ttk.LabelFrame(left_frame, text="主要指标", padding=5)
        metrics_frame.pack(fill='both', expand=True)
        
        columns = ('指标', '2024Q1', '2023Q4', '2023Q3')
        self.metrics_tree = ttk.Treeview(metrics_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.metrics_tree.heading(col, text=col)
            self.metrics_tree.column(col, width=100)
            
        scrollbar = ttk.Scrollbar(metrics_frame, orient='vertical', command=self.metrics_tree.yview)
        self.metrics_tree.configure(yscrollcommand=scrollbar.set)
        
        self.metrics_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 资产负债表
        balance_frame = ttk.LabelFrame(right_frame, text="资产负债表", padding=5)
        balance_frame.pack(fill='both', expand=True)
        
        columns2 = ('项目', '2024Q1', '2023Q4', '2023Q3')
        self.balance_tree = ttk.Treeview(balance_frame, columns=columns2, show='headings', height=10)
        
        for col in columns2:
            self.balance_tree.heading(col, text=col)
            self.balance_tree.column(col, width=100)
            
        scrollbar2 = ttk.Scrollbar(balance_frame, orient='vertical', command=self.balance_tree.yview)
        self.balance_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.balance_tree.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
    def create_shareholder_info(self):
        """股东信息"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='股东信息')
        
        # 前十大股东
        top_frame = ttk.LabelFrame(frame, text="前十大股东", padding=5)
        top_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('股东名称', '持股数量(万股)', '持股比例(%)', '股份性质')
        self.shareholder_tree = ttk.Treeview(top_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.shareholder_tree.heading(col, text=col)
            self.shareholder_tree.column(col, width=150)
            
        scrollbar = ttk.Scrollbar(top_frame, orient='vertical', command=self.shareholder_tree.yview)
        self.shareholder_tree.configure(yscrollcommand=scrollbar.set)
        
        self.shareholder_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 股东户数变化
        change_frame = ttk.LabelFrame(frame, text="股东户数变化", padding=5)
        change_frame.pack(fill='x', padx=5, pady=5)
        
        columns2 = ('日期', '股东户数', '较上期变化', '户均持股')
        self.shareholder_change_tree = ttk.Treeview(change_frame, columns=columns2, show='headings', height=5)
        
        for col in columns2:
            self.shareholder_change_tree.heading(col, text=col)
            self.shareholder_change_tree.column(col, width=120)
            
        scrollbar2 = ttk.Scrollbar(change_frame, orient='vertical', command=self.shareholder_change_tree.yview)
        self.shareholder_change_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.shareholder_change_tree.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
    def create_dividend_info(self):
        """分红融资"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='分红融资')
        
        # 分红记录
        dividend_frame = ttk.LabelFrame(frame, text="分红记录", padding=5)
        dividend_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('分红年度', '分红方案', '股权登记日', '除权除息日', '派息日')
        self.dividend_tree = ttk.Treeview(dividend_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.dividend_tree.heading(col, text=col)
            self.dividend_tree.column(col, width=120)
            
        scrollbar = ttk.Scrollbar(dividend_frame, orient='vertical', command=self.dividend_tree.yview)
        self.dividend_tree.configure(yscrollcommand=scrollbar.set)
        
        self.dividend_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def load_data(self, symbol, name):
        """加载详细信息"""
        self.current_symbol = symbol
        
        # 模拟数据（实际应从API获取）
        data = self.fetch_details_data(symbol)
        
        if data:
            self.update_display(data)
            
    def fetch_details_data(self, symbol):
        """获取详细信息（模拟）"""
        # 这里应该从真实的API获取数据
        # 使用模拟数据
        return {
            'company_name': f"{self.current_symbol}股份有限公司",
            'eng_name': f"{self.current_symbol} CO.,LTD",
            'list_date': '2010-01-01',
            'registered_capital': '100000万元',
            'industry': '制造业',
            'business': '产品研发、生产、销售',
            'legal_rep': '张三',
            'general_manager': '李四',
            'secretary': '王五',
            'address': '北京市朝阳区',
            'office_address': '上海市浦东新区',
            'phone': '010-12345678',
            'fax': '010-87654321',
            'website': 'www.example.com',
            'introduction': '公司是一家专注于...'
        }
        
    def update_display(self, data):
        """更新显示"""
        # 更新基本信息
        for key, label in self.info_labels.items():
            if key in data:
                label.config(text=data[key])
                
        # 更新公司简介
        self.intro_text.delete(1.0, 'end')
        self.intro_text.insert('end', data.get('introduction', '暂无简介'))