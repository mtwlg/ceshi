# tabs/watchlist_tab.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime

class WatchlistTab:
    """自选股监控标签页 - 完善版"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_selected_code = None
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面"""
        # ========== 顶部控制区域 ==========
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # 添加自选股区域
        add_frame = ttk.LabelFrame(control_frame, text="添加自选股", padding=10)
        add_frame.pack(fill='x', pady=5)
        
        ttk.Label(add_frame, text="股票代码:").grid(row=0, column=0, padx=5)
        self.watchlist_code = ttk.Entry(add_frame, width=15)
        self.watchlist_code.grid(row=0, column=1, padx=5)
        self.watchlist_code.bind('<KeyRelease>', self.on_code_input)  # 输入时自动识别
        
        ttk.Label(add_frame, text="股票名称:").grid(row=0, column=2, padx=5)
        self.watchlist_name = ttk.Entry(add_frame, width=15)
        self.watchlist_name.grid(row=0, column=3, padx=5)
        
        ttk.Label(add_frame, text="市场:").grid(row=0, column=4, padx=5)
        self.watchlist_market = ttk.Combobox(add_frame, values=['A股', '港股', '美股'], width=8)
        self.watchlist_market.set('A股')
        self.watchlist_market.grid(row=0, column=5, padx=5)
        
        # 当前价格显示
        ttk.Label(add_frame, text="当前价:").grid(row=0, column=6, padx=5)
        self.current_price_label = ttk.Label(add_frame, text="--", font=('Arial', 10, 'bold'))
        self.current_price_label.grid(row=0, column=7, padx=5)
        
        ttk.Button(add_frame, text="添加自选", command=self.add_to_watchlist).grid(row=0, column=8, padx=10)
        
        # ========== 主要内容区域 ==========
        main_content = ttk.Frame(self.parent)
        main_content.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 创建左右两个区域
        left_frame = ttk.Frame(main_content)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        right_frame = ttk.Frame(main_content)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # ========== 左侧：自选股列表 ==========
        list_label_frame = ttk.LabelFrame(left_frame, text="自选股列表", padding=5)
        list_label_frame.pack(fill='both', expand=True)
        
        # 自选股列表树形视图
        columns = ('代码', '名称', '市场', '最新价', '涨跌幅', '状态')
        self.watchlist_tree = ttk.Treeview(list_label_frame, columns=columns, show='headings', height=15)
        
        col_widths = [100, 120, 80, 100, 100, 80]
        col_texts = ['代码', '名称', '市场', '最新价', '涨跌幅', '状态']
        for col, width, text in zip(columns, col_widths, col_texts):
            self.watchlist_tree.heading(col, text=text)
            self.watchlist_tree.column(col, width=width)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_label_frame, orient='vertical', command=self.watchlist_tree.yview)
        self.watchlist_tree.configure(yscrollcommand=scrollbar.set)
        
        self.watchlist_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.watchlist_tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # 设置颜色标签
        self.watchlist_tree.tag_configure('up', foreground='red')
        self.watchlist_tree.tag_configure('down', foreground='green')
        self.watchlist_tree.tag_configure('normal', foreground='black')
        
        # 操作按钮
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="删除选中", command=self.delete_from_watchlist).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="刷新数据", command=self.refresh_data).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="设为当前监控", command=self.set_as_current).pack(side='left', padx=5)
        
        # ========== 右侧：实时数据详情 ==========
        # 模仿图片中的样式
        detail_frame = ttk.LabelFrame(right_frame, text="股票实时数据", padding=10)
        detail_frame.pack(fill='both', expand=True)
        
        # 创建上下两个区域
        top_detail = ttk.Frame(detail_frame)
        top_detail.pack(fill='x', pady=5)
        
        bottom_detail = ttk.Frame(detail_frame)
        bottom_detail.pack(fill='both', expand=True, pady=5)
        
        # 顶部：股票基本信息
        info_frame = ttk.Frame(top_detail)
        info_frame.pack(fill='x')
        
        # 左侧：股票名称和代码
        self.stock_name_label = ttk.Label(info_frame, text="--", font=('Arial', 16, 'bold'))
        self.stock_name_label.pack(side='left', padx=5)
        
        self.stock_code_label = ttk.Label(info_frame, text="", font=('Arial', 10))
        self.stock_code_label.pack(side='left', padx=5)
        
        # 右侧：更新时间
        self.update_time_label = ttk.Label(info_frame, text="", font=('Arial', 9))
        self.update_time_label.pack(side='right', padx=5)
        
        # 价格信息区域 - 模仿图片样式
        price_frame = ttk.Frame(top_detail)
        price_frame.pack(fill='x', pady=10)
        
        # 当前价格
        current_price_frame = ttk.Frame(price_frame)
        current_price_frame.pack(side='left', padx=20)
        
        ttk.Label(current_price_frame, text="当前价格", font=('Arial', 9)).pack()
        self.current_price_value = ttk.Label(current_price_frame, text="--", font=('Arial', 20, 'bold'))
        self.current_price_value.pack()
        self.current_price_change = ttk.Label(current_price_frame, text="--", font=('Arial', 10))
        self.current_price_change.pack()
        
        # 最高价
        high_frame = ttk.Frame(price_frame)
        high_frame.pack(side='left', padx=20)
        
        ttk.Label(high_frame, text="最高", font=('Arial', 9)).pack()
        self.high_value = ttk.Label(high_frame, text="--", font=('Arial', 14, 'bold'))
        self.high_value.pack()
        self.high_change = ttk.Label(high_frame, text="--", font=('Arial', 9))
        self.high_change.pack()
        
        # 最低价
        low_frame = ttk.Frame(price_frame)
        low_frame.pack(side='left', padx=20)
        
        ttk.Label(low_frame, text="最低", font=('Arial', 9)).pack()
        self.low_value = ttk.Label(low_frame, text="--", font=('Arial', 14, 'bold'))
        self.low_value.pack()
        self.low_change = ttk.Label(low_frame, text="--", font=('Arial', 9))
        self.low_change.pack()
        
        # 分隔线
        ttk.Separator(top_detail, orient='horizontal').pack(fill='x', pady=10)
        
        # 详细信息区域 - 模仿图片中的盘口、昨收、今开等
        detail_info_frame = ttk.Frame(top_detail)
        detail_info_frame.pack(fill='x')
        
        # 左侧详细信息
        left_info = ttk.Frame(detail_info_frame)
        left_info.pack(side='left', padx=20)
        
        info_items = [
            ('昨收价', 'prev_close'),
            ('今开价', 'open'),
            ('成交量', 'volume'),
            ('成交额', 'amount')
        ]
        
        self.info_labels = {}
        for i, (label, key) in enumerate(info_items):
            frame = ttk.Frame(left_info)
            frame.pack(fill='x', pady=2)
            ttk.Label(frame, text=f"{label}:", width=8).pack(side='left')
            self.info_labels[key] = ttk.Label(frame, text="--", font=('Arial', 10, 'bold'))
            self.info_labels[key].pack(side='left', padx=5)
        
        # 右侧盘口信息（买一/卖一）
        right_info = ttk.Frame(detail_info_frame)
        right_info.pack(side='right', padx=20)
        
        # 卖一
        sell_frame = ttk.Frame(right_info)
        sell_frame.pack(fill='x', pady=2)
        ttk.Label(sell_frame, text="卖一:", width=5).pack(side='left')
        self.sell_price = ttk.Label(sell_frame, text="--", font=('Arial', 10, 'bold'), foreground='green')
        self.sell_price.pack(side='left', padx=2)
        self.sell_volume = ttk.Label(sell_frame, text="", font=('Arial', 9))
        self.sell_volume.pack(side='left')
        
        # 买一
        buy_frame = ttk.Frame(right_info)
        buy_frame.pack(fill='x', pady=2)
        ttk.Label(buy_frame, text="买一:", width=5).pack(side='left')
        self.buy_price = ttk.Label(buy_frame, text="--", font=('Arial', 10, 'bold'), foreground='red')
        self.buy_price.pack(side='left', padx=2)
        self.buy_volume = ttk.Label(buy_frame, text="", font=('Arial', 9))
        self.buy_volume.pack(side='left')
        
        # 分隔线
        ttk.Separator(top_detail, orient='horizontal').pack(fill='x', pady=10)
        
        # 底部：功能按钮区域 - 模仿图片中的成本、分时、资金、详情、公告、研报等
        button_frame = ttk.Frame(bottom_detail)
        button_frame.pack(fill='x', pady=5)
        
        buttons = ['成本', '分时', '资金', '详情', '公告', '研报', '设置分组']
        for btn_text in buttons:
            btn = ttk.Button(button_frame, text=btn_text, command=lambda t=btn_text: self.on_detail_button(t))
            btn.pack(side='left', padx=2)
        
        # 初始化显示
        self.refresh_list()
        
    def on_code_input(self, event):
        """输入股票代码时自动识别"""
        code = self.watchlist_code.get().strip()
        market = self.watchlist_market.get()
        
        if len(code) >= 5:  # 输入足够长度时尝试识别
            # 尝试获取股票名称
            name = self.app.get_stock_name(code, market)
            if name and name != code:
                self.watchlist_name.delete(0, 'end')
                self.watchlist_name.insert(0, name)
            
            # 尝试获取实时价格
            data = self.app.get_stock_data(code, market)
            if data:
                self.current_price_label.config(
                    text=f"{data['price']:.2f} {data['change']:+.2f}%",
                    foreground='red' if data['change'] > 0 else 'green' if data['change'] < 0 else 'black'
                )
            else:
                self.current_price_label.config(text="--")
                
    def add_to_watchlist(self):
        """添加股票到自选股"""
        code = self.watchlist_code.get().strip()
        name = self.watchlist_name.get().strip()
        market = self.watchlist_market.get()
        
        if not code:
            messagebox.showwarning("警告", "请输入股票代码")
            return
            
        if not name:
            name = self.app.get_stock_name(code, market)
            if not name:
                name = code
            
        # 检查是否已存在
        for item in self.app.watchlist:
            if item['code'] == code:
                messagebox.showinfo("提示", "该股票已在自选股中")
                return
                
        # 添加到自选股列表
        stock_item = {
            'code': code,
            'name': name,
            'market': market,
            'added_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.app.watchlist.append(stock_item)
        self.app.save_watchlist()
        self.refresh_list()
        
        # 清空输入
        self.watchlist_code.delete(0, 'end')
        self.watchlist_name.delete(0, 'end')
        self.current_price_label.config(text="--")
        
        self.app.log(f"添加自选股: {name}({code})")
        
        # 立即获取一次数据
        self.app.update_all_watchlist_data()
        
    def delete_from_watchlist(self):
        """从自选股删除"""
        selected = self.watchlist_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的股票")
            return
            
        item = self.watchlist_tree.item(selected[0])
        values = item['values']
        
        if messagebox.askyesno("确认删除", f"确定要将 {values[1]}({values[0]}) 从自选股删除吗？"):
            for i, stock in enumerate(self.app.watchlist):
                if stock['code'] == values[0]:
                    del self.app.watchlist[i]
                    break
                    
            self.app.save_watchlist()
            self.refresh_list()
            self.clear_detail_display()
            self.app.log(f"删除自选股: {values[1]}({values[0]})")
            
    def on_select(self, event):
        """自选股选择事件"""
        selected = self.watchlist_tree.selection()
        if not selected:
            return
            
        item = self.watchlist_tree.item(selected[0])
        values = item['values']
        code = values[0]
        self.current_selected_code = code
        
        if code in self.app.watchlist_data:
            self.display_detail(code, self.app.watchlist_data[code])
        else:
            # 尝试获取实时数据
            market = values[2]
            data = self.app.get_stock_data(code, market)
            if data:
                self.app.watchlist_data[code] = data
                self.display_detail(code, data)
            
    def set_as_current(self):
        """设为当前监控股票"""
        selected = self.watchlist_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要监控的股票")
            return
            
        item = self.watchlist_tree.item(selected[0])
        values = item['values']
        
        self.app.set_current_stock(values[0], values[1], values[2])
        self.app.notebook.select(1)  # 切换到监控选项卡
        
        self.app.log(f"设置当前监控: {values[1]}({values[0]})")
        
    def refresh_list(self):
        """刷新自选股列表显示"""
        for item in self.watchlist_tree.get_children():
            self.watchlist_tree.delete(item)
            
        for stock in self.app.watchlist:
            code = stock['code']
            price_display = "--"
            change_display = "--"
            tag = 'normal'
            
            if code in self.app.watchlist_data:
                data = self.app.watchlist_data[code]
                price_display = f"{data['price']:.2f}"
                change_display = f"{data['change']:+.2f}%"
                
                if data['change'] > 0:
                    tag = 'up'
                elif data['change'] < 0:
                    tag = 'down'
                    
            status = "正常"
            if code in self.app.watchlist_data and abs(self.app.watchlist_data[code]['change']) > 5:
                status = "异动"
                
            self.watchlist_tree.insert('', 'end', values=(
                code,
                stock['name'],
                stock['market'],
                price_display,
                change_display,
                status
            ), tags=(tag,))
            
    def refresh_data(self):
        """刷新所有自选股数据"""
        self.app.log("开始刷新自选股数据...")
        thread = threading.Thread(target=self.app.update_all_watchlist_data)
        thread.daemon = True
        thread.start()
        
    def update_data_display(self):
        """更新自选股数据表格"""
        self.refresh_list()
        
        # 如果当前有选中的股票，更新详情显示
        if self.current_selected_code and self.current_selected_code in self.app.watchlist_data:
            self.display_detail(self.current_selected_code, self.app.watchlist_data[self.current_selected_code])
            
    def display_detail(self, code, data):
        """显示股票详细数据 - 模仿图片样式"""
        if not data:
            return
            
        # 查找股票名称
        name = code
        for stock in self.app.watchlist:
            if stock['code'] == code:
                name = stock['name']
                break
                
        # 更新基本信息
        self.stock_name_label.config(text=name)
        self.stock_code_label.config(text=f"({code})")
        self.update_time_label.config(text=data['datetime'])
        
        # 更新价格信息
        self.current_price_value.config(
            text=f"{data['price']:.2f}",
            foreground='red' if data['change'] > 0 else 'green' if data['change'] < 0 else 'black'
        )
        self.current_price_change.config(
            text=f"{data['change']:+.2f}%",
            foreground='red' if data['change'] > 0 else 'green' if data['change'] < 0 else 'black'
        )
        
        # 最高价
        high_change = ((data['high'] - data['prev_close']) / data['prev_close']) * 100
        self.high_value.config(text=f"{data['high']:.2f}")
        self.high_change.config(
            text=f"{high_change:+.2f}%",
            foreground='red' if high_change > 0 else 'green' if high_change < 0 else 'black'
        )
        
        # 最低价
        low_change = ((data['low'] - data['prev_close']) / data['prev_close']) * 100
        self.low_value.config(text=f"{data['low']:.2f}")
        self.low_change.config(
            text=f"{low_change:+.2f}%",
            foreground='red' if low_change > 0 else 'green' if low_change < 0 else 'black'
        )
        
        # 详细信息
        self.info_labels['prev_close'].config(text=f"{data['prev_close']:.2f}")
        self.info_labels['open'].config(text=f"{data['open']:.2f}")
        self.info_labels['volume'].config(text=f"{data['volume']/10000:.2f}万")
        
        # 模拟盘口数据（实际可以从更深的数据获取）
        # 这里简单用当前价格加减几分钱模拟
        self.sell_price.config(text=f"{data['price']+0.01:.2f}")
        self.sell_volume.config(text="(58)")
        self.buy_price.config(text=f"{data['price']-0.01:.2f}")
        self.buy_volume.config(text="(227)")
        
        # 模拟成交额
        amount = data['price'] * data['volume'] / 100000000  # 亿元
        self.info_labels['amount'].config(text=f"{amount:.2f}亿")
        
    def clear_detail_display(self):
        """清空详情显示"""
        self.stock_name_label.config(text="--")
        self.stock_code_label.config(text="")
        self.update_time_label.config(text="")
        
        self.current_price_value.config(text="--")
        self.current_price_change.config(text="--")
        self.high_value.config(text="--")
        self.high_change.config(text="--")
        self.low_value.config(text="--")
        self.low_change.config(text="--")
        
        for key in self.info_labels:
            self.info_labels[key].config(text="--")
            
        self.sell_price.config(text="--")
        self.sell_volume.config(text="")
        self.buy_price.config(text="--")
        self.buy_volume.config(text="")
        
    def on_detail_button(self, button_text):
        """处理详情按钮点击"""
        if not self.current_selected_code:
            messagebox.showinfo("提示", "请先选择股票")
            return
            
        self.app.log(f"点击 {button_text} 按钮 - 股票: {self.current_selected_code}")
        
        # 获取当前选中的股票信息
        stock_info = None
        for stock in self.app.watchlist:
            if stock['code'] == self.current_selected_code:
                stock_info = stock
                break
                
        if not stock_info:
            return
            
        # 打开对应的功能窗口
        if button_text == '成本':
            self.app.notebook.select(7)  # 持仓设置
            
        elif button_text == '分时':
            self.open_timeshare_window(stock_info)
            
        elif button_text == '资金':
            self.open_capital_window(stock_info)
            
        elif button_text == '详情':
            self.open_details_window(stock_info)
            
        elif button_text == '公告':
            self.open_announcements_window(stock_info)
            
        elif button_text == '研报':
            self.open_research_window(stock_info)
            
        elif button_text == '设置分组':
            messagebox.showinfo("提示", f"分组设置功能开发中...")
            
    def open_timeshare_window(self, stock_info):
        """打开分时图窗口"""
        try:
            from modules.timeshare import TimeShareModule
            
            window = tk.Toplevel(self.app.root)
            window.title(f"{stock_info['name']}({stock_info['code']}) - 分时图")
            window.geometry("900x700")
            
            module = TimeShareModule(window, self.app)
            module.load_data(stock_info['code'], stock_info['name'])
        except Exception as e:
            messagebox.showerror("错误", f"打开分时图窗口失败: {str(e)}")
            self.app.log(f"打开分时图窗口失败: {str(e)}")
        
    def open_capital_window(self, stock_info):
        """打开资金流向窗口"""
        try:
            from modules.capital import CapitalModule
            
            window = tk.Toplevel(self.app.root)
            window.title(f"{stock_info['name']}({stock_info['code']}) - 资金流向")
            window.geometry("1000x700")
            
            module = CapitalModule(window, self.app)
            module.load_data(stock_info['code'], stock_info['name'])
        except Exception as e:
            messagebox.showerror("错误", f"打开资金流向窗口失败: {str(e)}")
            self.app.log(f"打开资金流向窗口失败: {str(e)}")
        
    def open_details_window(self, stock_info):
        """打开详细信息窗口"""
        try:
            from modules.details import DetailsModule
            
            window = tk.Toplevel(self.app.root)
            window.title(f"{stock_info['name']}({stock_info['code']}) - 详细信息")
            window.geometry("1000x800")
            
            module = DetailsModule(window, self.app)
            module.load_data(stock_info['code'], stock_info['name'])
        except Exception as e:
            messagebox.showerror("错误", f"打开详细信息窗口失败: {str(e)}")
            self.app.log(f"打开详细信息窗口失败: {str(e)}")
        
    def open_announcements_window(self, stock_info):
        """打开公告窗口"""
        try:
            from modules.announcements import AnnouncementsModule
            
            window = tk.Toplevel(self.app.root)
            window.title(f"{stock_info['name']}({stock_info['code']}) - 公司公告")
            window.geometry("1000x800")
            
            module = AnnouncementsModule(window, self.app)
            module.load_data(stock_info['code'], stock_info['name'])
        except Exception as e:
            messagebox.showerror("错误", f"打开公告窗口失败: {str(e)}")
            self.app.log(f"打开公告窗口失败: {str(e)}")
        
    def open_research_window(self, stock_info):
        """打开研报窗口"""
        try:
            from modules.research import ResearchModule
            
            window = tk.Toplevel(self.app.root)
            window.title(f"{stock_info['name']}({stock_info['code']}) - 研究报告")
            window.geometry("1000x800")
            
            module = ResearchModule(window, self.app)
            module.load_data(stock_info['code'], stock_info['name'])
        except Exception as e:
            messagebox.showerror("错误", f"打开研报窗口失败: {str(e)}")
            self.app.log(f"打开研报窗口失败: {str(e)}")