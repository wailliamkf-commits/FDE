# FDE Delivery Toolbox · 0.1.13

正式交付私仓：https://github.com/wailliamkf-commits/FDE 。本仓库从审查后的文件快照建立独立根提交，不继承其他仓库的 Git 历史。交付不要求在维护者账户安装、不要求商店上架，也不要求升级团队账户。接收与验收见 `docs/REPOSITORY_DELIVERY.md`；只有需要原生安装时才阅读 `docs/INSTALL_AND_WORK.md`。

一套小而可执行的交付工具箱：从业务需求到可验证成果，再到安全交接与复用。
它是跨项目的通用方法层，不存放任何真实客户数据、凭据、现行生产配置或岗位截图原件。

**先读 `START_HERE.md`；只选择当前任务需要的技能，不先搭建万能 Agent 平台。**

## FDE 案例驱动交付基础包 · 0.1.0

新增 [fde-case-delivery-foundation](docs/fde-case-delivery-foundation/README.md)：24案来源索引、技术选择方法、主方案/备用方案/人工兜底、验收与价值追踪，以及后续知识补充入口。它是供现有九个技能按需读取的参考包，不是新增原生Skill或自动执行器；不包含PDF原件、未抓取的导图节点和真实客户数据。

## 媒体知识摄取与跨渠道参考包 · 0.1.0

[使用入口](docs/media-intake/README.md)连接连续读取、证据审阅、每小时进度、恢复与可恢复清理；按 SEO/GEO、广告、站点、视觉、社区、经营和 Agent 条件化整理来源。提供完整来源索引、时效纠错和试验路线，不提供新的原生 Skill、模型调用/清理执行器或业务收益保证。原始媒体与私人审计保留项目，不随仓库分发。

## 这是什么，已经做到了什么

- 九个标准 `SKILL.md` 能力包；每个都包含适用条件、输入、动作、输出和停止条件。
- 一个通过当前本地结构校验的 skills-only 插件清单，以及用于 GitHub workspace 导入的 `.agents/plugins/marketplace.json`；不包含 MCP 服务、Hooks、浏览器扩展或调度器。
- Python 3.10+ 标准库工具：环境检查、任务校验、操作范围预检查、证据文件校验、清理预览。
- 项目级安装器：默认只预览；明确 `--apply` 才复制文件；不覆盖旧 Skill、全局设置或项目 AGENTS.md。
- 保留的 GitHub 首次发布助手只适用于创建全新的 `fde-delivery-toolbox` 私仓；当前 FDE 分发仓库已存在，不使用该助手。后续更新通过当前仓库的审阅分支和 PR。
- 单元测试与离线演示。没有运行时第三方 Python 依赖，不运行安装 Hooks，不自动下载程序。
- 岗位需求基线与三张轻量交付模板：集成契约、评测/上线记分卡、复用/产品反馈。

**本版不是 OS 沙箱，不是生产执行网关，不是已部署的自动运营服务。**
`check-action` 只校验本工具箱可检查的条件，输出从不代表已获外部授权。
远端写入与删除全部返回 `REMOTE_EXECUTOR_REQUIRED`，即使提供一张声称已批准的 JSON，也不能执行。
证据 SHA-256 校验不等于商业事实正确，独立 QA 仍需检查真实内容与环境。

## 九个技能

| 技能 | 何时使用 | 主要产出 |
|---|---|---|
| `fde-discovery` | 新需求、接管项目、判断是否值得做 | 一页场景卡、价值基线、最小范围、非目标、验收与未决事实 |
| `fde-connector-preflight` | 接口、权限、工具与环境可能不通 | 实测能力记录、集成契约、只读验证、精确阻塞 |
| `fde-delivery` | 已有明确任务，需要实际实现 | 一个可检查的本地成果、差异、测试与异常说明 |
| `fde-eval-release` | 声称完成、准备合并或发布 | 统一记分卡、独立复核、放行建议；不自授发布权 |
| `fde-handoff-cleanup` | 换对话、收尾、开始巡检或整理临时文件 | 短交接、复用/产品反馈、清理预览与待验证调度信息 |
| `fde-brand-growth` | 品牌需求验证、优质流量、漏斗诊断、扩量与资产经营 | 分阶段指标、渠道/页面行动、实验与离线口径检查 |
| `fde-brand-site` | 跨行业品牌网站建设与持续优化 | 业务适配、竞品、页面/视觉/交互、SEO/GEO/自然流量、模型分工、上线验收 |
| `google-ads-diagnostics` | Search、Shopping、PMax、Demand Gen 数据与页面诊断 | 16 类取数入口、12 类问题、指标口径、商品/页面任务 |
| `meta-ads-diagnostics` | Facebook / Instagram 等 Meta 广告与承接诊断 | 14 类取数入口、16 条指标规则、17 类问题、整改任务 |

这是能力库，不是常驻 Agent 团队。一个总控可以按需调用；小任务可以由一名执行者完成，关键检查由独立上下文或人复核。

## 最短试用路径

只接收技能包：取得私仓读取权限，下载或克隆交接记录指定的完整提交，先阅读 `START_HERE.md` 和 `SECURITY.md`。不运行安装器、不修改账户设置。需要执行检查时，再按以下步骤验证。

先从交接记录取得已审阅的完整 Git commit 或整包 ZIP SHA-256，并在包外用可信宿主工具核对；包内 manifest 不能替代这个根信任。确认验证期间只有一个可信写入者后，第一条包内命令必须是隔离模式的精确文件树校验：

```sh
python3 -I -B tools/fde.py verify-bundle --expected-manifest-sha256 SHA256_FROM_TRUSTED_DELIVERY
```

它通过以后才运行其余入口：

```sh
python3 tools/fde.py doctor
python3 tools/audit_bundle.py --expected-manifest-sha256 SHA256_FROM_TRUSTED_DELIVERY
python3 -B -m unittest discover -s tests -v
python3 tools/smoke_demo.py
```

Windows 的 Python 命令可能为 `py -3`；由当前执行环境核验，不强制改系统解释器。
这些入口会把字节码缓存查找移出包目录并禁止写入；第一条 `-I -B` 校验同时避免包内同名模块在校验前遮蔽标准库。如果下载内容本身已含未列入 MANIFEST 的缓存或其他文件，精确校验会拒绝。它仍不是恶意下载沙箱：若验证器源码本身来自不可信包，只能靠前述包外 commit/ZIP 校验建立根信任。
演示使用临时的模拟项目，不接触商店，不证明真实业务上线。

可选：仅当用户要求在指定项目原生安装时，执行以下预览：

```sh
python3 tools/install.py --project /ABSOLUTE/EXISTING/PROJECT \
  --expected-manifest-sha256 SHA256_FROM_TRUSTED_DELIVERY \
  --skills fde-discovery fde-connector-preflight fde-delivery fde-eval-release fde-handoff-cleanup
```

预览核对后，同一命令添加 `--apply` 才复制文件。目标为该项目 `.agents/skills/` 和 `.fde/`，不修改用户全局技能目录。
在真实宿主的技能列表确认名字，再做一个无副作用测试。文件复制完成不等于宿主已经发现或启用技能。

## 仓库源码与安装目标必须分离

工具箱仓库：方法、通用代码、测试、无真实数据的模板、来源和版本。
项目工作区：实际产品资料、任务状态、截图、批准记录、成果与日志。
平台安全层：凭据、OAuth、沙箱、网络代理、批准服务、真正的写入执行器。

安装器拒绝把工具箱源码目录本身或其子目录当作项目根。项目档案根可以包含一个独立、只读的工具箱源码副本，但安装目标只写到项目自己的 `.agents/skills/` 与 `.fde/`。

`.gitignore` 不是数据防泄漏系统。首次上传只提交 `MANIFEST.json` 枚举的、已经审查的文件。

## 重要入口

- `START_HERE.md`：新对话启动与实际环境检查。
- `SECURITY.md`：权限、注入、数据、版本与失败处理。
- `docs/REPOSITORY_DELIVERY.md`：私仓交付范围、接收步骤、验收边界。
- `docs/INSTALL_AND_WORK.md`：Work / Codex / 插件的安装差异。
- `docs/OPERATING_METHOD.md`：岗位能力 → 可交付方法与任务循环。
- `docs/FDE_JOB_REQUIREMENTS_BASELINE.md`：有限招聘样本、公开一手岗位与工具箱设计的可追溯映射。
- `docs/SETTINGS_AND_PERMISSIONS.md`：应当怎样设置，哪些只是意图。
- `docs/PUBLISH_AND_RECOVER.md`：私有仓库创建、上传、回读与中断恢复。
- `docs/UPDATES_AND_EVALS.md`：新模型和新 Skill 的受控更新。
- `docs/ACCEPTANCE.md`：本版验收与未实现能力。

参考资料核验日期：2026-09-08。`docs/SOURCES.md` 保存公开来源。插件结构校验、Work 管理员导入、GitHub 上传和真实项目验证分别记录，不合并为“已部署”。

## 品牌增长模块 v0.3.1

新增市场/竞品/用户研究、广告与SEO交接、活动承诺及定制询盘闭环，见 [会议补充与验证](docs/GROWTH_MEETING_UPGRADE.md)。

品牌增长Skill以十步闭环串联需求、最小承接、商业验证、资产与监控反馈，覆盖S0需求探索到S4稳定经营；详细方案见 [docs/BRAND_GROWTH.md](docs/BRAND_GROWTH.md)。按需加载参考资料，不强制一次运行全部分析。真实业务数据留在项目工作区。仓库交付不等于后台接通、原生安装或商业效果已验证。

## 付费媒体诊断模块

[使用与溯源索引](docs/paid-media/README.md)说明两项广告技能的分类、版本、数据需求与验证边界。Google Ads 内容 v2.2.0、Meta 内容 v1.1.0 都可独立按文件使用；只在需要原生安装时按现有安装流程选择对应技能。没有新增广告 API、自动预算操作或必装插件。

## 跨行业品牌网站模块 v1.0.0

[客户使用入口](docs/BRAND_SITE.md)：零售、定制、B2B、服务预约、订阅和内容业务按模式选择对象、页面、视觉证据、转化与验收，不沿用某一客户的行业设定。包含五张可填写工作表、官方依据和合成演练。前沿思考模型负责定向与选择执行模型；每批次核验实际可用能力，不锁死代际名称。本包提供调度方法，**不包含自动模型切换服务或生产执行器**。

广告账户接手、页面池探索与商品分层见 [本轮架构更新](docs/paid-media/ARCHITECTURE_UPDATE_20260928.md)。
