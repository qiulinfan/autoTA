# AutoTA

**English** | [简体中文](README.zh-CN.md)

AutoTA is a portable, evidence-driven technical-art pipeline. It turns an art
requirement (a design brief's visual/audio needs) into license-verified or
generated assets with receipts, and hands engine integration to the target
project's own workflow. It is the **midstream** of a game production line:
upstream design docs state what is needed; AutoTA sources, generates, adapts,
and audits it; the target project (e.g. a CCGS/Codex game-studio setup)
integrates and verifies it in-engine.

Five portable Agent Skills:

- `search-game-art` — requirement matrix, source-covered search, per-item
  license verification, audited acquisition; programmatic CC0 acquisition for
  uniformly licensed sources (Poly Haven API).
- `create-2d-game-art` — deterministic 2D raster production (pixelize,
  sequence, pack, audit) with closed-schema receipts.
- `auto-ta` — Blender-side 3D technical art: authoring, adaptation, the
  isolated audit chain, round-trip validation, downstream optimization.
- `generate-hosted-game-art` — hosted generation via user-supplied Meshy /
  Tencent Hunyuan credentials: free capability probe, budget-authorized
  batches, generation receipts. Tripo AI is supported through the separate
  [Tripo adapter](scripts/tripo-adapter.md).
- `character-rig-animation-alignment` — humanoid × external animation
  alignment and engine-ready retargeting acceptance.

Plus `workflows/handoff-contract.md` (the receipt/gate schema every delivery
shares), two namespaced Codex agents (`autota_technical_artist`,
`autota_art_scout`), and one disabled-by-default project profile.

## Position in a production line

1. **Upstream (design)**: the game project's design docs state visual/audio
   requirements — that text is the design brief AutoTA consumes. Users can also
   specify the asset directly through a text description or images.
2. **Midstream (AutoTA)**: source or generate the asset, adapt it in Blender,
   audit it, and emit a receipt. Deliveries stay `prototype` until the named
   gates pass; a receipt never converts `not_tested` into a pass.
3. **Downstream (engine)**: the target project imports the delivery, wires it
   into scenes, and verifies in-engine with its own tools. AutoTA never
   mutates the game project's scenes on its own authority.

## Asset creation and sourcing

Choose the production route with the user before starting, unless it is already
specified or the user delegates the decision. Compare the expected result,
provider credits, agent tokens and likely repair work together.

| Route | When it fits | Handoff |
| --- | --- | --- |
| Licensed existing assets | A suitable asset can be adapted efficiently | Use `search-game-art` to verify style, technical contents and licensing before acquisition |
| Direct Blender authoring | Objects built from simple geometric parts, logical component structure, editable UVs, or exact text and numerals | Author locally, then audit and export |
| Meshy / Tencent Hunyuan | Hosted generation selected for the brief | Use `generate-hosted-game-art` with authorized credentials and budget |
| Tripo API | Explicit API generation with task tracking | Use the [Tripo adapter](scripts/tripo-adapter.md), then continue local inspection and integration |
| Tripo Studio web | Interactive generation using a Studio account | User manually downloads or uses Send to Blender / Studio Bridge; AutoTA resumes after local transfer |

For sourced 3D assets, prefer usable PBR material coverage beyond base color.
Check actual maps and account for missing-channel work. Simplified geometry is
appropriate when it matches the brief; do not select a cartoon/geometric asset
for a different style merely because it is free or low-poly.

Tripo defaults to the **P2 family**, subject to current availability and explicit
user overrides. The web route defaults to **text-to-model, Smart Mesh, quad
topology and 2K textures**. Verify available controls and credit costs before
submission. Web and API are separate routes: do not silently switch between them
or assume their credits are shared. See [runtime routing](skills/auto-ta/references/runtime-routing.md).

The API adapter implements balance checks, explicit submissions and task queries;
download/extraction and Blender/Unity orchestration are handled by the surrounding
asset job. A provider's quad, face-count or UV flags do not guarantee the delivered
mesh. API `export_uv` is not proof of Smart UV support. The web route includes a
human transfer step and is not an unattended end-to-end pipeline.

## Game-asset standards and adaptation

At the first asset conversation after deployment, ask once about the user's
standards unless already supplied or saved. Reuse accepted preferences;
explicit per-asset instructions take precedence.

These are configurable defaults:

| Area | Default |
| --- | --- |
| Editable topology | Triangles and quads only; no n-gons. Prefer quads and deformation-aware edge flow for deforming organic assets. Rigid props may use useful mixed topology; retain quads where editing benefits |
| Polygon budget | Usually 300–1000 polygons for small props; around 2000 for larger props, chosen by complexity and on-screen importance, with ±20% tolerance. Report engine triangles separately |
| Textures | 2048 × 2048, with appropriate PBR channels and color/data semantics |
| UVs and padding | Readable layouts, intended overlap policy and adequate spacing. Extend island-edge pixels into unused atlas space while preserving valid texels; check seams and mip behavior |
| Repair effort | Keep satisfactory assets; locally repair small defects. Consider reconstruction for important or visibly detailed assets, or severe defects that local repair cannot economically resolve |

Quads alone do not guarantee good deformation, and a few triangles do not justify
remeshing. Physical size alone does not determine importance. See the full
[asset standards](skills/auto-ta/references/asset-standards.md).

The optional [reconstruction helper](skills/auto-ta/references/mesh-reconstruction.md)
creates a new static-mesh candidate using voxel remeshing, QuadriFlow, UV unwrapping
and PBR rebaking. It extends unused atlas texels on all four baked maps using an
explicit UV coverage mask. It preserves the input and bounds retries; it is not
suitable for rigs, shape keys or transparent source materials. Reconstruction
outputs remain candidates until visual, geometry, UV, export and engine checks pass.

## Unity delivery

Integrate only into the user-authorized project and follow its render pipeline.
Reuse a clearly established model library such as an appropriate Art/Arts folder;
use Resources only when consistent with the project's existing convention.
Otherwise, use `Assets/AutoTA_Models`.

Name item folders, models and prefabs `category_Features`, for example
`sofa_RedThreeSeat` or `clock_RedAlarm`. Keep one shared batch import script and
per-item configuration outside `Assets`; when Unity needs a compiled Editor
script, stage it temporarily and remove it after saved results are verified.
This is an execution convention, not a bundled universal Unity importer.

Do not create a saved validation scene for every model by default. Users may drag
the asset into their own scene; agent checks can use an authorized existing scene,
Prefab Mode or a temporary unsaved preview. Pending visual checks remain
`not_tested`. See [Unity asset layout](skills/auto-ta/references/unity-asset-layout.md).

## Link the working tree into Codex

The linkers point Codex directly at this checkout. Editing a Skill or custom
agent here therefore changes what a newly started Codex task loads; no copied
installation is created.

Runtime requirements are Python 3.11+ and `uv` on every platform. `uv` runs
Skills with their locked inline dependencies; doctor fails closed when it is
missing. On macOS, use iTerm2 as the terminal emulator and run the POSIX
lifecycle in `zsh` or `bash`;
iTerm2 is not itself a shell, and PowerShell is not a macOS requirement. Linux
uses the same POSIX lifecycle. Windows uses PowerShell 7+ (`pwsh`) for the
Windows lifecycle scripts. Windows PowerShell 5.1 is unsupported,
and the PowerShell entrypoints fail before mutation when invoked by an older
host.

macOS — open the checkout in iTerm2, then run these commands in `zsh` or
`bash`:

~~~sh
./scripts/link.sh
./scripts/doctor.sh
~~~

Linux — run the same POSIX entrypoints in a POSIX shell:

~~~sh
./scripts/link.sh
./scripts/doctor.sh
~~~

Windows — run the Windows entrypoints in PowerShell 7:

~~~powershell
pwsh -NoProfile -File .\scripts\link.ps1
pwsh -NoProfile -File .\scripts\doctor.ps1
~~~

Set `CODEX_HOME` or pass an explicit home path as the first argument. Existing
real files or directories are never overwritten. Use `-Force` (PowerShell) or
`--force` (POSIX) only to replace a conflicting symbolic link; the scripts
still refuse to replace non-links.

Before the first `CODEX_HOME` write, the linker validates the manifest and its
exact Skill, agent, workflow, and profile inventories. It then creates direct
links for the five Skills, two namespaced agents, and the complete product
root at `${CODEX_HOME}/workflow-products/autota`. Skills resolve bundled
scripts and the handoff contract only through linked locations, so they work
from an unrelated game cwd.

The linker atomically records every managed destination, canonical source, kind,
and observed link type at
`${CODEX_HOME}/state/autota/install-receipt.json`. The receipt is bound to
this exact checkout and the AutoTA namespaces. Re-linking removes a
receipt-owned stale symlink/junction after a manifest rename or deletion;
unlinking uses the receipt rather than only the current disk inventory.
Corrupt, wrong-checkout, wrong-owner, or real destinations are preserved and
reported instead of guessed. `CODEX_HOME` must not equal, contain, or be
contained by this repository, because that would make the product-root link
recursive.

Unlink only receipt-owned entries that can still be proven to target this
checkout. On macOS, run the POSIX command in `zsh` or `bash` inside iTerm2; use
the same command on Linux:

~~~sh
./scripts/unlink.sh
~~~

On Windows, use PowerShell 7:

~~~powershell
pwsh -NoProfile -File .\scripts\unlink.ps1
~~~

Restart Codex after changing linked Skills or custom-agent configuration.
On Windows, Skill directories use junctions. Agent files use symbolic links when
available and same-volume hard links as the non-admin fallback. Because a Git
operation can replace a hard-linked file inode, run doctor after switching or
updating this bundle. A detached hardlink whose original source identity no
longer exists cannot be proven owned from its path; doctor/link/unlink fail
safely and preserve it for manual inspection. The lifecycle does not promise
automatic stale cleanup for that fallback. Enable Windows Developer Mode so
agent symlinks can be used when rename/delete cleanup must remain automatic.

Claude Code, OpenCode, and OMP integration is skills-only. Run
`scripts/link-skills.sh claude`, `opencode`, or `omp` on POSIX/WSL, or
`scripts/link-skills.ps1 -Runtime claude` / `opencode` / `omp` in PowerShell 7.
The existing `link-claude-skills` entry points remain available. The linker
uses each runtime's native `skills/` directory and preserves foreign entries;
rerun after pulling or changing the Skill inventory, then start a new session.
Bundled scripts resolve from all four runtime homes. Full product integration
and custom agents keep the Codex contract above.

## Profiles are explicit

The portable core never auto-selects a profile. A target repository or user
must explicitly choose one:

- `dreamweaver`: project workspace facts and historical retargeting case
  evidence.

Profiles can narrow paths and delivery adapters. They cannot expand user
authority or weaken validation, licensing, or workspace boundaries.

## Validate

The optional reconstruction helper has real Blender tests (no provider calls):
set `AUTOTA_TEST_BLENDER` to the installed Blender executable and run
`python -m unittest discover -s tests -p 'test_reconstruction*.py' -v`.
Without that variable, DCC integration tests skip while policy tests still run.

On macOS, open iTerm2 and run the complete POSIX validation path in `zsh` or
`bash`. Linux uses the same commands:

~~~sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s scripts -p test_tripo_client.py -v
python3 -m compileall -q skills scripts tests
sh -n scripts/link.sh scripts/unlink.sh scripts/doctor.sh
./scripts/doctor.sh --skip-link-check

codex_home="${CODEX_HOME:-$HOME/.codex}"
validator="$codex_home/skills/.system/skill-creator/scripts/quick_validate.py"
for skill_dir in skills/*; do
    [ -d "$skill_dir" ] || continue
    uv run --with pyyaml python "$validator" "$skill_dir"
done

git diff --check
~~~

This macOS path neither invokes nor requires `pwsh`. On Windows, run the
equivalent validation in PowerShell 7:

~~~powershell
$env:PYTHONUTF8 = '1'
python -m unittest discover -s tests -v
python -m unittest discover -s scripts -p test_tripo_client.py -v
python -m compileall -q skills scripts tests
pwsh -NoProfile -File .\scripts\doctor.ps1 -SkipLinkCheck
$codexHome = if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
    Join-Path $env:USERPROFILE '.codex'
} else {
    [System.IO.Path]::GetFullPath($env:CODEX_HOME)
}
$validator = Join-Path $codexHome 'skills\.system\skill-creator\scripts\quick_validate.py'
Get-ChildItem .\skills -Directory | ForEach-Object {
    uv run --with pyyaml python $validator $_.FullName
}
git diff --check
~~~

The tests use temporary Codex homes and do not modify the user's live Codex
installation.

## License status

No license could be established from the source checkout, public repository
metadata, or the new empty remote. This repository intentionally has no `LICENSE` file
until the owner selects terms. Do not infer permission to copy, redistribute,
or publish this work from repository visibility alone.
