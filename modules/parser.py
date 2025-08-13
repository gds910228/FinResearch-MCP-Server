from __future__ import annotations

import io
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

DEFAULT_HEADERS = {
    "User-Agent": "FinResearchMCP/0.1 (+https://example.org; contact: dev@example.org)",
    "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN,zh;q=0.8",
    "Connection": "close",
}


class ExtractResult(BaseModel):
    ok: bool = True
    url: str
    content_type: Optional[str] = None
    text: Optional[str] = None
    bytes: Optional[int] = None
    pages: Optional[int] = None  # PDF pages (not strictly counted here)
    message: Optional[str] = None


def _looks_like_pdf(url: str, content_type: Optional[str]) -> bool:
    if content_type and "pdf" in content_type.lower():
        return True
    return url.lower().endswith((".pdf", ".pdf?"))


def _is_sec_index_page(url: str) -> bool:
    u = (url or "").lower()
    return ("sec.gov" in u) and (u.endswith("-index.htm") or u.endswith("-index.html"))


def _clean_html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines[:20000])  # cap length


def _sec_find_primary_document_url(html: str, base_url: str) -> Optional[str]:
    """
    On EDGAR filing index pages (-index.htm), find the primary 10-Q/10-K HTML document.
    Strategy:
      1) Parse document table (older 'tableFile' or newer tables).
      2) Prefer rows whose Type column is '10-Q' or '10-K'.
      3) Fallback to first HTML link (.htm/.html) that is not an index.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Candidate tables commonly used by EDGAR
    tables = []
    # Older style
    tables.extend(soup.find_all("table", {"class": "tableFile"}))
    # Newer style generic tables
    tables.extend(soup.find_all("table"))
    seen = set()
    chosen: Optional[str] = None

    def pick_from_table(table) -> Optional[str]:
        # Heuristic: find rows; identify columns by header text if available
        # Extract header map
        headers = []
        thead = table.find("thead")
        if thead:
            ths = thead.find_all(["th", "td"])
            headers = [th.get_text(strip=True).lower() for th in ths if th]
        # fallback: infer columns from first row
        rows = table.find_all("tr")
        for tr in rows:
            cells = tr.find_all(["td", "th"])
            if not cells:
                continue
            # try detect document link (first anchor)
            link = None
            for a in tr.find_all("a", href=True):
                href = a["href"].strip()
                if href and href not in seen:
                    link = href
                    break
            if not link:
                continue

            # Determine type text
            type_text = ""
            if headers and "type" in headers:
                # pick the cell under Type header index
                try:
                    idx = headers.index("type")
                    if idx < len(cells):
                        type_text = cells[idx].get_text(strip=True)
                except Exception:
                    type_text = ""
            else:
                # scan cells to find likely 'Type'
                for c in cells:
                    val = c.get_text(strip=True)
                    if val.upper() in ("10-Q", "10-K"):
                        type_text = val
                        break

            # Build absolute URL
            abs_url = urljoin(base_url, link)

            # Prefer primary forms
            if type_text.upper() in ("10-Q", "10-K"):
                if not abs_url.lower().endswith(("-index.htm", "-index.html")):
                    return abs_url

            # Keep first reasonable HTML as fallback
            if (abs_url.lower().endswith((".htm", ".html"))
                    and not abs_url.lower().endswith(("-index.htm", "-index.html"))):
                if not chosen:
                    # defer choose; still keep looking for 10-Q/10-K type match
                    nonlocal_chosen = abs_url  # placeholder
                    return nonlocal_chosen  # early fallback

        return None

    # Pass 1: prefer type-matched rows
    for t in tables:
        url = pick_from_table(t)
        if url:
            return url

    # Pass 2: fallback - any HTML link on page that isn't index
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        abs_url = urljoin(base_url, href)
        if abs_url.lower().endswith((".htm", ".html")) and not abs_url.lower().endswith(("-index.htm", "-index.html")):
            return abs_url

    return None


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.8, min=1, max=6),
    retry=retry_if_exception_type(httpx.HTTPError),
)
def _download(url: str, timeout: float = 30.0) -> httpx.Response:
    with httpx.Client(headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp


def fetch_and_extract_text(url: str) -> ExtractResult:
    """
    Download URL and extract text:
    - If PDF: parse with pdfminer.six (lazy import)
    - If HTML: parse and strip boilerplate
    - If HTML is an EDGAR index page (-index.htm), auto-follow to the primary 10-Q/10-K document and parse that.
    """
    # Step 1: download original URL
    resp = _download(url)
    ctype = (resp.headers.get("Content-Type", "") or "").split(";")[0].strip()
    data = resp.content or b""
    size = len(data)
    final_url = str(resp.url)

    # PDF branch (lazy import)
    if _looks_like_pdf(final_url, ctype):
        try:
            from pdfminer.high_level import extract_text  # type: ignore
        except Exception:
            return ExtractResult(
                ok=False,
                url=final_url,
                content_type=ctype,
                bytes=size,
                message="PDF parse requires pdfminer.six; please install it to enable PDF extraction.",
            )
        try:
            text = extract_text(io.BytesIO(data))
            return ExtractResult(ok=True, url=final_url, content_type=ctype or "application/pdf", text=text, bytes=size, message="PDF parsed")
        except Exception as e:
            return ExtractResult(ok=False, url=final_url, content_type=ctype, bytes=size, message=f"PDF parse failed: {e}")

    # HTML branch
    try:
        html = resp.text
        # Detect EDGAR index page and follow to primary document
        if _is_sec_index_page(final_url):
            primary_url = _sec_find_primary_document_url(html, final_url)
            if primary_url and primary_url != final_url:
                resp2 = _download(primary_url)
                ctype2 = (resp2.headers.get("Content-Type", "") or "").split(";")[0].strip()
                data2 = resp2.content or b""
                size2 = len(data2)
                if _looks_like_pdf(str(resp2.url), ctype2):
                    try:
                        from pdfminer.high_level import extract_text  # type: ignore
                    except Exception:
                        return ExtractResult(
                            ok=False,
                            url=str(resp2.url),
                            content_type=ctype2,
                            bytes=size2,
                            message="PDF parse requires pdfminer.six; please install it to enable PDF extraction.",
                        )
                    try:
                        text2 = extract_text(io.BytesIO(data2))
                        return ExtractResult(ok=True, url=str(resp2.url), content_type=ctype2 or "application/pdf", text=text2, bytes=size2, message="PDF parsed (primary)")
                    except Exception as e:
                        return ExtractResult(ok=False, url=str(resp2.url), content_type=ctype2, bytes=size2, message=f"PDF parse failed (primary): {e}")
                else:
                    html2 = resp2.text
                    clean2 = _clean_html_to_text(html2)
                    return ExtractResult(ok=True, url=str(resp2.url), content_type=ctype2 or "text/html", text=clean2, bytes=size2, message="HTML parsed (primary)")

        # Normal HTML parsing
        clean = _clean_html_to_text(html)
        return ExtractResult(ok=True, url=final_url, content_type=ctype or "text/html", text=clean, bytes=size, message="HTML parsed")
    except Exception as e:
        return ExtractResult(ok=False, url=final_url, content_type=ctype, bytes=size, message=f"HTML parse failed: {e}")