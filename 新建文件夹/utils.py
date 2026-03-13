# utils.py - 完整优化版（含新浪源，缩进已修正）
import threading
import time
import json
import requests
import concurrent.futures
from datetime import datetime, timedelta
from functools import wraps
from requests.adapters import HTTPAdapter
import pandas as pd
import numpy as np
import yfinance as yf
import akshare as ak
from plyer import notification

# ---------- 重试装饰器 ----------
def retry(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** i))
            return None
        return wrapper
    return decorator


class DataFetcher:
    """数据获取工具类 - 终极优化版（并发+缓存+重试+新浪源）"""
    
    _name_cache = {}           # 股票名称缓存
    _history_cache = {}        # 历史数据缓存
    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls._session = requests.Session()
            adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)
            cls._session.mount('http://', adapter)
            cls._session.mount('https://', adapter)
        return cls._session

    # ========== 核心方法：并发获取实时数据 ==========
    @staticmethod
    def get_stock_data(symbol, market='A股'):
        return DataFetcher._get_stock_data_concurrent(symbol, market)

    @staticmethod
    def _get_stock_data_concurrent(symbol, market='A股', timeout=5):
        symbol = str(symbol).strip()
        print(f"[并发] 尝试获取数据: {symbol} ({market})")

        tasks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # 提交三个任务
            tasks.append(executor.submit(DataFetcher._fetch_yahoo, symbol, market, timeout))
            tasks.append(executor.submit(DataFetcher._fetch_akshare, symbol, market, timeout))
            tasks.append(executor.submit(DataFetcher._fetch_sina, symbol, market, timeout))

            # 等待第一个成功的结果
            for future in concurrent.futures.as_completed(tasks, timeout=timeout+2):
                try:
                    result = future.result(timeout=1)  # 单个任务最多等1秒
                    if result:
                        print(f"[并发] 成功从某个源获取数据")
                        return result
                except concurrent.futures.TimeoutError:
                    print("[并发] 单个任务超时")
                except Exception as e:
                    print(f"[并发] 任务错误: {e}")

        print("[并发] 所有源都失败，返回模拟数据")
        return DataFetcher._get_mock_data(symbol)

    # ---------- 数据源1: Yahoo Finance ----------
    @staticmethod
    @retry(max_retries=2, delay=0.5)
    def _fetch_yahoo(symbol, market, timeout):
        market_symbol = DataFetcher.format_symbol(symbol, market)
        print(f"[Yahoo] 尝试: {market_symbol}")
        try:
            stock = yf.Ticker(market_symbol)
            hist = stock.history(period="1d")
            if hist is not None and not hist.empty:
                return DataFetcher._parse_yahoo_data(hist, symbol)
        except Exception as e:
            print(f"[Yahoo] 异常: {e}")
        return None

    @staticmethod
    def _parse_yahoo_data(hist, symbol):
        last_price = hist['Close'].iloc[-1]
        today_high = hist['High'].max()
        today_low = hist['Low'].min()
        today_open = hist['Open'].iloc[0]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else last_price
        change = ((last_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
        volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
        return {
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'price': round(last_price, 2),
            'high': round(today_high, 2),
            'low': round(today_low, 2),
            'open': round(today_open, 2),
            'prev_close': round(prev_close, 2),
            'change': round(change, 2),
            'volume': volume,
            'symbol': symbol
        }

    # ---------- 数据源2: AKShare (东方财富接口) ----------
    @staticmethod
    @retry(max_retries=2, delay=0.5)
    def _fetch_akshare(symbol, market, timeout):
        if market != 'A股':
            return None
        code = DataFetcher._clean_code(symbol)
        print(f"[AKShare] 尝试: {code}")
        try:
            # 使用东方财富接口，更稳定
            df = ak.stock_zh_a_spot_em()
            df['代码'] = df['代码'].astype(str)
            stock_data = df[df['代码'] == code]
            if not stock_data.empty:
                row = stock_data.iloc[0]
                change = float(row['涨跌幅'])
                return {
                    'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'price': float(row['最新价']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'open': float(row['开盘']),
                    'prev_close': float(row['昨收']),
                    'change': change,
                    'volume': float(row['成交量']) * 100,  # 转换为股
                    'symbol': symbol
                }
        except Exception as e:
            print(f"[AKShare] 获取失败: {e}")
        return None

    # ---------- 数据源3: 新浪财经 (国内稳定) ----------
    @staticmethod
    def _fetch_sina(symbol, market, timeout):
        if market != 'A股':
            return None
        code = DataFetcher._clean_code(symbol)
        prefix = 'sh' if code.startswith('6') else 'sz'
        url = f"http://hq.sinajs.cn/list={prefix}{code}"
        print(f"[新浪] 尝试: {url}")
        try:
            resp = requests.get(url, timeout=timeout)
            resp.encoding = 'gbk'
            text = resp.text
            if text.startswith('var hq_str_'):
                # 解析新浪数据
                parts = text.split('="')[1].split(',')
                if len(parts) < 8:
                    return None
                name = parts[0]
                open_price = float(parts[1])
                prev_close = float(parts[2])
                price = float(parts[3])
                high = float(parts[4])
                low = float(parts[5])
                date = parts[6]
                time_str = parts[7]
                volume = int(parts[8]) if len(parts) > 8 else 0  # 成交量（手）
                change = ((price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
                return {
                    'datetime': f"{date} {time_str}",
                    'time': time_str,
                    'price': round(price, 2),
                    'high': round(high, 2),
                    'low': round(low, 2),
                    'open': round(open_price, 2),
                    'prev_close': round(prev_close, 2),
                    'change': round(change, 2),
                    'volume': volume * 100,  # 转换为股
                    'symbol': symbol
                }
        except Exception as e:
            print(f"[新浪] 获取失败: {e}")
        return None

    # ---------- 模拟数据 (保底) ----------
    @staticmethod
    def _get_mock_data(symbol):
        import random
        print(f"[模拟] 为 {symbol} 生成模拟数据")
        seed = sum(ord(c) for c in str(symbol))
        random.seed(seed)
        base_price = random.uniform(10, 100)
        change = random.uniform(-3, 3)
        return {
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'price': round(base_price, 2),
            'high': round(base_price * (1 + random.uniform(0, 0.02)), 2),
            'low': round(base_price * (1 - random.uniform(0, 0.02)), 2),
            'open': round(base_price * (1 + random.uniform(-0.01, 0.01)), 2),
            'prev_close': round(base_price * (1 - change/100), 2),
            'change': round(change, 2),
            'volume': random.randint(100000, 5000000),
            'symbol': symbol
        }

    # ========== 股票名称获取（带缓存） ==========
    @staticmethod
    def get_stock_name_cached(code, market):
        cache_key = f"{code}_{market}"
        if cache_key in DataFetcher._name_cache:
            print(f"[缓存] 命中名称: {cache_key}")
            return DataFetcher._name_cache[cache_key]
        name = DataFetcher.get_stock_name(code, market)
        DataFetcher._name_cache[cache_key] = name
        return name

    @staticmethod
    def get_stock_name(code, market):
        try:
            code = str(code).strip()
            clean_code = DataFetcher._clean_code(code)
            if market == 'A股':
                # 优先从新浪获取名称
                try:
                    prefix = 'sh' if clean_code.startswith('6') else 'sz'
                    url = f"http://hq.sinajs.cn/list={prefix}{clean_code}"
                    resp = requests.get(url, timeout=3)
                    resp.encoding = 'gbk'
                    text = resp.text
                    if text.startswith('var hq_str_'):
                        name = text.split('="')[1].split(',')[0]
                        if name:
                            return name
                except:
                    pass
                # 备用：从AKShare获取
                try:
                    df = ak.stock_zh_a_spot_em()
                    df['代码'] = df['代码'].astype(str)
                    stock_data = df[df['代码'] == clean_code]
                    if not stock_data.empty:
                        return stock_data.iloc[0]['名称']
                except:
                    pass
            return code
        except Exception as e:
            print(f"获取股票名称错误: {str(e)}")
        return code

    # ========== 历史数据获取（带缓存） ==========
    @staticmethod
    def get_historical_data_cached(symbol, market, days):
        cache_key = f"{symbol}_{market}_{days}"
        if cache_key in DataFetcher._history_cache:
            cached_time, cached_data = DataFetcher._history_cache[cache_key]
            if datetime.now() - cached_time < timedelta(days=1):
                print(f"[缓存] 命中历史数据: {cache_key}")
                return cached_data
        data = DataFetcher.get_historical_data(symbol, market, days)
        if data is not None:
            DataFetcher._history_cache[cache_key] = (datetime.now(), data)
        return data

    @staticmethod
    def get_historical_data(symbol, market, days):
        try:
            if market == 'A股':
                df = DataFetcher.get_akshare_data(symbol, days)
                if df is not None:
                    return df
            return DataFetcher.get_yfinance_data(symbol, market, days)
        except Exception as e:
            print(f"获取历史数据错误: {str(e)}")
        return None

    # ========== 辅助方法 ==========
    @staticmethod
    def format_symbol(symbol, market):
        try:
            symbol = str(symbol).strip()
            if market == 'A股':
                clean_code = DataFetcher._clean_code(symbol)
                if clean_code.startswith('6'):
                    return f"{clean_code}.SS"
                else:
                    return f"{clean_code}.SZ"
            elif market == '港股':
                clean_code = symbol.replace('.HK', '').replace('.hk', '')
                return f"{clean_code}.HK"
            else:
                return symbol.upper()
        except Exception as e:
            print(f"格式化代码错误: {str(e)}")
            return str(symbol)

    @staticmethod
    def _clean_code(symbol):
        code = str(symbol)
        if '.' in code:
            code = code.split('.')[0]
        code = code.replace('sh', '').replace('sz', '').replace('SH', '').replace('SZ', '')
        if len(code) < 6:
            code = code.zfill(6)
        return code

    @staticmethod
    def get_akshare_data(symbol, days):
        try:
            code = DataFetcher._clean_code(symbol)
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                   start_date=start_date, end_date=end_date, adjust="")
            if not df.empty:
                df = df.rename(columns={
                    '日期': 'Date', '开盘': 'Open', '收盘': 'Close',
                    '最高': 'High', '最低': 'Low', '成交量': 'Volume'
                })
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                df['Close'] = pd.to_numeric(df['Close'])
                df['Volume'] = pd.to_numeric(df['Volume'])
                return df
        except Exception as e:
            print(f"AKShare获取历史数据失败: {str(e)}")
        return None

    @staticmethod
    def get_yfinance_data(symbol, market, days):
        try:
            market_symbol = DataFetcher.format_symbol(symbol, market)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            stock = yf.Ticker(market_symbol)
            df = stock.history(start=start_date, end=end_date, interval="1d")
            return df
        except Exception as e:
            print(f"Yahoo Finance获取历史数据失败: {str(e)}")
        return None


class ChipAnalyzer:
    """筹码分析工具类"""
    
    @staticmethod
    def analyze(historical_data):
        try:
            if historical_data is None or historical_data.empty or len(historical_data) < 20:
                return None
                
            prices = historical_data['Close'].values
            volumes = historical_data['Volume'].values
            prices = prices[~np.isnan(prices)]
            volumes = volumes[~np.isnan(volumes)]
            
            if len(prices) == 0 or len(volumes) == 0:
                return None
                
            price_min = np.min(prices)
            price_max = np.max(prices)
            if price_max <= price_min:
                price_max = price_min * 1.1
                
            bins = 30
            hist_bins = np.linspace(price_min, price_max, bins)
            chip_distribution = np.zeros(bins-1)
            for i in range(len(prices)):
                price_idx = np.digitize(prices[i], hist_bins) - 1
                if 0 <= price_idx < len(chip_distribution):
                    chip_distribution[price_idx] += volumes[i]
            
            total_chip = np.sum(chip_distribution)
            if total_chip == 0:
                return None
                
            chip_percent = chip_distribution / total_chip * 100
            cum_chip = np.cumsum(chip_percent)
            
            target_percent = 90
            min_range = float('inf')
            best_start = 0
            best_end = 0
            
            for i in range(len(cum_chip)):
                for j in range(i, len(cum_chip)):
                    current_sum = cum_chip[j] - (cum_chip[i-1] if i > 0 else 0)
                    if current_sum >= target_percent:
                        current_range = ((hist_bins[j] - hist_bins[i]) / price_min) * 100
                        if current_range < min_range:
                            min_range = current_range
                            best_start = i
                            best_end = j
                        break
            
            return {
                'current_price': prices[-1],
                'price_min': price_min,
                'price_max': price_max,
                'total_volume': total_chip,
                'concentration_90': min_range if min_range != float('inf') else 0,
                'start_price': hist_bins[best_start],
                'end_price': hist_bins[best_end],
                'chip_percent_90': cum_chip[best_end] - (cum_chip[best_start-1] if best_start > 0 else 0),
                'distribution': list(zip(hist_bins[:-1], chip_percent))
            }
        except Exception as e:
            print(f"筹码分析错误: {str(e)}")
        return None


class DingDingSender:
    """钉钉消息发送工具类"""
    
    @staticmethod
    def send_message(webhook, message, phones=None):
        if not webhook:
            return False
        try:
            headers = {'Content-Type': 'application/json'}
            phone_list = []
            if phones:
                phone_list = [p.strip() for p in phones.split(',') if p.strip()]
            data = {
                "msgtype": "text",
                "text": {"content": message},
                "at": {"atMobiles": phone_list, "isAtAll": False}
            }
            response = requests.post(webhook, headers=headers, json=data, timeout=10)
            result = response.json()
            return result.get('errcode') == 0
        except Exception as e:
            print(f"钉钉发送错误: {str(e)}")
            return False


class FileManager:
    """文件管理工具类"""
    
    @staticmethod
    def save_json(filepath, data):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存文件失败 {filepath}: {str(e)}")
            return False
    
    @staticmethod
    def load_json(filepath, default=None):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return default if default is not None else []
        except Exception as e:
            print(f"加载文件失败 {filepath}: {str(e)}")
            return default if default is not None else []