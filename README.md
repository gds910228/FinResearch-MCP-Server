# FinResearch MCP Server

A Model Context Protocol (MCP) server for intelligent financial research and analysis with automated HTML report generation.

## Features

- **Multi-market Support**: Fetch financial reports from US (EDGAR) and Chinese A-share markets
- **Intelligent Text Extraction**: Extract and parse content from PDF and HTML financial documents
- **AI-Powered Analysis**: Generate comprehensive financial health assessments with Chinese A-share specialization
- **Automated HTML Reports**: Generate beautiful, interactive HTML financial analysis reports
- **End-to-End Workflow**: Complete analysis pipeline from data fetching to visual insights

## 🆕 New Features

### Chinese A-Share Analysis
- **Specialized A-Share Analyzer**: Dedicated module for Chinese financial reports analysis
- **Chinese Financial Terms**: Support for Chinese accounting terminology and standards
- **Localized Risk Assessment**: Risk evaluation tailored for Chinese market conditions

### Automated HTML Report Generation
- **Modern Design**: Bento Grid layout with Tesla Red (#E31937) theme
- **Data Visualization**: Interactive charts using Chart.js for risk assessment
- **Responsive Layout**: Mobile-friendly design with smooth animations
- **Professional Styling**: TailwindCSS + Font Awesome icons
- **Apple-style Animations**: Smooth scroll effects and hover interactions

## Tools

### `fetch_latest_report_tool`
Fetch the latest financial report metadata for a given stock symbol.

**Parameters:**
- `symbol` (string): Stock symbol (e.g., "AAPL", "600143")
- `market` (string, optional): Market code ("US" or "CN", defaults to "CN")

**Returns:**
- Report metadata including URL, title, date, and source information

### `extract_text_from_pdf`
Download and extract text content from PDF or HTML financial documents.

**Parameters:**
- `url` (string): URL of the document to extract text from

**Returns:**
- Extracted text content with metadata (content type, size, etc.)

### `analyze_text`
Generate a comprehensive financial health analysis from extracted text with automatic HTML report generation.

**Parameters:**
- `text` (string): Financial document text to analyze
- `symbol` (string, optional): Stock symbol for HTML report generation
- `company_name` (string, optional): Company name for report title

**Returns:**
- Structured analysis covering revenue, profitability, cash flow, debt, and risk assessment
- **Automatically generates HTML report** when symbol is provided

### `analyze_symbol` ⭐
End-to-end analysis combining all steps: fetch report → extract text → analyze → generate HTML.

**Parameters:**
- `symbol` (string): Stock symbol to analyze
- `market` (string, optional): Market code (defaults to "CN")

**Returns:**
- Complete analysis results with report metadata, extraction info, and financial insights
- **Automatically generates beautiful HTML report** saved to `reports/` directory

## Resources

### `report://{symbol}`
Access the latest report metadata for a stock symbol as a resource.

**Example:** `report://600143` returns metadata for stock 600143

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd FinResearch-MCP-Server
```

2. Install dependencies:
```bash
uv sync
```

3. Run the server:
```bash
uv run python main.py
```

The server will start on `http://localhost:8000` using Server-Sent Events (SSE) transport.

## Usage Examples

### Analyze Chinese A-Share Stock (with HTML Report)
```python
# Analyze 金发科技 (Kingfa) - automatically generates HTML report
result = analyze_symbol("600143", "CN")
# HTML report saved to: reports/600143_financial_report_YYYYMMDD_HHMMSS.html
```

### Analyze 三一重工 (Sany Heavy Industry)
```python
# Analyze 三一重工 - generates comprehensive HTML report
result = analyze_symbol("600031", "CN")
# Beautiful HTML report with charts and visualizations
```

### Analyze US Stock
```python
# Fetch and analyze Apple Inc.
result = analyze_symbol("AAPL", "US")
```

### View Generated HTML Reports
After analysis, HTML reports are automatically saved to the `reports/` directory. You can:

1. Start a local server to view reports:
```bash
python -m http.server 8080
```

2. Open in browser:
```
http://localhost:8080/reports/
```

## HTML Report Features

### 🎨 Visual Design
- **Bento Grid Layout**: Modern card-based design
- **Tesla Red Theme**: Professional color scheme (#E31937)
- **Typography**: Large impact numbers with Inter font
- **Bilingual**: Chinese-English mixed layout

### 📊 Data Visualization
- **Risk Assessment Radar Chart**: 5-dimension risk analysis
- **Industry Position Bars**: Market position indicators  
- **Financial Metrics Cards**: Key performance indicators
- **Interactive Elements**: Hover effects and animations

### 📱 Responsive Design
- **Mobile Optimized**: Perfect on all screen sizes
- **Smooth Animations**: Apple-style scroll effects
- **Touch Friendly**: Optimized for mobile interaction

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│  FinResearch     │───▶│   Data Sources  │
│                 │    │  MCP Server      │    │                 │
│ - Claude        │    │                  │    │ - EDGAR (US)    │
│ - Other clients │    │ - Report Fetcher │    │ - Sina Finance  │
│                 │    │ - Text Extractor │    │ - Custom URLs   │
│                 │    │ - CN Analyzer    │    │                 │
│                 │    │ - HTML Generator │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  HTML Reports   │
                       │                 │
                       │ - Bento Grid    │
                       │ - Charts        │
                       │ - Responsive    │
                       │ - Interactive   │
                       └─────────────────┘
```

## Supported Markets

- **US Market**: EDGAR SEC filings for US public companies
- **Chinese A-Share Market**: Shanghai/Shenzhen Stock Exchange with specialized analysis
- **Custom URLs**: Direct analysis of any accessible financial document

## File Structure

```
FinResearch-MCP-Server/
├── main.py                 # MCP server entry point
├── modules/
│   ├── scraper.py         # Data fetching from various sources
│   ├── parser.py          # Text extraction from documents
│   ├── analysis.py        # Main analysis orchestrator
│   ├── cn_analyzer.py     # Chinese A-share specialized analyzer
│   └── html_generator.py  # HTML report generation
├── reports/               # Generated HTML reports (auto-created)
└── README.md
```

## License

MIT License