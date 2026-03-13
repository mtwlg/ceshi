# tabs/chip_tab.py
import tkinter as tk
from tkinter import ttk, scrolledtext

class ChipTab:
    """筹码分析标签页"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        chip_frame = ttk.LabelFrame(self.parent, text="当前筹码分布", padding=10)
        chip_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.chip_text = scrolledtext.ScrolledText(chip_frame, height=20, width=80)
        self.chip_text.pack(fill='both', expand=True)
        
        result_frame = ttk.LabelFrame(self.parent, text="筹码分析结果", padding=10)
        result_frame.pack(fill='x', padx=10, pady=5)
        
        self.chip_result_var = tk.StringVar()
        self.chip_result_var.set("等待分析...")
        ttk.Label(result_frame, textvariable=self.chip_result_var, font=('Arial', 10, 'bold')).pack()
        
    def update_display(self, chip_analysis):
        if not chip_analysis:
            self.chip_text.delete(1.0, 'end')
            self.chip_text.insert('end', "暂无筹码分析数据")
            return
            
        self.chip_text.delete(1.0, 'end')
        
        result = f"""
╔══════════════════════════════════════════════════════════════╗
║                      筹码分布分析报告                          ║
╠══════════════════════════════════════════════════════════════╣
║ 当前价格: {chip_analysis['current_price']:.2f}                                        
║ 价格区间: {chip_analysis['price_min']:.2f} - {chip_analysis['price_max']:.2f}                      
║ 90%筹码集中度: {chip_analysis['concentration_90']:.2f}%                                  
║ 90%筹码区间: {chip_analysis['start_price']:.2f} - {chip_analysis['end_price']:.2f}                    
╚══════════════════════════════════════════════════════════════╝
        """
        self.chip_text.insert('end', result)
        
        concentration = chip_analysis['concentration_90']
        if concentration <= 15:
            self.chip_result_var.set(f"✅ 强烈买入信号：90%筹码集中在{concentration:.2f}%价格区间！")
        elif concentration >= 25:
            self.chip_result_var.set(f"⚠️ 卖出信号：90%筹码分布在{concentration:.2f}%价格区间！")
        else:
            self.chip_result_var.set(f"⏸️ 观望：当前90%筹码集中在{concentration:.2f}%价格区间")