# app_mixin_alert.py
import time
from datetime import datetime

class AppMixinAlert:
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