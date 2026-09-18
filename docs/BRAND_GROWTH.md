# 品牌增长方法 v0.3.0

目标：从「买到更多点击」升级为「持续获得可服务、有需求、能产生可持续贡献的人群」。本模块作为FDE的业务分析能力，使用 `skills/fde-brand-growth/SKILL.md`；独立于现有通用交付流程，不重建FDE，也不要求安装多个常驻Agent。

## 从第一轮项目到通用方法

起点是Dazuma双账户付费漏斗复盘：补齐原始报表、修正第三方推断、下钻搜索词/商品/页面，再结合会议形成系列承接、腰部商品、内容协作和实验记录。
通用化后，需求证据可以来自广告、自然搜索、社媒、客户、销售、伙伴或平台。零到一可以从任何有证据且可负担的路径启动；本版不讨论GEO的替代比例。

需要修正原构想的一点：业务差异不仅是类目和国家，还包括零售/询盘模式、购买周期、客单价与贡献、供给、现金和团队能力。这些一起决定流量质量和验证窗口。

## 核心路线

需求发现 → 市场验证 → 最小承接 → 用户行为验证 → 商业价值验证 → 资产建设 → 多渠道复用 → 品牌资产增长 → 稳定性监控 → 反馈需求。

需求验证、资产建设、监控纠偏三个循环共同运行。十步是工作流程，下面的S0—S4是需求单元的证据成熟阶段；一个项目不必每次从头执行。完整门槛与交接见 [闭环架构](../skills/fde-brand-growth/references/growth-loop.md)。

| 阶段 | 当前任务 | 看什么 | 下阶段凭什么进入 |
|---|---|---|---|
| S0 市场探索 | 找到明确问题与人群 | 真实需求、相关响应、可服务性、验证成本 | 明确需求-方案和成交试验路径 |
| S1 成交验证 | 找有效渠道-商品-页面组合 | 去重购买/合格商机、成熟周期、贡献 | 有重复证据且损失和供给可控 |
| S2 扩量 | 获取更多有效需求 | 边际获客成本、增量贡献、现金和履约 | 多周期结果和扩量试验 |
| S3 资产 | 把有效需求变成持续可用能力 | 页面/内容/客户关系的使用、成本和成熟结果 | 跨批次持续复用，关联不冒充因果 |
| S4 稳定经营 | 降低关键依赖与波动 | 集中度、贡献、回本、压力情境与恢复能力 | 持续复核，随证据降级或重测 |

详细阶段条件见Skill的 `references/stages.md`。这些是决策阶段，不是品牌年龄等级；一个品牌不同业务可以处于不同阶段。

## 怎样得到更好的流量

先定位缺量还是质量、匹配、承接、商业经济或供给的瓶颈。优先修复现有需求中可挽回的错配，再扩已经验证的组合，然后验证邻近需求/渠道/国家。每次扩大都看新增贡献与风险，不用平均ROAS掩盖边际变差。

渠道任务分为发现/教育、捕获需求、验证信任、成交和持续关系。品牌词或再营销可能承接已有需求；自然流量需要内容和时间投入。渠道的归因回报不等于增量作用。

## 一份复盘怎样落到动作

最小产出是：一个需求单元、一个有来源的约束判断、一个可区分替代解释的实验、一张具体页面/商品/渠道行动单、一个复盘日期。不是要求填完所有表格。

会议提出的系列页、集合页首排、商品分层、季节性、B2B、Feed、否词、支付流失、跨部门协作已映射到技能参考文件。固定月度款数、预算百分比、户外占比和页面删除数量均保留为项目参数，不能写成通用硬规则。

每周看成熟需求单元和上周实验；每月看商业贡献、资产与阶段；每季看集中度和新需求。日常先监测费用、追踪和可售/支付异常。

## v0.2.0 闭环基础

增加最小承接与长期资产的投资区分，以demand_id串联证据、实验、页面商品与商业结果；把反馈记录作为闭环结束条件。补齐页面/商品治理、首次异常排查、快照回补、季节覆盖和反证机制。历史项目固定数量与预算比例不升格为通用规则。

现有fde-brand-growth负责需求与商业决策；google-ads-diagnostics和meta-ads-diagnostics负责渠道专项；fde-brand-site负责页面体验与实现。使用实际可用技能，交接同一需求与实验记录，不重复造另一套平台。

升级兼容：保留原有技能名、S0—S4、单组快照输入契约与脚本行为。业务配置和实验空模板增加可选字段，旧项目按需要补齐；新增Markdown工作表由Agent填写，不是自动状态机或新的执行器。已有安装锁不自动升级。

## v0.3.0 研究与协作补充

新增四类研究证据、竞品假设验证、产品×场景×服务映射，以及广告—SEO—网站—销售交接。补齐促销一致性、移动端闭环、定制商机处理和组织等待时间；明确会议来源去重及不采用的经验断言。详见 [本次转化与验证](GROWTH_MEETING_UPGRADE.md)，使用 [研究到行动工作表](../skills/fde-brand-growth/assets/research-to-action.md)。不改变既有脚本与输入协议。

## 内容入口

- [闭环与交接](../skills/fde-brand-growth/references/growth-loop.md)、[需求档案](../skills/fde-brand-growth/assets/demand-record.md)：十步、三个循环、阶段监测与技能协作。
- [经营治理](../skills/fde-brand-growth/references/operating-governance.md)、[治理追踪表](../skills/fde-brand-growth/assets/governance-workpad.md)：排序、清退、责任和成效。
- [监控反馈](../skills/fde-brand-growth/references/monitoring-feedback.md)：异常、回补、季节与日周月动作。
- [技能入口](../skills/fde-brand-growth/SKILL.md)：运行顺序、输入缺口、成果和完成标准。
- [数据与指标](../skills/fde-brand-growth/references/measurement.md)：来源、归因、去重、指标定义和补数清单。
- [流量获取](../skills/fde-brand-growth/references/acquisition.md)：渠道任务、约束诊断、优先顺序。
- [页面与商品](../skills/fde-brand-growth/references/intent-page.md)：需求映射、商品排查、会议操作的可复用版本。
- [实验](../skills/fde-brand-growth/references/experiments.md)：控制、样本/周期、预算和停止条件。
- [资产与治理](../skills/fde-brand-growth/references/assets.md)：角色协同、账本与迭代。
- [案例与反例](../skills/fde-brand-growth/references/case-lessons.md)：从历史错误推导的回归题。
- [离线检查](../skills/fde-brand-growth/references/offline-audit.md)：单组规范化输入与执行限制。
- [复盘模板](../skills/fde-brand-growth/assets/review.md)、[业务配置](../skills/fde-brand-growth/assets/business-profile.json)、[实验模板](../skills/fde-brand-growth/assets/experiment.json)。

## 验证与使用边界

先按FDE根目录规则核对完整性并审阅脚本，再执行：

```sh
python3 -I -B skills/fde-brand-growth/scripts/audit_snapshot.py skills/fde-brand-growth/assets/snapshot.synthetic.json
python3 -B -m unittest discover -s tests -v
```

合成输入用于验证计算与失败分支，不证明Dazuma或任何真实客户的效果。脚本不读取广告后台、不计算跨平台增量、不自动输出投放建议。真实数据分析依赖项目资料和Skill判断；下一次Dazuma使用应先复核原始报表和缺失的结账/贡献数据。

FDE仓库只保存方法、空模板和合成测试；真实项目配置和账本留在各自工作区。安装不在本次交付范围，仓库存在不等于宿主已发现技能。

本轮验证范围见 [验证记录](GROWTH_VALIDATION.md)。

## 后续迭代

先运行一个真实需求单元的完整闭环，等成熟结果验证诊断，再在另一需求/商业模式复用。只有这些实践暴露的通用缺陷才升级规则。连接器、自动报表和新流量来源逐步接入已有契约，避免先造大平台再找用途。
