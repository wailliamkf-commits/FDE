# 首次 GitHub 上传与恢复

## 当前正式交付私仓

当前地址为 https://github.com/wailliamkf-commits/FDE ，由用户创建的专用私仓。首次导入采用已审阅的文件快照和新的根提交；不添加旧仓库 remote，不复制 `.git`，不导入旧分支或标签。以下首次发布助手是保留工具，不用于这个已存在的 FDE 仓库。后续变更使用 FDE 仓库的独立分支与 PR。

## 保留的首次发布助手

初次目标：用户个人账户下的新私有 `fde-delivery-toolbox`。不复用现有品牌站、ERP 或公开测试仓库。
上传的仅为通用工具箱。账户能 push 不代表当前聊天工具暴露了写入动作；两者分开核实。

## 在实际可写的 Work/Codex 执行

先检查 `gh auth status`，通过宿主安全登录；不把 token 贴入聊天。脚本自身不安装 gh、不读取明文凭据。
静态审查、manifest/audit/test 通过后：

```sh
python3 tools/publish_github.py --owner YOUR_GITHUB_LOGIN \
  --expected-manifest-sha256 SHA256_FROM_TRUSTED_DELIVERY
```

该命令只离线预览。批准新私有仓库的准确范围后，添加 `--apply` 才会联网、新建并推送。
发布器只支持首次新建；检查实际登录 owner、拒绝已有 repo，初始化独立目录中的 Git，显式暂存 manifest 文件，按命令设置公开 noreply 提交身份，不修改全局身份。
仅在真正回读为 private 且远端 main SHA 等于本地 SHA 时返回 UPLOADED_AND_READ_BACK。

## 中断或目标已存在

不要重复 --apply，不要 reset --hard、clean -fd、force push 或删除仓库。
只读检查当前 .git、origin、已提交文件、远端仓库和分支；记录到底完成在哪一步。
已有正确仓库需要更新时：审查差异，用独立分支和 PR；本版首次发布器不会替你执行后续更新。
尚未推送但已有本地提交：保留它，用宿主实际 GitHub 工具核对远端再续传。
登录/授权失败：只解决相应权限，不自动新增 PAT、不扩大全部仓库范围。

## 上传后仍要做什么

保存实际仓库 URL 与完整 commit；在另一个会话读回 START_HERE、SECURITY 和一个 SKILL。
GitHub App 可能需要用户把新私有仓库加入允许列表。未索引时可按已知路径/提交直接读取；不能编造文件已可见。
当前账户原生安装不是仓库交付前提。只有选择对应目标时，才另外验证宿主技能发现、插件安装、业务试点或调度部署。
