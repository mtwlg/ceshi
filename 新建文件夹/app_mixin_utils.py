# app_mixin_utils.py
import queue
from datetime import datetime

class AppMixinUtils:
    def get_stock_data(self, symbol, market):
        """保留原 HTTP 获取方法作为备选，但主要依赖 WebSocket"""
        return self.data_fetcher.get_stock_data(symbol, market)

    def get_stock_name_cached(self, code, market):
        """带缓存的股票名称获取（由 DataFetcher 提供）"""
        return self.data_fetcher.get_stock_name_cached(code, market)
        
    def get_historical_data(self, symbol, market, days):
        """获取历史数据"""
        # 优先使用缓存
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