# modules/research.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import requests
import json

class ResearchModule:
    """研报功能模块"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_symbol = None
        self.reports = []
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面"""
        # 控制栏
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(control_frame, text="机构名称:").pack(side='left', padx=5)
        self.org_entry = ttk.Entry(control_frame, width=20)
        self.org_entry.pack(side='left', padx=5)
        
        ttk.Label(control_frame, text="评级:").pack(side='left', padx=5)
        self.rating_var = tk.StringVar(value="全部")
        rating_combo = ttk.Combobox(control_frame, textvariable=self.rating_var,
                                    values=["全部", "买入", "增持", "中性", "减持", "卖出"], width=8)
        rating_combo.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="搜索", command=self.search).pack(side='left', padx=5)
        ttk.Button(control_frame, text="刷新", command=self.refresh_data).pack(side='left', padx=5)
        
        # 研报列表
        list_frame = ttk.LabelFrame(self.parent, text="研报列表", padding=5)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('日期', '研报标题', '机构名称', '研究员', '评级', '目标价')
        self.report_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        col_widths = [100, 300, 150, 100, 80, 100]
        for col, width in zip(columns, col_widths):
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=width)
            
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=scrollbar.set)
        
        self.report_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.report_tree.bind('<<TreeviewSelect>>', self.on_report_select)
        
        # 研报摘要
        summary_frame = ttk.LabelFrame(self.parent, text="研报摘要", padding=5)
        summary_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=8, wrap=tk.WORD)
        scrollbar2 = ttk.Scrollbar(summary_frame, orient='vertical', command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=scrollbar2.set)
        
        self.summary_text.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
        # 评级分布
        rating_frame = ttk.LabelFrame(self.parent, text="机构评级分布", padding=5)
        rating_frame.pack(fill='x', padx=5, pady=5)
        
        self.create_rating_chart(rating_frame)
        
    def create_rating_chart(self, parent):
        """创建评级分布图"""
        self.rating_frame = ttk.Frame(parent)
        self.rating_frame.pack(fill='x')
        
        ratings = ['买入', '增持', '中性', '减持', '卖出']
        colors = ['red', 'orange', 'gray', 'green', 'darkgreen']
        
        self.rating_bars = {}
        self.rating_labels = {}
        
        for i, (rating, color) in enumerate(zip(ratings, colors)):
            frame = ttk.Frame(self.rating_frame)
            frame.pack(side='left', fill='x', expand=True, padx=2)
            
            ttk.Label(frame, text=rating).pack()
            
            bar_frame = ttk.Frame(frame, height=20, width=60)
            bar_frame.pack(pady=2)
            bar_frame.pack_propagate(False)
            
            canvas = tk.Canvas(bar_frame, bg='lightgray', height=20, width=60)
            canvas.pack()
            
            self.rating_bars[rating] = canvas
            
            label = ttk.Label(frame, text="0")
            label.pack()
            self.rating_labels[rating] = label
            
    def load_data(self, symbol, name):
        """加载研报数据"""
        self.current_symbol = symbol
        
        # 获取研报数据
        self.reports = self.fetch_research_reports(symbol)
        self.update_list()
        self.update_rating_chart()
        
    def fetch_research_reports(self, symbol):
        """获取研报数据（模拟）"""
        # 这里应该从真实的研报API获取数据
        # 使用模拟数据
        reports = []
        
        organizations = [
            '中信证券', '国泰君安', '海通证券', '广发证券', 
            '招商证券', '华泰证券', '申万宏源', '银河证券'
        ]
        
        researchers = ['张明', '李华', '王强', '刘伟', '陈东', '赵阳']
        ratings = ['买入', '增持', '中性', '减持', '卖出']
        titles = [
            '深度研究：公司业务有望超预期',
            '首次覆盖：成长空间广阔',
            '季报点评：业绩符合预期',
            '行业专题：景气度持续提升',
            '事件点评：新项目落地',
            '年度策略：布局良机'
        ]
        
        for i in range(30):
            date = datetime.now() - timedelta(days=i*3)
            rating = ratings[i % len(ratings)]
            
            reports.append({
                'date': date.strftime('%Y-%m-%d'),
                'title': f"{symbol}：{titles[i % len(titles)]}",
                'organization': organizations[i % len(organizations)],
                'researcher': researchers[i % len(researchers)],
                'rating': rating,
                'target_price': round(10 + i * 0.5, 2),
                'summary': f"""【{rating}】{titles[i % len(titles)]}

核心观点：
1. 公司基本面稳健，业绩持续增长
2. 行业景气度提升，公司有望受益
3. 估值具有吸引力，建议{rating}

盈利预测：
预计2024-2026年EPS分别为1.2/1.5/1.8元
当前股价对应PE分别为15/12/10倍

风险提示：
1. 行业竞争加剧风险
2. 原材料价格波动风险
3. 政策变化风险"""
            })
            
        return reports
        
    def update_list(self):
        """更新研报列表"""
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
            
        # 根据筛选条件过滤
        filtered = self.filter_reports()
        
        for report in filtered:
            self.report_tree.insert('', 'end', values=(
                report['date'],
                report['title'],
                report['organization'],
                report['researcher'],
                report['rating'],
                report['target_price']
            ))
            
    def filter_reports(self):
        """筛选研报"""
        filtered = self.reports
        
        # 按机构筛选
        org = self.org_entry.get().strip()
        if org:
            filtered = [r for r in filtered if org.lower() in r['organization'].lower()]
            
        # 按评级筛选
        rating = self.rating_var.get()
        if rating != '全部':
            filtered = [r for r in filtered if r['rating'] == rating]
            
        return filtered
        
    def update_rating_chart(self):
        """更新评级分布图"""
        # 统计各评级数量
        rating_count = {'买入': 0, '增持': 0, '中性': 0, '减持': 0, '卖出': 0}
        
        for report in self.reports:
            if report['rating'] in rating_count:
                rating_count[report['rating']] += 1
                
        max_count = max(rating_count.values()) if rating_count.values() else 1
        
        # 更新图表
        for rating, count in rating_count.items():
            if rating in self.rating_bars:
                canvas = self.rating_bars[rating]
                canvas.delete('all')
                
                # 计算柱状图高度
                bar_height = (count / max_count) * 18 if max_count > 0 else 0
                
                # 绘制柱子
                canvas.create_rectangle(5, 18 - bar_height, 55, 18, 
                                      fill='blue', outline='black')
                
                # 更新标签
                if rating in self.rating_labels:
                    self.rating_labels[rating].config(text=str(count))
                    
    def search(self):
        """搜索"""
        self.update_list()
        
    def refresh_data(self):
        """刷新数据"""
        if self.current_symbol:
            self.reports = self.fetch_research_reports(self.current_symbol)
            self.update_list()
            self.update_rating_chart()
            
    def on_report_select(self, event):
        """选择研报"""
        selected = self.report_tree.selection()
        if not selected:
            return
            
        item = self.report_tree.item(selected[0])
        values = item['values']
        
        # 查找对应的研报摘要
        for report in self.reports:
            if (report['date'] == values[0] and 
                report['title'] == values[1] and 
                report['organization'] == values[2]):
                self.summary_text.delete(1.0, 'end')
                self.summary_text.insert('end', report['summary'])
                break