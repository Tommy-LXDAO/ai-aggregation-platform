"""Offline installation contracts; all destinations and credentials are temporary."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallationContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='平台 install ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skills = self.root/'skills'
        self.target = self.skills/'ai-aggregation-platform'
        self.credentials = self.root/'config'/'credentials'
        self.env = {**os.environ, 'HOME': str(self.root), 'USERPROFILE': str(self.root),
                    'AI_AGG_CONFIG_DIR': str(self.credentials.parent), 'AI_AGG_API_KEY': '',
                    'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUTF8': '1'}

    def invoke(self, *args, default_location=False):
        command = [sys.executable, str(ROOT/'install.py')]
        if not default_location:
            command += ['--skills-dir', str(self.skills)]
        return subprocess.run(command+list(args), input='', capture_output=True,
                              text=True, encoding='utf-8', env=self.env, timeout=25)

    def test_fresh_install_without_key_has_platform_guidance(self):
        result = self.invoke('--no-prompt')
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in ('https://ai.yykkj.com', '注册', '登录', '充值', 'API', '尚未配置'):
            self.assertIn(text, result.stdout)
        self.assertEqual((self.target/'scripts'/'image.py').read_bytes(), (ROOT/'skill/scripts/image.py').read_bytes())
        self.assertTrue((self.target/'tests/fixtures/clip.mp4').is_file())
        self.assertFalse(self.credentials.exists())

    def test_supplied_key_is_saved_without_generation_or_validation(self):
        key = 'offline-install-test-key'
        result = self.invoke('--key', key)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('API_KEY='+key, self.credentials.read_text(encoding='utf-8'))
        self.assertIn('未自动联网验证或生成', result.stdout)
        self.assertIn('充值', result.stderr)
        self.assertNotIn(key, result.stdout+result.stderr)
        self.assertFalse(list(self.target.rglob('*.task.json')))
        self.assertFalse(list(self.target.rglob('*.request.json')))

    def test_upgrade_retains_credentials_and_previous_skill(self):
        self.assertEqual(self.invoke('--key', 'existing-test-key').returncode, 0)
        before = self.credentials.read_bytes()
        (self.target/'local-note.txt').write_text('keep original', encoding='utf-8')
        result = self.invoke('--no-prompt')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.credentials.read_bytes(), before)
        self.assertIn('已有独立平台 Key', result.stdout)
        backups = list((self.skills.parent/'ai-aggregation-platform-backups').iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0]/'local-note.txt').read_text(), 'keep original')
        self.assertFalse((self.target/'local-note.txt').exists())
        self.assertEqual([p.name for p in self.skills.iterdir()], ['ai-aggregation-platform'])

    def test_foreign_directory_is_not_overwritten(self):
        self.target.mkdir(parents=True)
        marker = self.target/'important.txt'
        marker.write_text('keep', encoding='utf-8')
        result = self.invoke('--no-prompt')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_text(), 'keep')
        self.assertFalse((self.target/'SKILL.md').exists())

    def test_invalid_key_keeps_existing_credentials(self):
        self.assertEqual(self.invoke('--key', 'valid-offline-key').returncode, 0)
        before = self.credentials.read_bytes()
        result = self.invoke('--key', 'invalid key')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.credentials.read_bytes(), before)
        self.assertIn('Key 未保存', result.stderr)
        self.assertTrue((self.target/'SKILL.md').is_file())

    def test_source_overlap_is_rejected_without_changes(self):
        before = (ROOT/'skill/SKILL.md').read_bytes()
        result = self.invoke('--skills-dir', str(ROOT/'skill'), '--no-prompt')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('重叠', result.stderr)
        self.assertEqual((ROOT/'skill/SKILL.md').read_bytes(), before)
        self.assertFalse((ROOT/'skill/ai-aggregation-platform').exists())

    def test_default_destination_uses_current_user_home(self):
        result = self.invoke('--no-prompt', default_location=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root/'.agents/skills/ai-aggregation-platform/SKILL.md').is_file())

    def test_noninteractive_install_never_waits_for_key(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('尚未配置 Key', result.stdout)
        self.assertFalse(self.credentials.exists())
        status = subprocess.run([sys.executable, str(self.target/'scripts/auth.py'), 'status'],
                                capture_output=True, text=True, encoding='utf-8', env=self.env, timeout=10)
        self.assertFalse(json.loads(status.stdout)['configured'])
        for word in ('注册', '充值', 'https://ai.yykkj.com'):
            self.assertIn(word, status.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
