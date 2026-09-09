# Work、Codex 与插件安装

本文件仅用于用户明确选择原生安装时。默认正式交付为 GitHub 私仓，见 `REPOSITORY_DELIVERY.md`；没有安装菜单不阻塞技能包交付。

依据官方文档核验于 2026-09-09；宿主及账户实际能力优先。

## 本仓库的 Work 导入参数

以下为具备相应管理员入口的团队工作空间路径，不适用于个人账户；不是本项目默认交付步骤。

- Source：`https://github.com/wailliamkf-commits/FDE`
- Path：留空（市场清单位于根目录下的 `.agents/plugins/marketplace.json`）。
- Branch, tag, or commit：填写本次交接记录的完整 40 位提交；首次验收建议固定版本。
- 插件名称：`fde-delivery-toolbox`；五个 Skill 随同一插件导入。
- 初次验收：在新 Work 对话选中插件，用模拟场景调用 `fde-discovery`，返回非空场景卡、实际读取的技能名、来源提交与宿主能力；未完成原生发现前不报告安装成功。
- 只读试用：为一家虚构企业的订单异常人工分流流程生成场景卡，列出待验证假设、范围和验收；不连接真实 ERP、不发消息。

管理员操作入口和权限规则见 [OpenAI 官方插件管理说明](https://learn.chatgpt.com/docs/enterprise/plugin-management)。管理员导入需要 GitHub 账户能读取本仓库；仓库内策略不会自动覆盖工作空间策略。

## 路径 A：项目级独立 Skills，最小落地

适用：本地 ChatGPT 桌面/Codex、CLI 或 IDE 中实际支持 `.agents/skills` 的环境。
审查并测试 bundle；运行 install.py 先预览再 --apply。现有技能冲突就停止，不覆盖。
本包会复制获准技能和不可变共享文件到指定项目，不触碰 ~/.agents/skills 或全局 config.toml。
安装器不修改项目 .gitignore；在生成实际任务数据前，将 `.fde/` 与项目私密运行目录加入已有忽略规则并审阅差异，避免后续误提交。
在宿主技能列表验证，然后在新会话显式调用；Codex 使用其实际支持的 `$技能名` 或 /skills。
这条路径不能证明网页 Work 已经能够看到本地技能目录。

## 路径 B：Skills-only 插件，服务 Work 的重复调用

根目录含 `.codex-plugin/plugin.json`、`skills/` 与 `.agents/plugins/marketplace.json`，按 skills-only 插件和 GitHub workspace marketplace 组织。
工作区管理员在 Admin > Plugins > Add > Import marketplace 输入仓库 URL；仓库根使用空 Path，并在导入框把 Branch/tag/commit 固定到已审阅的完整 commit。marketplace 使用同仓库本地路径 `./`，不会再跟随第二个浮动 Git 来源；私有仓库需授权 GitHub 读取。
导入后逐项核对结果和安装策略，安装/刷新后新开会话测试。管理员导入、成员安装和技能真实触发是三项证据；任一未回读就不能写 `REGISTERED_AND_INVOKED`。
本包没有 MCP 服务、外部 app、浏览器扩展或自动执行 Hook。GitHub workspace 导入会忽略仓库内的安装/认证 policy；工作区管理员须在导入后另行配置实际策略。
个人、本地与工作区插件入口可能不同；没有管理入口不要求升级账户，也不为分发而公开仓库。只有已选择的安装路径记 BLOCKED；仓库交付独立验收。
插件安装只解决发现/加载，不自动授予 Shopify、GitHub 写入、文件权限和付费图像 API。

## 路径 C：只有 GitHub 读取能力

指定仓库及完整 commit，读取 START_HERE、SECURITY、catalog 与所需 SKILL。
可以按其流程协作，但应报告“已读取并按流程使用”，不是“原生插件已安装”。
若脚本或项目文件不可执行，只记录依赖该能力的任务受限；可继续分析和文档工作。无需为了按流程使用而安装。

## 一次性设置，不要装一堆东西

GitHub 连接是否可读本私仓需在接收环境实测，不能沿用维护者的连接状态；上传另需实际可用且已获授权的写入通道。
Python 3.10+ 与 Git 为本地工具前提，不是 ChatGPT 插件；本包没有 pip install 步骤。
`skill-creator` / `plugin-creator` 只在维护本工具箱时需要，不是日常运行依赖；须使用宿主可信内置版本，不从同名陌生仓库下载安装。
浏览器、图像、Shopify 等只在项目任务需要时连接；没有必要先接所有服务。

新对话不保证自动读取另一对话的全部历史。首次上传 bundle；仓库发布后，使用固定仓库、commit、START_HERE 和项目当前入口恢复。
