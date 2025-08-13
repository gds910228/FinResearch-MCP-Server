"""
中国A股财报数据获取模块
支持从多个数据源获取A股上市公司财务报告
"""

import httpx
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
import time

class CNStockFetcher:
    """中国A股财报数据获取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_latest_report(self, symbol: str) -> Dict[str, Any]:
        """
        获取A股公司最新财报信息
        
        Args:
            symbol: 股票代码，如 "000001", "600036"
        
        Returns:
            包含财报信息的字典
        """
        try:
            # 标准化股票代码
            normalized_symbol = self._normalize_symbol(symbol)
            
            # 尝试多个数据源
            report_info = self._fetch_from_eastmoney(normalized_symbol)
            if not report_info:
                report_info = self._fetch_from_sina(normalized_symbol)
            
            if report_info:
                return {
                    "ok": True,
                    "symbol": symbol,
                    "market": "CN",
                    "title": report_info.get("title", "年度报告"),
                    "date": report_info.get("date", ""),
                    "url": report_info.get("url", ""),
                    "source": report_info.get("source", "东方财富"),
                    "raw": report_info.get("raw", {}),
                    "message": "成功获取A股财报信息"
                }
            else:
                return {
                    "ok": False,
                    "symbol": symbol,
                    "market": "CN",
                    "message": "未找到该股票的财报信息，请检查股票代码是否正确"
                }
                
        except Exception as e:
            return {
                "ok": False,
                "symbol": symbol,
                "market": "CN",
                "message": f"获取A股财报时发生错误: {str(e)}"
            }
    
    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码"""
        # 移除可能的前缀和后缀
        symbol = symbol.upper().replace("SH", "").replace("SZ", "").replace(".SH", "").replace(".SZ", "")
        
        # 确保是6位数字
        if symbol.isdigit():
            symbol = symbol.zfill(6)
        
        return symbol
    
    def _fetch_from_eastmoney(self, symbol: str) -> Optional[Dict[str, Any]]:
        """从东方财富获取财报信息"""
        try:
            # 东方财富API接口
            url = f"https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ZYZBAjaxNew"
            params = {
                "companyType": "4",
                "reportDateType": "0",
                "reportType": "1",
                "dates": "2024-12-31,2023-12-31,2022-12-31",
                "code": symbol
            }
            
            with httpx.Client(headers=self.headers, timeout=10) as client:
                response = client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and "data" in data:
                        # 构造财报信息
                        report_url = f"http://www.cninfo.com.cn/new/disclosure/stock?stockCode={symbol}&orgId="
                        
                        return {
                            "title": f"{symbol} 年度财务报告",
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "url": report_url,
                            "source": "东方财富",
                            "raw": {
                                "api_data": data,
                                "symbol": symbol
                            }
                        }
            
        except Exception as e:
            print(f"从东方财富获取数据失败: {e}")
        
        return None
    
    def _fetch_from_sina(self, symbol: str) -> Optional[Dict[str, Any]]:
        """从新浪财经获取财报信息"""
        try:
            # 确定市场代码
            market_code = self._get_market_code(symbol)
            full_symbol = f"{market_code}{symbol}"
            
            # 新浪财经API
            url = f"https://money.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stockid/{full_symbol}.phtml"
            
            with httpx.Client(headers=self.headers, timeout=10) as client:
                response = client.get(url)
                if response.status_code == 200:
                    # 构造财报信息
                    return {
                        "title": f"{symbol} 财务摘要",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "url": url,
                        "source": "新浪财经",
                        "raw": {
                            "symbol": symbol,
                            "market_code": market_code
                        }
                    }
                
        except Exception as e:
            print(f"从新浪财经获取数据失败: {e}")
        
        return None
    
    def _get_market_code(self, symbol: str) -> str:
        """根据股票代码确定市场代码"""
        if symbol.startswith(('000', '002', '003', '300')):
            return "sz"  # 深圳
        elif symbol.startswith(('600', '601', '603', '605', '688')):
            return "sh"  # 上海
        else:
            # 默认深圳
            return "sz"
    
    def get_cninfo_report_url(self, symbol: str) -> str:
        """获取巨潮资讯网的报告链接"""
        market_code = self._get_market_code(symbol)
        if market_code == "sh":
            org_id = "9900000002"
        else:
            org_id = "9900000001"
        
        return f"http://www.cninfo.com.cn/new/disclosure/stock?stockCode={symbol}&orgId={org_id}"
    
    def fetch_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取详细的财务数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            财务数据字典
        """
        try:
            normalized_symbol = self._normalize_symbol(symbol)
            
            # 模拟财务数据结构（实际应用中需要从真实API获取）
            financial_data = {
                "revenue": {
                    "current": "营业收入数据需要从具体API获取",
                    "previous": "上期营业收入",
                    "growth_rate": "增长率"
                },
                "profit": {
                    "net_profit": "净利润数据",
                    "gross_profit": "毛利润",
                    "profit_margin": "利润率"
                },
                "assets": {
                    "total_assets": "总资产",
                    "current_assets": "流动资产",
                    "fixed_assets": "固定资产"
                },
                "liabilities": {
                    "total_liabilities": "总负债",
                    "current_liabilities": "流动负债",
                    "debt_ratio": "资产负债率"
                },
                "cash_flow": {
                    "operating_cash_flow": "经营活动现金流",
                    "investing_cash_flow": "投资活动现金流",
                    "financing_cash_flow": "筹资活动现金流"
                }
            }
            
            return {
                "ok": True,
                "symbol": normalized_symbol,
                "data": financial_data,
                "message": "A股财务数据获取成功（示例数据）"
            }
            
        except Exception as e:
            return {
                "ok": False,
                "symbol": symbol,
                "message": f"获取A股财务数据失败: {str(e)}"
            }