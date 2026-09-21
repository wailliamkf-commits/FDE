# SEO页面规格（空模板，复制到项目填写）

所有项目事实留在项目内。UNKNOWN与NOT_APPLICABLE分开；来源缺失时不补猜数值。使用方法见[SEO交付操作](../references/seo-delivery-playbook.md)。

## 冻结范围

- spec_id / revision / page_id：
- 业务对象、目标人群、地区/语言：
- 主要问题、搜索意图、用户阶段、业务动作及真实成功条件：
- 本轮动作：新建 / 补写 / 保留分工 / 合并候选 / 待数据
- 输入文件清单、对象版本、input_digest、摘要算法/生成时间：
- 修改对象/字段、保留项、授权来源及范围、执行环境：
- 资源上限、验收、回退对象/版本：

## 页面地图与内容责任

| page_id | 层级/父页ID | 当前/拟定URL | 页面类型/主内容类型 | 关键词/问题簇 | 现有承接与冲突解释 | 独立价值/不覆盖内容 | 优先级/理由 | 审计状态 |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | UNKNOWN |

- 内容路由：Question / How-to / Alternatives / Roundup / Vs / Single Review / 其他适用类型；混合意图理由：
- Title / Meta / H1：
- 直接回答 / UVP / 限定条件：
- 主CTA、真实目标、传递字段、成功/失败状态、返回路径：
- 16块模型页是否适用、选择/省略/待证模块及原因：

| block_id/顺序 | H2/模块职责 | 用户问题/短答 | claim_ids/evidence_ids | 视觉槽位/素材缺口 | 动作/目标 | 移动/错误状态 | KEEP/OMIT/NEEDS_DATA及验收 |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## 声明与事实台账

| claim_id | 精确声明/值/单位 | 对象/地区/方法/限制 | evidence_id及来源定位 | 来源版本/摘要/日期 | 来源种类＋evidence_status（REPORTED/HYPOTHESIS/OBSERVED/UNKNOWN/SYNTHETIC） | 冲突/未知 | 核验人/日期/失效条件 | 可用范围 |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## 审稿与补丁

| finding_id | 严重性/标题 | 原文证据及定位 | 原因 | 修法/示例 | 验证方法/结果 |
|---|---|---|---|---|---|
| | | | | | |

| patch_id/finding_id | page_id/字段/唯一锚 | before | after | claim_ids/evidence_ids | input_digest/前置版本 | 批准或复核记录 | 应用状态/回执 | final_digest |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

补丁定位不唯一、输入摘要/前置值不匹配或修改重叠时记STALE/CONFLICT；先重建该项。最终差异须能解释每个修改。哈希不代替真实性、权限或人类批准。

## 内链与URL候选

| candidate_id | 来源页/上下文 | 目标页/当前响应 | 锚文/语义关系 | 用户收益/证据 | 操作类型 | 范围/批准/回退 | 状态/实际验证 |
|---|---|---|---|---|---|---|---|
| | | | | | LINK_PATCH / REDIRECT_PROPOSAL / CANONICAL_PROPOSAL / NOINDEX_PROPOSAL | | PROPOSED |

redirect/noindex等候选不因列在表中自动写入。单列源URL、目标URL、页龄、现有指标窗口、内容保留方式、HTTP与回退验收；目标或页龄未知先补证据。

## 本页交付

- 草稿/保存/预览/公开环境及对象ID：
- 事实与结构验收：
- 桌面/移动、关键动作及异常结果：
- 未决缺口、人工项、替代方案与触发条件：
- 图片、迁移、多语、表单的适用项转入[SEO发布矩阵](seo-release-matrix.md)：
