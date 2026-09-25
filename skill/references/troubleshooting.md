# 排错和恢复

- `AUTH_REQUIRED`：打开 https://ai.yykkj.com，注册账号并登录 → 充值 →「API 密钥 / 令牌」创建 Key；用户给出 Key 后执行 auth.py set；不读取其他产品认证。
- `HTTP 401/403`：已写入不等于有效，运行 auth.py check 检查 Key/权限。
- `task model ... has no usage expression or meter`：服务端任务模型尚未配置计费表达式，不是脚本没找到模型。
- `/v1/models` 不列 H3：任务插件可能不进入标准模型清单，以视频接口实际结果为准。
- `HTTP 400`：查看保留的服务端错误和 request_id；检查模型、素材、时长与分组。不要无脑重试付费请求。
- `error_or_unknown` / POST超时 / 非JSON响应：可能已受理；不要因为没有收到成功响应就重复生成。查平台最近请求或任务。
- 视频超时：`video.py wait TASK_ID --receipt '/原回执路径'` 恢复；不再次 generate。
- 视频失败：失败终态、原始错误和退款核对结果保留在回执。`video.py billing TASK_ID` 可重新核对退款。
- 图片下载失败：`image.py download '/图片.request.json'` 从保存的响应恢复；回执不存在且响应丢失时不能保证重新取得旧产物。
- 输出/回执已存在：保护原文件并阻止重复生成。若确实需要全新作品，选择新输出名，不删除旧回执后盲重试。
- 已完成但计费 `verified=false`：可能日志尚未写入、已超出最近日志窗口，或只读日志权限不足；不等于零费用。
- 本地媒体报错：空文件、类型错误、过大素材、ffprobe 检测失败会在提交前拒绝；服务器读取 URL 失败则属于服务端错误。
- 脚本 stdout 是 JSON，stderr 是进度/错误；非零退出码表示未完成，3 专指缺少认证。
