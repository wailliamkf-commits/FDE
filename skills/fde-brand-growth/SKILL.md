---
name: fde-brand-growth
description: Analyze brand acquisition quality, intent-to-page funnels, market validation, and repeatable growth across channels. Use for a brand growth review, launch experiment, scaling decision, or asset and resilience plan; not for standalone ad copy or live campaign execution.
---

# 品牌增长：从需求到可持续贡献

为一个明确的「品牌 × 市场 × 需求场景 × 商业模式」生成有证据的增长决策。渠道是取得和验证需求的路径，不预设付费、自然或新兴入口优先。交付分析、实验和页面需求；实际投放、改价、发布沿用用户对具体动作的授权。

## 执行

1. **界定决策单元。** 明确正在决定启动、修复、扩量还是稳定经营；记录零售/询盘模式、国家、类目、购买周期、资源和可承受损失。缺少信息时先标未知并完成可独立的分析。读取 [阶段与商业配置](references/stages.md)。产出阶段判断及证据，不凭品牌年龄或销售额直接定阶段。
2. **建立证据底座。** 按 [数据与指标契约](references/measurement.md) 分开账户、时间、转化动作、归因和数据粒度。每个关键判断附来源、覆盖、成熟度与反证；把事实、假设、会议决策分开。数据缺口阻止相关推论，不阻止形成补数清单和小范围实验。
3. **定位增长约束。** 读取 [诊断与流量获取](references/acquisition.md)，先比较需求、匹配、行为、商业结果和供给能力，再判断缺量、质量下降、承接或履约问题。保留至少一个竞争解释和推翻当前判断所需证据。不能把用户希望强调的原因写成已证明根因。
4. **选择对应分支。** 页面/商品问题读 [页面与商品](references/intent-page.md)；新增渠道、放量、季节性或归因争议读 [实验与预算](references/experiments.md)；长期流量和抗风险读 [资产与治理](references/assets.md)。只读取与本次决策有关的分支。
5. **给出可执行成果。** 使用 [复盘与行动模板](assets/review.md)，每项写具体对象、证据、假设、责任角色、成本/时间上限、验收与回滚条件。补数写平台、报告、字段、日期、筛选、用途；最新后台路径按当时官方文档/可见界面核对。每次先完成最能改变决策的一项实验，不强制填写全部维度。
6. **核验并交接。** 分清观察结果、归因结果和增量证明。对符合 [离线输入约定](references/offline-audit.md) 的规范化单组快照，先将工作目录设为本Skill目录，再运行 `python3 -I -B scripts/audit_snapshot.py INPUT.json`（输入使用项目中的绝对路径），输出只做口径门禁和描述计算。检查 [来源案例与反例](references/case-lessons.md) 的相关失败模式。结论状态使用 `OBSERVED / HYPOTHESIS / NEEDS_DATA / TEST / SCALE_CANDIDATE / HOLD`；测试通过不等于业务达标。

## 按需调用渠道专项

渠道专项诊断时，先检查当前可用技能：Google Ads 取数、目标口径、Search/Shopping/PMax/Demand Gen 到页面问题使用 `google-ads-diagnostics`；Meta 素材、版位、目录/表单到页面问题使用 `meta-ads-diagnostics`。只读取相关专项，不同时运行全库；未安装专项时继续本技能已有分支并说明覆盖限制，不自动安装。专项产出的证据和任务回到同一份复盘，跨平台归因收入保持分列。

## 完成标准

- 用一句话回答「现阶段怎样获得更多有商业价值的需求」，说明最主要约束和为何优先处理它。
- 每个推荐都有来源或明确标注的假设；保留数据口径附录，管理层正文用平实中文。
- 同时报告数量、匹配、购买/合格询盘、贡献及不确定性；零售与项目销售采用各自周期。
- 交付当前行动和阶段升级条件，以及实验/决策/资产记录的更新位置。真实数据放项目工作区，工具仓库只保存方法、空模板和明确合成案例。
- 不声称已接通后台、完成安装、执行投放或改善销量，除非有对应的实际回读证据。
