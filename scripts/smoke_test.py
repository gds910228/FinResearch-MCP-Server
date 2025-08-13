#!/usr/bin/env python
"""
Smoke test for Intelligent Investment Research Assistant (local run without MCP client).

Usage examples:
  1) Direct report URL (HTML recommended for SEC filings):
     python scripts/smoke_test.py --url "https://www.sec.gov/Archives/edgar/data/1318605/000162828024007744/tsla-20231231.htm"

  2) Use symbol via EDGAR (US market):
     python scripts/smoke_test.py --symbol AAPL --market US
"""

from __future__ import annotations

import argparse
import json
import sys
import os
from typing import Dict, Any, Optional

# Ensure project root on sys.path for 'modules' package resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.scraper import fetch_latest_report, ReportMeta
from modules.parser import fetch_and_extract_text, ExtractResult
from modules.analysis import analyze_text as analyze_plain_text, AnalysisResult


def _dump(model) -> Dict[str, Any]:
    try:
        # pydantic v2 model
        return model.model_dump(exclude_none=True)  # type: ignore[attr-defined]
    except Exception:
        if isinstance(model, dict):
            return model
        return {"value": str(model)}


def run(url: Optional[str], symbol: str, market: str) -> Dict[str, Any]:
    # Build/Fetch report meta
    if url:
        meta = ReportMeta(
            ok=True,
            symbol="N/A",
            market=market,
            title="Direct Report URL",
            date=None,
            url=url,
            source="USER",
            raw={"hint": "Direct URL mode"},
            message=None,
        )
    else:
        meta = fetch_latest_report(symbol, market)

    if not meta.ok or not meta.url:
        return {
            "ok": False,
            "symbol": symbol,
            "market": market,
            "message": meta.message or "Failed to fetch latest report metadata.",
            "report": _dump(meta),
        }

    # Download & extract
    extract = fetch_and_extract_text(meta.url)
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

    # Analyze
    analysis = analyze_plain_text(extract.text)

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
            # "text": extract.text,  # uncomment if you need the full text
        },
        "analysis": _dump(analysis),
    }


def main():
    parser = argparse.ArgumentParser(description="Smoke test for FinResearch Assistant")
    parser.add_argument("--url", type=str, default=None, help="Direct report URL (PDF or HTML)")
    parser.add_argument("--symbol", type=str, default="AAPL", help="Ticker symbol (e.g., AAPL)")
    parser.add_argument("--market", type=str, default="US", help="Market (e.g., US, CN)")
    args = parser.parse_args()

    result = run(args.url, args.symbol, args.market)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()