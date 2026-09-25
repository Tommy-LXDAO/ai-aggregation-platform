---
name: "AI聚合平台"
description: "调用 AI聚合平台 ai.yykkj.com（New API 中转站）做文字对话、生图、多图改图和 MiniMax-H3 视频生成。用户要配置 API Key、生成或修改图片、用文字/图片/视频/音频生成视频、查询下载任务或核对任务扣费时使用。直接执行随 Skill 附带的独立命令行脚本，支持 macOS 和 Windows；不读取 Codex / CC Switch 认证。"
---

# AI聚合平台

## 执行原则

**直接执行本 Skill 的脚本。不要为每次调用临时编写 Python/JS/curl、构造 JSON、编辑代码或安装 SDK。** AI 只负责根据用户意图拼接参数、运行脚本、交付实际产物。共用库已随 Skill 附带，用户不必配置代码。

先定位本文件所在目录；下面 `$S` 指该目录的 `scripts`，不是固定安装位置。

- macOS：`python3 "$S/image.py" ...` / `python3 "$S/video.py" ...`
- Windows：`py -3 "$S\image.py" ...` / `py -3 "$S\video.py" ...`，也可用已安装的 `python`。
- 仅需 **Python 3.9+，不需要 pip、Node、Go、curl 或 ffmpeg**。缺少 Python 时提示安装 python.org 的 Python 3；Windows 勾选添加到 PATH。
- `ffprobe` 可选：装有时会验证视频可解码、时长和分辨率；没有时仍可使用，但不能把容器检查称为解码验证。
- 旧入口 `newapi.sh` / `newapi.ps1` 保留，内部调用同一套 Python 脚本。

## 首次使用与 API Key

1. 首次调用先执行 `auth.py status`。脚本直接运行时也会检查认证。
2. `configured: false` 或 `AUTH_REQUIRED` 时，明确告知：
   **“请打开 https://ai.yykkj.com，先注册账号并登录，然后在平台充值，再进入「API 密钥 / 令牌」新建并复制本平台 API Key。安装 Skill 本身不收费，实际生成会消耗平台余额。你可以直接把 Key 发给我，我会替你写入；不需要你改代码或配置环境变量。”**
3. 用户给出完整 Key 后，**直接调用已有脚本保存**，不要求用户再手工创建文件、不反复确认、不强制先联网验证：

   ```bash
   python3 "$S/auth.py" set --key '用户提供的完整Key'
   ```

   Windows 同样使用 `py -3 "$S\auth.py" set --key '用户提供的完整Key'`。
   也支持 `auth.py set` 交互输入或 stdin。脚本输出不回显密钥。
4. 写入成功后继续用户的生成请求。需要单独诊断时运行 `auth.py check`（不消耗生成额度）；认证失败时指出是平台 Key/权限问题，不读取其他产品凭据顶替。

密钥独立保存在 macOS/Linux 的 `${XDG_CONFIG_HOME:-~/.config}/ai-aggregation-platform/credentials` 或 Windows 的 `%APPDATA%\ai-aggregation-platform\credentials`。`auth.py path` 可查位置；`auth.py clear` 可清除。重装 Skill 不影响密钥。不要复用 `OPENAI_API_KEY`、Codex、CC Switch 的认证。

## 生图 / 多图改图

```bash
python3 "$S/image.py" '一艘蓝色玩具船，白色背景，无文字' --out '/绝对路径/图片.png'
python3 "$S/image.py" edit '保持小船形状，把船身改为红色' --ref '/绝对路径/图片.png' --out '/绝对路径/改图.png'
python3 "$S/image.py" edit '综合两张参考图的设计' --ref '/绝对路径/图1.png' --ref 'https://可访问域名/图2.png' --quality high --out '/绝对路径/融合.png'
```

- `--ref`（别名 `--image`）可重复，支持本地 PNG/JPEG/WebP/GIF、HTTP(S) URL 或 data URL；有参考图就自动使用 `/images/edits`，不会误传到忽略参考图的生图接口。
- `--mask FILE或URL` 与 `--ref` 配合；可传多张参考图。蒙版是否生效由所选上游模型支持情况决定，不承诺所有渠道支持精确局部编辑。
- `--quality fast` 默认 `gpt-image-2.5-flare`；`high` 默认 `gpt-image-2.5-sunburst`；`--model` 可指定其他已开通图片模型。
- 上游每次仅返回1张。`--n 1..10` 表示**本地并发调用多次**，每次发送 `n=1` 并独立计费；`--concurrency 1..4` 默认2。多图输出自动命名 `文件-1.png`、`文件-2.png`。
- 批量请求有总回执和每张独立回执。部分失败时保留成功作品、返回非零退出码；`image.py download 总回执` 只恢复已有响应的下载，不重发失败请求，也不重新生成成功图片。
- `--ratio` 是提示词构图要求，**不是服务端硬性像素尺寸保证**。
- 成功结果会附带按 `request_id` 匹配的近期扣费日志；也可 `image.py billing '/路径/图片.png.request.json'` 单独核对。
- 失败/下载中断保留 `.request.json`，已有响应可用 `image.py download '/路径/图片.png.request.json'` 恢复，不重新收费生成。

## 视频 / 图片+视频+音频多模态

```bash
python3 "$S/video.py" '蓝色玩具船在浅水上漂浮，无人物无文字' --seconds 4 --resolution 768P --ratio 16:9 --out '/绝对路径/视频.mp4'
python3 "$S/video.py" '保持参考小船外形，让它轻轻漂浮' --image '/绝对路径/图片.png' --out '/绝对路径/图生视频.mp4'
python3 "$S/video.py" '保持图片主体，参考视频的运动和音频氛围' --image '/绝对路径/图片.png' --video '/绝对路径/参考.mp4' --audio '/绝对路径/配乐.mp3' --out '/绝对路径/多模态.mp4'
```

- 模型仅 `MiniMax-H3`。`--seconds` 整数 **4–15**；`--resolution 768P|2K`。
- 比例：`adaptive|21:9|16:9|4:3|1:1|3:4|9:16`。
- `--image`、`--video`、`--audio` 均可重复，支持本地文件、HTTP(S) URL、data URL。混合本地文件和 URL 也可以。
- 本地文件自动 multipart 上传；URL 自动放入插件的 `metadata.metaso_content`。不要求用户部署素材服务器或编写 JSON。
- 本地单图 ≤30 MiB、单视频 ≤50 MiB、单音频 ≤15 MiB，最多16个素材、本地总量≤180 MiB；这是脚本保护边界，不是上游承诺的全部组合限制。素材格式/组合被上游拒绝时原样报告，不自动换模型或反复扣费。
- 默认完整执行：提交 → 轮询 → 下载 MP4 → 本地验证 → 查询该任务扣费。`--poll-interval` 默认5秒，`--timeout` 默认1800秒。
- 只提交：`video.py create '提示词' --out '/路径/a.mp4'`。受理不等于成功。
- 恢复：`video.py wait TASK_ID --receipt '/路径/a.mp4.task.json'`，恢复原输出路径，不新建任务。
- 查询：`video.py status TASK_ID`；下载：`video.py download TASK_ID --out '/路径/a.mp4'`；账单：`video.py billing TASK_ID`。
- `/v1/models` 可能不列任务插件模型；**不得因为列表没有 H3 就宣称不可调用**。

## 参数、恢复与验收标准

- 中文、空格、引号路径均应正常加 shell 引号；提示词包含复杂引号/多行时可使用 `--prompt-file UTF8文件` 或 stdin。不要现场写调用脚本。
- `--dry-run` 只本地校验，无网络、无费用，不算真实生成验收。`--help` 查看全部参数。
- 生成 POST **绝不自动重试**。网络中断也可能已经扣费；先查回执和平台记录。查询 GET 有限重试。
- 输出/回执已存在会阻止重新生成，避免重复扣费或覆盖用户文件。`error_or_unknown` 不代表必定未受理。
- 成功交付必须取得实际图片/视频文件；视频还要明确最终状态。展示文件时使用绝对路径。
- `billing.verified` 只指该任务终态与最近令牌日志一致。日志缺失/权限不足时明确未验证，不能说免费或已退款。
- 请求秒数和 MP4 容器时长可能有小差异；收费以服务端 `usage_facts`、分组倍率和扣费日志为证，不根据容器时长猜账单。
- 实时定价以平台为准。H3 当前表达式配置参考见 [接口与计费](references/endpoints.md)，不能把静态文档当成账户实扣。
- Windows 用法与引号处理见 [Windows](references/windows.md)；首次配置见 [配置说明](references/onboarding.md)；错误排查见 [故障处理](references/troubleshooting.md)。

## 文字对话（保留功能）

```bash
python3 "$S/text.py" '写一句简短介绍' --model deepseek-v4.1-flash
python3 "$S/text.py" '描述图片' --image '/绝对路径/图片.png' --model 支持视觉的模型
```

`--system` 设置系统提示词；`--image` 需要所选模型本身支持视觉，不把普通文本模型当成视觉模型。`newapi.py models` 只读查询令牌可见的标准模型。
