# Fork defaults and first-use preferences

Use these defaults unless the current request or explicitly selected user/project
standards override them. They express this fork's game-asset preferences, not a
claim that every game or provider requires quad-only meshes.

## First use after deployment

On the first asset job after deployment, ask once in plain language whether the
user has their own standards: target engine/platform, typical viewing distance,
editable topology, polygon and texture budgets. Present the defaults below so
the user can accept them without inventing a specification. Do not ask again
when that information is already supplied in the conversation (including this
fork owner's instructions), or a reviewed preferences file exists.

With the user's supplied/accepted choices, save a small JSON preferences file
in the authorized project's `.auto-ta/preferences.json`. For preferences the
user explicitly wants across projects, use the runtime's user state directory,
`state/auto-ta/preferences.json`, under the configured runtime home. Record
`schema_version`, `reviewed: true`, `scope`, and the supplied standards. Never
write secrets, provider budgets/consent, or engine mutation permissions there.
Do not edit unrelated runtime configuration. If the user declines customization,
record acceptance of the fork defaults; do not block routine work on an optional
onboarding answer or repeatedly ask after it is declined.

Precedence: current asset instructions > explicit project standards > explicit
user standards > fork defaults. Project-specific preferences do not become
global defaults. Deployment scripts may print a first-use reminder; the agent
conducts onboarding at the first actual job, not in an unattended installer.

## Default game-asset standards

- Deliver only triangles and quads: no polygons with more than four corners.
  Resolve n-gons locally before delivery; their presence alone does not justify
  a full remesh. Check the editable mesh as well as the triangulated export.
- Organic assets intended to deform (characters, animals, monsters) should be
  predominantly quads with edge flow supporting the intended joints and poses.
  Useful triangles at sharp tips/corners are allowed. Quads alone do not ensure
  good deformation: inspect weights, edge flow and representative poses.
- Rigid props (furniture, weapons) may freely mix useful triangles and quads;
  prefer quads where later editing benefits. Classify by actual deformation,
  not the object's label: flexible weapons need deformation-aware topology too.
- Triangle fans on a flat circular clock dial, triangular polyhedra and similar
  intentional constructions are acceptable when shading and editing remain
  sound. A fan is an option, not the only way to model a circle. Do not remesh
  satisfactory geometry merely to reach 100% quads.
- Small props: choose a concrete target of a few hundred to 1000 polygons
  (usually 300–1000). Large props: start around 2000. Choose by complexity,
  silhouette, on-screen size and use, not physical size alone. A complex or
  articulated asset may need a specifically disclosed exception.
- Use ±20% of the chosen target as the planning/acceptance range: 1000 means
  800–1200; 2000 means 1600–2400. An already-good, simpler mesh below this range
  should not be padded with useless faces: revise and record the target instead.
- These are editable polygon counts, not engine triangle counts. Report both;
  choose an engine triangle budget independently. An all-quad mesh typically
  triangulates to twice its polygon count.
- UVs should be understandable for editing: sensible seams, useful orientation,
  no unintended overlap/collapse, adequate padding and density. Do not stretch
  an island merely to make it rectangular. Retain existing satisfactory UVs.
- Default texture maps to 2048 x 2048 for all routes. Explicit asset or reviewed
  user/project settings may override this. Verify actual delivered dimensions;
  upscaling alone does not add detail or prove texture quality.

## Choose the amount of work before production

Ask about importance/viewing distance before a new asset when not known: e.g.
“Is this a distant background prop, an ordinary scene object, or a close-up
important asset?” Combine this with first-use onboarding where possible. If
the user has already provided a category or authorized reasonable autonomous
choices, record that choice rather than asking again. For an unanswered optional
question, state an ordinary-scene-prop assumption before proceeding.

Inspect the actual mesh, then record `priority`, expected viewing distance,
`chosen_route`, and why in the asset contract:

| Condition | Preferred route |
| --- | --- |
| Very low priority / tiny distant prop, acceptable at its target camera | Keep existing mesh; skip aesthetic retopology |
| Small localized holes, shading or topology issues | Local repair, preserving silhouette, parts and UVs |
| High importance, large on-screen presence with visible detail, or severe generated-mesh defects; local repair cannot economically meet the contract | Consider optional reconstruct-and-rebake route |

Low priority does not waive missing textures, corrupt exports, or visible holes
at the target camera. Conversely, a few triangles or a small cosmetic defect do
not justify rebuilding the whole object. Physical size alone does not trigger
remeshing. Consider token cost, processing time and expected rework alongside
provider credits. Eligibility for reconstruction is not an obligation to use it.

For reconstruction, read [mesh-reconstruction.md](mesh-reconstruction.md) only
then. A successful remesher is not visual acceptance. Ask again only if a newly
discovered tradeoff changes the agreed shape, functionality, cost or scope.

Record the chosen target, tolerance, measured polygons/triangles, exceptions,
route and preference source in each contract/receipt so defaults are auditable.

## Unity organization defaults

Follow [unity-asset-layout.md](unity-asset-layout.md) for destination discovery,
`Assets/AutoTA_Models` fallback, searchable `category_Features` folder/model names,
and one batch importer archived outside `Assets`. Apply these to new deliveries;
existing project assets are not automatically moved or renamed.

## Texture padding and background

Extend each atlas island's edge texels into unused space, preferably filling
remaining unused space by nearest-island color extension. A compatible main
material color is an acceptable base-color background when it will not
contaminate differently colored islands. Avoid arbitrary black gutters around
nonblack islands; preserve intentional black material pixels. Use a UV coverage
or bake mask, never replace every black pixel. Preserve island interiors and
intentional alpha. Apply channel-aware padding to data maps; do not fill normal
or roughness maps with base color. Choose margins and island spacing for texture
resolution and intended mip levels; inspect seams at near/far engine distances.
Padding reduces filtering bleed, but does not fix incorrect or out-of-bounds
UVs. Record the padding method and pixel margin.

## Source and authoring route

Before production, ask once whether to use licensed web resources, direct Blender
modeling by the agent, Tripo (API or web), Meshy, or Hunyuan if not already chosen.
Combine this with standards/priority questions. Honor previous choices. If the
user delegates the decision, choose and record the route without asking again.
Route choice does not itself authorize unspecified charges or uploads.

Use these as selection heuristics, not universal capability claims:
- Direct Blender authoring suits objects decomposable into simple geometric
  parts, logical component structure, editable UVs, and exact text/numerals.
  Author text explicitly with suitable licensed fonts instead of asking generated
  pixels to spell clock markings or newsprint.
- Hosted generation may suit complex sculptural/stylized characters or weapons.
  Compare the actual brief and results; do not assume a provider lacks semantic
  understanding or always outperforms direct modeling. Direct work may cost more
  tokens, while generation may need more repair. Compare total work and credits.
- Default Tripo to the P2 family unless overridden. This is the fork owner's
  quality/rework preference, not a universal finding that H is defective. Verify
  available versions, controls and prices. If P2 is unavailable, disclose that
  and resolve the alternative rather than silently switching to H.
- Prefer sourced 3D assets with usable PBR coverage beyond base color: suitable
  roughness/metallic and normal detail where needed. Verify actual supplied maps.
  Constant channels can be appropriate; base-color-only is not equivalent to a
  complete textured PBR delivery. Include missing-channel work in selection cost.
- Unless cartoon/geometric style is explicitly requested, exclude oversimplified
  candidates whose silhouette, geometry or material detail cannot meet the brief.
  Judge assets, not creator seniority; low polygon count alone is not low quality.
  Pass these criteria to search-game-art's requirement matrix and keep its
  licensing checks.
