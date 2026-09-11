# 离线单组快照检查

入口：`python3 -I -B scripts/audit_snapshot.py INPUT.json`，路径相对本Skill。只读一个最大2MB JSON文件，在标准输出返回结果；无网络、写入、自动否词、评分或投放功能。退出码0=口径检查通过（不等于业务有效），2=输入错误，3=存在口径阻断。

接受下列精确字段，额外字段拒绝，避免将未使用的原始客户字段误认为参与分析：

- `schema_version`: 1；`evidence_type`: synthetic 或 observed（后者仍是提供者声明，不代表脚本核验原始来源）。
- `scope`: `source_id`, `account`, `demand_unit`, `period_start`, `period_end`, `timezone`, `currency`, `conversion_action`, `date_basis`, `attribution_model` 字符串；ISO日期；币种为三位大写；时区为IANA名称。`conversion_action`只有 purchase 才可计算购买ROAS；`date_basis`为 interaction_date 或 conversion_date。
- `quality`: `mature`, `same_cohort`, `deduplicated`, `exclusive_channels` 布尔值。它们是调用方需举证的声明，不能由工具推断；任何false阻断对应衍生率，保留原始计数可供复核。

  `deduplicated` 同时要求会话按规则去重，收入/费用源记录不存在重复导入或连接放大；false会阻断会话率与购买ROAS。平台分数归因仍保持平台口径，不要求将其改写为财务订单收入。`same_cohort` 表示参与同一比率的输入范围已对齐，不声称广告点击与站内会话存在逐条身份对应。
- `metrics`: `spend`, `purchase_value`, `sessions`, `intent_known_sessions`, `intent_matched_sessions`, `qualified_sessions`, `purchase_sessions`；未知用null。spend为非负数；purchase_value允许负数（已调整退款后价值），口径须在source_id指向的报告说明；其余为非负整数。
- `channels`: 互斥的 `{channel, sessions}` 数组。channel只接受 paid_search、paid_social、organic_search、organic_social、email、referral、direct、other、unknown。AI来源本版映射referral并在项目明细保留source，不制造新归因能力。缺渠道数据用null；否则合计必须等于sessions。客户复购属性、品牌查询属性不能当渠道。

脚本拒绝重复JSON键、非有限数、布尔充当数字、非法日期、超界计数和重复渠道。匹配访问/合格行为是并列维度，不强制彼此包含；只要求各自是有效会话子集。购买会话不应假设必须经过可观测加购。渠道缺失、分母0、值缺失返回null与原因，不补0。

产出：分组原样标识、描述性比率、渠道份额、口径阻断和警告；永远 `business_verdict: NOT_ASSESSED`，`source_verified: false`。无跨期比较、利润测算、自动阶段升级或增量推断。B2B与事件漏斗按参考文档人工分析，不能塞进purchase字段。

示例位于 `../assets/snapshot.synthetic.json`，全部人工合成。测试覆盖单位、缺失、混合事件、成熟度、重复渠道与重复JSON键等真实分析失败模式。
