# widgets/info_display.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime

class InfoDisplay:
    """信息显示组件"""
    
    def __init__(self, parent):
        self.parent = parent
        
        # 创建主框架
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill='both', expand=True)
        
        # 创建树形视图
        self.tree = ttk.Treeview(self.main_frame, show='headings', height=15)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 创建文本框用于详细内容
        self.text_frame = ttk.Frame(parent)
        self.text_frame.pack(fill='both', expand=True)
        
        self.text = scrolledtext.ScrolledText(self.text_frame, height=10, wrap=tk.WORD)
        self.text.pack(fill='both', expand=True)
        
        # 默认隐藏文本框
        self.text_frame.pack_forget()
        
    def show_tree(self, columns, data):
        """显示树形数据"""
        # 清空并隐藏文本框
        self.text_frame.pack_forget()
        self.main_frame.pack(fill='both', expand=True)
        
        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 设置列
        self.tree['columns'] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
            
        # 添加数据
        for item in data:
            self.tree.insert('', 'end', values=item)
            
    def show_text(self, title, content):
        """显示文本内容"""
        self.main_frame.pack_forget()
        self.text_frame.pack(fill='both', expand=True)
        
        self.text.delete(1.0, 'end')
        self.text.insert('end', f"{'='*60}\n")
        self.text.insert('end', f"{title}\n")
        self.text.insert('end', f"{'='*60}\n\n")
        self.text.insert('end', content)
        self.text.config(state='disabled')
        
    def clear(self):
        """清空显示"""
        self.main_frame.pack(fill='both', expand=True)
        self.text_frame.pack_forget()
        
        for item in self.tree.get_children():
            self.tree.delete(item)

class TabView:
    """标签页视图组件"""
    
    def __init__(self, parent):
        self.parent = parent
        
        # 创建笔记本
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True)
        
        self.tabs = {}
        
    def add_tab(self, name, title):
        """添加标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        self.tabs[name] = frame
        return frame
        
    def get_tab(self, name):
        """获取标签页"""
        return self.tabs.get(name)
        
    def select_tab(self, name):
        """选择标签页"""
        if name in self.tabs:
            self.notebook.select(self.tabs[name])