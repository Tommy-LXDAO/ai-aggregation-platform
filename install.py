#!/usr/bin/env python3
"""Install the bundled skill and optionally save its independent platform API key."""
import argparse
import getpass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid


SKILL_NAME = 'ai-aggregation-platform'


def main():
    if sys.version_info < (3, 9):
        print('需要 Python 3.9+，无需 pip 或第三方依赖。', file=sys.stderr)
        return 1
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='安装 AI聚合平台 Skill，并引导平台注册、登录、充值与 API Key 配置。')
    parser.add_argument('--skills-dir', type=Path, default=Path.home()/'.agents'/'skills',
                        help='AI 客户端的 skills 父目录，默认 ~/.agents/skills')
    parser.add_argument('--key', help='直接保存用户提供的平台 API Key，不强制联网验证')
    parser.add_argument('--no-prompt', action='store_true', help='只安装和显示引导，不交互询问 Key')
    args = parser.parse_args()
    source = Path(__file__).resolve().parent/'skill'
    skills_dir = args.skills_dir.expanduser().resolve()
    target = skills_dir/SKILL_NAME
    if target.is_symlink():
        print('安装目标是符号链接，未替换；请使用 --skills-dir 指定普通目录。', file=sys.stderr)
        return 1
    if target == source or source in target.parents or target in source.parents:
        print('安装目标不能与仓库源码目录重叠。', file=sys.stderr)
        return 1
    if not (source/'SKILL.md').is_file() or not (source/'scripts'/'auth.py').is_file():
        print('缺少完整 skill 目录，请下载完整仓库，不要单独下载 install.py。', file=sys.stderr)
        return 1
    if target.exists() and (not target.is_dir() or not (target/'SKILL.md').is_file()):
        print('安装目标已存在且不是可识别的 Skill 目录，未覆盖。', file=sys.stderr)
        return 1

    print('AI聚合平台：https://ai.yykkj.com', flush=True)
    print('开通流程：注册账号并登录 → 在平台充值 →「API 密钥 / 令牌」新建 Key → 本地保存。', flush=True)
    print('已有账号或可用余额可跳过对应步骤。安装不收费，实际生成会消耗平台余额；安装器不会自动充值或调用生成接口。', flush=True)
    skills_dir.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.ai-aggregation-install-', dir=skills_dir))
    backup = None
    try:
        prepared = stage/SKILL_NAME
        shutil.copytree(source, prepared, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', '.DS_Store', 'credentials', '.env', '*.pem', '*.request.json', '*.task.json'))
        if target.exists():
            # Backups stay outside the skills directory so clients do not discover a duplicate skill.
            backup_dir = skills_dir.parent/'ai-aggregation-platform-backups'
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup = backup_dir/(SKILL_NAME+'-'+uuid.uuid4().hex)
            target.rename(backup)
        try:
            prepared.rename(target)
        except OSError:
            if backup is not None:
                backup.rename(target)
            raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    print('已安装：'+str(target), flush=True)
    if backup is not None:
        print('原版本已保留：'+str(backup), flush=True)

    auth_script = target/'scripts'/'auth.py'
    env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    status = subprocess.run([sys.executable, str(auth_script), 'status'], capture_output=True,
                            text=True, encoding='utf-8', env=env)
    if status.returncode != 0:
        print(status.stderr, file=sys.stderr, end='')
        return status.returncode
    configured = json.loads(status.stdout).get('configured', False)
    key = args.key
    if key is None and not configured and not args.no_prompt and sys.stdin.isatty():
        key = getpass.getpass('粘贴平台 API Key（直接回车可稍后配置）: ').strip() or None
    if key is not None:
        result = subprocess.run([sys.executable, str(auth_script), 'set'], input=key,
                                text=True, encoding='utf-8', env=env)
        if result.returncode != 0:
            print('Skill 已安装，但 Key 未保存；请根据错误修正后运行 auth.py set。', file=sys.stderr)
            return result.returncode
        print('Key 已保存。需要诊断时可运行 auth.py check；未自动联网验证或生成。')
    elif configured:
        print('已有独立平台 Key，继续保留，不修改凭据。')
    else:
        print('Skill 已安装，尚未配置 Key。可把 Key 交给 AI 代写，或执行：')
        print('"'+sys.executable+'" "'+str(auth_script)+'" set')
    print('在 AI 客户端中刷新/重新加载 Skill 后使用“AI聚合平台”；也可直接运行已安装的 image.py / video.py。')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print('安装失败：'+str(error), file=sys.stderr)
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print('\n已停止交互，未自动提交任何生成请求。可以稍后运行 auth.py set。', file=sys.stderr)
        sys.exit(130)
