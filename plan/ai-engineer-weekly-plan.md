# AI 工程师转型 · 52 周执行表

> 起点：2026-10-19（周一）｜结束：2027-10-11
> 强度：每周 ~10h｜适用：软件工程师转型 → AI 全栈/独立开发
> 配套：[ai-engineer-plan.md](./ai-engineer-plan.md)（判断依据与取舍理由）

## 使用说明

| 规则 | 说明 |
|---|---|
| **红线** | 任何一周没有 git commit，那一周记 0 分，下周必须先补 |
| **缓冲周** | 标 ⏸ 的周是缓冲/追账周，不是假期。没欠账就往下一阶段推进 |
| **并行轨** | 数学/ML 从 W6 起每周固定 2h，独立进度，见文末并行表 |
| **跳过权** | 如果你已掌握某周内容，做完验收题就跳过，把时间还给缓冲 |
| **链接** | 部分外链可能失效（原 repo 已过时）。404 就搜替代品，别卡住 |

每周默认时间分配：**3h 输入（周末整块）+ 5h 写代码（工作日碎片，天天碰）+ 2h 项目/复盘**

---

## Phase 0 · 环境与 Python 手感（W1–W2）

你不需要再学 OOP 和 Git。这两周只补"工程师转 Python AI"的实际缺口。

| 周 | 日期 | 主题 | 输入 | 动手 | 完成标准（可验证） |
|---|---|---|---|---|---|
| W1 | 10-19 | 现代 Python 工具链 | [uv 文档](https://docs.astral.sh/uv/)；[Pydantic 教程](https://docs.pydantic.dev/)；Python 类型注解、`asyncio` 基础 | 用 `uv init` 建项目，`typer` 写一个 CLI：批量整理指定目录文件（按扩展名/日期归档），配置用 pydantic 校验 | ✅ CLI 能跑，`uv run` 一键启动<br>✅ 配置错误时有清晰报错<br>✅ README 有安装+用法<br>✅ 已推 GitHub |
| W2 | 10-26 | 数据手感 | [Kaggle Learn: Pandas](https://www.kaggle.com/learn/pandas)（1–5 节）；[Numpy 快速入门](https://numpy.org/doc/stable/user/quickstart.html)；配好本地 Jupyter / Colab | 找一个感兴趣的真实 CSV（Kaggle 或自己的数据），做 10 个探索性分析并写下 5 条发现 | ✅ 熟练 `.groupby/.merge/.apply`<br>✅ 能不查文档写出 shape/dtype 检查<br>✅ 分析笔记公开（notebook 或博客） |

---

## Phase 1 · LLM 应用开发（W3–W11，9 周）

**这是你真正入门的地方。** 目标不是"会用 API"，而是"能交付一个带评测、控成本、可上线的 LLM 功能"。

| 周 | 日期 | 主题 | 输入 | 动手 | 完成标准 |
|---|---|---|---|---|---|
| W3 | 11-02 | API 与结构化输出 | [OpenAI 平台文档](https://platform.openai.com/docs/overview) 或 [Claude 文档](https://docs.claude.com/)；structured output / JSON mode 章节 | 写一个"非结构化文本 → 结构化 JSON"的工具（如：招聘 JD → 技能/年限/薪资字段），要求 schema 校验失败自动重试一次 | ✅ 能稳定产出符合 schema 的 JSON<br>✅ 理解 temperature / max_tokens 取舍<br>✅ 有 10 条以上输入输出样本存档 |
| W4 | 11-09 | Prompt 工程（工程视角） | [Anthropic Prompt Engineering 指南](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)；原 repo `03_modern-Ai/04_prompt-engineering.md` | 把 W3 工具重做三版 prompt（朴素 / few-shot / CoT+系统提示），人工对比 20 条输出差异，写成对比表 | ✅ 能说出每版改动的**原因**而非"感觉更好"<br>✅ 对比表有具体 bad case 举例<br>✅ prompt 已版本化管理（不放代码里） |
| W5 | 11-16 | 原理：Transformer 到底在干嘛 | [Karpathy: Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html) 第 1–4 集；[The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) | 手写一个极简 self-attention（numpy，50 行内），跑通一个 3 token 的例子 | ✅ 能解释 Q/K/V 与 attention score 计算<br>✅ 能说清 token ≠ 字符、上下文窗口的实际约束<br>✅ 代码已提交 |
| W6 | 11-23 | Tool use / Function calling | 官方文档 function calling 章节；[Toolformer 论文](https://arxiv.org/abs/2302.04761)（只读摘要+图 1） | 给 W3 工具接 2 个真实外部工具（如：网页抓取 + 计算器），让模型自己决定调不调 | ✅ 模型能正确选择"调/不调"<br>✅ 工具报错时能优雅降级不崩溃<br>✅ 并行轨：数学启动（见并行表 M1） |
| W7 | 11-30 | **Eval（一）：建评测集** | 原 repo 完全缺失这块。[promptfoo](https://www.promptfoo.dev/docs/intro/) 了解思路即可，**先手写** | 为 W3 工具建 30 条评测集（含 5 条故意刁难的 edge case），写断言式打分脚本，一条命令跑出通过率 | ✅ 30 条 case 覆盖正常/边界/对抗<br>✅ 打分脚本可重复运行<br>✅ **能报出当前准确率数字** |
| W8 | 12-07 | **Eval（二）：让它指导迭代** | LLM-as-judge 方法（Anthropic / OpenAI cookbook 搜 "evaluation"）；注意 judge 本身也有偏差 | 改一版 prompt，跑 eval 对比前后数字。**必须出现至少一次"改动让分数下降"并回滚**——这是关键体验 | ✅ 有 before/after 分数对比<br>✅ 至少 1 次"改坏并回滚"记录<br>✅ 评测纳入 git，改动 PR 都跑 |
| W9 | 12-14 | 成本、流式与可靠性 | token 计费与 counting；streaming 实现；超时/重试/限流退避 | 给工具加：token 统计与单次成本打印、流式输出、指数退避重试、主模型失败切备用模型 | ✅ 能算出每千次调用多少钱<br>✅ 模拟 429/500 时系统不崩<br>✅ 有 fallback 生效的日志证据 |
| W10 | 12-21 | **项目 ① 完成** | 自选 | 做一个"你或同事真的会用"的小工具（推荐：会议纪要/群聊 → 结构化 TODO + 负责人 + 截止时间） | ✅ README（问题/用法/局限）<br>✅ eval 脚本 + 通过率<br>✅ Gradio 或 Streamlit demo<br>✅ **公开链接可访问** |
| W11 | 12-28 | ⏸ 缓冲 / 项目 ① 打磨 | — | 追账；给项目 ① 补测试、写第一篇技术博客讲踩坑 | ✅ 无欠账<br>✅ 一篇 ≥800 字复盘公开 |

> 🎯 **阶段出口检查**（W11 结束时）：你有 1 个公开可访问、带 eval、带成本控制的 LLM 工具。
> 做不到就别往下走——RAG 只是给这个工具加个外挂知识库。

---

## Phase 2 · RAG 检索增强（W12–W18，7 周）

**核心纪律：先手写再上框架。** 跳过手写直接 LangChain，你会不知道框架替你做了哪些坏决定。

| 周 | 日期 | 主题 | 输入 | 动手 | 完成标准 |
|---|---|---|---|---|---|
| W12 | 01-04 | 手写最小 RAG | 原 repo `03_modern-Ai/03_rag.md`；embedding API 文档 | **不用任何框架**：切块 → embedding → 内存/文件暴力相似度检索 → 拼 prompt → 生成。控制在 150 行内 | ✅ 能回答"只有你的文档才知道"的问题<br>✅ 能打印出被检索到的原文片段<br>✅ 体验到"检索错了就全错" |
| W13 | 01-11 | Chunking 实验 | 搜 "chunking strategies RAG"；固定 vs 语义 vs 滑窗重叠 | 同一份文档跑 3 种切块策略，用 W7 的 eval 方法量化命中率差异 | ✅ 有 3 种策略的量化对比<br>✅ 能说出你这份数据适合的块大小及**原因** |
| W14 | 01-18 | 向量库选型与落地 | [pgvector](https://github.com/pgvector/pgvector)（你有 SQL 底子，这是优势）或 [Chroma](https://docs.trychroma.com/) | 把 W12 的内存检索换成真实向量库，灌入 ≥1000 个片段，测查询延迟 | ✅ 检索延迟 <100ms（1k 量级）<br>✅ 有建索引/重建的数据迁移脚本<br>✅ 持久化后重启不丢 |
| W15 | 01-25 | 检索质量：Hybrid + Rerank | BM25 关键词检索；hybrid search；reranker（Cohere / bge-reranker） | 加关键词检索并与向量检索融合（RRF），再加一层 rerank，用 eval 量化提升 | ✅ 三种检索方式的量化对比<br>✅ 能举出"纯向量检索失败、hybrid 救回"的真实 case |
| W16 | 02-01 | 项目 ② 启动：垂直数据 | — | 选定一个你有独家数据的领域（个人笔记/公司文档/某细分行业资料），定义 20 个真实用户问题 | ✅ 数据源确定且可获取<br>✅ 20 个问题写下来（这些就是你的评测集）<br>✅ 项目仓库建立 |
| W17 | 02-08 | 项目 ② 实现 | — | 完整 RAG 管线 + 引用溯源（回答必须标出来源片段，能点开） | ✅ 回答带来源引用<br>✅ 20 个问题里 ≥15 个答对<br>✅ 明确处理"文档里没有"时不瞎编 |
| W18 | 02-15 | ⏸ 缓冲 / 项目 ② 上线 | — | 追账；部署 demo；写第二篇博客（讲 RAG 里最反直觉的一个发现） | ✅ 公开可访问<br>✅ 无欠账 |

> 🎯 **阶段出口检查**：一个基于你独家数据、有引用溯源、能量化准确率的 RAG 产品。

---

## Phase 3 · Agent 智能体（W19–W25，7 周）

**跳过 Auto-GPT / BabyAGI**（历史文物）。只学：tool 循环、规划、memory、错误恢复。

| 周 | 日期 | 主题 | 输入 | 动手 | 完成标准 |
|---|---|---|---|---|---|
| W19 | 02-22 | 手写 ReAct 循环 | [ReAct 论文](https://arxiv.org/abs/2210.03629)（读摘要+示例）；原 repo `02_agentic-ai.md` 第 1–2 节 | 不用框架，写一个 while 循环：思考→调工具→观察→再思考，最多 N 步，有终止条件 | ✅ 能完成一个需要 2–3 次工具调用的任务<br>✅ 有步数上限和死循环保护<br>✅ 完整 trace 可打印 |
| W20 | 03-01 | 工具工程化 | [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 给 agent 的工具加：参数校验、超时、错误信息对模型友好、幂等保证、危险操作二次确认 | ✅ 工具返回的错误模型能读懂并自我纠正<br>✅ 有"模型自己修好参数后重试成功"的证据<br>✅ 危险操作有人工确认闸门 |
| W21 | 03-08 | 框架选型（只选一个） | [LangChain](https://docs.langchain.com/) 或 [LlamaIndex](https://docs.llamaindex.ai/) 二选一，**别都学** | 用框架重写 W19 的 agent，对比手写版的差异，写下"框架替我做了什么、我失去了什么" | ✅ 能列出 ≥3 个框架的隐性决定<br>✅ 能说出什么场景你宁愿手写 |
| W22 | 03-15 | Memory 与状态 | 短期/长期记忆；对话压缩；外部状态存储 | 给 agent 加跨会话记忆（用户偏好/历史结论），并做上下文压缩防止爆窗 | ✅ 第 10 轮对话仍能引用第 1 轮的结论<br>✅ 长对话不触发上下文超限<br>✅ 记忆可持久化、可清空 |
| W23 | 03-22 | 可观测性 | [Langfuse](https://langfuse.com/) 或 LangSmith，或自建日志 | 每一次 LLM 调用、工具调用、token 消耗全链路 trace，出问题时 5 分钟内定位到是哪一步 | ✅ 有可视化 trace 截图<br>✅ 故意制造一个 bug 并用 trace 定位<br>✅ 有异常告警（成本突增/失败率） |
| W24 | 03-29 | 安全与边界 | [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) | 对你的 agent 做 5 次 prompt injection 攻击（自己当红队），修复，再攻击 | ✅ 有攻击/修复记录<br>✅ 工具权限最小化<br>✅ 敏感数据不进日志 |
| W25 | 04-05 | ⏸ 缓冲 / 整合 | — | 追账；把 agent 能力并入项目 ② | ✅ 无欠账<br>✅ 项目 ② 具备 agent 能力 |

> 🎯 **阶段出口检查**：一个会调工具、有记忆、可观测、抗注入的 agent。

---

## Phase 4 · 部署与工程化（W26–W30，5 周）

**你的主场。** 这块对纯 AI 背景的人是短板，对你应该是加速器——如果这里卡住，说明前面基础有问题。

| 周 | 日期 | 主题 | 输入 | 动手 | 完成标准 |
|---|---|---|---|---|---|
| W26 | 04-12 | API 服务化 | [FastAPI 教程](https://fastapi.tiangolo.com/) | 把项目 ② 包成 REST API：异步、并发、健康检查、结构化错误响应 | ✅ 有 `/health` 与 OpenAPI 文档<br>✅ 并发 10 请求不串行阻塞<br>✅ 错误返回统一格式 |
| W27 | 04-19 | 容器化与部署 | Docker 基础；选一个平台（Fly.io / Railway / Hugging Face Spaces） | Dockerfile（多阶段构建、非 root 用户），部署上线，绑定自己的域名 | ✅ 一条命令本地起、线上跑<br>✅ 域名可 HTTPS 访问<br>✅ 有 CI 自动部署（GitHub Actions） |
| W28 | 04-26 | 流式与前端 | SSE / WebSocket；[Gradio](https://www.gradio.app/) 或极简 React | 前端逐字流式显示（不是转圈等完），有中断生成按钮 | ✅ 首字延迟 <1s<br>✅ 可中断<br>✅ 移动端可用 |
| W29 | 05-03 | 监控与成本治理 | 埋点、日志聚合、告警 | 上线监控：P95 延迟、失败率、每日花费；超预算自动告警/熔断 | ✅ 有真实监控面板<br>✅ 模拟流量打满时触发告警<br>✅ 知道单用户月成本 |
| W30 | 05-10 | ⏸ 缓冲 / 安全加固 | — | 追账；限流、鉴权、配额；补测试 | ✅ 无限流绕过<br>✅ 无欠账 |

> 🎯 **阶段出口检查**：系统 7×24 在线、有监控、有成本上限、有 CI/CD。**这就是"工程师"与"跑通 notebook"的分界线。**

---

## Phase 5 · Capstone A（W31–W38，8 周）

原 repo `04_capstone-project/capstone-projects.md` 的 5 个点子，**对独立开发最有价值的是 ① 和 ④**。
但更推荐：**做一个你自己愿意付费用的东西。**

| 周 | 日期 | 主题 | 动手 | 完成标准 |
|---|---|---|---|---|
| W31 | 05-17 | 选题与验证 | 列 5 个候选，用"我自己会不会每天用"筛到 1 个；找 3 个真人聊需求 | ✅ 选 1 个，写清目标用户与核心场景<br>✅ 3 段真实访谈记录<br>✅ 明确"不做"的范围 |
| W32 | 05-24 | 设计与 eval 前置 | 画架构图；**先写评测集再写实现**；定 MVP 边界 | ✅ 架构图 + 数据模型<br>✅ ≥30 条评测 case<br>✅ MVP 功能清单冻结 |
| W33–W36 | 05-31<br>06-07<br>06-14<br>06-21 | 实现（4 周） | 每周一个可演示增量，不追求完美 | ✅ 每周末有可点开的东西<br>✅ eval 通过率逐周可见地上升<br>✅ 持续 commit |
| W37 | 06-28 | 部署 + 文档 | 上线、README、使用示例 | ✅ 公开可访问<br>✅ 陌生人能照 README 跑起来 |
| W38 | 07-05 | 发布与反馈 | 发到 3 个渠道（社群/论坛/X），找 ≥5 个真人试用 | ✅ ≥5 份真实反馈<br>✅ 有 1 个人表示"会继续用"<br>✅ 复盘博客 |

---

## Phase 6 · Capstone B / 深化（W39–W47，9 周）

二选一，看你 Phase 1–5 之后缺什么：

- **路线 A（推荐给独立开发）**：第二个产品，换一个技术短板（例如从 RAG 换成 multimodal / 语音 / 本地小模型）
- **路线 B**：技术纵深——微调（LoRA/QLoRA）、推理优化（量化/vLLM）、或把 ML 并行轨升级为主轨

| 周 | 日期 | 主题 | 完成标准 |
|---|---|---|---|
| W39–W40 | 07-12<br>07-19 | 确定路线 B 选题 / 或 A 选题 | ✅ 明确目标与技术选型<br>✅ 沿用 W32 的 eval 前置纪律 |
| W41–W45 | 07-26<br>08-02<br>08-09<br>08-16<br>08-23 | 执行（5 周） | ✅ 每周可演示增量<br>✅ 有量化结果（准确率/延迟/成本其中至少两项） |
| W46 | 08-30 | 部署与文档 | ✅ 公开可访问 |
| W47 | 09-06 | ⏸ 缓冲 / 大缓冲周（消化前面所有欠账） | ✅ 无欠账 |

---

## Phase 7 · 收尾与输出（W48–W52，5 周）

| 周 | 日期 | 主题 | 完成标准 |
|---|---|---|---|
| W48 | 09-13 | 作品集整理 | ✅ GitHub profile 有 3 个置顶项目，每个有 demo 链接+架构说明 |
| W49 | 09-20 | 简历 / 个人站 | ✅ 一页个人站：项目 + 技术栈 + 联系方式<br>✅ 简历用"量化结果"而非"熟悉 XX"表述 |
| W50 | 09-27 | 技术输出 | ✅ ≥4 篇技术文章（复用 W11/W18/W38 的复盘）<br>✅ 至少 1 次公开分享或给开源项目提 PR |
| W51 | 10-04 | 补短板（针对目标岗位查漏） | ✅ 列出还缺的能力并排优先级 |
| W52 | 10-11 | 全年复盘 + 下一轮规划 | ✅ 一份年度复盘公开<br>✅ 下一年计划 |

---

## 并行轨 · 数学与 ML（W6 起，每周固定 2h）

**不要先学 6 周数学再碰模型。** 做项目卡在哪补哪。这 2h 从每周 10h 里切，不额外加。

| 里程碑 | 建议区间 | 内容 | 完成标准 |
|---|---|---|---|
| M1 | W6–W9 | [3Blue1Brown 线性代数本质](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab) 第 1–9 集 | ✅ 能解释矩阵乘法、特征值、向量空间直觉<br>✅ 能看懂 embedding 的几何含义 |
| M2 | W10–W13 | [Khan Academy 概率统计](https://www.khanacademy.org/math/statistics-probability) 选看：分布、贝叶斯、假设检验 | ✅ 做 eval 时能判断"这个提升是显著还是噪声" |
| M3 | W14–W18 | 微积分：导数、链式法则、梯度（[Khan Academy](https://www.khanacademy.org/math/calculus-1) 或 Imperial 的 Coursera 课） | ✅ 能手推线性回归的梯度下降 |
| M4 | W19–W24 | [Kaggle Learn: Intro to ML](https://www.kaggle.com/learn/intro-to-machine-learning) + [Intermediate ML](https://www.kaggle.com/learn/intermediate-machine-learning) | ✅ 一个完整 sklearn 项目（不是 notebook 抄一遍） |
| M5 | W25–W34 | [fast.ai Practical Deep Learning](https://course.fast.ai/) 前 4 课 | ✅ 训出一个图像/文本分类器并说清每个超参作用 |
| M6 | W35–W44 | **对比实验：sklearn 基线 vs LLM 方案** | ✅ 一篇"这个场景根本不需要 LLM"的分析——**这是真本事的体现** |

> 注：Andrew Ng 的 Stanford ML 课（Coursera）我**不建议**为转型而完整上完，对独立开发 ROI 太低。真想系统学，用 fast.ai 的自上而下路径。

---

## 追踪方式

Fork 原 repo，每个阶段建 `progress.md`，每周只记三行：

```
## W07 (11-30)
- 做了：建了 30 条 eval 集，跑了第一版，准确率 23/30
- 卡住：LLM-as-judge 打分不稳定，同一条两次分数不同
- 下周：改成分层断言，主观题才用 judge
```

**公开出来。** 10h/周 这种低强度学习，外部承诺是唯一的续命方式。

## 三个月度自检点

| 时点 | 检查 |
|---|---|
| W13（3 个月） | 有 ≥1 个公开可访问、带 eval 的 LLM 工具？没有→回到 Phase 1，别往前 |
| W26（6 个月） | 有真实用户用过你做的东西吗？（哪怕同事）没有→你一直在学，不是在交付 |
| W39（9 个月） | 能说清"这个场景为什么不该用 LLM"吗？说不清→M6 提前 |

---

## 免责与提醒

- 外链可能失效（原 repo 已过时，LangChain 文档域名迁移过、部分课程停更）。404 直接搜替代品。
- 我没有逐条验证全部外链的当前有效性，只用了知名度高、长期稳定的入口。
- 本表的周数是**带缓冲**的估算。若某阶段连续 3 周零 commit，说明强度或选题出了问题，需要重排而不是硬扛。
