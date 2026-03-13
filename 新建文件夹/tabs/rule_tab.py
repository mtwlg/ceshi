# tabs/rule_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

class RuleTab:
    """买卖规则标签页"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        # 规则列表
        list_frame = ttk.LabelFrame(self.parent, text="已有规则", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.rule_tree = ttk.Treeview(list_frame, columns=('类型', '条件', '参数1', '参数2', '动作', '状态'), show='headings', height=8)
        self.rule_tree.heading('类型', text='规则类型')
        self.rule_tree.heading('条件', text='条件')
        self.rule_tree.heading('参数1', text='参数1')
        self.rule_tree.heading('参数2', text='参数2')
        self.rule_tree.heading('动作', text='触发动作')
        self.rule_tree.heading('状态', text='状态')
        
        self.rule_tree.column('类型', width=120)
        self.rule_tree.column('条件', width=100)
        self.rule_tree.column('参数1', width=80)
        self.rule_tree.column('参数2', width=80)
        self.rule_tree.column('动作', width=150)
        self.rule_tree.column('状态', width=80)
        
        self.rule_tree.pack(fill='both', expand=True)
        
        # 添加规则区域
        add_frame = ttk.LabelFrame(self.parent, text="添加新规则", padding=10)
        add_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(add_frame, text="规则类型:").grid(row=0, column=0, sticky='w', padx=5)
        self.rule_type = ttk.Combobox(add_frame, values=['价格', '涨跌幅', '成交量', '筹码集中度'], width=15)
        self.rule_type.set('筹码集中度')
        self.rule_type.grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="条件:").grid(row=0, column=2, sticky='w', padx=5)
        self.condition = ttk.Combobox(add_frame, values=['买入条件', '卖出条件'], width=12)
        self.condition.set('买入条件')
        self.condition.grid(row=0, column=3, padx=5)
        
        ttk.Label(add_frame, text="筹码比例(%):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.chip_percent = ttk.Entry(add_frame, width=10)
        self.chip_percent.insert(0, "90")
        self.chip_percent.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="价格区间(%):").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.price_range = ttk.Entry(add_frame, width=10)
        self.price_range.insert(0, "15")
        self.price_range.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(add_frame, text="触发动作:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.action = ttk.Combobox(add_frame, values=['买入信号', '卖出信号', '提醒'], width=15)
        self.action.set('买入信号')
        self.action.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="备注:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.remark = ttk.Entry(add_frame, width=20)
        self.remark.grid(row=2, column=3, columnspan=2, padx=5, pady=5)
        
        btn_frame = ttk.Frame(add_frame)
        btn_frame.grid(row=3, column=0, columnspan=5, pady=10)
        
        ttk.Button(btn_frame, text="添加规则", command=self.add_rule).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="删除规则", command=self.delete_rule).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="启用/禁用", command=self.toggle_rule).pack(side='left', padx=5)
        
        self.refresh_rule_list()
        
    def add_rule(self):
        try:
            rule = {
                'type': self.rule_type.get(),
                'condition': self.condition.get(),
                'chip_percent': float(self.chip_percent.get()),
                'price_range': float(self.price_range.get()),
                'action': self.action.get(),
                'remark': self.remark.get(),
                'enabled': True
            }
            self.app.rules.append(rule)
            self.app.save_rules()
            self.refresh_rule_list()
            self.app.log(f"添加新规则: {rule}")
        except ValueError as e:
            messagebox.showwarning("警告", f"参数格式错误: {str(e)}")
            
    def delete_rule(self):
        selected = self.rule_tree.selection()
        if selected:
            index = self.rule_tree.index(selected[0])
            del self.app.rules[index]
            self.app.save_rules()
            self.refresh_rule_list()
            
    def toggle_rule(self):
        selected = self.rule_tree.selection()
        if selected:
            index = self.rule_tree.index(selected[0])
            self.app.rules[index]['enabled'] = not self.app.rules[index]['enabled']
            self.app.save_rules()
            self.refresh_rule_list()
            
    def refresh_rule_list(self):
        for item in self.rule_tree.get_children():
            self.rule_tree.delete(item)
            
        for rule in self.app.rules:
            status = "启用" if rule['enabled'] else "禁用"
            self.rule_tree.insert('', 'end', values=(
                rule['type'],
                rule['condition'],
                f"{rule['chip_percent']}%",
                f"{rule['price_range']}%",
                f"{rule['action']} ({rule['remark']})",
                status
            ))