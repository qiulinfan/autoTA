# Optional reconstruct and rebake route

Use after the importance/defect decision in [asset-standards.md](asset-standards.md).
This is a bounded static-mesh adaptation recipe, not the default for every asset.
Do not apply it to rigs, animation, shape keys, deliberate open sheets, or assets
whose exact authored topology/UVs must be preserved. Keep the original immutable.

## Execution

Resolve `scripts/blender_reconstruct.py` from this installed Skill's real path.
Run `--help` rather than reading the implementation into context on every job.
Use isolated background Blender with `--factory-startup --disable-autoexec
--offline-mode --python-exit-code 1 --python <script> -- ...`.

Required arguments: `--input-file`, `--output-dir` (new directory),
`--target-faces`, `--voxel-size-m`. Select specific meshes with repeated
`--object`; specify `--meters-per-unit` for ambiguous non-metric sources.
Optional: `--texture-size` (default 2048), `--tolerance` (default 0.2),
`--max-surface-error-m` and `--seed`. The helper never invokes a paid provider.

The helper copies selected static meshes, applies transforms on copies, voxel
remeshes and runs QuadriFlow, unwraps a new atlas, and bakes base color,
roughness, metallic and tangent-space normals from the original surfaces. It
saves an editable blend, an FBX, a map set per selected mesh, before/after captures and a
compact `reconstruction-report.json`. The helper is a candidate producer, not
the autoTA audit/receipt validator. Nonselected input meshes are not delivered.

The voxel size is in meters. Choose it relative to the smallest retained detail;
the script refuses components thinner than four voxels, changed component counts,
large bounds changes, excessive measured surface displacement, unsupported
materials, or a result outside the ±20% budget. It reports a failure rather than
silently removing parts, rebuilding them as arbitrary primitives, or retrying.
Its sampled nearest-surface measurement is diagnostic, not a Hausdorff proof.

## Preserve appearance and components

- Inspect thin parts and disconnected shells before choosing voxel size. Keep
  them out of the remesh route or handle them separately if they are at risk.
  A specific furniture-leg repair is not a universal small-component rule.
- Do not automatically cap every hole: a nonplanar or branched boundary can
  create surfaces across cushions, cavities or seams. Diagnose such areas and
  use a local patch/copy when needed before invoking the helper.
- Recalculate consistent normals, remove near-zero edges at the working scale,
  and verify that QuadriFlow actually reduced the mesh; the operator can return
  after a warning without a useful remesh.
- Set final smooth normals before tangent-space baking. Copy/rebake real PBR
  channels with color/non-color semantics; never substitute a color image for
  a normal or mask. New UVs are allowed during this adaptation stage, but must
  remain stable during the subsequent export/import comparison.
- Inspect before/after silhouette, small parts, seams, close-ups and target-camera
  appearance. Reject a technically closed mesh if its shape or bake regressed.

## Keep token use bounded

Run one candidate with the chosen parameters; inspect its summary and comparison
images. On failure, inspect just the named failing stage and relevant evidence.
Allow at most one diagnosed local rerun per decision; do not blindly retry or
cycle through providers. Escalate to a targeted repair plan when the route is
unsuitable. Reuse existing outputs after an interruption rather than rerunning
generation or baking. Do not repeatedly dump source, full logs or packed data.

## Acceptance after the helper

Run the existing source audit, extra self-intersection and UV checks, clean FBX
or GLB import comparison, and authorized engine verification. Check normals,
texture identity, tangent convention, chart padding and material mapping. The
helper's zero-boundary count is insufficient. The helper bakes an explicit target UV coverage mask and fills unused texels
on all four maps using deterministic jump-flood nearest-seed approximation.
Covered RGBA pixels remain unchanged; each map copies its own channel values.
This opaque-material helper does not support transparent source materials.
Full background extension does not replace engine mip/seam inspection. Bind captures, scripts and output
hashes to the final receipt. Preserve limitations as `prototype` or failures;
never modify the standard comparator to obtain a pass.
