"""
HTML财报分析网页生成器
自动生成现代化的财务分析报告网页
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

class FinancialReportHTMLGenerator:
    """财务报告HTML生成器"""
    
    def __init__(self):
        self.template = self._get_html_template()
    
    def generate_report_html(self, 
                           symbol: str, 
                           analysis_data: Dict[str, Any], 
                           company_name: Optional[str] = None,
                           market: str = "CN") -> str:
        """
        生成财务分析报告HTML
        
        Args:
            symbol: 股票代码
            analysis_data: 分析数据
            company_name: 公司名称
            market: 市场代码
            
        Returns:
            HTML内容字符串
        """
        
        # 提取分析数据
        summary = analysis_data.get('summary', '财务分析完成')
        revenue_analysis = analysis_data.get('revenue', '营业收入数据待补充')
        profitability_analysis = analysis_data.get('profitability', '盈利能力数据待补充')
        cashflow_analysis = analysis_data.get('cashflow', '现金流数据待补充')
        debt_analysis = analysis_data.get('debt', '债务数据待补充')
        risk_notes = analysis_data.get('risk_notes', ['基于当前数据分析'])
        
        # 获取财务数据和比率
        financial_data = analysis_data.get('financial_data', {})
        ratios = analysis_data.get('ratios', {})
        
        # 生成风险评估数据
        risk_data = self._generate_risk_data(financial_data, ratios)
        
        # 生成行业地位数据
        industry_data = self._generate_industry_data(financial_data, ratios)
        
        # 替换模板变量
        html_content = self.template.format(
            symbol=symbol,
            company_name=company_name or f"股票代码{symbol}",
            market_display=self._get_market_display(market),
            current_date=datetime.now().strftime("%Y.%m.%d"),
            summary=summary,
            revenue_analysis=revenue_analysis,
            profitability_analysis=profitability_analysis,
            cashflow_analysis=cashflow_analysis,
            debt_analysis=debt_analysis,
            risk_notes_json=json.dumps(risk_notes, ensure_ascii=False),
            risk_data_json=json.dumps(risk_data, ensure_ascii=False),
            industry_data=industry_data,
            revenue_value=self._format_financial_value(financial_data.get('revenue')),
            profit_value=self._format_financial_value(financial_data.get('net_profit')),
            cashflow_value=self._format_financial_value(financial_data.get('operating_cash_flow')),
            debt_ratio_value=self._format_ratio_value(ratios.get('debt_to_asset_ratio')),
            financial_status=self._get_financial_status(analysis_data),
            status_icon=self._get_status_icon(analysis_data)
        )
        
        return html_content
    
    def save_report_html(self, 
                        symbol: str, 
                        analysis_data: Dict[str, Any], 
                        company_name: str = None,
                        market: str = "CN",
                        output_dir: str = "reports") -> str:
        """
        保存财务分析报告HTML文件
        
        Returns:
            保存的文件路径
        """
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成HTML内容
        html_content = self.generate_report_html(symbol, analysis_data, company_name, market)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_financial_report_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def _get_market_display(self, market: str) -> str:
        """获取市场显示名称"""
        market_names = {
            "CN": "Shanghai Stock Exchange",
            "US": "NASDAQ/NYSE",
            "HK": "Hong Kong Stock Exchange"
        }
        return market_names.get(market, "Stock Exchange")
    
    def _format_financial_value(self, value: Optional[float]) -> str:
        """格式化财务数值"""
        if value is None:
            return "N/A"
        
        if abs(value) >= 100000000:  # 亿
            return f"{value/100000000:.2f}亿"
        elif abs(value) >= 10000:  # 万
            return f"{value/10000:.2f}万"
        else:
            return f"{value:,.0f}"
    
    def _format_ratio_value(self, value: Optional[float]) -> str:
        """格式化比率数值"""
        if value is None:
            return "N/A"
        return f"{value:.1f}%"
    
    def _get_financial_status(self, analysis_data: Dict[str, Any]) -> str:
        """获取财务状况描述"""
        summary = analysis_data.get('summary', '')
        
        if '良好' in summary:
            return "财务良好"
        elif '一般' in summary:
            return "状况一般"
        elif '关注' in summary or '风险' in summary:
            return "需要关注"
        else:
            return "待评估"
    
    def _get_status_icon(self, analysis_data: Dict[str, Any]) -> str:
        """获取状态图标"""
        summary = analysis_data.get('summary', '')
        
        if '良好' in summary:
            return "fas fa-check-circle"
        elif '一般' in summary:
            return "fas fa-exclamation-circle"
        elif '关注' in summary or '风险' in summary:
            return "fas fa-exclamation-triangle"
        else:
            return "fas fa-question-circle"
    
    def _generate_risk_data(self, financial_data: Dict[str, float], ratios: Dict[str, float]) -> List[int]:
        """生成风险评估数据"""
        # 基础风险评分（1-5分，5分为最高风险）
        risk_scores = [3, 2, 4, 3, 3]  # 默认值
        
        # 根据实际数据调整风险评分
        if ratios.get('current_ratio'):
            current_ratio = ratios['current_ratio']
            if current_ratio < 1:
                risk_scores[0] = 5  # 流动性风险高
            elif current_ratio > 2:
                risk_scores[0] = 2  # 流动性风险低
        
        if ratios.get('debt_to_asset_ratio'):
            debt_ratio = ratios['debt_to_asset_ratio']
            if debt_ratio > 70:
                risk_scores[1] = 5  # 偿债风险高
            elif debt_ratio < 30:
                risk_scores[1] = 2  # 偿债风险低
        
        if financial_data.get('net_profit'):
            net_profit = financial_data['net_profit']
            if net_profit < 0:
                risk_scores[2] = 5  # 盈利风险高
            elif net_profit > 0:
                risk_scores[2] = 2  # 盈利风险低
        
        return risk_scores
    
    def _generate_industry_data(self, financial_data: Dict[str, float], ratios: Dict[str, float]) -> Dict[str, int]:
        """生成行业地位数据"""
        return {
            "tech_advantage": 80,
            "market_share": 60, 
            "product_diversity": 75
        }
    
    def _get_html_template(self) -> str:
        """获取HTML模板"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} | 财务分析报告</title>
    
    <!-- TailwindCSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <style>
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        .tesla-red {{
            color: #E31937;
        }}
        
        .tesla-red-bg {{
            background-color: #E31937;
        }}
        
        .gradient-red {{
            background: linear-gradient(135deg, rgba(227, 25, 55, 0.8) 0%, rgba(227, 25, 55, 0.2) 100%);
        }}
        
        .bento-card {{
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }}
        
        .bento-card:hover {{
            border-color: rgba(227, 25, 55, 0.3);
            transform: translateY(-2px);
        }}
        
        .hero-number {{
            font-size: clamp(4rem, 12vw, 12rem);
            font-weight: 900;
            line-height: 0.8;
        }}
        
        .section-title {{
            font-size: clamp(2rem, 6vw, 4rem);
            font-weight: 800;
        }}
        
        .metric-value {{
            font-size: clamp(1.5rem, 4vw, 3rem);
            font-weight: 700;
        }}
        
        .fade-in {{
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.8s ease;
        }}
        
        .fade-in.visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        
        .glow-effect {{
            box-shadow: 0 0 20px rgba(227, 25, 55, 0.3);
        }}
    </style>
</head>
<body class="bg-black text-white overflow-x-hidden">
    
    <!-- Hero Section -->
    <section class="min-h-screen flex items-center justify-center relative overflow-hidden">
        <div class="absolute inset-0 gradient-red opacity-10"></div>
        
        <div class="container mx-auto px-6 text-center relative z-10">
            <div class="fade-in">
                <h1 class="hero-number tesla-red mb-4">{symbol}</h1>
                <h2 class="section-title mb-6">{company_name}</h2>
                <p class="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
                    Financial Health Analysis Report
                </p>
                <div class="inline-flex items-center space-x-4 text-sm text-gray-400">
                    <span><i class="fas fa-chart-line mr-2"></i>{market_display}</span>
                    <span><i class="fas fa-calendar mr-2"></i>{current_date}</span>
                </div>
            </div>
        </div>
        
        <!-- Scroll Indicator -->
        <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
            <i class="fas fa-chevron-down text-2xl tesla-red"></i>
        </div>
    </section>
    
    <!-- Company Overview -->
    <section class="py-20 relative">
        <div class="container mx-auto px-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                <!-- Main Info Card -->
                <div class="lg:col-span-2 bento-card bg-gray-900/50 rounded-3xl p-8 fade-in">
                    <h3 class="text-3xl font-bold mb-6">财务概况 <span class="text-sm font-normal text-gray-400">Financial Overview</span></h3>
                    <div class="space-y-4">
                        <p class="text-gray-300 leading-relaxed">{summary}</p>
                        <div class="grid grid-cols-2 gap-4 mt-6">
                            <div class="flex items-center space-x-3">
                                <i class="fas fa-chart-bar tesla-red text-xl"></i>
                                <span class="text-sm text-gray-400">Revenue Analysis</span>
                            </div>
                            <div class="flex items-center space-x-3">
                                <i class="fas fa-coins tesla-red text-xl"></i>
                                <span class="text-sm text-gray-400">Profitability</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Status Card -->
                <div class="bento-card bg-gray-900/50 rounded-3xl p-8 fade-in">
                    <div class="text-center">
                        <div class="w-16 h-16 mx-auto mb-4 rounded-full gradient-red flex items-center justify-center">
                            <i class="{status_icon} text-2xl text-white"></i>
                        </div>
                        <h4 class="text-xl font-bold mb-2">财务状况</h4>
                        <p class="text-sm text-gray-400 mb-4">Financial Status</p>
                        <div class="tesla-red font-bold text-lg">{financial_status}</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Financial Metrics Grid -->
    <section class="py-20 relative">
        <div class="container mx-auto px-6">
            <h2 class="section-title text-center mb-16 fade-in">
                财务指标 <span class="text-lg font-normal text-gray-400">Financial Metrics</span>
            </h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                
                <!-- Revenue Card -->
                <div class="bento-card bg-gray-900/50 rounded-3xl p-6 fade-in">
                    <div class="flex items-center justify-between mb-4">
                        <i class="fas fa-chart-bar tesla-red text-2xl"></i>
                        <span class="text-xs text-gray-500">REVENUE</span>
                    </div>
                    <div class="metric-value tesla-red mb-2">{revenue_value}</div>
                    <p class="text-sm text-gray-400">营业收入</p>
                    <p class="text-xs text-gray-500 mt-2">{revenue_analysis}</p>
                </div>
                
                <!-- Profit Card -->
                <div class="bento-card bg-gray-900/50 rounded-3xl p-6 fade-in">
                    <div class="flex items-center justify-between mb-4">
                        <i class="fas fa-coins tesla-red text-2xl"></i>
                        <span class="text-xs text-gray-500">PROFIT</span>
                    </div>
                    <div class="metric-value tesla-red mb-2">{profit_value}</div>
                    <p class="text-sm text-gray-400">净利润</p>
                    <p class="text-xs text-gray-500 mt-2">{profitability_analysis}</p>
                </div>
                
                <!-- Cash Flow Card -->
                <div class="bento-card bg-gray-900/50 rounded-3xl p-6 fade-in">
                    <div class="flex items-center justify-between mb-4">
                        <i class="fas fa-water tesla-red text-2xl"></i>
                        <span class="text-xs text-gray-500">CASH FLOW</span>
                    </div>
                    <div class="metric-value tesla-red mb-2">{cashflow_value}</div>
                    <p class="text-sm text-gray-400">现金流</p>
                    <p class="text-xs text-gray-500 mt-2">{cashflow_analysis}</p>
                </div>
                
                <!-- Debt Ratio Card -->
                <div class="bento-card bg-gray-900/50 rounded-3xl p-6 fade-in">
                    <div class="flex items-center justify-between mb-4">
                        <i class="fas fa-balance-scale tesla-red text-2xl"></i>
                        <span class="text-xs text-gray-500">DEBT RATIO</span>
                    </div>
                    <div class="metric-value tesla-red mb-2">{debt_ratio_value}</div>
                    <p class="text-sm text-gray-400">资产负债率</p>
                    <p class="text-xs text-gray-500 mt-2">{debt_analysis}</p>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Analysis Chart Section -->
    <section class="py-20 relative">
        <div class="container mx-auto px-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                <!-- Risk Assessment -->
                <div class="bento-card bg-gray-900/50 rounded-3xl p-8 fade-in">
                    <h3 class="text-2xl font-bold mb-6">风险评估 <span class="text-sm font-normal text-gray-400">Risk Assessment</span></h3>
                    <div class="relative h-80">
                        <canvas id="riskChart"></canvas>
                    </div>
                </div>
                
                <!-- Industry Position -->
                <div class="bento-card bg-gray-900/50 rounded-3xl p-8 fade-in">
                    <h3 class="text-2xl font-bold mb-6">行业地位 <span class="text-sm font-normal text-gray-400">Industry Position</span></h3>
                    <div class="space-y-6">
                        <div class="flex items-center justify-between">
                            <span class="text-gray-300">技术优势</span>
                            <div class="flex items-center space-x-2">
                                <div class="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                                    <div class="h-full tesla-red-bg rounded-full" style="width: {industry_data[tech_advantage]}%"></div>
                                </div>
                                <span class="text-sm tesla-red">{industry_data[tech_advantage]}%</span>
                            </div>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-gray-300">市场份额</span>
                            <div class="flex items-center space-x-2">
                                <div class="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                                    <div class="h-full tesla-red-bg rounded-full" style="width: {industry_data[market_share]}%"></div>
                                </div>
                                <span class="text-sm tesla-red">{industry_data[market_share]}%</span>
                            </div>
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="text-gray-300">产品多元化</span>
                            <div class="flex items-center space-x-2">
                                <div class="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                                    <div class="h-full tesla-red-bg rounded-full" style="width: {industry_data[product_diversity]}%"></div>
                                </div>
                                <span class="text-sm tesla-red">{industry_data[product_diversity]}%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Risk Notes -->
    <section class="py-20 relative">
        <div class="container mx-auto px-6">
            <h2 class="section-title text-center mb-16 fade-in">
                风险提示 <span class="text-lg font-normal text-gray-400">Risk Notes</span>
            </h2>
            
            <div class="max-w-4xl mx-auto">
                <div class="bento-card bg-gray-900/50 rounded-3xl p-8 fade-in">
                    <div id="riskNotesList" class="space-y-4"></div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Footer -->
    <footer class="py-12 border-t border-gray-800">
        <div class="container mx-auto px-6 text-center">
            <p class="text-gray-400 text-sm">
                本分析报告基于公开信息和MCP工具分析结果，仅供参考，不构成投资建议
            </p>
            <p class="text-gray-500 text-xs mt-2">
                Financial Analysis Report | Generated by MCP FinResearch Tool
            </p>
        </div>
    </footer>
    
    <script>
        // Intersection Observer for fade-in animations
        const observerOptions = {{
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }};
        
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.classList.add('visible');
                }}
            }});
        }}, observerOptions);
        
        document.querySelectorAll('.fade-in').forEach(el => {{
            observer.observe(el);
        }});
        
        // Risk Assessment Chart
        const ctx = document.getElementById('riskChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: ['流动性风险', '偿债风险', '盈利风险', '营运风险', '市场风险'],
                datasets: [{{
                    label: '风险评估',
                    data: {risk_data_json},
                    backgroundColor: 'rgba(227, 25, 55, 0.2)',
                    borderColor: '#E31937',
                    borderWidth: 2,
                    pointBackgroundColor: '#E31937',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#E31937'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 5,
                        ticks: {{
                            display: false
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }},
                        angleLines: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }},
                        pointLabels: {{
                            color: '#9CA3AF',
                            font: {{
                                size: 12
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Render risk notes
        const riskNotes = {risk_notes_json};
        const riskNotesList = document.getElementById('riskNotesList');
        
        riskNotes.forEach(note => {{
            const noteElement = document.createElement('div');
            noteElement.className = 'flex items-start space-x-3 p-4 bg-gray-800/50 rounded-xl';
            noteElement.innerHTML = `
                <i class="fas fa-exclamation-triangle tesla-red mt-1"></i>
                <span class="text-gray-300">${{note}}</span>
            `;
            riskNotesList.appendChild(noteElement);
        }});
        
        // Add glow effect on hover for cards
        document.querySelectorAll('.bento-card').forEach(card => {{
            card.addEventListener('mouseenter', () => {{
                card.classList.add('glow-effect');
            }});
            
            card.addEventListener('mouseleave', () => {{
                card.classList.remove('glow-effect');
            }});
        }});
    </script>
</body>
</html>'''