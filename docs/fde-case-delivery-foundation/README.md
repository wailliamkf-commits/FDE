# FDE 案例驱动交付基础包 · 0.2.0

标识：`fde-case-delivery-foundation`。类型：**reference_pack**，不是第十个原生 Skill、执行器或自动方案生成服务。

从 Datawhale 第一期 24 个案例提炼需求诊断与交付方法；后续导图、视频、官方文档作为有出处的增量资料进入，不改变已有项目授权。

本版增加 133 份历史视频报告版本的脱敏方法索引；对应 123 个来源路径，包含 10 个同名替换版，不包含旧 61 条批次。132 条提供方法或反例，122 仅保留排除记录。所有视频来源均为 `visual_only` 历史文字证据；覆盖不等于逐条事实验证，详见 [视频证据边界](video-evidence.md)。

## 最短使用路径

给执行者一段需求，附上这个入口；无需先安装。先使用现有 `fde-discovery` 判断范围，按 [方法与技术选择](method.md) 选择一条最小路径，填写 [交付方案工作表](templates/delivery-plan.md)。仅在需要案例时查询 [24案索引](cases.json)。

输入可以简短，但业务目标、数据可得性、权限、预算与验收未知时，输出只能是条件方案。先提出会改变方案的关键问题，不编造客户事实。

输出必须含：根因假设、证据与缺口、主方案、低依赖备用方案、人工兜底、切换条件、验证方法、责任人和价值回访。

## 文件与适用场景

- [来源与证据边界](sources.md)：核对版本、页码、效果数字、权利和事实/推断区分。
- [方法与技术选择](method.md)：业务诊断、非AI优先、技术组合与交付门槛。
- [方案工作表](templates/delivery-plan.md)：首次需求到主备方案与可交付输出。
- [验收与价值工作表](templates/acceptance-value.md)：基线、安全、成本、采用、输出兼容和回访。
- [知识补充工作表](templates/knowledge-intake.md)：新增来源或纠正旧结论。
- [补充与版本规则](updates.md)：来源去重、冲突、过期、模型无关的知识更新。
- [合成示例](example.md)：库存异常只读试点，不是真实客户项目。
- [人工演练清单](evaluation.md)：能力边界测试；未执行的宿主/业务验证显式保留。
- [133条覆盖索引](source-coverage.json)：按 `new-video-NNN`、主题、来源哈希查方法路径、冲突和同名替换关系。
- [选词与页面归属](video-keywords.md)：采购意图、工具口径、竞争缺口、聚类与疑似蚕食。
- [页面架构与内容生产](video-architecture-content.md)：Page Spec、页面模块、六类内容模板、证据审稿、补丁链、多语言。
- [技术SEO与CMS实操](video-technical-search.md)：索引、HTTP、图片、插件迁移、表单、国际化与抓取回退。
- [测量、渠道与GEO](video-distribution-measurement.md)：多源报表、询盘、外链审计、实体知识、AI引用与Discover口径。
- [Agent与企业知识系统架构](agent-knowledge-architecture.md)：知识治理、权限检索、长任务接续、共享知识及成本门槛。

独立站任务由现有 `fde-brand-site` / `fde-brand-growth` 按问题读取相应章节；需要原报告时，用 ID 与报告哈希向有权保管资料的人定位。本包不分发私人报告、媒体、客户案例数据或账户配置。

## 与现有技能的分工

| 环节 | 使用现有技能 | 基础包提供 |
|---|---|---|
| 场景与根因 | fde-discovery | 案例、假设与主备方案模板 |
| 接口权限 | fde-connector-preflight | 数据、权限和降级问题 |
| 实现 | fde-delivery | 已冻结的范围与输出契约 |
| 检验 | fde-eval-release | 基线、验收与放行证据 |
| 交接 | fde-handoff-cleanup | 复用项、回访与来源变更记录 |

安全以仓库 [SECURITY.md](../../SECURITY.md) 为准。本包没有网络调用、安装钩子、付费API或生产写入代码。
