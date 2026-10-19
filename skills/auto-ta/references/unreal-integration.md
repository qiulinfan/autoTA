# Unreal Engine integration

Use only for an authorized Unreal target. Record the canonical `.uproject` path,
engine version, target map and renderer/platform. Inspect existing plugins and
project conventions. Verify the running editor's project identity before live
mutations; launch CLI jobs with the explicit project path. Do not silently switch
to another open project or install plugins merely to make a route available.

## Execution and persistence

Prefer Blender background scripts for deterministic asset authoring and bounded
Unreal Python/CLI batches for import/assembly. Probe the installed engine's Python
capabilities before use; an executable alone does not prove plugin availability.
CLI operation is a route, not a requirement to close the user's editor. A file
job cannot see unsaved editor state; use the live saved state or a separate copy
and avoid simultaneous writers to the same packages.

Keep tooling outside runtime content. Map source asset IDs to engine object
paths and instance IDs to actors, not display labels alone. Explicitly translate
Blender meters/axes to the target's units/axes and record named rotation fields
(`pitch`, `yaw`, `roll` for UE). Check dimensions and semantic facing after import.
Do not infer rotation argument order from a tuple returned by another API.

After import inspect material slots, texture references, channel packing, normal
map orientation, color-space flags, collision and lightmap settings where needed.
Verify persisted assignments after save/reload in a separate process or clean
session. Keep mesh-count, materials, transform and lighting checks distinct.
Reimport must not reset user actor transforms, material overrides or light colors.

## Appearance checks

Record camera, post-process volumes, priorities, exposure method, physical-camera
exposure overrides and viewport exposure overrides. Piloting a camera is not
proof that its exposure governs the view. Diagnose overexposure by checking this
stack and light/emissive intensities; do not hide the problem with arbitrary
global multipliers. Use a reproducible exposure during visual comparisons.

Emissive screen materials control displayed pixels and visible brightness.
Contribution to nearby illumination depends on the rendering configuration;
verify it in the engine. Add small local lights only if the desired effect needs
them and the performance budget permits. For pipes/bends inspect smoothing,
split normals, tangent import and silhouette separately: smooth shading cannot
repair an insufficiently segmented silhouette. Use hard edges intentionally.

Capture beauty and diagnostic views with the actual renderer. Null-RHI commandlet
success proves neither shader appearance nor lighting. Do not claim new generic
UE automation has been engine-tested based on a prior project's screenshots.

## Packaging

Select deliverable maps explicitly; do not automatically ship all iterations.
Ensure startup/default map and retained dependencies resolve to included assets.
Keep `.uproject`, `Config`, required `Content`, and any necessary project plugins,
code/build inputs. Do not distribute the engine executable as project source.
For a saved delivery copy, `Intermediate` and `DerivedDataCache` are regenerable;
inspect `Saved` for needed captures, autosaves or work before excluding it.
Do not remove these directories from a live project as a cleanup shortcut.

Scan text/config for credentials and personal paths; use configurable paths.
Regenerated editor service tokens can reappear after a validation launch, so
scan the actual final copy after testing. Refresh manifests after edits. Test
opening/references from that copy and describe any missing intermediate source.
Package only when requested; if compression is deferred, label existing archives
as stale rather than silently claiming they contain the latest changes.
