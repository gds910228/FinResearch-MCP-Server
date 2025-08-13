# FinResearch MCP — 智能投研分析助手

面向「个人投资者/新手」的 MCP 服务：自动抓取最新财报、解析文本，并生成通俗化的综合财务健康分析（收入、盈利、现金流、负债与风险）。

## 功能亮点

- 一键端到端：抓取 → 解析 → 通俗化解读
- 支持 US 市场（EDGAR）：自动从 Atom 源定位最新 10-Q/10-K
- **支持 A股财报分析**：专业的中国A股财务分析，支持中文财务术语识别
- **自动生成 HTML 可视化报告**：分析后自动生成现代化的HTML财务分析网页，包含图表和交互效果
- 自动跟进 EDGAR filing 索引页（-index.htm）至主文档 HTML，提高分析有效性
- 支持直接传入 PDF/HTML 报告 URL（兜底）
- HTML 解析默认不依赖 pdfminer；PDF 解析可选安装 pdfminer.six

## 环境准备

- Python 3.13（Windows 11 已验证）
- 建议使用 venv/uv 等隔离环境

安装依赖（推荐使用清华镜像加速）：
```
# 若 venv 中无 pip，先安装
.\.venv\Scripts\python.exe -m ensurepip --upgrade

# （可选）设置镜像
.\.venv\Scripts\python.exe -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装最小依赖（HTML 解析即可运行）
.\.venv\Scripts\python.exe -m pip install -U beautifulsoup4 httpx tenacity pydantic python-dotenv openai mcp[cli]>=1.12.3

# 如需解析 PDF，再安装：
.\.venv\Scripts\python.exe -m pip install -U pdfminer.six
```

## 快速验证（本地冒烟测试）

无需 MCP 客户端，直接运行：
```bash
# 使用符号（US 市场自动抓取最新 10-Q/10-K）
.\.venv\Scripts\python.exe scripts/smoke_test.py --symbol AAPL --market US

# 或使用报告直链（HTML/PDF）
.\.venv\Scripts\python.exe scripts/smoke_test.py --url "https://www.sec.gov/Archives/edgar/data/.../xxx.htm"
```

成功时输出 JSON，包括：
- report：报告元数据（标题、日期、URL、来源）
- extract：解析概要（类型、大小、消息）
- analysis：通俗化财务健康解读

## 使用示例

### 1. 基础使用 - 分析美股公司

```bash
# 分析苹果公司最新财报
.\.venv\Scripts\python.exe scripts/smoke_test.py --symbol AAPL --market US

# 分析微软公司最新财报
.\.venv\Scripts\python.exe scripts/smoke_test.py --symbol MSFT --market US

# 分析特斯拉公司最新财报
.\.venv\Scripts\python.exe scripts/smoke_test.py --symbol TSLA --market US
```

### 2. 直接分析报告URL

```bash
# 分析指定的SEC报告
.\.venv\Scripts\python.exe scripts/smoke_test.py --url "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240930.htm"

# 分析PDF格式报告
.\.venv\Scripts\python.exe scripts/smoke_test.py --url "https://example.com/annual-report.pdf"
```

### 3. MCP客户端中的使用示例

在支持MCP的客户端（如Claude Desktop）中连接后，可以这样使用：

#### 工具调用示例

**获取最新报告元数据：**
```json
{
  "tool": "fetch_latest_report_tool",
  "arguments": {
    "symbol": "AAPL",
    "market": "US"
  }
}
```

**提取文档文本：**
```json
{
  "tool": "extract_text_from_pdf",
  "arguments": {
    "url": "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240930.htm"
  }
}
```

**分析文本内容：**
```json
{
  "tool": "analyze_text",
  "arguments": {
    "text": "Revenue increased by 15% year-over-year to $95.3 billion..."
  }
}
```

**端到端分析：**
```json
{
  "tool": "analyze_symbol",
  "arguments": {
    "symbol": "AAPL",
    "market": "US"
  }
}
```

#### 资源访问示例

**获取公司报告资源：**
```
report://AAPL
```

### 4. 典型输出示例

**成功的分析输出：**
```json
{
  "ok": true,
  "symbol": "AAPL",
  "market": "US",
  "report": {
    "ok": true,
    "symbol": "AAPL",
    "title": "Apple Inc. - Form 10-Q",
    "date": "2024-09-30",
    "url": "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240930.htm",
    "source": "EDGAR"
  },
  "extract": {
    "ok": true,
    "content_type": "text/html",
    "bytes": 245678,
    "message": "Successfully extracted text from HTML document"
  },
  "analysis": {
    "ok": true,
    "summary": "苹果公司财务状况整体健康...",
    "revenue_analysis": "营收表现强劲，同比增长15%...",
    "profitability_analysis": "盈利能力保持稳定...",
    "cash_flow_analysis": "现金流充裕...",
    "debt_analysis": "负债结构合理...",
    "risk_factors": ["市场竞争加剧", "供应链风险"],
    "overall_score": 85
  }
}
```

### 5. 常见使用场景

**投资研究：**
```bash
# 比较同行业公司
.\.venv\Scripts\python.exe scripts/smoke_test.py --symbol AAPL --market US
.\.venv\Scripts\python.exe scripts/smoke_test.py --symbol GOOGL --market US
.\.venv\Scripts\python.exe scripts/smoke_test.py --symbol MSFT --market US
```

**定期监控：**
```bash
# 监控持仓公司的最新财报
.\.venv\Scripts\python.exe scripts/smoke_test.py --symbol TSLA --market US
.\.venv\Scripts\python.exe scripts/smoke_test.py --symbol NVDA --market US
```

**深度分析：**
```bash
# 先获取报告URL，再进行详细分析
.\.venv\Scripts\python.exe scripts/smoke_test.py --symbol AMZN --market US
# 然后使用返回的URL进行更深入的分析
```

### 6. 错误处理示例

**符号不存在：**
```json
{
  "ok": false,
  "symbol": "INVALID",
  "market": "US",
  "message": "No recent filings found for symbol INVALID",
  "report": {
    "ok": false,
    "message": "Symbol not found in EDGAR database"
  }
}
```

**网络错误：**
```json
{
  "ok": false,
  "message": "Failed to extract text from report.",
  "extract": {
    "ok": false,
    "message": "HTTP 404: Document not found"
  }
}
```

## 以 MCP 方式运行

启动服务（Stdio 模式）：
```
.\.venv\Scripts\python.exe main.py
```

在支持 MCP 的客户端中连接后，可调用以下工具：

- fetch_latest_report(symbol, market="CN")  
  获取最新报告元数据（US: EDGAR；CN：占位；支持直接 URL 作为 symbol 兜底）

- extract_text_from_pdf(url)  
  下载并提取 PDF/HTML 文本（若为 EDGAR 索引页，会自动跟进至主文档）

- analyze_text(text)  
  对给定文本生成通俗化“综合财务健康分析”

- analyze_symbol(symbol, market="CN")  
  端到端：抓取 → 解析 → 分析

资源（Resources）：
- report://{symbol}  
  返回最新报告元数据（默认 market=CN）

## MCP 客户端配置

SSE 直连（默认，main.py 使用 transport="sse"）
1) 启动服务
```
.\.venv\Scripts\python.exe main.py
```
2) 观察控制台，记录输出的 SSE 地址（类似 http://127.0.0.1:43xxx/）。首次运行可能触发防火墙提示，请允许本地访问。
3) 在支持 MCP 的客户端中添加 SSE 配置（以 Claude Desktop 为例，示例 JSON 片段）：
```json
{
  "mcpServers": {
    "FinResearchMCP": {
      "type": "sse",
      "url": "http://127.0.0.1:43112/"
    }
  }
}
```
- url 填上一步控制台打印的实际地址
- 保存配置后，重启客户端或触发刷新

可选：使用 stdio 模式（某些客户端仅支持 command/stdio）
- 将 main.py 末尾启动方式改为：
```python
mcp.run(transport="stdio")
```
- 客户端配置改为 command/args（以 Claude Desktop 为例）：
```json
{
  "mcpServers": {
    "FinResearchMCP": {
      "command": "python",
      "args": ["main.py"]
    }
  }
}
```
- Windows 路径按实际 venv 位置填写，必要时加上 "cwd" 指定工作目录

工具与资源在客户端内可直接调用：
- Tools: fetch_latest_report, extract_text_from_pdf, analyze_text, analyze_symbol
- Resource: report://{symbol}


## 目录结构

```
.
├─ main.py                 # MCP 服务入口（FastMCP）
├─ modules/
│  ├─ scraper.py          # 报告抓取（US: EDGAR；直链兜底）
│  ├─ parser.py           # 文档解析（HTML；PDF 可选 pdfminer）
│  ├─ analysis.py         # 通俗化综合财务健康分析（规则/模板）
│  └─ __init__.py
├─ scripts/
│  └─ smoke_test.py       # 本地冒烟测试脚本（不依赖 MCP 客户端）
├─ docs/
│  ├─ PRD.md
│  └─ tasks.md
└─ pyproject.toml
```

## 设计与实现要点

- 抓取：US 使用 EDGAR Atom 源定位最新 10-Q/10-K；返回 filing 索引页链接。
- 解析：遇到 EDGAR 索引页（-index.htm）将自动解析“文档列表”并跟进至主文档 HTML，再提取正文文本。
- 分析：基于关键词与模板生成通俗化解读；覆盖收入、盈利、现金流、负债四大维度；可按需扩充词表或接入 LLM 增强。
- 异常与容错：网络重试（tenacity）、HTML 清洗、PDF 懒加载（未安装 pdfminer 也能跑 HTML）。

## 已知限制与后续优化

- CN 市场尚未接入官方源（可用直链兜底）；后续可集成巨潮/交易所公告目录。
- EDGAR 主文档选择采用启发式，少数 filing 结构可能需要专项规则增强。
- 分析为规则/模板基线，可接入 LLM（设置 OPENAI_API_KEY）以提升可读性与准确性。

## 许可证

MIT（如无特别声明，可按企业内部合规策略调整）