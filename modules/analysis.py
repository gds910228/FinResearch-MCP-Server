from __future__ import annotations

import os
import re
from typing import Dict, Any, List, Optional

from pydantic import BaseModel
from .cn_analyzer import CNFinancialAnalyzer


class AnalysisResult(BaseModel):
    ok: bool = True
    summary: str
    revenue: str
    profitability: str
    cashflow: str
    debt: str
    risk_notes: List[str] = []


def _find_indicator_lines(text: str, patterns: List[str], max_lines: int = 30) -> List[str]:
    lines = text.splitlines()
    found: List[str] = []
    pat = re.compile("|".join(patterns), re.IGNORECASE)
    for ln in lines:
        if pat.search(ln):
            s = ln.strip()
            if s and len(s) < 400:
                found.append(s)
            if len(found) >= max_lines:
                break
    return found


def _mk_paragraph(title: str, clues: List[str], fallback: str) -> str:
    if not clues:
        return fallback
    preview = " | ".join(clues[:3])
    return f"{title}: {preview}"


def analyze_text(text: str) -> AnalysisResult:
    """
    规则/模板驱动的通俗化综合财务健康分析（离线可用）：
    - 根据关键词在文本中抓取线索片段
    - 组装四大维度的通俗化段落
    - 若文本过短则给出温和提示
    - 支持中文A股财报分析
    """
    t = text or ""
    short = len(t) < 500
    
    # 检测是否为中文财报
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', t))
    is_chinese_report = chinese_chars > len(t) * 0.3  # 如果中文字符超过30%，认为是中文报告
    
    # 如果是中文财报，使用专门的A股分析器
    if is_chinese_report:
        cn_analyzer = CNFinancialAnalyzer()
        cn_result = cn_analyzer.analyze_cn_financial_text(t)
        
        if cn_result.get("ok", False):
            return AnalysisResult(
                ok=True,
                summary=cn_result.get("summary", "A股财务分析完成"),
                revenue=cn_result.get("revenue", "营业收入分析"),
                profitability=cn_result.get("profitability", "盈利能力分析"),
                cashflow=cn_result.get("cashflow", "现金流分析"),
                debt=cn_result.get("debt", "债务风险分析"),
                risk_notes=cn_result.get("risk_notes", [])
            )

    # 原有的英文财报分析逻辑
    revenue_clues = _find_indicator_lines(
        t,
        [
            r"revenue", r"sales", r"top line", r"营业收入", r"收入", r"主营业务收入",
        ],
    )
    profit_clues = _find_indicator_lines(
        t,
        [
            r"net income", r"profit", r"earnings", r"EPS", r"净利润", r"毛利率", r"费用率",
        ],
    )
    cash_clues = _find_indicator_lines(
        t,
        [
            r"cash flow", r"operating cash", r"现金流", r"经营活动现金流", r"自由现金流",
        ],
    )
    debt_clues = _find_indicator_lines(
        t,
        [
            r"debt", r"leverage", r"liabilities", r"asset[- ]?liability", r"负债", r"资产负债率",
        ],
    )

    revenue_para = _mk_paragraph(
        "Revenue performance",
        revenue_clues,
        "Revenue performance: No clear revenue lines detected; please refer to the detailed report for exact figures.",
    )
    profit_para = _mk_paragraph(
        "Profitability",
        profit_clues,
        "Profitability: Unable to locate profit-related sentences; margins and EPS may need manual confirmation.",
    )
    cash_para = _mk_paragraph(
        "Cash flow status",
        cash_clues,
        "Cash flow status: No obvious cash flow sentences found; verify operating cash flow in the statement.",
    )
    debt_para = _mk_paragraph(
        "Debt & risk level",
        debt_clues,
        "Debt & risk level: Debt-related context not found; check leverage and short-term borrowing carefully.",
    )

    risk_notes: List[str] = []
    if short:
        risk_notes.append("The source text is short; insights may be limited.")
    if not debt_clues:
        risk_notes.append("Debt information is unclear; consider reviewing the balance sheet and notes.")
    if not cash_clues:
        risk_notes.append("Cash flows are not explicit; check operating cash vs net income consistency.")

    summary = (
        "Overall, this is a plain-language financial health review covering revenue, profitability, cash flow, and debt. "
        "It highlights potential signals extracted from the document. "
        "Please validate key figures against official statements."
    )

    return AnalysisResult(
        ok=True,
        summary=summary,
        revenue=revenue_para,
        profitability=profit_para,
        cashflow=cash_para,
        debt=debt_para,
        risk_notes=risk_notes,
    )


# 预留：如检测到 OPENAI_API_KEY 可扩展 LLM 增强路径（当前未默认启用）
def analyze_text_with_llm(text: str) -> Optional[AnalysisResult]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        # 延展位：可在此接入 OpenAI SDK 进行更高质量结构化总结
        # 出于模板简洁考虑，这里不默认调用，以免影响离线可用性
        return None
    except Exception:
        return None