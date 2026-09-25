# AI聚合平台

配合 [AI聚合平台](https://ai.yykkj.com/) 使用的客户端工具仓库。`skill/` 存放 Skill 源码，提供文字对话、生图、多图编辑与 MiniMax-H3 多模态视频生成。平台基于 New API；本仓库不包含或修改 New API 服务端。

## 一句话安装

**下载或克隆本仓库后，在仓库根目录执行 `python3 install.py`（Windows：`py -3 install.py`），按提示完成平台注册登录、充值并粘贴 API Key，即可安装使用。**

如果由 AI 帮忙安装，可以直接对它说：

```text
请安装当前仓库的 AI聚合平台 Skill：运行根目录 install.py，并引导我前往 https://ai.yykkj.com 注册登录、充值和创建 API Key；我提供 Key 后请直接保存，不修改服务端，也不要自动发起付费生成。
```

安装程序只依赖 **Python 3.9+ 标准库**，不需要 pip、Node、Go、Docker、Git Bash 或管理员权限。需要完整仓库，不能只下载 `install.py`。下面命令用于下载/克隆后的本地完整仓库；远程一键下载命令待仓库发布后提供。

安装器会：

1. 将 `skill/` 安装到 `~/.agents/skills/ai-aggregation-platform/`，保留中文展示名“AI聚合平台”。
2. 明确提示平台开通流程；无 Key 时允许粘贴，也可以回车跳过，稍后交给 AI 配置。
3. 已有 Key 时直接保留；重复安装会将原 Skill 放到 skills 父目录旁的 `ai-aggregation-platform-backups/`，不会覆盖凭据或把旧版本留在 skills 目录造成重复发现。
4. 不强制联网验证 Key，不自动充值、不自动生成作品，也不修改系统执行策略。

不同 AI 客户端的 Skill 发现目录可能不同，可传入其 **skills 父目录**：

```bash
python3 install.py --skills-dir '/客户端支持的/skills目录'
```

已获得用户提供的 Key 时，可用一条命令安装并保存：

```bash
python3 install.py --key '用户提供的完整平台Key'
```

Windows 将 `python3` 换成 `py -3`；没有 `py` 启动器时使用 `python`。自动化安装但不交互询问 Key 使用 `--no-prompt`。实际安装可由 AI 操作现成安装器，不需要临时编写安装脚本。

## 先开通平台，再调用功能

**打开 https://ai.yykkj.com/ → 注册账号并登录 → 在平台充值 → 在「API 密钥 / 令牌」创建 Key → 安装时粘贴，或让 AI 代为保存。**

- 已有账号直接登录；已有可用余额不必重复充值。
- 安装 Skill 免费；实际生图、生视频等调用会消耗平台余额，价格以平台当前模型、分组和消费记录为准。
- 注册、充值、创建 Key 在平台网站完成；本地安装器只复制 Skill、保存 Key，不代用户进行支付。
- 平台 Key 独立保存，不读取 Codex、CC Switch 或 `OPENAI_API_KEY`。
- macOS/Linux：`${XDG_CONFIG_HOME:-~/.config}/ai-aggregation-platform/credentials`。
- Windows：`%APPDATA%\ai-aggregation-platform\credentials`。
- `AI_AGG_CONFIG_DIR` 可覆盖凭据目录；`AI_AGG_API_KEY` 可覆盖使用的 Key。升级或重新安装不清理独立凭据。

也可以不安装，直接从本仓库执行独立命令：

```bash
python3 skill/scripts/auth.py set
python3 skill/scripts/auth.py status
python3 skill/scripts/auth.py check
```

`set` 直接保存；`check` 是可选的只读联网认证检查，不会生成作品。缺少 Key 时，直接运行生成脚本也会提示注册、登录、充值和 Key 配置流程。

## 使用示例

以下命令在仓库根目录执行；`skill/scripts/` 已包含完整实现，AI 只需拼接参数，不要临时写业务脚本。**生成命令会消耗余额。**

```bash
# 生图；多张由本地并发调用，每个上游请求固定 n=1，逐张计费。
python3 skill/scripts/image.py '白底黄色玩具小船，无文字' --n 2 --concurrency 2 --out './outputs/小船.png'

# 改图，可重复 --ref 提供多张参考图。
python3 skill/scripts/image.py edit '保持造型，把船身改成红色' --ref './outputs/小船-1.png' --out './outputs/红船.png'

# MiniMax-H3 图生视频；也支持重复 --image / --video / --audio。
python3 skill/scripts/video.py '小船在浅水中缓慢漂浮' --image './outputs/小船-1.png' --seconds 4 --resolution 768P --out './outputs/小船.mp4'
```

支持本地素材、URL 和小型 data URL。Windows 大图片不要拼成超长 base64 命令行参数，应使用本地路径或 URL。复杂提示词使用 `--prompt-file`。任务超时或下载中断应使用回执恢复，不重复提交付费生成。

完整参数与处理流程见 [Skill 说明](skill/SKILL.md)、[Windows 说明](skill/references/windows.md)、[首次配置](skill/references/onboarding.md)、[排错和恢复](skill/references/troubleshooting.md)。

## 仓库结构

```text
AI_aggregation_platform/
├── README.md
├── install.py                 # 跨平台本地安装与 Key 引导
├── tests/test_install.py      # 安装、更新、凭据保留等离线测试
└── skill/
    ├── SKILL.md
    ├── scripts/               # 独立认证、文字、生图、生视频 CLI
    ├── references/
    └── tests/                 # CLI 黑盒回归与离线媒体素材
```

## 开发与验收

```bash
python3 -X utf8 -m unittest discover -s tests -v
python3 -X utf8 skill/tests/test_cli.py
```

Windows 使用 `py -3 -X utf8` 替换 `python3 -X utf8`。为子进程统一编码，建议在 PowerShell 中设置 `$env:PYTHONUTF8='1'`。第二组测试需要允许本机 `127.0.0.1` 临时 HTTP 服务；使用隔离假密钥，不访问平台、不产生生成费用。Windows 的 Bash 包装器测试预期跳过；其他测试应按真实结果记录。

当前功能基线来自 macOS 的真实端到端验收；Windows 原生执行、具体客户端的 Skill 自动发现与蒙版精准编辑效果仍需各自验证，不能以离线测试替代。保留用户要求的中文 `name`，只接受英文标识的通用校验器可能报格式错误；不要把它与生成接口故障混为一谈。

本仓库仅负责 Skill 和本地工具；能在客户端解决的问题，不改动平台服务端或数据库。
