import os
print("当前工作目录:", os.getcwd())
# main.py
import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
from datetime import datetime

from config import Config
from utils import DataFetcher, ChipAnalyzer, DingDingSender, FileManager
from data_provider import DataProvider   # 使用新的数据提供模块

from tabs.watchlist_tab import WatchlistTab
from tabs.monitor_tab import MonitorTab
from tabs.rule_tab import RuleTab
from tabs.alert_tab import AlertTab
from tabs.chip_tab import ChipTab
from tabs.source_tab import SourceTab
from tabs.dingding_tab import DingDingTab
from tabs.position_tab import PositionTab
from tabs.log_tab import LogTab

class StockMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("智能投资监控系统 v6.0 - WebSocket 实时版")
        self.root.geometry("1200x900")

        # 配置
        self.config = Config()

        # 数据存储
        self.monitoring = False
        self.monitor_thread = None
        self.rules = []
        self.notification_queue = queue.Queue()
        self.historical_data = {}
        self.watchlist = []
        self.watchlist_data = {}      # 存储实时数据
        self.last_alert_time = {}

        # 工具类
        self.data_fetcher = DataFetcher()
        self.chip_analyzer = ChipAnalyzer()
        self.ding_sender = DingDingSender()
        self.file_manager = FileManager()

        # 新的数据提供模块（替代原有的 data_stream）
        self.data_provider = DataProvider(self, ws_url="wss://realtime.alltick.co/ws")

        # 加载保存的数据
        self.load_data()

        # 创建界面
        self.create_widgets()

        # 检查通知队列
        self.check_notification_queue()

        # 如果已有自选股，启动 WebSocket 订阅
        if self.watchlist:
            symbols = [item['code'] for item in self.watchlist]
            self.data_provider.start_realtime(symbols)

    def create_widgets(self):
        """创建主界面"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        self.tabs = {}

        # 自选股监控
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='自选股监控')
        self.tabs['watchlist'] = WatchlistTab(frame, self)

        # 实时监控
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='实时监控')
        self.tabs['monitor'] = MonitorTab(frame, self)

        # 规则设置
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='买卖规则')
        self.tabs['rule'] = RuleTab(frame, self)

        # 涨跌提醒
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='涨跌提醒')
        self.tabs['alert'] = AlertTab(frame, self)

        # 筹码分析
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='筹码分析')
        self.tabs['chip'] = ChipTab(frame, self)

        # 数据源设置
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='数据源设置')
        self.tabs['source'] = SourceTab(frame, self)

        # 钉钉设置
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='钉钉设置')
        self.tabs['dingding'] = DingDingTab(frame, self)

        # 持仓设置
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='持仓设置')
        self.tabs['position'] = PositionTab(frame, self)

        # 日志
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='监控日志')
        self.tabs['log'] = LogTab(frame, self)

    def load_data(self):
        """加载所有数据"""
        # 加载规则
        self.rules = self.file_manager.load_json(
            self.config.RULES_FILE,
            self.config.DEFAULT_RULES
        )

        # 加载自选股
        self.watchlist = self.file_manager.load_json(
            self.config.WATCHLIST_FILE,
            self.config.DEFAULT_WATCHLIST
        )

    def save_rules(self):
        """保存规则"""
        self.file_manager.save_json(self.config.RULES_FILE, self.rules)

    def save_watchlist(self):
        """保存自选股，并更新 WebSocket 订阅"""
        self.file_manager.save_json(self.config.WATCHLIST_FILE, self.watchlist)
        symbols = [item['code'] for item in self.watchlist]
        self.data_provider.update_realtime_subscription(symbols)

    def save_position(self, position_data):
        """保存持仓"""
        self.file_manager.save_json(self.config.POSITION_FILE, position_data)

    def load_position(self):
        """加载持仓"""
        return self.file_manager.load_json(self.config.POSITION_FILE, {})

    def get_stock_data(self, symbol, market):
        """保留原 HTTP 获取方法作为备选，但主要依赖 WebSocket"""
        return self.data_fetcher.get_stock_data(symbol, market)

    def get_stock_name_cached(self, code, market):
        """带缓存的股票名称获取（由 DataFetcher 提供）"""
        return self.data_fetcher.get_stock_name_cached(code, market)

    def get_historical_data(self, symbol, market, days):
        """获取历史数据，优先使用 Tushare，失败则回退到原有 DataFetcher"""
        # 优先尝试新的数据提供模块（Tushare）
        df = self.data_provider.get_historical_data(symbol, market, days)
        if df is not None and not df.empty:
            return df
        # 备选：原有方式
        return self.data_fetcher.get_historical_data_cached(symbol, market, days)

    def analyze_chip(self, historical_data):
        """分析筹码"""
        return self.chip_analyzer.analyze(historical_data)

    def send_dingding(self, message):
        """发送钉钉消息"""
        webhook = self.tabs['dingding'].webhook_entry.get() if hasattr(self.tabs['dingding'], 'webhook_entry') else ""
        phones = self.tabs['dingding'].phone_entry.get() if hasattr(self.tabs['dingding'], 'phone_entry') else ""

        if webhook:
            success = self.ding_sender.send_message(webhook, message, phones)
            if success:
                self.log("钉钉消息发送成功")
            else:
                self.log("钉钉消息发送失败")

    def start_monitoring(self, symbol, interval, history_days):
        """开始监控（与原有逻辑保持一致）"""
        self.monitoring = True
        market = self.tabs['monitor'].market_type.get()

        # 获取历史数据
        hist_data = self.get_historical_data(symbol, market, history_days)
        if hist_data is not None:
            self.historical_data[symbol] = hist_data

        # 启动监控线程
        self.monitor_thread = threading.Thread(
            target=self.monitor_loop,
            args=(symbol, market, interval)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.log(f"开始监控 {symbol}")

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        self.log("停止监控")

    def monitor_loop(self, symbol, market, interval):
        """监控循环"""
        while self.monitoring:
            try:
                # 优先从 WebSocket 获取最新数据，如果不可用则用 HTTP
                if symbol in self.watchlist_data:
                    data = self.watchlist_data[symbol]
                else:
                    data = self.get_stock_data(symbol, market)

                if data:
                    # 更新持仓显示
                    if 'position' in self.tabs:
                        self.root.after(0, self.tabs['position'].update_display, data['price'])

                    # 检查涨跌幅提醒
                    if hasattr(self.tabs['alert'], 'enable_alert') and self.tabs['alert'].enable_alert.get():
                        self.check_price_alert(symbol, data)

                    # 筹码分析
                    chip_analysis = None
                    if symbol in self.historical_data:
                        chip_analysis = self.analyze_chip(self.historical_data[symbol])

                    # 检查规则
                    signals = self.check_rules(data, chip_analysis)

                    # 更新显示
                    self.root.after(0, self.tabs['monitor'].update_display, data, chip_analysis, signals)

                    # 更新筹码分析显示
                    if chip_analysis and 'chip' in self.tabs:
                        self.root.after(0, self.tabs['chip'].update_display, chip_analysis)

                    # 发送通知
                    if signals:
                        for signal in signals:
                            self.send_notification(signal, data, chip_analysis)

                time.sleep(interval)

            except Exception as e:
                self.log(f"监控错误: {str(e)}")

    def check_price_alert(self, symbol, data):
        """检查涨跌幅提醒（与原有逻辑一致）"""
        try:
            up_threshold = float(self.tabs['alert'].up_threshold.get())
            down_threshold = float(self.tabs['alert'].down_threshold.get())
            alert_interval = int(self.tabs['alert'].alert_interval.get()) * 60

            current_time = time.time()
            last_alert = self.last_alert_time.get(symbol, 0)

            if current_time - last_alert < alert_interval:
                return

            need_alert = False
            alert_type = ""

            if data['change'] >= up_threshold:
                need_alert = True
                alert_type = "上涨报警"
            elif data['change'] <= down_threshold:
                need_alert = True
                alert_type = "下跌报警"

            if need_alert:
                self.last_alert_time[symbol] = current_time
                self.send_price_alert(symbol, data, alert_type)

        except ValueError as e:
            self.log(f"涨跌幅提醒参数错误: {str(e)}")

    def send_price_alert(self, symbol, data, alert_type):
        """发送涨跌幅提醒（与原有逻辑一致）"""
        stock_name = self.tabs['monitor'].stock_name_entry.get()
        if not stock_name:
            stock_name = symbol

        market = self.tabs['monitor'].market_type.get()
        if market == 'A股':
            if symbol.startswith('6'):
                stock_code = f"sh{symbol}"
            else:
                stock_code = f"sz{symbol}"
        else:
            stock_code = symbol

        try:
            cost_price = float(self.tabs['position'].cost_price.get())
            quantity = int(self.tabs['position'].position_quantity.get())

            if cost_price > 0:
                cost_change = ((data['price'] - cost_price) / cost_price) * 100
                cost_profit = (data['price'] - cost_price) * quantity
            else:
                cost_change = 0
                cost_profit = 0
        except ValueError:
            cost_price = 0
            quantity = 0
            cost_change = 0
            cost_profit = 0

        message = f"""go-stock [{alert_type}]
{stock_name}({stock_code})
•  当前价格: {data['price']:.2f}  {data['change']:+.2f}%
•  最高价: {data['high']:.2f}  {((data['high'] - data['prev_close']) / data['prev_close'] * 100):+.2f}%
•  最低价: {data['low']:.2f}  {((data['low'] - data['prev_close']) / data['prev_close'] * 100):+.2f}%
•  昨收价: {data['prev_close']:.2f}
•  今开价: {data['open']:.2f}
•  成本价: {cost_price:.2f}  {cost_change:+.2f}%  {cost_profit:+.2f} ¥
•  成本数量: {quantity}股
•  日期: {data['datetime']}"""

        self.log(f"涨跌幅提醒触发: {alert_type} - 涨跌幅 {data['change']:+.2f}%")
        self.send_dingding(message)

    def check_rules(self, data, chip_analysis):
        """检查规则（与原有逻辑一致）"""
        signals = []

        for rule in self.rules:
            if not rule.get('enabled', True):
                continue

            try:
                triggered = False

                if rule['type'] == '筹码集中度' and chip_analysis:
                    concentration = chip_analysis['concentration_90']

                    if rule['condition'] == '买入条件':
                        if concentration <= rule['price_range']:
                            triggered = True
                            self.log(f"买入条件触发: 集中度 {concentration:.2f}% <= {rule['price_range']}%")

                    elif rule['condition'] == '卖出条件':
                        if concentration >= rule['price_range']:
                            triggered = True
                            self.log(f"卖出条件触发: 集中度 {concentration:.2f}% >= {rule['price_range']}%")

                if triggered:
                    signals.append({
                        'rule': rule,
                        'data': data,
                        'chip_analysis': chip_analysis,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

            except Exception as e:
                self.log(f"规则检查错误: {str(e)}")
                continue

        return signals

    def send_notification(self, signal, data, chip_analysis):
        """发送通知（与原有逻辑一致）"""
        rule = signal['rule']

        message = f"【{rule['action']}】\n"
        message += f"标的: {data['symbol']}\n"
        message += f"时间: {signal['time']}\n"
        message += f"价格: {data['price']}\n"

        if chip_analysis:
            message += f"90%筹码集中度: {chip_analysis['concentration_90']:.2f}%\n"

        message += f"触发规则: {rule['type']} - {rule['condition']}\n"

        if rule['type'] == '筹码集中度':
            message += f"参数: {rule['chip_percent']}%筹码在{rule['price_range']}%价格区间内\n"

        message += f"备注: {rule['remark']}"

        self.log(f"触发信号: {message}")
        self.send_dingding(message)

    def manual_chip_analysis(self, symbol):
        """手动进行筹码分析（与原有逻辑一致）"""
        market = self.tabs['monitor'].market_type.get()
        days = int(self.tabs['monitor'].history_days_entry.get())

        self.log(f"开始手动分析 {symbol}，使用{days}天历史数据")

        hist_data = self.get_historical_data(symbol, market, days)

        if hist_data is not None and not hist_data.empty:
            self.historical_data[symbol] = hist_data
            chip_analysis = self.analyze_chip(hist_data)

            if chip_analysis:
                self.tabs['chip'].update_display(chip_analysis)
                self.log("手动筹码分析完成")
            else:
                self.log("筹码分析失败")
        else:
            self.log("获取历史数据失败")

    def set_current_stock(self, code, name, market):
        """设置当前监控股票"""
        if 'monitor' in self.tabs:
            self.tabs['monitor'].set_stock(code, name, market)

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        self.notification_queue.put(log_message)

    def check_notification_queue(self):
        """检查通知队列"""
        try:
            while True:
                message = self.notification_queue.get_nowait()
                if 'log' in self.tabs:
                    self.tabs['log'].add_log(message)
        except queue.Empty:
            pass

        self.root.after(100, self.check_notification_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockMonitorApp(root)
    root.mainloop()