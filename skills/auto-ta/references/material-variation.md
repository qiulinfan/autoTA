# Material variation and optional weathering

Base PBR work does not imply damage, dirt or age. Weathering is off unless the
project selects it or auto mode derives it from the brief. Clean, stylized and
new objects must remain valid outputs. Define style, palette, roughness range,
detail scale and target lighting before choosing maps.

Use shared base materials with per-instance parameters where economical. Keep
source maps immutable; use derived variants or masks for tint, dirt and labels.
Inventory all users before editing a shared material or atlas. Dark/light metal
variants may share maps with controlled base-color/roughness differences; do not
erase material detail with an indiscriminate multiply. Keep plausible metallic
semantics and inspect in neutral and target light.

For selected weathering, place dirt according to causes: contact, touch, gravity,
water streaks, joints, sheltered dust and wear. Control amount by material and
usage; avoid equal noise on every object. Local wall decals or overlay geometry
can break tiling without replacing the base texture. Compare decal/mesh support,
blend mode, normal/roughness contribution, sorting, z-fighting, mip edges and cost
in the actual renderer. Transparent PNGs alone do not provide complete PBR.
Baked texture overlays suit object-specific dirt when material/UV constraints
permit; preserve the clean source and independently replaceable screen/label.

For tile walls, vary by stable integer tile coordinates, not fractional UVs that
repeat the same random values each texture tile. Derive a seeded per-tile hash
from object/scene coordinates, account for grout and staggered rows, and keep the
seed stable across reloads. Blend subtle per-tile roughness and normal tilt with
the base PBR. Low roughness sharpens reflections; different surface orientation
changes their direction, so roughness variation alone is not a substitute for
normal variation. Keep grout separate and avoid implausibly mirror-like patches.
Use mesh/bevel displacement only where silhouette or close views justify it.

Large-scale masks and non-repeating local decals complement tile variation.
Validate seams across wall pieces, scale, mip aliasing, wet/dirty material
responses and shader cost. Procedural randomness does not guarantee realism.
Record parameter ranges and seeds for repeatability. Agent visual checks are
required; human review follows only the project's selected review stages.
