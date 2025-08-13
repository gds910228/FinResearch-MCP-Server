from __future__ import annotations

import re
import time
from typing import Optional, Dict, Any

import httpx
import xml.etree.ElementTree as ET
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .cn_stock_fetcher import CNStockFetcher


class ReportMeta(BaseModel):
    ok: bool = True
    symbol: str
    market: str = "CN"
    title: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None


DEFAULT_HEADERS = {
    # SEC/EDGAR 要求提供合理 UA，建议包含联系信息
    "User-Agent": "FinResearchMCP/0.1 (+https://example.org; contact: dev@example.org)",
    "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN,zh;q=0.8",
    "Connection": "close",
}


def _is_url(value: str) -> bool:
    return value.strip().lower().startswith(("http://", "https://"))


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.8, min=1, max=6),
    retry=retry_if_exception_type(httpx.HTTPError),
)
def _get(url: str, params: Optional[dict] = None, timeout: float = 20.0) -> httpx.Response:
    with httpx.Client(headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp


def fetch_latest_report(symbol: str, market: str = "CN") -> ReportMeta:
    """
    获取标的最新报告元数据。
    - 若 symbol 本身是 URL（PDF/HTML），直接返回该 URL（兜底路径，便于 MVP 立刻可用）
    - US 市场：尝试从 SEC EDGAR Atom 源获取最近 10-Q/10-K
    - CN 市场：当前返回占位信息，建议使用直接 URL 兜底，或后续实现 CNINFO 抓取
    """
    symbol = symbol.strip()
    if _is_url(symbol):
        title = "Direct Report URL"
        today = time.strftime("%Y-%m-%d")
        return ReportMeta(
            ok=True,
            symbol="N/A",
            market=market,
            title=title,
            date=today,
            url=symbol,
            source="USER",
            raw={"hint": "Direct URL mode"},
            message="Using direct URL as report source.",
        )

    m = market.upper().strip() if market else "CN"
    if m == "US":
        meta = _fetch_us_edgar_latest(symbol)
        if meta:
            return meta
        return ReportMeta(
            ok=False,
            symbol=symbol,
            market=m,
            source="EDGAR",
            message="Failed to locate latest filing from EDGAR. You may pass a direct PDF/HTML URL instead.",
        )

    # CN 市场：使用A股数据获取器
    if m == "CN":
        cn_fetcher = CNStockFetcher()
        cn_result = cn_fetcher.fetch_latest_report(symbol)
        
        if cn_result["ok"]:
            return ReportMeta(
                ok=True,
                symbol=symbol,
                market=m,
                title=cn_result.get("title", f"{symbol} 财务报告"),
                date=cn_result.get("date"),
                url=cn_result.get("url"),
                source=cn_result.get("source", "CNINFO"),
                raw=cn_result.get("raw", {}),
                message=cn_result.get("message", "成功获取A股财报信息")
            )
        else:
            return ReportMeta(
                ok=False,
                symbol=symbol,
                market=m,
                source="CNINFO",
                message=cn_result.get("message", "获取A股财报失败，请检查股票代码或使用直接URL"),
            )
    
    # 其他市场：返回占位信息
    return ReportMeta(
        ok=False,
        symbol=symbol,
        market=m,
        source="UNKNOWN",
        message=f"Market {m} not supported yet. Please pass a direct PDF/HTML report URL as symbol for now.",
    )


def _fetch_us_edgar_latest(symbol: str) -> Optional[ReportMeta]:
    """
    通过 EDGAR 查询最近 10-Q 或 10-K 的 Filing 页面（多为 HTML）。
    返回的 url 指向 Filing 详情页（HTML），parser 将自动处理 HTML 提取文本。
    """
    # 先尝试 10-Q，再尝试 10-K
    for ftype in ("10-Q", "10-K"):
        meta = _edgar_atom_latest(symbol, ftype)
        if meta:
            return meta
    return None


def _edgar_atom_latest(symbol: str, form_type: str) -> Optional[ReportMeta]:
    # EDGAR browse 接口（Atom）
    # 示例: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=AAPL&type=10-Q&count=1&owner=exclude&output=atom
    url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        "action": "getcompany",
        "CIK": symbol,
        "type": form_type,
        "count": "1",
        "owner": "exclude",
        "output": "atom",
    }
    try:
        resp = _get(url, params=params)
    except httpx.HTTPError:
        return None

    try:
        root = ET.fromstring(resp.text)
    except Exception:
        return None

    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = root.find("a:entry", ns)
    if entry is None:
        return None

    title = entry.findtext("a:title", default="",
                           namespaces=ns) or f"{symbol} {form_type}"
    updated = entry.findtext("a:updated", default=None, namespaces=ns)

    link = None
    for l in entry.findall("a:link", ns):
        href = l.get("href")
        if href:
            link = href
            break

    summary_text = entry.findtext("a:summary", default="", namespaces=ns) or ""

    return ReportMeta(
        ok=True,
        symbol=symbol,
        market="US",
        title=title,
        date=_extract_date(updated) if updated else None,
        url=link,
        source="EDGAR",
        raw={"summary": summary_text, "form_type": form_type},
        message=f"Located latest {form_type} filing page.",
    )


def _extract_date(dt: str) -> Optional[str]:
    # 格式如 2025-05-03T16:20:54-04:00 -> 2025-05-03
    m = re.match(r"(\d{4}-\d{2}-\d{2})", dt or "")
    return m.group(1) if m else None