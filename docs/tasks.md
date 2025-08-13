## To Do
- [ ] Phase 1: 核心引擎开发
  - [ ] 抓取模块：完善 CN/US 抓取与健壮性（重试/容错/结构变更适配）
  - [ ] 文档解析模块：PDF/HTML 边界处理与单测
  - [ ] 分析模块：规则优化与风险提示模板细化（可选接入 LLM 增强）
- [ ] Phase 2: MCP 接口层
  - [ ] 错误码与返回结构统一、补充文档与示例
- [ ] Phase 3: 应用层（可选增强）
  - [ ] 提供最简 API (FastAPI) 输入股票代码输出分析结果
  - [ ] 最简 Web 界面（输入标的，展示卡片化分析）
- [ ] Phase 4: 质量与运维
  - [ ] 日志与基本单元测试
  - [ ] README 文档补充与使用说明

## Doing
- [ ] 端到端联调与本地验证（analyze_symbol 支持 URL 直连兜底）

## Done
- [x] PRD 需求梳理并保存至 docs/PRD.md
- [x] 依赖更新（httpx/tenacity/pdfminer.six/bs4/lxml/pydantic/dotenv/openai）
- [x] 模块骨架创建（modules/scraper.py / modules/parser.py / modules/analysis.py）
- [x] main.py 改造：暴露 MCP 工具与资源（fetch_latest_report / extract_text_from_pdf / analyze_text / analyze_symbol；report://{symbol}）