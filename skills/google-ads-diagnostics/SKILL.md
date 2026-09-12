---
name: google-ads-diagnostics
description: Diagnose Google Ads traffic quality, ad-to-page fit, landing-page content and purchase or qualified-lead friction from account exports, spreadsheets, embedded screenshots and site evidence. Use for Search, Shopping, Performance Max and Demand Gen reviews that must identify required data, retrieval locations and testable optimization tasks.
metadata:
  version: "2.0.0"
  category: "growth/paid-media"
---

# Google Ads 流量与落地页诊断

将广告数据与站内证据转换成可验证的优化任务。以真实渠道、需求、广告承诺、实际到达 URL／变体、用户阶段和业务结果为分析单位，适用于电商及 B2B 询盘。

## 开始与选读

先确认业务目标、市场与交付范围、阶段、观察期及已有资料。使用用户已有授权和输入；能完成的分析先完成，缺失部分列出最小取数请求，不把访问更多系统当作默认前提。

- 需要数据或不知道去哪里取：读 [data-sources.md](references/data-sources.md)。选择支持当前决策的最小数据组。
- 需要计算、比较或连接报表：读 [measurement-contract.md](references/measurement-contract.md)。先冻结指标和粒度，再解释变化。
- 需要判断问题出在哪一段：读 [diagnosis-matrix.md](references/diagnosis-matrix.md)。保留竞争解释及可推翻主假设的证据。
- 需要安排产品内容、落地页或体验优化：读 [channel-page-playbook.md](references/channel-page-playbook.md)。区分文字广告与商品广告的目的地限制。
- 需要阶段计划、试验、预算依据或沉淀品牌内容：读 [stages-experiments.md](references/stages-experiments.md)。不扩展成未经请求的全渠道战略项目。
- 使用 [诊断工作底稿](assets/diagnosis-workpad.md) 记录分析；仅在需要协作取数时使用 [取数任务单](assets/data-request.md)。按任务删减空表，不为填满模板增加工作。

## 工作流程

1. **登记证据。** 对工作簿同时提取单元格文字、公式缓存、图片及其工作表／锚点，保留日期、过滤条件和出处。OCR 只辅助检索；引用关键数字回看原图。区分计划、操作记录、投手判断、平台推荐、实测结果及历史截图。无法辨认或缺失处标未知。
2. **冻结业务与测量口径。** 区分购买、加购、询价、合格机会；核对账户、币种、时区、日期口径、目标配置、归因窗口、延迟、回填和去重。必要时把费用基表与转化动作表分开提取，连接后费用只累计一次。
3. **重建可观察路径。** 写清系列类型、实际渠道、广告形式、触达逻辑、意图、实际 URL／变体和最终结果。不要把再营销当作渠道，或把 PMax／Feed-only 名称当作 Shopping 渠道证据。
4. **定位候选原因。** 先排测量错误和明确不可成交条件，再区分流量适配、广告到页面匹配、页面内容、操作体验、商品／价格／履约。允许主因候选与次因并存，不能强制唯一归因。
5. **反证与对照。** 比较同页不同需求、同需求不同页面、同路径不同设备；核对商品结构与同期变更。选择能区分解释的最小验证，不用相关性宣称因果。
6. **转成任务。** 每条写出证据、取数位置、优化对象与具体修改、负责人、主指标、护栏、观察条件、回滚或关闭条件。明确哪些现在能做，哪些须等数据。
7. **记录结果和复用范围。** 保存通过验证的需求与页面规则，注明适用国家、品类、渠道、阶段及反例。未经验证的建议保留为假设。

## 必须保留的判断边界

- 混合加购价值的 ROAS 不能称为购买回报；Primary／Secondary 还需结合系列目标和自定义目标解释。
- 普通转化日期口径与“按转化时间”分列；不同平台归因不直接相加。分数购买不是后台整数订单。
- Ads 转化动作细分可使费用或点击显示空值；不要补造动作级费用，也不要把系列费用重复到动作行后求和。
- 实际查询受隐私限制；`0 < conversions < 1` 不是零转化，`> 0` 与 `< 1` 不是互斥组。
- 跳出、CTR、CPC、加购和设备购买占比都不能独立定责。GA4 事件总数比值、用户漏斗和同一 checkout 完成率不是一回事。
- Landing pages 的 expanded landing pages 与 PMax Expanded Final URL assets 是不同报告。配置 URL、报表 URL、重定向后实际到达需分别核对。
- 商品卡片落到对应具体商品及适当变体；泛集合页测试用于允许这种目的地的文字广告等路径。
- PMax 受众信号不是硬性圈定；资产组不是独立预算单元或天然随机试验。读取渠道报告不代表能直接分配 PMax 渠道预算。
- 不要求所有字段拼到一个不存在的全链路报告。声明真实关联键、可连接覆盖和未知部分，不按名称或比例补造用户链路。
- 不从单项目复制固定 ROAS、CPC、预算占比、点击数止损线、受众包、全量否词或设备／时段调整。

## 交付标准

按 **BLOCKER / SHOULD FIX / OPTIONAL** 排序。BLOCKER 只用于使关键判断不可靠、明确不可成交或违反当前目标／约束的问题；一个缺失字段通常只阻塞依赖它的结论，不阻塞全部工作。

默认交付四项：范围与证据覆盖；优先问题及最小补数入口；页面／产品／投放具体任务与责任；主指标、风险边界、观察、复查和回滚安排。先给决策和最高优先问题，同一结论不要在多个表重复；简单请求不展开全部底稿，完整审计或用户要求时再提供详细附录。

指标可复算、关键引用可定位、建议能执行且结论不超出证据时，分析交付才完成。数据不足时交付有用的部分和明确缺口，不宣称已定责。

本技能本身不授予账户、Feed、预算、主题、订单、权限或消息发送的写入授权。用户只要求分析时，执行只读；用户明确要求实施时按其已授权范围操作，不重复索取已有授权。

## 维护

界面路径与平台能力按 [数据地图](references/data-sources.md) 的官方链接现查；资料核验日期不等于客户后台实测日期。只读生成文件不等于已上线优化；文件存入仓库也不等于已安装到技能目录。
