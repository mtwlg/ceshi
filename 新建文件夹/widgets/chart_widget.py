# widgets/chart_widget.py
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

class TimeShareChart:
    """分时图组件"""
    
    def __init__(self, parent, width=8, height=4, dpi=100):
        self.parent = parent
        self.width = width
        self.height = height
        self.dpi = dpi
        
        # 创建图形
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.figure.add_subplot(111)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # 设置样式
        self.setup_style()
        
    def setup_style(self):
        """设置图表样式"""
        self.ax.set_facecolor('#f8f9fa')
        self.figure.patch.set_facecolor('white')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
    def plot_timeshare(self, data, stock_name):
        """绘制分时图"""
        self.ax.clear()
        self.setup_style()
        
        if not data or len(data) == 0:
            self.ax.text(0.5, 0.5, '暂无分时数据', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
            
        # 绘制价格线
        times = [d['time'] for d in data]
        prices = [d['price'] for d in data]
        avg_prices = [d.get('avg_price', d['price']) for d in data]
        
        self.ax.plot(times, prices, 'r-', linewidth=2, label='实时价格')
        self.ax.plot(times, avg_prices, 'b--', linewidth=1, label='均价')
        
        # 设置标题和标签
        self.ax.set_title(f'{stock_name} 分时图', fontsize=14, fontweight='bold')
        self.ax.set_xlabel('时间', fontsize=10)
        self.ax.set_ylabel('价格 (元)', fontsize=10)
        self.ax.legend(loc='upper left')
        
        # 旋转x轴标签
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
        
        # 填充颜色区域
        base_price = data[0]['prev_close'] if 'prev_close' in data[0] else prices[0]
        self.ax.fill_between(times, prices, base_price, 
                            where=(np.array(prices) > base_price),
                            color='red', alpha=0.3, interpolate=True)
        self.ax.fill_between(times, prices, base_price,
                            where=(np.array(prices) <= base_price),
                            color='green', alpha=0.3, interpolate=True)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
    def plot_capital_flow(self, data, stock_name):
        """绘制资金流向图"""
        self.ax.clear()
        self.setup_style()
        
        if not data:
            self.ax.text(0.5, 0.5, '暂无资金数据', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
            
        # 绘制柱状图
        categories = ['主力流入', '主力流出', '散户流入', '散户流出']
        values = [
            data.get('main_inflow', 0),
            data.get('main_outflow', 0),
            data.get('retail_inflow', 0),
            data.get('retail_outflow', 0)
        ]
        colors = ['red', 'green', 'lightcoral', 'lightgreen']
        
        bars = self.ax.bar(categories, values, color=colors, alpha=0.7)
        
        # 在柱子上添加数值
        for bar, value in zip(bars, values):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:.2f}亿', ha='center', va='bottom')
        
        self.ax.set_title(f'{stock_name} 资金流向', fontsize=14, fontweight='bold')
        self.ax.set_ylabel('金额 (亿元)', fontsize=10)
        self.ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
    def clear(self):
        """清空图表"""
        self.ax.clear()
        self.setup_style()
        self.canvas.draw()