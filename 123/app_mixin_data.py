# app_mixin_data.py
from config import Config

class AppMixinData:
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
        # 更新 WebSocket 订阅列表
        symbols = [item['code'] for item in self.watchlist]
        self.data_stream.update_subscription(symbols)
        
    def save_position(self, position_data):
        """保存持仓"""
        self.file_manager.save_json(self.config.POSITION_FILE, position_data)
        
    def load_position(self):
        """加载持仓"""
        return self.file_manager.load_json(self.config.POSITION_FILE, {})