# AI 工程师转型计划（软件工程师 → AI 全栈/独立开发）

基于 [AgenticAiLabs/Ai-Engineering-Roadmap](https://github.com/AgenticAiLabs/Ai-Engineering-Roadmap) 重排。
约束：已有工程能力 · 每周 <10h · 目标是能独立交付 AI 产品。

## 核心判断：这份路线图该怎么用

**用它的**：资源链接索引（大量确实是免费优质课）、模块划分。
**别信它的**：
- 阶段时长（"Python 4-6 周"是按零基础算的，你是工程师）
- "按顺序走"——独立开发需要**尽早做出能跑的东西**，数学和深度学习应该后置+按需
- 部分链接已过时/失效：LangChain 文档域名迁移过、Auto-GPT 基本停更、Cohere LLM Bootcamp 停更。遇到 404 直接搜替代品，不要卡住。

**它缺的三块，你自己必须补**（这才是"合格"与"玩具"的分界）：
1. **评测（Eval）**——没有 eval 的 AI 应用等于没有测试。这是你作为工程师最大的降维打击点。
2. **工程化**——结构化输出、重试/超时、成本控制、缓存、可观测性。路线图里几乎没有。
3. **验收标准**——原 repo 每个模块只有"Checkpoint 你应该能…"，这种自我感觉良好的清单不算验收。下面每个阶段我换成了**可交付物**。

---

## 时间轴（约 12 个月，40h/月）

### 阶段 0｜Python 生态补齐（2 周 · ~15h）
**跳过** `01_foundation/01_programming.md` 全部。你不需要再学 OOP 和 Git。

只补三件事：
- Python 与 TS/Java 的差异：列表推导、`asyncio`、类型注解、`pydantic`
- `numpy` / `pandas` 手感 —— [Kaggle Learn: Pandas](https://www.kaggle.com/learn/pandas)（~4h）
- `uv` 做环境与依赖管理（比 pip/conda 干净，工程师会舒服）

> ✅ 交付：一个用 `uv` + `pydantic` 搭的小 CLI 工具，推送到 GitHub。

### 阶段 1｜LLM 应用开发（8 周 · ~70h）← 从这里开始，不是从数学开始
**打乱原顺序**。直接跳到 `03_modern-Ai/`。理由：独立开发要的是"三个月内能做出东西"，先拿到正反馈。

- `03_modern-Ai/04_prompt-engineering.md`（1 周）—— 但别停在"技巧"层面，重点是 **structured output / function calling**
- `03_modern-Ai/01_llms.md` 第 1、2 节（2 周）—— Transformer 原理看 [Karpathy: Neural Networks Zero to Hero](https://www.youtube.com/playlist?v=VMj-3S1tku0) 前几集就够，比读论文值
- **补：Eval**（2 周，原 repo 没有）—— 搭一个最小评测集：20-50 条 case + 断言式打分 + 回归跑批
- **补：成本与可靠性**（1 周）—— token 计费、streaming、超时重试、fallback 模型

> ✅ 交付 ①：**一个带 eval 的 LLM 小工具**（比如"把乱糟糟的会议纪要转成结构化 TODO + 负责人"），有 README、有测试、有公开 demo 链接。

### 阶段 2｜RAG + Agent（10 周 · ~85h）
- `03_modern-Ai/03_rag.md`（3 周）—— 重点在 chunking 策略、embedding 选型、hybrid search、rerank。**别一上来就用 LangChain 全家桶**，先用原生 API 手写一个 100 行的 RAG，你才会知道框架在替你做什么决定。
- `03_modern-Ai/02_agentic-ai.md`（4 周）—— 只取：tool use、ReAct 循环、memory。**跳过 Auto-GPT / BabyAGI**（历史文物）。框架二选一就够，别全学。
- **补：可观测性**（1 周）—— trace 每一次 LLM 调用（LangSmith / Langfuse / 自己打日志都行）
- 去中心化的坑（2 周）—— 权限、prompt injection、PII。看 [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

> ✅ 交付 ②：**一个真正有人用的 RAG 产品**——拿你自己的笔记/文档/某个垂直领域数据做，部署上线，域名可访问。这是简历上唯一算数的东西。

### 阶段 3｜数学 + ML，按需回补（持续并行，每周 2h）
不要先学 6 周数学再碰模型。反过来：**做项目时卡在哪，补哪**。

- 线性代数：[3Blue1Brown 本质系列](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab) 前 9 集（~5h，性价比最高的一份）
- 概率统计：[Khan Academy](https://www.khanacademy.org/math/statistics-probability) 选看 —— 做 eval 时你会真的需要它
- ML 实战（4 周）：[Kaggle Learn: Intro to ML](https://www.kaggle.com/learn/intro-to-machine-learning) + [Machine Learning](https://www.kaggle.com/learn/machine-learning)。**不要**为了转型去上完 Andrew Ng 的完整课（对独立开发 ROI 太低）
- 深度学习（6 周）：[fast.ai Practical Deep Learning](https://course.fast.ai/) —— 自上而下，适合工程师

> ✅ 交付 ③：一个 sklearn 基线 vs LLM 方案的对比实验（你会经常发现"根本不需要 LLM"，这是真本事）

### 阶段 4｜部署与工程化（4 周 · ~35h）
对应 `03_modern-Ai/05_ai-tooling.md`，但按独立开发的现实重排优先级：
1. FastAPI 包一层 + Docker（1 周）
2. Hugging Face Spaces / Fly.io / Railway 选一个部署（1 周）
3. 流式响应 + 前端（1 周）——你有工程底子，这块应该最快
4. 监控与成本告警（1 周）

### 阶段 5｜Capstone 冲刺（8 周 · ~70h）
`04_capstone-project/capstone-projects.md` 里的 5 个点子里，**对独立开发最有价值的是 1 和 4**：
- ① AI Chat Assistant (RAG) —— 最贴近能变现的产品形态
- ④ AI Agent 任务自动化 —— 最容易做出"哇"效果

建议：直接做一个**你愿意自己付费用的东西**，而不是列表里的练习题。

---

## 每周节奏模板（10h）

| 时间 | 内容 |
|---|---|
| 3h | 主课/文档输入（周末整块时间） |
| 4h | **写代码**（工作日碎片，必须天天碰，哪怕 30 分钟） |
| 2h | 项目推进 / 修 bug |
| 1h | 记录 + 写一篇进度（公开，哪怕很短） |

**唯一会让你失败的原因**：看了三个月课，没提交过一行代码。
规则：**任何一周如果没有 git commit，那一周算没学。**

## 进度追踪
Fork 这个 repo，每个模块下建 `progress.md`，只记三件事：日期 / 做了什么 / 卡在哪。
公开出来——外部承诺是 10h/周 这种低强度学习唯一的续命方式。

## 三个月自检
- [ ] 有 3 个以上公开 repo，其中至少 1 个有真实用户（哪怕是你同事）
- [ ] 能说清"这个场景为什么不该用 LLM"
- [ ] 有自己写过的 eval 流程
- [ ] 完整部署过一次（域名 + 监控 + 成本控制）
做不到就说明走偏在"学"而不是"做"。
