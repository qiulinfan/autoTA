# Runtime routing

Probe capabilities at the start of each job. Tool names and installed products change; this file describes decisions, not assumed inventory.

## Blender

For a known executable, verify a clean background process before depending on it:

On macOS, run this in `zsh` or `bash` inside iTerm2; use the same POSIX command
on Linux:

```sh
"$blender_bin" --background --factory-startup \
  --python-expr 'import bpy,sys; print(bpy.app.version_string); print(sys.version.split()[0]); print(bpy.app.background)'
```

On Windows, use PowerShell 7:

```powershell
& $BlenderBin --background --factory-startup --python-expr "import bpy,sys; print(bpy.app.version_string); print(sys.version.split()[0]); print(bpy.app.background)"
```

Use a live Blender MCP when the user wants the currently open scene, the add-on bridge responds to a read-only query, and the exposed tool schema matches the instructions. Use headless Blender when creating or auditing a new isolated asset and the required operations are available through `bpy`.

Do not use headless Blender as a silent fallback for an unsaved open scene; it cannot see that state. Record the Blender version because `bpy` APIs, render engines, animation data, and export behavior differ between releases. Prefer feature detection over version-string branching.

Open an externally sourced `.blend` for first-pass audit only with `--background --factory-startup --disable-autoexec --offline-mode --python-exit-code 1`, with the isolation flags placed before the file argument. Treat Python-dependent drivers as unevaluated in that pass. Enabling auto-execution requires a trusted source or explicit user authorization and a separate receipt. Confine reports to a declared output root and use fresh run ids, input hashes, and atomic writes so an old pass report cannot survive a crashed invocation.

glTF/GLB physical units are meters; the clean-import audit rejects `--meters-per-unit` overrides for those formats. Use an explicit conversion only for a non-metric `.blend` contract or FBX, whose unit and axis behavior must be declared and tested.

## Unity

Before mutation, retrieve the Editor version, ready state, project root, active scene, installed render pipeline, and relevant packages. The connected project is not automatically the authorized project.

Use core asset/material/scene operations first. Treat optional tool groups such as ProBuilder, VFX Graph, Animation Rigging, or provider-backed asset generation as unavailable until both the tool and matching Unity package are verified. Do not add a Unity package just because an MCP tool group exists.

## Image generation

Image generation is appropriate for concept sheets, decals, masks, texture source imagery, and reference turnarounds that support a 3D asset. Standalone 2D art, sprite creation, and sprite-sheet production are outside this Skill. Image generation does not directly prove seamless tiling, physically meaningful material values, consistent orthographic views, mesh topology, rigging, animation, or engine compatibility. Validate and transform the image for its downstream 3D role.

## Existing assets

Invoke `search-game-art` when purchasing, downloading, or adapting a licensed asset is more efficient than creating it. Keep search claims separate from archive inspection and engine validation. Never infer redistribution or commercial permission from “free.”

## Hosted 3D and texture providers

Provider-backed generation runs through `$generate-hosted-game-art` (Meshy and
Tencent Cloud, from a user-supplied credential file). Resolve the route with the
user under [asset-standards.md](asset-standards.md), unless already selected or
delegated. Credentials alone do not select hosted generation over direct Blender
authoring. P2 is the Tripo default, subject to availability and user overrides.
Before use, establish
the provider and model/version, expected charge or quota (via that Skill's free
probe), upload boundary, content and license terms, credential availability
without exposing the secret, output formats, and independent audit route.

Provider success means only that output was returned. Run the same geometry, material, rig, visual, export, and engine gates as locally authored assets.

### Tripo API (opt-in product adapter)

For an explicitly requested Tripo API route, use the product's
`scripts/tripo_client.py` and [Tripo adapter guide](../../../scripts/tripo-adapter.md),
which contains official documentation, billing, pricing and credential links.
Resolve the real Skill path to its product root and verify both files exist;
alternatively use the runtime's linked `workflow-products/autota` root. Never
resolve a relative `scripts/` path from the target game's cwd. If a standalone
Skill copy lacks the product adapter, report that capability as unavailable;
do not claim the Meshy/Tencent helper already supports Tripo.

Probe balance read-only; explicit payment/upload authorization is still needed
for submission. Use a fresh stage per paid operation, retain task IDs and query
existing tasks after interruptions. Never retry a timed-out POST blindly. Do
not infer Smart UV support from `export_uv`, or quad/face guarantees from request
flags. Audit artifacts independently and select keep/local repair/reconstruct
using the user's saved standards, importance and observed defects.

### Tripo Studio web (manual transfer handoff)

Tripo Studio web is an alternative to the API. Honor the user's selected route;
do not switch a web task to paid API generation implicitly. Default new web
generation to text-to-model, Smart Mesh, quad topology and 2K textures unless
the current task or saved preferences override them. Verify available controls,
selected model/version, generation count and displayed credit cost before a
budget-authorized submission. Do not assume web and API credits are shared, web
is always cheaper, or a generation preset guarantees the delivered topology,
texture resolution, Smart UV or PBR channels.

After generation, ask the user to transfer the selected asset by either manual
download to the agreed local directory or the existing Studio Bridge's Send to
Blender / My Assets download button. This transfer is a deliberate human handoff
by default, not a requirement to automate browser downloads or Bridge clicks.
Do not bypass Chrome security warnings or install/configure a bridge solely to
avoid the handoff. Do not confuse Studio Bridge with the Blender Tripo API
Generator. Reuse an existing generated asset rather than generating it again
because transfer is pending.

Continue after the local files or intended Blender scene are available. Record
the Studio asset identity, selected variant, transfer method and actual file
hashes when saved. A Bridge 'transfer success' message alone does not prove
Blender import, materials or persistence: inspect the received objects, UVs,
image dependencies and actual texture sizes. Preserve unsaved user scenes;
request a saved copy if the only available audit route is headless Blender.
Use the normal autoTA audit, repair, export and Unity handoff gates afterward.

For batches, prefer a separate named collection per asset in a staging file,
or separate Blend files when materials, scale or identity would be ambiguous.
Track and audit each asset independently; never join unrelated assets merely
for transfer convenience. Do not claim this route is unattended end-to-end.

## Incompatible instruction sets

An external Skill is not executable merely because its topic matches. Reject or adapt it when it assumes MCP tool names that are not exposed, a different agent runtime or hard-coded home directory, an absent CLI/gateway/DCC/add-on/package/service, implicit installation or credential use, or a render image as a substitute for an editable 3D deliverable.

Record the mismatch in the receipt. Do not fabricate tool calls named by the external Skill.
