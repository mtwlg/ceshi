# tabs/position_tab.py
import tkinter as tk
from tkinter import ttk, messagebox

class PositionTab:
    """持仓设置标签页"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面"""
        position_frame = ttk.LabelFrame(self.parent, text="持仓成本设置", padding=10)
        position_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(position_frame, text="成本价:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.cost_price = ttk.Entry(position_frame, width=15)
        self.cost_price.insert(0, "0")
        self.cost_price.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(position_frame, text="持仓数量(股):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.position_quantity = ttk.Entry(position_frame, width=15)
        self.position_quantity.insert(0, "0")
        self.position_quantity.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(position_frame, text="持仓市值:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.position_value = ttk.Entry(position_frame, width=15, state='readonly')
        self.position_value.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(position_frame, text="盈亏金额:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.profit_loss = ttk.Entry(position_frame, width=15, state='readonly')
        self.profit_loss.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(position_frame, text="盈亏比例:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.profit_percent = ttk.Entry(position_frame, width=15, state='readonly')
        self.profit_percent.grid(row=4, column=1, padx=5, pady=5)
        
        # 保存按钮
        ttk.Button(position_frame, text="保存持仓设置", command=self.save_position).grid(row=5, column=0, columnspan=2, pady=10)
        
        # 加载已保存的数据
        self.load_position()
        
    def save_position(self):
        """保存持仓设置"""
        try:
            cost = float(self.cost_price.get())
            quantity = int(self.position_quantity.get())
            
            position_data = {
                'cost_price': cost,
                'quantity': quantity
            }
            
            self.app.save_position(position_data)
            self.app.log(f"持仓设置已保存: 成本价={cost}, 数量={quantity}")
            messagebox.showinfo("成功", "持仓设置已保存")
            
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的数字")
            
    def load_position(self):
        """加载持仓设置"""
        position_data = self.app.load_position()
        if position_data:
            self.cost_price.delete(0, 'end')
            self.cost_price.insert(0, str(position_data.get('cost_price', '0')))
            self.position_quantity.delete(0, 'end')
            self.position_quantity.insert(0, str(position_data.get('quantity', '0')))
            
    def update_display(self, current_price):
        """更新持仓显示"""
        try:
            cost = float(self.cost_price.get())
            quantity = int(self.position_quantity.get())
            
            if cost > 0 and quantity > 0:
                market_value = current_price * quantity
                self.position_value.config(state='normal')
                self.position_value.delete(0, 'end')
                self.position_value.insert(0, f"{market_value:.2f}")
                self.position_value.config(state='readonly')
                
                profit_amount = (current_price - cost) * quantity
                self.profit_loss.config(state='normal')
                self.profit_loss.delete(0, 'end')
                self.profit_loss.insert(0, f"{profit_amount:+.2f}")
                self.profit_loss.config(state='readonly')
                
                profit_percent = ((current_price - cost) / cost) * 100
                self.profit_percent.config(state='normal')
                self.profit_percent.delete(0, 'end')
                self.profit_percent.insert(0, f"{profit_percent:+.2f}%")
                self.profit_percent.config(state='readonly')
                
        except ValueError:
            pass