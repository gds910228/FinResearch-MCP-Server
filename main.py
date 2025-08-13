"""
Intelligent Investment Research Assistant - MCP Server

Tools:
- fetch_latest_report(symbol, market="CN")
- extract_text_from_pdf(url)
- analyze_text(text)
- analyze_symbol(symbol, market="CN")  # end-to-end: fetch -> parse -> analyze

Resources:
- report://{symbol}  # returns latest report meta (market defaults to CN)

Run:
    uv run python main.py
Then connect via your MCP client (SSE transport).
"""

from __future__ import annotations

import json
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP

from modules.scraper import fetch_latest_report, ReportMeta
from modules.parser import fetch_and_extract_text, ExtractResult
from modules.analysis import analyze_text as analyze_plain_text, AnalysisResult

# Create an MCP server
mcp = FastMCP("FinResearchMCP")


def _dump(model) -> Dict[str, Any]:
    try:
        return model.model_dump(exclude_none=True)  # pydantic v2
    except Exception:
        # fallback for plain dict or unexpected objects
        if isinstance(model, dict):
            return model
        return {"value": str(model)}


@mcp.tool()
def fetch_latest_report_tool(symbol: str, market: str = "CN") -> Dict[str, Any]:
    """Fetch latest report metadata for a symbol (supports US via EDGAR; CN currently placeholder; direct URL also supported)."""
    meta: ReportMeta = fetch_latest_report(symbol, market)
    return _dump(meta)


@mcp.tool()
def extract_text_from_pdf(url: str) -> Dict[str, Any]:
    """Download and extract text from a PDF or HTML page."""
    result: ExtractResult = fetch_and_extract_text(url)
    # 为避免在通道中传输超大文本，可选择性截断或仅返回提示。这里直接返回文本，客户端可自行处理。
    return _dump(result)


@mcp.tool()
def analyze_text(text: str) -> Dict[str, Any]:
    """Generate a plain-language comprehensive financial health analysis from provided text."""
    analysis: AnalysisResult = analyze_plain_text(text)
    return _dump(analysis)


@mcp.tool()
def analyze_symbol(symbol: str, market: str = "CN") -> Dict[str, Any]:
    """
    End-to-end analysis:
    1) Fetch latest report meta
    2) Download & extract text (PDF/HTML)
    3) Produce comprehensive financial health analysis (plain language)
    """
    meta: ReportMeta = fetch_latest_report(symbol, market)
    if not meta.ok or not meta.url:
        return {
            "ok": False,
            "symbol": symbol,
            "market": market,
            "message": meta.message or "Failed to fetch latest report metadata.",
            "report": _dump(meta),
        }

    extract: ExtractResult = fetch_and_extract_text(meta.url)
    if not extract.ok or not extract.text:
        return {
            "ok": False,
            "symbol": symbol,
            "market": market,
            "message": extract.message or "Failed to extract text from report.",
            "report": _dump(meta),
            "extract": {
                "ok": extract.ok,
                "content_type": extract.content_type,
                "bytes": extract.bytes,
                "message": extract.message,
                "url": extract.url,
            },
        }

    analysis: AnalysisResult = analyze_plain_text(extract.text)

    return {
        "ok": True,
        "symbol": symbol,
        "market": market,
        "report": _dump(meta),
        "extract": {
            "ok": extract.ok,
            "content_type": extract.content_type,
            "bytes": extract.bytes,
            "message": extract.message,
            "url": extract.url,
            # 如需返回全文，可添加 "text": extract.text
        },
        "analysis": _dump(analysis),
    }


@mcp.resource("report://{symbol}")
def report_resource(symbol: str) -> str:
    """
    Resource returning latest report metadata for a symbol.
    Note: market defaults to CN in this resource for simplicity.
    """
    meta: ReportMeta = fetch_latest_report(symbol, market="CN")
    return json.dumps(_dump(meta), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Start the server
    mcp.run(transport="stdio")