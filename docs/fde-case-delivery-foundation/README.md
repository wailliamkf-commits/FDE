# FDE 案例驱动交付基础包 · 0.2.0

标识：`fde-case-delivery-foundation`。类型：**reference_pack**，不是执行器或自动方案生成服务。仓库另提供 `fde-architecture-select` 原生技能入口，负责读取本包进行选型，安装与宿主调用仍需单独验证。

新增 [架构与实现工具包](architecture/README.md)：10 张模式卡、精炼知识、61 视频来源索引与 [部署交接单](templates/architecture-selection.md)。先按需求选一个主模式，按实际依赖组合；不默认加载全库或自动部署。

从 Datawhale 第一期 24 个案例提炼需求诊断与交付方法；后续导图、视频、官方文档作为有出处的增量资料进入，不改变已有项目授权。

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

## 与现有技能的分工

| 环节 | 使用现有技能 | 基础包提供 |
|---|---|---|
| 场景与根因 | fde-discovery | 案例、假设与主备方案模板 |
| 架构选型 | fde-architecture-select | 组件数据流、字段状态、实现次序与主备路径 |
| 接口权限 | fde-connector-preflight | 数据、权限和降级问题 |
| 实现 | fde-delivery | 已冻结的范围与输出契约 |
| 检验 | fde-eval-release | 基线、验收与放行证据 |
| 交接 | fde-handoff-cleanup | 复用项、回访与来源变更记录 |

安全以仓库 [SECURITY.md](../../SECURITY.md) 为准。本包没有网络调用、安装钩子、付费API或生产写入代码。
