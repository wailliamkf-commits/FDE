# EV：分层评测与可回放证据

选用：证明原型正确、排查错误、知识更新前回归。排除：没有样本与测量时，不能制造百分比分数。

## 层次与字段

组件（解析/召回/重排）→整链（依据完整性/忠实度/相关性）→业务（任务完成/人工通过/采用/成本）。这三层各有分母，不能平均一个总分掩盖权限或关键数值错误。
编辑建议测试项：case_id、input、expected_evidence、expected_result、forbidden_actions、metric_definition、threshold_owner、dataset_version；运行项：run_id、tool/model_version、step_events、actual_result、failure_stage、latency、usage。

## 实施顺序

选真实脱敏问题加边界/诱导例，标标准依据和评分；先跑基线再改一个组件，保持可比较的数据/口径；失败回流回归集。合成题须人工检查原文是否真的支持。
RAG 分别检查 Context Precision/Recall、Faithfulness、Answer Relevancy；具体算法按实际工具版本定义。高忠实低相关只能提示方向，不唯一确定检索故障。
链路保存输入摘要、意图、计划、工具参数脱敏摘要、真实返回证据、最终结果；不默认记录客户原文或隐藏思维链。HTTP 200 还要业务读回。

备用为少量人工标注/抽检并声明范围；门槛不通过回退已确认版本或停止扩大。测试：错误答案引用真的存在但不相关；越权召回；成功响应空结果；版本漂移；工具调用记录缺失却称完成；发布前重复回归。

来源：video-020、028、034 70–180 秒、046 60–180 秒、057 70–240 秒。Ragas/DeepEval/TruLens 仅来源提及，未作为依赖安装或能力保证。
