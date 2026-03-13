# data_provider.py
"""
增强版数据提供模块
- 实时行情：WebSocket 连接（支持自动重连、订阅管理）
- 历史数据：Tushare API（优先使用，稳定可靠）
"""

import websocket
import threading
import time
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== Tushare API 配置 ====================
TUSHARE_API_URL = "http://api.tushare.pro"
TUSHARE_TOKEN = "你的Tushare token"  # 请替换为真实的 token

class TushareApi:
    """Tushare 历史数据接口（返回 pandas DataFrame）"""
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()

    def _format_ts_code(self, code: str) -> str:
        """将 600000 格式化为 600000.SH / 000001.SZ"""
        if '.' in code:
            return code
        if code.startswith(('6', '9')):
            return f"{code}.SH"
        elif code.startswith(('0', '3', '1')):
            return f"{code}.SZ"
        else:
            return code  # 未知市场，原样返回

    def get_daily(self, code: str, start_date: str, end_date: str, timeout: int = 10) -> Optional[pd.DataFrame]:
        """
        获取A股日线数据
        :param code: 股票代码（如 600000 或 600000.SH）
        :param start_date: 开始日期 YYYYMMDD
        :param end_date: 结束日期 YYYYMMDD
        :param timeout: 超时时间（秒）
        :return: DataFrame 包含字段：trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount
        """
        fields = "ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount"
        ts_code = self._format_ts_code(code)

        request_data = {
            "api_name": "daily",
            "token": self.token,
            "params": {
                "ts_code": ts_code,
                "start_date": start_date,
                "end_date": end_date
            },
            "fields": fields
        }

        try:
            response = self.session.post(
                url=TUSHARE_API_URL,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 0 and "data" in result:
                data = result["data"]
                df = pd.DataFrame(data["items"], columns=data["fields"])
                # 转换日期列
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df.sort_values('trade_date', inplace=True)
                # 重命名列以匹配系统原有命名（可选）
                df.rename(columns={
                    'trade_date': 'date',
                    'pct_chg': 'change_percent'
                }, inplace=True)
                return df
            else:
                logger.error(f"Tushare API 错误: {result.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"Tushare 请求异常: {e}")
            return None


# ==================== WebSocket 实时行情 ====================
class FinancialWebSocketClient:
    """WebSocket 实时行情客户端（支持自动重连、订阅管理）"""
    def __init__(self, ws_url: str, app=None):
        self.ws_url = ws_url
        self.app = app  # 持有主程序引用，用于回调更新 UI
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_running = False
        self.connected = False
        self.subscribed_symbols: List[str] = []
        self.reconnect_delay = 5  # 重连延迟（秒）

    def _log(self, msg: str):
        """统一日志输出，可转发到主界面"""
        logger.info(f"[WebSocket] {msg}")
        if self.app:
            self.app.log(f"[WebSocket] {msg}")

    def on_open(self, ws):
        self.connected = True
        self._log("连接已建立")
        # 连接成功后自动订阅当前列表
        if self.subscribed_symbols:
            self._send_subscribe(self.subscribed_symbols)

    def on_message(self, ws, message):
        """处理接收到的实时行情消息"""
        try:
            data = json.loads(message)
            # 根据实际数据格式解析，此处为示例（AllTick 格式：{"s":"sh600000","p":10.5,"t":1623456789}）
            symbol = data.get("s")
            price = data.get("p")
            timestamp = data.get("t")

            if symbol and price is not None:
                # 构造与系统兼容的数据字典
                quote = {
                    'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'price': round(price, 2),
                    'symbol': symbol
                }
                # 更新到 app 的实时数据字典（需 app 有 watchlist_data 属性）
                if self.app:
                    if symbol in self.app.watchlist_data:
                        self.app.watchlist_data[symbol].update(quote)
                    else:
                        self.app.watchlist_data[symbol] = quote
                    # 触发 UI 更新
                    self.app.root.after(0, self._update_ui, symbol)
        except Exception as e:
            self._log(f"解析消息异常: {e}")

    def on_error(self, ws, error):
        self.connected = False
        self._log(f"错误: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        self._log(f"连接关闭 (状态码: {close_status_code}, 消息: {close_msg})")
        # 自动重连由 run_forever 循环外的重连逻辑处理

    def _update_ui(self, symbol):
        """通知 UI 刷新"""
        if self.app and 'watchlist' in self.app.tabs:
            self.app.tabs['watchlist'].update_data_display()
        # 可扩展：如果监控界面的股票匹配，也刷新

    def _send_subscribe(self, symbols: List[str]):
        """发送订阅消息（格式需根据具体 API 调整）"""
        if not self.ws or not self.connected:
            return
        # 示例订阅格式（AllTick）
        subscribe_msg = {
            "type": "subscribe",
            "symbols": symbols
        }
        try:
            self.ws.send(json.dumps(subscribe_msg))
            self._log(f"订阅已发送: {symbols}")
        except Exception as e:
            self._log(f"订阅发送失败: {e}")

    def _send_unsubscribe(self, symbols: List[str]):
        """发送取消订阅消息"""
        if not self.ws or not self.connected:
            return
        unsubscribe_msg = {
            "type": "unsubscribe",
            "symbols": symbols
        }
        try:
            self.ws.send(json.dumps(unsubscribe_msg))
        except Exception as e:
            self._log(f"取消订阅发送失败: {e}")

    def run(self):
        """启动 WebSocket 客户端（非阻塞，内部线程运行）"""
        self.is_running = True
        threading.Thread(target=self._run_forever, daemon=True).start()

    def _run_forever(self):
        """运行循环，处理自动重连"""
        while self.is_running:
            try:
                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                self.ws.run_forever()
            except Exception as e:
                self._log(f"run_forever 异常: {e}")
            finally:
                self.connected = False
            if self.is_running:
                self._log(f"尝试 {self.reconnect_delay} 秒后重连...")
                time.sleep(self.reconnect_delay)

    def update_subscription(self, new_symbols: List[str]):
        """更新订阅列表（自动处理取消旧订阅、订阅新列表）"""
        # 如果连接未建立，只保存列表，待连接成功后再订阅
        self.subscribed_symbols = new_symbols
        if self.connected:
            # 简单实现：先取消所有再订阅（若 API 支持全量替换可优化）
            self._send_unsubscribe(self.subscribed_symbols)  # 实际可能需要更精细的 diff
            self._send_subscribe(self.subscribed_symbols)

    def stop(self):
        """停止客户端"""
        self.is_running = False
        if self.ws:
            self.ws.close()
        self._log("已停止")


# ==================== 统一数据提供类 ====================
class DataProvider:
    """整合实时行情与历史数据，为监控系统提供统一接口"""
    def __init__(self, app, ws_url: str = "wss://realtime.alltick.co/ws"):
        self.app = app
        self.ws_client = FinancialWebSocketClient(ws_url, app)
        self.tushare = TushareApi(token=TUSHARE_TOKEN)

    def start_realtime(self, symbols: List[str]):
        """启动实时行情流并订阅股票列表"""
        self.ws_client.subscribed_symbols = symbols
        self.ws_client.run()

    def update_realtime_subscription(self, symbols: List[str]):
        """更新实时行情订阅（例如自选股变更时调用）"""
        self.ws_client.update_subscription(symbols)

    def get_historical_data(self, symbol: str, market: str, days: int) -> Optional[pd.DataFrame]:
        """
        获取历史日线数据
        :param symbol: 股票代码（如 600000）
        :param market: 市场（'A股' 或其他，目前仅支持 A股）
        :param days: 需要的历史天数
        :return: DataFrame 或 None
        """
        if market != 'A股':
            logger.warning(f"暂不支持 {market} 的历史数据")
            return None

        end = datetime.now()
        start = end - timedelta(days=days)
        start_str = start.strftime('%Y%m%d')
        end_str = end.strftime('%Y%m%d')

        # 尝试 Tushare
        df = self.tushare.get_daily(symbol, start_str, end_str)
        if df is not None and not df.empty:
            logger.info(f"Tushare 获取 {symbol} 历史数据成功，共 {len(df)} 条")
            return df

        # Tushare 失败，返回 None
        logger.warning(f"Tushare 获取 {symbol} 历史数据失败，请检查 token 或网络")
        return None

    def stop(self):
        """停止所有数据服务"""
        self.ws_client.stop()