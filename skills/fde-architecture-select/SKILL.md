---
name: fde-architecture-select
description: Use when a scoped FDE project needs architecture selection across workflow, Agent, RAG, tools, memory or recovery, or a concrete implementation handoff from case knowledge. Not for executing deployments or replacing domain-specific strategy.
---

# 项目架构选型与实施交接

输入：当前项目目标、已知数据/权限/系统、现有方案与验收要求。业务目标未明确时先用 fde-discovery；目标清楚后本技能只补技术选型，不重新发明项目总控。

## 定位参考

仓库阅读模式从本技能目录访问 [架构目录](../../docs/fde-case-delivery-foundation/architecture/README.md)。项目级安装后，技能文件可能单独复制：先读取项目 `.fde/toolbox-lock.json` 的 `bundle_root`，相对项目根目录解析，在该已核验副本内读取同名 `docs/fde-case-delivery-foundation/architecture/README.md`，不要臆造相对路径或重新安装。共享包不可读时明确阻塞，仅给条件方案，不虚构已读取内容。

## 选择步骤

1. 先区分固定规则、已有知识查询、实时状态和真正动态决策。稳定文档、实时业务状态、有副作用动作分开建模。为每项未知事实标 `UNKNOWN`，不能把客户愿望当已具备能力。
2. 读取架构 catalog.json 的触发/排除条件，选一个最小主模式和有理由的补充模块。记录未选的复杂方案及原因；固定报表可只用公式/脚本，允许“不需要新架构”。只读选中卡片；具体原理/参数有疑问再查知识手册相应章节。
3. 每项选择绑定已核对的项目事实、模式 ID、来源/候选状态、组件输入输出和失败方式。视频阈值不是项目默认，厂商接口/版本/兼容性须实施前核查。已有领域技能负责站点、增长、广告的业务规则，不因提到“独立站”就选建站技能。
4. 填写 [架构选择与部署交接单](../../docs/fde-case-delivery-foundation/templates/architecture-selection.md)（安装模式从 bundle_root 读取）。列主方案、能力损失不同的备用、切换条件、人工接管；每个有副作用步骤区分提交、结果未知和确认，给出恢复办法。无生产授权时仅交付本地草稿/隔离验证计划。
5. 交给 fde-connector-preflight 核查访问与接口，fde-delivery 完成获准的纵向切片，fde-eval-release 验证，fde-handoff-cleanup 留恢复入口。技能选择不是自动授权；本工具包没有生产执行器，现有项目授权与控制面始终优先。

完成条件：选型交接单中有采用与排除理由、组件/数据契约、主备切换、状态恢复、可执行验收用例、权限缺口、版本与事实来源。文件状态为 `DRAFT` 或 `READY_FOR_PREFLIGHT`，不是已部署。检查模板中的未知项是否阻断具体下一步，避免用一个未知项暂停所有安全工作。

常见误选：实时库存放旧知识索引；把 JSON Schema 当鉴权；把示例配置直接部署；复制来源演示代码却没有测试；看到多个任务就拆多 Agent。对应动作分别是源系统读回、真实权限控制、项目校准、隔离验证、先评估固定依赖图。
