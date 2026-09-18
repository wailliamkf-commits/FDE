# 合成反例：固定 CSV 周报不需要 Agent

输入已批准的 CSV，字段 week/sku/revenue/refunds，规则固定、仅本地输出。主方案是字段校验→确定性汇总→对账→Markdown/CSV 报告。仅参考 WF 的流程结构和 EV 的验证方法，无需状态机服务、LLM、向量库、记忆、多 Agent。

输出列 source_hash、period、currency、row_count、totals、invalid_rows；金额单位和退款口径未确认时不能做净收入结论。空值不当零、重复行标冲突。
备用为人工核对的电子表格，保留计算规则；损失自动化，不改变口径。验证正常数据、缺列、混币种、重复、空文件、汇总与明细不一致。必要技能仅 discovery（缺口径时）、delivery、eval-release；不安装全技能库。

本例是选型演练，不声称已有 CSV 汇总代码或业务验收。
