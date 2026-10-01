"""Native Skill linking stays product-owned and does not install agents."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNTIMES = ("claude", "codex", "opencode", "omp")


def powershell_ready():
    if not shutil.which("pwsh"):
        return False
    result = subprocess.run(["pwsh", "-NoLogo", "-NoProfile", "-Command", 'Write-Output "ready"'],
                            capture_output=True, text=True, timeout=15)
    return result.returncode == 0 and "ready" in result.stdout


PWSH_READY = powershell_ready()


class SkillLinkingTests(unittest.TestCase):
    linkers = ("sh",)

    def fixture(self, base):
        base = base.resolve()
        repo = base / "product checkout"
        scripts = repo / "scripts"
        scripts.mkdir(parents=True)
        for stem in ("link-skills", "link-claude-skills"):
            for suffix in ("sh", "ps1"):
                shutil.copy2(ROOT / "scripts" / f"{stem}.{suffix}", scripts)
        self.skill(repo / "skills/alpha")
        self.skill(repo / "skills/zeta")
        homes = {runtime: base / "homes" / runtime for runtime in RUNTIMES}
        homes["opencode"] = base / "config home" / "opencode"
        env = dict(os.environ, CLAUDE_CONFIG_DIR=str(homes["claude"]),
                   CODEX_HOME=str(homes["codex"]),
                   XDG_CONFIG_HOME=str(homes["opencode"].parent),
                   PI_CODING_AGENT_DIR=str(homes["omp"]))
        return repo, homes, env

    @staticmethod
    def skill(directory):
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text(
            f"---\nname: {directory.name}\ndescription: Fixture.\n---\nOriginal.\n")

    def run_linker(self, kind, repo, env, runtime, legacy=False, success=True):
        stem = "link-claude-skills" if legacy else "link-skills"
        command = (["sh", str(repo / "scripts" / f"{stem}.sh")] if kind == "sh" else
                   ["pwsh", "-NoLogo", "-NoProfile", "-File", str(repo / "scripts" / f"{stem}.ps1")])
        if not legacy:
            command += [runtime] if kind == "sh" else ["-Runtime", runtime]
        result = subprocess.run(command, cwd=repo, env=env, text=True,
                                capture_output=True, timeout=30)
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_four_native_homes_updates_and_legacy_claude_entry(self):
        for kind in self.linkers:
            with self.subTest(linker=kind), tempfile.TemporaryDirectory() as tmp:
                repo, homes, env = self.fixture(Path(tmp))
                for runtime in RUNTIMES:
                    self.run_linker(kind, repo, env, runtime)
                self.run_linker(kind, repo, env, "claude", legacy=True)
                manifest = repo / "skills/alpha/SKILL.md"
                manifest.write_text(manifest.read_text().replace("Original", "Updated"))
                for home in homes.values():
                    self.assertIn("Updated", (home / "skills/alpha/SKILL.md").read_text())
                    self.assertEqual({p.name for p in home.iterdir()}, {"skills"})
                shutil.rmtree(repo / "skills/alpha")
                self.skill(repo / "skills/beta")
                foreign = Path(tmp) / "foreign"
                foreign.mkdir()
                for runtime, home in homes.items():
                    (home / "skills/foreign").symlink_to(foreign, target_is_directory=True)
                    self.run_linker(kind, repo, env, runtime)
                    self.run_linker(kind, repo, env, runtime)
                    self.assertFalse(os.path.lexists(home / "skills/alpha"))
                    self.assertTrue((home / "skills/beta/SKILL.md").is_file())
                    self.assertEqual((home / "skills/foreign").resolve(), foreign.resolve())

    def test_conflict_preserves_foreign_entries_and_stale_links(self):
        for kind in self.linkers:
            with self.subTest(linker=kind), tempfile.TemporaryDirectory() as tmp:
                repo, homes, env = self.fixture(Path(tmp))
                skills = homes["omp"] / "skills"
                (skills / "zeta").mkdir(parents=True)
                marker = skills / "zeta/keep.txt"
                marker.write_text("preserve")
                (skills / "stale").symlink_to(repo / "skills/deleted", target_is_directory=True)
                self.run_linker(kind, repo, env, "omp", success=False)
                self.assertEqual(marker.read_text(), "preserve")
                self.assertTrue((skills / "stale").is_symlink())
                self.assertFalse((skills / "alpha").exists())
                shutil.rmtree(skills / "zeta")
                foreign = Path(tmp) / "foreign"
                foreign.mkdir()
                (skills / "zeta").symlink_to(foreign, target_is_directory=True)
                self.run_linker(kind, repo, env, "omp", success=False)
                self.assertEqual((skills / "zeta").resolve(), foreign.resolve())
                self.assertTrue((skills / "stale").is_symlink())


@unittest.skipUnless(PWSH_READY, "PowerShell 7 is absent or its runtime cannot initialize")
class PowerShellSkillLinkingTests(SkillLinkingTests):
    linkers = ("ps1",)


if __name__ == "__main__":
    unittest.main()
