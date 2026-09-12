# Google Ads 诊断数据地图

文档核验日期：2026-09-12。以下入口依据当日可访问的 Google、Shopify 官方文档，**不是客户后台权限或菜单实测**。菜单缺失时按报告名称查找；记录实际入口、权限和字段限制。一次诊断只取能验证当前问题的数据，不要求每次导出全部 16 类。

## 先确定口径与关联能力

- 先固定账户、系列范围、日期、时区、币种、业务目标、转化动作和归因窗口；购买、加购、询盘分别分析。
- **费用／流量基表与转化动作表分开提取。**按转化动作细分时，费用、点击、展示等列可能显示 `--`。按一致系列 ID、日期及兼容维度对齐，费用分母只计算一次；不得将费用复制到多个动作行再求和。购买 CPA／ROAS 可用已核对的购买动作数据与对应费用基表重算。
- 广告互动日期口径与转化发生日期口径分开。先记录回填延迟和数据成熟度；按转化时间的收入除以当期费用，不自动代表当期获取流量的最终回报。
- 查询、商品、URL、会话、订单并非天然连成一张明细表。仅使用真实存在、定义一致的关联键；报告无法逐条连接时，保留独立表和聚合对照，不按名称、顺序或比例补造明细。
- GA4 顺序漏斗不自动等于同一个会话或结账。先确定用户／会话／checkout 哪种入组单位、观察窗口及完成条件，再选择数据源。

## 数据地图

表中的字段是诊断所需清单，**不是保证一个界面能够同时导出的列**；不兼容时拆表，并记录缺失及无法关联的范围。

|编号|需取数据|入口或报告名|字段与粒度|用途和限制|官方来源|
|---|---|---|---|---|---|
|01|转化动作与系列目标|Ads → Goals → Conversions → Summary → Goals；动作详情／Settings|动作 ID、类别、来源、Primary／Secondary、计数方式、价值、窗口、归因模型、状态、使用该目标的系列|核对是否用加购代替购买、重复回传或目标不匹配。Secondary 纳入系列自定义目标时仍可能参与优化；“无近期转化”不自动等于追踪故障。|[目标与动作](https://support.google.com/google-ads/answer/10993988?hl=en)|
|02|系列日费用与分动作转化|Ads 系列统计表；Columns；Segment → Conversions → Conversion action；按名称添加转化时间列|基表：系列 ID＋日期＋费用／点击／展示；动作表：相同兼容维度＋动作 ID＋次数／价值；分别保留互动日期和转化日期列|用于购买 ROAS、CPA、回填核对。转化细分可能使费用／点击为空；必须分表对齐并防止费用重复计算。|[细分限制](https://support.google.com/google-ads/answer/2454072/use-segments-in-your-tables)、[转化时间口径](https://support.google.com/google-ads/answer/6270625?hl=en)|
|03|实际搜索词|Ads → Campaigns → Insights and reports → Search terms|查询＋系列／广告组 ID＋日期；匹配关键词、搜索词匹配类型、网络、费用、点击；购买动作另取兼容表|识别需求、比较／信任／售后意图，提出否词或内容候选。低量查询会隐藏；可见词不是全部查询；搜索词匹配类型不等于关键词设置。|[搜索词报告](https://support.google.com/google-ads/answer/2472708?hl=en)|
|04|PMax 实际渠道表现|Ads → Campaigns → Insights and reports → Channel performance|系列＋日期＋渠道；product data／video 格式；动作／类别；Ad event type；费用、点击、转化、价值|判断预算及结果来自哪个渠道、点击或观看等归因。支持 2025-06-06 后日期；使用商品数据包含部分展示再营销，不只 Shopping；有渠道报告不代表可直接分配渠道预算。|[PMax 渠道报告](https://support.google.com/google-ads/answer/16260130?hl=en)|
|05|广告目的网址与参数展开网址|Ads → Campaigns → Insights and reports → Landing pages → View expanded landing pages|系列＋落地 URL／参数展开 URL＋日期；点击；设备及转化等兼容细分另取|识别送错页、参数、站点链接和主标题的路径差异。参数展开网址不等于 PMax 自动网址扩展清单；Ads 报告也不证明浏览器成功到达，须与 GA4 或只读实际访问核对。|[落地页报告](https://support.google.com/google-ads/answer/7543502?hl=en)|
|06|自动网址扩展与广告承诺组合|PMax 资产报告 → Expanded Final URL assets；AI Max 的 Search terms 下拉 → Search terms and ad combinations|查询、标题、URL、系列／广告组、素材来源；另只读记录网址扩展开关及排除规则|核对需求—广告承诺—页面。AI Max 专属组合视图不能当作所有 PMax 的完整查询链；配置 URL 不等于实际承接 URL；仅查看设置，不点保存。|[PMax 网址扩展](https://support.google.com/google-ads/answer/14337539?hl=en)、[AI Max 报告](https://support.google.com/google-ads/answer/16470459?hl=en)|
|07|商品 ID 表现与商品属性|Ads 按名称查找 Products 商品表；已有 API 访问时查 Shopping Product／Shopping Performance 报告|Merchant ID、Item ID、feed label／国家／语言、系列、商品类型、自定义标签、价格段；费用、点击、购买价值|判断商品组合、客单、高花费商品和 Feed 需求匹配。Item ID、SKU、Product ID、Variant ID 不能默认相等；商品广告归因表现也不自动证明最终购买了该商品。|[商品表](https://support.google.com/google-ads/answer/3455573?hl=en)、[商品报告及支持范围](https://developers.google.com/google-ads/api/docs/shopping-ads/reporting)|
|08|Demand Gen 渠道与格式|Demand Gen 统计表 → Segment → Network；另按 Ad format 细分|系列／广告组／广告 ID＋网络＋格式；费用、点击、观看／互动、购买动作、归因事件类型|判断创意在哪个入口吸引兴趣及是否形成业务结果。网络包括 Discover、Gmail、YouTube、GDN、Maps；in-feed 汇总可能混合多个网络；不同格式的点击、观看、互动定义不同。|[Demand Gen 指标与报告](https://support.google.com/google-ads/answer/13695597?hl=en)|
|09|设备表现|Ads → Campaigns → Insights and reports → When and where ads showed → Devices；或 Segment → Device|设备＋系列＋日期；费用、点击、购买及价值；需要时关联 GA4 页面／浏览器聚合表|区分设备流量结构与操作问题。购买份额不能代替效率，必须有费用分母；设备差异只能提出 UX 假设。|[设备入口](https://support.google.com/google-ads/answer/1722028?hl=en)、[设备细分](https://support.google.com/google-ads/answer/2454072/use-segments-in-your-tables)|
|10|实际匹配地域与定位设置|Ads → Campaigns → Insights and reports → When and where ads showed → Matched locations；系列定位设置只读查看|国家／州／城市、地域类型、系列、费用、购买；设置的定位范围与位置选项|检查交付地区、语言、币种和承诺匹配。Matched locations 可包含人在当地或对当地感兴趣，不能直接等同用户实际所在地。|[匹配地域报告](https://support.google.com/google-ads/answer/7492954?hl=en)|
|11|操作变更时间线|Ads → Campaigns → Change history|时间、系列／广告组、变更类型、前后值、操作者／工具；预算、出价、目标、素材、URL 等|对照表现拐点并识别多项改动混杂。官方说明覆盖近 2 年；不覆盖全部站点及插件改动；时间重合不能证明因果。|[变更历史](https://support.google.com/google-ads/answer/2454137?hl=en)|
|12|GA4 实际落地与来源|GA4 → Reports → Engagement → Landing page；缺失时按 Landing page 报告名查找|Landing page＋query string、Session source／medium、Session campaign；设备、国家；Sessions、购买、购买收入、参与情况|同页比较不同来源，同来源比较不同页面。这是 session 范围，不能用首次用户来源代替当次来源；报告可能未发布；GA4 会话不等于 Ads 点击。|[GA4 落地页报告](https://support.google.com/analytics/answer/12931766?co=GENIE.Platform%3DDesktop&hl=en)|
|13|GA4 顺序漏斗与同批成交|GA4 → Explore → Funnel exploration；需要精确同批核对时使用已存在的事件明细／数据仓库|入组条件、open／closed、步骤、顺序和时限；view_item、add_to_cart、begin_checkout、purchase；必要时补会话键、transaction_id／checkout 映射|定位流失阶段。GA4 按用户及首次合格顺序计数，不自动限定同一会话／订单／结账；设备分组按首次值。总事件数相除不能冒充同批完成率；不得假设已有 checkout 标识。|[漏斗计数与限制](https://support.google.com/analytics/answer/9327974?hl=en)|
|14|Merchant Center 数据源与商品问题|Merchant Center → Settings → Data sources → Product sources → 具体来源；Products → Needs attention|来源类型、更新时间、处理状态；Item ID、目标国家、批准状态、问题；价格／库存／链接／变体／GTIN 与最终属性|检查同步、展示资格和商品承诺一致性。文件处理报告只适用于文件数据源；处理成功不等于商品无问题；API／插件同步须核对其实际来源。|[来源入口](https://support.google.com/merchants/answer/14991445?hl=en)、[处理与商品问题](https://support.google.com/merchants/answer/13760862?hl=en)|
|15|Shopify 订单、商品与退款|Shopify → Orders → 筛选 → Export；订单详情／交易记录|订单 ID、创建／付款时间、币种、付款状态、商品／SKU／数量、实付、折扣、运税、退款；需要时补交易明细|核实实际成交、客单、商品组合和净收入。一单多行，订单金额不得重复累加；折扣代码列不包含自动折扣；退款时点不足时补明细，不能凭订单汇总推断。|[订单导出与字段](https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders)|
|16|弃单、支付失败与恢复证据|Shopify → Orders → Abandoned checkouts → 具体结账 → Timeline → payment event；成功订单查看订单 Timeline|脱敏结账／订单标识、时间、币种、配送方法、付款尝试、状态、失败 Message、恢复情况|检查是否实际尝试支付及具体失败原因。弃单不覆盖所有匿名离开／加购；部分卡测试／机器人尝试不在列表；超过 3 个月弃单自动删除。只读取证，不发送恢复邮件。|[支付事件入口](https://help.shopify.com/en/manual/promoting-marketing/create-marketing/abandoned-checkouts)、[现行范围与保留](https://help.shopify.com/en/manual/promoting-marketing/create-marketing/migrate-abandoned-checkout)|

## 按问题选择最小取数

以下是执行建议，按问题逐步扩展；没有对应系列、事件或权限时记录缺口，不要求客户为了满足清单新建全部报告。

|当前问题|第一轮最少取数|什么证据出现后再扩展|应交付的判断|
|---|---|---|---|
|购买 ROAS 变化|01＋02＋11；两期一致范围的原始分子、分母、目标和变更|购买价值／次变化再取 07＋15；PMax／Demand Gen 渠道构成变化再取 04／08；地域、设备变化再取 09／10|先区分计量／回填、费用、购买率、客单及组合变化；解释不了的部分保留待验证|
|点击后未被记录为到站|02 的点击基表＋05＋12；同日期、系列、实际 URL|有扩展或路由异常再取 06；移动端集中再取 09；结合经授权的只读重定向、加载、标签与同意设置检查|点击类型／重复点击／会话规则／测量缺失与真实加载失败分别检查，不能把点击减会话全部算“损失流量”|
|页面有流量但不成交|12＋13；疑似路径的页面内容和可购买状态；搜索流量取 03，PMax／Demand Gen 取 04／08|需求与广告承诺不一致取 06；商品信息或库存可疑取 07＋14；价格／订单结构可疑取 15|形成流量不匹配、送错页、内容／报价不足、操作体验四类候选，并给出对照验证|
|加购／结账后流失|13 的明确入组漏斗＋15＋16 的脱敏样本和付款事件|特定设备／国家集中再取 09／10；缺少配送或支付原因时补实际配置及错误证据|区分未尝试支付、支付被拒、交付／总价障碍、测量重复；没有失败事件不得断言支付故障|
|B2B 表单或询盘质量低|01＋02＋相关 03／06＋12；CRM 或人工台账中的脱敏线索 ID、来源、提交时间、有效性、项目条件与状态|表单操作失败再取 13 或现有表单日志；线索有效但未成交再补回复时间、报价、阶段变更与成交结果|区分低意图流量、资格说明不清、表单摩擦、销售跟进问题；询盘提交不能替代有效线索／成交|

B2B 的 CRM／表单平台因项目而异，必须先识别实际系统与取数入口；不要虚构通用菜单或默认拥有离线回传能力。购买与 B2B 有效线索分别定义主指标。

## 取数元数据模板

每份导出或截图至少填写以下记录。未知值填写 `unknown`，未取得填 `missing`；不要用空字符串或数字 0 代替。

```yaml
dataset_id: "unknown"
question: "本表用于验证的具体问题"
source_system: "Google Ads / GA4 / Merchant Center / Shopify / 实际CRM"
report_name: "unknown"
actual_entry: "实际入口；仅有文档入口时明确注明"
account_or_property_id: "脱敏标识；映射保存在受控项目资料中"
exported_at: "含时区的时间"
period_start: "unknown"
period_end: "unknown"
timezone: "unknown"
currency: "unknown"
filters_and_scope: "系列、国家、网络、状态、已排除对象等"
row_grain: "一行代表什么；例如系列ID×日期"
metrics_and_definitions: "费用、点击、购买数、价值的确切列与定义"
conversion_action_ids: []
attribution_model_and_window: "unknown"
date_basis: "ad_interaction_date / conversion_date / order_created / paid_at"
data_maturity: "截止日距导出日、已知回填／退款延迟"
join_keys: []
join_cardinality: "one_to_one / one_to_many / aggregate_only / unknown"
coverage_and_missing: "行数、覆盖费用或会话、隐藏查询、缺失维度"
totals_reconciled: "对照原报表总额；差异及原因"
evidence_location: "文件＋工作表／单元格，或截图页码／报告链接"
verification_level: "原表复算 / 图片人工核对 / OCR待核 / 文档入口核验"
access_limits: "权限、保留期、不可导出或不可关联字段"
```

截图须尽量保留日期、账户范围、过滤条件和完整表头；缺少这些信息时只作为线索。OCR 数字回到原图核对，`--`、空白、缺失、零值分别处理。

## 使用边界

- 只读获取和诊断不授权修改预算、目标、否词、Feed、商品、页面或发送恢复消息。需要上线时交给明确的变更范围与验收流程。
- 当前官方落地页文档仍含旧式 Mobile-Friendly Test／AMP 描述。本地图只引用其报告入口，不把这些描述直接列为当前 UX 验收门槛；体验结论须有实际设备与行为／错误证据。
- 平台报告更新后，以实际可验证的界面和官方文档修订入口，并更新核验日期；不可用字段不能通过猜测补齐。
