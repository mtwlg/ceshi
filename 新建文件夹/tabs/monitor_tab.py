# tabs/monitor_tab.py
import tkinter as tk
from tkinter import ttk

class MonitorTab:
    """实时监控标签页"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面"""
        # 监控设置区域
        settings_frame = ttk.LabelFrame(self.parent, text="监控设置", padding=10)
        settings_frame.pack(fill='x', padx=10, pady=5)
        
        # 股票代码
        ttk.Label(settings_frame, text="投资标的代码:").grid(row=0, column=0, sticky='w', padx=5)
        self.symbol_entry = ttk.Entry(settings_frame, width=20)
        self.symbol_entry.grid(row=0, column=1, padx=5)
        ttk.Label(settings_frame, text="A股: 002531 (天顺风能)").grid(row=0, column=2, padx=5)
        
        # 股票名称
        ttk.Label(settings_frame, text="股票名称:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.stock_name_entry = ttk.Entry(settings_frame, width=20)
        self.stock_name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 市场选择
        ttk.Label(settings_frame, text="市场类型:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.market_type = ttk.Combobox(settings_frame, values=['A股', '港股', '美股'], width=10)
        self.market_type.set('A股')
        self.market_type.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # 监控间隔
        ttk.Label(settings_frame, text="监控间隔(秒):").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.interval_entry = ttk.Entry(settings_frame, width=10)
        self.interval_entry.insert(0, str(self.app.config.DEFAULT_INTERVAL))
        self.interval_entry.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        # 历史数据天数
        ttk.Label(settings_frame, text="历史数据天数:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.history_days_entry = ttk.Entry(settings_frame, width=10)
        self.history_days_entry.insert(0, str(self.app.config.DEFAULT_HISTORY_DAYS))
        self.history_days_entry.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        
        # 控制按钮
        btn_frame = ttk.Frame(settings_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="开始监控", command=self.start_monitoring)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止监控", command=self.stop_monitoring, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        self.analyze_btn = ttk.Button(btn_frame, text="立即分析筹码", command=self.manual_chip_analysis)
        self.analyze_btn.pack(side='left', padx=5)
        
        # 实时数据显示
        data_frame = ttk.LabelFrame(self.parent, text="实时数据", padding=10)
        data_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 创建表格
        columns = ('时间', '价格', '涨跌幅', '最高', '最低', '成交量', '筹码集中度', '提醒状态')
        self.tree = ttk.Treeview(data_frame, columns=columns, show='headings', height=10)
        
        col_widths = [100, 80, 80, 80, 80, 100, 100, 120]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(data_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def start_monitoring(self):
        """开始监控"""
        symbol = self.symbol_entry.get()
        if not symbol:
            messagebox.showwarning("警告", "请输入投资标的代码")
            return
            
        try:
            interval = int(self.interval_entry.get())
            history_days = int(self.history_days_entry.get())
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的数字")
            return
            
        self.app.start_monitoring(symbol, interval, history_days)
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
    def stop_monitoring(self):
        """停止监控"""
        self.app.stop_monitoring()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
    def manual_chip_analysis(self):
        """手动分析筹码"""
        symbol = self.symbol_entry.get()
        if not symbol:
            messagebox.showwarning("警告", "请输入投资标的代码")
            return
            
        self.app.manual_chip_analysis(symbol)
        
    def update_display(self, data, chip_analysis, signals):
        """更新显示"""
        chip_concentration = "N/A"
        if chip_analysis:
            chip_concentration = f"{chip_analysis['concentration_90']:.2f}%"
            
        alert_status = "正常"
        if self.app.enable_alert.get():
            if data['change'] >= float(self.app.up_threshold.get()):
                alert_status = "↑上涨提醒"
            elif data['change'] <= float(self.app.down_threshold.get()):
                alert_status = "↓下跌提醒"
            
        self.tree.insert('', 0, values=(
            data['time'],
            data['price'],
            f"{data['change']:+.2f}%",
            data['high'],
            data['low'],
            f"{data['volume']:,.0f}",
            chip_concentration,
            alert_status
        ))
        
        if len(self.tree.get_children()) > 100:
            self.tree.delete(self.tree.get_children()[-1])
            
    def set_stock(self, code, name, market):
        """设置当前股票"""
        self.symbol_entry.delete(0, 'end')
        self.symbol_entry.insert(0, code)
        self.stock_name_entry.delete(0, 'end')
        self.stock_name_entry.insert(0, name)
        self.market_type.set(market)