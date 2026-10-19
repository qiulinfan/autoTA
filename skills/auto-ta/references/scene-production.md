# Autonomous scene production

## Kickoff and optional modules

Default to completing the authorized job in one continuous run with agent-run
checks and a final handoff. A final user review may remain pending without
blocking production. Do not ask for approval after each asset, render or import.
Automatic checks remain required when human reviews are disabled. Continuous
execution is a workflow policy, not evidence of validated unattended uptime.

At kickoff, communicate the selected options in one short summary, and ask only
for material unknowns. Reuse existing choices; delegated implementation choices
need no reply. Store options in the project contract, not global skill edits:

```json
{
  "scene_options": {
    "intent": "original_game",
    "blockout": "auto",
    "master_variants": "auto",
    "human_edit_preservation": "auto",
    "weathering": "off",
    "human_review_stages": ["final"],
    "repair_attempts_per_issue": 2
  }
}
```

- `intent`: `original_game`, `reference_guided`, or `strict_reconstruction`.
  Multiple viewpoints, object references and gameplay/design ideas are normal
  inputs. Record source purpose and priority. Generated turnarounds are design
  proposals, not additional measurements. Resolve conflicting references from
  the stated priority; do not force a single camera match over gameplay needs.
- `blockout`: `auto`, `on`, `off`. Auto uses a cheap layout when spatial risk,
  navigation, sight lines or composition justify it. It is not a mandatory human
  gate. Off skips a separate whitebox deliverable, not dimensions/layout checks.
- `master_variants`: same three values. Auto reuses genuinely repeated families;
  unique assets need no artificial master. Separate geometry, shared material
  definitions and instance appearance; never mutate shared data to vary one item.
- `human_edit_preservation`: same three values. Auto snapshots existing authored
  scenes and protects user changes. Off means no managed override layer for a
  new generated scene; it never authorizes overwriting unrecognized user edits.
- `weathering`: `off`, `on`, `auto`; off by default. Auto enables only when the
  brief/style calls for it. Read [material-variation.md](material-variation.md)
  only for material variants, tiling issues or selected weathering.
- `human_review_stages`: a subset of `blockout`, `complex_assets`, `final`, or
  empty. Default final only. Selected intermediate reviews pause dependent work;
  otherwise the agent evaluates and proceeds. No response is not approval.
- Repairs are bounded per issue. On exhaustion retain useful output and report
  failure/prototype status; do not loop or silently buy another generation.

Project/asset preferences override these defaults. Provider spending/upload
authorization and exact target project remain separate from module selection.

Run `python <skill-dir>/scripts/validate_scene_options.py <asset-contract.json>`
to check and print normalized options without changing the input. This checks
policy syntax/conflicts only; it grants no permissions and validates no assets.

## Asset plan and contracts

Create a compact asset inventory with stable IDs, category, instance count,
priority/gameplay distance, semantic dimensions and forward/up axes, pivot,
source/authoring route, reference roles, material family, polygon/triangle budgets,
required channels and replaceable regions. Record units explicitly. A budget
such as 2000 polygons is project-specific, not a universal game-ready threshold.

Choose direct Blender authoring for regular, dimensioned geometry and hosted
generation when the expected shape/detail benefit outweighs repair cost. Make
reference sheets only where they resolve ambiguity; do not require three views
for every asset or send a composite sheet to an API without verified support.
Style consistency comes from shared references, material palettes, detail scale,
era and acceptance views, not identical prompts alone. Keep historical props
consistent with the chosen era. Preserve generated originals before any repair.

Use the existing asset topology/UV and round-trip gates. Replaceable screens,
labels and posters need a material region that can change independently, sensible
seams and a known image-to-surface aspect ratio. A rectangular region inside a
square texture is valid: record its UV bounds and content-placement rectangle.
Inspect with a grid/circle test; do not stretch UVs just to fill the image.
Symmetric UVs are optional and must not unintentionally mirror text. Smart UV is
an optional provider operation, not proof of readable UVs or a repair for geometry.
Verify current capability/cost before an authorized use; preserve pre-operation
files. Scan pages must be classified as single-page/spread before cropping;
select a whole page and use aspect-preserving fit when gutters are inappropriate.

## Assembly, repair and evidence

Store layout separately from geometry with stable asset and instance IDs,
resource references, transforms, material overrides and optional variant seeds.
Use named rotation fields plus the engine's convention; never assume tuple
order. Choose tolerances by units and precision, not exact float equality.
Define whether replay builds everything or inherits an existing scene template;
do not describe template-based static-mesh replay as a from-zero generator.

Before updating an existing scene, snapshot saved transforms/materials/lights and
compare against the last generated baseline. Apply only owned fields. Preserve
human overrides when selected; report conflicts instead of guessing ownership.
Inspect currently unsaved state before file-based work. In a new scene, use
incremental operations and stable IDs rather than delete-and-rebuild by label.

Check scale, facing, support contact, missing references and obvious intersections
after assembly. Bounding-box overlap is a candidate warning, not a collision
verdict: sockets, stacked surfaces and wall-mounted props need explicit allowed
contacts and mesh/visual inspection. These are required checks to implement for
the target; this reference does not supply a generic collision detector.

Capture fixed gameplay and diagnostic views under recorded exposure/lighting.
After a relevant edit rerun affected gates; technical pass and visual pass are
separate. Final user acceptance is separate again. Preserve actual before/after
evidence, not success messages from the generation service.

Use a stage ledger: input hashes, output hashes, tool/version, task ID, status,
repair reason, duration, API credits/currency and token usage with measurement
source. Unavailable token data is null, never estimated as an exact measurement.
CLI/API batching can reduce interaction overhead; report measured savings only.
Before retrying a timed-out paid submission, query its known task/receipt. If
acceptance is unknown and cannot be resolved, stop that paid branch rather than
submit again. Resume from verified durable outputs and invalidate dependents
when inputs change. Keep credentials and expiring signed URLs out of receipts.

## Delivery

Include final editable assets, engine dependencies, scripts/configuration and
reproduction scope. Validate a clean copy, including its saved map/resource
references, before stripping caches. Keep optional intermediate sources separate
when size matters. Do not claim a package can regenerate assets whose inputs are
omitted. Retain licenses and asset-specific provenance; separate self-authored
pipeline code, open-source dependencies, CC/public-domain imagery and commercial
generated assets. Do not assign one blanket license to all third-party content.
