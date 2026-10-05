# Unity asset layout and import tooling

## Choose an existing destination, otherwise use the fallback

Inspect the authorized project's instructions and Assets tree before import.
Reuse an established model destination under Arts, Art, Resources, or another
project-specific folder only when its contents or project conventions clearly
identify it as the appropriate model library. A folder name alone is not proof:
do not place models among unrelated UI, audio, or configuration assets. Resources
also has runtime loading/build semantics; use it only when the project already
uses that location for these models. Do not create Resources by default.

When no appropriate destination exists, or the choice remains ambiguous, use
Assets/AutoTA_Models without another routine confirmation. Place all models from
the batch under that root, each in its own named asset folder. Record the chosen
root and reason in the import configuration. Existing explicit project or user
conventions override this default.

## Searchable asset names

Use A_B for both the per-item directory and primary model/prefab basename:
A is the item category in lowercase singular English (sofa, cup, fork); B is
a concise distinguishing description in PascalCase (RedThreeSeat, GreenTwoSeat).
Use accurate distinguishing features; do not silently overwrite an existing
asset with the same name. If a separate variant needs a distinct name, extend B
with a meaningful distinguishing feature or version, keeping the A_B structure.

Example fallback layout:

```text
Assets/AutoTA_Models/
  sofa_RedThreeSeat/
    sofa_RedThreeSeat.fbx
    sofa_RedThreeSeat.prefab
    Materials/
      sofa_RedThreeSeat_Leather.mat
    Textures/
      sofa_RedThreeSeat_BaseColor.png
      sofa_RedThreeSeat_Normal.png
```

Common organizational subfolders such as Materials and Textures do not need
the A_B item name. Additional material/map suffixes may identify their roles.
Keep authored DCC originals and evidence outside Assets unless requested there.
Do not create an Editor folder or a saved validation Scene for each model.
Do not rename or relocate previous deliveries merely because this default was
added. When relocation is requested, preserve asset GUIDs through Unity asset
operations and verify serialized and string-based references afterward.

## One batch importer, archived outside Assets

Keep the authoritative import script and per-item configuration outside Assets,
for example under the authorized project root's AutoTA_Tools directory. Use one
shared batch entrypoint with per-item paths, settings, material bindings and
results rather than copying a script into each model's folder. Resume only
failed items; do not regenerate paid assets or overwrite successful outputs as
a side effect of retrying an import. Special asset types can use dedicated
handlers within this shared tooling.

A plain C# file outside Unity's compilation roots is not automatically compiled
or made callable by -executeMethod. Prefer an already available authorized
Editor bridge/tool. If a one-off Editor C# importer is necessary, temporarily
stage the shared importer in an isolated Editor folder under Assets (not under
each item), wait for compilation, execute and verify saved/reimported results,
then remove only that job's temporary script and its .meta after execution is
finished. Preserve its source/configuration and any evidence-bound version
outside Assets. Never remove unrelated tools or persistent import/runtime
dependencies. If interrupted or failed, record any temporary files left behind.
The final asset delivery should contain no one-off import scripts by default.
