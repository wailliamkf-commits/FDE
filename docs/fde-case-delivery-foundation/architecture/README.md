# 架构与实现知识工具包 · 0.2.0

本目录补足基础包的技术实现层：不重新做业务诊断，不执行部署。先用现有 discovery 明确问题，再按 [结构化目录](catalog.json) 选择一个主模式和必要的补充模块。只有简短需求时，可使用 `fde-architecture-select`；它产出选型与部署交接计划，不替用户批准生产动作。

## 选择入口

| 需求特征 | 主模式/补充模块 | 不应误选 |
|---|---|---|
| 字段清楚、规则固定 | [有状态工作流](patterns/workflow.md) | 不为固定任务搭多 Agent |
| 下一步依赖工具观察 | [有界 Agent](patterns/agent.md) | 工具不足不靠模型虚构 |
| 企业知识问答、文档解析 | [PDF/RAG](patterns/rag.md) | 实时库存价格另走源系统 |
| 外部系统读写 | [工具契约](patterns/tools.md) | Schema 校验不等于授权 |
| 跨会话偏好/历史 | [记忆治理](patterns/memory.md) | 精确字段不只存向量 |
| 长输入与历史膨胀 | [上下文管理](patterns/context.md) | 压缩不能改变用户约束 |
| 多步骤长任务/续跑 | [检查点恢复](patterns/recovery.md) | 未知执行结果不直接重试 |
| 多角色必要且可独立验收 | [多 Agent](patterns/multi-agent.md) | 默认仍是单执行者 |
| 已有技能很多且误选 | [Skill 路由](patterns/skill-routing.md) | 不无条件加载全库 |
| 上线前证明正确/出错排障 | [评测观测](patterns/evaluation.md) | HTTP 成功不是业务完成 |

每张卡给组件数据流、字段契约、实现次序、主备条件与测试。卡片是编辑后的工程候选，不是视频提供的可部署代码，也不是经过生产认证的架构。

## 按需读取

具体原理、示例参数及争议：[知识手册](../knowledge/agent-rag-skill.md)。按章节查询，不默认加载全文。
来源身份与覆盖：[sources.json](sources.json)；权利、时效与纠错：[来源边界](provenance.md)。
交付格式：[架构选择与部署交接单](../templates/architecture-selection.md)。
示例：[产品手册客服](examples/product-support.md)、[固定 CSV 报表](examples/csv-report.md)。
已运行检查与未验证边界：[验证记录](evaluation.md)。

与原基础包共用 [安全边界](../../../SECURITY.md)、[方法](../method.md) 和已有项目总控。领域技能（独立站、增长、广告）负责业务语义，本目录提供通用实现模块；不得取代领域规则。
