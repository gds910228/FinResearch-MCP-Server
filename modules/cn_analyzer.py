"""
中国A股财务分析模块
专门处理中文财务报告的分析和解读
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime

class CNFinancialAnalyzer:
    """中国A股财务分析器"""
    
    def __init__(self):
        # 中文财务术语映射
        self.financial_terms = {
            # 收入相关
            "营业收入": "revenue",
            "主营业务收入": "main_revenue", 
            "营业总收入": "total_revenue",
            "销售收入": "sales_revenue",
            
            # 利润相关
            "净利润": "net_profit",
            "归属于母公司所有者的净利润": "net_profit_parent",
            "毛利润": "gross_profit",
            "营业利润": "operating_profit",
            "利润总额": "total_profit",
            "扣除非经常性损益后的净利润": "adjusted_net_profit",
            
            # 资产相关
            "总资产": "total_assets",
            "流动资产": "current_assets",
            "非流动资产": "non_current_assets",
            "货币资金": "cash_and_equivalents",
            "应收账款": "accounts_receivable",
            "存货": "inventory",
            "固定资产": "fixed_assets",
            
            # 负债相关
            "总负债": "total_liabilities",
            "流动负债": "current_liabilities",
            "非流动负债": "non_current_liabilities",
            "短期借款": "short_term_debt",
            "长期借款": "long_term_debt",
            "应付账款": "accounts_payable",
            
            # 权益相关
            "所有者权益": "shareholders_equity",
            "股本": "share_capital",
            "资本公积": "capital_surplus",
            "盈余公积": "surplus_reserves",
            "未分配利润": "retained_earnings",
            
            # 现金流相关
            "经营活动产生的现金流量净额": "operating_cash_flow",
            "投资活动产生的现金流量净额": "investing_cash_flow",
            "筹资活动产生的现金流量净额": "financing_cash_flow",
            "现金及现金等价物净增加额": "net_cash_increase"
        }
        
        # 财务比率计算
        self.ratio_formulas = {
            "资产负债率": lambda assets, liabilities: (liabilities / assets * 100) if assets > 0 else 0,
            "流动比率": lambda current_assets, current_liabilities: (current_assets / current_liabilities) if current_liabilities > 0 else 0,
            "速动比率": lambda quick_assets, current_liabilities: (quick_assets / current_liabilities) if current_liabilities > 0 else 0,
            "毛利率": lambda gross_profit, revenue: (gross_profit / revenue * 100) if revenue > 0 else 0,
            "净利率": lambda net_profit, revenue: (net_profit / revenue * 100) if revenue > 0 else 0,
            "ROE": lambda net_profit, equity: (net_profit / equity * 100) if equity > 0 else 0,
            "ROA": lambda net_profit, assets: (net_profit / assets * 100) if assets > 0 else 0
        }
    
    def analyze_cn_financial_text(self, text: str) -> Dict[str, Any]:
        """
        分析中文财务报告文本
        
        Args:
            text: 财务报告文本内容
            
        Returns:
            分析结果字典
        """
        try:
            # 提取财务数据
            financial_data = self._extract_financial_data(text)
            
            # 计算财务比率
            ratios = self._calculate_ratios(financial_data)
            
            # 生成分析报告
            analysis = self._generate_analysis(financial_data, ratios, text)
            
            return {
                "ok": True,
                "summary": analysis.get("summary", "A股财务健康状况分析完成"),
                "revenue": analysis.get("revenue", "营业收入分析：需要更详细的数据进行分析"),
                "profitability": analysis.get("profitability", "盈利能力分析：请参考详细财务数据"),
                "cashflow": analysis.get("cashflow", "现金流分析：建议查看现金流量表"),
                "debt": analysis.get("debt", "债务风险分析：需要查看资产负债表详情"),
                "risk_notes": analysis.get("risk_notes", [
                    "建议关注资产负债率变化趋势",
                    "注意现金流与净利润的匹配性",
                    "关注主营业务收入的稳定性"
                ]),
                "financial_data": financial_data,
                "ratios": ratios
            }
            
        except Exception as e:
            return {
                "ok": False,
                "summary": f"A股财务分析过程中发生错误: {str(e)}",
                "revenue": "收入数据提取失败",
                "profitability": "盈利能力数据提取失败", 
                "cashflow": "现金流数据提取失败",
                "debt": "债务数据提取失败",
                "risk_notes": [
                    "数据提取不完整，建议查看原始财务报表",
                    "可能需要更详细的财务数据进行准确分析"
                ]
            }
    
    def _extract_financial_data(self, text: str) -> Dict[str, float]:
        """从文本中提取财务数据"""
        financial_data = {}
        
        # 数字模式匹配（支持中文数字格式）
        number_patterns = [
            r'([\d,]+\.?\d*)\s*万元',
            r'([\d,]+\.?\d*)\s*亿元',
            r'([\d,]+\.?\d*)\s*元',
            r'([\d,]+\.?\d*)\s*千元'
        ]
        
        # 遍历财务术语，尝试提取对应数值
        for cn_term, en_term in self.financial_terms.items():
            # 构建搜索模式
            for pattern in number_patterns:
                search_pattern = f'{cn_term}[：:]\\s*{pattern}'
                matches = re.findall(search_pattern, text)
                
                if matches:
                    try:
                        # 取第一个匹配的数值
                        value_str = matches[0].replace(',', '')
                        value = float(value_str)
                        
                        # 根据单位调整数值
                        if '万元' in search_pattern:
                            value *= 10000
                        elif '亿元' in search_pattern:
                            value *= 100000000
                        elif '千元' in search_pattern:
                            value *= 1000
                        
                        financial_data[en_term] = value
                        break
                    except ValueError:
                        continue
        
        return financial_data
    
    def _calculate_ratios(self, financial_data: Dict[str, float]) -> Dict[str, float]:
        """计算财务比率"""
        ratios = {}
        
        try:
            # 资产负债率
            if 'total_assets' in financial_data and 'total_liabilities' in financial_data:
                ratios['debt_to_asset_ratio'] = self.ratio_formulas['资产负债率'](
                    financial_data['total_assets'], 
                    financial_data['total_liabilities']
                )
            
            # 流动比率
            if 'current_assets' in financial_data and 'current_liabilities' in financial_data:
                ratios['current_ratio'] = self.ratio_formulas['流动比率'](
                    financial_data['current_assets'],
                    financial_data['current_liabilities']
                )
            
            # 毛利率
            if 'gross_profit' in financial_data and 'revenue' in financial_data:
                ratios['gross_margin'] = self.ratio_formulas['毛利率'](
                    financial_data['gross_profit'],
                    financial_data['revenue']
                )
            
            # 净利率
            if 'net_profit' in financial_data and 'revenue' in financial_data:
                ratios['net_margin'] = self.ratio_formulas['净利率'](
                    financial_data['net_profit'],
                    financial_data['revenue']
                )
            
            # ROE
            if 'net_profit' in financial_data and 'shareholders_equity' in financial_data:
                ratios['roe'] = self.ratio_formulas['ROE'](
                    financial_data['net_profit'],
                    financial_data['shareholders_equity']
                )
            
            # ROA
            if 'net_profit' in financial_data and 'total_assets' in financial_data:
                ratios['roa'] = self.ratio_formulas['ROA'](
                    financial_data['net_profit'],
                    financial_data['total_assets']
                )
                
        except Exception as e:
            print(f"计算财务比率时发生错误: {e}")
        
        return ratios
    
    def _generate_analysis(self, financial_data: Dict[str, float], ratios: Dict[str, float], text: str) -> Dict[str, Any]:
        """生成财务分析报告"""
        analysis = {}
        
        # 收入分析
        revenue_analysis = "营业收入分析："
        if 'revenue' in financial_data:
            revenue = financial_data['revenue']
            revenue_analysis += f"营业收入为{revenue:,.0f}元。"
            
            # 收入规模评估
            if revenue > 100000000000:  # 1000亿以上
                revenue_analysis += "属于大型企业收入规模。"
            elif revenue > 10000000000:  # 100亿以上
                revenue_analysis += "属于中大型企业收入规模。"
            elif revenue > 1000000000:  # 10亿以上
                revenue_analysis += "属于中型企业收入规模。"
            else:
                revenue_analysis += "属于中小型企业收入规模。"
        else:
            revenue_analysis += "未能从报告中提取到明确的营业收入数据，建议查看损益表。"
        
        analysis['revenue'] = revenue_analysis
        
        # 盈利能力分析
        profitability_analysis = "盈利能力分析："
        if 'net_profit' in financial_data:
            net_profit = financial_data['net_profit']
            if net_profit > 0:
                profitability_analysis += f"净利润为{net_profit:,.0f}元，公司盈利。"
            else:
                profitability_analysis += f"净利润为{net_profit:,.0f}元，公司亏损。"
            
            # 净利率分析
            if 'net_margin' in ratios:
                net_margin = ratios['net_margin']
                profitability_analysis += f"净利率为{net_margin:.2f}%。"
                if net_margin > 15:
                    profitability_analysis += "净利率较高，盈利能力强。"
                elif net_margin > 5:
                    profitability_analysis += "净利率适中。"
                else:
                    profitability_analysis += "净利率较低，需关注成本控制。"
        else:
            profitability_analysis += "未能提取到净利润数据，请查看利润表详情。"
        
        analysis['profitability'] = profitability_analysis
        
        # 现金流分析
        cashflow_analysis = "现金流分析："
        if 'operating_cash_flow' in financial_data:
            ocf = financial_data['operating_cash_flow']
            if ocf > 0:
                cashflow_analysis += f"经营活动现金流为{ocf:,.0f}元，现金流为正。"
            else:
                cashflow_analysis += f"经营活动现金流为{ocf:,.0f}元，现金流为负，需关注。"
        else:
            cashflow_analysis += "未能提取到经营现金流数据，建议查看现金流量表。"
        
        analysis['cashflow'] = cashflow_analysis
        
        # 债务风险分析
        debt_analysis = "债务风险分析："
        if 'debt_to_asset_ratio' in ratios:
            debt_ratio = ratios['debt_to_asset_ratio']
            debt_analysis += f"资产负债率为{debt_ratio:.2f}%。"
            if debt_ratio > 70:
                debt_analysis += "资产负债率较高，债务风险需要关注。"
            elif debt_ratio > 50:
                debt_analysis += "资产负债率适中。"
            else:
                debt_analysis += "资产负债率较低，财务结构稳健。"
        else:
            debt_analysis += "未能计算资产负债率，建议查看资产负债表。"
        
        analysis['debt'] = debt_analysis
        
        # 风险提示
        risk_notes = []
        
        if 'current_ratio' in ratios:
            current_ratio = ratios['current_ratio']
            if current_ratio < 1:
                risk_notes.append(f"流动比率为{current_ratio:.2f}，低于1，短期偿债能力需关注")
        
        if 'debt_to_asset_ratio' in ratios and ratios['debt_to_asset_ratio'] > 70:
            risk_notes.append("资产负债率超过70%，债务负担较重")
        
        if 'net_profit' in financial_data and financial_data['net_profit'] < 0:
            risk_notes.append("公司出现亏损，需关注经营状况")
        
        if not risk_notes:
            risk_notes.append("基于当前数据，未发现明显财务风险")
        
        analysis['risk_notes'] = risk_notes
        
        # 总体评估
        summary = "A股财务健康状况综合评估：基于提取的财务数据进行分析，"
        
        positive_signals = 0
        total_signals = 0
        
        # 盈利能力评分
        if 'net_profit' in financial_data and financial_data['net_profit'] > 0:
            positive_signals += 1
        total_signals += 1
        
        # 现金流评分
        if 'operating_cash_flow' in financial_data and financial_data['operating_cash_flow'] > 0:
            positive_signals += 1
        total_signals += 1
        
        # 债务水平评分
        if 'debt_to_asset_ratio' in ratios and ratios['debt_to_asset_ratio'] < 60:
            positive_signals += 1
        total_signals += 1
        
        if total_signals > 0:
            health_score = positive_signals / total_signals
            if health_score >= 0.8:
                summary += "财务状况良好。"
            elif health_score >= 0.6:
                summary += "财务状况一般，有改善空间。"
            else:
                summary += "财务状况需要关注，建议深入分析。"
        else:
            summary += "数据不足，建议获取更完整的财务报表进行分析。"
        
        analysis['summary'] = summary
        
        return analysis