# 一次配置

打开 https://ai.yykkj.com → 注册账号并登录 → 在平台充值 →「API 密钥 / 令牌」→ 新建 → 复制本平台 Key。

安装 Skill 本身不收费；生图、生视频等实际调用会消耗平台余额。已有账号直接登录；已有可用余额不需要重复充值。配置 Key 不会替用户注册、登录或充值，也不进行自动扣款。
用户可以直接把 Key 提供给 AI。AI 调用 Skill 已有的 `scripts/auth.py set --key '完整Key'` 保存即可，不要求用户编辑代码、JSON 或环境变量，也不强制验证后才保存。

- macOS：`python3 '/Skill绝对路径/scripts/auth.py' set`
- Windows：`py -3 'C:\Skill路径\scripts\auth.py' set`
- 交互输入、stdin 和 `--key` 都支持。
- `status` 只检查本地是否配置；`check` 访问 `/v1/models` 验证权限，不生成作品。
- 密钥持久化在独立配置目录，不在 Skill 内；仅使用该平台凭据，升级脚本不会覆盖 Key。
- 已配置时直接执行，不让用户每次重填。401/403 时说明 Key/权限问题，再按用户提供的新值更新。
