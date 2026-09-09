# FDE 岗位需求基线

核验日期：2026-09-08。目的：把有限招聘证据映射为可交付方法，不把职位描述当成市场规模、客户付费或特定技术选型的证明。

## 样本与限制

- 用户提供 10 张 BOSS 直聘局部截图；两组逐字节重复，得到 8 张唯一图片。原图留在用户私有项目，不进入本仓库。
- 公开一手补证来自当日可访问的 OpenAI、Anthropic、Scale AI 招聘页。
- 这是有日期的定性样本，不是全市场统计；岗位会变化，企业、行业和地区要求也不同。

## 稳定共性

| 能力门 | 要解决的问题 | 应留下的证据 | 对应 Skill |
|---|---|---|---|
| 场景与价值 | 谁的哪段流程值得做，为什么 | 基线、替代方案、价值假设、GO/NARROW/NO_GO | `fde-discovery` |
| 范围与协同 | 谁决定、谁使用、谁维护，原型到生产如何分界 | owner、非目标、验收、节奏和决策权 | `fde-discovery` |
| 架构与集成 | 数据、API、身份、权限、企业系统和异常如何连接 | 集成契约、数据流、写入副作用、恢复路径 | `fde-connector-preflight` |
| 亲手交付 | 是否能把模糊需求做成可检查的端到端纵切片 | 版本化成果、差异、测试和失败记录 | `fde-delivery` |
| AI 评测 | 输出、规则、工具调用和任务完成是否可靠 | 固定样本、阈值、通过率、严重错误、延迟、成本、安全 | `fde-eval-release` |
| 上线与运行 | 是否能部署、观测、恢复并长期维护 | 环境回读、告警、人工接管、运行 owner、回滚 | `fde-eval-release` |
| 采用与价值 | 用户是否真的用，流程是否改善 | 采用分母、实际用量、效率/错误/人工变化及限制 | `fde-eval-release` |
| 复用与产品反馈 | 哪些是模式，哪些只是客户特例 | 前提、失败边界、第二案例证据、产品缺口 | `fde-handoff-cleanup` |

OpenAI 的当前 FDE 岗位把 discovery、technical scoping、system design、build 和 production rollout 串成端到端责任，并以生产采用、可量化流程影响和评测驱动的产品/模型反馈衡量成功；还要求直接写生产级代码并把有效模式沉淀为工具或 playbook。[OpenAI FDE](https://openai.com/careers/forward-deployed-engineer-%28fde%29-sf-san-francisco/)

Anthropic 的当前岗位要求在客户系统内构建生产应用，交付 MCP server、sub-agent、agent skill 等技术资产，支持企业部署，沉淀重复模式并反馈产品，同时强调安全、可靠性、客户发现和跨组织协作。[Anthropic FDE](https://job-boards.greenhouse.io/anthropic/jobs/5302966008)

Scale AI 的公开岗位进一步强调全栈数据/云集成、快速实验、评测、guardrail、可观测性、运行反馈与业务影响，说明“原型能跑”只是中间状态。[Scale AI FDE](https://scale.com/careers/4593571005) [Scale AI Frontier Agents FDE](https://scale.com/careers/4694863005)

## 对工具箱的约束

1. 保持五个阶段 Skill，不用更多 Agent 数量冒充能力完整。
2. 领域知识、企业规则、连接器和生产配置进入具体项目，不进入通用仓库。
3. RAG、本体、知识图谱、MCP、向量数据库或多 Agent 只是候选技术，不是默认答案。
4. 每个项目必须分开报告本地产物、测试环境、生产回读、用户采用和商业结果。
5. 单一客户成功不能直接标准化；至少保存复用前提、失败边界和第二场景证据。

## 本版增强

- `SCENARIO_CARD.md` 增加基线分母、决策角色、原型/生产边界和采用指标。
- `INTEGRATION_CONTRACT.md` 固化企业系统、数据、权限、失败和恢复契约。
- `EVAL_RELEASE_SCORECARD.md` 统一质量、工具、任务、延迟、成本、安全、人工和采用评测。
- `REUSE_FEEDBACK.md` 区分客户特例、可复用模式与产品缺口。

这些模板缩短启动和交接时间，但不能替代领域访谈、真实工程、宿主权限、生产运维或独立验收。
