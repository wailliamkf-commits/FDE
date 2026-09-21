# SEO发布矩阵（空模板，复制适用分支到项目）

task_id / batch_id / page_ids / input_digest：
环境/精确对象与版本：　｜授权来源、允许字段与期限：
验收责任人/证据位置：　｜恢复对象/版本与条件：
范围分母与资源上限：　｜真实终态/未决：

按[SEO交付操作](../references/seo-delivery-playbook.md)或[多语言变更控制](../references/multilingual-change-control.md)填写。每条结果使用PASS / FAIL / NOT_TESTED / UNKNOWN / NOT_APPLICABLE；NOT_APPLICABLE须有理由。完成数量只是覆盖分母，不证明质量。

## 通用读回

| 对象/版本 | 检查项及预期 | 环境/视口/语言/时间 | 实际结果 | 状态 | 证据/回执 | 未覆盖范围/负责人 |
|---|---|---|---|---|---|---|
| | | | | NOT_TESTED | | |

阶段分别登记：PROPOSED提案、LOCAL本地、SAVED保存重开、PREVIEW预览、PUBLISHED发布角色与公开载荷；VERIFIED须指明实际验证项目。复核者与批准者不得由Agent伪造。

## 图片源到前台

| image_id/源摘要/权利 | 原尺寸/方向/格式 | 槽位/视口/DPR/显示尺寸 | 裁切/输出参数/格式/尺寸/字节/摘要 | 元数据处理/视觉复核 | 上传媒体ID/URL/读回 | 绑定page_id/字段/alt/旧映射 | 实际请求/状态/Content-Type/解码/字节/DOM alt | 分阶段结果/证据 |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | LOCAL_READY / UPLOADED / BOUND / REQUEST_VERIFIED |

非图片/跳过/失败项及原因：
小源图放大决定与理由：
前台失败时恢复槽位与验证结果：

## 插件迁移与异常核销

原/新组件实际版本、责任输出项：
源导出摘要、恢复快照、代表样本选择理由：

| migration_row_id/对象/URL | 字段 | 源值/版本 | 映射或变换规则 | 预期值 | 目标实际值/读回 | MATCH/APPROVED_TRANSFORM/EXCLUDED/UNRESOLVED | 原因/批准/异常ID/证据 |
|---|---|---|---|---|---|---|---|
| | | | | | | UNRESOLVED | |

- 源记录总数 = MATCH + APPROVED_TRANSFORM + EXCLUDED + UNRESOLVED（各行互斥）；对象数与字段行数分别报：
- 源不存在但目标新增/重复的行及原因：
- `undefined`或其他异常定位、影响与未解决项：
- 所有受改跳转、模板/语言/索引例外的前台抽检证据：
- title/meta/canonical/robots/schema/sitemap输出唯一责任、后台与前台差异：
- 关键未决数量、切换决定、旧配置恢复实测：
- 分析连接（若适用）：认证/所选站点/窗口/新鲜结果：

## 多语言批次与签字

URL集合基线摘要/预计页数/预计字段与片段数：
语言地区、术语版本、代表批范围与扩展条件：

| locale/page_id/field/segment_id | source_digest/input_digest/terms_version | defect/finding/patch_id | before/after位置 | 当前阶段/状态 | 保存读回/复扫证据 | 人工审校人/范围/结果 | 未决/恢复入口 |
|---|---|---|---|---|---|---|---|
| | | | | PENDING | | | |

| 阶段 | 预计/已读/已改/已验证/失败/未触达 | 产物摘要/回执 | 阻断缺陷/合法例外 | 继续或暂停条件 |
|---|---|---|---|---|
| preflight | | | | |
| baseline | | | | |
| scan | | | | |
| sweep | | | | |
| terms | | | | |
| apply | | | | |
| review | | | | |
| signoff | | | | |

全量机器检查范围：　｜人工审校/抽样方法与未审范围：
URL差异、RTL/移动、语言入口、媒体与表单运行结果：
可公开运行范围：　｜已获语言验收范围：
真实签署主体/时间/范围/证据，或SIGNOFF_PENDING：
断点/未确认提交/TERMS_STALE影响/下一项：

## 表单与防误杀

允许的测试环境/收件人、合成test_id规则、成功定义：
新增防护/观察模式/限额、回退开关、最少日志与保留期限：

| case_id/test_id | 正向/负向/误杀探针 | 输入条件/预期 | 前台反馈 | 服务端记录ID | 通知队列/发送状态 | 真实收件箱同ID回执 | 去重/分析事件 | 结果/证据/未决 |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | NOT_TESTED |

有效提交误拦的恢复与规则回退结果：
邮件失效时已验证落库、负责人可见性与人工处理队列：
无发信授权或未收到邮件时，实际送达边界：

## 最终交付与恢复

通过的精确范围及层级：
未验证/失败项、责任人、下一动作：
回退实际验证与仍被引用资源保留：
发布后需观察的结果及窗口（未配置调度不记已监控）：
