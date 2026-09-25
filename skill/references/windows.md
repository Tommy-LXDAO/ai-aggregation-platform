# Windows

平台开通：打开 https://ai.yykkj.com，注册账号并登录，然后充值，再进入「API 密钥 / 令牌」创建 Key，由 AI 或 `auth.py set` 写入。安装不收费，实际生成消耗平台余额。

仅需 Python 3.9+，不需要 Git Bash、WSL、curl、pip 或 SDK。没有 Python 时从 python.org 安装并勾选 PATH。

PowerShell 示例（`$S` 按实际 Skill 安装目录设置一次，不是代码配置）：

```powershell
$S = "$env:USERPROFILE\.agents\skills\ai-aggregation-platform\scripts"
py -3 "$S\auth.py" status
py -3 "$S\auth.py" set --key '用户提供的完整Key'
py -3 "$S\image.py" '蓝色玩具小船，白色背景' --out "$env:USERPROFILE\Pictures\小船.png"
py -3 "$S\image.py" edit '把小船改为红色' --ref "$env:USERPROFILE\Pictures\小船.png" --out "$env:USERPROFILE\Pictures\红船.png"
py -3 "$S\video.py" '让参考图中的小船缓慢漂浮' --image "$env:USERPROFILE\Pictures\小船.png" --seconds 4 --resolution 768P --out "$env:USERPROFILE\Videos\小船.mp4"
py -3 "$S\video.py" wait TASK_ID --receipt "$env:USERPROFILE\Videos\小船.mp4.task.json"
```

如果 Python 安装没有 `py` 启动器，替换 `py -3` 为 `python`。

`newapi.ps1 image ...` 等兼容入口也会自动查找 Python。执行策略限制 ps1 时，直接运行 `.py` 入口，不要求修改系统策略。

Windows PowerShell 5.1 对原生命令中的嵌套引号和管道编码有已知限制：复杂提示词使用 UTF-8 文件和 `--prompt-file 'C:\路径\提示词.txt'`。普通中文参数和空格路径用引号包住即可。Python 输出固定 UTF-8；凭据使用 `%APPDATA%\ai-aggregation-platform\credentials`。

自动回归入口：`py -3 tests\test_cli.py`（开发验收用，附带离线测试素材，不产生平台费用）。PowerShell 包装器在 macOS 运行通过并不等于 Windows 原生验收通过，交付时必须区分。
