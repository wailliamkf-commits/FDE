# 合成演练：产品手册、动态库存与退款草稿

所有数据与场景均为合成；状态 DRAFT，无客户验收或生产部署。
事实假设：仅批准脱敏样本与本地草稿，没有生产 API 写权限；每小时库存是期望而非已验证能力。

## 选择

主 WF 固定工作流；补 RG 资料定位、TC 工具契约、EV 评测。RC 的本地进度记录可复用，尚不需要独立恢复服务。排除 AG/MA/MM：未证明需要动态规划、多角色或跨会话画像。不是建站任务，不使用 fde-brand-site；需要实际站点入口改动时另开明确范围。

数据流：意图分类→PDF 产品依据检索 / 当前库存查询适配器 / 退款材料整理→字段与证据校验→人工确认草稿。
稳定资料字段 doc_id/version/page/sku；库存字段 sku/quantity/unit/as_of/source_version；草稿 request_id/input_digest/evidence_refs/missing_fields/handoff_reason。库存适配器当前只读样本 CSV，输出必须标样本和时间；时效阈值由业务确认，未知时不得称实时可售。
状态 RECEIVED→VALIDATED→DRAFTED→REVIEW_REQUIRED，异常 BLOCKED；本轮没有 REFUNDED 状态，也不模拟真实退款成功。

## 实施与备用

先用少量手工标注 PDF 问题验证页码/型号，再接样本库存查表，最后生成退款材料单。退款金额/政策缺失就列未决，不猜规则。重复 input_digest 复用对应本地产物；版本变化使草稿过期，重新验证；中断恢复只重建草稿，不撤销/重做真实退款。
解析质量不足时 B：人工整理 FAQ+库存 CSV+材料表，牺牲自动覆盖；C：资料冲突、SKU 不匹配、库存过期或缺政策时转人工。未来接实时读 API 先 preflight；加入退款写入需独立受控执行通道和新授权。

## 验收与技能交接

测试页码错误、旧资料、越权文档、缺 SKU、库存过期、PDF 注入、缺退款政策、重复和中断。硬失败：无依据承诺可售/退款，任何未授权外发或生产写入。
fde-discovery 冻结样本范围→fde-architecture-select 填交接单→fde-connector-preflight 核对工具→fde-delivery 做本地纵向切片→fde-eval-release 核验→fde-handoff-cleanup 留恢复入口。未运行任何实际项目测试。
