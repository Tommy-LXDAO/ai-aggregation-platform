# 接口和费用证据

统一 Base URL：`https://ai.yykkj.com/v1`。调用由脚本封装，不手写请求脚本。

| 功能 | 现成命令 | 接口 |
|---|---|---|
| 文本/视觉 | text.py | POST /chat/completions |
| 文生图 | image.py | POST /images/generations |
| 参考图/蒙版 | image.py edit | POST /images/edits，images[].image_url |
| 提交视频 | video.py / video.py create | POST /videos |
| 状态 | video.py status | GET /videos/{id} |
| 视频文件 | video.py download | GET /videos/{id}/content |
| 任务扣费 | video.py billing | GET /api/log/token，按 task_id 匹配 |

MiniMax-H3：JSON 参考素材在 `metadata.metaso_content`；本地文件按 multipart 的 `reference_image` / `reference_video` / `reference_audio` 上传。`metadata.metaso_resolution` 与 `metadata.metaso_ratio` 指定分辨率与比例。

H3 在本次服务端配置中的基础价格（**不是所有用户最终价格承诺**）：

- 768P：输出 $0.05/秒，输入视频 $0.05/秒。
- 2K：输出 $0.075/秒，输入视频 $0.075/秒。
- 参考图片前5张免费，之后 $0.02/张。
- 实扣还包含分组/用户特殊倍率；从日志读取。`quota_per_unit` 从 `/api/status` 读取，不能假设固定换算。
- 成功任务可能有差额扣费/退款；失败任务不能在退款日志出现前宣称已退。
- `/api/log/token` 只有最近日志，不是完整分页账本；旧任务记录缺失时 `verified=false`。
- `/api/pricing` 本站可能需要管理面板登录，不拿 Skill Key 调管理员配置，也不以其401推断模型不可用。
- 两个默认图片模型此次设为 $0.05/次。以实际消耗日志核对，不能用旧 token 计费示例推断。

官方插件指南： https://metaso.cn/minimax-h3/new-api-guide （New API 任务插件部分）。
